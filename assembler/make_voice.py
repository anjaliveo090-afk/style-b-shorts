#!/usr/bin/env python3
"""Make a test voiceover + SRT from a script in the user's format, with Kokoro (free, offline TTS).

  Narrator: [curious] What if ...? [break] [excited] Day 1. ...

  Grandma: [confused] Sweetie... how do I turn this thing on?

Every speaker gets its own voice (VOICES below: Kokoro voice, pitch shift, speed). Kokoro cannot act
emotions, so each tag is approximated with speed / loudness / pitch (EMOTIONS below); [whispering]
is also quieter and breathier. Pauses follow script_guide.md section 6: [break] 0.28 s, [pause] 0.45 s,
[long pause] 0.6 s, speaker change 0.25 s, so the voice runs ~90% of the time like the references.

Usage: make_voice.py script.txt out_dir [--model kokoro.onnx --voices voices.bin]
Writes out_dir/voice.mp3, out_dir/subs.srt and out_dir/speakers.json (who speaks when, for lip-sync).
Model files: https://github.com/thewh1teagle/kokoro-onnx/releases/tag/model-files-v1.0
(kokoro-v1.0.int8.onnx + voices-v1.0.bin); pip install kokoro-onnx."""
import argparse
import json
import re
import subprocess
from pathlib import Path

import librosa
import numpy as np

SR = 24000
# speaker -> (kokoro voice, pitch shift in semitones, base speed)
VOICES = {
    "narrator": ("am_puck", 0.0, 1.05),
    "kid": ("af_sky", 7.0, 1.1),
    "mom": ("af_sarah", 0.0, 1.0),
    "dad": ("am_michael", -1.5, 0.98),
    "grandma": ("bf_isabella", -2.0, 0.86),
    "grandpa": ("bm_george", -2.0, 0.86),
    "sister": ("af_nicole", 2.5, 1.05),
    "brother": ("am_echo", 2.5, 1.05),
    "grandkid": ("af_sky", 7.5, 1.12),
}
DEFAULT_VOICE = ("am_adam", 0.0, 1.0)
# emotion -> (speed x, gain dB, pitch semitones)
EMOTIONS = {
    "curious": (1.0, 0, 0.5), "excited": (1.12, 2, 1.0), "chuckling": (1.04, 0, 0.3), "laughing": (1.1, 1, 0.8),
    "gasping": (1.12, 2, 1.0), "shocked": (1.14, 3, 1.5), "suspense": (0.92, -1, -0.5), "cheerful": (1.08, 1, 0.8),
    "soft": (0.94, -3, -0.3), "deadpan": (0.92, -1, -0.8), "sad": (0.88, -3, -1.0), "whispering": (0.95, -9, 0.0),
    "confused": (0.9, 0, 0.5), "sweet": (0.95, -1, 0.5), "confident": (1.05, 1, 0.0), "crying": (1.0, 2, 1.5),
    "angry": (1.1, 3, 0.5), "suspicious": (0.95, 0, -0.3), "pleading": (1.1, 2, 1.5), "panicked": (1.18, 3, 1.5),
    "proud": (1.0, 1, 0.0), "mocking": (1.05, 1, 1.0), "sighing": (0.9, -2, -0.5), "emphasis": (1.0, 3, 0.5),
}
PAUSES = {"break": 0.28, "pause": 0.45, "long pause": 0.6}
SPEAKER_GAP = 0.25
JOIN_GAP = 0.08


def parse(script):
    """-> [(speaker, [("text", str, emotions) | ("pause", seconds)])]"""
    blocks = []
    for raw in re.split(r"\n\s*\n", script.strip()):
        m = re.match(r"\s*([A-Za-z][\w ]*?)\s*:\s*(.*)", raw, re.S)
        if not m:
            continue
        who, body = m.group(1).strip().lower(), " ".join(m.group(2).split())
        items, emos, fresh = [], [], False
        for tok in re.split(r"(\[[^\]]+\])", body):
            if not tok.strip():
                continue
            if tok.startswith("["):
                tag = tok[1:-1].strip().lower()
                if tag in PAUSES:
                    items.append(("pause", PAUSES[tag]))
                    emos, fresh = [e for e in emos if e != "emphasis"], True   # the mood carries over a pause
                else:
                    if fresh:                                                    # a new tag starts a new mood
                        emos, fresh = [], False
                    emos = emos + [tag]
            else:
                items.append(("text", tok.strip(), list(emos)))
                fresh = True
        blocks.append((who, items))
    return blocks


def trim(a, top_db=35):
    idx = np.where(np.abs(a) > np.max(np.abs(a)) * 10 ** (-top_db / 20))[0]
    if not len(idx):
        return a
    return a[max(0, idx[0] - int(0.01 * SR)): idx[-1] + int(0.04 * SR)]


def speak(kokoro, text, who, emos):
    voice, pitch0, speed0 = VOICES.get(who, DEFAULT_VOICE)
    speed, gain, pitch = speed0, 0.0, pitch0
    for e in emos:
        s, g, p = EMOTIONS.get(e, (1.0, 0, 0))
        speed, gain, pitch = speed * s, gain + g, pitch + p
    say = text.replace("...", ",").replace("…", ",")
    a, _ = kokoro.create(say, voice=voice, speed=float(np.clip(speed, 0.6, 1.5)), lang="en-us")
    a = trim(np.asarray(a, np.float32))
    if abs(pitch) > 0.05:
        a = librosa.effects.pitch_shift(a, sr=SR, n_steps=pitch)
    if "whispering" in emos:   # breathier: thin out the low end
        a = a - np.convolve(a, np.ones(40) / 40, mode="same") * 0.7
    if "crying" in emos:       # a shaky voice
        t = np.arange(len(a)) / SR
        a = a * (1 + 0.25 * np.sin(2 * np.pi * 7 * t))
    return a * 10 ** (gain / 20)


def ts(x):
    return f"{int(x // 3600):02d}:{int(x % 3600 // 60):02d}:{int(x % 60):02d},{int(round(x % 1 * 1000)) % 1000:03d}"


def main():
    p = argparse.ArgumentParser()
    p.add_argument("script")
    p.add_argument("out_dir")
    p.add_argument("--model", default="kokoro.onnx")
    p.add_argument("--voices", default="voices.bin")
    a = p.parse_args()
    from kokoro_onnx import Kokoro
    kokoro = Kokoro(a.model, a.voices)
    out = Path(a.out_dir)
    out.mkdir(parents=True, exist_ok=True)
    audio, t, cues, speakers = [np.zeros(int(SR * 0.3), np.float32)], 0.3, [], {}
    prev_who = None
    for who, items in parse(Path(a.script).read_text(encoding="utf-8")):
        if prev_who is not None:
            audio.append(np.zeros(int(SR * SPEAKER_GAP), np.float32))
            t += SPEAKER_GAP
        prev_who = who
        last_pause = True
        for it in items:
            if it[0] == "pause":
                audio.append(np.zeros(int(SR * it[1]), np.float32))
                t += it[1]
                last_pause = True
                continue
            if not last_pause:
                audio.append(np.zeros(int(SR * JOIN_GAP), np.float32))
                t += JOIN_GAP
            seg = speak(kokoro, it[1], who, it[2])
            d = len(seg) / SR
            cues.append((t, t + d, it[1].replace("[", "").replace("]", "")))
            speakers.setdefault(who, []).append([round(t, 2), round(t + d, 2)])
            audio.append(seg)
            t += d
            last_pause = False
    audio.append(np.zeros(int(SR * 0.4), np.float32))
    y = np.concatenate(audio)
    y = y / (np.max(np.abs(y)) + 1e-9) * 0.9
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "f32le", "-ar", str(SR), "-ac", "1", "-i", "-",
                    "-b:a", "192k", str(out / "voice.mp3")], input=y.astype(np.float32).tobytes(), check=True)
    (out / "subs.srt").write_text("\n".join(f"{k}\n{ts(s)} --> {ts(e)}\n{txt}\n" for k, (s, e, txt) in
                                            enumerate(cues, 1)), encoding="utf-8")
    json.dump(speakers, open(out / "speakers.json", "w"), indent=1)
    print(f"wrote {out}/voice.mp3 ({len(y) / SR:.1f}s), subs.srt ({len(cues)} cues), speakers.json")


if __name__ == "__main__":
    main()

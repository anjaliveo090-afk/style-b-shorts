#!/usr/bin/env python3
"""Silent parts of a narrated video: every gap in the VOICE stem (from audio_ref.py / separate.py),
how long it is, which line comes before and after, what the music+SFX stem does in the gap
(SFX hit, music only), and the frame in the middle of the gap.

Usage: silences.py video.mp4 voice.wav inst.wav [subs.srt] out_prefix [min_gap=0.25]
       silences.py - voice.mp3 - [subs.srt] out_prefix      (a voiceover alone, before making a video:
                                                             lists every pause so shots can be planned)
Writes out_prefix.json and out_prefix.png (one frame per gap >= 0.4 s, labelled)."""
import json
import subprocess
import sys
from pathlib import Path

import librosa
import numpy as np
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "assembler"))
from assemble import parse_srt  # noqa: E402

SR = 16000
HOP = 160   # 10 ms


def db(x):
    return 20 * np.log10(np.maximum(x, 1e-6))


def main(video, voice, inst, srt, prefix, min_gap=0.25):
    v, _ = librosa.load(voice, sr=SR, mono=True)
    m = librosa.load(inst, sr=SR, mono=True)[0] if inst != "-" else np.zeros_like(v)
    rv = db(librosa.feature.rms(y=v, frame_length=400, hop_length=HOP)[0])
    rm = db(librosa.feature.rms(y=m, frame_length=400, hop_length=HOP)[0])
    n = min(len(rv), len(rm))
    rv, rm = rv[:n], rm[:n]
    # 22 dB under the loud speech: voice-tool files keep breaths and room tone (-32..-40 dB) between
    # words, which a deeper threshold counts as speech (it read 99% "speech" on the user's voices)
    speech_floor = np.percentile(rv[rv > -80], 90) - 22
    on = rv > speech_floor
    # close tiny dropouts inside words (< 80 ms)
    k = 8
    on = np.convolve(on.astype(float), np.ones(k) / k, mode="same") > 0.01
    cues = parse_srt(srt) if srt else []
    music_floor = np.median(rm)
    gaps, i = [], 0
    while i < n:
        if on[i]:
            i += 1
            continue
        j = i
        while j < n and not on[j]:
            j += 1
        t0, t1 = i * HOP / SR, j * HOP / SR
        if t1 - t0 >= min_gap:
            seg = rm[i:j]
            peak = float(seg.max())
            before = next((c for a, b, c in reversed(cues) if a < t0 + 0.05), "")
            after = next((c for a, b, c in cues if a >= t1 - 0.15), "")
            gaps.append(dict(t0=round(t0, 2), t1=round(t1, 2), dur=round(t1 - t0, 2),
                             position="start" if i == 0 else ("end" if j >= n else "middle"),
                             sfx_in_gap=bool(peak > music_floor + 9), peak_vs_music_db=round(float(peak - music_floor), 1),
                             before=before[-40:], after=after[:40]))
        i = j
    talk = sum(on) * HOP / SR
    dur = n * HOP / SR
    mid = [g for g in gaps if g["position"] == "middle"]
    summary = dict(video=Path(video).name, duration=round(float(dur), 2), speech_share=round(float(talk / dur), 3),
                   gaps_total=len(mid), gaps_per_10s=round(len(mid) / dur * 10, 1),
                   gap_median=round(float(np.median([g["dur"] for g in mid])), 2) if mid else 0,
                   gap_p90=round(float(np.percentile([g["dur"] for g in mid], 90)), 2) if mid else 0,
                   gap_max=max([g["dur"] for g in mid], default=0),
                   gaps_over_0_6s=int(sum(g["dur"] >= 0.6 for g in mid)),
                   gaps_with_sfx=int(sum(g["sfx_in_gap"] for g in mid)),
                   lead_in=gaps[0]["dur"] if gaps and gaps[0]["position"] == "start" else 0.0,
                   tail=gaps[-1]["dur"] if gaps and gaps[-1]["position"] == "end" else 0.0)
    json.dump(dict(summary=summary, gaps=gaps), open(prefix + ".json", "w"), indent=1)
    print(json.dumps(summary))
    for g in gaps:
        print(f"{g['t0']:6.2f}-{g['t1']:6.2f} {g['dur']:4.2f}s {g['position']:6s} sfx={int(g['sfx_in_gap'])} "
              f"| {g['before']!r} -> {g['after']!r}")
    big = [g for g in gaps if g["dur"] >= 0.4]
    if not big or video == "-":
        return
    tw, th = 160, 284
    sheet = Image.new("RGB", (tw * min(8, len(big)), (th + 34) * ((len(big) + 7) // 8)), "white")
    d = ImageDraw.Draw(sheet)
    font = ImageFont.load_default(size=11)
    for k, g in enumerate(big):
        t = (g["t0"] + g["t1"]) / 2
        raw = subprocess.run(["ffmpeg", "-v", "error", "-ss", str(t), "-i", video, "-frames:v", "1", "-vf",
                              f"scale={tw}:{th}", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"],
                             capture_output=True).stdout
        if len(raw) == tw * th * 3:
            sheet.paste(Image.frombytes("RGB", (tw, th), raw), ((k % 8) * tw, (k // 8) * (th + 34)))
        x, y = (k % 8) * tw, (k // 8) * (th + 34) + th
        d.text((x + 2, y + 1), f"{g['t0']:.2f}s  {g['dur']:.2f}s {'SFX' if g['sfx_in_gap'] else ''}", fill="red",
               font=font)
        d.text((x + 2, y + 16), g["after"][:24], fill="blue", font=font)
    sheet.save(prefix + ".png")


if __name__ == "__main__":
    a = sys.argv[1:]
    srt = a[3] if len(a) > 4 and a[3].endswith(".srt") else None
    rest = a[4:] if srt else a[3:]
    main(a[0], a[1], a[2], srt, rest[0], *(float(x) for x in rest[1:]))

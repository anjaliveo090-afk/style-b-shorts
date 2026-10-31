#!/usr/bin/env python3
"""Shorten long pauses in a voiceover to the reference length, and shift the SRT to match.

The references keep the voice running ~90% of the time: pauses between lines are 0.2-0.5 s and
never longer than ~0.7 s (script_guide.md section 6). TTS tags like [long pause] often make 1-2 s
gaps; this trims every gap longer than --max down to --max (keeping its middle, so breaths/tails
stay natural) and moves every SRT cue after it earlier by the same amount.

Usage: tighten_voice.py voice.mp3 subs.srt out_voice.wav out_subs.srt [--max 0.6] [--keep-end 0.4]"""
import argparse
import re
import subprocess
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from assemble import parse_srt  # noqa: E402

SR = 44100


def load(path):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(path), "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"],
                         capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.float32).copy()


def ts(x):
    x = max(0.0, x)
    return f"{int(x // 3600):02d}:{int(x % 3600 // 60):02d}:{int(x % 60):02d},{int(round(x % 1 * 1000)) % 1000:03d}"


def main():
    p = argparse.ArgumentParser()
    p.add_argument("voice")
    p.add_argument("srt")
    p.add_argument("out_voice")
    p.add_argument("out_srt")
    p.add_argument("--max", type=float, default=0.6, help="longest pause kept (s)")
    p.add_argument("--keep-end", type=float, default=0.4, help="silence kept after the last word (s)")
    a = p.parse_args()
    x = load(a.voice)
    hop = SR // 100
    n = len(x) // hop
    rms = np.sqrt((x[:n * hop].reshape(n, hop) ** 2).mean(1))
    db = 20 * np.log10(rms + 1e-7)
    on = db > np.percentile(db[db > -90], 90) - 30
    on = np.convolve(on.astype(float), np.ones(8) / 8, mode="same") > 0.01
    cuts = []   # (t_start, seconds removed)
    i = 0
    while i < n:
        if on[i]:
            i += 1
            continue
        j = i
        while j < n and not on[j]:
            j += 1
        dur = (j - i) / 100
        if i > 0 and j < n and dur > a.max:
            remove = dur - a.max
            mid = (i + j) / 2 / 100
            cuts.append((mid - remove / 2, remove))
        elif j >= n and dur > a.keep_end:
            cuts.append((i / 100 + a.keep_end, dur - a.keep_end))
        i = j
    keep, last = [], 0
    for t0, rem in cuts:
        s0, s1 = int(t0 * SR), int((t0 + rem) * SR)
        keep.append(x[last:s0])
        last = s1
    keep.append(x[last:])
    y = np.concatenate(keep)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "f32le", "-ar", str(SR), "-ac", "1", "-i", "-",
                    a.out_voice], input=y.astype(np.float32).tobytes(), check=True)

    def shift(t):
        return t - sum(min(rem, max(0.0, t - t0)) for t0, rem in cuts)
    cues = parse_srt(a.srt)
    out = [f"{k}\n{ts(shift(s))} --> {ts(shift(e))}\n{txt}\n" for k, (s, e, txt) in enumerate(cues, 1)]
    Path(a.out_srt).write_text("\n".join(out), encoding="utf-8")
    print(f"removed {sum(r for _, r in cuts):.2f}s in {len(cuts)} pauses; "
          f"{len(x) / SR:.2f}s -> {len(y) / SR:.2f}s")
    for t0, rem in cuts:
        print(f"  at {t0:6.2f}s  -{rem:.2f}s")


if __name__ == "__main__":
    main()

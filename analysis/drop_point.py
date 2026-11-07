#!/usr/bin/env python3
"""Find out what was on screen and in the voice where viewers swiped away (YouTube retention drop).

Usage: drop_point.py <story> <time_s> [window_s=3]
  <story> = the name in videos.md / animator/<story>.py (output/<story>/ must hold the final mp4,
            subs.srt and words/aligned.json)
Prints:
  - the shots around the drop (name, start, length), the spoken lines and words in the window;
  - a pace check: how long since the last new visual, the camera/motion level, the voice gaps,
    and the SFX in the window;
Writes output/<story>/drop_<time>.png: frames every 0.25 s from t-window to t+1, with the line spoken.
Use the checklist in lessons.md ("How to diagnose a drop") to name the reason."""
import importlib
import json
import subprocess
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "assembler"))
sys.path.insert(0, str(ROOT / "animator"))
sys.path.insert(0, str(ROOT / "analysis"))
from assemble import parse_srt  # noqa: E402


def main(story, t, win=3.0):
    t, win = float(t), float(win)
    O = ROOT / "output" / story
    video = next((p for p in (O / f"{story}_final_captions.mp4", O / f"{story}_final.mp4") if p.exists()), None)
    if video is None:
        sys.exit(f"no final mp4 in {O}")
    cues = parse_srt(O / "subs.srt") if (O / "subs.srt").exists() else []
    words = json.load(open(O / "words" / "aligned.json")) if (O / "words" / "aligned.json").exists() else []
    a, b = max(0.0, t - win), t + 1.0

    print(f"== {story}: drop at {t:.2f}s (window {a:.2f}-{b:.2f}s)  video: {video.name}")
    try:
        mod = importlib.import_module(story)
        shots = mod.SHOTS
        print("-- shots")
        for k, s in enumerate(shots):
            if s["end"] >= a - 2 and s["start"] <= b:
                mark = "  <== DROP" if s["start"] <= t < s["end"] else ""
                print(f"  {s['start']:6.2f}s  {s['end'] - s['start']:4.2f}s  {s['draw'].__name__}{mark}")
        sfx = [x for x in getattr(mod, "SFX", []) if a <= x[0] <= b]
        print(f"-- SFX in window: {len(sfx)}  " + ", ".join(f"{x[0]:.2f} {x[1]}" for x in sfx))
    except Exception as e:   # the story module may need its output folder; keep going
        print("  (could not load the story module:", e, ")")
    print("-- spoken lines")
    for s, e, txt in cues:
        if e >= a and s <= b:
            print(f"  {s:6.2f}-{e:6.2f}  {txt}")
    if words:
        print("-- words: " + " ".join(f"{w['w']}@{w['s']:.1f}" for w in words if a <= w["s"] <= b))
        before = [w for w in words if w["e"] <= t]
        if before:
            print(f"-- silence before the drop: {max(0.0, t - before[-1]['e']):.2f}s since the last word")

    import new_visuals
    changes, _ = new_visuals.changes(str(video))
    prev = [c for c in changes if c <= t]
    nxt = [c for c in changes if c > t]
    print(f"-- last new visual {t - prev[-1]:.2f}s before the drop" if prev else "-- no new visual before the drop")
    if nxt:
        print(f"-- next new visual {nxt[0] - t:.2f}s after the drop")
    gaps = np.diff([0] + changes)
    long = [(changes[i] - g, g) for i, g in enumerate(gaps) if g > 2.0]
    print("-- visual holds over 2 s in the whole video: " + (", ".join(f"{s:.1f}s ({g:.1f}s)" for s, g in long) or "none"))

    tw, th = 120, 213
    times = list(np.arange(a, b + 0.01, 0.25))
    cols = 8
    sheet = Image.new("RGB", (cols * (tw + 2), ((len(times) + cols - 1) // cols) * (th + 30)), "white")
    d = ImageDraw.Draw(sheet)
    font = ImageFont.load_default(size=11)
    for k, tt in enumerate(times):
        raw = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{tt:.2f}", "-i", str(video), "-frames:v", "1", "-vf",
                              f"scale={tw}:{th}", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], capture_output=True).stdout
        x, y = (k % cols) * (tw + 2), (k // cols) * (th + 30)
        if len(raw) == tw * th * 3:
            sheet.paste(Image.frombytes("RGB", (tw, th), raw), (x, y))
        line = next((c for s, e, c in cues if s <= tt < e), "")
        d.text((x + 2, y + th + 1), f"{tt:.2f}" + ("  DROP" if abs(tt - t) < 0.13 else ""),
               fill="red", font=font)
        d.text((x + 2, y + th + 14), line[:20], fill="blue", font=font)
    out = O / f"drop_{t:.1f}.png"
    sheet.save(out)
    print("-- frames:", out)


if __name__ == "__main__":
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    main(*sys.argv[1:4])

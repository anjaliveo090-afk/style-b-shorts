#!/usr/bin/env python3
"""Burn Style B (reference-style) captions onto a finished video, without re-rendering it.

Look measured from the reference videos (style_bible.md section 1):
- 1-2 words at a time, centred at x 360, y ~825 of 720x1280;
- heavy font (Inter Display ExtraBold), letters ~80 px tall incl. outline, flat fill,
  thick black outline, soft drop shadow underneath;
- normal words white in normal case; the key word in CAPITALS and the whole group in a colour
  (yellow, green, red, pink, purple, orange, blue);
- every new caption pops in (0.85 -> 1.0 with a small overshoot) on its first word.

Usage:
  captions.py video.mp4 aligned.json spec.json out.mp4
    aligned.json : analysis/align_words.py output ([{"w", "s", "e"}, ...])
    spec.json    : [[word_index_or_time, "TEXT", "colour or null"], ...] one entry per caption,
                   in order; an int is the index of the caption's first word in aligned.json,
                   a float is an absolute time (for words the SRT missed, e.g. "EWW!").
  captions.py video.mp4 aligned.json auto out.mp4
    groups words 2 at a time, white, with a colour + capitals on numbers and on words ending in ! or ?
The audio of video.mp4 is copied unchanged."""
import json
import math
import subprocess
import sys

import cairo
import numpy as np

W, H = 720, 1280
FONT = "Inter Display ExtraBold"
SIZE = 92                 # font size: ~80 px tall caps + outline, as measured
Y = 825                   # caption centre
MAX_W = 600               # wider captions are scaled down
COLOURS = {
    "white": "#ffffff", "yellow": "#fccc0c", "green": "#3ce454", "red": "#ff3b3b", "pink": "#fc6ccc",
    "purple": "#cc84fc", "orange": "#fcb40c", "blue": "#54ccfc",
}


def hexc(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))


def probe(path):
    out = subprocess.check_output(["ffprobe", "-v", "error", "-select_streams", "v", "-show_entries",
                                   "stream=r_frame_rate:format=duration", "-of", "json", path], text=True)
    d = json.loads(out)
    num, den = d["streams"][0]["r_frame_rate"].split("/")
    return float(d["format"]["duration"]), float(num) / float(den)


def resolve(words, spec):
    """spec -> [(t0, t1, text, colour)] with display times."""
    caps = []
    for k, (ref, text, col) in enumerate(spec):
        if isinstance(ref, int):
            n = len(text.split())
            t0 = words[ref]["s"]
            last = words[min(len(words) - 1, ref + n - 1)]["e"]
        else:
            t0 = float(ref)
            last = t0 + 0.12 * len(text)
        caps.append([t0, last, text, col])
    out = []
    for k, (t0, last, text, col) in enumerate(caps):
        nxt = caps[k + 1][0] if k + 1 < len(caps) else last + 0.6
        t1 = nxt if nxt - last < 0.6 else last + 0.35   # hold until the next caption unless there is a pause
        out.append((t0, max(t0 + 0.12, t1), text, col))
    return out


def auto_spec(words):
    spec, i = [], 0
    while i < len(words):
        w = words[i]["w"]
        key = any(c.isdigit() for c in w) or w.endswith(("!", "?"))
        if key:
            spec.append([i, w.upper(), "yellow"])
            i += 1
            continue
        grp = [w]
        if i + 1 < len(words) and not w.endswith((",", ".")):
            nxt = words[i + 1]["w"]
            if not (any(c.isdigit() for c in nxt) or nxt.endswith(("!", "?"))):
                grp.append(nxt)
        spec.append([i, " ".join(grp), None])
        i += len(grp)
    return spec


def draw_caption(ctx, text, col, k):
    """One caption; k = seconds since it appeared (drives the pop)."""
    sc = 1 - 0.15 * math.exp(-14 * k) * math.cos(20 * k)
    ctx.save()
    ctx.select_font_face(FONT, cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
    ctx.set_font_size(SIZE)
    e = ctx.text_extents(text)
    fit = min(1.0, MAX_W / max(1.0, e.width))
    ctx.translate(W / 2, Y)
    ctx.scale(sc * fit, sc * fit)
    x, y = -e.width / 2 - e.x_bearing, -e.height / 2 - e.y_bearing
    ctx.set_line_join(cairo.LINE_JOIN_ROUND)
    ctx.move_to(x + 2, y + 8)                                # soft drop shadow
    ctx.text_path(text)
    ctx.set_source_rgba(0, 0, 0, 0.45)
    ctx.set_line_width(SIZE * 0.2)
    ctx.stroke_preserve()
    ctx.fill()
    ctx.move_to(x, y)                                        # thick black outline + flat fill
    ctx.text_path(text)
    ctx.set_source_rgb(0.04, 0.03, 0.05)
    ctx.set_line_width(SIZE * 0.17)
    ctx.stroke_preserve()
    ctx.set_source_rgb(*hexc(COLOURS.get(col or "white", col or "#ffffff")))
    ctx.fill()
    ctx.restore()


def main(video, aligned, spec_path, out):
    words = json.load(open(aligned))
    spec = auto_spec(words) if spec_path == "auto" else json.load(open(spec_path))
    caps = resolve(words, spec)
    dur, fps = probe(video)
    n = int(round(dur * fps))
    cmd = ["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-i", video,
           "-f", "rawvideo", "-pix_fmt", "bgra", "-s", f"{W}x{H}", "-r", f"{fps}", "-i", "-",
           "-filter_complex", "[0:v][1:v]overlay=0:0:format=auto:alpha=premultiplied,format=yuv420p[v]",
           "-map", "[v]", "-map", "0:a?", "-c:v", "libx264", "-preset", "medium", "-crf", "20",
           "-c:a", "copy", "-movflags", "+faststart", out]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
    blank = bytes(W * H * 4)
    for f in range(n):
        T = f / fps
        cur = [c for c in caps if c[0] <= T < c[1]]
        if not cur:
            proc.stdin.write(blank)
            continue
        ctx = cairo.Context(surf)
        ctx.set_operator(cairo.OPERATOR_CLEAR)
        ctx.paint()
        ctx.set_operator(cairo.OPERATOR_OVER)
        t0, t1, text, col = cur[-1]
        draw_caption(ctx, text, col, T - t0)
        surf.flush()
        proc.stdin.write(bytes(surf.get_data()))
    proc.stdin.close()
    proc.wait()
    print(f"wrote {out} ({len(caps)} captions)")


if __name__ == "__main__":
    if len(sys.argv) != 5:
        sys.exit(__doc__)
    main(*sys.argv[1:])

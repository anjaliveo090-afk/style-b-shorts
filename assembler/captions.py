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
  captions.py video.mp4 aligned.json spec.json out.mp4 animator/<story>.py
    also skips text that is already on screen: the story's shots are replayed at each caption's
    start / middle / end, every text they draw (labels, chapter cards, bubbles, HUD, UI) is recorded,
    and caption words already visible are removed (a caption left with only filler words is dropped).
The audio of video.mp4 is copied unchanged."""
import importlib
import json
import math
import os
import re
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


NUMBERS = {"ONE": "1", "TWO": "2", "THREE": "3", "FOUR": "4", "FIVE": "5", "SIX": "6", "SEVEN": "7",
           "EIGHT": "8", "NINE": "9", "TEN": "10", "TWENTY": "20", "FIFTY": "50", "HUNDRED": "100"}
FILLER = {"A", "AN", "THE", "TO", "OF", "IN", "ON", "AT", "BY", "AND", "IS", "IT", "ITS", "SO", "FOR", "YOU",
          "YOUR", "YOURE", "THAT", "THIS", "BUT", "OR", "WITH", "FROM"}


def norm(word):
    w = re.sub(r"[^A-Z0-9]", "", word.upper())
    return NUMBERS.get(w, w)


def onscreen_reader(story_path):
    """Returns f(T) -> set of normalised words the story shows on screen at time T."""
    sys.path.insert(0, os.path.dirname(os.path.abspath(story_path)))
    story = importlib.import_module(os.path.splitext(os.path.basename(story_path))[0])
    import sets
    seen, inside = set(), [0]
    orig_bold, orig_label = sets.bold_text, sets.label

    def bold_text(ctx, s, *a, **kw):
        if not inside[0] and kw.get("scale", 1.0) > 0.3 and s:
            seen.update(norm(w) for w in str(s).split())
        return orig_bold(ctx, s, *a, **kw)

    def label(ctx, s, x, y, size, *a, **kw):
        if kw.get("scale", 1.0) > 0.3:
            seen.update(norm(w) for w in str(s).split())
        inside[0] += 1
        try:
            return orig_label(ctx, s, x, y, size, *a, **kw)
        finally:
            inside[0] -= 1

    sets.bold_text, sets.label = bold_text, label
    if hasattr(story, "label"):
        story.label = label
    shots = story.SHOTS
    surf = cairo.ImageSurface(cairo.FORMAT_RGB24, W, H)

    def at(T):
        seen.clear()
        i = max(k for k, sh in enumerate(shots) if sh["start"] <= T or k == 0)
        sh = shots[i]
        t, d = T - sh["start"], sh["end"] - sh["start"]
        ctx = cairo.Context(surf)
        sh["draw"](ctx, t, d)
        if sh.get("overlay"):
            sh["overlay"](ctx, t, d)
        return {w for w in seen if w}
    return at


def skip_onscreen(caps, at):
    """Remove caption words that are already visible on screen while the caption shows."""
    out, dropped = [], 0
    for t0, t1, text, col in caps:
        vis = set()
        for T in (t0 + 0.04, (t0 + t1) / 2, max(t0 + 0.04, t1 - 0.04)):
            vis |= at(T)
        keep = [w for w in text.split() if norm(w) not in vis]
        # a cut-down caption is dropped when what is left is only filler or a lone short lowercase word
        # ("got PAID?!" with PAID?! on screen would leave just "got")
        leftover_weak = all(norm(w) in FILLER or (not w.isupper() and len(norm(w)) <= 4) for w in keep)
        if len(keep) < len(text.split()) and (not keep or leftover_weak):
            print(f"  {t0:6.2f}s  '{text}' skipped (on screen)")
            dropped += 1
            continue
        if len(keep) < len(text.split()):
            print(f"  {t0:6.2f}s  '{text}' -> '{' '.join(keep)}' (rest is on screen)")
        out.append((t0, t1, " ".join(keep), col))
    print(f"skipped {dropped} captions whose text is already on screen")
    return out


def main(video, aligned, spec_path, out, story=None):
    words = json.load(open(aligned))
    spec = auto_spec(words) if spec_path == "auto" else json.load(open(spec_path))
    caps = resolve(words, spec)
    if story:
        caps = skip_onscreen(caps, onscreen_reader(story))
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
    if len(sys.argv) not in (5, 6):
        sys.exit(__doc__)
    main(*sys.argv[1:])

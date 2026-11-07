"""Landscape contact sheet: one frame per shot (at 70 % of the shot) for a 16:9 story.
  python3 preview_ls.py <story> <out.png> [t_from] [t_to] [cols=6]"""
import importlib
import sys

import cairo
import numpy as np
from PIL import Image, ImageDraw

mod = importlib.import_module(sys.argv[1])
import engine  # noqa: E402  (after the story set the 16:9 mode)

out = sys.argv[2]
t0 = float(sys.argv[3]) if len(sys.argv) > 3 else 0.0
t1 = float(sys.argv[4]) if len(sys.argv) > 4 else 1e9
cols = int(sys.argv[5]) if len(sys.argv) > 5 else 6
engine.OUT_SCALE = 0.25
tw, th = int(engine.W * 0.25), int(engine.H * 0.25)
shots = [s for s in mod.SHOTS if t0 <= s["start"] < t1]
surf = cairo.ImageSurface(cairo.FORMAT_RGB24, tw, th)
cells = []
for sh in shots:
    t = 0.7 * (sh["end"] - sh["start"])
    engine._draw_shot(sh, t, surf, None)
    surf.flush()
    a = np.ndarray((th, tw, 4), np.uint8, surf.get_data(), strides=(surf.get_stride(), 4, 1))
    im = Image.fromarray(a[:, :, 2::-1].copy())
    ImageDraw.Draw(im).text((4, 2), f"{sh['start']:.2f}", fill=(255, 255, 0))
    cells.append(im)
rows = (len(cells) + cols - 1) // cols
sheet = Image.new("RGB", (cols * (tw + 4), rows * (th + 4)), "white")
for i, im in enumerate(cells):
    sheet.paste(im, ((i % cols) * (tw + 4), (i // cols) * (th + 4)))
sheet.save(out)
print(out, len(cells), "shots")

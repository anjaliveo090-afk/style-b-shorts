"""Contact sheet of a story before the full render: frames of every shot (after
safezone.fit) with the Shorts safe zone drawn, labelled with time and shot name.
Usage: python3 contact.py <story_module> out.png [frames_per_shot=2]
e.g.   python3 contact.py sample /tmp/sample_contact.png"""
import importlib
import sys

import cairo
import numpy as np
from PIL import Image, ImageDraw

import engine
import safezone
from engine import H, W


def main(mod_name, out, per=2):
    mod = importlib.import_module(mod_name)
    shots = mod.SHOTS
    safezone.fit(shots, mod, verbose=False)
    surf = cairo.ImageSurface(cairo.FORMAT_RGB24, W, H)
    noise = [np.zeros((H, W, 1), np.int16)]
    tiles = []
    for s in shots:
        d = s["end"] - s["start"]
        for k in range(per):
            t = d * (0.35 + 0.6 * k / max(1, per - 1)) if per > 1 else d * 0.6
            engine._draw_shot(s, t, surf, noise)
            a = np.ndarray((H, W, 4), np.uint8, surf.get_data())[:, :, [2, 1, 0]].copy()
            im = Image.fromarray(a).resize((240, 427))
            dr = ImageDraw.Draw(im)
            sx = 240 / W
            pts = [(safezone.X0, safezone.Y0), (safezone.X1, safezone.Y0), (safezone.X1, safezone.NOTCH_Y),
                   (safezone.NOTCH_X, safezone.NOTCH_Y), (safezone.NOTCH_X, safezone.Y1), (safezone.X0, safezone.Y1)]
            dr.polygon([(x * sx, y * sx) for x, y in pts], outline=(255, 60, 60), width=2)
            if s.get("top"):
                dr.line([(0, s["top"] * sx), (240, s["top"] * sx)], fill=(255, 160, 0), width=1)
            dr.rectangle([0, 0, 240, 16], fill=(0, 0, 0))
            dr.text((3, 2), f"{s['start'] + t:.2f}s {s['draw'].__name__}", fill=(255, 255, 255))
            tiles.append(im)
    cols = 8
    rows = (len(tiles) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * 242, rows * 429), "white")
    for i, im in enumerate(tiles):
        sheet.paste(im, ((i % cols) * 242, (i // cols) * 429))
    sheet.save(out)
    print("wrote", out, len(tiles), "frames")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], *(int(x) for x in sys.argv[3:]))

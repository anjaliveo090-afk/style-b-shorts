"""Thumbnail kit for the LOCKED REFERENCE THUMBNAIL DNA (thumbnail_dna.md): 9:16, 1080x1920 only.

Pieces the DNA asks for:
  layer(fn)            draw something on its own transparent layer
  sticker(base, lay)   paste a layer with the thick white sticker stroke (+ a soft shadow) around it (7/7 refs)
  headline(...)        ALL CAPS display text: fill (gold gradient or flat), brown outline, white outer stroke,
                       drop shadow, slight tilt (Luckiest Guy; falls back to Inter Display Black)
  red_ring(...)        the red circle on the proof object, with a white edge (6/7 refs)
  curved_arrow(...)    optional red curved arrow (2/7 refs)
  save(surf, title)    writes output/thumbnails/<title>.png (filename = title, the user's rule)

Characters and props come from style.py / sets.py, drawn at 1080x1920 coordinates."""
import math
import os

import cairo
import numpy as np
from PIL import Image, ImageFilter

W, H = 1080, 1920
PI = math.pi
BROWN = (0.36, 0.16, 0.06)
GOLD = [(0.0, "#fff7b8"), (0.45, "#ffd23a"), (1.0, "#ff9418")]
CREAM = [(0.0, "#fffbe6"), (1.0, "#ffe68a")]


def _hex(c):
    if isinstance(c, str):
        c = c.lstrip("#")
        return tuple(int(c[i:i + 2], 16) / 255 for i in (0, 2, 4))
    return c


def font_name():
    import subprocess
    out = subprocess.run(["fc-list", ":", "family"], capture_output=True, text=True).stdout
    return "Luckiest Guy" if "Luckiest Guy" in out else "Inter Display Black"


FONT = font_name()


def landscape():
    """Switch the kit to 16:9, 1920x1080 (long-video thumbnails, thumbnail_dna.md section 9)."""
    global W, H
    W, H = 1920, 1080


def new():
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
    return surf, cairo.Context(surf)


def layer(fn):
    surf, ctx = new()
    ctx.set_line_join(cairo.LINE_JOIN_ROUND)
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    fn(ctx)
    surf.flush()
    return surf


def _alpha(surf):
    return np.ndarray((H, W, 4), np.uint8, surf.get_data(), strides=(surf.get_stride(), 4, 1))[:, :, 3].copy()


def _mask_surface(alpha, rgb, a=1.0):
    """ARGB32 surface of one colour with the given alpha (premultiplied BGRA)."""
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
    arr = np.ndarray((H, W, 4), np.uint8, surf.get_data(), strides=(surf.get_stride(), 4, 1))
    al = (alpha.astype(np.float32) * a)
    r, g, b = rgb
    arr[:, :, 0] = (al * b).astype(np.uint8)
    arr[:, :, 1] = (al * g).astype(np.uint8)
    arr[:, :, 2] = (al * r).astype(np.uint8)
    arr[:, :, 3] = al.astype(np.uint8)
    surf.mark_dirty()
    return surf


def dilate(alpha, r):
    img = Image.fromarray(alpha).filter(ImageFilter.GaussianBlur(r * 0.5))
    img = img.point(lambda v: 255 if v > 4 else 0).filter(ImageFilter.GaussianBlur(1.2))
    return np.asarray(img)


def sticker(base_ctx, lay, r=16, col=(1, 1, 1), shadow=0.28):
    """Paste lay onto base_ctx with a thick sticker stroke of radius r around its shape."""
    al = dilate(_alpha(lay), r)
    if shadow:
        sh = np.asarray(Image.fromarray(al).filter(ImageFilter.GaussianBlur(6)))
        base_ctx.set_source_surface(_mask_surface(sh, (0.15, 0.05, 0.2), shadow), 8, 12)
        base_ctx.paint()
    base_ctx.set_source_surface(_mask_surface(al, _hex(col)), 0, 0)
    base_ctx.paint()
    base_ctx.set_source_surface(lay, 0, 0)
    base_ctx.paint()


def _grad(y0, y1, stops):
    g = cairo.LinearGradient(0, y0, 0, y1)
    for k, c in stops:
        g.add_color_stop_rgb(k, *_hex(c))
    return g


def headline(ctx, txt, x, y, size, fill=GOLD, outline=BROWN, white=True, tilt=-0.04, max_w=None, arc=0.0):
    """One line of thumbnail text centred at (x, y). fill: list of gradient stops or a colour.
    max_w shrinks the size so the line fits. arc > 0 bends the line (letters on a gentle curve)."""
    ctx.save()
    ctx.select_font_face(FONT, cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
    ctx.set_font_size(size)
    e = ctx.text_extents(txt)
    if max_w and e.x_advance > max_w:
        size *= max_w / e.x_advance
        ctx.set_font_size(size)
        e = ctx.text_extents(txt)
    ctx.translate(x, y)
    ctx.rotate(tilt)
    x0 = -e.x_advance / 2
    yb = -e.y_bearing / 2 - e.height / 2 + e.height / 2   # baseline so the caps are centred on y
    yb = e.height / 2

    def path():
        ctx.new_path()
        cx = x0
        for ch in txt:
            ce = ctx.text_extents(ch)
            mid = cx + ce.x_advance / 2
            dy = arc * (mid / (e.x_advance / 2)) ** 2 * size if arc else 0.0
            ang = arc * 2 * mid / (e.x_advance / 2) * 0.35 if arc else 0.0
            ctx.save()
            ctx.translate(mid, yb + dy)
            ctx.rotate(ang)
            ctx.move_to(-ce.x_advance / 2, 0)
            ctx.text_path(ch)
            ctx.restore()
            cx += ce.x_advance
    ctx.set_line_join(cairo.LINE_JOIN_ROUND)
    ctx.save()                                   # drop shadow
    ctx.translate(size * 0.03, size * 0.08)
    path()
    ctx.set_source_rgba(0.12, 0.02, 0.15, 0.45)
    ctx.set_line_width(size * (0.36 if white else 0.2))
    ctx.stroke_preserve()
    ctx.fill()
    ctx.restore()
    if white:                                    # white outer stroke
        path()
        ctx.set_source_rgb(1, 1, 1)
        ctx.set_line_width(size * 0.34)
        ctx.stroke()
    path()                                       # brown outline
    ctx.set_source_rgb(*_hex(outline))
    ctx.set_line_width(size * 0.17)
    ctx.stroke()
    path()                                       # fill
    if isinstance(fill, list):
        ctx.set_source(_grad(yb - e.height, yb, fill))
    else:
        ctx.set_source_rgb(*_hex(fill))
    ctx.fill()
    ctx.save()                                   # glossy top highlight
    path()
    ctx.clip()
    ctx.rectangle(-W, yb - e.height - 4, 2 * W, e.height * 0.3)
    ctx.set_source_rgba(1, 1, 1, 0.28)
    ctx.fill()
    ctx.restore()
    ctx.restore()
    return size


def red_ring(ctx, x, y, rx, ry, w=20, tilt=-0.08):
    ctx.save()
    ctx.translate(x, y)
    ctx.rotate(tilt)
    ctx.scale(rx, ry)
    ctx.new_sub_path()
    ctx.arc(0, 0, 1, 0, 2 * PI)
    ctx.restore()
    path = ctx.copy_path()
    ctx.set_source_rgb(1, 1, 1)
    ctx.set_line_width(w * 1.9)
    ctx.stroke()
    ctx.append_path(path)
    ctx.set_source_rgb(*_hex("#ff2b3a"))
    ctx.set_line_width(w)
    ctx.stroke()


def curved_arrow(ctx, x0, y0, x1, y1, bend=0.35, w=22, col="#ff2b3a"):
    mx, my = (x0 + x1) / 2, (y0 + y1) / 2
    nx, ny = -(y1 - y0) * bend, (x1 - x0) * bend
    cx, cy = mx + nx, my + ny
    ang = math.atan2(y1 - cy, x1 - cx)
    hx, hy = x1 - math.cos(ang) * w * 1.6, y1 - math.sin(ang) * w * 1.6
    for lw, c in ((w * 1.9, (1, 1, 1)), (w, _hex(col))):
        ctx.move_to(x0, y0)
        ctx.curve_to(cx, cy, cx, cy, hx, hy)
        ctx.set_source_rgb(*c)
        ctx.set_line_width(lw)
        ctx.set_line_cap(cairo.LINE_CAP_ROUND)
        ctx.stroke()
    for grow, c in ((w * 0.5, (1, 1, 1)), (0, _hex(col))):
        L = w * 2.4 + grow
        ctx.move_to(x1 + math.cos(ang) * grow * 0.6, y1 + math.sin(ang) * grow * 0.6)
        ctx.line_to(x1 - math.cos(ang - 0.5) * L, y1 - math.sin(ang - 0.5) * L)
        ctx.line_to(x1 - math.cos(ang + 0.5) * L, y1 - math.sin(ang + 0.5) * L)
        ctx.close_path()
        ctx.set_source_rgb(*c)
        ctx.fill()


def save(surf, title, out_dir=None):
    out_dir = out_dir or os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "output", "thumbnails")
    os.makedirs(out_dir, exist_ok=True)
    safe = "".join(ch for ch in title if ch not in '/\\:*?"<>|').rstrip(". ")
    path = os.path.join(out_dir, safe + ".png")
    flat = cairo.ImageSurface(cairo.FORMAT_RGB24, W, H)
    c = cairo.Context(flat)
    c.set_source_surface(surf, 0, 0)
    c.paint()
    flat.write_to_png(path)
    return os.path.abspath(path)

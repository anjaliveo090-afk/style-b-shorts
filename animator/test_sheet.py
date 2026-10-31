"""Style test sheet: every cast member x all expressions (busts) and x the main arm/leg poses (full body).
Usage: python3 test_sheet.py out_prefix  -> out_prefix_expr.png, out_prefix_poses.png"""
import sys

import cairo

import style
from engine import hexc, text

CAST = [("KID", style.KID), ("MOM", style.MOM), ("MOM_ROBE", style.MOM_ROBE), ("GRANDMA", style.GRANDMA),
        ("NOOB", style.NOOB), ("DAD", style.DAD)]


def bg(ctx, w, h):
    g = cairo.LinearGradient(0, 0, 0, h)
    g.add_color_stop_rgb(0, *hexc("#84d4fb"))
    g.add_color_stop_rgb(1, *hexc("#b8e8fb"))
    ctx.set_source(g)
    ctx.paint()


def expr_sheet(path, cell=200):
    ex = style.EXPRESSIONS
    w, h = cell * len(ex), int(cell * 1.15) * len(CAST) + 40
    surf = cairo.ImageSurface(cairo.FORMAT_RGB24, w, h)
    ctx = cairo.Context(surf)
    bg(ctx, w, h)
    for j, e in enumerate(ex):
        text(ctx, e, j * cell + cell / 2, 20, 20, (1, 1, 1))
    for i, (name, ch) in enumerate(CAST):
        for j, e in enumerate(ex):
            x, y = j * cell + cell / 2, 40 + i * int(cell * 1.15) + cell * 1.9
            ctx.save()
            ctx.rectangle(j * cell, 40 + i * int(cell * 1.15), cell, int(cell * 1.15))
            ctx.clip()
            ch.draw(ctx, x, y, 0.95, e, 0.3, arms=("down", "down"), bob=0)
            ctx.restore()
    surf.write_to_png(path)


def pose_sheet(path, cell=230):
    combos = [(a, a, "stand") for a in style.ARMS] + [("down", "down", p) for p in style.POSES[1:]]
    w, h = cell * len(combos), 420 * len(CAST[:4]) + 40
    surf = cairo.ImageSurface(cairo.FORMAT_RGB24, w, h)
    ctx = cairo.Context(surf)
    bg(ctx, w, h)
    for j, (a, b, p) in enumerate(combos):
        text(ctx, p if p != "stand" else a, j * cell + cell / 2, 20, 20, (1, 1, 1))
    for i, (name, ch) in enumerate(CAST[:4]):
        for j, (a, b, p) in enumerate(combos):
            ch.draw(ctx, j * cell + cell / 2, 40 + i * 420 + 390, 1.0, "happy" if j % 3 == 0 else "neutral", 0.4,
                    arms=(a, b), pose=p, walk_phase=0.25, item="phone" if a == "phone" else None, bob=0)
    surf.write_to_png(path)


if __name__ == "__main__":
    expr_sheet(sys.argv[1] + "_expr.png")
    pose_sheet(sys.argv[1] + "_poses.png")

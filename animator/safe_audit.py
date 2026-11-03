"""Audit a story against the Shorts safe zone, frame by frame (after safezone.fit, so the camera is the render's).

Checks, on screen, everything a viewer must see:
  - every character's HEAD (any Block, also secondary characters inside close-ups), clipped to what is visible;
  - every piece of text (labels, name tags, bubbles, toasts, UI rows, cards: all go through sets.bold_text);
  - the shot's keep=[...] boxes.
Things crossing the frame edge (entering / leaving / off screen) are not counted.
Zone (safezone.py): x 38..680, y 149..1013; below y 678 the right edge is x 599 (like/comment buttons).

Usage (from animator/):  python3 safe_audit.py <story> [fps=4]
Prints one line per (shot, element) that leaves the zone, with the worst overflow in px and when."""
import importlib
import sys

import cairo

import engine
import safezone as sz
import sets as st
import style
from engine import H, W

X0, X1, Y0, Y1, NX, NY = sz.X0, sz.X1, sz.Y0, sz.Y1, sz.NOTCH_X, sz.NOTCH_Y
TOL = 4          # px of overflow that nobody can see
_rec = []


def _clip(ctx, x0, y0, x1, y1):
    cx0, cy0, cx1, cy1 = ctx.clip_extents()
    x0, y0, x1, y1 = max(x0, cx0), max(y0, cy0), min(x1, cx1), min(y1, cy1)
    if x1 - x0 < 2 or y1 - y0 < 2:
        return None
    pts = [ctx.user_to_device(x, y) for x, y in ((x0, y0), (x1, y0), (x0, y1), (x1, y1))]
    xs, ys = [p[0] for p in pts], [p[1] for p in pts]
    return min(xs), min(ys), max(xs), max(ys)


def _install():
    orig_draw = style.Block.draw

    def draw(self, ctx, x, y, s=1.0, *a, **kw):
        u = self.HW * 64 * s
        hy = y - 2.5 * u
        b = _clip(ctx, x - 0.55 * u, hy - 0.6 * u, x + 0.55 * u, hy + 0.55 * u)
        if b:
            _rec.append(("head #%d (x %d)" % (sum(1 for k, _ in _rec if k.startswith("head")), x), b))
        return orig_draw(self, ctx, x, y, s, *a, **kw)
    style.Block.draw = draw

    orig_text = st.bold_text

    def bold_text(ctx, s, x, y, size, *a, **kw):
        sc = kw.get("scale", 1.0)
        if s and sc > 0.3:
            w = st.text_width(ctx, s, size) * sc
            h = size * 0.75 * sc
            align = kw.get("align", "c")
            x0 = {"c": x - w / 2, "l": x, "r": x - w}[align]
            b = _clip(ctx, x0, y - h / 2, x0 + w, y + h / 2)
            if b:
                _rec.append(("text '%s'" % s[:18], b))
        return orig_text(ctx, s, x, y, size, *a, **kw)
    st.bold_text = bold_text


def overflow(b):
    x0, y0, x1, y1 = b
    if x0 <= 1 or x1 >= W - 1 or y0 <= 1 or y1 >= H - 1:   # (boxes are clipped to the frame)
        return 0.0   # crossing the frame edge: entering/leaving the frame (or off screen), not placed there
    right = NX if y1 > NY else X1
    return max(0.0, X0 - x0, x1 - right, Y0 - y0, y1 - Y1)


def audit(module, fps=4):
    shots = module.SHOTS
    sz.fit(shots, module, verbose=False)
    _install()
    surf = cairo.ImageSurface(cairo.FORMAT_RGB24, W, H)
    worst = {}
    for shot in shots:
        n = max(2, int((shot["end"] - shot["start"]) * fps))
        for i in range(n):
            T = shot["start"] + (i + 0.5) * (shot["end"] - shot["start"]) / n
            del _rec[:]
            ctx = cairo.Context(surf)
            z, (cx, cy) = engine.key_camera(shot["keys"], T)
            ctx.translate(W / 2, H / 2)
            ctx.scale(z, z)
            ctx.translate(-cx, -cy)
            engine._CAM.update(z=z, c=(cx, cy), z0=shot["keys"][0][1], c0=shot["keys"][0][2], strength=0.3)
            shot["draw"](ctx, T - shot["start"], shot["end"] - shot["start"])
            for x0, y0, x1, y1 in shot.get("keep", ()):
                _rec.append(("keep box", ((x0 - cx) * z + W / 2, (y0 - cy) * z + H / 2,
                                          (x1 - cx) * z + W / 2, (y1 - cy) * z + H / 2)))
            if shot.get("overlay"):
                ctx = cairo.Context(surf)
                shot["overlay"](ctx, T - shot["start"], shot["end"] - shot["start"])
            for kind, b in _rec:
                o = overflow(b)
                if o > TOL:
                    key = (shot["start"], shot["draw"].__name__, kind.split(" (x")[0])
                    if o > worst.get(key, (0,))[0]:
                        worst[key] = (o, T, tuple(round(v) for v in b))
    return worst


if __name__ == "__main__":
    mod = importlib.import_module(sys.argv[1])
    res = audit(mod, int(sys.argv[2]) if len(sys.argv) > 2 else 4)
    for (start, name, kind), (o, T, b) in sorted(res.items()):
        print(f"{start:6.2f} {name:22s} {kind:28s} out {o:5.0f}px at {T:6.2f}s  box {b}")
    print(f"{len(res)} elements outside the safe zone")

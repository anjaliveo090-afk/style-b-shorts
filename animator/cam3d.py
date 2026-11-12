"""Fake-3D cinematic camera for our 2D shots (the user, 2026-11-12: "3d camera moment ... cinematic 3D animation
style"): smooth, slow, continuous camera moves where the background (far) and the subject (near) move by different
amounts, so the flat drawing reads as a 3D set. Plus a soft depth-of-field blur on the background in the final render.

How it works: a shot gets cam="orbit_l" (etc.). wrap() applies the SUBJECT move to the whole shot; every background
helper of the story draws through bg(ctx, fn): it undoes the subject move and applies the BACKGROUND move instead
(parallax), optionally blurred (depth of field). Moves are eased over the whole shot (they never stop mid-shot).

Moves (p 0..1 over the shot):
  orbit_l / orbit_r  the camera arcs round the subject: the background slides the other way (+-46 px), the subject
                     drifts a little with a slight turn of scale (the signature 3D look)
  push / pull        dolly in / out: the subject grows faster than the background (1.0 -> 1.09 vs 1.0 -> 1.03)
  vertigo            dolly zoom: the subject keeps its size, the background zooms 1.0 -> 1.28 (shock moments)
  crane_up / _down   the camera rises / sinks: the subject moves vertically more than the background
  track_l / track_r  a sideways dolly: the subject slides +-28 px, the background +-9 px
  low                a low-angle hero shot: the subject grows from its feet, the background sinks behind it
Use 1 move per shot, change the move every shot, and give shock beats vertigo, entrances low, reveals push.
"""
import math

import cairo

from engine import H, W, clamp

STATE = {"fg": None, "bg": None, "dof": 0.0, "blur_on": False}
BG_BASE = 1.14          # the background is drawn a little larger so its moves never show an edge


def _smooth(p):
    p = clamp(p)
    return p * p * p * (p * (6 * p - 15) + 10)          # smootherstep: a soft start and a soft landing


def _lerp(a, b, p):
    return a + (b - a) * p


def _m(dx=0.0, dy=0.0, s=1.0, ax=W / 2, ay=H / 2):
    """Affine matrix: scale s about (ax, ay), then move (dx, dy)."""
    m = cairo.Matrix()
    m.translate(ax + dx, ay + dy)
    m.scale(s, s)
    m.translate(-ax, -ay)
    return m


def move(name, p):
    """(subject matrix, background matrix, depth-of-field 0..1) at progress p of the shot."""
    q = _smooth(p)
    if name in ("orbit_l", "orbit_r"):
        sg = 1 if name == "orbit_r" else -1
        fg = _m(sg * _lerp(-14, 14, q), 0, 1.0 + 0.025 * math.sin(math.pi * q), 360, 900)
        bg = _m(-sg * _lerp(-54, 54, q), 0, 1.0 + 0.04 * math.sin(math.pi * q), 360, 700)
        return fg, bg, 0.6
    if name == "push":
        return _m(0, 0, _lerp(1.0, 1.11, q), 360, 700), _m(0, 0, _lerp(1.0, 1.03, q), 360, 700), 0.6
    if name == "pull":
        return _m(0, 0, _lerp(1.09, 1.0, q), 360, 700), _m(0, 0, _lerp(1.03, 1.0, q), 360, 700), 0.5
    if name == "vertigo":
        k = _smooth(min(1.0, p * 1.6))                     # most of the zoom in the first 60 % of the shot
        return _m(0, 0, 1.0 + 0.02 * k, 360, 700), _m(0, 0, _lerp(1.0, 1.32, k), 360, 600), 0.8
    if name in ("crane_up", "crane_down"):
        sg = 1 if name == "crane_up" else -1
        return (_m(0, sg * _lerp(-26, 26, q), 1.0, 360, 900),
                _m(0, sg * _lerp(-8, 8, q), 1.0, 360, 640), 0.5)
    if name in ("track_l", "track_r"):
        sg = 1 if name == "track_l" else -1
        return _m(sg * _lerp(28, -28, q), 0, 1.0, 360, 900), _m(sg * _lerp(9, -9, q), 0, 1.0, 360, 640), 0.5
    if name == "low":
        return (_m(0, 0, _lerp(1.0, 1.08, q), 360, 1000),
                _m(0, _lerp(0, 34, q), _lerp(1.0, 1.04, q), 360, 640), 0.6)
    return cairo.Matrix(), cairo.Matrix(), 0.0


def wrap(draw, name):
    """A shot's draw(ctx, t, d) moved by the 3D camera `name`."""
    if not name:
        return draw

    def fn(ctx, t, d):
        fg, bgm, dof = move(name, t / max(d, 1e-6))
        STATE.update(fg=fg, bg=bgm, dof=dof)
        ctx.save()
        ctx.transform(fg)
        draw(ctx, t, d)
        ctx.restore()
        STATE.update(fg=None, bg=None, dof=0.0)
    return fn


def bg(ctx, draw, blur=1.0):
    """Draw a background layer at the far depth: the background move instead of the subject move, a little larger
    (BG_BASE) so no edge shows, and blurred for depth of field in the final render (blur 0 = sharp)."""
    if STATE.get("in_bg"):                                  # already inside a background layer
        draw(ctx)
        return
    STATE["in_bg"] = True
    try:
        _bg(ctx, draw, blur)
    finally:
        STATE["in_bg"] = False


def _bg(ctx, draw, blur):
    ctx.save()
    if STATE["fg"] is not None:
        inv = cairo.Matrix(*STATE["fg"])
        inv.invert()
        ctx.transform(inv)
        ctx.transform(STATE["bg"])
    ctx.transform(_m(0, 0, BG_BASE, W / 2, H / 2))
    amt = blur * STATE["dof"] if STATE["blur_on"] else 0.0
    if amt <= 0.05:
        draw(ctx)
        ctx.restore()
        return
    # depth of field: draw the background at reduced resolution, then scale it back up smoothly
    tgt = ctx.get_target()
    tw, th = tgt.get_width(), tgt.get_height()
    f = 1.0 + 2.2 * amt                                     # 1.0 sharp .. 3.2 soft
    sw, sh = max(1, int(tw / f)), max(1, int(th / f))
    small = cairo.ImageSurface(cairo.FORMAT_ARGB32, sw, sh)
    c2 = cairo.Context(small)
    c2.scale(sw / tw, sh / th)
    c2.transform(ctx.get_matrix())
    draw(c2)
    small.flush()
    ctx.identity_matrix()
    ctx.scale(tw / sw, th / sh)
    ctx.set_source_surface(small, 0, 0)
    ctx.get_source().set_filter(cairo.FILTER_GOOD)
    ctx.paint()
    ctx.restore()

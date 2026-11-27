"""Fake-3D cinematic camera for our 2D shots (the user, 2026-11-12: "3d camera moment"; trained 2026-11-19 on the
camera chapter of the user's 3D-animator reference, "only camera": camera_guide.md).

The model: a real camera on a RAIL. Each move is ONE cubic Bezier rail in camera space (x, y = sideways / up-down in
px at the subject's depth, d = dolly fraction towards the subject) driven by ONE eased progress value p, plus an aim
weight a (1 = the camera keeps looking at the subject, an orbit; 0 = it does not turn, a track). Every layer is
placed by its depth factor k (subject 1.0, background KB = 0.3), so parallax comes out of the geometry, not from
hand-set numbers:
    shift = (a - k) * (x, y)          scale = 1 / (1 - k * d)
The subject layer is the whole shot (wrap); the background helpers draw through bg(ctx, fn) at depth KB, with a thin
depth of field that racks with the dolly (closer = softer background). No zoom: the lens never changes, the camera
moves. The rail is eased with easeInOut over the shot plus 0.25 s each side, so every cut lands on motion.

Moves: orbit_l / orbit_r (an arc round the subject with a little dolly), push / pull (a dolly with a little orbit, a
curved path like a real operator), rush (a fast push that lands, for shocks; old name "vertigo"), crane_up /
crane_down, track_l / track_r, low (the camera sinks and pushes: a hero angle). Check: python3 cam3d.py <story>
prints the camera speed per shot and flags jerks.
"""
import math
import sys

import cairo

from engine import H, W, clamp

STATE = {"fg": None, "bg": None, "dof": 0.0, "blur_on": False}
BG_BASE = 1.14          # the background is drawn a little larger so its moves never show an edge
KB = 0.3                # depth factor of the background layer (the subject is 1.0)
LEAD = 0.25             # seconds of the rail before and after the shot: cut on motion
SUBJ = (360, 760)       # where the subject usually stands (scale anchor)


def ease_io(k):
    """easeInOut (cubic), the reference's travel easing."""
    k = clamp(k)
    return 4 * k * k * k if k < 0.5 else 1 - (-2 * k + 2) ** 3 / 2


def ease_out(k):
    k = clamp(k)
    return 1 - (1 - k) ** 3


def _bez(p0, c1, c2, p3, u):
    v = 1 - u
    return tuple(v ** 3 * a + 3 * v * v * u * b + 3 * v * u * u * c + u ** 3 * d
                 for a, b, c, d in zip(p0, c1, c2, p3))


def _m(dx=0.0, dy=0.0, s=1.0, ax=W / 2, ay=H / 2):
    """Affine matrix: scale s about (ax, ay), then move (dx, dy)."""
    m = cairo.Matrix()
    m.translate(ax + dx, ay + dy)
    m.scale(s, s)
    m.translate(-ax, -ay)
    return m


def _mirror(r):
    return tuple((-x, y, d) for x, y, d in r)


# rails: (START, C1, C2, END) in (x px, y px, d), aim a, easing, subject anchor
ORBIT_R = ((-70, 0, 0.0), (-25, 0, 0.035), (25, 0, 0.035), (70, 0, 0.01))
PUSH = ((0, 0, 0.0), (8, 0, 0.035), (16, -5, 0.075), (18, -6, 0.105))
CRANE_UP = ((0, 46, 0.0), (4, 16, 0.02), (6, -16, 0.03), (6, -46, 0.02))
TRACK_R = ((-34, 0, 0.0), (-12, 0, 0.02), (12, 0, 0.02), (34, 0, 0.0))
LOW = ((0, 0, 0.0), (0, 14, 0.03), (6, 30, 0.06), (8, 36, 0.085))
RUSH = ((0, 0, 0.0), (0, 0, 0.09), (4, -3, 0.13), (5, -4, 0.14))
MOVES = {
    "orbit_r": (ORBIT_R, 1.0, ease_io, SUBJ), "orbit_l": (_mirror(ORBIT_R), 1.0, ease_io, SUBJ),
    "push": (PUSH, 1.0, ease_io, (360, 700)), "pull": (PUSH[::-1], 1.0, ease_io, (360, 700)),
    "crane_up": (CRANE_UP, 0.6, ease_io, SUBJ), "crane_down": (CRANE_UP[::-1], 0.6, ease_io, SUBJ),
    "track_r": (TRACK_R, 0.0, ease_io, SUBJ), "track_l": (_mirror(TRACK_R), 0.0, ease_io, SUBJ),
    "low": (LOW, 0.5, ease_io, (360, 1000)), "rush": (RUSH, 1.0, ease_out, (360, 700)),
}
MOVES["vertigo"] = MOVES["rush"]          # no zoom: a dolly zoom is a lens change, the reference never does it


def layer(name, p, k):
    """Matrix of a layer at depth factor k at rail progress p (0..1, already including the lead-in)."""
    rail, aim, ease, (ax, ay) = MOVES[name]
    x, y, d = _bez(*rail, ease(p))
    return _m((aim - k) * x, (aim - k) * y, 1.0 / (1.0 - k * d), ax, ay), d


def move(name, t, dur):
    """(subject matrix, background matrix, depth of field 0..1) at shot time t of a shot lasting dur."""
    if name not in MOVES or STATE.get("off"):
        return cairo.Matrix(), cairo.Matrix(), 0.0
    p = (t + LEAD) / (dur + 2 * LEAD)
    fg, d = layer(name, p, 1.0)
    bgm, _ = layer(name, p, KB)
    dof = 0.35 + 3.0 * max(0.0, d)            # rack focus: the closer the camera, the softer the background
    return fg, bgm, min(0.75, dof)


def wrap(draw, name):
    """A shot's draw(ctx, t, d) moved by the 3D camera `name`."""
    if not name:
        return draw

    def fn(ctx, t, d):
        fg, bgm, dof = move(name, t, max(d, 1e-6))
        STATE.update(fg=fg, bg=bgm, dof=dof)
        ctx.save()
        ctx.transform(fg)
        draw(ctx, t, d)
        ctx.restore()
        STATE.update(fg=None, bg=None, dof=0.0)
    return fn


def bg(ctx, draw, blur=1.0, floor=None):
    """Draw a background layer at the far depth: the background move instead of the subject move, a little larger
    (BG_BASE) so no edge shows, and blurred for depth of field in the final render (blur 0 = sharp)."""
    if STATE.get("in_bg"):                                  # already inside a background layer
        draw(ctx)
        return
    if STATE.get("layer") == "fg":                          # diorama.py: the subject layer only
        return
    if STATE.get("layer") == "bg":                          # diorama.py: the background goes to its own surface
        c2 = STATE["bg_ctx"]
        c2.save()
        c2.set_matrix(ctx.get_matrix())
        STATE["in_bg"] = True
        try:
            draw(c2)
        finally:
            STATE["in_bg"] = False
            c2.restore()
        if floor is not None:
            STATE["floor_y"] = floor
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
    f = 1.0 + 1.6 * amt                                     # thin lens: 1.0 sharp .. ~2.2 soft, never a toy
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


def comfort(mod_name, fps=60):
    """The reference's comfort check: camera speed per frame for every shot (the subject point and a background
    point), and a JERK flag where the speed changes suddenly between two frames."""
    import importlib
    mod = importlib.import_module(mod_name)
    bad = 0
    for sh in mod.SHOTS:
        name = getattr(mod, "CAM3D", {}).get(round(sh["start"], 2))
        if not name:
            continue
        dur = sh["end"] - sh["start"]
        steps, prev = [], None
        for f in range(int(dur * fps) + 1):
            fg, bgm, _ = move(name, f / fps, dur)
            pt = fg.transform_point(*SUBJ) + bgm.transform_point(360, 300)
            if prev:
                steps.append(max(math.hypot(pt[0] - prev[0], pt[1] - prev[1]),
                                 math.hypot(pt[2] - prev[2], pt[3] - prev[3])))
            prev = pt
        if not steps:
            continue
        med = sorted(steps)[len(steps) // 2]
        acc = max((abs(b - a) for a, b in zip(steps, steps[1:])), default=0.0)
        jerk = acc > 0.25 * max(steps) + 0.3            # a sudden change of speed between two frames
        bad += jerk
        print(f"{sh['start']:6.2f} {name:10s} median {med:5.2f} px/frame  max {max(steps):5.2f}"
              f"{'  JERK' if jerk else ''}")
    print(f"{bad} jerky moves")


if __name__ == "__main__":
    comfort(sys.argv[1])

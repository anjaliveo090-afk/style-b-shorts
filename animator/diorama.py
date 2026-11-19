"""2.5D diorama render: our flat Style B drawings placed in a real 3D space and filmed with a real perspective camera
(the user, 2026-11-19: "zip me jo camera moment thi waisi": the camera chapter of the 3D-animator reference).

The set of every shot is split into layers (cam3d.STATE["layer"]): the background helpers (cam3d.bg) give the WALL
and the FLOOR, everything else is the SUBJECT. Each becomes a plane in 3D:
  subject  a card at z = 0, the frame's size (from the home camera it looks exactly like the 2D shot)
  wall     a card at z = DW behind it, standing on the floor, scaled so it looks its 2D size from home
  floor    the floor strip of the background laid flat (y = the feet line) from the wall to under the camera
           (only shots whose background helper passed floor=...; bursts and cards have a far wall only)
The camera is the reference's: ONE lens (vertical FOV ~46 deg, never animated), the eye on a smooth 3D rail driven by
one eased value, always looking at the subject (orbit / push / crane / low angle come from the rail's shape), thin-
lens depth of field (the wall and the floor soften with their distance from the focus plane), and motion blur
(sub-frames over a 180 deg shutter). One rail can run across many cuts in the same set, so the camera feels continuous.
The HUD overlay stays flat on the screen.

Run (from animator/):  python3 diorama.py school_short <t0> <t1> <out.mp4>   (rails: RAILS in this file)"""
import importlib
import math
import subprocess
import sys

import cairo
import cv2
import numpy as np

import cam3d
import engine
from engine import H, W

Z0 = 1500.0                  # home camera distance = focal length in px (the 2D frame at z 0 maps 1:1)
DW = 650.0                   # wall depth behind the subject
FEET = 1000                  # frame y of the floor line
CW, CH, OX, OY = 2100, 2300, 690, 510      # layer canvas (margin round the frame so the camera can look round)
APERTURE = 7.0               # depth-of-field strength (px of blur per unit of 1 - d_focus / d)
SUBFRAMES = 2                # motion blur samples per frame
SHUTTER = 0.5                # fraction of a frame the shutter is open (180 deg)


def ease_io(k):
    k = min(1.0, max(0.0, k))
    return 4 * k * k * k if k < 0.5 else 1 - (-2 * k + 2) ** 3 / 2


def bez(p0, c1, c2, p3, u):
    v = 1 - u
    return tuple(v ** 3 * a + 3 * v * v * u * b + 3 * v * u * u * c + u ** 3 * d for a, b, c, d in zip(p0, c1, c2, p3))


def orbit_eye(theta_deg, r, y):
    th = math.radians(theta_deg)
    return np.array([r * math.sin(th), y, -r * math.cos(th)])


# A rail: (t0, t1, (theta, radius, eye height) at START, C1, C2, END, look target).
# theta: degrees round the subject (+ = the camera to the right), radius from the subject, eye y (+ = lower = a
# low angle). The gym fight is ONE rail from the doors to ERASED; the close-up swing has its own.
RAILS = {
    "school_short": [
        (30.43, 40.45, ((-16, 1700, -70), (-8, 1600, 60), (6, 1450, 40), (16, 1380, -20)), (0, -60, 0)),
        (38.48, 39.44, ((10, 1550, 0), (5, 1500, 0), (-2, 1440, 0), (-6, 1400, 0)), (0, -80, 0)),
    ],
}


def camera_at(story, T):
    """(eye, look) at story time T: the latest rail that covers T (a later rail overrides an earlier one)."""
    rail = None
    for r in RAILS.get(story, []):
        if r[0] <= T <= r[1]:
            rail = r
    if rail is None:
        return np.array([0.0, 0.0, -Z0]), np.zeros(3)
    t0, t1, pts, look = rail
    th, r, y = bez(*pts, ease_io((T - t0) / (t1 - t0)))
    return orbit_eye(th, r, y), np.array(look, float)


def basis(eye, look):
    fwd = look - eye
    fwd /= np.linalg.norm(fwd)
    right = np.cross(np.array([0.0, 1.0, 0.0]), fwd)
    right /= np.linalg.norm(right)
    down = np.cross(fwd, right)
    return right, down, fwd


def project(pts, eye, look):
    right, down, fwd = basis(eye, look)
    d = pts - eye
    z = d @ fwd
    return np.stack([Z0 * (d @ right) / z + W / 2, Z0 * (d @ down) / z + H / 2], 1), z


def warp(img, src_quad, world_quad, eye, look, sigma=0.0):
    """Warp an RGBA (premultiplied float) texture region onto the screen as the 3D quad world_quad."""
    scr, z = project(np.array(world_quad, float), eye, look)
    if (z < 30).any():
        return None
    m = cv2.getPerspectiveTransform(np.float32(src_quad), np.float32(scr))
    out = cv2.warpPerspective(img, m, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT,
                              borderValue=(0, 0, 0, 0))
    if sigma > 0.6:
        out = cv2.GaussianBlur(out, (0, 0), sigma)
    return out


def over(src, dst):
    """src over dst (premultiplied); src None = nothing to draw."""
    if src is None:
        return dst
    a = src[:, :, 3:4]
    return src + dst * (1 - a)


def surf_to_np(surf):
    a = np.ndarray((CH, CW, 4), np.uint8, surf.get_data(), strides=(surf.get_stride(), 4, 1))
    return a.astype(np.float32) / 255.0            # BGRA, premultiplied


def layers(shot, T):
    """(background RGBA, subject RGBA, floor line or None) of a shot at story time T, on the big canvas."""
    t, d = T - shot["start"], shot["end"] - shot["start"]
    out = {}
    for mode in ("bg", "fg"):
        surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, CW, CH)
        ctx = cairo.Context(surf)
        ctx.translate(OX, OY)
        if mode == "bg":
            bsurf = cairo.ImageSurface(cairo.FORMAT_ARGB32, CW, CH)
            bctx = cairo.Context(bsurf)
            cam3d.STATE.update(layer="bg", bg_ctx=bctx, floor_y=None)
            shot["draw"](ctx, t, d)
            bsurf.flush()
            out["bg"], out["floor"] = surf_to_np(bsurf), cam3d.STATE.get("floor_y")
        else:
            cam3d.STATE.update(layer="fg")
            shot["draw"](ctx, t, d)
            surf.flush()
            out["fg"] = surf_to_np(surf)
    cam3d.STATE.update(layer=None)
    return out["bg"], out["fg"], out["floor"]


def overlay_np(shot, T):
    ov = shot.get("overlay")
    if not ov:
        return None
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
    ov(cairo.Context(surf), T - shot["start"], shot["end"] - shot["start"])
    surf.flush()
    return np.ndarray((H, W, 4), np.uint8, surf.get_data(), strides=(surf.get_stride(), 4, 1)).astype(np.float32) / 255


def frame(story, shot, T):
    bgl, fgl, floor = layers(shot, T)
    acc = np.zeros((H, W, 4), np.float32)
    for k in range(SUBFRAMES):
        ts = T + ((k + 0.5) / SUBFRAMES - 0.5) * SHUTTER / engine.FPS
        eye, look = camera_at(story, ts)
        img = np.zeros((H, W, 4), np.float32)
        img[:, :, :3] = bgl[OY + 40, OX:OX + W, :3].mean(0)      # past the set's edge: the set's own colour
        img[:, :, 3] = 1.0
        dfocus = np.linalg.norm(look - eye)
        X0, X1 = -OX - W / 2, CW - OX - W / 2                       # the canvas in world x at the subject plane
        if floor is not None:
            yf = floor - H / 2                                          # world y of the floor
            s = (Z0 + DW) / Z0
            ybase = OY + floor                                          # canvas row of the floor line
            wall_src = [(0, 0), (CW, 0), (CW, ybase), (0, ybase)]
            wall = [(X0 * s, yf - ybase * s, DW), (X1 * s, yf - ybase * s, DW), (X1 * s, yf, DW), (X0 * s, yf, DW)]
            sig = APERTURE * abs(1 - dfocus / np.linalg.norm(np.array([0, yf, DW]) - eye))
            img = over(warp(bgl, wall_src, wall, eye, look, sig), img)
            zn = -Z0 * 0.62
            fl_src = [(0, ybase), (CW, ybase), (CW, CH), (0, CH)]
            fl = [(X0 * s, yf, DW), (X1 * s, yf, DW), (X1 * s * 0.75, yf, zn), (X0 * s * 0.75, yf, zn)]
            img = over(warp(bgl, fl_src, fl, eye, look, sig * 0.5), img)
        else:
            s = (Z0 + DW * 1.4) / Z0
            Y0, Y1 = -OY - H / 2, CH - OY - H / 2
            wall_src = [(0, 0), (CW, 0), (CW, CH), (0, CH)]
            wall = [(X0 * s, Y0 * s, DW * 1.4), (X1 * s, Y0 * s, DW * 1.4), (X1 * s, Y1 * s, DW * 1.4),
                    (X0 * s, Y1 * s, DW * 1.4)]
            sig = APERTURE * abs(1 - dfocus / np.linalg.norm(np.array([0, 0, DW * 1.4]) - eye))
            img = over(warp(bgl, wall_src, wall, eye, look, sig), img)
        Y0, Y1 = -OY - H / 2, CH - OY - H / 2
        subj = [(X0, Y0, 0), (X1, Y0, 0), (X1, Y1, 0), (X0, Y1, 0)]
        img = over(warp(fgl, [(0, 0), (CW, 0), (CW, CH), (0, CH)], subj, eye, look), img)
        acc += img
    img = acc / SUBFRAMES
    img = over(overlay_np(shot, T), img)
    yy, xx = np.mgrid[0:H, 0:W]                                         # a soft vignette, as in the 2D render
    v = 1 - 0.18 * (((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2) / 2
    return np.clip(img[:, :, :3] * v[:, :, None] * 255, 0, 255).astype(np.uint8)


def main(story, t0, t1, out):
    mod = importlib.import_module(story)
    cam3d.STATE["off"] = True                      # the 2D camera moves are replaced by the real camera
    engine.set_voice(f"../output/{story}/voice.wav")
    ff = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "bgr24", "-s", f"{W}x{H}",
                           "-r", str(engine.FPS), "-i", "-", "-c:v", "libx264", "-crf", "18", "-pix_fmt", "yuv420p",
                           out], stdin=subprocess.PIPE)
    n = int(round((t1 - t0) * engine.FPS))
    for f in range(n):
        T = t0 + f / engine.FPS
        shot = max((s for s in mod.SHOTS if s["start"] <= T + 1e-9), key=lambda s: s["start"])
        engine._NOW.update(t=T)
        ff.stdin.write(frame(story, shot, T).tobytes())
        if f % 60 == 0:
            print(f"frame {f}/{n}", flush=True)
    ff.stdin.close()
    ff.wait()


if __name__ == "__main__":
    main(sys.argv[1], float(sys.argv[2]), float(sys.argv[3]), sys.argv[4])

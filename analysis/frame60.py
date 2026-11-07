#!/usr/bin/env python3
"""Frame-exact (every frame, 60 fps) motion analysis of a Style B video.

Reads EVERY frame (no sampling) at 180x320 and measures, frame by frame:
  cuts          exact cut frames (colour-histogram jump), shot lengths in frames
  holds         frames whose content does not change after removing the camera move: tells whether characters
                animate on 1s (every frame) or 2s/3s (each drawing held 2-3 frames)
  camera        best-fit similarity (zoom, pan, roll) between consecutive frames, from tracked corners
                (caption band left out); per shot: the zoom curve, punch-ins (start, frames, size, ease shape),
                shakes (frames, amplitude, frequency), whip pans (frames, speed)
  captions      caption pop curves: text width in the caption band, frame by frame after each caption change
                (start scale, frames to the peak, overshoot, frames to settle)
Usage: frame60.py video.mp4 out_prefix   -> out_prefix.json + a printed summary"""
import json
import subprocess
import sys

import cv2
import numpy as np

W, H = 180, 320
CAP0, CAP1 = 0.58, 0.72          # caption band (references: captions centred at y ~ 0.645 of the height)


def frames(path):
    fps = float(eval(subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
                                     "stream=r_frame_rate", "-of", "csv=p=0", path],
                                    capture_output=True, text=True).stdout.strip()))
    p = subprocess.Popen(["ffmpeg", "-v", "error", "-i", path, "-vf", f"scale={W}:{H}", "-f", "rawvideo",
                          "-pix_fmt", "bgr24", "-"], stdout=subprocess.PIPE)
    n = W * H * 3
    out = []
    while True:
        b = p.stdout.read(n)
        if len(b) < n:
            break
        out.append(np.frombuffer(b, np.uint8).reshape(H, W, 3))
    return fps, out


def hist(f):
    hsv = cv2.cvtColor(f, cv2.COLOR_BGR2HSV)
    h = cv2.calcHist([hsv], [0, 1, 2], None, [12, 6, 6], [0, 180, 0, 256, 0, 256])
    return cv2.normalize(h, h).flatten()


def similarity(g0, g1, mask):
    """Similarity transform g0 -> g1: (scale, angle, tx, ty) in px of the 180-wide frame, or None."""
    p0 = cv2.goodFeaturesToTrack(g0, 220, 0.01, 5, mask=mask)
    if p0 is None or len(p0) < 12:
        return None
    p1, st, _ = cv2.calcOpticalFlowPyrLK(g0, g1, p0, None, winSize=(15, 15), maxLevel=3)
    ok = st.flatten() == 1
    if ok.sum() < 12:
        return None
    M, inl = cv2.estimateAffinePartial2D(p0[ok], p1[ok], method=cv2.RANSAC, ransacReprojThreshold=1.5)
    if M is None or inl is None or inl.sum() < 10:
        return None
    s = float(np.hypot(M[0, 0], M[1, 0]))
    a = float(np.arctan2(M[1, 0], M[0, 0]))
    # translation of the frame centre
    cx, cy = W / 2, H / 2
    tx = float(M[0, 0] * cx + M[0, 1] * cy + M[0, 2] - cx)
    ty = float(M[1, 0] * cx + M[1, 1] * cy + M[1, 2] - cy)
    return s, a, tx, ty, M, float(inl.mean())


def caption_width(f):
    """Width (px of 180) of high-contrast text in the caption band (edge columns)."""
    band = cv2.cvtColor(f[int(H * CAP0):int(H * CAP1)], cv2.COLOR_BGR2GRAY)
    e = cv2.Canny(band, 80, 200)
    cols = (e > 0).sum(0)
    idx = np.where(cols >= 3)[0]
    if len(idx) < 6:
        return 0.0
    return float(idx[-1] - idx[0])


def analyse(path):
    fps, fr = frames(path)
    n = len(fr)
    gray = [cv2.cvtColor(f, cv2.COLOR_BGR2GRAY) for f in fr]
    hs = [hist(f) for f in fr]
    mask = np.full((H, W), 255, np.uint8)
    mask[int(H * CAP0):int(H * CAP1)] = 0
    rows = []
    for i in range(n):
        r = {"i": i, "t": round(i / fps, 4)}
        if i:
            r["hd"] = float(cv2.compareHist(hs[i - 1], hs[i], cv2.HISTCMP_BHATTACHARYYA))
            r["diff"] = float(np.abs(gray[i].astype(np.int16) - gray[i - 1]).mean())
            sim = similarity(gray[i - 1], gray[i], mask)
            if sim:
                s, a, tx, ty, M, q = sim
                r.update(scale=s, rot=a, tx=tx, ty=ty, q=q)
                warp = cv2.warpAffine(gray[i - 1], M, (W, H), borderMode=cv2.BORDER_REPLICATE)
                m = mask > 0
                r["resid"] = float(np.abs(gray[i].astype(np.int16) - warp)[m].mean())
            else:
                r["resid"] = r["diff"]
        r["capw"] = caption_width(fr[i])
        rows.append(r)

    # ---- cuts: a histogram jump that is not just a camera move
    cuts = [0]
    for r in rows[1:]:
        if r["hd"] > 0.32 and r["i"] - cuts[-1] >= 4:
            cuts.append(r["i"])
    shots = [(a, b) for a, b in zip(cuts, cuts[1:] + [n])]
    lens = np.array([b - a for a, b in shots])

    # ---- holds (animation on 1s / 2s): residual after removing the camera, inside shots, not at cuts
    inner = [r for r in rows[1:] if r["i"] not in cuts and r["i"] - 1 not in cuts]
    res = np.array([r["resid"] for r in inner])
    still = res < 0.35
    # the share of frames with no drawing change; and whether changes alternate (on twos)
    alt = 0
    seq = still.astype(int)
    for k in range(2, len(seq)):
        if seq[k] != seq[k - 1] and seq[k - 1] != seq[k - 2]:
            alt += 1
    # ---- camera per shot
    pin, shakes, whips = [], [], []
    for a, b in shots:
        seg = [rows[k] for k in range(a + 1, b) if "scale" in rows[k]]
        if len(seg) < 4:
            continue
        lz = np.cumsum([np.log(r["scale"]) for r in seg])
        vz = np.array([np.log(r["scale"]) for r in seg])
        txs = np.array([r["tx"] for r in seg])
        tys = np.array([r["ty"] for r in seg])
        # punch-ins: runs of fast zoom-in (> 0.25 %/frame) adding up to > 4 %
        k = 0
        while k < len(vz):
            if vz[k] > 0.0025:
                j = k
                while j < len(vz) and vz[j] > 0.0008:
                    j += 1
                tot = float(np.exp(vz[k:j].sum()) - 1)
                if tot > 0.04:
                    pk = int(np.argmax(vz[k:j]))
                    pin.append({"t": seg[k]["t"], "frames": j - k, "zoom": round(tot, 3),
                                "peak_at": round(pk / max(1, j - k - 1), 2), "since_cut": seg[k]["i"] - a})
                k = j
            k += 1
        # whip pans: >= 2 frames moving faster than 9 % of the width per frame
        fast = np.hypot(txs, tys) > 0.09 * W
        k = 0
        while k < len(fast):
            if fast[k]:
                j = k
                while j < len(fast) and fast[j]:
                    j += 1
                if j - k >= 2:
                    whips.append({"t": seg[k]["t"], "frames": j - k,
                                  "speed": round(float(np.hypot(txs[k:j], tys[k:j]).mean() / W * 100), 1)})
                k = j
            k += 1
        # shakes: translation that flips sign every 1-3 frames with amplitude > 0.6 % width
        sgn = np.sign(txs + 1e-9)
        flips = np.where((sgn[1:] != sgn[:-1]) & (np.abs(txs[1:]) > 0.006 * W))[0]
        if len(flips) >= 4:
            groups, g = [], [flips[0]]
            for f_ in flips[1:]:
                if f_ - g[-1] <= 4:
                    g.append(f_)
                else:
                    groups.append(g)
                    g = [f_]
            groups.append(g)
            for g in groups:
                if len(g) >= 4:
                    span = g[-1] - g[0] + 1
                    amp = float(np.abs(txs[g[0]:g[-1] + 1]).mean() / W * 100)
                    shakes.append({"t": seg[g[0]]["t"], "frames": int(span), "amp_pct": round(amp, 2),
                                   "hz": round(len(g) / 2 / (span / fps), 1)})
    # ---- caption pops: after each big jump of the caption width, track width / final width
    caps = []
    cw = np.array([r["capw"] for r in rows])
    for i in range(2, n - 20):
        if cw[i] > 12 and (cw[i - 1] < 4 or abs(cw[i] - cw[i - 1]) > 0.35 * max(cw[i], 1)) and \
                (not caps or i - caps[-1]["i"] > 8):
            final = np.median(cw[i + 10:i + 16])
            if final < 12:
                continue
            curve = [round(float(cw[i + k] / final), 2) for k in range(0, 12)]
            caps.append({"i": i, "t": round(i / fps, 3), "curve": curve})
    summary = {
        "fps": fps, "frames": n, "duration": round(n / fps, 2),
        "shots": len(shots), "shot_frames_median": int(np.median(lens)), "shot_frames_p10": int(np.percentile(lens, 10)),
        "shot_frames_p90": int(np.percentile(lens, 90)),
        "still_share": round(float(still.mean()), 3), "alternating_share": round(alt / max(1, len(seq)), 3),
        "punch_ins": len(pin), "punch_frames_median": float(np.median([p["frames"] for p in pin])) if pin else 0,
        "punch_zoom_median": float(np.median([p["zoom"] for p in pin])) if pin else 0,
        "punch_peak_at_median": float(np.median([p["peak_at"] for p in pin])) if pin else 0,
        "punch_since_cut_median": float(np.median([p["since_cut"] for p in pin])) if pin else 0,
        "shakes": len(shakes), "shake_frames_median": float(np.median([s["frames"] for s in shakes])) if shakes else 0,
        "shake_amp_median": float(np.median([s["amp_pct"] for s in shakes])) if shakes else 0,
        "shake_hz_median": float(np.median([s["hz"] for s in shakes])) if shakes else 0,
        "whips": len(whips), "whip_frames": [w["frames"] for w in whips],
        "caption_pops": len(caps),
        "caption_curve_median": [round(float(np.median([c["curve"][k] for c in caps])), 2) for k in range(12)] if caps else [],
    }
    return summary, {"cuts": [round(c / fps, 4) for c in cuts], "cut_frames": cuts, "punch_ins": pin,
                     "shakes": shakes, "whips": whips, "captions": caps, "rows": rows}


if __name__ == "__main__":
    summ, detail = analyse(sys.argv[1])
    json.dump({"summary": summ, **detail}, open(sys.argv[2] + ".json", "w"))
    for k, v in summ.items():
        print(f"{k:24s} {v}")

#!/usr/bin/env python3
"""Turn a YouTube Studio audience-retention export into drop points in SECONDS, with the line spoken there.

YouTube exports retention per 1 % of the video ("Detailed activity.csv": Started watching / Stopped watching per
position). This prints every position where an unusual number of viewers stopped, converted to seconds, with the
SRT line playing then, and groups neighbouring positions into drop zones.

Usage: retention.py <export folder or zip> <video.mp4 or duration_s> [subs.srt] [--min 1.0]
  --min  a position counts as a drop when its stops are >= this % of the starters (default 1.0)
Output: a table per zone (start-end s, share of starters lost, the lines), and the whole curve as CSV-like rows."""
import csv
import io
import os
import subprocess
import sys
import zipfile


def read_exports(src):
    files = {}
    if zipfile.is_zipfile(src):
        with zipfile.ZipFile(src) as z:
            for n in z.namelist():
                if n.lower().endswith(".csv"):
                    files[os.path.basename(n)] = z.read(n).decode("utf-8-sig")
    else:
        for n in os.listdir(src):
            if n.lower().endswith(".csv"):
                files[n] = open(os.path.join(src, n), encoding="utf-8-sig").read()
    return files


def srt_lines(path):
    out = []
    if not path:
        return out
    for b in open(path, encoding="utf-8-sig").read().strip().split("\n\n"):
        L = b.strip().splitlines()
        if len(L) < 3 or "-->" not in L[1]:
            continue
        f = lambda s: sum(float(x) * m for x, m in zip(s.strip().replace(",", ".").split(":"), (3600, 60, 1)))
        a, c = L[1].split("-->")
        txt = " ".join(L[2:])
        if "(Transcribed by" in txt:
            txt = txt.split(")", 1)[-1].strip()
        out.append((f(a), f(c), txt))
    return out


def line_at(lines, t, pad=0.0):
    hit = [x for a, b, x in lines if a - pad <= t <= b + pad]
    if hit:
        return " / ".join(hit)
    before = [x for a, b, x in lines if b < t]
    return f"(gap after: {before[-1]})" if before else "(before the first word)"


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    mn = float(sys.argv[sys.argv.index("--min") + 1]) if "--min" in sys.argv else 1.0
    if "--min" in sys.argv:
        args = [a for a in args if a != sys.argv[sys.argv.index("--min") + 1]]
    src, vid = args[0], args[1]
    srt = args[2] if len(args) > 2 else None
    try:
        dur = float(vid)
    except ValueError:
        dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0",
                                    vid], capture_output=True, text=True).stdout)
    files = read_exports(src)
    det = next((v for k, v in files.items() if k.lower().startswith("detailed activity")), None)
    if det is None:
        sys.exit("no 'Detailed activity.csv' in the export")
    rows = list(csv.DictReader(io.StringIO(det)))
    start = int(rows[0]["Started watching"] or 0)
    lines = srt_lines(srt)
    print(f"duration {dur:.2f} s, starters {start}, 1 % = {dur / 100:.2f} s")
    allr = next((v for k, v in files.items() if k.lower() == "all.csv"), None)
    ret = {}
    if allr:
        for r in csv.DictReader(io.StringIO(allr)):
            ret[int(r["Video position (%)"])] = float(r["Absolute audience retention (%)"])
    marked = []
    for r in rows:
        p = int(r["Video position (%)"])
        s = int(r["Stopped watching"] or 0)
        share = 100 * s / max(1, start)
        marked.append((p, p * dur / 100, s, share))
    zones, cur = [], []
    for p, t, s, share in marked:
        if share >= mn and p < 98:                     # the last 2 % is the natural end / loop point
            cur.append((p, t, s, share))
        elif cur:
            zones.append(cur)
            cur = []
    if cur:
        zones.append(cur)
    print("\nDROP ZONES (stops >= %.1f %% of the starters per 1 %% of the video; first 2 s = the normal swipe)" % mn)
    for z in zones:
        t0, t1 = z[0][1], z[-1][1] + dur / 100
        lost = sum(x[3] for x in z)
        peak = max(z, key=lambda x: x[2])
        print(f"\n{t0:5.1f}-{t1:5.1f} s  lost {lost:4.1f} % of starters  (peak {peak[1]:.1f} s, {peak[2]} stops)")
        seen = []
        for a, b, x in lines:
            if b >= t0 - 3.0 and a <= t1:
                seen.append(f"    {a:5.2f}-{b:5.2f}  {x}")
        print("\n".join(seen) if seen else "    (no SRT given)")
    print("\nCURVE  pos | sec | retention % | stopped | line")
    for p, t, s, share in marked:
        print(f"{p:3d} | {t:5.1f} | {ret.get(p, float('nan')):6.1f} | {s:5d} | {line_at(lines, t)[:70]}")


if __name__ == "__main__":
    main()

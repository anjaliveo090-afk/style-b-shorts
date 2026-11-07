"""Cut a shorter voice out of a long one (a Short from a long video) so the joins are not heard.

Each segment is given by its OLD start and end time (SRT cue start of its first line, cue end of its last line). For
every segment the tool finds the real speech onset / offset around those times (10 ms RMS, threshold relative to the
voice), keeps a short natural lead-in and release, and joins the pieces with a 30 ms equal-power crossfade so that the
pause between the last word of one piece and the first word of the next is PAUSE seconds (the voice's own typical
sentence pause), never a hard edit. The SRT and the word times are retimed to the new voice.

  python3 assembler/cut_voice.py <voice> <subs.srt> <words.json or -> <out_dir> <seg> [<seg> ...] [--pause 0.30]
      seg = old_start:old_end   (seconds; old_end = the cue END of the segment's last line)

Writes <out_dir>/voice.wav, subs.srt, words/srt_words.json (if words were given) and segments.json
([{old_start, old_end, new_start, new_end, onset, offset}], with onset/offset = first/last speech in OLD time)."""
import argparse
import json
import os
import subprocess
import wave

import numpy as np

SR = 44100
HOP = 0.01


def load(path):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-ac", "2", "-ar", str(SR), "-f", "f32le", "-"],
                         capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.float32).reshape(-1, 2).astype(np.float64)


def ts(s):
    h, m, r = s.strip().split(":")
    return int(h) * 3600 + int(m) * 60 + float(r.replace(",", "."))


def fmt(t):
    t = max(0.0, t)
    ms = int(round(t * 1000))
    return f"{ms // 3600000:02d}:{ms // 60000 % 60:02d}:{ms // 1000 % 60:02d},{ms % 1000:03d}"


def read_srt(path):
    cues = []
    for b in open(path, encoding="utf-8").read().strip().split("\n\n"):
        lines = b.strip().split("\n")
        if len(lines) >= 3 and "-->" in lines[1]:
            a, e = lines[1].split("-->")
            cues.append((ts(a), ts(e), " ".join(lines[2:])))
    return cues


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("voice")
    ap.add_argument("srt")
    ap.add_argument("words")
    ap.add_argument("out")
    ap.add_argument("segs", nargs="+")
    ap.add_argument("--pause", type=float, default=0.30, help="silence between two pieces, word to word")
    ap.add_argument("--start", type=float, default=0.20, help="lead silence before the first word")
    ap.add_argument("--thr", type=float, default=-34.0, help="speech threshold, dBFS of a 10 ms frame")
    a = ap.parse_args()

    x = load(a.voice)
    mono = x.mean(1)
    f = int(SR * HOP)
    n = len(mono) // f
    db = 20 * np.log10(np.sqrt((mono[:n * f].reshape(n, f) ** 2).mean(1)) + 1e-9)
    loud = db >= a.thr

    cue_starts = sorted(c[0] for c in read_srt(a.srt))

    def quietest(lo, hi, near):
        """The cut point: the deepest 10 ms frame in [lo, hi] (the gap between two lines); of the frames within
        4 dB of it, the one nearest to `near` (so a breath or a stop consonant earlier in the gap is not chosen)."""
        i0, i1 = max(0, int(lo / HOP)), min(n - 1, int(hi / HOP))
        if i1 <= i0:
            return lo
        seg = db[i0:i1 + 1]
        cand = np.nonzero(seg <= seg.min() + 4.0)[0] + i0
        return cand[np.argmin(np.abs(cand * HOP - near))] * HOP

    def first_loud(t0, t1):
        for i in range(int(t0 / HOP), min(n - 2, int(t1 / HOP))):
            if loud[i] and loud[i + 1]:
                return i * HOP
        return t0

    def last_loud(t0, t1):
        for i in range(min(n - 1, int(t1 / HOP)), int(t0 / HOP), -1):
            if loud[i]:
                return (i + 1) * HOP
        return t1

    def start_of(t):
        """(cut_in, onset) for a line whose SRT start is t."""
        if t < 0.35:
            return 0.0, first_loud(0.0, t + 0.5)
        cut = quietest(t - 0.3, t + 0.04, t)
        return cut, first_loud(cut, cut + 0.5)

    def end_of(t):
        """(offset, cut_out) for a line whose SRT end is t (SRT ends are often early: look up to the next line)."""
        nxt = next((c for c in cue_starts if c > t - 0.05), t + 0.6)
        hi = min(len(mono) / SR - HOP, max(nxt, t + 0.15) + 0.05)
        # the LAST real pause before the next line: a dip inside a word (a stop consonant, "re-STORED") is earlier
        i0, i1 = max(1, int((t - 0.1) / HOP)), min(n - 2, int(hi / HOP))
        dips = [i for i in range(i0, i1 + 1)
                if db[i] <= -45 and db[i] <= db[i - 1] and db[i] <= db[i + 1]]
        cut = min(dips, key=lambda i: abs(i * HOP - nxt)) * HOP if dips else quietest(t - 0.1, hi, nxt)
        return last_loud(cut - 0.8, cut), cut

    segs = [tuple(float(v) for v in s.split(":")) for s in a.segs]
    pieces, info = [], []
    for s0, s1 in segs:
        cut_in, on = start_of(s0)
        off, cut_out = end_of(s1)
        lead = min(0.12, on - cut_in)                 # a natural lead-in, never into the previous line
        rel = min(0.18, cut_out - off)                # the decay of the last word, then a fade
        i0, i1 = int((on - lead) * SR), int((off + rel) * SR)
        p = x[i0:i1].copy()
        nf = int(SR * 0.008)
        p[:nf] *= np.linspace(0, 1, nf)[:, None]
        nr = int(SR * 0.03)
        p[-nr:] *= np.linspace(1, 0, nr)[:, None]
        pieces.append(p)
        info.append(dict(old_start=on - lead, old_end=off + rel, onset=on, offset=off, lead=lead, rel=rel))

    out = [np.zeros((int(SR * max(0.0, a.start - info[0]["lead"])), 2))]
    t = len(out[0]) / SR
    for k, (p, d) in enumerate(zip(pieces, info)):
        if k:
            gap = a.pause - info[k - 1]["rel"] - d["lead"]
            if gap > 0:
                out.append(np.zeros((int(SR * gap), 2)))
                t += int(SR * gap) / SR
            else:                                   # overlap the two quiet edges (they are faded)
                ov = int(SR * -gap)
                tail = out[-1]
                m = min(ov, len(tail), len(p))
                tail[-m:] += p[:m]
                p = p[m:]
                t -= m / SR
        d["new_start"] = t
        out.append(p)
        t += len(p) / SR
        d["new_end"] = t
    y = np.concatenate(out)

    os.makedirs(a.out, exist_ok=True)
    with wave.open(os.path.join(a.out, "voice.wav"), "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((np.clip(y, -1, 1) * 32767).astype(np.int16).tobytes())

    def remap(t_old, end=False):
        for d in info:
            lo, hi = d["old_start"] - 0.05, d["old_end"] + (0.3 if end else -0.12)
            if lo <= t_old <= hi:
                v = t_old - d["old_start"] + d["new_start"]
                return min(max(v, d["new_start"]), d["new_end"])
        return None

    srt = []
    for c0, c1, txt in read_srt(a.srt):
        n0 = remap(c0)
        if n0 is None:
            continue
        n1 = remap(c1, True)
        if n1 is None or n1 <= n0:
            n1 = next(d["new_end"] for d in info if d["new_start"] - 1e-6 <= n0 <= d["new_end"] + 1e-6)
        srt.append((n0, n1, txt))
    with open(os.path.join(a.out, "subs.srt"), "w", encoding="utf-8") as fh:
        for i, (c0, c1, txt) in enumerate(srt, 1):
            fh.write(f"{i}\n{fmt(c0)} --> {fmt(c1)}\n{txt}\n\n")
    if a.words != "-":
        words = []
        for wd in json.load(open(a.words)):
            n0 = remap(wd["start"])
            if n0 is not None:
                n1 = remap(wd["end"], True) or n0 + 0.2
                words.append(dict(word=wd["word"], start=round(n0, 3), end=round(max(n1, n0 + 0.05), 3),
                                  old_start=wd["start"]))
        os.makedirs(os.path.join(a.out, "words"), exist_ok=True)
        json.dump(words, open(os.path.join(a.out, "words", "srt_words.json"), "w"), indent=0)
    json.dump([{k: round(v, 3) for k, v in d.items()} for d in info], open(os.path.join(a.out, "segments.json"), "w"),
              indent=1)
    print(f"wrote {a.out}/voice.wav: {len(y) / SR:.2f} s from {len(segs)} pieces; {len(srt)} cues")
    for d in info:
        print(f"  old {d['old_start']:7.2f}-{d['old_end']:7.2f} -> new {d['new_start']:6.2f}-{d['new_end']:6.2f}"
              f"  (lead {d['lead']:.2f}, release {d['rel']:.2f})")


if __name__ == "__main__":
    main()

"""Re-render only some shots of a story and splice them into its existing animation (CLAUDE.md step 8:
"patch only the shots asked about, never regenerate the rest").

  python3 patch_render.py <story> <old_animation.mp4> <new_animation.mp4> <voice> <shot_start> [<shot_start> ...]

- Imports the story, runs safezone.fit exactly like its __main__, loads the voice for lip-sync.
- For each listed shot (by its start time) renders the frames whose time falls in [start, end) with
  engine.render(frames=...), merging neighbouring shots into one range.
- Builds the new animation in one ffmpeg pass: untouched frames are copied from the old animation by frame index
  (trim=start_frame/end_frame), patched ranges come from the new renders. Frame count and frame rate stay the same.
Re-assemble with assembler/assemble.py afterwards (the voice, music and SFX do not change)."""
import importlib
import math
import os
import subprocess
import sys
import tempfile

if len(sys.argv) > 1:                            # a 16:9 story sets STYLEB_ASPECT before its imports: do the same
    _src = os.path.join(os.path.dirname(os.path.abspath(__file__)), sys.argv[1] + ".py")
    if os.path.exists(_src) and 'STYLEB_ASPECT"] = "16x9"' in open(_src).read():
        os.environ["STYLEB_ASPECT"] = "16x9"

import engine     # noqa: E402
import safezone   # noqa: E402


def ranges_for(shots, total, fps, starts):
    want = sorted(set(round(s, 4) for s in starts))
    rs = []
    for i, sh in enumerate(shots):
        if round(sh["start"], 4) not in want:
            continue
        end = shots[i + 1]["start"] if i + 1 < len(shots) else total
        a = math.ceil(sh["start"] * fps - 1e-6)
        b = math.ceil(end * fps - 1e-6) if i + 1 < len(shots) else int(round(total * fps))
        if rs and rs[-1][1] == a:
            rs[-1] = (rs[-1][0], b)
        else:
            rs.append((a, b))
    return rs


def frame_count(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-count_frames", "-select_streams", "v:0", "-show_entries",
                          "stream=nb_read_frames", "-of", "csv=p=0", path], capture_output=True, text=True).stdout
    return int(out.strip())


def main():
    story, old, new, voice = sys.argv[1:5]
    starts = [float(x) for x in sys.argv[5:]]
    mod = importlib.import_module(story)
    if engine.ASPECT != "16x9":                  # long 16:9 videos are not fitted to the Shorts safe zone
        safezone.fit(mod.SHOTS, mod, verbose=False)
    engine.set_voice(voice)
    fps = engine.FPS
    n = frame_count(old)
    rs = ranges_for(mod.SHOTS, mod.TOTAL, fps, starts)
    print(f"{len(rs)} ranges, {sum(b - a for a, b in rs)} of {n} frames re-rendered")
    tmp = tempfile.mkdtemp()
    parts = []                       # (kind, a, b, path)
    for k, (a, b) in enumerate(rs):
        p = os.path.join(tmp, f"patch_{k:03d}.mp4")
        engine.render(mod.SHOTS, mod.TOTAL, p, xfade=0.0, grain=2, fade_out=0.0, fade_in=0.0, frames=(a, b))
        parts.append((a, b, p))
    # each untouched piece reads the old video through its OWN input: one shared input trimmed twice makes ffmpeg
    # queue every frame of the later piece in memory (killed for lack of RAM on a 1080p long video)
    inputs, filters, labels, pos, idx = [], [], [], 0, 0
    for a, b, p in parts + [(n, n, None)]:
        if a > pos:
            inputs += ["-i", old]
            filters.append(f"[{idx}:v]trim=start_frame={pos}:end_frame={a},setpts=PTS-STARTPTS[s{len(labels)}]")
            labels.append(f"[s{len(labels)}]")
            idx += 1
        if p:
            inputs += ["-i", p]
            filters.append(f"[{idx}:v]setpts=PTS-STARTPTS[s{len(labels)}]")
            labels.append(f"[s{len(labels)}]")
            idx += 1
            pos = b
    filters.append(f"{''.join(labels)}concat=n={len(labels)}:v=1:a=0,fps={fps}[v]")
    subprocess.run(["ffmpeg", "-y", "-v", "error", *inputs, "-filter_complex", ";".join(filters), "-map", "[v]",
                    "-c:v", "libx264", "-preset", "medium", "-crf", "17", "-pix_fmt", "yuv420p", new], check=True)
    print(f"wrote {new}: {frame_count(new)} frames (old {n})")


if __name__ == "__main__":
    main()

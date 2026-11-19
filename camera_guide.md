# Camera guide (3D camera moves for our 2D Shorts)

Learned 2026-11-19 from the camera chapter of the user's 3D-animator reference ("only camera": nothing about light,
models, sound or look was taken; our Style B look stays). Implemented in `animator/cam3d.py`.

## The rules
1. **One move = one rail + one eased value.** Every shot's camera is one cubic Bezier rail (START, C1, C2, END) in
   camera space (x, y in px at the subject's depth, d = dolly towards the subject), driven by ONE progress value
   `p = easeInOut(...)`. Change the shape with the control points, the timing only with the easing.
2. **Curved paths, not robot moves.** A dolly gets a little orbit in it (the PUSH rail drifts 18 px sideways while it
   pushes); an orbit gets a little dolly (d rises to 0.035 mid-arc). "Right, then forward" reads as a robot.
3. **No zoom.** The lens never changes: to make something bigger, the camera moves closer (dolly). The old
   "vertigo" (dolly zoom = a lens change) is now `rush`, a fast push that lands (ease-out), for shocks.
4. **Parallax comes from depth, not hand-set numbers.** Each layer has a depth factor k (subject 1.0, background
   `KB = 0.3`); with the aim weight a (1 = the camera keeps looking at the subject, 0 = it does not turn):
   `shift = (a - k) * (x, y)`, `scale = 1 / (1 - k * d)`. An orbit (a = 1) keeps the subject still and slides the
   background; a track (a = 0) slides the subject more than the background.
5. **Thin depth of field, racked with the dolly.** Focus on what the viewer reads (the subject). The background
   softens as the camera gets closer (`dof = 0.35 + 3 d`, at most 0.75; downsample at most ~2.2x). Huge blur looks
   like a toy.
6. **Cut on motion.** The rail runs 0.25 s before and after the shot (`LEAD`), so the camera is moving at every cut.
   (The reference also holds 0.3-0.5 s at the start and end of LONG moves; our shots are ~1.2 s, so we cut on motion.)
7. **Continuous rails across cuts in one place.** When consecutive shots are in the same set, keep the move going
   the same way (school_short: every gym shot of the boss fight orbits right), so the cut feels like one camera.
8. **Comfort check.** `cd animator && python3 cam3d.py <story>` prints the camera speed per frame of every shot and
   flags a JERK where the speed changes suddenly between two frames. Must print `0 jerky moves`. Smooth a jerk by
   moving control points, not by adding keys. One direction change per move at most.

## Moves (`CAM3D = {shot start: move}` in the story)
| Move | Rail | Aim | Use for |
|---|---|---|---|
| `orbit_l` / `orbit_r` | x -70 → 70 with a small dolly arc | 1 | a reaction, a character, a prop being shown; a fight (keep one direction) |
| `push` / `pull` | dolly to d 0.105 with an 18 px curve | 1 | a reveal, a key word, a UI line / leaving a moment |
| `rush` | fast push (ease-out) to d 0.14 | 1 | a shock: a scream, "DELETED", "MOM!" |
| `crane_up` / `crane_down` | y +46 → -46 | 0.6 | looking up at something (a speaker, a building), a crowd |
| `track_l` / `track_r` | x -34 → 34 | 0 | someone walking or flying across |
| `low` | the camera sinks 36 px and pushes, anchored at the feet | 0.5 | an entrance, authority, a hero moment, the boss |

Still part of our style (kept): the punch-ins and bumps on hits (`visual_grammar.md` section 2b) ride on top of the rail.

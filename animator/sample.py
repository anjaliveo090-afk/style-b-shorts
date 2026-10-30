"""Sample story in Style B (the template to copy for new voiceovers).

Narration (made up, ~22 s, same tone as the references):
  What if your mom put a password on Roblox? / Day one. You type: password. Wrong! /
  Day two. You try her birthday. Locked for one hour! / Day three. You find a sticky note
  on the fridge. "Mom is the boss, one, two, three." Access granted! / You beat the hardest
  obby in one jump... but the leaderboard says: Number one, Mom. /
  Comment loop if your mom is a pro gamer.

How it follows visual_grammar.md:
- a hard cut on every phrase (~1.0-1.3 s), a literal visual for each (padlock, keyboard,
  cake, fridge, sticky note, obby, leaderboard, comments);
- the camera holds or drifts and *punches in* on the key word (short key moves of 0.12-0.2 s);
- expressions snap on key words; "DAY N" painted chapter text; game UI;
- SFX: about one per visual event, at measured Style B levels (sound_design.md);
- ends on the first frame, so the Short loops (render fade_in=0, fade_out=0).

Run (see CLAUDE.md for the full pipeline):
  python3 sample.py out.mp4 cues.json [first_frame last_frame]"""
import math
import sys

import engine
import sets as st
import style
from engine import clamp, ease, hexc, keyed, lerp, pop, render
from sets import label
from style import Block

TOTAL = 22.3
engine.LIPSYNC = False            # the references do not lip-sync
engine.DRIFT = (0.02, 5, -3)      # calm creep while holding (measured camera median 2-5 % width/s)
engine.ENERGY = 3.0               # livelier idle bounce/sway (non-camera motion target 5-8)
SFX_GAIN = 0.17                   # all cue volumes x this: SFX median ~-3 dB vs the voice (sound_design.md)

KID, KID_GAME, MOM = style.KID, style.KID_GAME, style.MOM
MOM_GAMER = Block("#ff7a8a", pants="#5a4fb0", skin="#c89f82", hair="pony", hair_col="#a0442a", outfit="cardigan",
                  lashes=True, shoes="dark", headset="rgb", crown=True)
WIN_W, WIN_H = 720, 1280


# ================================================================ helpers
def laptop_screen(typed="", wrong=0.0, granted=0.0, title="ENTER PASSWORD"):
    return lambda c, x, y, w, h, T: st.login_screen(c, x, y, w, h, T, typed=typed, wrong=wrong, granted=granted,
                                                    title=title)


def bedroom_kid(ctx, T, kid_expr, look=0.4, arms=("hold", "hold"), door_x=520, stand_x=430):
    """The kid sitting up in bed with the laptop (lid back to camera)."""
    st.night_bedroom(ctx, T, door_x=door_x, stand_x=stand_x)
    KID.draw(ctx, 220, 1150, 1.5, kid_expr, T, arms=arms, look=look, pose="sit")
    st.checker(ctx, -60, 1075, 470, 200, n=7)          # blanket over the lap
    st.laptop(ctx, 220, 1105, 0.72, T, back=True)


FACE_S = 4.2                                   # close-up scale: head ~55% of the frame width
FACE_Y = 560 + 2.5 * Block.HW * 64 * FACE_S     # puts the head centre at y 560
FACE_KEEP = [(165, 300, 555, 760)]              # the face box safezone keeps on screen


def kid_face(ctx, T, expr, bg="night", look=0.0, arms=("down", "down")):
    """Close-up: head and chest fill the frame."""
    if bg == "night":
        st.night_wall(ctx, 2000)
        st.window(ctx, 470, 120, 230, 300, T, night=True)
        st.glow(ctx, 360, 900, 520, (0.55, 0.8, 1.0), 0.35)   # laptop glow on the face
    elif bg == "red":
        st.burst(ctx, T, "#ff8a7a", "#c8283a", cy=640)
    KID.draw(ctx, 360, FACE_Y, FACE_S, expr, T, arms=arms, look=look)


# ================================================================ hook
def s_hook(ctx, t, d, T0=0.0, frozen=False):
    T = T0 + (0.0 if frozen else t)
    bedroom_kid(ctx, T, keyed(T, [(0, "happy"), (0.55, "shock")]), door_x=375, stand_x=640)
    MOM.draw(ctx, 462, 1060, 1.2, "smirk", T, arms=("show", "down"), look=-0.6)
    st.padlock(ctx, 330, 650, 0.25, pop(T - 0.6) if not frozen else 1.0)


def s_lock(ctx, t, d):
    T = 1.05 + t
    st.night_wall(ctx, 2000)
    st.laptop(ctx, 360, 1060, 1.55, T, laptop_screen())
    k = clamp((T - 1.08) / 0.12)                      # the padlock slams onto the screen
    if T > 1.2:
        st.impact_star(ctx, 360, 660, 260, T - 1.2)
    st.padlock(ctx, 360, lerp(-200, 640, k * k), 0.75, 1.0)


def s_roblox(ctx, t, d):
    T = 1.85 + t
    kid_face(ctx, T, "shock", look=0.0)
    label(ctx, "ROBLOX?!", 360, 330, 70, fg=st.YELLOW, scale=pop(T - 1.9))


# ================================================================ day 1
def s_day1(ctx, t, d):
    T = 2.72 + t
    st.night_wall(ctx, 2000)
    st.laptop(ctx, 420, 1000, 1.25, T, laptop_screen())
    style.back_figure(ctx, 150, 1260, 2.4, KID.hair_col, KID.shirt)
    st.day_text(ctx, "DAY 1", 360, 300, T - 2.74)


def s_type(ctx, t, d):
    T = 3.55 + t
    st.night_wall(ctx, 2000)
    word = "password"
    n = int(clamp((T - 3.9) / 0.55) * len(word))
    st.monitor(ctx, 360, 640, 1.0, T, laptop_screen(typed=word[:n]))
    st.keyboard(ctx, 360, 960, 1.0, T, mash=1.0 if 3.9 < T < 4.5 else 0.0)
    for side in (-1, 1):   # the kid's blocky hands hammering the keys
        bob = abs(math.sin(T * 24 + side)) * 18 if 3.9 < T < 4.5 else 0
        style.block(ctx, 360 + side * 150 - 50, 1010 - bob, 100, 230, 14, KID.shirt, 4)


def s_wrong(ctx, t, d):
    T = 4.72 + t
    st.night_wall(ctx, 2000)
    st.monitor(ctx, 360, 900, 1.0, T, laptop_screen(typed="password", wrong=clamp((T - 4.77) / 0.1)))
    st.red_x(ctx, 360, 600, 170, (T - 4.77) / 0.25)
    st.tint(ctx, (1, 0.1, 0.1), 0.12 * math.exp(-4 * max(0, T - 4.77)))
    label(ctx, "WRONG!", 360, 300, 84, fg=st.RED, scale=pop(T - 4.8))


# ================================================================ day 2
def s_day2(ctx, t, d):
    T = 5.58 + t
    bedroom_kid(ctx, T, keyed(T, [(0, "sad"), (6.0, "determined")]), look=0.6)
    st.day_text(ctx, "DAY 2", 380, 330, T - 5.62)


def s_cake(ctx, t, d):
    T = 6.48 + t
    st.night_wall(ctx, 2000)
    st.block(ctx, -100, 980, 920, 400, 0, hexc("#7a6aa8"), 5, gloss=False)
    typed = "MOM'S BDAY"[:int(clamp((T - 6.6) / 0.35) * 10)]
    st.monitor(ctx, 300, 980, 1.0, T, laptop_screen(typed=typed))
    sc = pop(T - 6.95)
    if sc > 0:
        ctx.save()
        ctx.translate(540, 1040)
        ctx.scale(sc, sc)
        st.cake(ctx, 0, 0, 1.0, T)
        ctx.restore()
        st.sparkles(ctx, T, 540, 720, spread=170, n=7, seed=2, c=st.YELLOW)
    label(ctx, "BIRTHDAY?", 360, 270, 60, fg=st.PINK, scale=pop(T - 7.0))


def s_locked(ctx, t, d):
    T = 7.72 + t
    st.burst(ctx, T, "#ff8a7a", "#a8202e", cy=600)
    k = clamp((T - 7.74) / 0.14)
    if T > 7.88:
        st.impact_star(ctx, 360, 640, 300, T - 7.88)
    st.padlock(ctx, 360, lerp(-300, 600, k * k), 1.4, 1.0)
    secs = max(0, 3600 - int((T - 7.9) * 7))
    if T > 7.9:
        label(ctx, f"{secs // 60}:{secs % 60:02d}", 360, 950, 90, bg=st.UI_DARK, fg=st.RED, scale=pop(T - 7.9))


def s_hour(ctx, t, d):
    T = 8.30 + t
    kid_face(ctx, T, "cry", bg="red")
    label(ctx, "1 HOUR?!", 360, 330, 76, fg=(1, 1, 1), scale=pop(T - 8.35))


# ================================================================ day 3
def s_day3(ctx, t, d):
    T = 9.05 + t
    st.kitchen(ctx, T)
    k = ease((T - 9.1) / 0.9)
    KID.draw(ctx, lerp(120, 300, k), 1180, 1.2, "determined", T, pose="walk" if k < 1 else "stand",
             walk_phase=T * 2.2, arms=("down", "down"), look=0.6)
    st.day_text(ctx, "DAY 3", 360, 330, T - 9.08)


def s_find(ctx, t, d):
    T = 10.0 + t
    st.kitchen(ctx, T)
    st.fridge(ctx, 560, 1080, T, note_glow=clamp((T - 10.35) / 0.2))
    KID.draw(ctx, 300, 1180, 1.2, keyed(T, [(0, "neutral"), (10.35, "shock")]), T, arms=("down", "point"),
             look=0.8)
    if T > 10.35:
        st.sparkles(ctx, T, 570, 620, spread=90, n=6, seed=5, c=st.YELLOW, size=22)


def s_stars(ctx, t, d):
    T = 11.1 + t
    kid_face(ctx, T, "stars", look=0.6)
    st.glow(ctx, 640, 700, 320, (1, 0.95, 0.5), 0.5)


def s_note(ctx, t, d):
    T = 11.87 + t
    st.fridge(ctx, 360, 1700, T, note=False, w=1100, h=1900)
    st.glow(ctx, 360, 640, 500, (1, 0.95, 0.6), 0.45)
    digits = "".join(c for c, tc in (("1", 12.6), ("2", 12.85), ("3", 13.1)) if T >= tc)
    st.sticky_note(ctx, 360, 640, 1.6, ["MOM IS", "THE BOSS", digits or " "],
                   shown=[T - 11.89, T - 12.26, T - 12.6], size=58, tilt=-0.03)


def s_granted(ctx, t, d):
    T = 13.62 + t
    st.burst(ctx, T, "#b8ffb0", "#2e9c46", cy=560)
    st.monitor(ctx, 360, 820, 0.9, T, laptop_screen(typed="MOMISTHEBOSS123", granted=1.0, title="WELCOME!"))
    st.check_mark(ctx, 360, 330, 80, T - 13.65)
    st.confetti(ctx, T, 13.97, n=30)
    KID.draw(ctx, 360, 1400, 1.5, "stars", T, arms=("up", "up"))
    label(ctx, "ACCESS GRANTED!", 360, 460, 52, bg=st.GREEN, scale=pop(T - 13.97))


# ================================================================ game
def s_obby(ctx, t, d):
    T = 14.9 + t
    tops = st.obby(ctx, T, y_top=900)
    KID_GAME.draw(ctx, tops[0][0], tops[0][1], 1.15, keyed(T, [(0, "determined"), (15.27, "smug")]), T,
                  arms=("cross", "cross"))
    st.stage_pill(ctx, 360, 300, "HARDEST OBBY", s=pop(T - 15.27))
    label(ctx, "0.01% BEAT IT", 360, 400, 34, bg=st.RED, scale=pop(T - 15.68))


def s_jump(ctx, t, d):
    T = 16.05 + t
    st.game_sky(ctx)
    st.block_clouds(ctx, T)
    st.lava(ctx, 1100, T)
    for i in range(7):
        st.platform(ctx, -60 + i * 150, 960 - i * 20, 100, ("#2cd5fc", "#fa3a9f", "#f7e04a", "#a694e1")[i % 4],
                    num=94 + i)
    st.platform(ctx, 560, 820, 200, "#4fd16a")
    st.finish_flag(ctx, 690, 820, 0.9, T)
    p = clamp((T - 16.12) / 0.5)
    x = lerp(40, 640, ease(p))
    y = lerp(960, 820, p) - math.sin(math.pi * p) * 420
    if 0 < p < 1:
        st.speed_lines(ctx, T, x, y - 150, n=16, r0=160, r1=500, a=0.35)
    KID_GAME.draw(ctx, x, y, 1.0, "smug" if p < 1 else "happy", T, arms=("up", "up") if p < 1 else ("up", "down"),
                  pose="jump" if 0 < p < 1 else "stand")
    if p >= 1:
        st.dust(ctx, 640, 820, (T - 16.62) / 0.4)
        st.confetti(ctx, T, 16.62, n=40)
    label(ctx, "ONE JUMP!", 360, 330, 72, fg=st.YELLOW, scale=pop(T - 16.31))


def _row_face(skin, hair, crown=False):
    return lambda c, x, y, T: st.face_icon(c, x, y, 26, skin, hair, crown)


def s_board(ctx, t, d):
    T = 17.0 + t
    st.burst(ctx, T, "#7fb8ff", "#2f4bb0", cy=560)
    reveal = T >= 18.33
    rows = [("MOM" if reveal else "???", "999,999" if reveal else "???", _row_face("#c89f82", "#a0442a", True)
             if reveal else None),
            ("You", "12,450", _row_face("#e6ddd6", "#4a2f22")),
            ("ObbyKing", "9,871", _row_face("#e9c22c", "#e9c22c")),
            ("BlockPro", "7,302", None)]
    st.leaderboard(ctx, 360, 260, 1.05, rows, T, k_rows=[T - 17.1 if not reveal else T - 18.33, T - 17.3,
                                                         T - 17.45, T - 17.6])
    if reveal:
        st.shockwave(ctx, 360, 470, (T - 18.33) / 0.5, r_max=420)
        st.sparkles(ctx, T, 360, 450, spread=260, n=10, seed=7, c=st.YELLOW)
    KID_GAME.draw(ctx, 360, 1005, 0.62, "scared" if reveal else "worried", T, arms=("down", "down"), look=-0.3)


def s_mom(ctx, t, d):
    T = 18.76 + t
    st.burst(ctx, T, "#ffe27a", "#f29a2e", cy=520)
    MOM_GAMER.draw(ctx, 360, FACE_Y - 60, FACE_S * 0.9, keyed(T, [(0, "smug"), (19.2, "wink")]), T,
                   arms=("show", "down"))
    label(ctx, "#1 MOM", 360, 300, 74, bg=st.PINK, scale=pop(T - 18.8))


# ================================================================ ending
def s_comments(ctx, t, d):
    T = 19.62 + t
    st.night_bedroom(ctx, T)
    typed = "LOOP"[:int(clamp((T - 20.0) / 0.3) * 4)]
    st.comments_sheet(ctx, T, [("@blockfan", "my mom is literally this", "#ff5fa2"),
                               ("@noob_2012", "mom beat my obby too", "#4f8bff")], typed=typed, y0=560,
                      likes_t=20.4)
    label(ctx, "COMMENT \"LOOP\"", 360, 300, 50, bg=st.RED, scale=pop(T - 19.66))


def s_rewind(ctx, t, d):
    T = 21.5 + t
    s_hook(ctx, 0, 0, T0=0.0, frozen=True)


def s_end(ctx, t, d):
    s_hook(ctx, t, d, T0=0.0, frozen=True)   # exactly the first frame: the Short loops


# ================================================================ shots
S = []


def shot(start, draw, keys, **kw):
    kw.setdefault("vignette", 0.15)        # flat vector look: almost no vignette
    S.append(dict(start=start, draw=draw, keys=keys, **kw))


def punch(t0, z0, c0, t_key, z1, c1, m=0.16):
    """Hold a framing, then punch in (or out) to arrive on the key word at t_key."""
    return [(t0, z0, c0), (t_key, z1, c1, m)]


shot(0.00, s_hook, punch(0.0, 1.05, (340, 800), 0.55, 1.15, (320, 820)), keep=[(270, 590, 390, 710)])
shot(1.05, s_lock, punch(1.05, 1.0, (360, 700), 1.2, 1.08, (360, 690), 0.1), shake=(0.15, 14))
shot(1.85, s_roblox, punch(1.85, 1.0, (360, 700), 1.9, 1.1, (360, 660), 0.12), shake=(0.05, 8), closeup=True,
     keep=FACE_KEEP)
shot(2.72, s_day1, punch(2.72, 1.0, (360, 700), 3.0, 1.06, (380, 700), 0.3), keep=[(180, 230, 540, 380)])
shot(3.55, s_type, punch(3.55, 1.0, (360, 760), 3.9, 1.12, (360, 760), 0.15))
shot(4.72, s_wrong, punch(4.72, 1.0, (360, 700), 4.77, 1.1, (360, 680), 0.1), shake=(0.05, 16))
shot(5.58, s_day2, punch(5.58, 1.0, (360, 760), 6.0, 1.12, (320, 800), 0.16), keep=[(200, 260, 560, 410)])
shot(6.48, s_cake, punch(6.48, 1.0, (360, 700), 6.95, 1.1, (420, 720), 0.15))
shot(7.72, s_locked, punch(7.72, 1.0, (360, 700), 7.88, 1.1, (360, 700), 0.1), shake=(0.16, 18))
shot(8.30, s_hour, punch(8.30, 1.0, (360, 700), 8.35, 1.1, (360, 660), 0.12), shake=(0.05, 7), closeup=True,
     keep=FACE_KEEP)
shot(9.05, s_day3, punch(9.05, 1.0, (360, 760), 9.6, 1.06, (380, 780), 0.4), keep=[(180, 260, 540, 410)])
shot(10.0, s_find, punch(10.0, 1.0, (400, 760), 10.35, 1.25, (500, 700), 0.18))
shot(11.1, s_stars, punch(11.1, 1.0, (360, 700), 11.13, 1.08, (360, 660), 0.12), closeup=True, keep=FACE_KEEP)
shot(11.87, s_note, [(11.87, 1.0, (360, 640)), (12.26, 1.06, (360, 640), 0.15), (12.6, 1.14, (360, 680), 0.15)])
shot(13.62, s_granted, punch(13.62, 1.0, (360, 700), 13.97, 1.08, (360, 680), 0.15), shake=(0.35, 8))
shot(14.9, s_obby, punch(14.9, 1.0, (360, 700), 15.27, 1.15, (300, 720), 0.16))
shot(16.05, s_jump, punch(16.05, 1.0, (360, 700), 16.62, 1.08, (480, 700), 0.2), shake=(0.57, 10))
shot(17.0, s_board, punch(17.0, 1.0, (360, 640), 18.33, 1.12, (360, 560), 0.16), shake=(1.33, 8),
     keep=[(60, 250, 660, 520)])
shot(18.76, s_mom, punch(18.76, 1.0, (360, 700), 18.8, 1.1, (360, 660), 0.12), closeup=True,
     keep=[(150, 230, 570, 720)])
shot(19.62, s_comments, punch(19.62, 1.0, (360, 700), 20.0, 1.06, (360, 720), 0.2))
shot(21.5, s_rewind, [(21.5, 1.12, (330, 780)), (21.85, 1.0, (360, 760), 0.3)], blur=True)
shot(21.85, s_end, [(21.85, 1.0, (360, 760))])
SHOTS = S
for k, s in enumerate(SHOTS):
    s["end"] = SHOTS[k + 1]["start"] if k + 1 < len(SHOTS) else TOTAL


def _rewind_overlay(ctx, t, d):
    st.rewind_bars(ctx, t / d)


SHOTS[-2]["overlay"] = _rewind_overlay

# ---------------------------------------------------------------- SFX: about one per visual event
SFX = [
    (0.25, "pop.wav", 0.6), (0.55, "hit.wav", 1.3), (0.62, "pop.wav", 0.7), (1.2, "boom.wav", 1.6),
    (1.9, "pop.wav", 0.8), (2.74, "hit.wav", 1.3), (3.0, "swish.wav", 0.6), (3.95, "type_key.wav", 0.6), (4.25, "type_key.wav", 0.6),
    (4.77, "buzz.wav", 0.8), (4.8, "pop.wav", 0.7), (5.62, "hit.wav", 1.3), (6.0, "pop.wav", 0.6),
    (6.62, "type_key.wav", 0.5), (6.95, "ding.wav", 0.8), (7.74, "boom.wav", 1.6), (7.9, "tick.wav", 0.6),
    (8.35, "pop.wav", 0.8), (9.08, "hit.wav", 1.3), (9.45, "step.wav", 0.6), (10.35, "sparkle.wav", 0.9),
    (11.13, "pop.wav", 0.7), (11.89, "pop.wav", 0.7), (12.26, "pop.wav", 0.7), (12.6, "tick.wav", 0.8),
    (13.1, "tick.wav", 0.8), (13.65, "success.wav", 0.9), (13.97, "pop.wav", 0.8),
    (14.95, "pop.wav", 0.6), (15.27, "hit.wav", 1.3), (15.68, "pop.wav", 0.6), (16.12, "boing.wav", 0.7),
    (16.62, "hit.wav", 1.3), (16.65, "ding.wav", 0.7), (17.05, "swish.wav", 0.7), (17.45, "tick.wav", 0.6), (18.33, "boom.wav", 1.6), (18.8, "chaching.wav", 0.9), (19.2, "pop.wav", 0.6),
    (19.66, "pop.wav", 0.8), (20.1, "type_key.wav", 0.6),
    (20.45, "ding.wav", 0.8), (21.5, "whip.wav", 0.9), (21.86, "pop.wav", 0.6),
    (5.05, "swish.wav", 0.7), (10.62, "pop.wav", 0.7), (14.25, "pop.wav", 0.7), (19.05, "sparkle.wav", 0.8),
]

if __name__ == "__main__":
    import json
    import safezone
    json.dump([{"time": round(t, 3), "file": f, "volume": round(v * SFX_GAIN, 3)} for t, f, v in sorted(SFX)],
              open(sys.argv[2], "w"), indent=1)
    kw = {}
    if len(sys.argv) > 4:
        kw["frames"] = (int(sys.argv[3]), int(sys.argv[4]))
    safezone.fit(SHOTS, sys.modules[__name__])
    # seamless loop: the last framing equals the (fitted) first framing
    SHOTS[-1]["keys"] = [(SHOTS[-1]["start"], SHOTS[0]["keys"][0][1], SHOTS[0]["keys"][0][2])]
    render(SHOTS, TOTAL, sys.argv[1], xfade=0.0, grain=2, fade_out=0.0, fade_in=0.0, **kw)

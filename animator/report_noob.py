"""Story: "This noob is the reason Roblox invented the report button" (Kevin the noob).

Voice: output/report_noob/voice.mp3 (59.8 s) + subs.srt; word times from analysis/align_words.py.
Built from sample.py: hard cut per phrase, punch-in keys on key words, face close-ups with
closeup=True + keep boxes, game UI, SFX ~1 per visual event, loop back to the first frame.

Run (from animator/):
  python3 report_noob.py ../output/report_noob/clips/animation.mp4 ../output/report_noob/cues.json
  (writes cues.json + music.wav next to it)"""
import math
import os
import sys

import engine
import sets as st
import style
from engine import clamp, ease, hexc, keyed, lerp, pop, render
from sets import label
from style import Block

TOTAL = 60.1
engine.LIPSYNC = False
engine.DRIFT = (0.02, 5, -3)
engine.ENERGY = 3.0
SFX_GAIN = 0.4                    # real recorded voice: measured -2.8 dB median vs voice (TTS sample needed 0.17)
MUSIC = dict(dips=[(29.3, 31.5), (54.0, 55.3)])   # music_game() kwargs: quieter under the two dramatic beats

KEVIN = Block("#1a68cf", pants="#9bbc36", skin="#e9c22c", hair=None, sleeves="skin", shoes=None)
KEVIN_HAT = Block("#1a68cf", pants="#9bbc36", skin="#e9c22c", hair=None, sleeves="skin", shoes=None, cap="#ffcc33")
DEV = Block("#3b3f5a", pants="#2b2f45", skin="#f0c9a8", hair="spiky", hair_col="#2a1a14", outfit="hoodie",
            glasses=True, headset="#4f8bff", shoes="dark")
P = [style.crowd_member(i) for i in range(10)]   # other players

U1 = Block.HW * 64                                # head width at s=1
FACE_S = 4.2
FACE_Y = 560 + 2.5 * U1 * FACE_S                 # close-up: head centre at y 560
FACE_KEEP = [(165, 300, 555, 760)]


def head_y(y, s):
    """Head centre of a standing Block drawn at (x, y, s)."""
    return y - 2.5 * U1 * s


def kevin(ctx, x, y, s, expr, T, tag=True, hat=False, **kw):
    (KEVIN_HAT if hat else KEVIN).draw(ctx, x, y, s, expr, T, **kw)
    if tag:
        st.nametag(ctx, x, y - 3.35 * U1 * s, "Kevin", size=max(22, 26 * s))


def kevin_face(c, x, y, r):
    st.face_icon(c, x, y, r, "#e9c22c", "#e9c22c")


def closeup(ctx, ch, expr, T, x=360, look=0.0, arms=("down", "down"), s=FACE_S, dy=0):
    ch.draw(ctx, x, 560 + 2.5 * U1 * s + dy, s, expr, T, arms=arms, look=look)


def classic_world(ctx, T, old=False):
    if old:
        st.game_sky(ctx, "#a9bfd4", "#dfe6ee")
        st.baseplate(ctx, 760, "#8f959e")
    else:
        st.game_sky(ctx)
        st.block_clouds(ctx, T)
        st.baseplate(ctx, 760)


# ================================================================ hook (v2: big face, crime teaser, slam)
HI_POPS = [(560, 300, 0.36, (-1, 1)), (165, 330, 0.5, (1, 1)), (600, 470, 0.64, (-1, 1)),
           (140, 520, 0.78, (1, 1))]


def s_hook(ctx, t, d, T0=0.0, frozen=False):
    """0.00-0.95 "This noob is the": Kevin's crazy face slams into the frame, THIS NOOB + arrow,
    angry players in the corners, HI! bubbles multiplying from "noob"."""
    T = T0 + (0.0 if frozen else t)
    st.burst(ctx, T, "#ffe27a", "#ff7a1a", cy=560, spin=0.4)
    for x, i, look in ((-30, 0, 0.8), (750, 1, -0.8)):   # angry faces peeking in from the corners
        P[i].draw(ctx, x, 1580, 2.6, "angry", T, arms=("hip", "hip"), look=look)
    closeup(ctx, KEVIN, keyed(T, [(0, "crazy"), (0.36, "grin")]), T, arms=("down", "wave"))
    for bx, by, tk, tail in HI_POPS:
        st.speech_bubble(ctx, bx, by, "HI!", 46, T - tk, tail=tail)
    st.arrow(ctx, 610, 300, 520, 400, k=0.6 + ease(T / 0.15) * 0.4)
    label(ctx, "THIS NOOB", 340, 205, 74, fg=st.RED, scale=pop(T))


def s_teaser(T_scene, fn, t_off):
    """A 0.3 s flash of a later scene at its peak moment (the 'reason' montage)."""
    def draw(ctx, t, d):
        fn(ctx, t + t_off, d)
        st.flash(ctx, 0.55 * math.exp(-25 * t))      # a white hit-frame on every cut
    draw.__name__ = "teaser_" + fn.__name__
    return draw


def s_invented(ctx, t, d):
    """1.85-2.38 "Roblox invented the": developer eureka close-up, lightbulb pops."""
    T = 1.85 + t
    st.burst(ctx, T, "#c4d8ff", "#3a4ab0", cy=520)
    closeup(ctx, DEV, keyed(T, [(0, "shock"), (1.95, "crazy")]), T, arms=("down", "up"))
    st.lightbulb(ctx, 560, 300, 0.8, T - 1.89, T)
    label(ctx, "INVENTED", 300, 230, 64, fg=(1, 1, 1), scale=pop(T - 1.89))


def s_button(ctx, t, d):
    """2.38-3.18 "report button": the button slams down with Kevin riding on top; on "button" a giant
    cursor presses it and Kevin is launched into the sky."""
    T = 2.38 + t
    classic_world(ctx, T)
    bx, base = 320, 900
    k = clamp((T - 2.38) / 0.08)
    by = lerp(base - 160, base, k * k)              # short hard slam
    if T >= 2.46:
        st.shockwave(ctx, bx, base + 30, (T - 2.46) / 0.5, r_max=440)
        st.dust(ctx, bx, base + 30, (T - 2.46) / 0.4, n=6, spread=90)
    pressed = T > 2.79
    st.report_button(ctx, bx, by, 1.1, T, pressed=1.0 if pressed else 0.0, glow_a=0.5)
    top = by - 110 * 1.1 + (34 * 1.1 if pressed else 0)   # the button's top face
    if T < 2.82:
        kevin(ctx, bx + 60, top, 0.9, keyed(T, [(0, "grin"), (2.46, "shock")]), T,
              arms=("up", "up") if T >= 2.46 else ("down", "wave"))
    else:                                            # launched straight up, spinning
        p = (T - 2.82) / 0.32
        ky = top - p * p * 1300 - p * 300
        kx = bx + 60 + p * 120
        ctx.save()
        ctx.translate(kx, ky - 130)
        ctx.rotate(p * 8)
        ctx.translate(-kx, -(ky - 130))
        KEVIN.draw(ctx, kx, ky, 0.9, "scared", T, arms=("up", "up"), pose="jump")
        ctx.restore()
        st.speed_lines(ctx, T, kx, ky - 130, n=12, r0=120, r1=420, a=0.45)
        st.impact_star(ctx, bx + 60, top - 40, 120, T - 2.82, "YEET!")
    if 2.6 < T < 2.95:                               # a giant cursor slams the button on "button"
        kk = ease((T - 2.6) / 0.19)
        st.cursor(ctx, lerp(40, 160, kk), lerp(560, 800, kk), 2.4, click=1.0 if pressed else 0.0)
    if T >= 2.46:
        st.flash(ctx, 0.6 * math.exp(-18 * (T - 2.46)))


# ================================================================ 2006
def s_2006(ctx, t, d):
    T = 3.18 + t
    st.burst(ctx, T, "#e9d6b0", "#b08a5a", cy=640)
    k = clamp((T - 3.2) / 0.36)
    year = int(round(lerp(2026, 2006, ease(k))))
    st.calendar(ctx, 360, 660, 1.3, "YEAR", str(year), col="#8a5a3a", flip=(T * 6) % 1 if k < 1 else 0.0)
    label(ctx, "BACK IN...", 360, 270, 54, fg=(1, 1, 1), scale=pop(T - 3.21))


def s_oldworld(ctx, t, d):
    T = 4.05 + t
    classic_world(ctx, T, old=True)
    for j in range(5):   # a wobbly tower of bricks with someone on top
        st.block(ctx, 520, 760 - j * 80, 110, 80, 4, hexc("#a8a8b0"), 4)
    P[3].draw(ctx, 575, 360, 0.55, "laugh", T, arms=("up", "up"))
    fy = 520 + math.sin(T * 3) * 30   # a player flying for no reason
    st.speed_lines(ctx, T, 200, fy - 60, n=10, r0=90, r1=260, a=0.3)
    P[4].draw(ctx, 200, fy, 0.6, "crazy", T, arms=("up", "up"), pose="jump")
    P[5].draw(ctx, 330, 980, 0.9, "angry", T, arms=("punch", "down"))
    P[6].draw(ctx, 470, 990, 0.9, "shock", T, arms=("up", "up"))
    st.tint(ctx, (0.6, 0.5, 0.35), 0.18)          # old photo feel
    label(ctx, "2006", 360, 260, 70, bg="#8a5a3a", scale=pop(T - 4.1))


def s_norules(ctx, t, d):
    T = 6.25 + t
    st.burst(ctx, T, "#fff3c0", "#e8b04a", cy=640)
    st.rule_book(ctx, 360, 680, 0.95, T)
    st.red_x(ctx, 540, 560, 70, (T - 6.72) / 0.25)
    label(ctx, "NO RULES", 360, 330, 72, fg=st.RED, scale=pop(T - 6.45))


def s_onenoob(ctx, t, d):
    T = 7.25 + t
    classic_world(ctx, T)
    for i, x in enumerate((80, 200, 520, 640)):
        P[i + 4].draw(ctx, x, 980, 0.85, "cold", T, arms=("down", "down"))
    kevin(ctx, 360, 1000, 1.0, keyed(T, [(0, "neutral"), (8.03, "happy")]), T, tag=False, arms=("down", "wave"))
    if T > 7.7:
        st.spotlight(ctx, 360, 820, 230, a=0.7 * clamp((T - 7.7) / 0.15))
    label(ctx, "1 NOOB", 360, 330, 64, fg=st.YELLOW, scale=pop(T - 8.03))


def s_named(ctx, t, d):
    T = 8.53 + t
    st.burst(ctx, T, "#a8e6ff", "#4fb0e8", cy=560)
    closeup(ctx, KEVIN, keyed(T, [(0, "happy"), (9.35, "grin")]), T, arms=("wave", "down"))
    label(ctx, "KEVIN", 360, 250, 80, bg=st.BLUE, scale=pop(T - 8.57))


def s_friends(ctx, t, d):
    T = 9.9 + t
    classic_world(ctx, T)
    kevin(ctx, 190, 1000, 1.1, keyed(T, [(0, "worried"), (10.49, "happy")]), T, arms=("down", "show"), look=0.8)
    if T > 10.5:
        ctx.save()
        ctx.translate(500, 560)
        sc = pop(T - 10.49)
        ctx.scale(sc, sc)
        st.friends_panel(ctx, 0, 0, 0.62, 0, T)
        ctx.restore()
    st.hearts(ctx, T, 10.5, 200, 640, n=4)


def s_servers(ctx, t, d):
    T = 11.0 + t
    st.burst(ctx, T, "#7fb8ff", "#2f4bb0", cy=640)
    st.server_list(ctx, T, [11.31 + i * 0.13 for i in range(6)])
    kevin(ctx, 600, 1180, 0.55, "grin", T, tag=False, arms=("wave", "down"))


def s_spam(ctx, t, d):
    T = 12.28 + t
    classic_world(ctx, T)
    n = max(0, int((T - 12.43) / 0.07))
    st.chat_box(ctx, 50, 230, 620, 560, [("Kevin", "hello", st.YELLOW)] * min(n, 30), T, size=30)
    kevin(ctx, 360, 1060, 0.9, "happy", T, arms=("hold", "hold"))


def s_thousand(ctx, t, d):
    T = 13.25 + t
    classic_world(ctx, T)
    st.chat_box(ctx, 50, 230, 620, 300, [("Kevin", "hello", st.YELLOW)] * 20, T, size=26)
    for i, x in enumerate((130, 360, 590)):
        P[i].draw(ctx, x, 1000, 0.85, "angry" if T > 14.08 else "cold", T, arms=("cover", "cover"))
    n = int(lerp(1, 1000, ease((T - 13.3) / 0.78)))
    label(ctx, f"x{n:,}", 360, 620, 90, fg=st.YELLOW, scale=1.0 if T < 14.08 else pop(T - 14.08) * 1.15)


def make_hi(T0, i, bg):
    def s_hi(ctx, t, d):
        T = T0 + t
        st.burst(ctx, T, *bg, cy=560)
        P[i].draw(ctx, 230, 560 + 2.5 * U1 * 2.6, 2.6, "shock", T, arms=("up", "up"))
        kk = ease((T - T0) / 0.12)
        KEVIN.draw(ctx, lerp(800, 520, kk), 600 + 2.5 * U1 * 2.4, 2.4, "grin", T, arms=("down", "wave"))
        st.speech_bubble(ctx, 470, 300, "HI!", 70, T - T0 - 0.05, tail=(1, 1))
    s_hi.__name__ = f"s_hi{i}"
    return s_hi


HIS = [(15.12, 1, ("#ffd0e6", "#ff5fa2")), (15.56, 2, ("#b8ffb0", "#2e9c46")), (16.04, 3, ("#ffe27a", "#f29a2e")),
       (16.56, 6, ("#d0c0ff", "#7a3fd8"))]


# ================================================================ helpful
def s_helpful(ctx, t, d):
    T = 17.38 + t
    classic_world(ctx, T)
    on = T >= 17.77
    kevin(ctx, 360, 1040, 1.4, keyed(T, [(0, "neutral"), (17.77, "determined"), (18.42, "grin")]), T,
          hat=on, arms=("hip", "hip"))
    if 17.7 < T < 18.2:
        st.poof(ctx, 360, 600, 110, (T - 17.7) / 0.5)
    if T > 18.42:
        st.sparkles(ctx, T, 360, 700, spread=240, n=8, seed=4, c=st.YELLOW)
    label(ctx, "HELPFUL!", 360, 290, 76, fg=st.GREEN, scale=pop(T - 18.42))


def bridge_scene(ctx, T, built, lava):
    st.void_bg(ctx)
    st.block_clouds(ctx, T, n=3)
    st.cliff(ctx, -120, 900, 260)
    st.cliff(ctx, 580, 900, 260)
    st.lava_bridge(ctx, 140, 580, 900, T, built=built, lava=lava)


def s_bridge(ctx, t, d):
    T = 18.95 + t
    bridge_scene(ctx, T, clamp((T - 19.35) / 0.8), 0.0)
    kevin(ctx, 70, 900, 0.85, "determined", T, hat=True, arms=("down", "point"))
    label(ctx, "BRIDGE", 360, 300, 64, bg="#8a5a3a", scale=pop(T - 19.68))


def s_lava(ctx, t, d):
    T = 20.25 + t
    bridge_scene(ctx, T, 1.0, clamp((T - 20.27) / 0.3))
    kevin(ctx, 70, 900, 0.85, "happy", T, hat=True, arms=("up", "down"))
    burn = T > 20.95
    if not burn:
        P[7].draw(ctx, lerp(650, 470, ease((T - 20.3) / 0.65)), 900, 0.8, "neutral", T, pose="walk",
                  walk_phase=T * 2.5)
    else:
        st.poof(ctx, 470, 800, 90, (T - 20.95) / 0.55)
        P[7].draw(ctx, 470, 900 - (T - 20.95) * 900, 0.8, "shock", T, arms=("up", "up"), pose="jump")
    label(ctx, "LAVA?!", 360, 300, 84, fg=hexc("#ff7a1a"), scale=pop(T - 20.95))


def s_lemonade(ctx, t, d):
    T = 21.5 + t
    classic_world(ctx, T)
    kevin(ctx, 360, 1000, 1.0, keyed(T, [(0, "happy"), (22.2, "grin")]), T, tag=False, arms=("down", "wave"))
    sc = pop(T - 22.2)
    if sc > 0.01:
        ctx.save()
        ctx.translate(360, 1060)
        ctx.scale(sc, sc)
        st.lemonade_stand(ctx, 0, 0, 1.15, T)
        ctx.restore()


def s_obbystand(ctx, t, d):
    T = 23.1 + t
    st.game_sky(ctx)
    st.block_clouds(ctx, T)
    st.lava(ctx, 1040, T)
    for i in range(3):
        st.platform(ctx, -40 + i * 150, 860 - i * 30, 100, ("#2cd5fc", "#fa3a9f", "#f7e04a")[i], num=97 + i)
    st.platform(ctx, 420, 760, 160, "#a694e1", num=None)
    st.lemonade_stand(ctx, 500, 760, 0.45, T)
    kevin(ctx, 455, 760, 0.42, "happy", T, tag=False, arms=("wave", "down"))
    st.platform(ctx, 640, 700, 160, "#4fd16a")
    st.finish_flag(ctx, 700, 700, 0.7, T)
    st.stage_pill(ctx, 360, 300, "OBBY", s=pop(T - 23.65))


def s_finaljump(ctx, t, d):
    T = 24.15 + t
    st.game_sky(ctx)
    st.block_clouds(ctx, T)
    st.lava(ctx, 1150, T)
    st.platform(ctx, -100, 1000, 380, "#a694e1")
    st.lemonade_stand(ctx, 230, 1000, 0.8, T)
    st.platform(ctx, 560, 900, 300, "#4fd16a")
    st.finish_flag(ctx, 640, 900, 1.0, T)
    hit = T > 25.12
    P[8].draw(ctx, 60 if not hit else 40, 1000, 0.9, "angry" if hit else "determined", T, arms=("down", "point"),
              look=0.8)
    if hit:
        st.impact_star(ctx, 120, 760, 80, T - 25.12, "BONK!")
    st.stage_pill(ctx, 360, 300, "FINAL JUMP", s=pop(T - 24.76))


def s_spot(ctx, t, d):
    T = 25.38 + t
    classic_world(ctx, T)
    kevin(ctx, 220, 1000, 1.2, keyed(T, [(0, "neutral"), (26.61, "stars")]), T, arms=("down", "down"), look=0.9)
    P[9].draw(ctx, lerp(760, 540, ease((T - 25.7) / 0.8)), 1000, 1.0, "neutral", T, pose="walk",
              walk_phase=T * 2.2, look=-0.5)
    st.speech_bubble(ctx, 220, 440, "!!", 60, T - 26.61)


def s_hug(ctx, t, d):
    T = 27.08 + t
    st.burst(ctx, T, "#ffd0e6", "#ff5fa2", cy=600)
    sq = 1 - 0.08 * clamp((T - 27.65) / 0.2)
    ctx.save()
    ctx.translate(430, 1000)
    ctx.scale(sq, 1)
    ctx.translate(-430, -1000)
    P[9].draw(ctx, 430, 1000, 1.35, keyed(T, [(0, "shock"), (27.65, "scared")]), T, arms=("up", "up"), lean=-0.1)
    ctx.restore()
    kevin(ctx, 255, 1000, 1.35, "happy", T, arms=("down", "point"), lean=0.12)
    st.hearts(ctx, T, 27.65, 360, 520, n=7)
    label(ctx, "HUG!", 360, 290, 90, fg=st.PINK, scale=pop(T - 28.09))


# ================================================================ the problem
def s_problem(ctx, t, d):
    T = 28.53 + t
    st.night_wall(ctx, 2000)
    closeup(ctx, P[9], "worried", T, look=-0.3)
    label(ctx, "THE PROBLEM?", 360, 250, 62, fg=st.YELLOW, scale=pop(T - 28.65))


def s_stuck(ctx, t, d):
    T = 29.27 + t
    classic_world(ctx, T)
    for i, x in enumerate((520, 610)):
        P[i + 1].draw(ctx, x, 900, 0.8, "sad", T, arms=("down", "down"), bob=0.2)
    P[9].draw(ctx, 370, 990, 1.2, "scared", T, arms=("up", "up"), bob=0.0)
    kevin(ctx, 215, 990, 1.2, "happy", T, arms=("down", "point"), lean=0.12)
    st.tint(ctx, (0.4, 0.6, 1.0), 0.15)
    label(ctx, "STUCK", 360, 300, 84, bg="#2f6bd8", scale=pop(T - 29.89))


def s_hours(ctx, t, d):
    T = 30.27 + t
    st.burst(ctx, T, "#c4d8ff", "#4a5aa8", cy=600)
    hrs = 3 * ease((T - 30.3) / 1.1)
    st.big_clock(ctx, 360, 620, 230, hrs, T)
    label(ctx, "3 HOURS", 360, 300, 80, fg=(1, 1, 1), scale=pop(T - 30.3))
    kevin(ctx, 230, 1180, 0.7, "happy", T, tag=False, arms=("down", "point"), lean=0.12, bob=0.0)
    P[9].draw(ctx, 330, 1180, 0.7, "sleepy", T, arms=("up", "up"), bob=0.0)


# ================================================================ the devs
def devs_door(ctx, T):
    st.night_wall(ctx, 1080, wall="#3b2f6a")
    st.floor(ctx, 1080)
    st.door(ctx, 230, 1080, 260, 560, open_frac=0.0, col="#5a4fb0")
    label(ctx, "DEVS", 360, 420, 56, bg=st.RED, tilt=0.0)


def s_beg(ctx, t, d):
    T = 31.55 + t
    devs_door(ctx, T)
    for i, x in enumerate((110, 250, 470, 610)):
        P[i].draw(ctx, x, 1150 + (i % 2) * 40, 0.9, "cry" if T > 32.3 else "sad", T, pose="sit",
                  arms=("up", "up"), look=0.0)
    label(ctx, "PLEASE!!", 360, 280, 70, fg=(1, 1, 1), scale=pop(T - 32.3))


def s_banpls(ctx, t, d):
    T = 33.15 + t
    st.dark_glow_bg(ctx, T, glow_col="#ff4f5a", base="#1b1426")
    names = ["blox_99", "obbyqueen", "noobslayer", "Tom", "pizza_guy", "ZoomZoom"]
    n = max(0, int((T - 33.2) / 0.12))
    lines = [(names[i % 6], "PLS BAN KEVIN", st.RED) for i in range(n)]
    st.chat_box(ctx, 50, 230, 620, 640, lines, T, size=30)
    label(ctx, "GET RID OF HIM", 360, 980, 52, bg=st.RED, scale=pop(T - 33.94))


def s_nobutton(ctx, t, d):
    T = 34.5 + t
    st.burst(ctx, T, "#c4d8ff", "#4a5aa8", cy=640)
    st.settings_menu(ctx, 360, 660, 0.95, T, missing_k=pop(T - 35.43) if T > 35.43 else 0.0)
    st.red_x(ctx, 360, 890, 70, (T - 35.85) / 0.25)
    label(ctx, "NO BUTTON?!", 360, 260, 62, fg=st.YELLOW, scale=pop(T - 35.43))


def desk_front(ctx, y_desk):
    st.block(ctx, -100, y_desk, 920, 50, 8, hexc("#b9b4d8"), 5)
    st.block(ctx, -100, y_desk + 50, 920, 700, 0, hexc("#7a6aa8"), 5, gloss=False)


def dev_at_desk(ctx, T, expr, night, sun=0.0, n_cups=1, lean=0.0, steam=True):
    st.office(ctx, T, night=night, sun=sun, y_desk=900)
    DEV.draw(ctx, 230, 1070, 1.4, expr, T, arms=("hold", "hold"), lean=lean, bob=0.4 if lean else 1.0)
    desk_front(ctx, 900)
    st.monitor(ctx, 500, 905, 0.42, T, lambda c, x, y, w, h, TT: st.code_screen(c, x, y, w, h, TT, typed=0.6))
    for i in range(n_cups):
        st.coffee_cup(ctx, 70 + (i % 4) * 56, 905 - (i // 4) * 62, 0.85,
                      steam_T=T if steam and i == n_cups - 1 else None)


def s_dev(ctx, t, d):
    T = 36.45 + t
    dev_at_desk(ctx, T, keyed(T, [(0, "determined"), (38.2, "tired")]), 1.0,
                n_cups=1 + int(clamp((T - 37.4) / 0.8) * 5))
    label(ctx, "ALL NIGHT", 360, 300, 60, bg=st.UI_DARK, fg=st.YELLOW, scale=pop(T - 38.2))


def s_code(ctx, t, d):
    T = 38.15 + t
    st.night_wall(ctx, 2000)
    st.monitor(ctx, 360, 860, 1.12, T,
               lambda c, x, y, w, h, TT: st.code_screen(c, x, y, w, h, TT, typed=clamp((TT - 38.2) / 1.2),
                                                        button_k=pop(TT - 39.33) if TT > 39.33 else 0.0))
    st.keyboard(ctx, 360, 1080, 1.0, T, mash=1.0)
    label(ctx, "NEW BUTTON", 360, 250, 60, fg=st.GREEN, scale=pop(T - 39.33))


def s_oneword(ctx, t, d):
    T = 39.95 + t
    st.office(ctx, T, night=1.0)
    closeup(ctx, DEV, "smirk", T, arms=("down", "show"))
    label(ctx, "ONE WORD...", 360, 250, 64, fg=(1, 1, 1), scale=pop(T - 40.02))


def s_report(ctx, t, d):
    T = 40.75 + t
    st.burst(ctx, T, "#ff8a7a", "#a8202e", cy=640)
    k = T - 40.83
    st.shockwave(ctx, 360, 640, k / 0.5, r_max=460)
    st.report_button(ctx, 360, 640, pop(k) * 1.1, T, glow_a=0.6)
    st.flash(ctx, 0.7 * math.exp(-10 * max(0.0, k)) if k > 0 else 0)


# ================================================================ friendly
def s_friendly(ctx, t, d):
    T = 41.4 + t
    st.burst(ctx, T, "#ffd0e6", "#ff5fa2", cy=560)
    closeup(ctx, KEVIN, keyed(T, [(0, "happy"), (42.25, "stars")]), T, arms=("wave", "down"))
    st.hearts(ctx, T, 42.25, 360, 520, n=6)
    label(ctx, "SO FRIENDLY", 360, 250, 64, fg=(1, 1, 1), scale=pop(T - 42.25))


def s_likesub(ctx, t, d):
    T = 42.75 + t
    st.burst(ctx, T, "#a8e6ff", "#4fb0e8", cy=640)
    st.like_button(ctx, 360, 470, 1.1, pressed=1.0 if T > 43.18 else 0.0)
    st.subscribe_button(ctx, 360, 800, 1.1, pressed=clamp((T - 43.6) * 4))
    kx, ky = (420, 520) if T < 43.45 else (420, 840)
    st.cursor(ctx, kx, ky, 1.6, click=1.0 if (43.18 < T < 43.3 or 43.6 < T < 43.72) else 0.0)
    kevin(ctx, 600, 1180, 0.55, "grin", T, tag=False, arms=("wave", "down"))


def s_forty(ctx, t, d):
    T = 44.7 + t
    st.burst(ctx, T, "#a8e6ff", "#4fb0e8", cy=640)
    toggle = int(T * 14) % 2
    st.like_button(ctx, 250, 560, 0.85, pressed=float(toggle))
    st.subscribe_button(ctx, 360, 820, 1.0, pressed=float(1 - toggle))
    n = int(lerp(1, 40, ease((T - 44.74) / 0.45)))
    label(ctx, f"x{n}", 480, 540, 100, fg=st.YELLOW, scale=1.0 if T < 45.17 else pop(T - 45.17) * 1.1)
    kevin(ctx, 600, 1180, 0.55, "laugh", T, tag=False, arms=("up", "up"))


# ================================================================ the reports
def s_morning(ctx, t, d):
    T = 46.1 + t
    dev_at_desk(ctx, T, "sleepy", 1 - clamp((T - 46.15) / 0.8), sun=clamp((T - 46.15) / 1.0), n_cups=8,
                lean=0.3, steam=False)
    label(ctx, "NEXT MORNING", 360, 300, 60, bg="#ffb02e", scale=pop(T - 46.56))


def s_inbox(ctx, t, d):
    T = 47.55 + t
    st.burst(ctx, T, "#ffd0d0", "#d8283a", cy=520)
    for i in range(14):   # report tickets raining in
        ph = (T - 47.6) * 1.4 - i * 0.07
        if ph > 0:
            x = 60 + (i * 97) % 620
            y = -150 + ph * 900
            st.report_card(ctx, x, min(y, 1080 - (i % 4) * 40), 0.5, tilt=(i % 5 - 2) * 0.15)
    n = int(lerp(0, 10000, ease((T - 47.6) / 0.45)))
    label(ctx, f"{n:,} REPORTS", 360, 330, 60, bg=st.UI_DARK, fg=st.RED,
          scale=1.0 if T < 48.05 else pop(T - 48.05) * 1.1)


def s_guess(ctx, t, d):
    T = 49.4 + t
    st.office(ctx, T)
    closeup(ctx, DEV, keyed(T, [(0, "worried"), (49.84, "scared")]), T, x=300, arms=("down", "phone"))
    st.report_card(ctx, 520, 650, 1.1, face="?", tilt=0.08)
    label(ctx, "WHO?!", 360, 250, 80, fg=st.YELLOW, scale=pop(T - 49.84))


def s_kevin(ctx, t, d):
    T = 51.4 + t
    st.burst(ctx, T, "#ffe27a", "#f29a2e", cy=600)
    for i in range(6):
        st.report_card(ctx, 90 + (i % 3) * 270, 360 + (i // 3) * 600, 0.7, face=kevin_face, tilt=(i - 2.5) * 0.08)
    kevin(ctx, 360, 1040, 1.3, "grin", T, arms=("wave", "wave"))
    label(ctx, "KEVIN!", 360, 260, 90, fg=st.YELLOW, scale=pop(T - 51.44))


def s_banned(ctx, t, d):
    T = 52.0 + t
    st.burst(ctx, T, "#ffb0b0", "#a8202e", cy=640)
    st.profile_card(ctx, 360, 640, 1.05, "Kevin", face=kevin_face, status="noob since 2006")
    if T < 52.57:
        a = lerp(-1.2, 0.0, ease((T - 52.1) / 0.45))
        st.ban_hammer(ctx, 600, 420, 1.0, a)
    st.stamp(ctx, 360, 640, "BANNED", T - 52.57, size=110)


def s_year(ctx, t, d):
    T = 53.05 + t
    st.night_wall(ctx, 2000)
    st.calendar(ctx, 360, 470, 0.9, "BANNED FOR", "365", col="#e8323a", flip=clamp((T - 53.08) / 0.35))
    KEVIN.draw(ctx, 360, 1240, 1.5, "cry", T, arms=("down", "down"))
    label(ctx, "1 YEAR", 360, 760, 64, bg=st.RED, scale=pop(T - 53.6))


def s_crazy(ctx, t, d):
    T = 54.03 + t
    st.night_wall(ctx, 2000)
    closeup(ctx, KEVIN, "cold", T)
    st.spotlight(ctx, 360, 560, 300, a=0.85)
    label(ctx, "?!", 360, 250, 100, fg=st.YELLOW, scale=pop(T - 54.49))


def s_today(ctx, t, d):
    T = 55.3 + t
    st.office(ctx, T)
    k = ease((T - 55.35) / 0.9)
    x = lerp(-60, 330, k)
    kevin(ctx, x, 1180, 1.1, "happy", T, tag=False, pose="walk" if k < 1 else "stand", walk_phase=T * 2.2)
    st.staff_badge(ctx, x, 1180 - 1.55 * U1 * 1.1, 0.75)
    label(ctx, "TODAY", 360, 300, 72, bg=st.BLUE, scale=pop(T - 55.34))


def s_works(ctx, t, d):
    T = 56.55 + t
    st.office(ctx, T)
    kevin(ctx, 360, 1150, 1.5, keyed(T, [(0, "happy"), (57.17, "smug")]), T, tag=False, arms=("hip", "hip"))
    st.staff_badge(ctx, 360, 1150 - 1.55 * U1 * 1.5, 1.0)
    label(ctx, "STAFF", 360, 300, 80, fg=st.GREEN, scale=pop(T - 56.59))


def s_job(ctx, t, d):
    T = 57.65 + t
    st.office(ctx, T)
    closeup(ctx, KEVIN, "smirk", T, arms=("down", "show"))
    label(ctx, "HIS JOB?", 360, 250, 72, fg=st.YELLOW, scale=pop(T - 57.72))


def s_review(ctx, t, d):
    T = 58.5 + t
    st.office(ctx, T)
    st.paper_pile(ctx, 560, 990, 360, 380, T, seed=4)
    kevin(ctx, 200, 1150, 1.25, "smug", T, tag=False, arms=("down", "point"))
    for i, ts in enumerate((58.54, 58.9, 59.05, 59.35)):
        if T >= ts - 0.1:
            cx_, cy_ = 420 + i * 25, 780 - i * 12
            st.report_card(ctx, cx_, cy_, 0.75, face=kevin_face if i % 2 else "?", tilt=-0.05 + i * 0.03)
            st.stamp(ctx, cx_, cy_, "BANNED", T - ts, size=44)
    label(ctx, "REVIEWING REPORTS", 360, 290, 50, bg=st.RED, scale=pop(T - 58.54))


def s_end(ctx, t, d):
    s_hook(ctx, t, d, T0=0.0, frozen=True)   # the first frame again: the Short loops


# ================================================================ shots
S = []


def shot(start, draw, keys, **kw):
    kw.setdefault("vignette", 0.15)
    S.append(dict(start=start, draw=draw, keys=keys, **kw))


def punch(t0, z0, c0, t_key, z1, c1, m=0.16):
    return [(t0, z0, c0), (t_key, z1, c1, m)]


C = (360, 700)
CU = dict(closeup=True, keep=FACE_KEEP)
shot(0.00, s_hook, [(0.0, 1.3, (360, 600)), (0.12, 1.0, (360, 680), 0.12), (0.36, 1.12, (360, 620), 0.1)],
     shake=(0.36, 12), closeup=True, keep=FACE_KEEP)
shot(3.18, s_2006, punch(3.18, 1.0, C, 3.56, 1.08, (360, 680), 0.12), keep=[(130, 420, 590, 920)])
shot(4.05, s_oldworld, [(4.05, 1.1, (360, 760)), (5.88, 1.0, (360, 720), 0.35)])
shot(6.25, s_norules, punch(6.25, 1.0, C, 6.45, 1.08, (360, 680), 0.14), keep=[(60, 470, 660, 890)])
shot(7.25, s_onenoob, punch(7.25, 1.0, (360, 760), 8.03, 1.2, (360, 800), 0.16))
shot(8.53, s_named, punch(8.53, 1.0, C, 8.57, 1.08, (360, 680), 0.12), **CU)
shot(9.9, s_friends, punch(9.9, 1.0, (360, 760), 10.49, 1.06, (380, 740), 0.15), keep=[(330, 430, 670, 690)])
shot(11.0, s_servers, punch(11.0, 1.0, C, 11.84, 1.05, (360, 680), 0.3), keep=[(40, 280, 680, 1000)])
shot(12.28, s_spam, punch(12.28, 1.0, (360, 760), 12.82, 1.06, (360, 740), 0.2), keep=[(50, 230, 670, 790)])
shot(13.25, s_thousand, punch(13.25, 1.0, (360, 760), 14.08, 1.12, (360, 700), 0.14), shake=(0.83, 10))
for i, (t0, pi, bg) in enumerate(HIS):
    shot(t0, make_hi(t0, pi, bg), punch(t0, 1.0, C, t0 + 0.05, 1.08, (360, 680), 0.1), shake=(0.05, 9),
         closeup=True, keep=[(110, 300, 640, 760)])
shot(17.38, s_helpful, punch(17.38, 1.0, (360, 760), 18.42, 1.1, (360, 740), 0.14))
shot(18.95, s_bridge, [(18.95, 1.0, (360, 760)), (19.68, 1.05, (360, 760), 0.4)])
shot(20.25, s_lava, punch(20.25, 1.0, (360, 760), 20.95, 1.12, (420, 760), 0.14), shake=(0.7, 10))
shot(21.5, s_lemonade, punch(21.5, 1.0, (360, 760), 22.2, 1.06, (360, 760), 0.15), keep=[(120, 560, 600, 1060)])
shot(23.1, s_obbystand, [(23.1, 1.25, (480, 720)), (23.65, 1.0, (360, 700), 0.3)], keep=[(400, 540, 600, 780)])
shot(24.15, s_finaljump, punch(24.15, 1.0, (360, 760), 24.76, 1.06, (380, 760), 0.15), shake=(0.97, 9),
     keep=[(60, 640, 400, 1000), (190, 260, 530, 340)])
shot(25.38, s_spot, punch(25.38, 1.0, (360, 760), 26.61, 1.12, (300, 760), 0.15))
shot(27.08, s_hug, punch(27.08, 1.0, (360, 760), 28.09, 1.1, (350, 740), 0.12), shake=(0.57, 12))
shot(28.53, s_problem, punch(28.53, 1.0, C, 28.65, 1.06, (360, 680), 0.1), **CU)
shot(29.27, s_stuck, [(29.27, 1.0, (360, 760)), (29.89, 1.04, (360, 760), 0.3)])
shot(30.27, s_hours, punch(30.27, 1.0, C, 30.3, 1.06, (360, 680), 0.12), keep=[(130, 390, 590, 850)])
shot(31.55, s_beg, punch(31.55, 1.0, (360, 760), 32.3, 1.08, (360, 780), 0.15), keep=[(220, 380, 500, 460)])
shot(33.15, s_banpls, punch(33.15, 1.0, C, 33.94, 1.04, (360, 680), 0.2), keep=[(50, 230, 670, 870)])
shot(34.5, s_nobutton, punch(34.5, 1.0, C, 35.43, 1.08, (360, 760), 0.14), keep=[(90, 340, 630, 980)])
shot(36.45, s_dev, punch(36.45, 1.0, (360, 700), 38.2, 1.1, (300, 720), 0.16))
shot(38.15, s_code, punch(38.15, 1.0, C, 39.33, 1.1, (400, 640), 0.14), keep=[(60, 420, 660, 860)])
shot(39.95, s_oneword, punch(39.95, 1.0, C, 40.02, 1.06, (360, 680), 0.1), **CU)
shot(40.75, s_report, punch(40.75, 1.0, C, 40.83, 1.08, (360, 660), 0.1), shake=(0.08, 18),
     keep=[(100, 500, 620, 670)])
shot(41.4, s_friendly, punch(41.4, 1.0, C, 42.25, 1.08, (360, 680), 0.14), **CU)
shot(42.75, s_likesub, punch(42.75, 1.0, C, 43.6, 1.06, (360, 720), 0.15), keep=[(120, 360, 600, 880)])
shot(44.7, s_forty, punch(44.7, 1.0, C, 45.17, 1.1, (380, 640), 0.12), shake=(0.47, 9))
shot(46.1, s_morning, punch(46.1, 1.0, (360, 700), 46.56, 1.06, (340, 700), 0.2))
shot(47.55, s_inbox, punch(47.55, 1.0, C, 48.05, 1.1, (360, 660), 0.12), shake=(0.5, 12))
shot(49.4, s_guess, punch(49.4, 1.0, C, 49.84, 1.08, (400, 680), 0.14), closeup=True,
     keep=[(110, 300, 650, 780)])
shot(51.4, s_kevin, punch(51.4, 1.0, (360, 760), 51.44, 1.08, (360, 740), 0.1), shake=(0.04, 12))
shot(52.0, s_banned, punch(52.0, 1.0, C, 52.57, 1.1, (360, 660), 0.1), shake=(0.57, 16),
     keep=[(110, 390, 610, 900)])
shot(53.05, s_year, punch(53.05, 1.0, C, 53.6, 1.06, (360, 700), 0.15), keep=[(190, 260, 530, 690)])
shot(54.03, s_crazy, [(54.03, 1.0, (360, 680)), (55.25, 1.25, (360, 600), 1.1)], **CU)
shot(55.3, s_today, punch(55.3, 1.0, (360, 760), 55.86, 1.04, (360, 760), 0.3))
shot(56.55, s_works, punch(56.55, 1.0, (360, 760), 57.17, 1.08, (360, 720), 0.15))
shot(57.65, s_job, punch(57.65, 1.0, C, 57.72, 1.06, (360, 680), 0.1), **CU)
shot(58.5, s_review, punch(58.5, 1.0, (360, 760), 59.05, 1.06, (380, 760), 0.15), shake=(0.04, 7))
shot(59.75, s_end, [(59.75, 1.0, (360, 760))])
# hook montage: reuse the later shots' framing at their peak moment
_src = {sh["draw"]: sh for sh in S}
for start, fn, t_off in ((0.95, s_thousand, 0.83), (1.25, s_lava, 0.7), (1.55, s_hug, 0.97)):
    src = _src[fn]
    keys = [(start, src["keys"][-1][1], src["keys"][-1][2])]
    shot(start, s_teaser(src["start"], fn, t_off), keys, shake=(0.0, 14), keep=src.get("keep", []))
shot(1.85, s_invented, punch(1.85, 1.0, C, 1.95, 1.1, (360, 660), 0.1), closeup=True,
     keep=[(150, 230, 640, 760)])
shot(2.38, s_button, punch(2.38, 1.0, (340, 700), 2.79, 1.06, (330, 680), 0.12), shake=(0.08, 18),
     keep=[(45, 650, 595, 960)])
S.sort(key=lambda sh: sh["start"])
SHOTS = S
for k, s in enumerate(SHOTS):
    s["end"] = SHOTS[k + 1]["start"] if k + 1 < len(SHOTS) else TOTAL

# ---------------------------------------------------------------- SFX (time, file, volume before SFX_GAIN)
SFX = [
    (0.03, "boom.wav", 1.6), (0.36, "pop.wav", 0.8), (0.5, "pop.wav", 0.6), (0.78, "pop.wav", 0.6),
    (0.95, "hit.wav", 1.3), (1.25, "boom.wav", 1.4), (1.55, "hit.wav", 1.3), (1.89, "ding.wav", 0.9),
    (2.46, "boom.wav", 1.6), (2.79, "click.wav", 0.9), (2.82, "boing.wav", 0.8), (2.86, "whoosh.wav", 0.6),
    (3.25, "tick.wav", 0.6), (3.4, "tick.wav", 0.6), (3.56, "ding.wav", 0.8), (4.1, "pop.wav", 0.7),
    (4.6, "boing.wav", 0.5), (5.4, "pop.wav", 0.5), (6.45, "hit.wav", 1.3), (6.72, "swish.wav", 0.7),
    (7.7, "sparkle.wav", 0.7), (8.03, "hit.wav", 1.3), (8.57, "pop.wav", 0.8), (9.35, "pop.wav", 0.5),
    (10.49, "ding.wav", 0.7), (11.31, "click.wav", 0.7), (11.57, "click.wav", 0.7), (11.83, "click.wav", 0.7),
    (12.43, "type_key.wav", 0.6), (12.63, "type_key.wav", 0.6), (12.82, "tick.wav", 0.6),
    (13.3, "tick.wav", 0.5), (13.62, "tick.wav", 0.5), (14.08, "hit.wav", 1.3),
    (15.17, "pop.wav", 0.8), (15.61, "pop.wav", 0.8), (16.09, "pop.wav", 0.8), (16.61, "pop.wav", 0.8),
    (17.77, "swish.wav", 0.6), (17.8, "pop.wav", 0.6), (18.42, "sparkle.wav", 0.8),
    (19.4, "tick.wav", 0.6), (19.68, "hit.wav", 1.3), (19.9, "tick.wav", 0.6), (20.3, "boom.wav", 1.6),
    (20.95, "pop.wav", 0.8), (21.0, "boing.wav", 0.5), (21.9, "click.wav", 0.6), (22.2, "ding.wav", 0.8),
    (23.15, "swish.wav", 0.6), (23.65, "pop.wav", 0.7), (24.76, "pop.wav", 0.7), (25.12, "hit.wav", 1.3),
    (25.7, "step.wav", 0.6), (26.0, "step.wav", 0.6), (26.61, "pop.wav", 0.8), (27.21, "swish.wav", 0.6),
    (27.65, "hit.wav", 1.3), (28.09, "pop.wav", 0.8), (28.65, "pop.wav", 0.7), (29.89, "hit.wav", 1.3),
    (30.3, "tick.wav", 0.7), (30.6, "tick.wav", 0.7), (30.9, "tick.wav", 0.7), (31.2, "ding.wav", 0.7),
    (31.6, "pop.wav", 0.6), (32.3, "pop.wav", 0.8), (33.3, "type_key.wav", 0.5), (33.6, "type_key.wav", 0.5),
    (33.94, "pop.wav", 0.7), (34.6, "swish.wav", 0.6), (35.43, "pop.wav", 0.7), (35.85, "buzz.wav", 0.8),
    (36.5, "click.wav", 0.6), (37.41, "tick.wav", 0.6), (37.8, "tick.wav", 0.6), (38.2, "hit.wav", 1.3),
    (38.5, "type_key.wav", 0.5), (38.8, "type_key.wav", 0.5), (39.33, "pop.wav", 0.8), (40.02, "pop.wav", 0.7),
    (40.83, "boom.wav", 1.6), (40.86, "ding.wav", 0.8), (41.45, "pop.wav", 0.6), (42.25, "sparkle.wav", 0.8),
    (43.18, "click.wav", 0.9), (43.2, "pop.wav", 0.7), (43.6, "click.wav", 0.9), (43.62, "pop.wav", 0.7),
    (44.75, "tick.wav", 0.6), (44.95, "tick.wav", 0.6), (45.17, "hit.wav", 1.3), (46.2, "ding.wav", 0.7),
    (46.56, "pop.wav", 0.7), (47.6, "swish.wav", 0.6), (47.8, "tick.wav", 0.6), (48.05, "boom.wav", 1.6),
    (48.4, "pop.wav", 0.5), (49.6, "tick.wav", 0.6), (49.84, "hit.wav", 1.3), (50.3, "tick.wav", 0.6),
    (50.62, "tick.wav", 0.6), (51.44, "boom.wav", 1.6), (51.47, "ding.wav", 0.8), (52.3, "swish.wav", 0.7),
    (52.57, "boom.wav", 1.6), (53.1, "tick.wav", 0.6), (53.6, "pop.wav", 0.8), (54.49, "sting_low.wav", 0.8),
    (55.34, "pop.wav", 0.7), (55.6, "step.wav", 0.6), (55.95, "step.wav", 0.6), (56.59, "ding.wav", 0.8),
    (57.17, "pop.wav", 0.6), (57.72, "pop.wav", 0.7), (58.54, "hit.wav", 1.3), (58.9, "hit.wav", 1.0),
    (59.05, "hit.wav", 1.3), (59.35, "hit.wav", 1.0), (59.6, "whip.wav", 0.9), (59.8, "pop.wav", 0.6),
]

if __name__ == "__main__":
    import json
    import audio
    import safezone
    json.dump([{"time": round(t, 3), "file": f, "volume": round(v * SFX_GAIN, 3)} for t, f, v in sorted(SFX)],
              open(sys.argv[2], "w"), indent=1)
    audio.save(os.path.join(os.path.dirname(os.path.abspath(sys.argv[2])), "music.wav"),
               audio.music_game(TOTAL, **MUSIC))
    kw = {}
    if len(sys.argv) > 4:
        kw["frames"] = (int(sys.argv[3]), int(sys.argv[4]))
    safezone.fit(SHOTS, sys.modules[__name__])
    SHOTS[-1]["keys"] = [(SHOTS[-1]["start"], SHOTS[0]["keys"][0][1], SHOTS[0]["keys"][0][2])]
    render(SHOTS, TOTAL, sys.argv[1], xfade=0.0, grain=2, fade_out=0.0, fade_in=0.0, **kw)

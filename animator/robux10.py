"""Story: "What if you got 1,000,000 Robux in just 10 seconds?"

Voice: output/robux10/voice.mp3 (43.7 s) + subs.srt; word times from analysis/align_words.py
(SRT line starts used where the aligner slipped: "Give me that", "The mystery box", "Comment").
A "Second 10 -> 5" countdown story like the reference: a timer pill on every shot, a SECOND N card
with a shockwave on every number, literal game UI per beat, then mom's refund and a cliffhanger.

Run (from animator/):
  python3 robux10.py ../output/robux10/clips/animation.mp4 ../output/robux10/cues.json"""
import math
import os
import sys

import engine
import sets as st
import style
from engine import clamp, ease, hexc, keyed, lerp, pop, render
from sets import label
from style import Block

TOTAL = 43.95
engine.LIPSYNC = True              # only characters drawn with talk=True move their mouths
DIALOGUE = {"mom": [(27.27, 28.57), (30.65, 31.75)], "kid": [(28.57, 30.15)]}   # who speaks when (SRT)
engine.DRIFT = (0.035, 9, -6)       # livelier hold (no_break measured a low camera median with 0.02)
engine.ENERGY = 3.0
SFX_GAIN = 0.26                     # this voice is quieter (-19.5 dB): measured SFX median +0.8 dB at 0.4
MUSIC = dict(dips=[(37.1, 38.9)])   # quieter under "But Mom forgot one thing"

KID = style.KID
KID_SH = Block("#2fbf8f", pants="#2b3f8f", skin="#e6ddd6", hair="bowl", hair_col="#4a2f22", emblem="star",
               emblem_col="#ffd84a", shoes="white", shades=True)
AVATAR = style.KID_GAME
MOM = style.MOM
CROWD = [style.crowd_member(i) for i in range(6)]

U1 = Block.HW * 64
FACE_S = 4.2
FACE_KEEP = [(165, 300, 555, 760)]


def closeup(ctx, ch, expr, T, x=360, look=0.0, arms=("down", "down"), s=FACE_S, talk=False):
    ch.draw(ctx, x, 560 + 2.5 * U1 * s, s, expr, T, arms=arms, look=look, talk=talk)


def talking(who, T):
    return any(a <= T <= b for a, b in DIALOGUE[who])


def game_bg(ctx, T):
    st.game_sky(ctx)
    st.block_clouds(ctx, T)
    st.baseplate(ctx, 760)


def coin_rain(ctx, T, n=14, seed=3):
    for i in range(n):
        ph = (T * 0.9 + i / n) % 1
        x = (i * 137 + seed * 53) % 760 - 20
        st.coin(ctx, x, -100 + ph * 1500, 0.8, spin=T * 5 + i)


def second(ctx, T, n, t0, bg="#ffe27a", bg2="#f29a2e", box_glow=0.0):
    """SECOND N chapter beat: the card flies in over the mystery box on the baseplate."""
    game_bg(ctx, T)
    st.mystery_box(ctx, 360, 1000, 1.0, T, glow_a=box_glow)
    st.second_card(ctx, 360, 470, n, T - t0)


# ================================================================ hook
def s_hook(ctx, t, d, T0=0.0, frozen=False):
    T = T0 + (0.0 if frozen else t)
    st.burst(ctx, T, "#ffe27a", "#f29a2e", cy=560, spin=0.4)
    coin_rain(ctx, T)
    closeup(ctx, KID, keyed(T, [(0, "stars"), (1.02, "crazy")]), T, arms=("up", "up"))
    label(ctx, "1,000,000 R$", 360, 300, 66, fg=st.YELLOW, scale=pop(T - 0.67) if T >= 0.67 else 0.0)


def s_tensec(ctx, t, d):
    T = 1.65 + t
    st.burst(ctx, T, "#ff8a7a", "#a8202e", cy=600)
    st.alarm_clock(ctx, 360, 640, 1.8, "0:10", T, ring=1.0 if T > 2.08 else 0.0)
    KID.draw(ctx, 590, 1040, 0.75, "shock", T, arms=("up", "up"))
    label(ctx, "10 SECONDS?", 340, 330, 64, fg=(1, 1, 1), scale=pop(T - 2.08))


def s_watch(ctx, t, d):
    T = 3.0 + t
    st.night_wall(ctx, 2000)
    closeup(ctx, KID_SH, "smug", T)
    if T > 3.38:
        style.sparkle(ctx, 470, 520, 40 * pop(T - 3.38))
    label(ctx, "WATCH THIS", 360, 300, 66, fg=st.GREEN, scale=pop(T - 3.06))


# ================================================================ seconds 10 -> 5
def s_sec10(ctx, t, d):
    T = 3.95 + t
    second(ctx, T, 10, 4.0)


def s_open(ctx, t, d):
    T = 4.8 + t
    game_bg(ctx, T)
    k = ease((T - 4.99) / 0.35)
    st.mystery_box(ctx, 430, 1000, 1.0, T, open_k=k, glow_a=0.6 * k)
    AVATAR.draw(ctx, 170, 1000, 1.1, keyed(T, [(0, "determined"), (4.99, "grin")]), T,
                arms=("down", "point"), look=0.8)
    if T > 5.0:
        st.sparkles(ctx, T, 430, 650, spread=200, n=10, seed=4, c=st.YELLOW)
    label(ctx, "MYSTERY BOX", 360, 300, 60, bg="#7a3fd8", scale=pop(T - 5.34))


def s_sec9(ctx, t, d):
    T = 6.3 + t
    second(ctx, T, 9, 6.35, box_glow=0.6)


def s_ticket(ctx, t, d):
    T = 7.0 + t
    st.dark_glow_bg(ctx, T, glow_col="#ffcc33", base="#2a1a3a")
    st.mystery_box(ctx, 360, 1150, 0.8, T, open_k=1.0, glow_a=0.5)
    p = clamp((T - 7.05) / 1.1)
    y = lerp(1000, 620, ease(min(1, p * 1.6))) + max(0, p - 0.65) * 300
    st.golden_ticket(ctx, 360, y, 1.15, rot=math.sin(T * 3) * 0.12, flip=math.cos((T - 7.05) * 9) if p < 0.7 else 1.0)
    label(ctx, "GOLDEN TICKET", 360, 300, 58, fg=st.YELLOW, scale=pop(T - 7.52))


def s_sec8(ctx, t, d):
    T = 8.8 + t
    second(ctx, T, 8, 8.84, box_glow=0.6)


def s_spin(ctx, t, d):
    T = 9.65 + t
    st.burst(ctx, T, "#c4a8ff", "#4a2fb0", cy=600, spin=1.2)
    v = (T * 987654) % 99999
    st.number_counter(ctx, 360, 640, 1.0, v, T, spinning=T > 9.84)
    coin_rain(ctx, T, n=10, seed=7)
    label(ctx, "SPINNING...", 360, 330, 62, fg=(1, 1, 1), scale=pop(T - 10.44))


def s_sec7(ctx, t, d):
    T = 10.9 + t
    second(ctx, T, 7, 10.94, box_glow=0.6)


def s_hundred(ctx, t, d):
    T = 11.75 + t
    st.burst(ctx, T, "#ffe27a", "#f29a2e", cy=600)
    landed = T >= 12.6
    v = 100000 if landed else (T * 987654) % 99999
    st.number_counter(ctx, 360, 520, 1.0, v, T, spinning=not landed)
    if landed:
        st.shockwave(ctx, 360, 520, (T - 12.6) / 0.5, r_max=420)
        st.confetti(ctx, T, 12.6, n=40)
    AVATAR.draw(ctx, 360, 1060, 1.2, "laugh" if landed else "worried", T, arms=("up", "up") if landed else
                ("down", "down"), pose="jump" if landed else "stand")


def s_sec6(ctx, t, d):
    T = 13.8 + t
    second(ctx, T, 6, 14.17, box_glow=0.6)


SHOP = [("SPEED", "#4f8bff"), ("FLY", "#9d5cff"), ("x2 COINS", "#ffb02e"), ("PET", "#ff5fa2"),
        ("TRAIL", "#2fbf8f"), ("GIANT", "#e8323a")]


def s_glitch(ctx, t, d):
    T = 14.7 + t
    st.burst(ctx, T, "#a8e6ff", "#4fb0e8", cy=600)
    st.shop_grid(ctx, T, SHOP, y0=360)
    st.glitch(ctx, T, k=1.0 if T > 15.18 else 0.0)
    label(ctx, "GLITCH", 360, 300, 70, fg=st.RED, scale=pop(T - 15.18), tilt=0.06 * math.sin(T * 40))


def s_free(ctx, t, d):
    T = 15.8 + t
    st.burst(ctx, T, "#b8ffb0", "#2e9c46", cy=600)
    st.shop_grid(ctx, T, SHOP, y0=360)
    for i in range(6):
        cx, cy = 70 + (i % 3) * 205 + 90, 360 + 90 + (i // 3) * 220 + 80
        st.stamp(ctx, cx, cy, "FREE", T - (16.0 + i * 0.12), col="#3ce454", size=40)
    label(ctx, "EVERYTHING FREE!", 360, 300, 54, fg=st.GREEN, scale=pop(T - 16.79))


def s_subs(ctx, t, d):
    T = 17.45 + t
    game_bg(ctx, T)
    for i, x in enumerate((90, 230, 490, 630)):
        CROWD[i].draw(ctx, x, 1060, 0.85, "stars" if T > 17.93 else "happy", T, arms=("up", "up"))
    st.subscribe_button(ctx, 360, 560, 1.05, pressed=clamp((T - 17.93) * 4))
    st.cursor(ctx, 420, 600, 1.6, click=1.0 if 17.9 < T < 18.05 else 0.0)


def s_wheel(ctx, t, d):
    T = 18.9 + t
    st.burst(ctx, T, "#ffd0e6", "#ff5fa2", cy=640)
    spin = 3.0 * (1 - math.exp(-2 * (T - 18.9))) * 6
    st.prize_wheel(ctx, 360, 680, 250, T, angle=spin)
    label(ctx, "FREE SPIN", 360, 300, 66, bg=st.PINK, scale=pop(T - 19.2))


def s_sec5(ctx, t, d):
    T = 19.85 + t
    second(ctx, T, 5, 20.28, box_glow=0.8)


def s_gold(ctx, t, d):
    T = 20.95 + t
    st.night_wall(ctx, 2000)

    def screen(c, x, y, w, h, TT):
        st.burst(c, TT, "#fff3a8", "#ffcc33", cx=x + w / 2, cy=y + h / 2)
    st.monitor(ctx, 360, 900, 1.15, T, screen if T > 21.47 else None)
    if T > 21.47:
        st.flash(ctx, 0.7 * math.exp(-6 * (T - 21.47)))
        st.glow(ctx, 360, 600, 500, (1, 0.85, 0.3), 0.5)
    label(ctx, "GOLD!", 360, 300, 80, fg=st.YELLOW, scale=pop(T - 21.96))


def s_million(ctx, t, d):
    T = 22.55 + t
    st.burst(ctx, T, "#ffe27a", "#f29a2e", cy=560)
    st.coin_pile(ctx, 360, 1280, 760, 380, T)
    closeup(ctx, KID, "stars", T, arms=("up", "up"), s=3.2)
    st.number_counter(ctx, 360, 300, 0.85, 1000000, T)


def s_pet(ctx, t, d):
    T = 23.95 + t
    st.burst(ctx, T, "#e0c0ff", "#7a3fd8", cy=640)
    if T < 24.45:
        st.egg(ctx, 360, 900, 1.3, T, crack=clamp((T - 24.0) / 0.4))
    else:
        st.poof(ctx, 360, 760, 160, (T - 24.45) / 0.5)
        st.pet_puppy(ctx, 380, 1000, pop(T - 24.5) * 1.25, T)
    label(ctx, "LEGENDARY", 360, 300, 64, bg="#7a3fd8", scale=pop(T - 25.29))
    label(ctx, "0.001%", 360, 400, 40, bg=st.UI_DARK, scale=pop(T - 25.4))


# ================================================================ mom
def bedroom_kid(ctx, T, expr, look=0.4, door=0.0):
    st.night_bedroom(ctx, T, door_open=door)
    KID.draw(ctx, 230, 1150, 1.5, expr, T, arms=("hold", "hold"), pose="sit", look=look)
    st.checker(ctx, -60, 1075, 470, 200, n=7)
    st.tablet(ctx, 230, 1000, 0.6, T, lambda c, x, y, w, h, TT: st.burst(c, TT, "#ffe27a", "#f29a2e",
                                                                           cx=x + w / 2, cy=y + h / 2))


def s_momin(ctx, t, d):
    T = 26.1 + t
    bedroom_kid(ctx, T, keyed(T, [(0, "happy"), (26.49, "shock")]), look=0.8, door=ease((T - 26.13) / 0.3))
    k = ease((T - 26.3) / 0.6)
    MOM.draw(ctx, lerp(640, 560, k), 1060, 1.1, "cold", T, pose="walk" if k < 1 else "stand", walk_phase=T * 2,
             look=-0.8, arms=("hip", "hip"))
    label(ctx, "MOM!", 520, 330, 70, bg=st.PINK, scale=pop(T - 26.49))


def s_card(ctx, t, d):
    T = 27.2 + t
    st.night_wall(ctx, 2000)
    closeup(ctx, MOM, keyed(T, [(0, "cold"), (28.03, "angry")]), T, arms=("down", "show"), talk=talking("mom", T))
    st.credit_card(ctx, 560, 420, 0.9 * pop(T - 27.29), rot=-0.15)
    label(ctx, "WHOSE CARD?", 330, 300, 60, fg=(1, 1, 1), scale=pop(T - 28.03))


def s_mine(ctx, t, d):
    T = 28.55 + t
    st.burst(ctx, T, "#a8e6ff", "#4fb0e8", cy=560)
    closeup(ctx, KID_SH, keyed(T, [(0, "smirk"), (29.21, "smug")]), T, arms=("down", "show"), talk=talking("kid", T))
    label(ctx, "OBVIOUSLY", 360, 300, 66, fg=st.YELLOW, scale=pop(T - 29.21))


def s_yoink(ctx, t, d):
    T = 30.6 + t
    st.night_bedroom(ctx, T)
    grab = T > 30.82
    KID.draw(ctx, 220, 1060, 1.2, "shock" if grab else "smug", T, arms=("hold", "hold") if not grab else ("up", "up"))
    MOM.draw(ctx, 520, 1060, 1.2, "angry", T, arms=("down", "point") if not grab else ("show", "down"),
             talk=talking("mom", T))
    tx = lerp(240, 500, ease((T - 30.82) / 0.15)) if grab else 240
    ty = lerp(870, 660, ease((T - 30.82) / 0.15)) if grab else 870
    st.tablet(ctx, tx, ty, 0.45, T, None)
    if grab:
        st.impact_star(ctx, 380, 760, 110, T - 30.82, "YOINK!")
    label(ctx, "GIVE ME THAT", 360, 300, 60, fg=st.RED, scale=pop(T - 30.65))


def s_tap(ctx, t, d):
    T = 31.9 + t
    st.night_wall(ctx, 2000)
    st.tablet(ctx, 360, 640, 1.4, T, lambda c, x, y, w, h, TT: st.burst(c, TT, "#ffe27a", "#f29a2e",
                                                                         cx=x + w / 2, cy=y + h / 2))
    st.number_counter(ctx, 360, 640, 0.75, 1000000, T)
    k = ease((T - 32.0) / 0.19)   # mom's finger comes in and taps once
    st.block(ctx, lerp(760, 470, k), lerp(1100, 700, k), 70, 260, 30, MOM.skin, 5)
    st.tap_ripple(ctx, 500, 700, (T - 32.19) / 0.5)
    label(ctx, "TAP", 360, 300, 70, fg=(1, 1, 1), scale=pop(T - 32.19))


def s_refund(ctx, t, d):
    T = 33.35 + t
    st.burst(ctx, T, "#ffb0b0", "#a8202e", cy=640)
    st.number_counter(ctx, 360, 640, 1.0, 1000000, T)
    st.stamp(ctx, 360, 640, "REFUNDED", T - 33.4, size=90)


def s_zero(ctx, t, d):
    T = 34.55 + t
    st.night_wall(ctx, 2000)
    v = lerp(1000000, 0, ease((T - 34.6) / 0.55))
    st.number_counter(ctx, 360, 560, 1.0, v, T, col="#ff4f5a" if T > 35.15 else "#ffd84a")
    KID.draw(ctx, 360, 1080, 1.2, "shock" if T < 35.2 else "cry", T, arms=("up", "up"))
    if T > 35.2:
        st.shockwave(ctx, 360, 560, (T - 35.2) / 0.5, col=(1, 0.3, 0.3))


def s_gone(ctx, t, d):
    T = 35.8 + t
    st.night_wall(ctx, 2000)
    if T < 36.32:
        st.pet_puppy(ctx, 520, 1000, 0.9, T)
    else:
        st.poof(ctx, 520, 860, 140, (T - 36.32) / 0.5)
    KID.draw(ctx, 210, 1080, 1.2, "cry", T, arms=("down", "point"), look=0.8)
    label(ctx, "GONE", 360, 330, 90, fg=(1, 1, 1), scale=pop(T - 36.32))


def s_forgot(ctx, t, d):
    T = 37.05 + t
    st.night_bedroom(ctx, T, door_open=1.0)
    k = ease((T - 37.1) / 1.2)
    MOM.draw(ctx, lerp(380, 600, k), 1060, 1.15, "smug", T, pose="walk", walk_phase=T * 1.8, arms=("hold", "down"))
    KID.draw(ctx, 170, 1060, 1.15, keyed(T, [(0, "cry"), (37.98, "smirk")]), T, look=0.8)
    label(ctx, "ONE THING...", 360, 330, 64, fg=st.YELLOW, scale=pop(T - 38.3))


def s_onemore(ctx, t, d):
    T = 38.95 + t
    st.dark_glow_bg(ctx, T, glow_col="#9d5cff", base="#1b1426")
    st.mystery_box(ctx, 360, 1000, 1.15, T, glow_a=0.6 + 0.2 * math.sin(T * 8))
    style.sparkle(ctx, 520, 520, 40 * (1 + 0.3 * math.sin(T * 9)))
    label(ctx, "+1 SPIN", 360, 330, 90, bg=st.GREEN, scale=pop(T - 40.42))


def s_comment(ctx, t, d):
    T = 41.6 + t
    st.night_bedroom(ctx, T)
    typed = "SPIN"[:int(clamp((T - 41.75) / 0.3) * 4)]
    st.comments_sheet(ctx, T, [("@robux_rich", "i'd spin 1000 times", "#ff5fa2"),
                               ("@blockfan", "mom always wins", "#4f8bff")], typed=typed, y0=560, likes_t=42.2)
    label(ctx, "COMMENT \"SPIN\"", 360, 330, 54, bg=st.RED, scale=pop(T - 41.7))


def s_end(ctx, t, d):
    s_hook(ctx, t, d, T0=0.0, frozen=True)   # the first frame again: the Short loops


# ================================================================ shots
S = []


def shot(start, draw, keys, **kw):
    kw.setdefault("vignette", 0.15)
    kw.setdefault("top", 250)
    S.append(dict(start=start, draw=draw, keys=keys, **kw))


def punch(t0, z0, c0, t_key, z1, c1, m=0.16):
    return [(t0, z0, c0), (t_key, z1, c1, m)]


C = (360, 700)
CU = dict(closeup=True, keep=FACE_KEEP)
CARDK = [(170, 380, 550, 560)]
shot(0.00, s_hook, [(0.0, 1.25, (360, 640)), (0.12, 1.0, (360, 700), 0.12), (0.67, 1.1, (360, 660), 0.12)],
     shake=(0.67, 10), **CU)
shot(1.65, s_tensec, punch(1.65, 1.0, C, 2.08, 1.1, (360, 660), 0.12), shake=(0.43, 12), keep=[(160, 480, 560, 790)])
shot(3.0, s_watch, punch(3.0, 1.0, C, 3.38, 1.08, (380, 640), 0.12), **CU)
shot(3.95, s_sec10, punch(3.95, 1.0, C, 4.0, 1.06, (360, 680), 0.1), shake=(0.05, 12), keep=CARDK)
shot(4.8, s_open, punch(4.8, 1.0, C, 4.99, 1.1, (400, 760), 0.14), shake=(0.19, 10))
shot(6.3, s_sec9, punch(6.3, 1.0, C, 6.35, 1.06, (360, 680), 0.1), shake=(0.05, 12), keep=CARDK)
shot(7.0, s_ticket, punch(7.0, 1.0, C, 7.52, 1.1, (360, 660), 0.14), keep=[(150, 520, 570, 720)])
shot(8.8, s_sec8, punch(8.8, 1.0, C, 8.84, 1.06, (360, 680), 0.1), shake=(0.04, 12), keep=CARDK)
shot(9.65, s_spin, punch(9.65, 1.0, C, 10.44, 1.08, (360, 660), 0.14), keep=[(60, 545, 660, 735)])
shot(10.9, s_sec7, punch(10.9, 1.0, C, 10.94, 1.06, (360, 680), 0.1), shake=(0.04, 12), keep=CARDK)
shot(11.75, s_hundred, punch(11.75, 1.0, C, 12.6, 1.1, (360, 640), 0.12), shake=(0.85, 14),
     keep=[(60, 425, 660, 615)])
shot(13.8, s_sec6, punch(13.8, 1.0, C, 14.17, 1.06, (360, 680), 0.1), shake=(0.37, 12), keep=CARDK)
shot(14.7, s_glitch, punch(14.7, 1.0, C, 15.18, 1.1, (360, 660), 0.1), shake=(0.48, 16), keep=[(30, 360, 690, 920)])
shot(15.8, s_free, punch(15.8, 1.0, C, 16.79, 1.06, (360, 680), 0.14), keep=[(30, 360, 690, 920)])
shot(17.45, s_subs, punch(17.45, 1.0, C, 17.93, 1.08, (360, 640), 0.12), keep=[(140, 500, 580, 620)])
shot(18.9, s_wheel, punch(18.9, 1.0, C, 19.2, 1.06, (360, 680), 0.14), keep=[(100, 400, 620, 940)])
shot(19.85, s_sec5, punch(19.85, 1.0, C, 20.28, 1.06, (360, 680), 0.1), shake=(0.43, 12), keep=CARDK)
shot(20.95, s_gold, punch(20.95, 1.0, C, 21.47, 1.12, (360, 640), 0.12), shake=(0.52, 10))
shot(22.55, s_million, punch(22.55, 1.0, C, 22.96, 1.08, (360, 660), 0.12), shake=(0.41, 10), closeup=True,
     keep=[(110, 220, 610, 760)])
shot(23.95, s_pet, punch(23.95, 1.0, C, 24.45, 1.08, (370, 720), 0.12), shake=(0.5, 10))
shot(26.1, s_momin, punch(26.1, 1.0, (360, 760), 26.49, 1.06, (400, 760), 0.15))
shot(27.2, s_card, punch(27.2, 1.0, C, 27.29, 1.08, (360, 660), 0.1), closeup=True,
     keep=FACE_KEEP + [(400, 320, 700, 520)])
shot(28.55, s_mine, punch(28.55, 1.0, C, 29.21, 1.08, (360, 660), 0.12), **CU)
shot(30.6, s_yoink, punch(30.6, 1.0, (360, 760), 30.82, 1.08, (380, 760), 0.1), shake=(0.22, 14))
shot(31.9, s_tap, punch(31.9, 1.0, C, 32.19, 1.08, (400, 660), 0.1), keep=[(80, 430, 640, 850)])
shot(33.35, s_refund, punch(33.35, 1.0, C, 33.4, 1.08, (360, 660), 0.1), shake=(0.05, 16), keep=[(60, 545, 660, 735)])
shot(34.55, s_zero, punch(34.55, 1.0, C, 35.2, 1.1, (360, 640), 0.12), shake=(0.65, 14), keep=[(60, 465, 660, 655)])
shot(35.8, s_gone, punch(35.8, 1.0, C, 36.32, 1.08, (380, 700), 0.12))
shot(37.05, s_forgot, punch(37.05, 1.0, (360, 760), 38.3, 1.06, (300, 760), 0.15))
shot(38.95, s_onemore, punch(38.95, 1.0, C, 40.42, 1.12, (360, 700), 0.14), shake=(1.47, 10),
     keep=[(160, 620, 560, 1000)])
shot(41.6, s_comment, punch(41.6, 1.0, C, 41.7, 1.04, (360, 720), 0.2))
shot(43.55, s_end, [(43.55, 1.0, C)], **CU)
SHOTS = S
for k, s in enumerate(SHOTS):
    s["end"] = SHOTS[k + 1]["start"] if k + 1 < len(SHOTS) else TOTAL

# ---------------------------------------------------------------- countdown timer pill (every shot)
HUD = [(4.0, "0:10"), (6.35, "0:09"), (8.84, "0:08"), (10.94, "0:07"), (14.17, "0:06"), (20.28, "0:05")]


def hud_state(T):
    cur = (0.0, "0:10")
    for ts, txt in HUD:
        if T >= ts:
            cur = (ts, txt)
    if T >= 26.13:                     # mom walks in: the clock freezes in red
        cur = (26.13 if T < 35.2 else 35.2, "0:05" if T < 35.2 else "0:00")
    return cur


def make_overlay(T0, frozen=False):
    def ov(ctx, t, d):
        T = T0 if frozen else T0 + t
        ts, txt = hud_state(T)
        st.hud_timer(ctx, txt, bump=math.exp(-9 * (T - ts)) if ts > 0 else 0.0, urgent=T >= 26.13)
    return ov


for s in SHOTS:
    s["overlay"] = make_overlay(0.0, frozen=True) if s["draw"] is s_end else make_overlay(s["start"])

# ---------------------------------------------------------------- SFX (time, file, volume before SFX_GAIN)
SFX = [
    (0.03, "boom.wav", 1.6), (0.67, "ding.wav", 0.9), (1.02, "coin.wav", 0.7), (1.7, "swish.wav", 0.6),
    (2.08, "hit.wav", 1.3), (2.38, "tick.wav", 0.7), (3.06, "pop.wav", 0.7), (3.38, "sparkle.wav", 0.8),
    (4.0, "hit.wav", 1.3), (4.47, "tick.wav", 0.7), (4.99, "pop.wav", 0.8), (5.1, "ding.wav", 0.8),
    (5.34, "pop.wav", 0.6), (6.35, "hit.wav", 1.3), (6.74, "tick.wav", 0.7), (7.1, "swish.wav", 0.6),
    (7.52, "ding.wav", 0.9), (8.15, "pop.wav", 0.7), (8.84, "hit.wav", 1.3), (9.18, "tick.wav", 0.7),
    (9.84, "tick.wav", 0.6), (10.0, "tick.wav", 0.6), (10.2, "tick.wav", 0.6), (10.44, "pop.wav", 0.7),
    (10.94, "hit.wav", 1.3), (11.29, "tick.wav", 0.7), (11.98, "tick.wav", 0.6), (12.2, "tick.wav", 0.6),
    (12.6, "boom.wav", 1.6), (12.65, "chaching.wav", 0.9), (14.17, "hit.wav", 1.3), (14.83, "pop.wav", 0.6),
    (15.18, "buzz.wav", 0.8), (15.5, "click.wav", 0.6), (16.0, "pop.wav", 0.6), (16.24, "pop.wav", 0.6),
    (16.48, "pop.wav", 0.6), (16.79, "ding.wav", 0.8), (17.47, "pop.wav", 0.6), (17.93, "click.wav", 0.9),
    (17.96, "pop.wav", 0.7), (18.5, "sparkle.wav", 0.7), (18.95, "swish.wav", 0.6), (19.2, "tick.wav", 0.6),
    (19.4, "tick.wav", 0.6), (19.6, "tick.wav", 0.6), (20.28, "hit.wav", 1.3), (20.6, "tick.wav", 0.7),
    (21.09, "pop.wav", 0.6), (21.47, "boom.wav", 1.4), (21.96, "ding.wav", 0.9), (22.6, "pop.wav", 0.7),
    (22.96, "chaching.wav", 0.9), (23.5, "coin.wav", 0.6), (24.02, "tick.wav", 0.6), (24.45, "boom.wav", 1.4),
    (24.88, "sparkle.wav", 0.8), (25.29, "ding.wav", 0.9), (25.58, "pop.wav", 0.6), (26.13, "hit.wav", 1.3),
    (26.49, "step.wav", 0.6), (26.78, "step.wav", 0.6), (27.29, "pop.wav", 0.8), (28.03, "hit.wav", 1.3),
    (28.67, "pop.wav", 0.6), (29.21, "sparkle.wav", 0.7), (29.6, "pop.wav", 0.5), (30.65, "pop.wav", 0.6),
    (30.82, "hit.wav", 1.3), (30.86, "swish.wav", 0.7), (31.97, "pop.wav", 0.6), (32.19, "click.wav", 0.9),
    (32.52, "tick.wav", 0.6), (33.4, "buzz.wav", 0.8), (33.45, "boom.wav", 1.6), (34.61, "tick.wav", 0.6),
    (34.8, "tick.wav", 0.6), (35.0, "tick.wav", 0.6), (35.2, "hit.wav", 1.3), (35.89, "pop.wav", 0.6),
    (36.32, "boom.wav", 1.4), (36.4, "boing.wav", 0.6), (37.13, "step.wav", 0.6), (37.6, "step.wav", 0.6),
    (37.98, "pop.wav", 0.7), (38.3, "pop.wav", 0.7), (39.03, "swish.wav", 0.6), (39.51, "sparkle.wav", 0.8),
    (40.03, "tick.wav", 0.6), (40.42, "hit.wav", 1.3), (40.92, "ding.wav", 0.9), (41.7, "pop.wav", 0.8),
    (41.8, "type_key.wav", 0.6), (41.95, "type_key.wav", 0.6), (42.2, "ding.wav", 0.7), (42.58, "pop.wav", 0.6),
    (43.09, "hit.wav", 1.0), (43.5, "whip.wav", 0.8),
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
    engine.set_voice(os.path.join(os.path.dirname(os.path.abspath(sys.argv[2])), "voice.mp3"))
    safezone.fit(SHOTS, sys.modules[__name__])
    SHOTS[-1]["keys"] = [(SHOTS[-1]["start"], SHOTS[0]["keys"][0][1], SHOTS[0]["keys"][0][2])]
    render(SHOTS, TOTAL, sys.argv[1], xfade=0.0, grain=2, fade_out=0.0, fade_in=0.0, **kw)

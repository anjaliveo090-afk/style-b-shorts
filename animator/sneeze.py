"""Story: "What If You Got 1 ROBUX Every Time You Sneezed?" (script written from script_guide.md).

Voice: output/sneeze/voice.mp3 (46.5 s, the user's voice tool) + subs.srt. The SRT leaves out the
sneezes; they were found in the loudness: "Ah" 2.70, "AH" 3.0, ACHOO 3.34, and a final ACHOO at 45.96.
Every DAY card is followed by a shot in a different place/angle, so it counts as a new visual
(the grandma_pro drop check found a 3.5 s same-place stretch).

Run (from animator/):
  python3 sneeze.py ../output/sneeze/clips/animation.mp4 ../output/sneeze/cues.json"""
import math
import os
import sys

import engine
import sets as st
import style
from engine import clamp, ease, hexc, keyed, lerp, pop, render
from sets import label
from style import Block

TOTAL = 47.0
engine.LIPSYNC = True
engine.DRIFT = (0.035, 9, -6)
engine.ENERGY = 3.0
SFX_GAIN = 0.28                      # this voice tool: 0.28 measured right on grandma_pro
MUSIC = dict(dips=[(36.15, 37.9)])   # quieter under "Your nose... completely quiet"
DIALOGUE = {"kid": [(2.63, 5.55), (29.97, 32.01), (45.7, 46.3)], "mom": [(27.65, 29.75), (38.03, 38.93)]}
ACHOO1, ACHOO_MOM, ACHOO_END = 3.34, 40.37, 45.96

KID = style.KID
KID_SH = Block("#2fbf8f", pants="#2b3f8f", skin="#e6ddd6", hair="bowl", hair_col="#4a2f22", emblem="star",
               emblem_col="#ffd84a", shoes="white", shades=True)
KID_BIZ = Block("#2b2f45", pants="#2b2f45", skin="#e6ddd6", hair="bowl", hair_col="#4a2f22", outfit="suit",
                accent="#e8323a", shoes="dark", shades=True)
KID_GAME = style.KID_GAME
MOM = style.MOM
CROWD = [style.crowd_member(i) for i in range(6)]

U1 = Block.HW * 64
FACE_S = 4.2
FACE_KEEP = [(165, 300, 555, 760)]
NOSE_Y = 560 + 0.12 * U1 * FACE_S    # the nose of a close-up face (head centre at y 560)


def talking(who, T):
    return any(a <= T <= b for a, b in DIALOGUE[who])


def closeup(ctx, ch, expr, T, x=360, look=0.0, arms=("down", "down"), s=FACE_S, talk=False, bob=0.35):
    # a calmer idle sway: at close-up scale the full sway moves the whole frame like a shaking camera
    ch.draw(ctx, x, 560 + 2.5 * U1 * s, s, expr, T, arms=arms, look=look, talk=talk, bob=bob)


def counter(ctx, T, v, y=300, s=0.85, col="#ffd84a"):
    st.number_counter(ctx, 360, y, s, v, T, col=col)


def coins_burst(ctx, T, t0, x, y, n=8, spread=260):
    k = T - t0
    if not 0 <= k < 1.2:
        return
    for i in range(n):
        a = -math.pi / 2 + (i - n / 2) * 0.35
        d = spread * ease(min(1, k / 0.5))
        st.coin(ctx, x + math.cos(a) * d, y + math.sin(a) * d + 300 * k * k, 0.7, spin=T * 6 + i)


# ================================================================ hook
def s_hook(ctx, t, d, T0=0.0, frozen=False):
    T = T0 + (0.0 if frozen else t)
    st.burst(ctx, T, "#ffe27a", "#f29a2e", cy=560, spin=0.4)
    closeup(ctx, KID, keyed(T, [(0, "worried"), (0.98, "stars")]), T)
    st.particle_cloud(ctx, 360, NOSE_Y + 40, 110, T, col="#5a5060", n=10, seed=2)
    if T >= 0.98:
        st.coin(ctx, 580, 300, 1.4 * pop(T - 0.98), spin=T * 3)
    label(ctx, "+1 R$", 330, 280, 74, fg=st.YELLOW, scale=pop(T - 0.98) if T >= 0.98 else 0.0)


def s_rule(ctx, t, d):
    T = 1.6 + t
    st.night_bedroom(ctx, T)
    KID.draw(ctx, 300, 1090, 1.3, keyed(T, [(0, "neutral"), (2.02, "happy")]), T, arms=("hold", "down"))
    st.block(ctx, 470, 940, 160, 90, 10, hexc("#4f8bff"), 5)          # a tissue box
    st.block(ctx, 520, 900, 60, 50, 20, (1, 1, 1), 4, gloss=False)
    label(ctx, "ACHOO = 1 R$", 360, 330, 64, bg=st.GREEN, scale=pop(T - 2.02))


def s_achoo(ctx, t, d):
    T = 2.63 + t
    st.night_wall(ctx, 2000)
    swell = ease((T - 2.7) / 0.6) if T < ACHOO1 else 0.0
    expr = "sleepy" if T < ACHOO1 else "crazy"
    closeup(ctx, KID, expr, T, s=FACE_S * (1 + 0.06 * swell), talk=talking("kid", T))
    if T < ACHOO1:
        st.bold_text(ctx, "Ah..." if T < 3.0 else "AH...", 360, 270, 60 + 40 * swell, (1, 1, 1))
    st.sneeze_blast(ctx, 360, NOSE_Y, T - ACHOO1, direction=1, size=110)
    if T >= ACHOO1:
        st.flash(ctx, 0.6 * math.exp(-10 * (T - ACHOO1)))
        st.coin(ctx, 200, 380 - (T - ACHOO1) * 200, 1.0, spin=T * 6)
        st.bold_text(ctx, "+1", 260, 300 - (T - ACHOO1) * 200, 60, st.GREEN)


def s_paid(ctx, t, d):
    T = 3.69 + t
    st.burst(ctx, T, "#b8ffb0", "#2e9c46", cy=560)
    closeup(ctx, KID, keyed(T, [(0, "shock"), (5.24, "stars")]), T, arms=("down", "phone"), talk=talking("kid", T))
    st.toast(ctx, 360, 250, "+1 Robux received!", T - 3.75, col="#4fd16a")
    label(ctx, "PAID?!", 360, 360, 80, fg=st.YELLOW, scale=pop(T - 5.24))


# ================================================================ day 1: pepper
def s_day1(ctx, t, d):
    T = 5.85 + t
    st.kitchen(ctx, T, night=False)
    KID.draw(ctx, 300, 1180, 1.25, "grin", T, arms=("down", "show"))
    st.pepper_jar(ctx, 470, 900, 0.8)
    st.day_text(ctx, "DAY 1", 360, 380, T - 5.93)


def s_sniff(ctx, t, d):
    T = 6.6 + t
    st.burst(ctx, T, "#e0d0c0", "#6b5a4a", cy=560)
    closeup(ctx, KID, keyed(T, [(0, "smirk"), (7.64, "crazy")]), T)
    st.pepper_jar(ctx, 540, NOSE_Y + 290, 1.0, open_k=clamp((T - 6.65) / 0.3))
    st.particle_cloud(ctx, 400, NOSE_Y, 300, T, n=60, seed=4, k=clamp((T - 6.8) / 0.8))
    st.sneeze_blast(ctx, 360, NOSE_Y, T - 8.28, direction=-1)
    label(ctx, "SNIFF!", 360, 280, 74, fg=(1, 1, 1), scale=pop(T - 6.61))


def s_fifty(ctx, t, d):
    T = 8.9 + t
    st.burst(ctx, T, "#ffe27a", "#f29a2e", cy=640, spin=0.8)
    shake = math.sin(T * 30) * 12
    KID.draw(ctx, 360 + shake, 1100, 1.35, "crazy", T, arms=("up", "up"))
    for k in range(5):   # rapid sneezes
        st.sneeze_blast(ctx, 300, 690, T - (9.0 + k * 0.35), direction=-1 if k % 2 else 1, txt="ACHOO!", size=60)
    v = int(lerp(0, 50, clamp((T - 9.0) / 1.3)))
    counter(ctx, T, v)
    coins_burst(ctx, T, 10.23, 360, 640)


# ================================================================ day 2: the cat
def s_day2(ctx, t, d):
    T = 11.0 + t
    st.street(ctx, T)
    KID.draw(ctx, 250, 1120, 1.1, "determined", T, pose="walk", walk_phase=T * 2)
    st.cat(ctx, 520, 1080, 0.55, T, dusty=1.0, expr="neutral")
    st.day_text(ctx, "DAY 2", 360, 380, T - 11.05)


def s_cat(ctx, t, d):
    T = 12.55 + t
    st.burst(ctx, T, "#e0d0c0", "#8a7a68", cy=560)
    st.dust_cloud(ctx, 380, 700, 300, (T - 12.7) / 0.9)            # behind them
    KID.draw(ctx, 360, 1150, 1.35, keyed(T, [(0, "happy"), (13.4, "worried")]), T, arms=("hold", "hold"))
    st.cat(ctx, 380, 980, 0.95, T, dusty=1.0, expr="happy")
    label(ctx, "DUSTIEST CAT", 360, 280, 60, bg="#8a7a68", scale=pop(T - 12.89))


def s_fivek(ctx, t, d):
    T = 14.6 + t
    st.street(ctx, T)
    KID.draw(ctx, 300, 1120, 1.25, "crazy", T, arms=("up", "up"))
    st.sneeze_blast(ctx, 300, 780, T - 14.65, direction=1)
    st.dust_cloud(ctx, 560, 820, 200, (T - 14.7) / 0.8)
    v = int(lerp(50, 5000, ease((T - 14.7) / 0.6)))
    counter(ctx, T, v)
    coins_burst(ctx, T, 14.99, 360, 600, n=10)


# ================================================================ day 3: the attic
def s_day3(ctx, t, d):
    T = 16.1 + t
    st.attic(ctx, T)
    KID.draw(ctx, 360, 1180, 1.0, "worried", T, arms=("down", "down"), look=0.4)
    st.day_text(ctx, "DAY 3", 360, 380, T - 16.13)


def s_attic_boom(ctx, t, d):
    T = 17.3 + t
    st.attic(ctx, T)
    st.dust_cloud(ctx, 360, 820, 420, (T - 17.35) / 0.8, col="#c8b898")
    KID.draw(ctx, 360, 1180, 1.2, "shock", T, arms=("up", "up"))
    label(ctx, "GRANDMA'S ATTIC", 360, 300, 56, bg="#7a3f2a", scale=pop(T - 17.33))


def s_million(ctx, t, d):
    T = 18.2 + t
    st.burst(ctx, T, "#ffe27a", "#f29a2e", cy=560)
    st.coin_pile(ctx, 360, 1280, 760, 380, T)
    closeup(ctx, KID, "stars", T, arms=("up", "up"), s=3.2)
    v = lerp(5000, 1000000, ease((T - 18.2) / 0.4))
    counter(ctx, T, v, y=290)
    if T > 18.66:
        st.shockwave(ctx, 360, 290, (T - 18.66) / 0.5, r_max=400)


# ================================================================ day 4: the launch
def s_day4(ctx, t, d):
    T = 19.65 + t
    tops = st.obby(ctx, T, y_top=920)
    KID_GAME.draw(ctx, tops[0][0], tops[0][1], 0.95, "smug", T, arms=("hip", "hip"))
    st.day_text(ctx, "DAY 4", 360, 380, T - 19.73)


def s_launch(ctx, t, d):
    T = 20.6 + t
    st.game_sky(ctx)
    st.block_clouds(ctx, T)
    st.lava(ctx, 1150, T)
    for i in range(7):
        st.platform(ctx, -60 + i * 150, 980 - i * 25, 100, ("#2cd5fc", "#fa3a9f", "#f7e04a", "#a694e1")[i % 4],
                    num=90 + i)
    st.platform(ctx, 560, 800, 200, "#4fd16a")
    st.finish_flag(ctx, 690, 800, 0.9, T)
    p = clamp((T - 21.55) / 0.9)
    x = lerp(60, 640, ease(p))
    y = lerp(980, 800, p) - math.sin(math.pi * p) * 380
    if T < 21.55:
        KID_GAME.draw(ctx, 60, 980, 1.0, "sleepy", T, arms=("down", "down"))
    else:
        st.speed_lines(ctx, T, x, y - 150, n=16, r0=150, r1=500, a=0.4)
        KID_GAME.draw(ctx, x, y, 1.0, "crazy", T, arms=("up", "up"), pose="jump")
    st.sneeze_blast(ctx, 60, 840, T - 21.55, direction=-1)
    if p >= 1:
        st.confetti(ctx, T, 22.45, n=36)
    label(ctx, "LAUNCH!", 360, 330, 80, fg=st.YELLOW, scale=pop(T - 21.65))


def s_subs(ctx, t, d):
    T = 23.05 + t
    st.street(ctx, T)
    for i, x in enumerate((90, 230, 490, 630)):
        CROWD[i].draw(ctx, x, 1100, 0.85, "stars" if T > 23.57 else "happy", T, arms=("up", "up"))
    st.subscribe_button(ctx, 360, 560, 1.05, pressed=clamp((T - 23.57) * 4))
    st.cursor(ctx, 420, 600, 1.6, click=1.0 if 23.53 < T < 23.7 else 0.0)
    for k in range(4):
        st.sneeze_blast(ctx, 90 + k * 180, 850, T - (24.75 + k * 0.08), direction=1 if k % 2 else -1, txt="", size=40)
    label(ctx, "FREE SNEEZE", 360, 330, 58, bg=st.BLUE, scale=pop(T - 24.72))


# ================================================================ day 5: mom
def s_day5(ctx, t, d):
    T = 25.55 + t
    st.kitchen(ctx, T, night=False)
    k = ease((T - 25.7) / 0.7)
    MOM.draw(ctx, lerp(720, 470, k), 1180, 1.25, "cold", T, pose="walk" if k < 1 else "stand", walk_phase=T * 2)
    st.day_text(ctx, "DAY 5", 360, 380, T - 25.61)


def s_jar(ctx, t, d):
    T = 26.3 + t
    st.burst(ctx, T, "#e0d0c0", "#6b5a4a", cy=560)
    st.pepper_jar(ctx, 360, 900, 1.6)
    st.block(ctx, 210, 960, 300, 260, 60, MOM.skin, 5)     # mom's hand holding it up
    label(ctx, "PEPPER?!", 360, 320, 74, fg=st.RED, scale=pop(T - 27.05))


def s_mom_why(ctx, t, d):
    T = 27.65 + t
    st.kitchen(ctx, T, night=False)
    closeup(ctx, MOM, keyed(T, [(0, "cold"), (28.96, "angry")]), T, arms=("down", "show"),
            talk=talking("mom", T))


def s_kitchen_sneeze(ctx, t, d):
    T = 28.9 + t
    st.kitchen(ctx, T, night=False)
    st.particle_cloud(ctx, 360, 700, 380, T, n=60, seed=6)
    for k, (x, y) in enumerate(((560, 520), (150, 700), (420, 860))):
        st.speech_bubble(ctx, x, y, "ACHOO!", 42, T - (28.95 + k * 0.15), tail=(-1, 1))
    label(ctx, "SNEEZING?!", 360, 300, 66, fg=(1, 1, 1), scale=pop(T - 29.39))


def s_business(ctx, t, d):
    T = 29.95 + t
    st.night_wall(ctx, 2000)
    closeup(ctx, KID_BIZ, "smug", T, arms=("down", "show"), talk=talking("kid", T))


def s_office(ctx, t, d):
    T = 31.15 + t
    st.office(ctx, T)
    KID_BIZ.draw(ctx, 230, 1040, 1.2, "smug", T, arms=("down", "point"), talk=talking("kid", T))
    st.block(ctx, 380, 420, 300, 260, 14, (1, 1, 1), 5)    # a chart going up
    pts = [(400, 650), (460, 610), (520, 630), (580, 520), (650, 450)]
    k = clamp((T - 31.2) / 0.5)
    for i in range(1, len(pts)):
        if i / (len(pts) - 1) <= k + 1e-6:
            ctx.move_to(*pts[i - 1])
            ctx.line_to(*pts[i])
    ctx.set_source_rgb(*st.GREEN)
    ctx.set_line_width(12)
    ctx.stroke()
    label(ctx, "BUSINESS", 360, 300, 66, bg=st.UI_DARK, fg=st.GREEN, scale=pop(T - 31.51))


# ================================================================ the punishment
def s_clean(ctx, t, d):
    T = 32.5 + t
    st.day_room(ctx, T)
    k = ease((T - 32.55) / 1.4)
    MOM.draw(ctx, lerp(200, 520, k), 1150, 1.2, "angry", T, pose="walk", walk_phase=T * 3, arms=("hold", "hold"))
    st.vacuum(ctx, lerp(320, 640, k), 1150, 0.85, T)
    st.sparkles(ctx, T, 300, 800, spread=260, n=10, seed=3)
    label(ctx, "CLEAN!", 360, 330, 80, fg=st.BLUE, scale=pop(T - 32.73))


def s_nolist(ctx, t, d):
    T = 34.05 + t
    st.burst(ctx, T, "#c4d8ff", "#4a5aa8", cy=640)
    xs = (130, 360, 590)
    st.dust_cloud(ctx, xs[0], 640, 90, 0.7)
    st.pepper_jar(ctx, xs[1], 720, 0.7)
    st.cat(ctx, xs[2], 720, 0.42, T, dusty=0.6)
    for x, tk in zip(xs, (34.29, 34.96, 35.65)):
        st.red_x(ctx, x, 640, 85, (T - tk) / 0.2)
    label(ctx, "ALL CLEAN", 360, 330, 64, bg=st.BLUE, scale=pop(T - 34.29))


def s_quiet(ctx, t, d):
    T = 36.1 + t
    st.night_wall(ctx, 2000)
    closeup(ctx, KID, keyed(T, [(0, "sad"), (37.47, "cry")]), T)
    st.tint(ctx, (0.5, 0.5, 0.6), 0.2)
    st.bold_text(ctx, "...", 480, NOSE_Y - 60, 90, (1, 1, 1), scale=pop(T - 36.41))
    label(ctx, "QUIET...", 360, 280, 66, fg=(1, 1, 1), scale=pop(T - 37.47))


def s_bless(ctx, t, d):
    T = 37.95 + t
    st.kitchen(ctx, T, night=False)
    closeup(ctx, MOM, keyed(T, [(0, "smirk"), (38.55, "wink")]), T, arms=("down", "show"), talk=talking("mom", T))
    st.hearts(ctx, T, 38.55, 360, 420, n=5)


def s_mom_sneeze(ctx, t, d):
    T = 39.1 + t
    st.kitchen(ctx, T, night=True)
    st.tint(ctx, (0.03, 0.03, 0.15), 0.3)
    swell = ease((T - 39.5) / 0.8) if T < ACHOO_MOM else 0.0
    closeup(ctx, MOM, "worried" if T < ACHOO_MOM else "crazy", T, s=FACE_S * (1 + 0.05 * swell))
    st.sneeze_blast(ctx, 360, NOSE_Y, T - ACHOO_MOM, direction=-1, size=110)
    if T >= ACHOO_MOM:
        st.flash(ctx, 0.5 * math.exp(-10 * (T - ACHOO_MOM)))


def s_to_her(ctx, t, d):
    T = 41.2 + t
    st.burst(ctx, T, "#ffd0e6", "#ff5fa2", cy=640)
    KID.draw(ctx, 150, 1100, 0.95, "cry", T, arms=("up", "up"))
    MOM.draw(ctx, 560, 1100, 1.05, "laugh", T, arms=("up", "up"))
    for i in range(10):   # coins flying from the kid to mom
        ph = (T * 1.6 + i / 10) % 1
        st.coin(ctx, lerp(170, 540, ph), 760 - math.sin(ph * math.pi) * 260, 0.6, spin=T * 5 + i)
    v = lerp(1000000, 0, ease((T - 41.3) / 1.0))
    counter(ctx, T, v, y=300, col="#ff4f5a")
    label(ctx, "MOM: 1,000,000", 360, 420, 46, bg=st.PINK, scale=pop(T - 42.35))


def s_comment(ctx, t, d):
    T = 42.8 + t
    st.night_bedroom(ctx, T)
    typed = "ACHOO"[:int(clamp((T - 42.95) / 0.4) * 5)]
    st.comments_sheet(ctx, T, [("@pepper_pro", "i'd sniff the whole jar", "#ff5fa2"),
                               ("@cat_lover", "the dusty cat lol", "#4f8bff")], typed=typed, y0=560, likes_t=44.0)
    label(ctx, "COMMENT \"ACHOO\"", 360, 330, 50, bg=st.RED, scale=pop(T - 42.92))


def s_final(ctx, t, d):
    T = 45.1 + t
    st.burst(ctx, T, "#ffe27a", "#f29a2e", cy=560, spin=0.4)
    swell = ease((T - 45.4) / 0.5) if T < ACHOO_END else 0.0
    closeup(ctx, KID, "sleepy" if T < ACHOO_END else "crazy", T, s=FACE_S * (1 + 0.06 * swell), talk=talking("kid", T))
    st.particle_cloud(ctx, 360, NOSE_Y + 40, 110, T, col="#5a5060", n=10, seed=2)
    st.sneeze_blast(ctx, 360, NOSE_Y, T - ACHOO_END, direction=1, size=110)


# ================================================================ shots
S = []


def shot(start, draw, keys, **kw):
    kw.setdefault("vignette", 0.15)
    S.append(dict(start=start, draw=draw, keys=keys, **kw))


def punch(t0, z0, c0, t_key, z1, c1, m=0.16):
    return [(t0, z0, c0), (t_key, z1, c1, m)]


C = (360, 700)
CU = dict(closeup=True, keep=FACE_KEEP)
CARD = [(170, 300, 550, 460)]
shot(0.00, s_hook, [(0.0, 1.25, (360, 640)), (0.12, 1.0, (360, 700), 0.12), (0.98, 1.1, (360, 660), 0.12)],
     shake=(0.98, 5), **CU)
shot(1.6, s_rule, punch(1.6, 1.0, (360, 760), 2.02, 1.08, (360, 740), 0.14), keep=[(130, 270, 590, 390)])
shot(2.63, s_achoo, [(2.63, 1.0, C), (3.0, 1.06, (360, 690), 0.2), (ACHOO1, 1.14, (360, 660), 0.08)],
     shake=(ACHOO1 - 2.63, 11), **CU)
shot(3.69, s_paid, punch(3.69, 1.0, C, 5.24, 1.1, (360, 660), 0.14), **CU)
shot(5.85, s_day1, punch(5.85, 1.0, C, 6.27, 1.06, (360, 720), 0.15), keep=CARD)
shot(6.6, s_sniff, punch(6.6, 1.0, C, 8.28, 1.12, (360, 660), 0.12), shake=(8.28 - 6.6, 10), **CU)
shot(8.9, s_fifty, punch(8.9, 1.0, C, 10.23, 1.1, (360, 680), 0.14), shake=(0.1, 5))
shot(11.0, s_day2, punch(11.0, 1.0, C, 11.25, 1.06, (360, 720), 0.15), keep=CARD)
shot(12.55, s_cat, punch(12.55, 1.0, C, 13.08, 1.08, (370, 760), 0.14))
shot(14.6, s_fivek, punch(14.6, 1.0, C, 14.99, 1.08, (360, 640), 0.12), shake=(0.05, 7), keep=[(60, 205, 660, 395)])
shot(16.1, s_day3, punch(16.1, 1.0, C, 16.38, 1.06, (360, 720), 0.15), keep=CARD)
shot(17.3, s_attic_boom, punch(17.3, 1.0, (360, 760), 17.78, 1.1, (360, 760), 0.12), shake=(0.48, 8))
shot(18.2, s_million, punch(18.2, 1.0, C, 18.66, 1.08, (360, 660), 0.12), shake=(0.46, 6), closeup=True,
     keep=[(110, 200, 610, 760)])
shot(19.65, s_day4, punch(19.65, 1.0, C, 19.93, 1.06, (360, 720), 0.15), keep=CARD)
shot(20.6, s_launch, [(20.6, 1.0, (300, 760)), (21.55, 1.1, (200, 800), 0.15), (22.45, 1.0, (480, 720), 0.7)],
     shake=(21.55 - 20.6, 8))
shot(23.05, s_subs, punch(23.05, 1.0, C, 23.57, 1.08, (360, 640), 0.12), keep=[(140, 500, 580, 620)])
shot(25.55, s_day5, punch(25.55, 1.0, C, 25.8, 1.06, (360, 720), 0.15), keep=CARD)
shot(26.3, s_jar, punch(26.3, 1.0, C, 27.05, 1.1, (360, 700), 0.12), shake=(0.75, 6), keep=[(150, 260, 570, 900)])
shot(27.65, s_mom_why, punch(27.65, 1.0, C, 28.16, 1.08, (360, 660), 0.12), **CU)
shot(28.9, s_kitchen_sneeze, punch(28.9, 1.0, C, 29.39, 1.08, (360, 700), 0.12), shake=(0.49, 6))
shot(29.95, s_business, punch(29.95, 1.0, C, 30.24, 1.08, (360, 660), 0.12), **CU)
shot(31.15, s_office, punch(31.15, 1.0, (360, 760), 31.51, 1.06, (360, 740), 0.14), keep=[(370, 410, 690, 690)])
shot(32.5, s_clean, punch(32.5, 1.0, (360, 760), 32.73, 1.06, (380, 760), 0.15))
shot(34.05, s_nolist, punch(34.05, 1.0, C, 34.29, 1.05, (360, 680), 0.12), keep=[(40, 530, 680, 760)])
shot(36.1, s_quiet, [(36.1, 1.0, C), (37.9, 1.12, (360, 640), 1.6)], **CU)
shot(37.95, s_bless, punch(37.95, 1.0, C, 38.55, 1.08, (360, 660), 0.12), **CU)
shot(39.1, s_mom_sneeze, [(39.1, 1.0, C), (ACHOO_MOM, 1.14, (360, 660), 0.7)], shake=(ACHOO_MOM - 39.1, 11), **CU)
shot(41.2, s_to_her, punch(41.2, 1.0, (360, 760), 42.35, 1.06, (360, 720), 0.14), keep=[(60, 205, 660, 470)])
shot(42.8, s_comment, punch(42.8, 1.0, C, 42.92, 1.04, (360, 720), 0.2))
shot(45.1, s_final, [(45.1, 1.0, C), (ACHOO_END, 1.14, (360, 660), 0.5)], shake=(ACHOO_END - 45.1, 10), **CU)
SHOTS = S
_rw_draw, _rw_ov = st.rewind_shot(SHOTS, [41.6, 34.5, 21.9, 14.9, 7.5, 0.0])
shot(46.3, _rw_draw, [(46.3, 1.0, (360, 640))], overlay=_rw_ov, blur=False, closeup=True, keep=[])
for k, s in enumerate(SHOTS):
    s["end"] = SHOTS[k + 1]["start"] if k + 1 < len(SHOTS) else TOTAL

# ---------------------------------------------------------------- SFX (time, file, volume before SFX_GAIN)
SFX = [
    (0.03, "pop.wav", 0.7), (0.98, "coin.wav", 0.9), (1.02, "pop.wav", 0.7), (1.65, "swish.wav", 0.5),
    (2.02, "ding.wav", 0.8), (2.7, "tick.wav", 0.5), (3.0, "tick.wav", 0.6), (ACHOO1, "boom.wav", 1.6),
    (3.4, "coin.wav", 0.8), (3.75, "ding.wav", 0.8), (4.6, "pop.wav", 0.5), (5.24, "hit.wav", 1.3),
    (5.93, "hit.wav", 1.3), (6.61, "swish.wav", 0.7), (7.0, "pop.wav", 0.5), (7.64, "pop.wav", 0.6),
    (8.28, "boom.wav", 1.4), (9.0, "pop.wav", 0.6), (9.35, "pop.wav", 0.6), (9.7, "pop.wav", 0.6),
    (10.05, "pop.wav", 0.6), (10.23, "chaching.wav", 0.9), (11.05, "hit.wav", 1.3), (11.6, "step.wav", 0.5),
    (12.59, "pop.wav", 0.7), (12.89, "boing.wav", 0.5), (13.4, "tick.wav", 0.5), (14.65, "boom.wav", 1.4),
    (14.99, "chaching.wav", 0.9), (16.13, "hit.wav", 1.3), (16.9, "tick.wav", 0.5), (17.35, "boom.wav", 1.4),
    (17.78, "pop.wav", 0.6), (18.15, "tick.wav", 0.6), (18.66, "chaching.wav", 0.9), (19.73, "hit.wav", 1.3),
    (20.63, "pop.wav", 0.6), (21.55, "boom.wav", 1.6), (21.65, "whoosh.wav", 0.6), (22.45, "hit.wav", 1.0),
    (22.7, "ding.wav", 0.8), (23.57, "click.wav", 0.9), (23.6, "pop.wav", 0.7), (24.72, "ding.wav", 0.8),
    (24.85, "pop.wav", 0.5), (25.61, "hit.wav", 1.3), (25.9, "step.wav", 0.5), (26.2, "step.wav", 0.5),
    (27.05, "pop.wav", 0.8), (27.76, "pop.wav", 0.5), (28.96, "hit.wav", 1.0), (29.0, "pop.wav", 0.5),
    (29.15, "pop.wav", 0.5), (29.39, "pop.wav", 0.7), (29.81, "pop.wav", 0.6), (30.24, "sparkle.wav", 0.6),
    (31.2, "tick.wav", 0.5), (31.51, "chaching.wav", 0.8), (32.55, "swish.wav", 0.7), (32.73, "pop.wav", 0.6),
    (33.55, "sparkle.wav", 0.6), (34.29, "hit.wav", 1.2), (34.96, "hit.wav", 1.2), (35.65, "hit.wav", 1.2),
    (36.41, "tick.wav", 0.5), (37.47, "pop.wav", 0.6), (38.26, "pop.wav", 0.6), (38.55, "sparkle.wav", 0.7),
    (39.5, "tick.wav", 0.5), (39.9, "tick.wav", 0.5), (ACHOO_MOM, "boom.wav", 1.6), (41.3, "coin.wav", 0.6),
    (41.49, "chaching.wav", 0.9), (41.8, "tick.wav", 0.5), (42.35, "hit.wav", 1.0), (42.92, "pop.wav", 0.8),
    (43.05, "type_key.wav", 0.6), (43.25, "type_key.wav", 0.6), (44.0, "ding.wav", 0.7), (44.46, "pop.wav", 0.5),
    (45.76, "tick.wav", 0.5), (ACHOO_END, "boom.wav", 1.4), (46.3, "whip.wav", 0.9),
]

if __name__ == "__main__":
    import json
    import audio
    import safezone
    json.dump([{"time": round(t, 3), "file": f, "volume": round(v * SFX_GAIN, 3)} for t, f, v in sorted(SFX)],
              open(sys.argv[2], "w"), indent=1)
    audio.save(os.path.join(os.path.dirname(os.path.abspath(sys.argv[2])), "music.wav"),
               audio.music_game(TOTAL, **MUSIC))
    engine.set_voice(os.path.join(os.path.dirname(os.path.abspath(sys.argv[2])), "voice.mp3"))
    kw = {}
    if len(sys.argv) > 4:
        kw["frames"] = (int(sys.argv[3]), int(sys.argv[4]))
    safezone.fit(SHOTS, sys.modules[__name__])
    render(SHOTS, TOTAL, sys.argv[1], xfade=0.0, grain=2, fade_out=0.0, fade_in=0.0, **kw)

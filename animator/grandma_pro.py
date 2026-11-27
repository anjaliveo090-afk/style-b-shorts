"""Story: "What If Your GRANDMA Became a Roblox Pro?" (script written from script_guide.md).

Voice: output/grandma_pro/voice.mp3 (46.5 s, the user's voice tool) + subs.srt; word times from
analysis/align_words.py, SRT line starts used where the aligner slipped ("Day 2", "to a 1v1").
Lip-sync on Grandma's and the Kid's lines only; the narrator moves no mouths. Ends with the
references' REWIND montage back to the first frame.

Run (from animator/):
  python3 grandma_pro.py ../output/grandma_pro/clips/animation.mp4 ../output/grandma_pro/cues.json"""
import math
import os
import sys

import engine
import sets as st
import style
from engine import clamp, ease, hexc, keyed, lerp, pop, render
from sets import label
from style import Block

TOTAL = 47.3
engine.LIPSYNC = True               # only characters drawn with talk=True move their mouths
engine.DRIFT = (0.035, 9, -6)
engine.ENERGY = 3.0
SFX_GAIN = 0.28                    # measured: 0.4 put the SFX median at +0.4 dB vs this voice
MUSIC = dict(dips=[(38.45, 40.4)])  # quieter under the whispered "But then..."
DIALOGUE = {"grandma": [(2.61, 4.89), (26.99, 29.39), (36.09, 38.23), (44.65, 46.43)],
            "kid": [(25.51, 26.69), (34.47, 35.41)]}

GRANDMA = style.GRANDMA
GRANDMA_G = Block("#b48cff", pants="#5a4fb0", skin="#e8c3a8", hair="greybun", hair_col="#d8d8e4",
                  outfit="cardigan", lashes=True, glasses=True, shoes="dark", headset="rgb")
KID = style.KID
KID_GAME = style.KID_GAME
NOOB = style.NOOB
NOOB_SWEATER = [Block(c, pants="#9bbc36", skin="#e9c22c", hair=None, outfit="hoodie", sleeves="long",
                      emblem="heart", emblem_col="#ffffff", shoes=None)
                for c in ("#e8323a", "#2fbf8f", "#ff5fa2", "#4f8bff", "#ffb02e")]
CROWD = [style.crowd_member(i) for i in range(10)]
GRANDMA_YOUNG = Block("#ff8a3d", pants="#2b45a6", skin="#e8c3a8", hair="long", hair_col="#6b3a1f", lashes=True,
                      shoes="white")

U1 = Block.HW * 64
FACE_S = 4.2
FACE_KEEP = [(165, 300, 555, 760)]


def talking(who, T):
    return any(a <= T <= b for a, b in DIALOGUE[who])


def closeup(ctx, ch, expr, T, x=360, look=0.0, arms=("down", "down"), s=FACE_S, talk=False):
    ch.draw(ctx, x, 560 + 2.5 * U1 * s, s, expr, T, arms=arms, look=look, talk=talk)


def living_room(ctx, T, night=False):
    st.day_room(ctx, T) if not night else st.night_bedroom(ctx, T, door_open=0.0)


def game_bg(ctx, T):
    st.game_sky(ctx)
    st.block_clouds(ctx, T)
    st.baseplate(ctx, 760)


# ================================================================ hook
def s_hook(ctx, t, d, T0=0.0, frozen=False):
    T = T0 + (0.0 if frozen else t)
    st.burst(ctx, T, "#e0c0ff", "#7a3fd8", cy=560, spin=0.4)
    closeup(ctx, GRANDMA_G, keyed(T, [(0, "crazy"), (0.5, "grin")]), T, arms=("up", "up"))
    label(ctx, "GRANDMA", 360, 290, 80, fg=st.PINK, scale=pop(T - 0.5) if T >= 0.5 else 0.0)


def s_pro(ctx, t, d):
    T = 1.2 + t
    st.night_wall(ctx, 2000)
    for i, x in enumerate((110, 610)):   # trophies on shelves behind her
        st.block(ctx, x - 90, 520, 180, 20, 4, hexc("#8a5a3a"), 4, gloss=False)
        st.trophy(ctx, x, 520, 0.35, T)
    st.glow(ctx, 360, 700, 420, (0.6, 0.85, 1), 0.3)
    GRANDMA_G.draw(ctx, 360, 1100, 1.35, "smug", T, arms=("hold", "hold"))
    st.block(ctx, -100, 930, 920, 50, 8, hexc("#b9b4d8"), 5)
    st.block(ctx, -100, 980, 920, 700, 0, hexc("#7a6aa8"), 5, gloss=False)
    st.laptop(ctx, 360, 935, 0.5, T, back=True)
    label(ctx, "PRO", 360, 300, 90, bg=st.GREEN, scale=pop(T - 1.7))


def s_turnon(ctx, t, d):
    T = 2.55 + t
    living_room(ctx, T)
    GRANDMA.draw(ctx, 330, 1100, 1.45, "worried", T, arms=("hold", "hold"),
                 talk=talking("grandma", T))
    st.tablet(ctx, 330, 850, 0.55, T, None, tilt=math.pi + 0.15 * math.sin(T * 3))   # held upside down
    for i, (x, y) in enumerate(((520, 520), (590, 430), (470, 410))):
        if T > 3.0 + i * 0.3:
            st.bold_text(ctx, "?", x, y + math.sin(T * 4 + i) * 8, 70, st.YELLOW, scale=pop(T - 3.0 - i * 0.3))


def s_tablet_cu(ctx, t, d):
    T = 3.65 + t
    living_room(ctx, T)
    st.tablet(ctx, 360, 640, 1.3, T, lambda c, x, y, w, h, TT: st.screen_obby(c, x, y, w, h, TT, None, "STAGE 1"),
              tilt=math.pi)
    k = ease((T - 3.7) / 0.3)   # grandma's finger pokes the wrong side
    st.block(ctx, lerp(760, 520, k), lerp(1200, 900, k), 70, 240, 30, GRANDMA.skin, 5)
    st.tap_ripple(ctx, 540, 900, (T - 4.0) / 0.5)
    label(ctx, "UPSIDE DOWN", 360, 300, 56, bg=st.RED, scale=pop(T - 4.26))


# ================================================================ days 1-4
def s_day1(ctx, t, d):
    T = 5.05 + t
    game_bg(ctx, T)
    GRANDMA_G.draw(ctx, 330, 1000, 1.2, "happy", T, arms=("hold", "hold"), pose="sit")
    st.yarn_ball(ctx, 470, 960, 45, T=T)
    st.day_text(ctx, "DAY 1", 360, 380, T - 5.13)


def s_sweaters(ctx, t, d):
    T = 6.6 + t
    game_bg(ctx, T)
    n = 1 + int(clamp((T - 6.65) / 0.5) * 4)
    for i in range(5):
        x = 80 + i * 140
        if i < n:
            NOOB_SWEATER[i].draw(ctx, x, 980 + (i % 2) * 40, 0.75, "happy", T + i, arms=("up", "down"))
            if i == n - 1:
                st.poof(ctx, x, 830, 60, (T - 6.65 - i * 0.12) / 0.4)
        else:
            NOOB.draw(ctx, x, 980 + (i % 2) * 40, 0.75, "neutral", T + i)
    st.hearts(ctx, T, 7.14, 360, 700, n=6)
    label(ctx, "SWEATERS FOR NOOBS", 360, 300, 46, bg="#e8323a", scale=pop(T - 7.14))


def s_day2(ctx, t, d):
    T = 8.15 + t
    tops = st.obby(ctx, T, y_top=920)
    GRANDMA_G.draw(ctx, tops[0][0], tops[0][1], 0.95, "determined", T, arms=("down", "down"))
    st.walking_stick(ctx, tops[0][0] + 85, tops[0][1] - 200, 0.6)
    st.day_text(ctx, "DAY 2", 360, 380, T - 8.23)


def s_hardest(ctx, t, d):
    T = 9.84 + t
    tops = st.obby(ctx, T, y_top=920, start=97)
    GRANDMA_G.draw(ctx, tops[0][0], tops[0][1], 0.95, "smug", T, arms=("down", "hip"))
    st.walking_stick(ctx, tops[0][0] + 85, tops[0][1] - 200, 0.6)
    st.stage_pill(ctx, 360, 330, "HARDEST OBBY", s=pop(T - 10.41))


def s_pogo(ctx, t, d):
    T = 11.45 + t
    st.game_sky(ctx)
    st.block_clouds(ctx, T)
    st.lava(ctx, 1150, T)
    for i in range(5):
        st.platform(ctx, -40 + i * 170, 980 - i * 40, 110, ("#2cd5fc", "#fa3a9f", "#f7e04a", "#a694e1", "#4fd16a")[i])
    p = clamp((T - 11.5) / 1.6)
    x = lerp(20, 650, p)
    hop = abs(math.sin(p * math.pi * 4)) * 260
    y = lerp(980, 820, p) - hop
    st.walking_stick(ctx, x, y - 10, 0.9, ang=math.pi)               # the stick points down: a pogo
    GRANDMA_G.draw(ctx, x, y - 250, 1.15, "laugh", T, arms=("hold", "hold"), pose="jump")
    if hop < 30:
        st.dust(ctx, x, y + 200, 0.3)
    label(ctx, "POGO STICK!", 360, 330, 64, fg=st.YELLOW, scale=pop(T - 12.44))


def s_day3(ctx, t, d):
    T = 13.45 + t
    game_bg(ctx, T)
    st.lemonade_stand(ctx, 380, 1020, 1.05, T, sign="COOKIES")
    GRANDMA_G.draw(ctx, 380, 880, 0.75, "happy", T, arms=("wave", "down"))
    st.day_text(ctx, "DAY 3", 360, 340, T - 13.49)


def s_shop(ctx, t, d):
    T = 14.55 + t
    st.burst(ctx, T, "#ffe0b0", "#c98a3e", cy=560)
    GRANDMA_G.draw(ctx, 360, 1080, 1.2, "grin", T, arms=("show", "down"))
    for i in range(6):   # cookies popping out of the oven tray
        k = T - 14.9 - i * 0.12
        if k > 0:
            cx = 140 + (i % 3) * 220
            cy = 450 + (i // 3) * 170
            st.cookie(ctx, cx, cy, 60 * pop(k), rot=i)
    label(ctx, "COOKIE SHOP", 360, 300, 60, bg="#c98a3e", scale=pop(T - 15.0))


def s_line(ctx, t, d):
    T = 15.75 + t
    game_bg(ctx, T)
    for row in range(4):   # a long queue fading into the distance
        for i in range(9):
            s = 0.35 + row * 0.12
            x = (i * 90 + row * 45) % 760 - 20
            CROWD[(i + row) % 10].draw(ctx, x, 800 + row * 90, s, "stars", T + i, arms=("up", "down"))
    v = lerp(1000, 1000000, ease((T - 15.78) / 0.4))
    st.number_counter(ctx, 360, 470, 0.85, v, T, prefix="")
    label(ctx, "PLAYERS", 360, 600, 50, bg=st.BLUE, scale=pop(T - 16.44))


def s_day4(ctx, t, d):
    T = 17.4 + t
    game_bg(ctx, T)
    GRANDMA_G.draw(ctx, 360, 1000, 1.2, "smug", T, arms=("hip", "hip"))
    st.day_text(ctx, "DAY 4", 360, 380, T - 17.47)


def s_board(ctx, t, d):
    T = 18.55 + t
    st.burst(ctx, T, "#7fb8ff", "#2f4bb0", cy=560)
    rows = [("GRANDMA", "999,999", lambda c, x, y, TT: st.face_icon(c, x, y, 26, "#e8c3a8", "#d8d8e4", True)),
            ("ProGamer", "12,450", None), ("ObbyKing", "9,871", None), ("You", "7,302",
                                                                       lambda c, x, y, TT: st.face_icon(c, x, y, 26))]
    st.leaderboard(ctx, 360, 290, 1.0, rows, T, k_rows=[T - 18.6, T - 18.75, T - 18.85, T - 18.95])
    st.sparkles(ctx, T, 360, 450, spread=260, n=10, seed=7, c=st.YELLOW)


def s_subs(ctx, t, d):
    T = 20.4 + t
    game_bg(ctx, T)
    for i, x in enumerate((90, 230, 490, 630)):
        CROWD[i].draw(ctx, x, 1060, 0.85, "stars" if T > 20.86 else "happy", T, arms=("up", "up"))
    st.subscribe_button(ctx, 360, 560, 1.05, pressed=clamp((T - 20.86) * 4))
    st.cursor(ctx, 420, 600, 1.6, click=1.0 if 20.82 < T < 20.98 else 0.0)
    if T > 21.64:
        st.cookie(ctx, 360, 780, 80 * pop(T - 21.64), rot=T)
    label(ctx, "FREE COOKIE", 360, 300, 58, bg="#c98a3e", scale=pop(T - 21.64))


def s_cookie_cu(ctx, t, d):
    T = 21.6 + t
    st.burst(ctx, T, "#ffe0b0", "#c98a3e", cy=640, spin=0.5)
    st.cookie(ctx, 360, 660, 210 * pop(T - 21.64), rot=T * 0.6)
    st.sparkles(ctx, T, 360, 660, spread=260, n=10, seed=5, c=st.YELLOW)
    label(ctx, "FREE!", 360, 300, 90, fg=st.GREEN, scale=pop(T - 21.64))


# ================================================================ day 5: the 1v1
def s_day5(ctx, t, d):
    T = 22.95 + t
    st.arena(ctx, T)
    GRANDMA_G.draw(ctx, 360, 1060, 1.1, "cold", T, arms=("down", "down"))
    st.walking_stick(ctx, 450, 820, 0.7)
    st.day_text(ctx, "DAY 5", 360, 380, T - 23.01)


def s_vs(ctx, t, d):
    T = 23.95 + t
    st.arena(ctx, T)
    KID_GAME.draw(ctx, 170, 1060, 1.0, "determined", T, arms=("punch", "down"))
    GRANDMA_G.draw(ctx, 550, 1060, 1.0, "smirk", T, arms=("down", "down"), look=-0.6)
    st.walking_stick(ctx, 640, 830, 0.6)
    st.vs_banner(ctx, 360, 430, T - 24.3)


def s_ready(ctx, t, d):
    T = 25.45 + t
    st.arena(ctx, T)
    closeup(ctx, KID_GAME, "smug", T, arms=("down", "point"), talk=talking("kid", T))


def s_sweetie(ctx, t, d):
    T = 26.95 + t
    st.burst(ctx, T, "#e0c0ff", "#7a3fd8", cy=560)
    closeup(ctx, GRANDMA_G, keyed(T, [(0, "smirk"), (28.13, "smug")]), T, arms=("down", "down"),
            talk=talking("grandma", T))
    label(ctx, "SINCE 1975", 360, 240, 58, bg=st.UI_DARK, fg=st.YELLOW, scale=pop(T - 28.53))


def s_retro(ctx, t, d):
    T = 28.45 + t
    st.burst(ctx, T, "#e9d6b0", "#b08a5a", cy=640)
    st.monitor(ctx, 360, 760, 0.75, T, lambda c, x, y, w, h, TT: st.screen_obby(c, x, y, w, h, TT, None, "LEVEL 1"))
    GRANDMA_YOUNG.draw(ctx, 360, 1240, 1.0, "laugh", T, arms=("hold", "hold"))
    st.tint(ctx, (0.6, 0.45, 0.25), 0.25)   # an old photo
    label(ctx, "1975", 360, 300, 90, bg="#8a5a3a", scale=pop(T - 28.53))


def s_swing(ctx, t, d):
    T = 29.65 + t
    st.arena(ctx, T)
    sw = ease((T - 29.75) / 0.2)
    GRANDMA_G.draw(ctx, 520, 1060, 1.05, "angry", T, arms=("down", "up"))
    st.walking_stick(ctx, 600, 700, 0.75, ang=lerp(-2.2, 0.9, sw))
    hit = T > 29.95
    kx = 230 - (T - 29.95) * 700 if hit else 230
    ky = 1060 - (math.sin(min(1, (T - 29.95) * 2) * math.pi) * 400 if hit else 0)
    KID_GAME.draw(ctx, kx, ky, 1.0, "shock" if hit else "smug", T, arms=("up", "up"), pose="jump" if hit else "stand")
    if hit:
        st.impact_star(ctx, 300, 820, 130, T - 29.95, "BONK!")


def s_noob(ctx, t, d):
    T = 31.4 + t
    st.arena(ctx, T)
    if T < 32.3:
        KID_GAME.draw(ctx, 360, 1060, 1.2, "shock", T, arms=("up", "up"))
    else:
        NOOB.draw(ctx, 360, 1060, 1.2, "cry", T, arms=("down", "down"))
    st.poof(ctx, 360, 830, 160, (T - 32.25) / 0.5)
    label(ctx, "NOOB", 360, 330, 90, fg=st.YELLOW, scale=pop(T - 32.42))


def s_zero(ctx, t, d):
    T = 32.85 + t
    st.night_wall(ctx, 2000)
    v = lerp(250000, 0, ease((T - 33.06) / 0.6))
    st.number_counter(ctx, 360, 520, 1.0, v, T, col="#ff4f5a" if T > 33.7 else "#ffd84a")
    NOOB.draw(ctx, 360, 1080, 1.2, "cry", T, arms=("up", "up"))
    if T > 33.81:
        st.shockwave(ctx, 360, 520, (T - 33.81) / 0.5, col=(1, 0.3, 0.3))


def s_no(ctx, t, d):
    T = 34.45 + t
    st.burst(ctx, T, "#ff8a7a", "#a8202e", cy=560)
    closeup(ctx, KID, "cry", T, arms=("up", "up"), talk=talking("kid", T))


def s_gg(ctx, t, d):
    T = 35.75 + t
    living_room(ctx, T)
    closeup(ctx, GRANDMA, keyed(T, [(0, "wink"), (36.58, "happy")]), T, arms=("down", "show"),
            talk=talking("grandma", T))
    st.hearts(ctx, T, 36.3, 360, 420, n=5)
    label(ctx, "GG", 560, 300, 80, bg=st.PINK, scale=pop(T - 36.3))


def s_veggies(ctx, t, d):
    T = 37.1 + t
    st.kitchen(ctx, T, night=False)
    st.block(ctx, -100, 960, 920, 40, 6, hexc("#e9e4f5"), 4)
    KID.draw(ctx, 360, 930, 1.35, "sad", T, arms=("down", "down"))
    st.block(ctx, -100, 1000, 920, 400, 0, hexc("#c99a6a"), 5, gloss=False)
    st.veggie_plate(ctx, 360, 990, 1.1 * pop(T - 37.43) if T > 37.43 else 0.01)
    label(ctx, "VEGETABLES", 360, 300, 60, bg=st.GREEN, scale=pop(T - 37.76))


# ================================================================ twist + ending
def s_butthen(ctx, t, d):
    T = 38.45 + t
    st.night_wall(ctx, 2000)
    closeup(ctx, KID, "sad", T, look=0.6)
    st.tint(ctx, (0.03, 0.03, 0.15), 0.35)
    st.spotlight(ctx, 360, 560, 320, a=0.6)


def s_ring(ctx, t, d):
    T = 39.15 + t
    living_room(ctx, T, night=True)
    st.tint(ctx, (0.03, 0.03, 0.15), 0.45)

    def screen(c, x, y, w, h, TT):
        c.rectangle(x, y, w, h)
        c.set_source_rgb(*hexc("#1f2236"))
        c.fill()
        st.bold_text(c, "ROBLOX HQ", x + w / 2, y + h * 0.35, w * 0.13, (1, 1, 1), stroke=0.1)
        st.bold_text(c, "calling...", x + w / 2, y + h * 0.5, w * 0.09, st.GREEN, stroke=0.0, shadow=False)
    ring = 1.0 if T > 39.2 else 0.0
    st.phone(ctx, 360 + math.sin(T * 60) * 8 * ring, 680, 1.1, T, screen, tilt=math.sin(T * 40) * 0.05 * ring)
    st.glow(ctx, 360, 680, 300, (0.4, 1, 0.6), 0.3 * ring)
    label(ctx, "RING RING!", 360, 300, 60, fg=st.GREEN, scale=pop(T - 40.16))


def s_hire(ctx, t, d):
    T = 40.45 + t
    st.office(ctx, T)
    GRANDMA.draw(ctx, 360, 1150, 1.4, "grin", T, arms=("show", "down"))
    st.staff_badge(ctx, 360, 1150 - 1.55 * U1 * 1.4, 1.0)
    st.stamp(ctx, 360, 380, "HIRED!", T - 40.93, col="#3ce454", size=100)
    st.confetti(ctx, T, 40.93, n=30)


def s_comment(ctx, t, d):
    T = 41.95 + t
    living_room(ctx, T)
    typed = "GRANDMA"[:int(clamp((T - 42.26) / 0.5) * 7)]
    st.comments_sheet(ctx, T, [("@cookie_fan", "my grandma is a pro too", "#ff5fa2"),
                               ("@obby_king", "the pogo stick lol", "#4f8bff")], typed=typed, y0=560, likes_t=43.4)
    label(ctx, "COMMENT \"GRANDMA\"", 360, 330, 48, bg=st.RED, scale=pop(T - 41.99))


def s_destroy(ctx, t, d):
    T = 43.05 + t
    st.arena(ctx, T)
    GRANDMA_G.draw(ctx, 470, 1060, 1.2, "smug", T, arms=("up", "hip"))
    st.walking_stick(ctx, 620, 560, 0.75, ang=0.3)
    NOOB.draw(ctx, 170, 1060, 0.8, "cry", T, arms=("down", "down"))
    label(ctx, "DESTROYED", 360, 300, 66, fg=st.RED, scale=pop(T - 43.46))


def s_off(ctx, t, d):
    T = 44.55 + t
    living_room(ctx, T)
    GRANDMA.draw(ctx, 330, 1100, 1.45, "worried", T, arms=("hold", "hold"), talk=talking("grandma", T))
    st.tablet(ctx, 330, 850, 0.55, T, None, tilt=math.pi + 0.15 * math.sin(T * 3))
    for i, (x, y) in enumerate(((520, 520), (590, 430), (470, 410))):
        if T > 45.2 + i * 0.25:
            st.bold_text(ctx, "?", x, y + math.sin(T * 4 + i) * 8, 70, st.YELLOW, scale=pop(T - 45.2 - i * 0.25))


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
shot(0.00, s_hook, [(0.0, 1.25, (360, 640)), (0.12, 1.0, (360, 700), 0.12), (0.5, 1.1, (360, 660), 0.12)],
     shake=(0.5, 10), **CU)
shot(1.2, s_pro, punch(1.2, 1.0, C, 1.7, 1.1, (360, 700), 0.14), keep=[(220, 240, 500, 360)])
shot(2.55, s_turnon, punch(2.55, 1.0, (360, 760), 3.4, 1.08, (340, 740), 0.15))
shot(3.65, s_tablet_cu, punch(3.65, 1.0, C, 4.26, 1.08, (380, 700), 0.14), keep=[(130, 470, 590, 800)])
shot(5.05, s_day1, punch(5.05, 1.0, C, 5.73, 1.08, (380, 760), 0.15), keep=CARD)
shot(6.6, s_sweaters, punch(6.6, 1.0, (360, 760), 7.14, 1.06, (360, 760), 0.15))
shot(8.15, s_day2, punch(8.15, 1.0, C, 8.45, 1.06, (360, 720), 0.15), keep=CARD)
shot(9.84, s_hardest, punch(9.84, 1.0, C, 10.82, 1.1, (300, 760), 0.14))
shot(11.45, s_pogo, [(11.45, 1.0, (360, 760)), (12.44, 1.05, (420, 720), 0.4)])
shot(13.45, s_day3, punch(13.45, 1.0, C, 14.13, 1.06, (380, 760), 0.15), keep=CARD)
shot(14.55, s_shop, punch(14.55, 1.0, C, 15.0, 1.08, (360, 680), 0.14))
shot(15.75, s_line, punch(15.75, 1.0, C, 16.15, 1.1, (360, 600), 0.12), shake=(0.4, 10),
     keep=[(60, 375, 660, 640)])
shot(17.4, s_day4, punch(17.4, 1.0, C, 17.62, 1.06, (360, 720), 0.15), keep=CARD)
shot(18.55, s_board, punch(18.55, 1.0, C, 18.91, 1.06, (360, 640), 0.14), keep=[(60, 280, 660, 790)])
shot(20.4, s_subs, punch(20.4, 1.0, C, 20.86, 1.08, (360, 640), 0.12), keep=[(140, 500, 580, 620)])
shot(21.6, s_cookie_cu, punch(21.6, 1.0, C, 21.64, 1.08, (360, 660), 0.1), keep=[(150, 450, 570, 870)])
shot(22.95, s_day5, punch(22.95, 1.0, C, 23.14, 1.06, (360, 720), 0.15), keep=CARD, shake=(0.06, 10))
shot(23.95, s_vs, punch(23.95, 1.0, C, 24.36, 1.08, (360, 700), 0.12), shake=(0.35, 12), keep=[(40, 350, 680, 510)])
shot(25.45, s_ready, punch(25.45, 1.0, C, 26.38, 1.08, (360, 660), 0.12), **CU)
shot(26.95, s_sweetie, punch(26.95, 1.0, C, 27.85, 1.1, (360, 660), 0.14), **CU)
shot(28.45, s_retro, punch(28.45, 1.0, C, 28.83, 1.08, (360, 700), 0.14), keep=[(220, 240, 500, 360)])
shot(29.65, s_swing, punch(29.65, 1.0, (360, 760), 29.95, 1.08, (330, 760), 0.1), shake=(0.3, 18))
shot(31.4, s_noob, punch(31.4, 1.0, C, 32.42, 1.1, (360, 700), 0.12), shake=(0.85, 10))
shot(32.85, s_zero, punch(32.85, 1.0, C, 33.81, 1.1, (360, 640), 0.12), shake=(0.96, 14), keep=[(60, 425, 660, 615)])
shot(34.45, s_no, punch(34.45, 1.0, C, 35.16, 1.1, (360, 660), 0.1), shake=(0.71, 12), **CU)
shot(35.75, s_gg, punch(35.75, 1.0, C, 36.3, 1.08, (360, 660), 0.12), **CU)
shot(37.1, s_veggies, punch(37.1, 1.0, (360, 760), 37.76, 1.08, (360, 800), 0.14), keep=[(170, 820, 550, 1000)])
shot(38.45, s_butthen, punch(38.45, 1.0, C, 38.62, 1.06, (360, 660), 0.14), **CU)
shot(39.15, s_ring, punch(39.15, 1.0, C, 40.16, 1.1, (360, 680), 0.4), shake=(0.05, 6), keep=[(240, 480, 480, 880)])
shot(40.45, s_hire, punch(40.45, 1.0, (360, 760), 40.93, 1.06, (360, 740), 0.12), shake=(0.48, 12),
     keep=[(150, 300, 570, 460)])
shot(41.95, s_comment, punch(41.95, 1.0, C, 42.26, 1.04, (360, 720), 0.2))
shot(43.05, s_destroy, punch(43.05, 1.0, (360, 760), 43.46, 1.08, (360, 740), 0.12), shake=(0.41, 10))
shot(44.55, s_off, punch(44.55, 1.0, (360, 760), 45.17, 1.08, (340, 740), 0.15))
SHOTS = S
# REWIND montage after the last word (script_guide.md section 6), landing on the first frame
_rw_draw, _rw_ov = st.rewind_shot(SHOTS, [40.8, 33.4, 24.6, 16.2, 6.9, 0.0])
shot(46.45, _rw_draw, [(46.45, 1.0, (360, 640))], overlay=_rw_ov, blur=False, closeup=True, keep=[])
for k, s in enumerate(SHOTS):
    s["end"] = SHOTS[k + 1]["start"] if k + 1 < len(SHOTS) else TOTAL

# ---------------------------------------------------------------- SFX (time, file, volume before SFX_GAIN)
SFX = [
    (0.03, "boom.wav", 1.6), (0.5, "pop.wav", 0.8), (1.2, "swish.wav", 0.6), (1.7, "ding.wav", 0.9),
    (2.61, "pop.wav", 0.6), (3.0, "pop.wav", 0.5), (3.6, "pop.wav", 0.5), (4.56, "boing.wav", 0.5),
    (5.13, "hit.wav", 1.3), (5.73, "tick.wav", 0.6), (6.0, "tick.wav", 0.6), (6.65, "pop.wav", 0.7),
    (6.9, "pop.wav", 0.6), (7.14, "ding.wav", 0.8), (7.6, "pop.wav", 0.5), (8.23, "hit.wav", 1.3),
    (9.2, "tick.wav", 0.5), (10.41, "pop.wav", 0.7), (10.82, "hit.wav", 1.0), (11.6, "boing.wav", 0.7),
    (12.0, "boing.wav", 0.6), (12.44, "boing.wav", 0.8), (12.87, "pop.wav", 0.6), (13.49, "hit.wav", 1.3),
    (14.13, "pop.wav", 0.6), (14.9, "pop.wav", 0.5), (15.0, "ding.wav", 0.8), (15.3, "pop.wav", 0.5),
    (15.8, "tick.wav", 0.6), (16.0, "tick.wav", 0.6), (16.15, "chaching.wav", 0.9), (16.44, "pop.wav", 0.6),
    (17.47, "hit.wav", 1.3), (18.32, "pop.wav", 0.6), (18.6, "ding.wav", 0.9), (18.91, "pop.wav", 0.6),
    (19.71, "sparkle.wav", 0.7), (20.45, "pop.wav", 0.6), (20.86, "click.wav", 0.9), (20.9, "pop.wav", 0.7),
    (21.64, "ding.wav", 0.8), (22.36, "pop.wav", 0.5), (23.01, "hit.wav", 1.3), (23.99, "swish.wav", 0.6),
    (24.36, "boom.wav", 1.4), (25.51, "pop.wav", 0.6), (26.38, "pop.wav", 0.5), (27.21, "pop.wav", 0.6),
    (28.13, "hit.wav", 1.0), (28.53, "pop.wav", 0.7), (29.75, "swish.wav", 0.8), (29.95, "boom.wav", 1.6),
    (30.3, "boing.wav", 0.6), (31.6, "tick.wav", 0.5), (32.25, "boom.wav", 1.2), (32.42, "pop.wav", 0.7),
    (33.1, "tick.wav", 0.6), (33.3, "tick.wav", 0.6), (33.81, "hit.wav", 1.3), (34.47, "hit.wav", 1.0),
    (35.16, "pop.wav", 0.6), (36.09, "pop.wav", 0.6), (36.3, "sparkle.wav", 0.7), (37.43, "pop.wav", 0.8),
    (37.76, "boing.wav", 0.5), (38.62, "tick.wav", 0.5), (39.2, "bell.wav", 0.5), (39.6, "bell.wav", 0.5),
    (40.16, "ding.wav", 0.8), (40.93, "boom.wav", 1.4), (41.0, "chaching.wav", 0.8), (41.99, "pop.wav", 0.8),
    (42.3, "type_key.wav", 0.6), (42.5, "type_key.wav", 0.6), (42.7, "type_key.wav", 0.6), (43.4, "ding.wav", 0.7),
    (44.07, "pop.wav", 0.6), (44.65, "pop.wav", 0.5), (45.2, "pop.wav", 0.5), (45.7, "pop.wav", 0.5),
    (46.45, "whip.wav", 0.9),
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

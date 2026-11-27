"""Story: "This Noob Is the REASON Roblox Has a Leave Button" (Toby).

Voice + SRT: output/leave_noob/voice.mp3 (57.2 s, the user's voiceflow voice, no gaps over 0.2 s).
Plan: output/leave_noob/plan.md (52 shots, a new visual every ~1.1 s).
Toby's acted lines (lip-sync, the user's rule): "You're welcome!" 10.6-11.3, "pepperoni or cheese?" 18.2-19.4,
"Found you! Happy birthday!" 29.3-30.7, "did somebody order pizza?" 53.3-54.6.
Same build as chat_filter_v2.py: engine.profile("set3"), SAFE_BODY whole characters, closeup() reaction shots,
the Roblox in-game interface (top bar + Players + a chat that tells the story) on the in-game shots.

Scenes use ABSOLUTE time T; a shot wraps a scene with at(scene, start).
Run (from animator/):
  python3 leave_noob.py ../output/leave_noob/clips/animation.mp4 ../output/leave_noob/cues.json"""
import math
import os
import sys

import engine
import sets as st
import style
from engine import PI, clamp, ease, hexc, keyed, lerp, pop, render
from sets import label
from style import Block

engine.profile("set3")
engine.ENERGY = 3.0
SAFE_BODY = True        # safezone.fit boxes characters by their real pixels: whole characters stay in the zone
engine.LIPSYNC = True
TOTAL = 58.2
SFX_GAIN = 0.24
MUSIC = dict(bpm=128, perc=0.6, dips=[(44.2, 45.9)])     # quieter while Toby is alone
DIALOGUE = {"toby": [(10.58, 11.32), (18.18, 19.42), (29.33, 30.72), (53.32, 54.6)]}

TOBY = Block("#22b8c8", pants="#9bbc36", skin="#e9c22c", hair=None, sleeves="skin", shoes=None)
MOD = Block("#2f6bd8", pants="#2b2f45", skin="#f0c9a8", hair="smooth", hair_col="#3a2a2a", outfit="hoodie",
            shoes="dark", glasses=True)
ADMIN = Block("#e8323a", pants="#2b2f45", skin="#f0c9a8", hair="spiky", hair_col="#2a1a14", outfit="hoodie",
              shoes="dark", crown=True)
DEV = Block("#3b3f5a", pants="#2b2f45", skin="#f0c9a8", hair="spiky", hair_col="#2a1a14", outfit="hoodie",
            glasses=True, headset="#4f8bff", shoes="dark")
P = [style.crowd_member(i) for i in range(14)]
COZY, BOB, RACER = P[4], P[5], P[2]
NAMES = st.ROBLOX_NAMES

U1 = Block.HW * 64
FACE_S = 4.2


def talking(who, T):
    return any(a <= T <= b for a, b in DIALOGUE[who])


def snap_at(T, t0):
    return (T - t0) if T >= t0 else None


def at(fn, T0):
    return lambda ctx, t, d: fn(ctx, T0 + t, d)


CU_FEET, CU_X, CU_S = 995, 320, 2.3     # close-up framing that keeps the whole character in the safe zone


def closeup(ctx, ch, expr, T, x=360, look=0.0, arms=("down", "down"), s=FACE_S, talk=False, bob=0.35, dy=0,
            snap=None, fit=True):
    """A reaction close-up (copied from chat_filter_v2.py): the character is drawn whole, feet at y 995, head near
    (320, 465). Returns (m, k): m(px, py) maps a point placed for the old full-frame close-up (head centre (x, 560),
    scale s) onto the new framing; k is the size factor, so face props follow the face."""
    if not fit:
        ch.draw(ctx, x, 560 + 2.5 * U1 * s + dy, s, expr, T, arms=arms, look=look, talk=talk, bob=bob, snap=snap)
        return (lambda px, py: (px, py)), 1.0
    s2 = min(CU_S + 0.05, s * CU_S / FACE_S)
    k = s2 / s
    nx = CU_X + (x - 360) * k
    ch.draw(ctx, nx, CU_FEET, s2, expr, T, arms=arms, look=look, talk=talk, bob=bob, snap=snap)
    hx, hy = nx, CU_FEET - 2.5 * U1 * s2
    return (lambda px, py: (hx + (px - x) * k, hy + (py - 560) * k)), k


def hat_on(ctx, hx, hy, s, tilt=-0.15):
    """Toby's party hat on a head centred at (hx, hy) drawn at character scale s."""
    ctx.save()
    ctx.translate(hx, hy - 0.5 * U1 * s)
    ctx.rotate(tilt)
    st.party_hat(ctx, 0, 0, 0.0042 * U1 * s, col="#ff5fb0")
    ctx.restore()


def toby(ctx, x, y, s, expr, T, tag=True, hat=True, **kw):
    TOBY.draw(ctx, x, y, s, expr, T, **kw)
    if hat:
        hat_on(ctx, x, y - 2.5 * U1 * s, s)
    if tag:
        st.name_pill(ctx, x, y - 3.75 * U1 * s, "Toby", size=max(20, 24 * s))


def toby_cu(ctx, expr, T, hat=True, **kw):
    """Toby's reaction close-up with his party hat; returns (m, k) like closeup()."""
    m, k = closeup(ctx, TOBY, expr, T, **kw)
    if hat:
        hat_on(ctx, *m(kw.get("x", 360), 560), FACE_S * k)
    return m, k


def world(ctx, T, y=1000):
    st.game_sky(ctx)
    st.block_clouds(ctx, T)
    st.baseplate(ctx, y)


def burst_ground(ctx, T, c1, c2, y=1000, spin=0.5):
    """A comic burst behind an emphasis moment, with the ground strip so characters still stand."""
    st.burst(ctx, T, c1, c2, cy=600, spin=spin)
    st.baseplate(ctx, y)


def race_track(ctx, T, y=1000):
    """A race track: sky, grandstand, grey asphalt with lane stripes and a checkered line."""
    st.game_sky(ctx)
    st.block(ctx, -100, 560, 920, 200, 0, hexc("#5a5f7a"), 4, gloss=False)          # grandstand
    for i in range(14):
        for j in range(3):
            ctx.new_sub_path()
            ctx.arc(-40 + i * 60 + (j % 2) * 30, 600 + j * 50, 14, 0, 2 * PI)
            ctx.set_source_rgb(*hexc(("#ff4f5a", "#ffd84a", "#6fc3ff", "#4fd16a")[(i + j) % 4]))
            ctx.fill()
    st.block(ctx, -100, 760, 920, 700, 0, hexc("#3a3d4a"), 4, gloss=False)          # asphalt
    off = (T * 900) % 160
    for i in range(8):
        st.block(ctx, -160 + i * 160 - off, 880, 90, 14, 4, (1, 1, 1), 0, gloss=False)
    for i in range(10):                                                            # checkered line
        for j in range(8):
            if (i + j) % 2 == 0:
                ctx.rectangle(560 + j * 16, 760 + i * 24, 16, 24)
    ctx.set_source_rgb(1, 1, 1)
    ctx.fill()


def typed(txt, T, t0, cps=22):
    return txt[:max(0, int((T - t0) * cps))]


def binoculars(ctx, x, y, s=1.0):
    for dx in (-48, 48):
        ctx.new_sub_path()
        ctx.arc(x + dx * s, y, 42 * s, 0, 2 * PI)
    style.shape_fill(ctx, hexc("#2b2f45"), 6, y - 42 * s, y + 42 * s)
    for dx in (-48, 48):
        ctx.new_sub_path()
        ctx.arc(x + dx * s, y, 26 * s, 0, 2 * PI)
    ctx.set_source_rgb(*hexc("#6fc3ff"))
    ctx.fill()
    style.block(ctx, x - 16 * s, y - 18 * s, 32 * s, 36 * s, 6 * s, hexc("#3a3f55"), 3, gloss=False)


def appear(ctx, T, t0, x, y, r=70):
    """A spawn poof at t0 (for 0.4 s)."""
    if 0 <= T - t0 < 0.4:
        st.poof(ctx, x, y, r, (T - t0) / 0.4)


# ================================================================ Roblox in-game HUD (screen-space overlay)
Y_, PK_, BL_, GR_, OR_, CY_, RD_ = "#ffd84a", "#ff5fb0", "#6fc3ff", "#4fd16a", "#ff8a3d", "#6fe6ff", "#ff4f5a"
CHAT_LOG = [   # (time posted, name or None for a grey system line, text, name colour)
    (2.9, None, "Toby joined the game", None), (4.9, "Toby", "WELCOME EVERYONE!!!", CY_), (5.9, "BloxKid", "hi?", PK_),
    (6.6, None, "Toby joined Lava Obby", None), (8.6, "Toby", "building a surprise :)", CY_),
    (10.7, "Toby", "YOU'RE WELCOME!", CY_), (11.7, "ObbyQueen", "where is the jump??", GR_),
    (12.5, "PizzaGamer99", "i fell", BL_), (12.95, None, "ObbyQueen left the game", None),
    (14.9, None, "Toby joined Speed Racers", None), (16.5, "Racer_X", "MOVE", OR_),
    (18.3, "Toby", "pepperoni or cheese?", CY_), (19.9, "Racer_X", "bro im in a race", OR_),
    (20.6, "SpeedyKid", "HONK HONK", Y_), (24.2, None, "Toby joined Hide and Seek", None),
    (25.6, "CozyCat", "shhh im hiding", PK_), (28.2, "Toby", "COZYCAT! BUILDER_BOB!", CY_),
    (29.4, "Toby", "FOUND YOU!", CY_), (30.1, "Toby", "HAPPY BIRTHDAY!", CY_),
    (30.6, "CozyCat", "its not my birthday", PK_), (31.4, "Builder_Bob", "MODS PLS", BL_),
    (33.6, None, "Toby was kicked", None), (34.6, None, "Toby joined the game", None),
    (35.4, "Toby", "MORE BALLOONS!", CY_), (41.7, None, "CozyCat left the game", None),
    (42.45, None, "Builder_Bob left the game", None), (42.9, None, "Racer_X left the game", None),
    (43.4, None, "BloxKid left the game", None), (44.6, "Toby", "hello?", CY_),
    (50.1, None, "Toby left the game", None), (50.5, None, "Toby joined the game", None),
    (51.5, None, "Toby left the game", None), (51.9, None, "Toby joined the game", None),
    (53.4, "Toby", "did somebody order pizza?", CY_), (55.2, "[DEV] Sam", "...", RD_),
]


def players_at(T):
    if T < 12.95:
        return 18
    if T < 14.9:
        return 17
    if T < 24.2:
        return 22
    if T < 41.6:
        return 26 if not (33.6 <= T < 34.6) else 25
    if T < 44.0:                                     # one by one the server empties
        return max(1, 26 - int((T - 41.6) * 11))
    if 50.1 <= T < 54.0:                             # Toby leaves and rejoins
        return 0 if int((T - 50.1) / 0.4) % 2 == 0 else 1
    return 1


def hud(ctx, T):
    st.roblox_topbar(ctx, T, players=players_at(T))
    st.roblox_chat(ctx, CHAT_LOG, T, w=420, size=23)


def hud_ov(T0):
    return lambda ctx, t, d: hud(ctx, T0 + t)


LBL_Y = 520              # labels on HUD shots sit under the HUD (screen y ~400 with the camera at y 760)


# ================================================================ hook (0 - 2.55 s)
def s_hook(ctx, T, d):
    st.burst(ctx, T, "#ffc4ec", "#c0307a", cy=560, spin=0.5)
    m, k = toby_cu(ctx, keyed(T, [(0, "crazy"), (0.34, "grin")]), T, arms=("wave", "down"), snap=snap_at(T, 0.34))
    st.balloons(ctx, *m(560, 860), 1.3 * k, T, n=5, seed=3)
    st.speech_bubble(ctx, 360, 250, "WELCOME!!!", 58, T + 0.4, tail=(0, 1))
    st.confetti(ctx, T, 0.0, n=26)
    label(ctx, "THIS NOOB", 360, 955, 74, fg=st.YELLOW)


def s_flee(ctx, T, d, t0=0.80):
    world(ctx, T, 1000)
    k = clamp((T - t0) / 0.6)
    for i in range(6):                       # players run away into the distance (shrinking, inside the zone)
        side = -1 if i < 3 else 1
        q = ease(k)
        x = lerp(360 + (i - 2.5) * 80, 360 + side * (130 + (i % 3) * 70), q)
        y = lerp(1000, 900, q)
        sc = lerp(0.8, 0.3, q)
        P[i].draw(ctx, x, y, sc, "scream", T, pose="run", walk_phase=T * 3.5, arms=("up", "up"))
    st.speed_lines(ctx, T, 360, 800, n=16, r0=200, r1=700, a=0.3)
    toby(ctx, 360, 1000, 0.95, "laugh", T, arms=("wave", "up"))
    st.sfx_word(ctx, 360, 520, "ZOOM!", T - t0 - 0.05, col=st.BLUE, size=60)


def s_menu(ctx, T, d):
    world(ctx, T, 1000)
    toby(ctx, 360, 1000, 0.9, "grin", T, arms=("wave", "down"), tag=False)
    st.esc_menu(ctx, T, k=T - 1.40, hi="leave" if T >= 1.89 else None, pressed=clamp((T - 2.13) / 0.08))
    kk = ease(clamp((T - 1.55) / 0.45))
    st.cursor(ctx, lerp(600, 380, kk), lerp(640, 925, kk), 1.6, click=1.0 if T >= 2.13 else 0.0)
    st.sfx_word(ctx, 520, 800, "CLICK!", T - 2.13, col=st.BLUE, size=50)


# ================================================================ Toby + his dream
def s_spawn(ctx, T, d):
    world(ctx, T, 1000)
    st.spawn_pad(ctx, 360, 1000, 1.4, beam=clamp(1 - (T - 2.6) / 0.6))
    kk = T - 2.62
    if kk >= 0:
        ctx.save()
        ctx.translate(360, 1000)
        ctx.scale(1, pop(kk))
        ctx.translate(-360, -1000)
        toby(ctx, 360, 1000, 1.15, keyed(T, [(0, "happy"), (3.16, "grin")]), T, arms=("wave", "down"),
             snap=snap_at(T, 3.16))
        ctx.restore()
    st.sparkles(ctx, T, 360, 760, spread=220, n=12, seed=6, c=(1, 1, 1))
    label(ctx, "TOBY", 360, LBL_Y, 84, fg=st.GREEN, scale=pop(T - 3.16) if T >= 3.16 else 0.0)


def s_dream(ctx, T, d):
    st.burst(ctx, T, "#fff6c4", "#8fd0ff", cy=560, spin=0.3)
    m, k = toby_cu(ctx, keyed(T, [(0, "happy"), (4.01, "stars")]), T, arms=("hold", "hold"), snap=snap_at(T, 4.01))
    st.thought_cloud(ctx, 500, 300, 300, 210, T - 3.55, tail=(-1, 1))
    if T >= 3.7:
        for i, (fx, col) in enumerate(((430, "#e9c22c"), (500, "#f0c9a8"), (570, "#8a5a3a"))):
            st.face_icon(ctx, fx, 300, 30 * min(1.0, pop(T - 3.7 - i * 0.08) + 0.01), col, "#4a2f22", expr="grin")
        st.hearts(ctx, T, 3.9, 500, 250, n=4, seed=5)
    label(ctx, "ONE DREAM", 360, 955, 70, fg=st.YELLOW, scale=pop(T - 4.01) if T >= 4.01 else 0.0)


def s_welcome(ctx, T, d):
    world(ctx, T, 1000)
    for i, x in enumerate((110, 215, 505, 610)):
        P[i + 6].draw(ctx, x, 1000, 0.8, keyed(T, [(0, "neutral"), (5.93, "happy")]), T,
                      arms=("up", "up") if T >= 5.93 else ("down", "down"), look=0.4 if x < 360 else -0.4,
                      snap=snap_at(T, 5.93))
    toby(ctx, 360, 1000, 1.0, "laugh", T, arms=("up", "up"))
    if T >= 5.93:
        st.hearts(ctx, T, 5.93, 360, 640, n=8, seed=3)
    label(ctx, "WELCOME!", 360, LBL_Y, 84, fg=st.PINK, scale=pop(T - 5.93) if T >= 5.93 else 0.0)


# ================================================================ the welcome sign over the first jump
def s_obby(ctx, T, d):
    tops = st.obby(ctx, T, y_lava=1060, y_top=930, x0=-80, dx=230, rise=-30, nums=False)
    (x0, y0), (x1, y1) = tops[0], tops[1]
    p = clamp((T - 6.85) / 0.55)
    x, y = lerp(x0 + 40, x1, p), lerp(y0, y1, p) - math.sin(PI * p) * 260
    toby(ctx, x, y, 0.9, "laugh" if p < 1 else "grin", T, arms=("up", "up"), pose="jump" if 0 < p < 1 else "stand",
         tag=p >= 1)
    st.sfx_word(ctx, x1 + 40, y1 - 320, "BOING!", T - 7.2, col=st.PINK, size=50)


def s_build(ctx, T, d):
    world(ctx, T, 1000)
    rise = ease(clamp((T - 7.75) / 0.3))
    st.welcome_sign(ctx, 420, 1000 + (1 - rise) * 600, 0.72, T, k_letters=T - 8.0)
    hit = abs(math.sin((T - 7.7) * 9))
    toby(ctx, 120, 1000, 0.85, "determined", T, arms=("punch" if hit > 0.5 else "up", "down"))
    st.sfx_word(ctx, 250, 520, "BONK!", T - 7.85, col=st.YELLOW, size=46, tilt=-0.15)
    st.sfx_word(ctx, 230, 640, "BONK!", T - 8.5, col=st.YELLOW, size=42, tilt=0.12, seed=5)
    if T >= 7.8:
        st.dust(ctx, 420, 1000, clamp((T - 7.8) / 0.5), n=6, spread=220)


def s_signwide(ctx, T, d):
    st.game_sky(ctx)
    st.block_clouds(ctx, T)
    st.lava(ctx, 1000, T)
    st.platform(ctx, -40, 800, 240, "#4fd16a", h=80)                 # the start
    for i, (x, col) in enumerate(((220, "#2cd5fc"), (360, "#fa3a9f"), (500, "#f7e04a"))):
        st.platform(ctx, x, 760 - i * 30, 110, col, h=60)
    st.welcome_sign(ctx, 390, 1000, 0.64, T)                         # right over the first jumps
    toby(ctx, 150, 800, 0.62, "happy", T, arms=("wave", "down"), tag=False)
    st.arrow(ctx, 640, 300, 470, 560, k=ease(clamp((T - 9.85) / 0.2)))
    st.sfx_word(ctx, 600, 260, "???", T - 9.9, col=st.RED, size=46)


def s_yourewelcome(ctx, T, d):
    st.burst(ctx, T, "#fff6c4", "#ffb84a", cy=560, spin=0.4)
    m, k = toby_cu(ctx, keyed(T, [(0, "grin"), (10.61, "stars")]), T, arms=("up", "wave"),
                   talk=talking("toby", T), snap=snap_at(T, 10.61))
    st.speech_bubble(ctx, 360, 240, "YOU'RE WELCOME!", 50, T - 10.61, tail=(0, 1))
    st.sparkles(ctx, T, *m(360, 560), spread=320, n=10, seed=2, c=st.YELLOW)


def s_bonk(ctx, T, d):
    world(ctx, T, 1000)
    st.welcome_sign(ctx, 445, 1000, 0.62, T)
    p = clamp((T - 11.5) / 0.43)
    hit = T >= 11.93
    x = lerp(60, 250, p) if not hit else 250 - 40 * ease(clamp((T - 11.93) / 0.25))
    P[3].draw(ctx, x, 1000, 0.9, "shock" if hit else "determined", T, pose="run" if not hit else "stand",
              walk_phase=T * 3.5, arms=("up", "up") if hit else ("down", "down"), lean=-0.3 if hit else 0.15,
              snap=snap_at(T, 11.93))
    st.sfx_word(ctx, 300, 540, "BONK!", T - 11.93, col=st.RED, size=58)
    if hit:
        for i in range(3):
            a = (T - 11.93) * 6 + i * 2.1
            style.sparkle(ctx, x + math.cos(a) * 60, 1000 - 3.0 * U1 * 0.9 + math.sin(a) * 18, 16)


def s_fall(ctx, T, d):
    st.game_sky(ctx)
    st.block_clouds(ctx, T)
    st.lava(ctx, 1000, T)
    st.platform(ctx, -40, 780, 220, "#4fd16a", h=80)
    for i, (t0, x0) in enumerate(((12.26, 150), (12.62, 110))):
        k = T - t0
        if k < 0:
            P[i + 9].draw(ctx, x0, 780, 0.8, "happy", T, arms=("up", "up"))
            continue
        x = x0 + 260 * min(k, 0.45) / 0.45
        y = 780 - 220 * math.sin(PI * min(1.0, k / 0.45) * 0.5) + max(0, k - 0.22) * 900
        if y < 990:
            P[i + 9].draw(ctx, x, y, 0.8 * (1 - 0.3 * clamp(k)), "scream", T, pose="jump", arms=("up", "up"))
        else:
            st.avatar_break(ctx, x, 990, 0.7, (k - 0.5) / 0.6)
            st.sfx_word(ctx, x, 820, "SPLASH!", k - 0.5, col=hexc("#ff8a3d"), size=46, seed=i + 3)
    label(ctx, "CAN'T SEE!", 360, LBL_Y, 78, bg=st.RED, scale=pop(T - 12.34) if T >= 12.34 else 0.0)


# ================================================================ the pizza stand in a racing game
def s_pizza(ctx, T, d):
    st.street(ctx, T, y_ground=1000)
    st.lemonade_stand(ctx, 460, 1000, 0.92, T, sign="FREE PIZZA", goods="pizza")
    toby(ctx, 160, 1000, 0.95, keyed(T, [(0, "happy"), (13.83, "laugh")]), T, arms=("down", "wave"),
         snap=snap_at(T, 13.83))
    label(ctx, "FREE!", 360, LBL_Y, 84, fg=st.YELLOW, scale=pop(T - 13.83) if T >= 13.83 else 0.0)


def racer(c, hx, hy):
    RACER.draw(c, hx, hy + 2.5 * U1 * 0.55, 0.55, "determined", 0.0, arms=("hold", "hold"), shadow=False)


def s_race(ctx, T, d):
    race_track(ctx, T)
    for i, (col, t0, y) in enumerate((("#e8323a", 14.8, 990), ("#2f6bd8", 15.15, 1000))):
        x = lerp(-300, 1100, clamp((T - t0) / 0.7))
        st.race_car(ctx, x, y, 0.62, T, col=col, num=str(i + 1))
    st.speed_lines(ctx, T, 360, 800, n=16, r0=200, r1=700, a=0.25)
    st.stage_pill(ctx, 360, LBL_Y, "RACING GAME", s=1.0, col="#e8323a")


def s_pass(ctx, T, d):
    st.street(ctx, T, y_ground=1000)
    st.lemonade_stand(ctx, 480, 1000, 0.6, T, sign="FREE PIZZA", goods="pizza")
    toby(ctx, 300, 1000, 0.62, "happy", T, arms=("wave", "down"), tag=False)
    x = lerp(-320, 1100, clamp((T - 15.95) / 0.5))
    st.race_car(ctx, x, 1010, 0.7, T, col="#4fd16a", num="7")
    if 16.0 < T < 16.6:
        st.speed_lines(ctx, T, 360, 820, n=14, r0=200, r1=700, a=0.35)
    st.sfx_word(ctx, 300, 600, "ZOOM!", T - 16.21, col=st.BLUE, size=60)


def s_stop(ctx, T, d):
    burst_ground(ctx, T, "#ffe27a", "#ff9418")
    p = clamp((T - 16.9) / 0.23)
    car_x = lerp(-200, 245, 1 - (1 - p) ** 3)
    toby(ctx, 530, 1000, 0.9, "grin", T, arms=("up", "down"), tag=False)
    st.race_car(ctx, car_x, 1010, 0.62, T, col="#4fd16a", num="7", driver=racer)
    if T >= 17.13:
        st.dust(ctx, car_x - 120, 1000, clamp((T - 17.13) / 0.5), n=6, spread=120)
    st.sfx_word(ctx, 300, 640, "SKRRT!", T - 17.13, col=st.YELLOW, size=56)


def s_choice(ctx, T, d):
    st.burst(ctx, T, "#ffe27a", "#ff7a1a", cy=560, spin=0.5)
    m, k = toby_cu(ctx, "happy", T, arms=("hold", "hold"), talk=talking("toby", T))
    st.pizza(ctx, *m(170, 820), 120 * k, kind="pepperoni", T=T)
    st.pizza(ctx, *m(550, 820), 120 * k, kind="cheese", T=T)
    st.speech_bubble(ctx, 210, 250, "PEPPERONI?", 44, T - 18.21, tail=(1, 1))
    st.speech_bubble(ctx, 520, 360, "CHEESE?", 44, T - 18.94, tail=(-1, 1))


def s_jam(ctx, T, d):
    st.street(ctx, T, y_ground=1000)
    cols = ("#e8323a", "#2f6bd8", "#ffd84a", "#9d5cff")
    for i, col in enumerate(cols):
        x = 150 + i * 140 + math.sin(T * 30 + i) * 2
        st.race_car(ctx, x, 1000 - (i % 2) * 6, 0.42, T, col=col, num=str(i + 2), speed=0.0)
    st.sfx_word(ctx, 160, 620, "HONK!", T - 19.85, col=st.RED, size=46, tilt=-0.15)
    st.sfx_word(ctx, 540, 680, "HONK!", T - 20.3, col=st.RED, size=46, tilt=0.12, seed=7)
    label(ctx, "TRAFFIC JAM", 360, LBL_Y, 72, bg=st.RED, scale=pop(T - 20.74) if T >= 20.74 else 0.0)


# ================================================================ the surprise party in hide and seek
def s_notdone(ctx, T, d):
    st.burst(ctx, T, "#e2c8ff", "#7a3fd8", cy=560, spin=0.5)
    m, k = toby_cu(ctx, keyed(T, [(0, "smirk"), (22.29, "smug")]), T, arms=("down", "down"), snap=snap_at(T, 22.29))
    if T >= 22.29:
        style.sparkle(ctx, *m(450, 470), 46 * k * pop(T - 22.29))
    label(ctx, "NOT DONE", 360, 300, 80, fg=(1, 1, 1), scale=pop(T - 22.09) if T >= 22.09 else 0.0)


def s_party(ctx, T, d):
    st.burst(ctx, T, "#ffc4ec", "#c0307a", cy=600, spin=0.6)
    st.cake(ctx, 470, 1000, 0.9, T, lit=True)
    toby(ctx, 200, 1000, 1.0, "laugh", T, arms=("up", "up"))
    st.balloons(ctx, 600, 760, 0.8, T, n=5, seed=8)
    st.confetti(ctx, T, 23.28, n=40)
    st.sfx_word(ctx, 360, 380, "SURPRISE!", T - 23.28, col=st.PINK, size=64)


def spots(ctx, T, balloon_t=(99, 99, 99), lift=0.0, exposed=False):
    """The three hiding spots (trash can, bush, box); balloons tied to each from balloon_t[i]; lift raises them."""
    xs = (130, 330, 500)
    if exposed:                                                       # hiders revealed under the lifted lids
        P[5].draw(ctx, 130, 1000, 0.62, "shock", T, arms=("up", "up"), shadow=False)
        COZY.draw(ctx, 500, 1000, 0.62, "shock", T, arms=("up", "up"), shadow=False)
    st.trash_can(ctx, 130, 1000 - lift * 0.9, 1.0, lid=0.0)
    st.bush(ctx, 330, 1000, 1.0, T, shake=0.6)
    st.cardboard_box(ctx, 500, 1000 - lift, 0.9, peek=0.0 if exposed else 1.0, T=T)
    for i, (x, tb) in enumerate(zip(xs, balloon_t)):
        if T >= tb:
            top = {0: 860, 1: 860, 2: 870}[i] - (lift if i != 1 else 0)
            ctx.save()
            ctx.translate(x, top)
            sc = min(1.0, pop(T - tb) + 0.05)
            ctx.scale(sc, sc)
            ctx.translate(-x, -top)
            st.balloons(ctx, x, top, 0.62, T, n=4, seed=i + 2)
            ctx.restore()
    if not exposed:
        for x, y in ((130, 812), (330, 880)):
            for ex in (-14, 14):
                ctx.new_sub_path()
                ctx.arc(x + ex, y, 7, 0, 2 * PI)
            ctx.set_source_rgb(1, 1, 1)
            ctx.fill()


def s_hideseek(ctx, T, d):
    world(ctx, T, 1000)
    spots(ctx, T)
    st.stage_pill(ctx, 360, LBL_Y, "HIDE AND SEEK", s=1.0, col="#7a3fd8")


def s_balloons(ctx, T, d):
    world(ctx, T, 1000)
    tb = (25.3, 25.72, 26.06)
    spots(ctx, T, balloon_t=tb)
    for x, t in zip((175, 330, 485), tb):
        st.sfx_word(ctx, x, 600, "POP!", T - t, col=st.GREEN, size=40)


def s_exposed(ctx, T, d):
    burst_ground(ctx, T, "#ffc0c0", "#e8323a")
    lift = 190 * ease(clamp((T - 26.4) / 0.5))
    spots(ctx, T, balloon_t=(0, 0, 0), lift=lift, exposed=lift > 30)
    label(ctx, "EXPOSED!", 360, LBL_Y, 80, bg=st.RED, scale=pop(T - 26.68) if T >= 26.68 else 0.0)


def s_shout(ctx, T, d):
    st.burst(ctx, T, "#ffe27a", "#ff7a1a", cy=560, spin=0.6)
    m, k = toby_cu(ctx, "laugh", T, arms=("hold", "down"), x=330)
    st.megaphone(ctx, *m(440, 640), 1.2 * k, ang=-0.25, T=T)
    for i, nm in enumerate(("COZYCAT!", "BOB!")):
        if T >= 28.16 + i * 0.18:
            st.speech_bubble(ctx, 470 - i * 40, 250 + i * 95, nm, 46 - i * 4, T - 28.16 - i * 0.18, tail=(-1, 1))


def s_names(ctx, T, d):
    world(ctx, T, 1000)
    spots(ctx, T, balloon_t=(0, 0, 0))
    for i, (x, nm) in enumerate(((150, "BloxKid!"), (340, "Builder_Bob!"), (500, "CozyCat!"))):
        if T >= 28.55 + i * 0.22:
            st.speech_bubble(ctx, x, 620 - (i % 2) * 70, nm, 34, T - 28.55 - i * 0.22, tail=(0, 1))
    st.sfx_word(ctx, 360, 560, "LOUD!", T - 28.55, col=st.RED, size=44)


def s_found(ctx, T, d):
    burst_ground(ctx, T, "#fff1a8", "#f2b02e")
    st.cardboard_box(ctx, 520, 1000, 0.9, peek=0.0)
    COZY.draw(ctx, 520, 1000 - 70, 0.7, "shock", T, arms=("up", "up"), shadow=False, snap=snap_at(T, 29.36))
    st.cardboard_box(ctx, 520, 1000, 0.9, peek=0.0)
    toby(ctx, 190, 1000, 1.0, "grin", T, arms=("down", "point"), talk=talking("toby", T))
    st.speech_bubble(ctx, 240, 520, "FOUND YOU!", 52, T - 29.36, tail=(0, 1))


def s_bday(ctx, T, d):
    st.burst(ctx, T, "#ffc4ec", "#c0307a", cy=600, spin=0.7)
    st.cake(ctx, 360, 1000, 1.0, T, lit=True)
    toby(ctx, 140, 1000, 0.9, "laugh", T, arms=("up", "up"), talk=talking("toby", T), tag=False)
    COZY.draw(ctx, 590, 1000, 0.85, "cold", T, arms=("cross", "cross"))
    st.confetti(ctx, T, 30.0, n=40)
    st.speech_bubble(ctx, 330, 380, "HAPPY BIRTHDAY!", 48, T - 30.01, tail=(-1, 1))


# ================================================================ kicked, and back
def s_beg(ctx, T, d):
    world(ctx, T, 1000)
    for i, x in enumerate((130, 290, 450, 600)):
        P[i].draw(ctx, x, 1000, 0.8, "cry", T, arms=("up", "up"), bob=1.4, look=0.4)
    st.speech_bubble(ctx, 360, 600, "PLEASE!", 56, T - 31.0, tail=(0, 1))


def s_mods(ctx, T, d):
    st.night_wall(ctx, 1000, wall="#1e2a5a")
    st.block(ctx, -100, 1000, 920, 500, 0, hexc("#2a2f45"), 4, gloss=False)
    st.bold_text(ctx, "MOD HQ", 360, 640, 58, hexc("#6fc3ff"), shadow=False, stroke=0.1)
    for i, x in enumerate((160, 360, 560)):
        MOD.draw(ctx, x, 1000, 0.85, "determined", T, arms=("cross", "cross"))
        st.name_pill(ctx, x, 1000 - 3.45 * U1 * 0.85, "[MOD]", size=22, col=st.RED)
    label(ctx, "REMOVE HIM", 360, LBL_Y, 74, bg=st.RED, scale=pop(T - 32.37) if T >= 32.37 else 0.0)


def s_kick(ctx, T, d):
    burst_ground(ctx, T, "#ffb3b3", "#c0303a", spin=0.8)
    ADMIN.draw(ctx, 170, 1000, 1.0, keyed(T, [(0, "angry"), (33.53, "determined")]), T,
               arms=("down", "punch") if T >= 33.45 else ("down", "point"), snap=snap_at(T, 33.53))
    st.name_pill(ctx, 170, 1000 - 4.05 * U1, "[ADMIN]", size=24, col=st.RED)
    k = T - 33.53
    if k < 0:
        toby(ctx, 470, 1000, 0.95, "happy", T, arms=("wave", "down"))
    else:
        q = clamp(k / 0.5)
        x, y, sc = lerp(430, 440, q), lerp(1000, 520, q), lerp(0.95, 0.3, q)
        ctx.save()
        ctx.translate(x, y - 1.5 * U1 * sc)
        ctx.rotate(k * 9)
        ctx.translate(-x, -(y - 1.5 * U1 * sc))
        toby(ctx, x, y, sc, "shock", T, arms=("up", "up"), tag=False)
        ctx.restore()
    st.sfx_word(ctx, 360, 560, "KICK!", k, col=st.RED, size=66)


def s_kicked(ctx, T, d):
    st.void_bg(ctx, top="#2a2d40", bottom="#0d0f18", y0=200, y1=1200)
    st.disconnect_dialog(ctx, 360, 600, 1.08, T - 34.02, title="Kicked",
                         msg="You were kicked: too much welcoming", code="Error Code: 267")


def s_rejoin(ctx, T, d):
    world(ctx, T, 1000)
    st.spawn_pad(ctx, 360, 1000, 1.3, beam=clamp(1 - (T - 34.62) / 0.5))
    st.game_toast(ctx, 360, LBL_Y, "Toby", "joined the game", T - 34.58, icon_col="#22b8c8", name_col="#6fe6ff",
                  size=28)
    appear(ctx, T, 34.62, 360, 880, 90)
    if T >= 34.75:
        toby(ctx, 360, 1000, 1.0, "grin", T, arms=("wave", "down"))


def s_twice(ctx, T, d):
    burst_ground(ctx, T, "#ffc4ec", "#c0307a")
    lift = 30 * ease(clamp((T - 35.3) / 0.5))
    toby(ctx, 300, 1000 - lift, 1.0, "laugh", T, arms=("down", "up"), tag=False)
    st.balloons(ctx, 420, 640 - lift, 0.95, T, n=6 if T < 35.3 else 12, seed=4, lean=0.35)
    label(ctx, "x2 BALLOONS", 360, LBL_Y, 76, fg=st.YELLOW, scale=pop(T - 35.3) if T >= 35.3 else 0.0)


# ================================================================ the developers' new button
def s_devs(ctx, T, d):
    st.office(ctx, T, night=1.0, y_desk=900)
    DEV.draw(ctx, 230, 1070, 1.4, keyed(T, [(0, "sleepy"), (36.83, "determined")]), T, arms=("hold", "hold"),
             bob=0.4, snap=snap_at(T, 36.83))
    st.block(ctx, -100, 900, 920, 50, 8, hexc("#b9b4d8"), 5)
    st.block(ctx, -100, 950, 920, 700, 0, hexc("#7a6aa8"), 5, gloss=False)
    st.monitor(ctx, 500, 905, 0.42, T, lambda c, x, y, w, h, TT: st.code_screen(c, x, y, w, h, TT, typed=0.3))
    label(ctx, "THE DEVS", 360, 330, 74, bg=st.UI_DARK, fg=st.YELLOW, scale=pop(T - 36.83) if T >= 36.83 else 0.0)


def s_newbtn(ctx, T, d):
    st.night_wall(ctx, 2000)

    def scr(c, x, y, w, h, TT):
        st.code_screen(c, x, y, w, h, TT, typed=clamp((TT - 37.6) / 0.5))
        if TT >= 38.14:
            st.leave_button(c, x + w / 2, y + h * 0.62, 0.55 * w / 560 * min(1.0, pop(TT - 38.14) + 0.05), TT)
    st.monitor(ctx, 360, 860, 1.12, T, scr)
    st.keyboard(ctx, 360, 1000, 1.0, T, mash=1.0 if T < 38.1 else 0.0)
    label(ctx, "NEW BUTTON", 360, 300, 72, fg=st.GREEN, scale=pop(T - 38.0) if T >= 38.0 else 0.0)


def s_escape(ctx, T, d):
    world(ctx, T, 1000)
    st.esc_menu(ctx, T, k=T - 38.51, hi="leave" if T >= 39.28 else None, pressed=0.0)
    kk = ease(clamp((T - 38.7) / 0.5))
    st.cursor(ctx, lerp(620, 380, kk), lerp(600, 920, kk), 1.6)
    if T >= 39.28:
        st.glow(ctx, 360, 915, 160, (0.4, 0.6, 1.0), 0.35)


def s_instant(ctx, T, d):
    world(ctx, T, 1000)
    gone = T >= 40.07
    if not gone:
        P[1].draw(ctx, 330, 1000, 1.0, "happy", T, arms=("down", "point"))
    appear(ctx, T, 40.07, 330, 820, 110)
    st.leave_button(ctx, 520, 640, 0.42, T, pressed=1.0 if T >= 39.95 else 0.0)
    kk = ease(clamp((T - 39.7) / 0.25))
    st.cursor(ctx, lerp(650, 560, kk), lerp(820, 660, kk), 1.4, click=1.0 if T >= 39.95 else 0.0)
    st.sfx_word(ctx, 330, 580, "POOF!", T - 40.07, col=st.PINK, size=56)


def s_leavebig(ctx, T, d):
    st.burst(ctx, T, "#c4d8ff", "#2f3f9a", cy=640, spin=0.5)
    st.leave_button(ctx, 360, 640, 1.05, T, pressed=1.0 if T >= 40.75 else 0.0, glow_a=0.5)
    kk = ease(clamp((T - 40.69) / 0.06))
    st.cursor(ctx, lerp(560, 470, kk), lerp(820, 690, kk), 2.2, click=1.0 if T >= 40.75 else 0.0)
    st.sfx_word(ctx, 360, 400, "CLICK!", T - 40.75, col=st.BLUE, size=70)


def s_clicks(ctx, T, d):
    burst_ground(ctx, T, "#c4d8ff", "#2f3f9a")
    for i, x in enumerate((120, 280, 440, 600)):
        tk = 41.6 + i * 0.2
        P[i + 2].draw(ctx, x, 1000, 0.62, "determined", T, arms=("down", "point"))
        st.leave_button(ctx, x, 640, 0.24, T, pressed=1.0 if T >= tk else 0.0)
        st.cursor(ctx, x + 40, 665, 1.0, click=1.0 if T >= tk else 0.0)
        st.sfx_word(ctx, x, 520, "CLICK", T - tk, col=st.BLUE, size=30, seed=i)


def s_onebyone(ctx, T, d):
    world(ctx, T, 1000)
    xs = (110, 230, 350, 470, 590)
    for i, x in enumerate(xs):
        t0 = 42.43 + i * 0.2
        if T < t0:
            P[i + 4].draw(ctx, x, 1000, 0.7, "neutral", T, look=0.3)
        appear(ctx, T, t0, x, 860, 70)
    for i, nm in enumerate(("CozyCat", "Builder_Bob", "Racer_X")):
        st.game_toast(ctx, 360, LBL_Y + i * 56, nm, "left the game", T - (42.45 + i * 0.3), size=24)


def s_emptied(ctx, T, d):
    st.game_sky(ctx, top="#f28a5a", bottom="#ffd9a8")
    st.baseplate(ctx, 1000)
    n = max(1, int(lerp(26, 1, ease(clamp((T - 43.4) / 0.7)))))
    st.number_counter(ctx, 360, 520, 0.9, n, T, col="#ff4f5a", prefix="PLAYERS: ")
    toby(ctx, 360, 1000, 0.55, "happy", T, arms=("wave", "down"), tag=False)


def s_alone(ctx, T, d):
    world(ctx, T, 1000)
    st.tint(ctx, (0.15, 0.2, 0.45), 0.28)
    toby(ctx, 360, 1000, 1.0, keyed(T, [(0, "neutral"), (45.4, "sad")]), T, arms=("down", "down"),
         snap=snap_at(T, 45.4))
    st.balloons(ctx, 470, 860, 0.8, T, n=4, seed=6, droop=0.3 * clamp((T - 44.4) / 1.2), lean=1.0 * clamp((T - 44.4) / 1.2))
    label(ctx, "ALONE", 360, LBL_Y, 80, bg=st.UI_DARK, fg=(1, 1, 1), scale=pop(T - 45.43) if T >= 45.43 else 0.0)


# ================================================================ the doorbell
def s_crazy(ctx, T, d):
    st.burst(ctx, T, "#e2c8ff", "#7a3fd8", cy=560, spin=0.6)
    toby_cu(ctx, keyed(T, [(0, "sad"), (46.40, "stars")]), T, arms=("up", "up"), snap=snap_at(T, 46.40))
    label(ctx, "CRAZY PART", 360, 300, 74, fg=st.YELLOW, scale=pop(T - 46.40) if T >= 46.40 else 0.0)


def s_spot(ctx, T, d):
    st.burst(ctx, T, "#bfe3ff", "#2f6bd8", cy=560, spin=0.4)
    m, k = toby_cu(ctx, keyed(T, [(0, "neutral"), (48.2, "shock")]), T, arms=("hold", "hold"), snap=snap_at(T, 48.2))
    binoculars(ctx, *m(360, 545), 1.5 * k)
    st.leave_button(ctx, 520, 290, 0.32 * min(1.0, pop(T - 47.6) + 0.05) if T >= 47.6 else 0.0, T, glow_a=0.4)
    if T >= 48.2:
        st.speech_bubble(ctx, *m(170, 300), "!", 70, T - 48.2, tail=(1, 1))


def s_doorbell(ctx, T, d):
    world(ctx, T, 1000)
    toby(ctx, 200, 1000, 0.95, keyed(T, [(0, "happy"), (49.25, "stars")]), T, arms=("down", "point"),
         snap=snap_at(T, 49.25))
    st.thought_cloud(ctx, 470, 600, 330, 260, T - 48.65, tail=(-1, 1))
    if T >= 48.75:
        st.doorbell(ctx, 470, 600, 0.75 * min(1.0, pop(T - 48.75) + 0.05), pressed=1.0 if T >= 49.25 else 0.0)
    st.sfx_word(ctx, 470, 400, "DING DONG!", T - 49.25, col=st.YELLOW, size=50)


def s_click20(ctx, T, d):
    st.burst(ctx, T, "#c4d8ff", "#2f3f9a", cy=600, spin=0.6)
    st.leave_button(ctx, 470, 760, 0.62, T, pressed=1.0 if int((T - 50.0) * 8) % 2 == 0 and T >= 50.0 else 0.0)
    toby(ctx, 160, 1000, 0.95, "crazy", T, arms=("down", "point"), tag=False)
    n = int(clamp((T - 50.03) / 0.95) * 20)
    st.number_counter(ctx, 360, 330, 0.9, n, T, col="#ffd84a", prefix="CLICKS: ")
    if T >= 50.0:
        st.cursor(ctx, 540, 790 + 6 * (int((T - 50.0) * 8) % 2), 1.6, click=1.0 if int((T - 50.0) * 8) % 2 == 0 else 0.0)


def s_rejoinloop(ctx, T, d):
    world(ctx, T, 1000)
    st.spawn_pad(ctx, 360, 1000, 1.2)
    phase = int((T - 51.32) / 0.35)
    if phase % 2 == 0:
        toby(ctx, 360, 1000, 0.95, "laugh", T, arms=("wave", "down"))
    appear(ctx, T, 51.32 + 0.35 * (phase + 1) - 0.05, 360, 880, 80)
    msgs = [("Toby", "left the game"), ("Toby", "joined the game")] * 2
    for i, (nm, msg) in enumerate(msgs):
        st.game_toast(ctx, 360, LBL_Y + i * 52, nm, msg, T - (51.35 + i * 0.3), icon_col="#22b8c8",
                      name_col="#6fe6ff", size=24)


def s_popin(ctx, T, d):
    burst_ground(ctx, T, "#ffe27a", "#ff5fb0")
    appear(ctx, T, 52.7, 360, 860, 110)
    if T >= 52.85:
        toby(ctx, 300, 1000, 1.05, "laugh", T, arms=("down", "up"))
        st.pizza_tower(ctx, 470, 1000, 4, w=150, T=T)
    st.sfx_word(ctx, 360, LBL_Y + 60, "TA-DA!", T - 52.9, col=st.PINK, size=52)


def s_order(ctx, T, d):
    st.burst(ctx, T, "#ffe27a", "#ff7a1a", cy=560, spin=0.6)
    m, k = toby_cu(ctx, "crazy", T, arms=("hold", "hold"), talk=talking("toby", T))
    st.pizza(ctx, *m(360, 860), 150 * k, kind="pepperoni", T=T)
    msg = typed("DID SOMEBODY ORDER PIZZA?", T, 53.35, cps=24)
    if msg:
        st.speech_bubble(ctx, 360, 240, msg, 34, 1.0, tail=(0, 1))


# ================================================================ the developers log off
def s_devscry(ctx, T, d):
    st.office(ctx, T, night=1.0, y_desk=1000)
    for i, x in enumerate((140, 360, 580)):
        DEV.draw(ctx, x, 1000, 1.05, "cry", T, arms=("up", "up"), bob=0.8)
    label(ctx, "THE DEVS", 360, 300, 72, bg=st.UI_DARK, fg=st.YELLOW, scale=pop(T - 54.88) if T >= 54.88 else 0.0)


def s_logoff(ctx, T, d):
    st.night_wall(ctx, 2000)

    def scr(c, x, y, w, h, TT):
        c.save()
        c.translate(x, y)
        c.scale(w / 720, h / 800)
        c.translate(0, -180)
        st.esc_menu(c, TT, k=1.0, hi="leave", pressed=1.0 if TT >= 56.45 else 0.0, names=["[DEV] Sam", "[DEV] Ana",
                                                                                         "[DEV] Leo"])
        c.restore()
        if TT >= 56.5:
            c.set_source_rgba(0.05, 0.06, 0.1, 0.85 * clamp((TT - 56.5) / 0.15))
            c.rectangle(x, y, w, h)
            c.fill()
            st.bold_text(c, "You left the game", x + w / 2, y + h / 2, 34, (1, 1, 1), shadow=False, stroke=0.0,
                         scale=pop(TT - 56.5))
    st.monitor(ctx, 360, 860, 1.12, T, scr)
    kk = ease(clamp((T - 56.05) / 0.35))
    st.cursor(ctx, lerp(600, 380, kk), lerp(980, 820, kk), 1.8, click=1.0 if T >= 56.45 else 0.0)
    label(ctx, "LOGGED OFF", 360, 300, 76, bg=st.UI_DARK, fg=st.GREEN, scale=pop(T - 56.5) if T >= 56.5 else 0.0)


# ================================================================ shots
S = []


def shot(start, draw, keys, **kw):
    kw.setdefault("vignette", 0.15)
    S.append(dict(start=start, draw=draw, keys=keys, **kw))


def punch(t0, z0, c0, t_key, z1, c1, m=0.13):
    return [(t0, z0, c0), (t_key, z1, c1, m)]


C = (360, 700)
G = (360, 760)

shot(0.00, s_hook, [(0.0, 1.0, (360, 680)), (0.34, 1.08, (360, 660), 0.1)], shake=(0.34, 10),
     keep=[(110, 180, 610, 330)])
shot(0.80, at(s_flee, 0.80), punch(0.80, 1.0, G, 0.85, 1.05, (360, 740), 0.1))
shot(1.40, at(s_menu, 1.40), punch(1.40, 1.0, (360, 640), 2.13, 1.05, (360, 680), 0.08), shake=(0.73, 10),
     keep=[(50, 180, 670, 980)])
shot(2.55, at(s_spawn, 2.55), punch(2.55, 1.0, G, 3.16, 1.06, (360, 740), 0.12))
shot(3.47, at(s_dream, 3.47), punch(3.47, 1.0, C, 4.01, 1.08, (360, 660), 0.12), keep=[(340, 180, 660, 420)])
shot(4.68, at(s_welcome, 4.68), punch(4.68, 1.0, G, 5.93, 1.06, (360, 740), 0.12))
shot(6.40, at(s_obby, 6.40), punch(6.40, 1.0, G, 7.2, 1.05, (360, 740), 0.12))
shot(7.70, at(s_build, 7.70), punch(7.70, 1.0, G, 8.48, 1.05, (380, 740), 0.12), keep=[(180, 560, 660, 760)])
shot(9.10, at(s_signwide, 9.10), [(9.10, 1.0, (360, 700)), (10.5, 1.05, (360, 700), 1.2)],
     keep=[(190, 630, 590, 1000)])
shot(10.58, at(s_yourewelcome, 10.58), punch(10.58, 1.0, C, 10.61, 1.1, (360, 650), 0.08), shake=(0.03, 8),
     keep=[(80, 180, 640, 320)])
shot(11.50, at(s_bonk, 11.50), punch(11.50, 1.0, G, 11.93, 1.06, (340, 740), 0.08), shake=(0.43, 10))
shot(12.24, at(s_fall, 12.24), punch(12.24, 1.0, G, 12.4, 1.05, (360, 740), 0.12))
shot(13.05, at(s_pizza, 13.05), punch(13.05, 1.0, G, 13.83, 1.06, (380, 760), 0.12), keep=[(200, 560, 600, 1000)])
shot(14.78, at(s_race, 14.78), punch(14.78, 1.0, G, 14.9, 1.04, (360, 740), 0.12), whip=1)
shot(15.64, at(s_pass, 15.64), punch(15.64, 1.0, G, 16.21, 1.05, (360, 760), 0.1))
shot(16.90, at(s_stop, 16.90), punch(16.90, 1.0, G, 17.13, 1.06, (380, 760), 0.08), shake=(0.23, 12))
shot(18.18, at(s_choice, 18.18), punch(18.18, 1.0, C, 18.21, 1.06, (360, 670), 0.1),
     keep=[(60, 190, 640, 420)])
shot(19.50, at(s_jam, 19.50), punch(19.50, 1.0, G, 20.74, 1.05, (360, 760), 0.12), whip=-1,
     keep=[(40, 870, 680, 1000)])
shot(21.57, at(s_notdone, 21.57), punch(21.57, 1.0, C, 22.29, 1.1, (380, 650), 0.12))
shot(22.46, at(s_party, 22.46), punch(22.46, 1.0, G, 23.28, 1.08, (360, 720), 0.08), shake=(0.82, 12),
     keep=[(100, 300, 620, 1000)])
shot(24.06, at(s_hideseek, 24.06), punch(24.06, 1.0, G, 24.66, 1.05, (360, 760), 0.12), whip=1)
shot(25.27, at(s_balloons, 25.27), punch(25.27, 1.25, (330, 820), 25.72, 1.3, (330, 820), 0.12))
shot(26.34, at(s_exposed, 26.34), [(26.34, 1.0, G), (27.5, 1.08, (360, 780), 1.0)])
shot(27.56, at(s_shout, 27.56), punch(27.56, 1.0, C, 28.16, 1.08, (360, 660), 0.1), keep=[(260, 190, 640, 420)])
shot(28.48, at(s_names, 28.48), punch(28.48, 1.0, G, 28.6, 1.04, (360, 760), 0.1), keep=[(60, 520, 660, 1000)])
shot(29.33, at(s_found, 29.33), punch(29.33, 1.0, G, 29.36, 1.07, (360, 760), 0.08), shake=(0.03, 10))
shot(30.00, at(s_bday, 30.00), punch(30.00, 1.0, G, 30.01, 1.06, (360, 740), 0.08), shake=(0.01, 12),
     keep=[(80, 300, 640, 1000)])
shot(30.92, at(s_beg, 30.92), punch(30.92, 1.0, G, 31.34, 1.05, (360, 760), 0.12))
shot(31.64, at(s_mods, 31.64), punch(31.64, 1.0, G, 32.37, 1.06, (360, 760), 0.12), whip=1)
shot(32.99, at(s_kick, 32.99), punch(32.99, 1.0, G, 33.53, 1.06, (380, 740), 0.08), shake=(0.54, 20))
shot(34.00, at(s_kicked, 34.00), punch(34.00, 1.0, (360, 640), 34.05, 1.06, (360, 640), 0.1), shake=(0.03, 8),
     keep=[(70, 420, 650, 780)])
shot(34.53, at(s_rejoin, 34.53), punch(34.53, 1.0, G, 34.75, 1.06, (360, 760), 0.1))
shot(35.27, at(s_twice, 35.27), punch(35.27, 1.0, G, 35.3, 1.07, (360, 740), 0.1))
shot(36.53, at(s_devs, 36.53), punch(36.53, 1.0, G, 36.83, 1.08, (320, 760), 0.12), whip=-1)
shot(37.58, at(s_newbtn, 37.58), punch(37.58, 1.0, (360, 700), 38.14, 1.06, (360, 680), 0.1),
     keep=[(80, 240, 640, 840)])
shot(38.51, at(s_escape, 38.51), punch(38.51, 1.0, (360, 640), 39.28, 1.05, (360, 680), 0.12),
     keep=[(50, 180, 670, 980)])
shot(39.69, at(s_instant, 39.69), punch(39.69, 1.0, G, 40.07, 1.06, (380, 740), 0.08), shake=(0.38, 8))
shot(40.69, at(s_leavebig, 40.69), punch(40.69, 1.0, (360, 640), 40.75, 1.1, (360, 640), 0.06), shake=(0.06, 22),
     keep=[(80, 330, 640, 860)])
shot(41.51, at(s_clicks, 41.51), punch(41.51, 1.0, G, 41.6, 1.04, (360, 760), 0.12))
shot(42.40, at(s_onebyone, 42.40), punch(42.40, 1.0, G, 42.85, 1.04, (360, 760), 0.12))
shot(43.34, at(s_emptied, 43.34), [(43.34, 1.0, G), (44.2, 0.96, (360, 740), 0.8)])
shot(44.28, at(s_alone, 44.28), [(44.28, 1.0, G), (45.8, 1.1, (360, 720), 1.5)])
shot(45.83, at(s_crazy, 45.83), punch(45.83, 1.0, C, 46.40, 1.1, (360, 650), 0.1), shake=(0.57, 10))
shot(47.10, at(s_spot, 47.10), punch(47.10, 1.0, C, 48.2, 1.08, (360, 660), 0.12), keep=[(380, 180, 660, 400)])
shot(48.59, at(s_doorbell, 48.59), punch(48.59, 1.0, G, 49.25, 1.06, (380, 720), 0.1), keep=[(290, 360, 650, 760)])
shot(49.81, at(s_click20, 49.81), punch(49.81, 1.0, (360, 700), 50.42, 1.06, (360, 680), 0.12),
     keep=[(150, 260, 640, 900)])
shot(51.32, at(s_rejoinloop, 51.32), punch(51.32, 1.0, G, 51.8, 1.04, (360, 760), 0.12))
shot(52.68, at(s_popin, 52.68), punch(52.68, 1.0, G, 52.85, 1.07, (360, 760), 0.08), shake=(0.17, 10))
shot(53.32, at(s_order, 53.32), punch(53.32, 1.0, C, 53.98, 1.08, (360, 660), 0.12), keep=[(60, 190, 660, 300)])
shot(54.75, at(s_devscry, 54.75), punch(54.75, 1.0, G, 55.47, 1.06, (360, 760), 0.12), whip=-1)
shot(56.00, at(s_logoff, 56.00), punch(56.00, 1.0, G, 56.5, 1.06, (360, 760), 0.1), shake=(0.5, 8))
SHOTS = S
_rw_draw, _rw_ov = st.rewind_shot(SHOTS, [55.5, 44.8, 33.6, 17.2, 10.9, 0.0])
shot(57.30, _rw_draw, [(57.30, 1.0, (360, 640))], overlay=_rw_ov, blur=False, closeup=True, keep=[])
HUD_SHOTS = (0.80, 2.55, 4.68, 6.40, 7.70, 11.50, 12.24, 13.05, 14.78, 15.64, 19.50, 24.06, 25.27, 28.48, 30.92,
             34.53, 39.69, 42.40, 43.34, 44.28, 48.59, 51.32)
for sh in S:
    if round(sh["start"], 2) in HUD_SHOTS:
        sh["overlay"] = hud_ov(sh["start"])
        sh["top"] = 345                                   # characters and labels stay below the HUD
S.sort(key=lambda sh: sh["start"])
for k, s in enumerate(SHOTS):
    s["end"] = SHOTS[k + 1]["start"] if k + 1 < len(SHOTS) else TOTAL

# ---------------------------------------------------------------- SFX (time, file, volume before SFX_GAIN)
# One sound per visual event, spaced >= ~0.25 s; 4 booms (party, birthday, kick, LEAVE GAME).
SFX = [
    (0.03, "sting_low.wav", 0.9), (0.34, "pop.wav", 0.8), (0.80, "whoosh.wav", 0.7), (1.40, "swish.wav", 0.6),
    (1.89, "tick.wav", 0.6), (2.13, "click.wav", 1.2), (2.25, "hit.wav", 0.9), (2.62, "sparkle.wav", 0.8),
    (3.16, "pop.wav", 0.8), (3.55, "pop.wav", 0.6), (4.01, "ding.wav", 0.8), (4.7, "pop.wav", 0.5),
    (5.2, "pop.wav", 0.5), (5.93, "success.wav", 0.8), (6.45, "click.wav", 0.6), (6.9, "swish.wav", 0.5),
    (7.2, "boing.wav", 0.8), (7.85, "hit.wav", 0.9), (8.1, "pop.wav", 0.6), (8.5, "hit.wav", 0.8),
    (8.8, "pop.wav", 0.6), (9.15, "tick.wav", 0.5), (9.89, "pop.wav", 0.8), (10.61, "sparkle.wav", 0.9),
    (11.05, "pop.wav", 0.5), (11.93, "hit.wav", 1.1), (12.3, "swish.wav", 0.5), (12.75, "thud.wav", 0.9),
    (13.1, "thud.wav", 0.7), (13.4, "pop.wav", 0.5), (13.83, "ding.wav", 0.8), (14.3, "pop.wav", 0.5),
    (14.8, "whoosh.wav", 0.8), (15.15, "whoosh.wav", 0.6), (15.7, "tick.wav", 0.5), (16.21, "whoosh.wav", 0.9),
    (16.9, "swish.wav", 0.5), (17.13, "hit.wav", 1.0), (17.5, "pop.wav", 0.5), (18.21, "pop.wav", 0.8),
    (18.94, "pop.wav", 0.8), (19.5, "swish.wav", 0.5), (19.85, "buzz.wav", 0.7), (20.3, "buzz.wav", 0.7),
    (20.74, "pop.wav", 0.8), (21.6, "tick.wav", 0.5), (22.29, "sparkle.wav", 0.8), (22.5, "pop.wav", 0.5),
    (23.28, "boom.wav", 1.4), (23.6, "pop.wav", 0.5), (24.06, "swish.wav", 0.6), (24.66, "click.wav", 0.6),
    (25.3, "pop.wav", 0.8), (25.72, "pop.wav", 0.8), (26.06, "pop.wav", 0.8), (26.45, "whoosh.wav", 0.6),
    (26.68, "hit.wav", 0.9), (27.1, "pop.wav", 0.5), (27.6, "tick.wav", 0.5), (28.16, "hit.wav", 0.9),
    (28.55, "pop.wav", 0.6), (28.77, "pop.wav", 0.6), (28.99, "pop.wav", 0.6), (29.36, "hit.wav", 1.0),
    (30.01, "boom.wav", 1.3), (30.35, "pop.wav", 0.5), (31.0, "pop.wav", 0.7), (31.34, "tick.wav", 0.5),
    (31.64, "swish.wav", 0.5), (32.37, "pop.wav", 0.8), (32.99, "tick.wav", 0.5), (33.53, "boom.wav", 1.4),
    (34.02, "buzz.wav", 0.8), (34.62, "sparkle.wav", 0.7), (35.0, "pop.wav", 0.5), (35.3, "pop.wav", 0.8),
    (35.7, "pop.wav", 0.5), (36.55, "swish.wav", 0.6), (36.83, "pop.wav", 0.7), (37.6, "type_key.wav", 0.6),
    (37.85, "type_key.wav", 0.6), (38.14, "ding.wav", 0.9), (38.51, "swish.wav", 0.6), (38.9, "tick.wav", 0.5),
    (39.28, "pop.wav", 0.8), (39.95, "click.wav", 0.9), (40.07, "whoosh.wav", 0.8), (40.75, "boom.wav", 1.3),
    (41.05, "click.wav", 0.6), (41.6, "click.wav", 0.7), (41.8, "click.wav", 0.6), (42.0, "click.wav", 0.6),
    (42.43, "pop.wav", 0.7), (42.63, "pop.wav", 0.6), (42.83, "pop.wav", 0.6), (43.03, "pop.wav", 0.6),
    (43.4, "whoosh.wav", 0.5), (43.8, "tick.wav", 0.6), (44.3, "sting_soft.wav", 0.8), (45.43, "tick.wav", 0.6),
    (45.85, "tick.wav", 0.5), (46.40, "hit.wav", 1.0), (46.7, "sparkle.wav", 0.6), (47.15, "swish.wav", 0.5),
    (47.6, "pop.wav", 0.6), (48.2, "pop.wav", 0.8), (48.65, "pop.wav", 0.6), (49.25, "bell.wav", 1.0),
    (49.85, "tick.wav", 0.5), (50.05, "click.wav", 0.7), (50.3, "click.wav", 0.6), (50.55, "click.wav", 0.6),
    (50.8, "click.wav", 0.6), (51.1, "ding.wav", 0.6), (51.35, "pop.wav", 0.7), (51.7, "pop.wav", 0.6),
    (52.05, "pop.wav", 0.6), (52.4, "pop.wav", 0.6), (52.7, "sparkle.wav", 0.8), (52.9, "pop.wav", 0.6),
    (53.35, "pop.wav", 0.6), (53.98, "tick.wav", 0.5), (54.3, "pop.wav", 0.6), (54.78, "swish.wav", 0.5),
    (55.1, "tick.wav", 0.5), (55.47, "pop.wav", 0.6), (56.0, "click.wav", 0.7), (56.45, "pop.wav", 0.7),
    (56.57, "pop.wav", 0.6), (56.69, "pop.wav", 0.6), (56.9, "success.wav", 0.8), (57.30, "whip.wav", 0.9),
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

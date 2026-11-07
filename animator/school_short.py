"""Story (Short, 9:16): "What If the WHOLE SCHOOL Became Roblox?" cut to 60 s from the long video's voice.

Voice: output/school_short/voice.wav, 10 pieces of output/whole_school/voice.mp3 joined at real pauses by
assembler/cut_voice.py (segments in SEGMENTS below; 0.28 s word to word at each join, 30 ms fades).
Plan: output/school_short/plan.md (47 shots + the rewind).
"Cut cut na lage" (the user, 2026-11-07): every voice join lands on a picture that continues the last one (the same
classroom for the PA, the Friday of the announcement for the boss, the gym for the swing), and the music runs on
through the joins (SCORE changes only on chapter turns).
Same build as leave_noob.py: engine.profile("set3"), SAFE_BODY whole characters, closeup() reaction shots, the
Roblox in-game interface on the in-game shots. The landscape school places of school_sets.py are drawn through
land(): (640, 640) of the 1280x720 world lands on (360, 1000) of the portrait frame.
Run (from animator/):
  python3 school_short.py ../output/school_short/clips/animation.mp4 ../output/school_short/cues.json"""
import math
import os
import sys

import engine
import school_sets as ss
import sets as st
import style
from engine import PI, clamp, ease, hexc, keyed, lerp, pop, render
from sets import label
from style import Block

engine.profile("set3")
engine.ENERGY = 3.0
SAFE_BODY = True
engine.LIPSYNC = True
TOTAL = 60.0
SFX_GAIN = 0.24
ss.W, ss.H = 1280, 720            # school_sets places keep their landscape width (drawn through land())

# old (long voice) -> new (this voice): new = old + offset, from output/school_short/segments.json
SEGMENTS = [(0.00, 5.01, 0.16), (34.62, 39.23, -29.38), (60.45, 63.12, -50.42), (72.04, 77.65, -59.15),
            (236.00, 241.14, -217.32), (276.95, 283.19, -252.99), (326.80, 333.68, -296.37),
            (404.90, 413.09, -367.42), (420.43, 426.73, -374.57), (457.01, 464.17, -404.65)]
DIALOGUE = {"pebble": [(12.95, 15.59)], "stone": [(18.78, 23.70)],
            "kid": [(29.43, 30.15), (45.85, 49.73), (58.49, 59.35)], "mom": [(56.77, 58.17)]}

# music follows the situation (score.py); it runs on through the voice joins inside a chapter
SCORE = [(0.0, "hype"), (5.24, "game"), (18.68, "tension"), (30.43, "boss"), (37.48, "final"), (40.28, "triumph"),
         (52.36, "mystery"), (59.30, "hype")]
STINGS = [(28.31, "hit"), (31.18, "rise"), (31.18, "hit"), (39.44, "hit_major"), (49.99, "fanfare"), (58.49, "hit")]

KID = style.KID
MOM = style.MOM
PEBBLE = Block("#7fb8ff", pants="#5a4fb0", skin="#e8c3a8", hair="bun", hair_col="#6a4a3a", outfit="cardigan",
               glasses=True, lashes=True, shoes="dark")
STONE = Block("#3b3f5a", pants="#2b2f45", skin="#d9a77f", hair="smooth", hair_col="#555566", outfit="suit",
              crown=True, accent="#e8323a", shoes="dark")
LEO = Block("#ff8a3d", pants="#3b3f5a", skin="#c89f82", hair="spiky", hair_col="#2a1a14", outfit="tshirt")
PRIYA = Block("#9d5cff", pants="#2b2f45", skin="#b98a6a", hair="pony", hair_col="#1a1010", glasses=True, lashes=True)
P = [style.crowd_member(i) for i in range(12)]
CAST = {"kid": KID, "mom": MOM, "pebble": PEBBLE, "stone": STONE}

U1 = Block.HW * 64
FACE_S = 4.2
GY = 1000                          # portrait ground line (feet)
BLOCK_COLS = ("#ff4f5a", "#4f8bff", "#4fd16a", "#ffd84a", "#9d5cff", "#ff8a3d")
NAMES = ["Leo", "Priya_99", "xX_Ninja_Xx", "PizzaLover", "ToiletDestroyer9000"]


def talking(who, T):
    return any(a <= T <= b for a, b in DIALOGUE.get(who, ()))


def snap_at(T, t0):
    return (T - t0) if T >= t0 else None


def at(fn, T0):
    return lambda ctx, t, d: fn(ctx, T0 + t, d)


def typed(txt, T, t0, cps=22):
    return txt[:max(0, int((T - t0) * cps))]


def lbl(ctx, txt, x, y, size, T, t, bg=None, fg=(1, 1, 1)):
    if T >= t:
        label(ctx, txt, x, y, size, bg=bg, fg=fg, scale=pop(T - t))


CU_FEET, CU_X, CU_S = 995, 320, 2.3


def closeup(ctx, ch, expr, T, x=360, look=0.0, arms=("down", "down"), s=FACE_S, talk=False, bob=0.35, snap=None):
    """A reaction close-up (from chat_filter_v2.py): the whole character, feet at y 995, head near (320, 465).
    Returns (m, k): m maps a point placed for a full-frame face (head (x, 560), scale s) onto this framing."""
    s2 = min(CU_S + 0.05, s * CU_S / FACE_S)
    k = s2 / s
    nx = CU_X + (x - 360) * k
    ch.draw(ctx, nx, CU_FEET, s2, expr, T, arms=arms, look=look, talk=talk, bob=bob, snap=snap)
    hx, hy = nx, CU_FEET - 2.5 * U1 * s2
    return (lambda px, py: (hx + (px - x) * k, hy + (py - 560) * k)), k


def land(ctx, draw, k=1.0, gx=640, gy=GY, fill=None):
    """Draw a landscape school_sets place: world point (gx, 640) lands on (360, gy), scaled k."""
    if fill:
        ctx.set_source_rgb(*hexc(fill))
        ctx.paint()
    ctx.save()
    ctx.translate(360 - gx * k, gy - ss.GROUND * k)
    ctx.scale(k, k)
    draw(ctx)
    ctx.restore()


def outside(ctx, T, y=GY):
    st.game_sky(ctx)
    st.block_clouds(ctx, T, y0=160, y1=520, n=4)
    st.baseplate(ctx, y)


def school(ctx, T, s=0.62, y=GY, sign=None, sign_k=1.0, lift=0.0, cx=640):
    outside(ctx, T, y)
    land(ctx, lambda c: ss.school_ext(c, T, cx=cx, s=s, sign=sign, sign_k=sign_k, lift=lift, ground=False), gy=y)


def classroom(ctx, T, board="", y=GY):
    land(ctx, lambda c: ss.classroom(c, T, board=board, clock_h=9.0), gy=y, fill="#8fd0e8")


def gym(ctx, T, dark_k=0.0, doors=0.0):
    land(ctx, lambda c: ss.gym(c, T, dark_k=dark_k, doors=doors), fill="#f0b866")


def falling_blocks(ctx, T, n=12, speed=620):
    for i in range(n):
        x = (i * 83 + 30) % 760 - 20
        y = ((T * speed + i * 157) % 1400) - 140
        sz = 38 + (i * 13) % 34
        ctx.save()
        ctx.translate(x, y)
        ctx.rotate(T * (1.5 + (i % 3)) + i)
        style.block(ctx, -sz / 2, -sz / 2, sz, sz, 6, hexc(BLOCK_COLS[i % len(BLOCK_COLS)]), 4)
        ctx.restore()


def tablet(ctx, x, y, s, T, fn=None, rot=0.0):
    """A hand-held tablet (x, y = centre); fn(c, x, y, w, h, T) draws the screen."""
    ctx.save()
    ctx.translate(x, y)
    ctx.rotate(rot)
    w, h = 300 * s, 210 * s
    style.block(ctx, -w / 2, -h / 2, w, h, 20 * s, hexc("#2b2f45"), 5)
    if fn:
        fn(ctx, -w / 2 + 14 * s, -h / 2 + 14 * s, w - 28 * s, h - 28 * s, T)
    ctx.restore()


def health(ctx, frac, name="FINAL EXAM", y=230):
    st.health_bar(ctx, frac, name=name, y=y)


def boss(ctx, T, x=360, s=0.6, jaw=0.15, rage=1.0, erase=0.0, y=GY):
    ss.exam_boss(ctx, x, y, s, T, jaw=jaw, rage=rage, erase_k=erase)


# ================================================================ Roblox in-game HUD (screen-space overlay)
Y_, PK_, BL_, GR_, OR_, RD_ = "#ffd84a", "#ff5fb0", "#6fc3ff", "#4fd16a", "#ff8a3d", "#ff4f5a"
CHAT_LOG = [   # (time posted, name or None for a grey system line, text, name colour)
    (5.4, None, "You joined Roblox School", None), (7.3, "Leo", "bro we're BLOCKS", OR_),
    (10.1, None, "Ms. Pebble joined the game", None), (11.2, "Priya_99", "present", PK_),
    (15.1, "Leo", "LOL WHO IS THAT", OR_), (15.5, "xX_Ninja_Xx", "toilet destroyer lmao", GR_),
    (18.8, "[ADMIN] Stone", "ATTENTION STUDENTS", RD_), (30.5, None, "The gym is open", None),
    (40.4, None, "Final exam defeated", None), (42.3, None, "ToiletDestroyer9000 is the new admin", None),
    (44.5, "Everyone", "TOILET DESTROYER!!", Y_), (51.1, "Priya_99", "SUMMER!!!", PK_),
]


def players_at(T):
    return 412


def hud(ctx, T):
    st.roblox_topbar(ctx, T, players=players_at(T))
    st.roblox_chat(ctx, CHAT_LOG, T, w=420, size=23)


def hud_ov(T0):
    return lambda ctx, t, d: hud(ctx, T0 + t)


LBL_Y = 520


# ================================================================ hook (0 - 5.24)
def s_hook(ctx, T, d):
    st.burst(ctx, T, "#ffd27a", "#ff4f2a", cy=560, spin=0.8)
    falling_blocks(ctx, T)
    m, k = closeup(ctx, KID, "scream", T, arms=("up", "up"), snap=snap_at(T, 0.04), bob=0.6)
    style.shake_lines(ctx, *m(360, 560), 300 * k, 260 * k, T, n=3, lw=9)
    label(ctx, "ROBLOX SCHOOL?!", 360, 230, 76, fg=st.YELLOW, scale=min(1.0, pop(T) + 0.35))


def normal_school(c):
    c.save()
    c.translate(640, ss.GROUND)
    c.scale(0.62, 0.62)
    style.block(c, -560, -420, 1120, 420, 4, hexc("#b8b0a0"), 5, gloss=False)
    style.block(c, -150, -540, 300, 140, 4, hexc("#a8a090"), 5, gloss=False)
    for row in range(2):
        for i in (-4, -3, -2, 2, 3, 4):
            style.block(c, i * 110 - 40, -360 + row * 150, 80, 90, 2, hexc("#7a8a9a"), 3, gloss=False)
    style.block(c, -95, -230, 190, 230, 4, hexc("#6a5a4a"), 5, gloss=False)
    c.restore()


def s_become(ctx, T, d, t_sweep=1.10, dur=0.45):
    st.game_sky(ctx, top="#b8c4d8", bottom="#e0e6ee")
    st.baseplate(ctx, GY, col="#7a9a6a")
    land(ctx, normal_school)
    sx = lerp(-120, 860, clamp((T - t_sweep) / dur))
    ctx.save()
    ctx.rectangle(-200, -200, sx + 200, 1800)
    ctx.clip()
    school(ctx, T)
    ctx.restore()
    st.glow(ctx, sx, 700, 220, (1, 1, 0.85), 0.9)
    ctx.set_source_rgba(1, 1, 1, 0.85)
    ctx.rectangle(sx - 12, -100, 24, 1500)
    ctx.fill()
    st.sparkles(ctx, T, sx, 700, spread=260, n=12, seed=4, c=(1, 1, 1))
    st.sfx_word(ctx, 360, 360, "WHOOSH!", T - t_sweep - 0.1, col=st.BLUE, size=56)


def s_roblox(ctx, T, d, t_word=2.25):
    school(ctx, T)
    for i, (x, nm) in enumerate(zip((105, 245, 475, 615), ("Leo", "Priya_99", "BloxKid", "xX_Ninja_Xx"))):
        ch = (LEO, PRIYA, P[3], P[4])[i]
        ch.draw(ctx, x, GY, 0.62, "stars" if T >= t_word else "happy", T, arms=("up", "up"), snap=snap_at(T, t_word))
        st.name_pill(ctx, x, GY - 3.75 * U1 * 0.62, nm, size=20)
    st.bold_text(ctx, "ROBLOX?!", 360, 340, 124, st.YELLOW, scale=pop(T - t_word) if T >= t_word else 0.0,
                 tilt=-0.06)


def s_days(ctx, T, d, t0=2.90):
    st.burst(ctx, T, "#e2c8ff", "#7a3fd8", cy=560, spin=0.4)
    for i, day in enumerate(("MON", "TUE", "WED", "THU", "FRI")):
        k = T - (t0 + 0.05 + i * 0.1)
        if k < 0:
            continue
        sc = 0.46 * (pop(k) if k < 0.6 else 1.0)
        x, y = (150, 360, 570, 255, 465)[i], (400, 400, 400, 620, 620)[i]
        ss.calendar(ctx, x, y, sc, top=day, big=str(i + 1), col="#e8323a" if i == 4 else "#4f8bff")
    if T >= 3.37:
        st.bold_text(ctx, "5 DAYS", 360, 850, 120, (1, 1, 1), scale=pop(T - 3.37))


def s_one(ctx, T, d, t_word=4.22):
    school(ctx, T)
    if T >= t_word:
        st.impact_star(ctx, 360, 330, 180, T - t_word, c1="#fff3a8", c2="#ffb02e")
        st.bold_text(ctx, "1", 360, 330, 250, st.GOLD, scale=pop(T - t_word))
        lbl(ctx, "ONE SCHOOL", 360, 560, 70, T, 4.51, fg=st.YELLOW)


# ================================================================ Day 1 (5.24 - 10.03)
def s_day1(ctx, T, d, t0=5.24):
    st.burst(ctx, T, "#e2c8ff", "#7a3fd8", cy=560, spin=0.3)
    st.day_write(ctx, "DAY", 1, 360, 520, T - t0, size=130, T=T)
    lbl(ctx, "MONDAY", 360, 760, 64, T, 5.95, bg=st.UI_DARK, fg=st.YELLOW)


def s_walk(ctx, T, d, t0=6.85):
    school(ctx, T, sign="WELCOME, PLAYERS!", sign_k=(T - 7.2) / 0.5)
    p = clamp((T - t0) / 1.15)
    x = lerp(40, 150, ease(p))
    KID.draw(ctx, x, GY, 0.82, "happy" if p < 1 else "shock", T, pose="walk" if p < 1 else "stand",
             walk_phase=T * 2.2, arms=("down", "down") if p < 1 else ("up", "up"), snap=snap_at(T, t0 + 1.15))
    st.name_pill(ctx, x, GY - 3.75 * U1 * 0.82, "You", size=22)


def s_blocks(ctx, T, d, t_word=9.07):
    land(ctx, lambda c: ss.wall(c, "#d8433a", ss.GROUND), fill="#d8433a")
    st.baseplate(ctx, GY)
    poke = T >= 8.85
    KID.draw(ctx, 330, GY, 1.35, keyed(T, [(0, "happy"), (t_word, "shock")]), T,
             arms=("point" if poke else "down", "down"), look=0.4, snap=snap_at(T, t_word))
    if T >= t_word:
        for i in range(5):                                          # studs pop under the finger
            k = T - t_word - i * 0.06
            if k > 0:
                ctx.new_sub_path()
                ctx.arc(560 + (i % 3) * 40 - 40, 560 + (i // 3) * 40, 14 * min(1.0, pop(k) + 0.05), 0, 2 * PI)
        ctx.set_source_rgba(1, 1, 1, 0.8)
        ctx.fill()
    st.sfx_word(ctx, 520, 330, "BLOCKS!", T - t_word, col=st.RED, size=78)
    st.sfx_word(ctx, 560, 470, "BOINK!", T - 8.86, col=st.YELLOW, size=44, tilt=0.12, seed=5)


# ================================================================ attendance (10.03 - 18.68)
def kids_row(ctx, T, expr="happy", look=0.0, y=GY, tags=True, xs=(150, 360, 570), snap=None):
    who = (LEO, PRIYA, P[5])
    for i, x in enumerate(xs):
        who[i].draw(ctx, x, y, 0.62, expr, T, look=look, arms=("down", "down"), snap=snap)
        if tags:
            st.name_pill(ctx, x, y - 3.75 * U1 * 0.62, NAMES[i], size=18)
    for x in xs:
        ss.desk(ctx, x, y + 6, 0.62)


def s_pebble(ctx, T, d):
    classroom(ctx, T, board="ATTENDANCE")
    PEBBLE.draw(ctx, 170, GY, 0.95, "happy", T, arms=("hold", "down"), look=0.4, snap=snap_at(T, 10.32))
    tablet(ctx, 240, GY - 150, 0.32, T)
    for i, x in enumerate((420, 590)):
        (LEO, PRIYA)[i].draw(ctx, x, GY, 0.62, "neutral", T, look=-0.5)
        ss.desk(ctx, x, GY + 6, 0.62)
    lbl(ctx, "MISS PEBBLE", 360, LBL_Y, 66, T, 10.32, bg=st.BLUE)


def list_screen(names, T, t0, me=None, step=0.3):
    def fn(c, x, y, w, h, TT):
        n = max(0, min(len(names), int((TT - t0) / step) + 1))
        st.player_list(c, x + 20, y + 20, names[:n], TT, s=(w - 40) / 300, me=me)
    return fn


def s_list(ctx, T, d, t0=10.96):
    classroom(ctx, T, board="")
    rise = ease(clamp((T - t0) / 0.3))
    ctx.save()
    ctx.translate(0, (1 - rise) * 500)
    style.block(ctx, 70, 300, 580, 520, 24, hexc("#1e2230"), 6)
    st.bold_text(ctx, "PLAYERS", 360, 350, 44, (1, 1, 1), shadow=False, stroke=0.0)
    for i, nm in enumerate(NAMES):
        k = T - (t0 + 0.25 + i * 0.28)
        if k < 0:
            continue
        yy = 420 + i * 78
        style.block(ctx, 100, yy - 30, 520, 62, 12, hexc("#3a3f55"), 3, gloss=False)
        st.face_icon(ctx, 140, yy + 1, 22, ("#c89f82", "#b98a6a", "#e6ddd6", "#f0c9a8", "#f0c9a8")[i],
                     "#2a1a14", expr="smirk")
        st.bold_text(ctx, nm, 180, yy, 32, (1, 1, 1), align="l", shadow=False, stroke=0.0,
                     scale=min(1.0, pop(k) + 0.05))
        if i < 4 and T >= t0 + 0.45 + i * 0.28:
            st.check_mark(ctx, 585, yy, 18, (T - t0 - 0.45 - i * 0.28) / 0.25)
    ctx.restore()
    lbl(ctx, "ATTENDANCE", 360, 220, 66, T, t0 + 0.1, bg=st.GREEN)


def s_pebble_cu(ctx, T, d, t0=12.95):
    st.burst(ctx, T, "#c8e6ff", "#2f6bd8", cy=560, spin=0.4)
    m, k = closeup(ctx, PEBBLE, keyed(T, [(0, "neutral"), (14.03, "shock")]), T, arms=("hold", "down"),
                   talk=talking("pebble", T), snap=snap_at(T, 14.03))
    tablet(ctx, *m(500, 760), 0.5 * k * 2.2, T, list_screen(NAMES, T, -10))
    txt = typed("ToiletDestroyer9000?", T, 13.30, 15)
    if txt:
        st.speech_bubble(ctx, 400, 215, txt, 40, 1.0, tail=(-1, 1))


def s_zoom_name(ctx, T, d, t0=14.03):
    st.void_bg(ctx, top="#2a2d50", bottom="#0d0f18", y0=0, y1=1280)
    for i, nm in enumerate(NAMES[:4]):
        yy = 170 + i * 72
        style.block(ctx, 80, yy, 560, 58, 12, hexc("#2b2f45"), 3, gloss=False)
        st.bold_text(ctx, nm, 130, yy + 29, 28, hexc("#7a80a0"), align="l", shadow=False, stroke=0.0)
        st.check_mark(ctx, 600, yy + 29, 16, 1.0)
    style.block(ctx, 40, 470, 640, 130, 24, hexc("#3a3f55"), 6)
    st.face_icon(ctx, 105, 535, 36, "#f0c9a8", "#4a2f22", expr="grin")
    sz = 44
    st.bold_text(ctx, "ToiletDestroyer9000", 380, 535, sz, (1, 1, 1), shadow=False, stroke=0.0,
                 scale=min(1.0, pop(T - t0) + 0.2))
    if T >= 15.0:
        k = clamp((T - 15.0) / 0.25)
        ctx.save()
        ctx.translate(360, 535)
        ctx.scale(1.0, 0.42)
        ctx.new_sub_path()
        ctx.arc(0, 0, 360, -PI / 2, -PI / 2 + 2 * PI * k)
        ctx.restore()
        ctx.set_source_rgb(*hexc("#ff3b4a"))
        ctx.set_line_width(12)
        ctx.stroke()
        st.arrow(ctx, 560, 840, 450, 640, k=ease(k))
        st.sfx_word(ctx, 330, 330, "9000?!", T - 15.0, col=st.RED, size=72)


def s_stare(ctx, T, d, t0=15.0):
    classroom(ctx, T, board="ATTENDANCE")
    turn = T >= t0 + 0.15
    for i, x in enumerate((120, 600)):
        (LEO, PRIYA)[i].draw(ctx, x, GY, 0.6, "laugh" if i == 0 else "shock", T, look=0.6 if x < 360 else -0.6,
                             arms=("point", "down") if (turn and i == 0) else ("down", "cover"),
                             snap=snap_at(T, t0 + 0.15))
        ss.desk(ctx, x, GY + 6, 0.6)
    KID.draw(ctx, 360, GY, 0.8, "forced", T, arms=("down", "down"), snap=snap_at(T, t0 + 0.15))
    ss.desk(ctx, 360, GY + 6, 0.8)
    st.name_pill(ctx, 360, GY - 3.75 * U1 * 0.8, "ToiletDestroyer9000", size=22, col=st.YELLOW)
    style.sweat(ctx, 430, GY - 2.9 * U1 * 0.8, 1.0, T)


def s_flashback(ctx, T, d, t0=15.99):
    st.night_bedroom(ctx, T, y_floor=1000)
    KID.draw(ctx, 250, GY, 0.5, "laugh", T, arms=("hold", "hold"), look=0.6)
    ss.desk(ctx, 470, GY, 1.15)
    st.monitor(ctx, 470, GY - 146, 0.5, T, lambda c, x, y, w, h, TT: (
        c.set_source_rgb(*hexc("#141a3e")), c.rectangle(x, y, w, h), c.fill(),
        st.bold_text(c, "NEW USERNAME:", x + w / 2, y + h * 0.3, h * 0.13, hexc("#9aa0b8"), shadow=False, stroke=0.0),
        st.bold_text(c, typed("ToiletDestroyer9000", TT, t0 + 0.2, 17), x + w / 2, y + h * 0.62, h * 0.12,
                     (1, 1, 1), shadow=False, stroke=0.0)))
    st.tint(ctx, (0.55, 0.42, 0.2), 0.25)
    lbl(ctx, "AGE 6", 360, 300, 80, T, t0 + 0.1, bg=st.UI_DARK, fg=st.YELLOW)


def s_cringe(ctx, T, d, t_word=18.03):
    st.burst(ctx, T, "#ffc4ec", "#c0307a", cy=560, spin=0.4)
    m, k = closeup(ctx, KID, "forced", T, arms=("cover", "down"), snap=snap_at(T, 17.25))
    style.sweat(ctx, *m(470, 470), 1.6 * k * 2, T)
    st.thought_cloud(ctx, 520, 260, 260, 190, T - 17.35, tail=(-1, 1))
    if T >= 17.5:
        KID.draw(ctx, 520, 330, 0.34, "laugh", T, arms=("up", "up"), shadow=False)
    lbl(ctx, "SIX.", 360, 900, 80, T, t_word, fg=st.YELLOW)


# ================================================================ the announcement (18.68 - 23.96)
def s_speaker(ctx, T, d, t0=18.68):
    classroom(ctx, T, board="ATTENDANCE")
    kick = clamp((T - t0) / 0.2)
    ss.pa_speaker(ctx, 360, 380, 0.95, T, crackle=1.0)
    for i, x in enumerate((150, 360, 570)):
        (LEO, KID, PRIYA)[i].draw(ctx, x, GY, 0.62, "shock", T, look=0.0, arms=("down", "down"),
                                  snap=snap_at(T, t0 + 0.1))
        ss.desk(ctx, x, GY + 6, 0.62)
    st.sfx_word(ctx, 560, 500, "KSSHH!", T - t0, col=st.YELLOW, size=56)
    if kick < 1:
        style.shake_lines(ctx, 360, 380, 160, 120, T, n=3, lw=8)


def s_stone(ctx, T, d, t_fri=19.94):
    st.burst(ctx, T, "#ffb3b3", "#c0303a", cy=560, spin=0.3)
    m, k = closeup(ctx, STONE, "smug", T, arms=("hold", "down"), talk=talking("stone", T))
    mx, my = m(560, 760)
    style.block(ctx, mx - 10 * k, my - 40 * k, 20 * k, 330 * k, 6, hexc("#3a3f55"), 4)        # the mic stand
    style.block(ctx, mx - 34 * k, my - 90 * k, 68 * k, 62 * k, 22 * k, hexc("#5a5f7a"), 4)
    if T >= t_fri:
        ctx.save()
        ctx.translate(560, 300)
        sc = 0.5 * min(1.0, pop(T - t_fri) + 0.05)
        ctx.scale(sc, sc)
        ss.calendar(ctx, 0, 0, 1.0, top="FRIDAY", big="5", col="#e8323a")
        ctx.restore()
    lbl(ctx, "FINAL EXAM", 360, 900, 72, T, 21.21, bg=st.RED)


def s_kids_shock(ctx, T, d, t0=21.59):
    st.burst(ctx, T, "#ffe27a", "#f29a2e", cy=560, spin=0.5)
    for i, (x, ch) in enumerate(((140, LEO), (360, KID), (580, PRIYA))):
        ch.draw(ctx, x, GY, 1.1, "scream" if i == 1 else "shock", T, arms=("up", "up"), snap=snap_at(T, t0 + 0.05))
    st.sfx_word(ctx, 360, 380, "THIS YEAR?!", T - t0 - 0.1, col=st.RED, size=60)


def s_paper(ctx, T, d, t_hp=23.0):
    classroom(ctx, T, board="")
    ss.desk(ctx, 360, GY + 6, 1.7)
    ctx.save()                                                          # the test paper standing on the desk
    ctx.translate(360, GY - 205)
    ctx.rotate(-0.06)
    style.block(ctx, -150, -190, 300, 200, 10, (1, 1, 1), 6)
    st.bold_text(ctx, "FINAL EXAM", 0, -150, 34, hexc("#e8323a"), shadow=False, stroke=0.05)
    for i in range(4):
        style.block(ctx, -120, -110 + i * 30, 240, 8, 4, hexc("#9ad0ff"), 0, gloss=False)
    ctx.restore()
    if T >= t_hp:
        k = clamp((T - t_hp) / 0.3)
        ctx.save()
        ctx.translate(0, 420)
        health(ctx, k, name="FINAL EXAM", y=0)
        ctx.restore()
        lbl(ctx, "HEALTH BAR?!", 360, 300, 74, T, 23.41, fg=st.YELLOW)


# ================================================================ summer deleted (23.96 - 30.43)
def panel_screen(red, lines):
    return lambda c, x, y, w, h, TT: ss.admin_screen(c, x, y, w, h, TT, red=red, lines=lines)


PANEL_LINES = ("Players: 412", "Chat bubbles: ON", "UPDATE: FRI 3 PM", "Summer: DELETE")


def s_panel(ctx, T, d):
    st.void_bg(ctx, top="#141a2e", bottom="#05060f", y0=0, y1=1280)
    st.monitor(ctx, 360, 860, 1.12, T, panel_screen(2 if T >= 24.43 else None, PANEL_LINES))
    lbl(ctx, "UPDATE SCHEDULED", 360, 260, 60, T, 24.43, bg=st.RED)


def s_friday3(ctx, T, d, t_three=25.93):
    st.burst(ctx, T, "#ffb3b3", "#c0303a", cy=560, spin=0.4)
    ss.calendar(ctx, 360, 420, 0.95, top="FRIDAY", big="5", col="#e8323a")
    if T >= t_three:
        sc = min(1.0, pop(T - t_three) + 0.05)
        st.big_clock(ctx, 360, 780, 120 * sc, 15.0, T)
        lbl(ctx, "3 P.M.", 560, 880, 64, T, 26.09, bg=st.UI_DARK, fg=st.YELLOW)


def s_summer(ctx, T, d, deleted_t=None):
    st.burst(ctx, T, "#fff6c4", "#8fd0ff", cy=560, spin=0.3)
    dk = clamp((T - deleted_t) / 0.35) if deleted_t is not None and T >= deleted_t else 0.0
    ss.summer_card(ctx, 360, 580, 1.15, T, deleted=dk)
    if deleted_t is None:
        st.sparkles(ctx, T, 360, 580, spread=330, n=10, seed=2, c=st.YELLOW)


def s_kid_deleted(ctx, T, d, t0=29.43):
    st.burst(ctx, T, "#ff8a8a", "#c0303a", cy=560, spin=0.9)
    m, k = closeup(ctx, KID, "scream", T, arms=("up", "up"), talk=talking("kid", T), snap=snap_at(T, t0 + 0.03))
    style.shake_lines(ctx, *m(360, 560), 300 * k, 260 * k, T, n=3, lw=9)
    st.speech_bubble(ctx, 470, 220, "DELETED?!", 58, T - t0, tail=(-1, 1))


# ================================================================ the final exam (30.43 - 37.48)
def s_doors(ctx, T, d, t0=30.43):
    gym(ctx, T, dark_k=0.35, doors=clamp((T - t0) / 0.6))
    for i, (x, ch) in enumerate(((150, LEO), (360, KID), (570, PRIYA))):
        ch.draw(ctx, x, GY, 0.7, "scared", T, look=0.0, arms=("down", "down"))
    lbl(ctx, "FRIDAY, 2:59 PM", 360, LBL_Y, 60, T, t0 + 0.1, bg=st.UI_DARK, fg=st.YELLOW)


def s_reveal(ctx, T, d, t0=31.18):
    gym(ctx, T, dark_k=0.55)
    k = ease(clamp((T - t0) / 0.7))
    ctx.save()
    ctx.rectangle(-100, -100, 920, GY + 6 + 100)
    ctx.clip()
    boss(ctx, T, s=0.66, y=GY + (1 - k) * 720, jaw=0.25 + 0.5 * k, rage=1.0)
    ctx.restore()
    if k >= 1:
        style.shake_lines(ctx, 360, 380, 330, 160, T, n=3, lw=10)
    lbl(ctx, "THE FINAL EXAM", 360, 200, 70, T, 31.9, bg=st.RED)


def s_scale(ctx, T, d, t0=32.52):
    gym(ctx, T, dark_k=0.4)
    boss(ctx, T, x=430, s=0.7, jaw=0.3)
    KID.draw(ctx, 130, GY, 0.42, "scared", T, arms=("up", "up"), snap=snap_at(T, t0 + 0.1))
    ctx.set_source_rgb(*hexc("#ffd84a"))                                # the 50 FT ruler
    style.block(ctx, 70, 300, 26, GY - 300, 6, hexc("#ffd84a"), 4)
    for i in range(6):
        style.block(ctx, 60, 300 + i * 136, 46, 8, 3, hexc("#ffd84a"), 2, gloss=False)
    lbl(ctx, "50 FT", 200, 250, 64, T, 32.89, bg=st.UI_DARK, fg=st.YELLOW)


def s_arms(ctx, T, d, t_word=34.14):
    gym(ctx, T, dark_k=0.45)
    boss(ctx, T, s=0.66, jaw=0.4 + 0.3 * math.sin(T * 12))
    lbl(ctx, "ARMS!", 360, 300, 90, T, t_word, fg=st.YELLOW)


def s_teeth(ctx, T, d, t0=34.71):
    gym(ctx, T, dark_k=0.5)
    chomp = 0.5 + 0.5 * math.sin((T - t0) * 22)
    boss(ctx, T, s=1.25, y=GY + 560, jaw=chomp)
    st.sfx_word(ctx, 360, 250, "CHOMP!", T - t0 - 0.05, col=st.RED, size=70)
    lbl(ctx, "TEETH!", 360, 880, 86, T, t0 + 0.05, fg=st.YELLOW)


def s_hp(ctx, T, d, t0=35.75):
    gym(ctx, T, dark_k=0.45)
    boss(ctx, T, s=0.56, jaw=0.2)
    fill = clamp((T - t0) / 0.7)
    health(ctx, fill, y=230)
    n = int(10000 * ease(fill))
    st.bold_text(ctx, f"{n:,} HP", 360, 340, 80, hexc("#ff4f5a"), scale=min(1.0, pop(T - t0) + 0.1))


# ================================================================ the swing (37.48 - 45.86)
def s_leap(ctx, T, d, t0=37.48):
    gym(ctx, T, dark_k=0.3)
    boss(ctx, T, x=520, s=0.55, jaw=0.6)
    p = clamp((T - t0) / 1.0)
    x, y = lerp(60, 260, p), GY - math.sin(PI * min(1.0, p * 1.3)) * 380
    KID.draw(ctx, x, y, 0.72, "determined", T, pose="jump", arms=("up", "up"))
    ss.eraser(ctx, x + 40, y - 3.3 * U1 * 0.72, 0.9, rot=-0.6)
    st.speed_lines(ctx, T, 360, 640, n=18, r0=260, r1=900, a=0.3)
    st.sfx_word(ctx, 200, 340, "JUMP!", T - t0 - 0.1, col=st.BLUE, size=58)


def s_swing(ctx, T, d, t0=38.48):
    st.burst(ctx, T, "#fff3a8", "#ff8a3d", cy=560, spin=1.0)
    m, k = closeup(ctx, KID, "scream", T, arms=("up", "up"), snap=snap_at(T, t0))
    ang = -1.6 + 2.2 * ease(clamp((T - t0 - 0.2) / 0.45))
    hx, hy = m(360, 560)
    ss.eraser(ctx, hx + math.cos(ang) * 260, hy - 40 + math.sin(ang) * 260, 1.5, rot=ang + PI / 2)
    st.sfx_word(ctx, 440, 620, "SWOOSH!", T - t0 - 0.45, col=st.BLUE, size=60)


def s_erased(ctx, T, d, t0=39.44):
    gym(ctx, T, dark_k=0.2)
    boss(ctx, T, s=0.62, jaw=1.0, erase=clamp((T - t0) / 0.7))
    for i in range(10):
        a = i * 0.63 + T
        r = (T - t0) * 420
        style.sparkle(ctx, 360 + math.cos(a) * r, 560 + math.sin(a) * r * 0.8, 24)
    st.stamp(ctx, 360, 560, "ERASED!", T - t0 - 0.05, size=120)


def s_defeated(ctx, T, d, t0=40.28):
    gym(ctx, T)
    st.tint(ctx, (0.05, 0.06, 0.1), 0.35)
    st.system_message(ctx, 360, 560, 1.3, ["FINAL EXAM", "DEFEATED!"], T - t0, T=T, typed=clamp((T - t0) / 0.7))
    st.confetti(ctx, T, t0 + 0.3, n=36)


def s_crown(ctx, T, d, t0=42.20):
    st.burst(ctx, T, "#fff1a8", "#f2b02e", cy=560, spin=0.6)
    landk = clamp((T - t0 - 0.05) / 0.35)
    m, k = closeup(ctx, KID, "stars" if landk >= 1 else "shock", T, arms=("up", "up"), snap=snap_at(T, t0 + 0.4))
    hx, hy = m(360, 560)
    ss.crown(ctx, hx, lerp(-120, hy - 0.85 * U1 * CU_S, ease(landk)), 0.5, T)
    lbl(ctx, "NEW ADMIN!", 360, 900, 76, T, 42.53, fg=st.YELLOW)


def s_admin_name(ctx, T, d, t0=43.11):
    st.burst(ctx, T, "#fff1a8", "#f2b02e", cy=560, spin=0.5)
    m, k = closeup(ctx, KID, keyed(T, [(0, "grin"), (43.9, "forced")]), T, arms=("up", "down"),
                   snap=snap_at(T, 43.9))
    hx, hy = m(360, 560)
    ss.crown(ctx, hx, hy - 0.85 * U1 * CU_S, 0.5, T)
    lbl(ctx, "[ADMIN]", 360, 195, 40, T, t0, bg=st.RED)
    lbl(ctx, "ToiletDestroyer9000", 360, 265, 50, T, t0 + 0.08, bg=st.UI_DARK, fg=st.YELLOW)
    if T >= 43.9:
        style.sweat(ctx, *m(470, 470), 1.4, T)


def s_cheer(ctx, T, d, t0=44.40):
    gym(ctx, T)
    for i, x in enumerate((80, 200, 520, 640)):
        P[i + 6].draw(ctx, x, GY, 0.6, "laugh", T, arms=("up", "up"), bob=1.5)
    KID.draw(ctx, 360, GY - 60, 0.72, "forced", T, arms=("up", "up"), pose="jump")
    ss.crown(ctx, 360, GY - 60 - 2.9 * U1 * 0.72, 0.22, T)
    st.confetti(ctx, T, t0, n=36)
    st.sfx_word(ctx, 360, 560, "TOILET DESTROYER!", T - t0 - 0.05, col=st.YELLOW, size=46)


def s_facepalm(ctx, T, d, t0=45.86):
    st.burst(ctx, T, "#e2c8ff", "#7a3fd8", cy=560, spin=0.3)
    m, k = closeup(ctx, KID, "forced", T, arms=("cover", "down"), talk=talking("kid", T), snap=snap_at(T, t0))
    hx, hy = m(360, 560)
    ss.crown(ctx, hx, hy - 0.85 * U1 * CU_S, 0.4, T)
    st.speech_bubble(ctx, 450, 215, "Change that name...", 40, T - t0 - 0.1, tail=(-1, 1))


def s_rename(ctx, T, d, t0=47.07):
    st.void_bg(ctx, top="#2a2d50", bottom="#0d0f18", y0=0, y1=1280)
    st.roblox_dialog(ctx, 360, 560, 1.3, T - t0, "Change Username", "ToiletDestroyer9000", button="SAVE",
                     col="#2f6bd8")
    if T >= 47.94:
        st.red_x(ctx, 360, 560, 120, (T - 47.94) / 0.25)
        lbl(ctx, "NAME TAKEN... BY YOU", 360, 880, 50, T, 48.1, bg=st.RED)


def s_command(ctx, T, d, t0=48.51):
    gym(ctx, T)
    st.tint(ctx, (0.05, 0.06, 0.1), 0.3)
    KID.draw(ctx, 360, GY, 1.2, "determined", T, arms=("point", "down"), talk=talking("kid", T))
    ss.crown(ctx, 360, GY - 3.25 * U1 * 1.2, 0.3, T)
    ss.command_bar(ctx, 360, 420, 560, "/summer", T, t0 + 0.15, cps=12)


def s_restored(ctx, T, d, t0=49.99):
    st.burst(ctx, T, "#fff6c4", "#ffb84a", cy=560, spin=0.5)
    r = clamp((T - t0) / 0.5)
    ss.summer_card(ctx, 360, 580, 1.15, T, deleted=1 - r, restored=r)
    st.sparkles(ctx, T, 360, 580, spread=330, n=14, seed=2, c=st.YELLOW)
    lbl(ctx, "RESTORED!", 360, 900, 84, T, 51.02, fg=st.GREEN)


def s_party(ctx, T, d, t0=51.02):
    school(ctx, T, sign="SUMMER!!!", sign_k=(T - t0) / 0.4)
    for i, (x, ch) in enumerate(((100, LEO), (230, PRIYA), (490, P[6]), (620, P[7]))):
        ch.draw(ctx, x, GY, 0.62, "laugh", T, arms=("up", "up"), bob=1.5)
    KID.draw(ctx, 360, GY - 40, 0.7, "laugh", T, arms=("up", "up"), pose="jump")
    st.confetti(ctx, T, t0, n=40)


# ================================================================ the twist (52.36 - 59.30)
def s_update(ctx, T, d, t0=52.36):
    st.night_bedroom(ctx, T, y_floor=1000)
    st.tint(ctx, (0.05, 0.06, 0.1), 0.45)
    st.roblox_dialog(ctx, 360, 560, 1.3, T - t0, "New update available", "Roblox School 2", button="INSTALL",
                     col="#2f6bd8")


def s_rs2(ctx, T, d, t2=55.51):
    school(ctx, T, s=0.62)
    st.tint(ctx, (0.1, 0.05, 0.2), 0.35)
    st.bold_text(ctx, "ROBLOX", 360, 250, 100, (1, 1, 1), scale=min(1.0, pop(T - 53.75) + 0.05))
    st.bold_text(ctx, "SCHOOL", 360, 360, 100, st.YELLOW, scale=min(1.0, pop(T - 54.63) + 0.05) if T >= 54.63
                 else 0.0)
    if T >= t2:
        st.impact_star(ctx, 360, 610, 170, T - t2, c1="#ffb3b3", c2="#e8323a")
        st.bold_text(ctx, "2", 360, 610, 260, st.RED, scale=pop(T - t2))


def s_install(ctx, T, d, t0=56.01):
    st.night_bedroom(ctx, T, y_floor=1000)
    st.tint(ctx, (0.05, 0.06, 0.1), 0.45)
    st.roblox_dialog(ctx, 360, 560, 1.3, 1.0, "New update available", "Roblox School 2", button="INSTALL",
                     col="#2f6bd8")
    kk = ease(clamp((T - t0) / 0.3))
    st.cursor(ctx, lerp(560, 400, kk), lerp(860, 680, kk), 1.5, click=1.0 if T >= t0 + 0.32 else 0.0)
    st.sfx_word(ctx, 520, 820, "CLICK!", T - t0 - 0.32, col=st.BLUE, size=50)


def s_mom(ctx, T, d, t0=56.77):
    st.burst(ctx, T, "#ffc4ec", "#c0307a", cy=560, spin=0.4)
    m, k = closeup(ctx, MOM, "happy", T, arms=("hold", "wave"), talk=talking("mom", T))

    def screen(c, x, y, w, h, TT):
        c.set_source_rgb(*hexc("#141a3e"))
        c.rectangle(x, y, w, h)
        c.fill()
        p = clamp((TT - t0) / 1.4)
        st.bold_text(c, "INSTALLING...", x + w / 2, y + h * 0.32, h * 0.16, (1, 1, 1), shadow=False, stroke=0.0)
        style.block(c, x + w * 0.1, y + h * 0.6, w * 0.8, h * 0.16, 6, hexc("#3a3f55"), 2, gloss=False)
        if p > 0:
            style.block(c, x + w * 0.1, y + h * 0.6, w * 0.8 * p, h * 0.16, 6, hexc("#4fd16a"), 2, gloss=False)
    tablet(ctx, *m(520, 800), 1.0 * k * 2.2 * 0.5, T, screen, rot=-0.08)
    st.speech_bubble(ctx, 420, 210, "Already pressed YES!", 40, T - t0, tail=(-1, 1))


def s_mom_scream(ctx, T, d, t0=58.49):
    st.burst(ctx, T, "#ff8a8a", "#c0303a", cy=560, spin=1.0)
    falling_blocks(ctx, T)
    m, k = closeup(ctx, KID, "scream", T, arms=("up", "up"), talk=talking("kid", T), snap=snap_at(T, t0 + 0.03))
    style.shake_lines(ctx, *m(360, 560), 300 * k, 260 * k, T, n=3, lw=9)
    label(ctx, "MOM!!", 360, 230, 96, fg=st.YELLOW, scale=pop(T - t0))


# ================================================================ shots
S = []


def shot(start, draw, keys, **kw):
    kw.setdefault("vignette", 0.15)
    S.append(dict(start=start, draw=draw, keys=keys, **kw))


def punch(t0, z0, c0, t_key, z1, c1, m=0.13):
    return [(t0, z0, c0), (t_key, z1, c1, m)]


C = (360, 700)
G = (360, 760)

shot(0.00, s_hook, [(0.0, 1.0, (360, 680)), (0.36, 1.08, (360, 660), 0.1)], shake=(0.36, 10),
     keep=[(70, 180, 650, 300)])
shot(0.83, at(s_become, 0.83), [(0.83, 1.0, G), (1.83, 1.04, G, 1.0)])
shot(1.83, at(s_roblox, 1.83), punch(1.83, 1.0, G, 2.25, 1.06, (360, 740), 0.1), shake=(0.42, 10),
     keep=[(60, 250, 660, 420)])
shot(2.90, at(s_days, 2.90), punch(2.90, 1.0, C, 3.37, 1.05, (360, 680), 0.1), keep=[(60, 230, 660, 920)])
shot(4.22, at(s_one, 4.22), punch(4.22, 1.0, G, 4.25, 1.06, (360, 720), 0.08), shake=(0.03, 10),
     keep=[(170, 150, 550, 600)])
shot(5.24, at(s_day1, 5.24), punch(5.24, 1.0, C, 5.59, 1.05, (360, 640), 0.12), keep=[(110, 420, 610, 800)])
shot(6.85, at(s_walk, 6.85), [(6.85, 1.0, G), (8.11, 1.05, (380, 760), 1.2)])
shot(8.11, at(s_blocks, 8.11), punch(8.11, 1.0, G, 9.07, 1.07, (420, 700), 0.1), shake=(0.96, 10),
     keep=[(380, 260, 660, 600)])
shot(10.03, at(s_pebble, 10.03), punch(10.03, 1.0, G, 10.32, 1.05, (340, 760), 0.12), whip=1)
shot(10.96, at(s_list, 10.96), punch(10.96, 1.0, C, 12.29, 1.04, (360, 640), 0.2), keep=[(70, 170, 650, 820)])
shot(12.95, at(s_pebble_cu, 12.95), punch(12.95, 1.0, C, 14.03, 1.06, (360, 660), 0.1), keep=[(150, 160, 660, 280)])
shot(14.03, at(s_zoom_name, 14.03), punch(14.03, 1.0, (360, 600), 15.0, 1.08, (360, 580), 0.1), shake=(0.97, 10),
     keep=[(40, 270, 680, 610)])
shot(15.00, at(s_stare, 15.00), punch(15.00, 1.0, G, 15.15, 1.05, (360, 760), 0.1), whip=-1)
shot(15.99, at(s_flashback, 15.99), [(15.99, 1.0, G), (17.23, 1.05, (360, 740), 1.2)], keep=[(230, 250, 490, 350)])
shot(17.23, at(s_cringe, 17.23), punch(17.23, 1.0, C, 18.03, 1.07, (360, 680), 0.1), keep=[(390, 160, 650, 360)])
shot(18.68, at(s_speaker, 18.68), punch(18.68, 1.0, G, 18.78, 1.05, (360, 700), 0.08), shake=(0.1, 9),
     keep=[(250, 290, 470, 470)])
shot(19.94, at(s_stone, 19.94), punch(19.94, 1.0, C, 21.21, 1.06, (360, 680), 0.12), keep=[(460, 210, 660, 390)])
shot(21.59, at(s_kids_shock, 21.59), punch(21.59, 1.0, G, 21.64, 1.06, (360, 740), 0.08), shake=(0.05, 12))
shot(22.48, at(s_paper, 22.48), punch(22.48, 1.0, G, 23.0, 1.06, (360, 720), 0.12), keep=[(100, 360, 620, 470)])
shot(23.96, at(s_panel, 23.96), [(23.96, 1.0, (360, 640)), (25.27, 1.05, (360, 660), 1.2)],
     keep=[(50, 200, 670, 860)])
shot(25.27, at(s_friday3, 25.27), punch(25.27, 1.0, C, 25.93, 1.05, (360, 660), 0.1), keep=[(200, 250, 660, 920)])
shot(26.51, at(s_summer, 26.51), [(26.51, 1.0, (360, 620)), (28.31, 1.05, (360, 600), 1.6)],
     keep=[(60, 370, 660, 790)])
shot(28.31, at(lambda c, T, d: s_summer(c, T, d, deleted_t=28.31), 28.31),
     punch(28.31, 1.05, (360, 600), 28.33, 1.1, (360, 590), 0.08), shake=(0.02, 12), keep=[(60, 370, 660, 790)])
shot(29.43, at(s_kid_deleted, 29.43), punch(29.43, 1.0, C, 29.46, 1.08, (360, 660), 0.08), shake=(0.03, 22),
     keep=[(250, 160, 660, 290)])
shot(30.43, at(s_doors, 30.43), [(30.43, 1.0, G), (31.18, 1.04, G, 0.7)], whip=1)
shot(31.18, at(s_reveal, 31.18), [(31.18, 1.0, (360, 700)), (32.52, 1.06, (360, 640), 1.2)], shake=(0.7, 12),
     keep=[(150, 150, 570, 1000)])
shot(32.52, at(s_scale, 32.52), punch(32.52, 1.0, G, 32.89, 1.04, (360, 740), 0.1), keep=[(60, 200, 340, 1000)])
shot(33.67, at(s_arms, 33.67), punch(33.67, 1.0, G, 34.14, 1.06, (360, 700), 0.1), keep=[(140, 230, 580, 1000)])
shot(34.71, at(s_teeth, 34.71), punch(34.71, 1.0, C, 34.75, 1.08, (360, 640), 0.08), shake=(0.04, 12),
     keep=[(150, 180, 570, 940)])
shot(35.75, at(s_hp, 35.75), punch(35.75, 1.0, G, 36.41, 1.05, (360, 700), 0.12), keep=[(100, 180, 620, 400)])
shot(37.48, at(s_leap, 37.48), [(37.48, 1.0, G), (38.48, 1.05, (340, 720), 0.8)], whip=-1)
shot(38.48, at(s_swing, 38.48), punch(38.48, 1.0, C, 38.95, 1.07, (360, 660), 0.08), shake=(0.47, 12))
shot(39.44, at(s_erased, 39.44), punch(39.44, 1.0, G, 39.47, 1.08, (360, 640), 0.08), shake=(0.03, 14),
     keep=[(90, 450, 630, 670)])
shot(40.28, at(s_defeated, 40.28), [(40.28, 1.0, (360, 640)), (42.2, 1.05, (360, 620), 1.5)],
     keep=[(60, 360, 660, 760)])
shot(42.20, at(s_crown, 42.20), punch(42.20, 1.0, C, 42.6, 1.06, (360, 660), 0.1))
shot(43.11, at(s_admin_name, 43.11), punch(43.11, 1.0, C, 43.9, 1.06, (360, 640), 0.12), keep=[(70, 180, 650, 250)])
shot(44.40, at(s_cheer, 44.40), [(44.40, 1.0, G), (45.86, 1.05, G, 1.2)], keep=[(140, 530, 580, 590)])
shot(45.86, at(s_facepalm, 45.86), punch(45.86, 1.0, C, 47.07, 1.05, (360, 680), 0.15), keep=[(240, 170, 660, 260)])
shot(47.07, at(s_rename, 47.07), punch(47.07, 1.0, (360, 640), 47.94, 1.06, (360, 640), 0.1), shake=(0.87, 10),
     keep=[(60, 420, 660, 920)])
shot(48.51, at(s_command, 48.51), [(48.51, 1.0, G), (49.99, 1.05, (360, 700), 1.2)], keep=[(80, 380, 640, 460)])
shot(49.99, at(s_restored, 49.99), punch(49.99, 1.0, (360, 640), 51.0, 1.05, (360, 640), 0.12),
     keep=[(60, 370, 660, 940)])
shot(51.02, at(s_party, 51.02), [(51.02, 1.0, G), (52.36, 1.05, G, 1.2)])
shot(52.36, at(s_update, 52.36), [(52.36, 1.0, (360, 640)), (53.75, 1.05, (360, 620), 1.2)],
     keep=[(60, 420, 660, 700)])
shot(53.75, at(s_rs2, 53.75), punch(53.75, 1.0, (360, 640), 55.51, 1.08, (360, 560), 0.1), shake=(1.76, 12),
     keep=[(70, 180, 650, 760)])
shot(56.01, at(s_install, 56.01), punch(56.01, 1.0, (360, 640), 56.33, 1.06, (360, 660), 0.08),
     keep=[(60, 420, 660, 880)])
shot(56.77, at(s_mom, 56.77), punch(56.77, 1.0, C, 57.52, 1.05, (360, 680), 0.15), keep=[(210, 170, 640, 260)])
shot(58.49, at(s_mom_scream, 58.49), punch(58.49, 1.0, C, 58.52, 1.1, (360, 660), 0.08), shake=(0.03, 24),
     keep=[(160, 160, 560, 300)])
SHOTS = S
_rw_draw, _rw_ov = st.rewind_shot(SHOTS, [56.4, 43.5, 31.8, 18.2, 8.9, 0.0])
shot(59.30, _rw_draw, [(59.30, 1.0, (360, 640))], overlay=_rw_ov, blur=False, closeup=True, keep=[])
HUD_SHOTS = (6.85, 10.03, 15.00, 18.68, 30.43, 44.40, 51.02)
for sh in S:
    if round(sh["start"], 2) in HUD_SHOTS:
        sh["overlay"] = hud_ov(sh["start"])
        sh["top"] = 345
S.sort(key=lambda sh: sh["start"])
for k, s in enumerate(SHOTS):
    s["end"] = SHOTS[k + 1]["start"] if k + 1 < len(SHOTS) else TOTAL

# ---------------------------------------------------------------- SFX (time, file, volume before SFX_GAIN)
# ~1.1 per second; 4 booms (DELETED, the boss rising, ERASED, MOM!).
SFX = [
    (0.03, "sting_low.wav", 0.9), (0.36, "pop.wav", 0.8), (0.83, "swish.wav", 0.5), (1.15, "sparkle.wav", 0.9),
    (1.6, "pop.wav", 0.5), (1.85, "pop.wav", 0.6), (2.25, "hit.wav", 1.0), (2.6, "pop.wav", 0.5),
    (2.95, "pop.wav", 0.6), (3.05, "pop.wav", 0.6), (3.15, "pop.wav", 0.6), (3.25, "pop.wav", 0.6),
    (3.37, "ding.wav", 0.8), (4.22, "hit.wav", 1.1), (4.51, "pop.wav", 0.8), (5.30, "pop.wav", 0.7),
    (5.59, "ding.wav", 0.8), (5.95, "pop.wav", 0.7), (6.9, "step.wav", 0.6), (7.25, "pop.wav", 0.6),
    (7.5, "step.wav", 0.6), (8.0, "pop.wav", 0.5), (8.86, "boing.wav", 0.8), (9.07, "pop.wav", 0.9),
    (9.4, "pop.wav", 0.5), (10.05, "swish.wav", 0.5), (10.32, "pop.wav", 0.8), (11.0, "swish.wav", 0.5),
    (11.21, "tick.wav", 0.6), (11.49, "tick.wav", 0.6), (11.77, "tick.wav", 0.6), (12.05, "tick.wav", 0.6),
    (12.33, "pop.wav", 0.6), (12.97, "pop.wav", 0.6), (13.3, "type_key.wav", 0.5), (13.7, "type_key.wav", 0.5),
    (14.03, "ding.wav", 0.8), (14.6, "pop.wav", 0.5), (15.0, "hit.wav", 1.0), (15.15, "whoosh.wav", 0.6),
    (15.5, "pop.wav", 0.5), (16.0, "swish.wav", 0.5), (16.2, "type_key.wav", 0.6), (16.6, "type_key.wav", 0.6),
    (17.0, "type_key.wav", 0.6), (17.35, "pop.wav", 0.7), (18.03, "pop.wav", 0.9), (18.68, "buzz.wav", 0.8),
    (18.9, "pop.wav", 0.5), (19.3, "tick.wav", 0.5), (19.94, "pop.wav", 0.8), (20.5, "tick.wav", 0.5),
    (21.21, "ding.wav", 0.8), (21.6, "hit.wav", 0.9), (22.0, "pop.wav", 0.5), (22.5, "swish.wav", 0.5),
    (23.0, "pop.wav", 0.8), (23.41, "hit.wav", 0.9), (24.0, "type_key.wav", 0.6), (24.43, "tick.wav", 0.6),
    (24.9, "tick.wav", 0.5), (25.3, "pop.wav", 0.8), (25.93, "tick.wav", 0.7), (26.09, "pop.wav", 0.7),
    (26.55, "sparkle.wav", 0.8), (27.1, "pop.wav", 0.5), (27.7, "tick.wav", 0.5), (28.31, "boom.wav", 1.4),
    (28.7, "pop.wav", 0.5), (29.43, "hit.wav", 1.1), (29.9, "pop.wav", 0.5), (30.43, "thud.wav", 0.9),
    (30.8, "tick.wav", 0.5), (31.18, "boom.wav", 1.3), (31.9, "pop.wav", 0.8), (32.52, "swish.wav", 0.5),
    (32.89, "pop.wav", 0.8), (33.3, "tick.wav", 0.5), (33.67, "swish.wav", 0.6), (34.14, "pop.wav", 0.9),
    (34.71, "hit.wav", 1.0), (35.1, "pop.wav", 0.6), (35.75, "tick.wav", 0.6), (35.95, "tick.wav", 0.6),
    (36.15, "tick.wav", 0.6), (36.45, "ding.wav", 0.9), (36.9, "pop.wav", 0.5), (37.5, "whoosh.wav", 0.8),
    (37.9, "pop.wav", 0.5), (38.48, "pop.wav", 0.6), (38.93, "swish.wav", 1.0), (39.44, "boom.wav", 1.5),
    (39.8, "sparkle.wav", 0.7), (40.28, "success.wav", 0.9), (40.7, "pop.wav", 0.5), (41.1, "pop.wav", 0.6),
    (41.6, "pop.wav", 0.5), (42.25, "swish.wav", 0.5), (42.6, "ding.wav", 0.9), (43.11, "pop.wav", 0.9),
    (43.5, "pop.wav", 0.5), (43.9, "pop.wav", 0.7), (44.45, "pop.wav", 0.7), (44.8, "pop.wav", 0.6),
    (45.2, "pop.wav", 0.6), (45.86, "pop.wav", 0.7), (46.5, "tick.wav", 0.5), (47.07, "pop.wav", 0.7),
    (47.5, "tick.wav", 0.5), (47.94, "buzz.wav", 0.8), (48.1, "pop.wav", 0.6), (48.7, "type_key.wav", 0.6),
    (48.9, "type_key.wav", 0.6), (49.1, "type_key.wav", 0.6), (49.3, "type_key.wav", 0.6), (49.6, "click.wav", 0.8),
    (49.99, "success.wav", 0.9), (50.5, "sparkle.wav", 0.6), (51.02, "pop.wav", 0.9), (51.4, "pop.wav", 0.6),
    (51.8, "pop.wav", 0.6), (52.36, "ding.wav", 0.9), (52.9, "tick.wav", 0.5), (53.75, "pop.wav", 0.9),
    (54.63, "pop.wav", 0.9), (55.51, "hit.wav", 1.2), (55.9, "pop.wav", 0.5), (56.33, "click.wav", 1.1),
    (56.77, "pop.wav", 0.7), (57.2, "tick.wav", 0.5), (57.6, "tick.wav", 0.5), (58.0, "ding.wav", 0.7),
    (58.49, "boom.wav", 1.4), (58.8, "pop.wav", 0.5), (59.30, "whip.wav", 0.9),
]

if __name__ == "__main__":
    import json
    import safezone
    import score
    json.dump([{"time": round(t, 3), "file": f, "volume": round(v * SFX_GAIN, 3)} for t, f, v in sorted(SFX)],
              open(sys.argv[2], "w"), indent=1)
    out_dir = os.path.dirname(os.path.abspath(sys.argv[2]))
    score.save_raw(os.path.join(out_dir, "music.wav"), score.music_score(TOTAL, SCORE, STINGS))
    engine.set_voice(os.path.join(out_dir, "voice.wav"))
    kw = {}
    if len(sys.argv) > 4:
        kw["frames"] = (int(sys.argv[3]), int(sys.argv[4]))
    safezone.fit(SHOTS, sys.modules[__name__])
    render(SHOTS, TOTAL, sys.argv[1], xfade=0.0, grain=2, fade_out=0.0, fade_in=0.0, **kw)

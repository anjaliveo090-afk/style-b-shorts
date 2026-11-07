"""LONG VIDEO (16:9): "What If the WHOLE SCHOOL Became Roblox? 😱" (script: scripts/whole_school_long.txt).

Voice + SRT: output/whole_school/voice.mp3 (464.2 s, the user's voice; no pauses over 0.6 s).
Format: engine 16:9 mode (1280x720 world rendered at 1920x1080), 30 fps, set3 motion (bumps, settling punch-ins).
Props: school_sets.py. One shot per SRT cue (long cues split), lip-sync only on character dialogue,
the Roblox HUD (top bar + Players + chat) on the in-game wide shots, a REWIND to the first frame at the end.
Scenes take (ctx, T, t0, **params): T = absolute time, t0 = the shot start.
Run (from animator/):
  python3 whole_school.py ../output/whole_school/clips/animation.mp4 ../output/whole_school/cues.json [f0 f1]"""
import os
os.environ["STYLEB_ASPECT"] = "16x9"
import math   # noqa: E402
import sys    # noqa: E402

import engine                     # noqa: E402
import school_sets as ss          # noqa: E402
import sets as st                 # noqa: E402
import style                      # noqa: E402
from engine import PI, clamp, ease, hexc, keyed, lerp, pop, render   # noqa: E402
from style import Block           # noqa: E402

engine.profile("set3")
engine.FPS = 30                   # long video: 30 fps (set3 motion constants kept)
engine.ENERGY = 3.0
engine.LIPSYNC = True
TOTAL = 464.6
SFX_GAIN = 0.24
MUSIC = dict(bpm=128, perc=0.6, dips=[(31.7, 34.6), (263.4, 270.8), (316.5, 326.8)])
GROUND = ss.GROUND
C = (640, 360)
U1 = Block.HW * 64

KID = style.KID
KID_ZOMBIE = Block("#2fbf8f", pants="#2b3f8f", skin="#8fd16a", hair="bowl", hair_col="#4a2f22", emblem="star",
                   emblem_col="#ffd84a", shoes="white")
LEO = Block("#ff8a3d", pants="#3b3f5a", skin="#c89f82", hair="spiky", hair_col="#2a1a14", outfit="tshirt")
PRIYA = Block("#9d5cff", pants="#2b2f45", skin="#b98a6a", hair="pony", hair_col="#1a1010", glasses=True, lashes=True)
EMMA = Block("#2b2f45", pants="#1e2230", skin="#f0c9a8", hair="long", hair_col="#1a1010", outfit="hoodie",
             lashes=True)
PEBBLE = Block("#7fb8ff", pants="#5a4fb0", skin="#e8c3a8", hair="bun", hair_col="#6a4a3a", outfit="cardigan",
               glasses=True, lashes=True, shoes="dark")
STONE = Block("#3b3f5a", pants="#2b2f45", skin="#d9a77f", hair="smooth", hair_col="#555566", outfit="suit",
              crown=True, accent="#e8323a", shoes="dark")
ADULTS = [Block("#5a5f7a", pants="#2b2f45", skin="#d9a77f", hair="smooth", hair_col="#888899", outfit="suit",
                beard="#888899", glasses=True, shoes="dark"),
          Block("#a0442a", pants="#3b3550", skin="#c89f82", hair="bun", hair_col="#aaaaaa", outfit="cardigan",
                glasses=True, lashes=True, shoes="dark"),
          Block("#2f6bd8", pants="#2b2f45", skin="#7a4a2e", hair=None, outfit="suit", beard="#2a1a14", shoes="dark"),
          Block("#6b8e23", pants="#3b3550", skin="#f0c9a8", hair="spiky", hair_col="#777777", outfit="hoodie",
                beard="#777777", shoes="dark")]
LUNCH = Block("#ffffff", pants="#c9cde0", skin="#c89f82", hair="bun", hair_col="#d8d8e4", outfit="robe",
              lashes=True, shoes="dark")
MOM, DAD = style.MOM, style.DAD
P = [style.crowd_member(i) for i in range(16)]

# ---------------------------------------------------------------- who speaks when (lip-sync, the user's rule)
DIALOGUE = {
    "kid": [(10.48, 13.38), (16.78, 18.82), (23.68, 26.98), (28.34, 29.42), (55.22, 57.18), (94.94, 95.84),
            (185.88, 188.58), (215.1, 217.92), (228.66, 231.96), (282.42, 283.14), (287.9, 289.74),
            (304.94, 305.92), (309.28, 311.72), (349.78, 355.14), (385.12, 387.04), (420.42, 424.3),
            (453.34, 453.86), (463.14, 463.54)],
    "leo": [(13.86, 14.38), (71.34, 71.78), (378.46, 379.0)],
    "pebble": [(63.18, 63.94), (70.56, 71.16), (72.1, 74.74), (165.5, 167.56)],
    "night": [(93.58, 94.76), (96.18, 97.98)],
    "dad": [(103.96, 106.28), (174.26, 175.66), (320.32, 321.4), (403.88, 404.64), (441.2, 442.2)],
    "priya": [(115.26, 118.9), (311.72, 316.2), (355.34, 358.58)],
    "stone": [(146.38, 147.42), (236.1, 241.02), (413.1, 414.34)],
    "lunch": [(182.32, 185.64)],
    "mom": [(207.6, 210.26), (218.48, 219.74), (233.2, 234.22), (391.32, 392.24), (444.88, 446.9),
            (452.2, 453.16), (461.42, 462.82)],
    "emma": [(283.14, 287.82), (289.74, 294.5)],
    "exam": [(333.7, 334.78), (373.38, 374.0)],
}
CAST = {"kid": KID, "leo": LEO, "pebble": PEBBLE, "night": ADULTS[0], "dad": DAD, "priya": PRIYA, "stone": STONE,
        "lunch": LUNCH, "mom": MOM, "emma": EMMA, "zombie": KID_ZOMBIE}


def talking(who, T):
    return who is not None and any(a <= T <= b for a, b in DIALOGUE.get(who, ()))


def snap_at(T, t0):
    return (T - t0) if T >= t0 else None


def typed(txt, T, t0, cps=24):
    return txt[:max(0, int((T - t0) * cps))]


def lbl(ctx, txt, x, y, size, T, t, bg=None, fg=(1, 1, 1)):
    if T >= t:
        st.label(ctx, txt, x, y, size, bg=bg, fg=fg, scale=pop(T - t))


def stand(ctx, who, x, expr, T, s=1.0, y=GROUND, ch=None, **kw):
    """A whole character standing on the ground line; talks when `who` has a line now."""
    (ch or CAST[who]).draw(ctx, x, y, s, expr, T, talk=talking(who, T), **kw)


def tag(ctx, x, s, name, y=GROUND, col=(1, 1, 1)):
    st.name_pill(ctx, x, y - 3.75 * U1 * s, name, size=max(20, int(24 * s)), col=col)


# ---------------------------------------------------------------- Roblox HUD (screen-space, in-game wide shots)
Y_, PK_, BL_, GR_, OR_, CY_, RD_ = "#ffd84a", "#ff5fb0", "#6fc3ff", "#4fd16a", "#ff8a3d", "#6fe6ff", "#ff4f5a"
CHAT_LOG = [
    (35.0, None, "You joined Roblox School", None), (40.0, "Leo", "bro we're BLOCKS", OR_),
    (48.0, "Priya", "finally. a leaderboard.", PK_), (61.0, None, "Ms. Pebble joined the game", None),
    (83.0, None, "Everyone teleported to Science", None), (90.0, "TaxGuy42", "who let a kid in", BL_),
    (101.0, "Dad", "omw buddy!!", Y_), (113.5, "Priya", "+10 XP +10 XP +10 XP", PK_),
    (136.0, "Leo", "RUN BRO", OR_), (147.7, None, "You were teleported to Detention", None),
    (158.5, "Leo", "what", OR_), (167.0, None, "You were muted", None), (178.0, None, "Lunch is served", None),
    (195.5, "BloxKid", "ZOMBIE!!!", PK_), (200.5, "TraderJoe", "trade? 10 robux", GR_),
    (204.4, None, "Supermom1987 joined the game", None), (224.0, "Leo", "LOL", OR_),
    (226.0, "Priya", "aww", PK_), (236.2, "[ADMIN] Stone", "ATTENTION STUDENTS", RD_),
    (322.8, None, "The gym is open", None), (345.0, "Leo", "56!", OR_), (345.4, "BloxKid", "52?", PK_),
    (347.0, None, "Summer deleted in 60 s", None), (359.0, "Priya", "42. Photosynthesis. 1776.", PK_),
    (363.0, "Everyone", "42 PHOTOSYNTHESIS 1776", Y_), (387.7, None, "Supermom1987 joined the game", None),
    (400.0, None, "Dad reached Stage 40", None), (407.8, None, "Final exam defeated", None),
    (409.7, None, "ToiletDestroyer9000 is the new admin", None), (417.5, "Everyone", "TOILET DESTROYER!!", Y_),
]


def draw_hud(ctx, T, players=412):
    st.roblox_topbar(ctx, T, players=players, y=46, left=56, right=1236)
    st.roblox_chat(ctx, CHAT_LOG, T, x=26, y=86, w=440, size=22)


# ================================================================ generic scenes
def s_cu(ctx, T, t0, who="kid", expr="happy", keys=None, bg=("#ffe27a", "#f29a2e"), bubble=None, btime=None,
         type_it=False, side=1, arms=("down", "down"), s=2.05, snap=None, prop=None, label=None, label_t=None,
         label_bg=None, ch=None, sfx_word=None, tint=None):
    """A reaction close-up: burst background, the character big (legs cut by the frame), an optional speech bubble
    (typed for dialogue), an optional prop drawn with the head position."""
    st.burst(ctx, T, bg[0], bg[1], cx=640, cy=330, spin=0.4)
    x = 450 if side > 0 else 830
    e = keyed(T, keys) if keys else expr
    sn = snap_at(T, snap) if snap is not None else None
    chr_ = ch or CAST[who]
    chr_.draw(ctx, x, 790, s, e, T, talk=talking(who, T), arms=arms, snap=sn, bob=0.5)
    hx, hy = x, 790 - 2.5 * U1 * s
    if prop:
        prop(ctx, T, hx, hy, s)
    if bubble:
        k = T - (btime if btime is not None else t0)
        txt = typed(bubble, T, btime if btime is not None else t0) if type_it else bubble
        if k >= 0 and txt:
            size = 46
            while size > 26 and st.text_width(ctx, txt, size) > 440:
                size -= 2
            bx = 880 if side > 0 else 400
            st.speech_bubble(ctx, bx, 170, txt, size, 1.0 if type_it else k, tail=(-side, 1))
    if label:
        lbl(ctx, label, 640, 640, 70, T, label_t if label_t is not None else t0, bg=label_bg)
    if sfx_word:
        txt, tw, col = sfx_word
        st.sfx_word(ctx, 1000 if side > 0 else 280, 470, txt, T - tw, col=col, size=60)
    if tint:
        st.tint(ctx, tint[0], tint[1])


def s_card(ctx, T, t0, word="DAY", num=1, sub=None, bg=("#e2c8ff", "#7a3fd8"), icon=None):
    """Chapter card: the DAY n write-on + a weekday pill."""
    st.burst(ctx, T, bg[0], bg[1], cx=640, cy=360, spin=0.3)
    st.day_write(ctx, word, num, 640, 330, T - t0, size=130, T=T)
    if sub:
        lbl(ctx, sub, 640, 520, 64, T, t0 + 0.45, bg=st.UI_DARK, fg=st.YELLOW)
    if icon:
        icon(ctx, T)


def s_big(ctx, T, t0, text="", sub=None, bg=("#ffe27a", "#f29a2e"), fg=(1, 1, 1), size=120, icon=None, stamp=None):
    """A punchy text card (5 DAYS, RULE 2, FOREVER...)."""
    st.burst(ctx, T, bg[0], bg[1], cx=640, cy=360, spin=0.4)
    if icon:
        icon(ctx, T)
    st.bold_text(ctx, text, 640, 330 if sub else 360, size, fg, scale=min(1.0, pop(T - t0) + 0.05))
    if sub:
        lbl(ctx, sub, 640, 500, 60, T, t0 + 0.25, bg=st.UI_DARK, fg=st.YELLOW)
    if stamp:
        st.stamp(ctx, 640, 360, stamp[0], T - stamp[1], size=150)


def s_ui(ctx, T, t0, kind="system", lines=("",), title="", msg="", button="OK", col="#e8323a", bg="dark",
         typed_k=True, extra=None, s=1.1):
    """A Roblox UI moment on a dimmed backdrop: system message / dialog / toast / teleport."""
    if bg == "dark":
        st.void_bg(ctx, top="#2a2d50", bottom="#0d0f18", y0=0, y1=720)
    elif bg == "game":
        st.game_sky(ctx)
        st.block_clouds(ctx, T, y0=40, y1=300, n=6)
        st.baseplate(ctx, GROUND)
        st.tint(ctx, (0.05, 0.06, 0.1), 0.45)
    elif callable(bg):
        bg(ctx, T)
        st.tint(ctx, (0.05, 0.06, 0.1), 0.45)
    if kind == "system":
        st.system_message(ctx, 640, 360, s, list(lines), T - t0, T=T,
                          typed=clamp((T - t0) / 0.9) if typed_k else 1.0)
    elif kind == "dialog":
        st.roblox_dialog(ctx, 640, 360, s, T - t0, title, msg, button=button, col=col)
    elif kind == "toast":
        st.game_toast(ctx, 640, 360, title, msg, T - t0, size=40)
    elif kind == "teleport":
        st.void_bg(ctx, top="#2a3a8a", bottom="#0d0f28", y0=0, y1=720)
        st.bold_text(ctx, msg, 640, 210, 70, (1, 1, 1), stroke=0.12, scale=min(1.0, pop(T - t0) + 0.05))
        ss.loading_ring(ctx, 640, 400, 70, T)
        st.bold_text(ctx, title, 640, 560, 36, hexc("#d8dbe6"), shadow=False, stroke=0.0)
    if extra:
        extra(ctx, T)


# ================================================================ intro + cold open
def s_title(ctx, T, t0, label=True):
    ss.school_ext(ctx, T, cx=640, s=0.9)
    stand(ctx, "kid", 640, keyed(T, [(0, "happy"), (1.75, "shock")]), T, s=0.62, arms=("up", "up") if T > 1.75 else
          ("down", "down"), snap=snap_at(T, 1.75))
    if label:
        lbl(ctx, "ROBLOX SCHOOL?!", 640, 672, 74, T, 1.75, fg=st.YELLOW)


# ---------------------------------------------------------------- the hook (rebuilt 2026-11-07: "hook boring hai")
# lessons.md rule 1: the stake in the first frame, a new picture every <= 0.8 s in the first 3 s.
# Word times (align_words): whole 0.46, school 0.82, became 1.36, Roblox 1.82, days 2.96, One 4.10, Friday 5.75,
# fighting 7.78, final 8.46, exam 8.83.
BLOCK_COLS = ("#ff4f5a", "#4f8bff", "#4fd16a", "#ffd84a", "#9d5cff", "#ff8a3d")


def falling_blocks(ctx, T, n=16, speed=620, seed=0):
    for i in range(n):
        x = (i * 97 + 40 + seed * 31) % 1300 - 10
        y = ((T * speed + i * 157) % 980) - 140
        sz = 38 + (i * 13) % 34
        ctx.save()
        ctx.translate(x, y)
        ctx.rotate(T * (1.5 + (i % 3)) + i)
        style.block(ctx, -sz / 2, -sz / 2, sz, sz, 6, hexc(BLOCK_COLS[i % len(BLOCK_COLS)]), 4)
        ctx.new_sub_path()
        ctx.arc(0, -sz * 0.18, sz * 0.18, 0, 2 * PI)
        ctx.set_source_rgba(1, 1, 1, 0.45)
        ctx.fill()
        ctx.restore()


def s_hk_face(ctx, T, t0):
    st.burst(ctx, T, "#ffd27a", "#ff4f2a", cx=640, cy=330, spin=0.8)
    falling_blocks(ctx, T)
    KID.draw(ctx, 640, 800, 2.15, "scream", T, arms=("up", "up"), snap=snap_at(T, 0.05), bob=0.6)
    style.shake_lines(ctx, 640, 330, 300, 260, T, n=3, lw=9)
    st.label(ctx, "ROBLOX SCHOOL?!", 640, 600, 80, fg=st.YELLOW, scale=min(1.0, pop(T) + 0.35))


def s_hk_slam(ctx, T, t0, t_land=0.82):
    st.game_sky(ctx)
    st.block_clouds(ctx, T, y0=40, y1=260, n=6)
    st.baseplate(ctx, GROUND)
    k = clamp((T - t0) / (t_land - t0))
    lift = 0.0 if T >= t_land else (1 - k * k) * 560
    if T < t_land:                                                     # its shadow grows on the ground
        style_k = 0.2 + 0.6 * k
        ctx.save()
        ctx.translate(640, GROUND + 20)
        ctx.scale(1, 0.12)
        ctx.new_sub_path()
        ctx.arc(0, 0, 520 * style_k, 0, 2 * PI)
        ctx.restore()
        ctx.set_source_rgba(0, 0, 0, 0.25 * k)
        ctx.fill()
    ss.school_ext(ctx, T, cx=640, s=0.9, lift=lift, ground=False)
    if T >= t_land:
        st.shockwave(ctx, 640, GROUND + 10, (T - t_land) / 0.5, r_max=760)
        st.dust(ctx, 640, GROUND + 20, clamp((T - t_land) / 0.5), n=10, spread=620, r=40)
        st.sfx_word(ctx, 1020, 200, "SLAM!", T - t_land, col=st.RED, size=78)
    for i, x in enumerate((150, 1130)):
        P[i].draw(ctx, x, GROUND + 60, 0.8, "shock" if T >= t_land else "neutral", T, arms=("up", "up") if
                  T >= t_land else ("down", "down"), look=0.5 if x < 640 else -0.5, snap=snap_at(T, t_land))


def normal_school(ctx, cx=640, s=0.9):
    """A plain, grey, everyday school (before it turns into Roblox)."""
    ctx.save()
    ctx.translate(cx, GROUND)
    ctx.scale(s, s)
    style.block(ctx, -560, -420, 1120, 420, 4, hexc("#b8b0a0"), 5, gloss=False)
    style.block(ctx, -150, -540, 300, 140, 4, hexc("#a8a090"), 5, gloss=False)
    for row in range(2):
        for i in (-4, -3, -2, 2, 3, 4):
            style.block(ctx, i * 110 - 40, -360 + row * 150, 80, 90, 2, hexc("#7a8a9a"), 3, gloss=False)
    style.block(ctx, -95, -230, 190, 230, 4, hexc("#6a5a4a"), 5, gloss=False)
    ctx.restore()


def s_hk_become(ctx, T, t0, t_sweep=1.36, dur=0.42):
    st.game_sky(ctx, top="#b8c4d8", bottom="#e0e6ee")
    st.baseplate(ctx, GROUND, col="#7a9a6a")
    normal_school(ctx)
    sx = lerp(-200, 1500, clamp((T - t_sweep) / dur))
    ctx.save()
    ctx.rectangle(-400, -400, sx + 400, 1600)
    ctx.clip()
    ss.school_ext(ctx, T, cx=640, s=0.9)
    ctx.restore()
    st.glow(ctx, sx, 360, 220, (1, 1, 0.85), 0.9)
    ctx.set_source_rgba(1, 1, 1, 0.85)
    ctx.rectangle(sx - 14, -100, 28, 1000)
    ctx.fill()
    st.sparkles(ctx, T, sx, 360, spread=300, n=14, seed=4, c=(1, 1, 1))


def s_hk_roblox(ctx, T, t0, t_word=1.85):
    ss.school_ext(ctx, T, cx=640, s=0.9)
    names = ("Leo", "Priya_99", "BloxKid", "xX_Ninja_Xx")
    for i, (x, nm) in enumerate(zip((130, 300, 980, 1150), names)):
        P[i + 3].draw(ctx, x, GROUND + 60, 0.72, "stars" if T >= t_word else "happy", T, arms=("up", "up"),
                      snap=snap_at(T, t_word))
        tag(ctx, x, 0.72, nm, y=GROUND + 60)
    st.bold_text(ctx, "ROBLOX?!", 640, 330, 170, st.YELLOW, scale=pop(T - t_word) if T >= t_word else 0.0,
                 tilt=-0.06)


def s_hk_days(ctx, T, t0):
    st.burst(ctx, T, "#e2c8ff", "#7a3fd8", cx=640, cy=330, spin=0.4)
    for i, day in enumerate(("MON", "TUE", "WED", "THU", "FRI")):
        k = T - (2.45 + i * 0.12)
        if k < 0:
            continue
        sc = 0.62 * (pop(k) if k < 0.6 else 1.0)
        ss.calendar(ctx, 160 + i * 240, 300, sc, top=day, big=str(i + 1), col="#e8323a" if i == 4 else "#4f8bff")
    if T >= 2.96:
        st.bold_text(ctx, "5 DAYS", 640, 600, 120, (1, 1, 1), scale=pop(T - 2.96))


def s_hk_one(ctx, T, t0, t_word=4.1):
    ss.school_ext(ctx, T, cx=640, s=0.85)
    if T >= t_word:
        st.impact_star(ctx, 640, 300, 230, T - t_word, c1="#fff3a8", c2="#ffb02e")
        st.bold_text(ctx, "1", 640, 300, 330, st.GOLD, scale=pop(T - t_word))
        st.label(ctx, "ONE SCHOOL", 640, 650, 70, fg=st.YELLOW, scale=pop(T - 4.35) if T >= 4.35 else 0.0)


def s_hk_friday(ctx, T, t0, t_word=5.75):
    st.burst(ctx, T, "#ffb3b3", "#c0303a", cx=640, cy=360, spin=0.6)
    wob = math.sin(T * 40) * 0.04 if T >= t_word else 0.0
    ctx.save()
    ctx.translate(640, 360)
    ctx.rotate(wob)
    ss.calendar(ctx, 0, 0, 1.45, top="FRIDAY", big="5", col="#e8323a")
    ctx.restore()
    if T >= t_word:
        st.stamp(ctx, 640, 420, "EXAM DAY!", T - t_word, size=120)


def s_hk_charge(ctx, T, t0, t_hit=7.78):
    ss.gym(ctx, T, dark_k=0.2)
    p = clamp((T - t0) / 1.6)
    for i, who in enumerate(("kid", "leo", "priya", "emma")):
        x = lerp(-120 - i * 150, 760 - i * 170, ease(p))
        stand(ctx, who, x, "scream" if T < t_hit else "determined", T, s=0.82, y=GROUND + 40, pose="run",
              walk_phase=T * 4 + i, arms=("up", "up"))
        ss.pencil(ctx, x + 70, GROUND - 260, 0.9, -1.2)
    st.speed_lines(ctx, T, 1000, 360, n=22, r0=240, r1=900, a=0.35)
    st.sfx_word(ctx, 640, 150, "CHAAARGE!", T - t0 - 0.1, col=st.RED, size=76)
    if T >= t_hit:
        st.flash(ctx, 0.6 * (1 - clamp((T - t_hit) / 0.25)))


def s_hk_boss(ctx, T, t0, t_rise=8.2, t_roar=8.46):
    k = clamp((T - t_rise) / 0.3)
    roar = clamp((T - t_roar) / 0.12) * (1.0 if T < 9.3 else 0.6)
    boss_gym(ctx, T, boss_x=640, boss_s=0.6, jaw=roar, rage=1.0, dark_k=0.55)
    if k < 1:                                                          # rising from the floor
        ss.gym(ctx, T, dark_k=0.55)
        ctx.save()
        ctx.rectangle(-300, -300, 1900, GROUND + 330)
        ctx.clip()
        ss.exam_boss(ctx, 640, GROUND + 20 + (1 - ease(k)) * 700, 0.6, T, jaw=0.2, rage=1.0)
        ctx.restore()
    if T >= t_roar:
        style.shake_lines(ctx, 640, 200, 420, 200, T, n=3, lw=10)
        st.label(ctx, "THE FINAL EXAM", 640, 600, 76, bg=st.RED, scale=pop(T - t_roar))
    if T >= 8.83:
        ctx.save()
        ctx.translate(0, -40 * (1 - clamp((T - 8.83) / 0.2)))
        health(ctx, 1.0)
        ctx.restore()


def s_school_wide(ctx, T, t0, sign=None, sign_t=0.0, label=None, label_t=None, kid=None, crowd=False, bell=None,
                  walk=None, s=0.9, cx=640):
    ss.school_ext(ctx, T, cx=cx, s=s, sign=sign, sign_k=(T - sign_t) / 0.5 if sign else 1.0, bell_T=bell)
    if crowd:
        for i, x in enumerate((140, 250, 1030, 1140)):
            P[i].draw(ctx, x, GROUND + 40, 0.7, "happy", T, arms=("wave", "down"), look=0.4 if x < 640 else -0.4)
    if walk:
        p = clamp((T - walk[0]) / walk[1])
        x = lerp(-80, 560, ease(p))
        stand(ctx, "kid", x, "happy" if p < 1 else "shock", T, s=0.75, y=GROUND + 50,
              pose="walk" if p < 1 else "stand", walk_phase=T * 2, arms=("down", "down") if p < 1 else ("up", "up"))
    elif kid:
        stand(ctx, "kid", 640, kid, T, s=0.7, y=GROUND + 50, arms=("up", "up") if kid == "shock" else ("down", "down"))
    if label:
        lbl(ctx, label, 640, 672, 70, T, label_t if label_t is not None else t0, fg=st.YELLOW)


def boss_gym(ctx, T, boss_x=900, boss_s=0.62, jaw=0.0, rage=0.0, erase=0.0, dark_k=0.15, hp=None):
    ss.gym(ctx, T, dark_k=dark_k)
    ss.exam_boss(ctx, boss_x, GROUND + 20, boss_s, T, jaw=jaw, rage=rage, erase_k=erase)
    if hp is not None:
        health(ctx, hp)


def health(ctx, frac, name="FINAL EXAM"):
    ctx.save()
    ctx.translate(280, -200)
    st.health_bar(ctx, frac, name=name, y=272)
    ctx.restore()


def s_fight(ctx, T, t0, phase="class"):
    """The gym battle: the class (pencils up) facing the final exam."""
    boss_gym(ctx, T, boss_x=930, boss_s=0.6, jaw=0.3 + 0.3 * math.sin(T * 6), rage=1.0)
    xs = (110, 240, 370, 500)
    for i, (who, x) in enumerate(zip(("kid", "leo", "priya", "emma"), xs)):
        stand(ctx, who, x, "determined", T, s=0.72, arms=("punch", "up"), bob=1.2)
    if phase == "class":
        lbl(ctx, "THE FINAL EXAM", 640, 100, 70, T, 8.14, bg=st.RED)


def s_coldopen(ctx, T, t0):
    boss_gym(ctx, T, boss_x=1000, boss_s=0.55, jaw=0.4, rage=1.0)
    stand(ctx, "kid", 380, "scream", T, s=0.95, arms=("point", "up"))
    stand(ctx, "leo", 150, "shock", T, s=0.85, arms=("up", "up"))
    if talking("kid", T):
        st.speech_bubble(ctx, 520, 150, "LEO, THE ERASER!", 46, T - t0, tail=(-1, 1))


def eraser_slot(ctx, T, sel=1, cx=640, y=640):
    items = [lambda c, x, y, sz: ss.pencil(c, x, y, sz / 120, -0.6),
             lambda c, x, y, sz: ss.eraser(c, x, y, sz / 150, -0.3),
             lambda c, x, y, sz: ss.juice_box(c, x, y + 6, sz / 140)]
    st.hotbar(ctx, y, items, sel=sel, T=T, cx=cx)


# ================================================================ Sunday night
def s_bedroom(ctx, T, t0, clock=None, kid="tired", talk_bubble=None, glow=0.0, lights_out=None, paper=False):
    lights = 1.0 if lights_out is None else 1.0 - clamp((T - lights_out) / 0.4)
    ss.bedroom_ls(ctx, T, lights=1.0)
    stand(ctx, "kid", 500, kid, T, s=0.95, arms=("hold", "point"), pose="sit", look=0.5)
    st.tablet(ctx, 700, GROUND - 260, 0.42, T)
    if glow > 0:
        st.glow(ctx, 700, GROUND - 260, 300, (0.4, 0.8, 1.0), glow)
    if clock is not None:
        st.big_clock(ctx, 1080, 160, 80, clock, T)
        lbl(ctx, "11 P.M.", 1080, 290, 50, T, t0 + 0.2, bg=st.UI_DARK, fg=st.YELLOW)
    if paper:
        ss.homework(ctx, 330, 360, 0.75, text="0/20")
    if talk_bubble and talking("kid", T):
        st.speech_bubble(ctx, 860, 180, talk_bubble, 40, T - t0, tail=(-1, 1))
    if lights < 1:
        st.tint(ctx, (0.0, 0.0, 0.03), 0.85 * (1 - lights))


def s_homework(ctx, T, t0):
    ss.bedroom_ls(ctx, T)
    ss.homework(ctx, 640, 380, 1.15, text="0/20" if T > t0 + 0.6 else None)
    st.sfx_word(ctx, 920, 220, "BLANK!", T - t0 - 0.6, col=st.RED, size=60)


def tablet_screen(lines, prog=None, prog_t=0.0, title="SYSTEM"):
    def fn(c, x, y, w, h, TT):
        c.set_source_rgb(*hexc("#141a3e"))
        c.rectangle(x, y, w, h)
        c.fill()
        st.bold_text(c, title, x + w / 2, y + h * 0.16, h * 0.09, hexc("#6fc3ff"), shadow=False, stroke=0.0)
        for i, ln in enumerate(lines):
            st.bold_text(c, ln, x + w / 2, y + h * (0.4 + i * 0.16), h * 0.1, (1, 1, 1), shadow=False, stroke=0.0)
        if prog is not None:
            f = clamp((TT - prog_t) / prog)
            c.set_source_rgb(*hexc("#2c3350"))
            c.rectangle(x + w * 0.1, y + h * 0.78, w * 0.8, h * 0.08)
            c.fill()
            c.set_source_rgb(*hexc("#4fd16a"))
            c.rectangle(x + w * 0.1, y + h * 0.78, w * 0.8 * f, h * 0.08)
            c.fill()
    return fn


def s_tablet(ctx, T, t0, lines=("REQUEST RECEIVED",), prog=None):
    st.void_bg(ctx, top="#1b1f4a", bottom="#05060f", y0=0, y1=720)
    st.glow(ctx, 640, 380, 520, (0.3, 0.6, 1.0), 0.5)
    st.tablet(ctx, 640, 380, 1.35, T, fn=tablet_screen(lines, prog, t0 + 0.3))


def s_lightsout(ctx, T, t0):
    ss.home_street(ctx, T, night=1.0, lit=1.0)
    k = clamp((T - t0 - 0.8) / 1.2)
    st.tint(ctx, (0, 0, 0.05), 0.75 * k)
    st.sfx_word(ctx, 640, 200, "CLICK", T - t0 - 0.8, col=st.YELLOW, size=56)


# ================================================================ Day 1: arriving
def s_blocks(ctx, T, t0):
    red = hexc("#d8433a")
    style.block(ctx, -100, -100, 1500, 1000, 0, red, 5, gloss=False)
    ss.studs(ctx, -100, -100, 1400, 900, red, step=90, r=26)
    for i in range(5):
        x = (i * 290 + T * 40) % 1400 - 60
        style.sparkle(ctx, x, 140 + (i % 3) * 180, 40 + 10 * math.sin(T * 5 + i))
    stand(ctx, "kid", 640, "stars", T, s=1.7, y=GROUND + 300, arms=("up", "point"))
    lbl(ctx, "PLASTIC!", 640, 110, 80, T, t0 + 1.6, fg=st.YELLOW)


def s_crowd_tags(ctx, T, t0):
    ss.school_ext(ctx, T, cx=640, s=0.9)
    names = ("xX_Ninja_Xx", "BloxKid", "PizzaLover", "Priya_99", "CoolGuy12", "Builder_Bob")
    for i, (x, nm) in enumerate(zip((120, 330, 540, 750, 960, 1170), names)):
        P[i + 2].draw(ctx, x, GROUND + 50, 0.72, "happy", T, arms=("wave", "down") if i % 2 else ("down", "down"))
        if T >= t0 + 0.3 + i * 0.12:
            tag(ctx, x, 0.72, nm, y=GROUND + 50)


def s_hall(ctx, T, t0, action="look", sign=None, label=None, label_t=None):
    ss.hallway(ctx, T, sign=sign)
    if action == "look":
        stand(ctx, "kid", 560, "neutral", T, s=0.95, arms=("point", "down"), look=-0.3)
    elif action == "run_slow":
        stand(ctx, "kid", 400 + (T - t0) * 25, "determined", T, s=0.95, pose="run", walk_phase=T * 0.6,
              arms=("up", "up"))
        st.number_counter(ctx, 900, 140, 0.8, 16, T, col="#ff4f5a", prefix="SPEED: ")
    elif action == "sprint":
        p = clamp((T - t0) / 2.6)
        stand(ctx, "kid", lerp(-100, 1100, p), "laugh", T, s=0.95, pose="run", walk_phase=T * 5, arms=("up", "up"),
              lean=0.3)
        st.speed_lines(ctx, T, 640, 360, n=24, r0=260, r1=900, a=0.4)
        st.sfx_word(ctx, 640, 150, "ZOOOM!", T - t0 - 0.2, col=st.BLUE, size=70)
    if label:
        lbl(ctx, label, 640, 600, 70, T, label_t if label_t is not None else t0, bg=st.RED)


def s_inventory(ctx, T, t0, items=("pencil", "eraser", "juice"), k_times=None, sel=None, extra=None, label=None,
                label_t=None, bg="hall"):
    if bg == "hall":
        ss.hallway(ctx, T)
        st.tint(ctx, (0.05, 0.06, 0.1), 0.45)
    else:
        st.void_bg(ctx, top="#1b1f4a", bottom="#05060f", y0=0, y1=720)
    k_items = None if k_times is None else [T - t for t in k_times]
    ss.inventory(ctx, 640, 380, 1.15 if extra is None else 0.95, list(items), k_items=k_items, sel=sel,
                 extra_k=None if extra is None else T - extra, T=T)
    if label:
        lbl(ctx, label, 640, 120, 72, T, label_t if label_t is not None else t0, fg=st.YELLOW)


def s_juice_q(ctx, T, t0):
    st.void_bg(ctx, top="#3a1d5a", bottom="#0d0618", y0=0, y1=720)
    st.glow(ctx, 640, 380, 420, (0.8, 0.4, 1.0), 0.45)
    ss.juice_box(ctx, 470, 400, 2.2, rot=math.sin(T * 2) * 0.08)
    ss.calendar(ctx, 900, 380, 1.0, top="FRIDAY", big="?")


# ================================================================ classroom
SEATS = [(260, 0), (480, 1), (800, 2), (1020, 3)]


def class_scene(ctx, T, t0, board="", teacher=True, teacher_expr="happy", students=None, focus_kid="neutral",
                list_k=None, hi=None, bubbles=(), poof_t=None, empty=False, heads_t=None, wall="#8fd0e8",
                clock_h=9.0, teacher_x=170, kid_x=640, label=None, label_t=None, mute=False, xp=None):
    ss.classroom(ctx, T, board=board, clock_h=clock_h, wall_col=wall)
    look = clamp((T - heads_t) / 0.2) if heads_t is not None else 0.0
    people = students if students is not None else [("leo", 420), ("priya", 860), ("emma", 1090)]
    gone = poof_t is not None and T >= poof_t + 0.15
    for who, x in people:
        if gone and who != "kid":
            continue
        e = "shock" if look > 0 else ("happy" if who != "emma" else "neutral")
        stand(ctx, who, x, e, T, s=0.78, y=GROUND + 30, look=-0.6 if (look and x > 640) else (0.6 if look else 0))
        ss.desk(ctx, x, GROUND + 40, 0.78)
    if not (gone and False):
        stand(ctx, "kid", kid_x, focus_kid, T, s=0.8, y=GROUND + 30)
        ss.desk(ctx, kid_x, GROUND + 40, 0.8)
    if teacher and not gone:
        stand(ctx, "pebble", teacher_x, teacher_expr, T, s=0.9, y=GROUND + 20, arms=("point", "down"))
    if poof_t is not None:
        for who, x in people + ([("pebble", teacher_x)] if teacher else []):
            if 0 <= T - poof_t < 0.45:
                st.poof(ctx, x, GROUND - 120, 90, (T - poof_t) / 0.45)
    for (who_x, txt, tt) in bubbles:
        if T >= tt:
            st.speech_bubble(ctx, who_x, 250, txt, 34, T - tt, tail=(0, 1))
    if mute:
        st.speech_bubble(ctx, kid_x, 360, "...", 54, 1.0, tail=(0, 1))
    if xp:
        for i, tt in enumerate(xp):
            if 0 <= T - tt < 1.2:
                st.bold_text(ctx, "+10 XP", 860 + i * 40, 280 - (T - tt) * 120, 40, st.GREEN,
                             scale=min(1.0, pop(T - tt) + 0.1))
    if list_k is not None:
        names = ["Shadow Ninja", "Pizza Lover", "Toilet Destroyer 9000", "Priya_99", "BloxKid"]
        ctx.save()
        ctx.translate(840, 140)
        st.player_list(ctx, 0, 0, names, T, s=1.0, me=hi)
        ctx.restore()
    if label:
        lbl(ctx, label, 640, 110, 70, T, label_t if label_t is not None else t0, bg=st.UI_DARK, fg=st.YELLOW)


def s_flashback6(ctx, T, t0):
    ss.bedroom_ls(ctx, T)
    stand(ctx, "kid", 520, "laugh", T, s=0.55, arms=("hold", "hold"), pose="sit")
    st.monitor(ctx, 760, GROUND - 210, 0.55, T, lambda c, x, y, w, h, TT: (
        c.set_source_rgb(*hexc("#141a3e")), c.rectangle(x, y, w, h), c.fill(),
        st.bold_text(c, "USERNAME:", x + w / 2, y + h * 0.3, h * 0.12, hexc("#9aa0b8"), shadow=False, stroke=0.0),
        st.bold_text(c, typed("ToiletDestroyer9000", TT, t0 + 0.3, 16), x + w / 2, y + h * 0.6, h * 0.11,
                     (1, 1, 1), shadow=False, stroke=0.0)))
    lbl(ctx, "AGE 6", 300, 120, 70, T, t0 + 0.2, bg=st.UI_DARK, fg=st.YELLOW)


def s_bell(ctx, T, t0, ring=True):
    st.burst(ctx, T, "#fff1a8", "#f2b02e", cx=640, cy=330)
    ss.school_bell(ctx, 640, 380, 1.6, (T - t0) if ring else None)
    if ring:
        st.sfx_word(ctx, 960, 200, "RIIING!", T - t0, col=st.RED, size=64)
    else:
        st.bold_text(ctx, "?", 900, 220, 140, st.YELLOW, scale=min(1.0, pop(T - t0) + 0.1))


def s_adults(ctx, T, t0, focus=None, board="SCIENCE"):
    ss.classroom(ctx, T, board=board, wall_col="#b8c4d8")
    for i, x in enumerate((180, 420, 860, 1100)):
        expr = "cold" if i != 0 else ("angry" if talking("night", T) else "cold")
        ADULTS[i].draw(ctx, x, GROUND + 30, 0.86, expr, T, talk=talking("night", T) and i == 0,
                       arms=("point", "down") if (i == 0 and focus == "point") else ("down", "down"))
        ss.desk(ctx, x, GROUND + 40, 0.86)
    stand(ctx, "kid", 640, keyed(T, [(0, "neutral"), (t0 + 0.4, "shock")]), T, s=0.62, y=GROUND + 30)
    ss.desk(ctx, 640, GROUND + 40, 0.62)


def s_cu_adult(ctx, T, t0, bubble="You're late, new guy.", expr="cold"):
    s_cu(ctx, T, t0, who="night", expr=expr, bg=("#c4c8e8", "#4a4f8a"), bubble=bubble, type_it=True,
         arms=("point", "down"))


# ================================================================ parking lot
def s_parking(ctx, T, t0, stage=1, dad="wave", label=None, label_t=None, night=0.0):
    ss.parking_obby(ctx, T, stage=stage)
    if dad == "wave":
        stand(ctx, "dad", 200, "happy", T, s=0.62, y=GROUND - 50, arms=("wave", "down"))
    elif dad == "jump":
        p = ((T - t0) * 0.9) % 1
        x = lerp(80, 290, p)
        y = GROUND - 70 - math.sin(PI * p) * 140
        stand(ctx, "dad", x, "determined", T, s=0.6, y=y, pose="jump", arms=("up", "up"))
    elif dad == "sweat":
        stand(ctx, "dad", 300, "worried", T, s=0.62, y=GROUND - 110, arms=("up", "down"))
        style.sweat(ctx, 350, GROUND - 330, 1.2, T)
    elif dad == "sleep":
        stand(ctx, "dad", 520, "sleepy", T, s=0.62, y=GROUND - 110, arms=("down", "down"), pose="sit")
        for i in range(3):
            zz = (T * 0.8 + i * 0.33) % 1
            st.bold_text(ctx, "Z", 600 + zz * 80, GROUND - 330 - zz * 120, 30 + i * 8, (1, 1, 1),
                         scale=1.0 - zz * 0.3)
    if night > 0:
        st.tint(ctx, (0.05, 0.05, 0.25), 0.45 * night)
    if label:
        lbl(ctx, label, 640, 120, 74, T, label_t if label_t is not None else t0, fg=st.YELLOW)


def s_clock(ctx, T, t0, h0=15.0, h1=15.0, label=None, bg=("#bfe3ff", "#2f6bd8")):
    st.burst(ctx, T, bg[0], bg[1], cx=640, cy=360, spin=0.3)
    st.big_clock(ctx, 640, 360, 210, lerp(h0, h1, clamp((T - t0) / 1.0)), T)
    if label:
        lbl(ctx, label, 640, 640, 64, T, t0 + 0.2, bg=st.UI_DARK, fg=st.YELLOW)


def s_walkhome(ctx, T, t0):
    ss.home_street(ctx, T, sunset=1.0)
    p = clamp((T - t0) / 1.2)
    stand(ctx, "kid", lerp(200, 900, p), "sad", T, s=0.8, y=GROUND + 30, pose="walk", walk_phase=T * 1.6)


# ================================================================ Day 2: the rules
def s_rules(ctx, T, t0):
    st.burst(ctx, T, "#e2c8ff", "#7a3fd8", cx=640, cy=360, spin=0.3)
    style.block(ctx, 380, 120, 520, 520, 26, hexc("#f4e2b8"), 7)
    st.bold_text(ctx, "THE RULES", 640, 190, 64, hexc("#8a5a3a"), outline=(1, 1, 1), shadow=False)
    for i, r in enumerate(("1. RIGHT ANSWER = XP", "2. NO RUNNING", "3. CHAT BUBBLES")):
        if T >= t0 + 0.3 + i * 0.25:
            st.bold_text(ctx, r, 640, 300 + i * 100, 40, hexc("#2b2f45"), outline=None, shadow=False, stroke=0.0,
                         scale=min(1.0, pop(T - t0 - 0.3 - i * 0.25) + 0.05))


def s_levelup(ctx, T, t0, n0=1, n1=99, who="priya", label="LEVEL UP!"):
    st.burst(ctx, T, "#b8ffb0", "#2e9c46", cx=640, cy=330, spin=0.6)
    CAST[who].draw(ctx, 640, 780, 1.6, "smug" if who == "priya" else "happy", T, arms=("up", "up"),
                   talk=talking(who, T))
    st.glow(ctx, 640, 360, 380, (1, 0.9, 0.4), 0.5)
    n = int(lerp(n0, n1, ease(clamp((T - t0) / 1.6))))
    ss.level_pill(ctx, 640, 120, n, s=1.4, col="#2e9c46")
    if label:
        st.bold_text(ctx, label, 1010, 300, 64, st.YELLOW, scale=min(1.0, pop(T - t0) + 0.05))


def s_glow(ctx, T, t0):
    st.void_bg(ctx, top="#3a2a10", bottom="#0d0806", y0=0, y1=720)
    st.glow(ctx, 640, 380, 520, (1, 0.85, 0.3), 0.85)
    stand(ctx, "priya", 640, "stars", T, s=1.3, y=GROUND + 120, arms=("up", "up"))
    st.sparkles(ctx, T, 640, 330, spread=420, n=18, seed=3, c=st.YELLOW)
    ss.level_pill(ctx, 640, 90, 99, s=1.2, col="#ffcc33")


def s_still(ctx, T, t0, n=1):
    st.void_bg(ctx, top="#4a4f6a", bottom="#1a1d2a", y0=0, y1=720)
    stand(ctx, "kid", 640, "sad" if n == 1 else "cold", T, s=1.5, y=GROUND + 120)
    ss.level_pill(ctx, 640, 120, 1, s=1.2, col="#8a90a8")


def s_purchase(ctx, T, t0, mode="card"):
    st.burst(ctx, T, "#c4d8ff", "#2f3f9a", cx=640, cy=360, spin=0.4)
    if mode == "card":
        st.gamepass_card(ctx, 640, 360, 1.25, T, title="RUNNING", price="25")
    else:
        st.purchase_prompt(ctx, 640, 360, 1.15, "RUNNING", "25", T - t0, pressed=clamp((T - t0 - 0.6) / 0.15),
                           done=T > t0 + 0.9)
        if T > t0 + 0.6:
            st.cursor(ctx, 700, 470, 1.8, click=1.0)


def s_bonk(ctx, T, t0):
    ss.hallway(ctx, T)
    stand(ctx, "stone", 820, keyed(T, [(0, "neutral"), (t0 + 0.55, "angry")]), T, s=1.15, snap=snap_at(T, t0 + 0.55))
    p = clamp((T - t0) / 0.55)
    x = lerp(150, 640, p) if p < 1 else 640 - 60 * ease(clamp((T - t0 - 0.55) / 0.3))
    stand(ctx, "kid", x, "shock" if p >= 1 else "laugh", T, s=0.95, pose="run" if p < 1 else "stand",
          walk_phase=T * 5, arms=("up", "up"), lean=-0.25 if p >= 1 else 0.3)
    st.sfx_word(ctx, 730, 200, "BONK!", T - t0 - 0.55, col=st.RED, size=72)


def crown_prop(ctx, T, hx, hy, s):
    st.glow(ctx, hx, hy - 0.8 * U1 * s, 220, (1, 0.85, 0.3), 0.5)


def s_command(ctx, T, t0, cmd="/detention", who="stone", bg=("#ffb3b3", "#c0303a")):
    st.burst(ctx, T, bg[0], bg[1], cx=640, cy=360, spin=0.4)
    stand(ctx, who, 300, "smug" if who != "kid" else "determined", T, s=1.2, y=GROUND + 160, arms=("point", "down"))
    ss.command_bar(ctx, 820, 360, 640, cmd, T=T, t0=t0 + 0.1)


def s_roof(ctx, T, t0):
    ss.roof(ctx, T)
    stand(ctx, "kid", 640, "sad", T, s=0.75, y=GROUND - 40)
    ss.cage(ctx, 640, GROUND - 40, 0.8)
    for i in range(2):                                                  # birds
        bx = (T * 80 + i * 500) % 1500 - 100
        st.bold_text(ctx, "v", bx, 160 + i * 60, 40, style.INK, outline=None, shadow=False, stroke=0.0)
    lbl(ctx, "DETENTION", 640, 120, 76, T, t0 + 0.3, bg=st.RED)


def s_whisper(ctx, T, t0, bubble=None, bt=None):
    ss.classroom(ctx, T, board="BE QUIET")
    stand(ctx, "leo", 760, "neutral", T, s=1.0, y=GROUND + 40, look=-0.4)
    stand(ctx, "kid", 520, "smirk", T, s=1.0, y=GROUND + 40, arms=("cover", "down"), look=0.5)
    if bubble and bt is not None and T >= bt:
        st.speech_bubble(ctx, 520, 150, bubble, 40, T - bt, tail=(0, 1))


# ================================================================ Dad's updates
def s_news(ctx, T, t0, text="DAD'S UPDATE"):
    st.burst(ctx, T, "#ffe27a", "#ff7a1a", cx=640, cy=360, spin=0.5)
    style.block(ctx, 240, 220, 800, 260, 26, hexc("#e8323a"), 7)
    st.bold_text(ctx, "BREAKING", 640, 280, 50, st.YELLOW, shadow=False)
    st.bold_text(ctx, text, 640, 380, 80, (1, 1, 1), scale=min(1.0, pop(T - t0) + 0.05))


# ================================================================ Day 3: cafeteria
def s_cafe(ctx, T, t0, lunch=True, buttons=False, sel=None, kid=None, tray=False, tables=True, crowd=None,
           label=None, label_t=None, trade=None, mom=False, unicorn_x=None):
    ss.cafeteria(ctx, T)
    if tables:
        ss.long_table(ctx, 900, GROUND + 40, w=520)
    if lunch:
        stand(ctx, "lunch", 220, "happy", T, s=0.9, y=GROUND - 120, arms=("hold", "hold"))
    if buttons:
        ss.shop_buttons(ctx, 520, 160, 0.8, sel=sel, k=T - t0)
    if crowd == "sit":
        for i, x in enumerate((760, 900, 1040)):
            P[i + 5].draw(ctx, x, GROUND + 20, 0.72, "happy", T)
    elif crowd == "scream":
        for i, x in enumerate((760, 900, 1040, 1180)):
            P[i + 5].draw(ctx, x, GROUND + 20, 0.72, "scream", T, arms=("up", "up"), look=-0.5)
    elif crowd == "run":
        k = clamp((T - t0) / 1.2)
        for i in range(5):
            x = lerp(760 + i * 100, 1450 + i * 60, ease(k))
            P[i + 5].draw(ctx, x, GROUND + 20, 0.72, "scream", T, pose="run", walk_phase=T * 4, arms=("up", "up"))
    elif crowd == "trade":
        for i, x in enumerate((820, 980, 1140)):
            P[i + 9].draw(ctx, x, GROUND + 20, 0.72, "grin", T, arms=("down", "point"), look=-0.5)
    if kid:
        ch = KID_ZOMBIE if kid.startswith("z") else KID
        e = {"z": "happy", "zs": "shock"}.get(kid, kid)
        ch.draw(ctx, 560, GROUND + 30, 0.85, e, T, talk=talking("kid", T), arms=("hold", "hold") if tray else
                ("down", "down"))
        if tray:
            ss.meat_tray(ctx, 560, GROUND - 170, 0.55, T)
    if mom:
        if unicorn_x == "walk":
            unicorn_x = lerp(-420, 120, ease(clamp((T - t0) / 1.8)))
        if unicorn_x is not None:
            ss.unicorn(ctx, unicorn_x, GROUND + 30, 0.7, T)
        stand(ctx, "mom", 380 if unicorn_x is None else unicorn_x + 220, "happy", T, s=0.9, y=GROUND + 30,
              arms=("wave", "hold"), pose="walk" if unicorn_x is not None else "stand", walk_phase=T * 2)
    if trade is not None:
        ss.trade_window(ctx, 640, 330, 0.9, k=T - trade)
    if label:
        lbl(ctx, label, 640, 300, 72, T, label_t if label_t is not None else t0, fg=st.YELLOW)


def s_buttons_cu(ctx, T, t0, sel=0):
    st.burst(ctx, T, "#c4d8ff", "#2f3f9a", cx=640, cy=360, spin=0.3)
    stand(ctx, "lunch", 330, "happy", T, s=1.25, y=GROUND + 170, arms=("hold", "down"))
    ss.shop_buttons(ctx, 860, 300, 1.25, sel=sel, k=T - t0 + 1.0)
    if sel == 1:
        ss.meat_tray(ctx, 860, 640, 0.8, T)


def s_zombie(ctx, T, t0):
    st.burst(ctx, T, "#c8ffb0", "#2e7a2a", cx=640, cy=330, spin=0.5)
    green = clamp((T - t0 - 0.9) / 0.4)
    ch = KID_ZOMBIE if green > 0.5 else KID
    ch.draw(ctx, 640, 790, 2.0, "shock" if green > 0.5 else "happy", T, arms=("hold", "hold"))
    if T < t0 + 0.9:
        ss.meat_tray(ctx, 640, 640, 0.9, T)
    if green > 0:
        st.number_counter(ctx, 640, 100, 0.9, 10, T, col="#4fd16a", prefix="ZOMBIE: ", icon=False)
        st.sfx_word(ctx, 960, 240, "CHOMP!", T - t0 - 0.9, col=st.GREEN, size=64)


def s_toast(ctx, T, t0, name="Supermom1987", msg="joined the game"):
    ss.cafeteria(ctx, T)
    st.tint(ctx, (0.05, 0.06, 0.1), 0.35)
    st.game_toast(ctx, 640, 330, name, msg, T - t0, icon_col="#ff7a8a", name_col="#ff9fb0", size=46)


def s_mom_cu(ctx, T, t0, bubble=None, expr="happy", prop=None, bg=("#ffc4ec", "#c0307a"), arms=("wave", "hold")):
    s_cu(ctx, T, t0, who="mom", expr=expr, bg=bg, bubble=bubble, type_it=True, arms=arms, prop=prop)


def s_emote(ctx, T, t0, sel=None):
    ss.cafeteria(ctx, T)
    st.tint(ctx, (0.05, 0.06, 0.1), 0.35)
    stand(ctx, "mom", 260, "worried" if sel is None else "happy", T, s=1.0, y=GROUND + 40, arms=("point", "down"))
    ss.emote_wheel(ctx, 820, 360, 1.15, sel=sel, k=T - t0 + 0.7)
    if sel is not None:
        st.cursor(ctx, 760, 260, 1.6, click=1.0)


def s_kiss(ctx, T, t0, hearts=False):
    st.burst(ctx, T, "#ffc4ec", "#e0307a", cx=640, cy=360, spin=0.6)
    stand(ctx, "mom", 420, "happy", T, s=1.3, y=GROUND + 150, arms=("up", "up"))
    stand(ctx, "kid", 880, "shock" if not hearts else "cry", T, s=1.1, y=GROUND + 150, arms=("cover", "cover"))
    if hearts:
        st.hearts(ctx, T, t0, 640, 360, n=16, seed=5)
        st.confetti(ctx, T, t0, n=30)
    else:
        st.bold_text(ctx, "MWAH!", 640, 160, 80, st.PINK, scale=min(1.0, pop(T - t0 - 0.4) + 0.05) if T > t0 + 0.4
                     else 0.0)


def s_stare(ctx, T, t0):
    ss.cafeteria(ctx, T)
    for i in range(7):
        x = 100 + i * 180
        P[(i + 3) % 16].draw(ctx, x, GROUND + 30, 0.66, "shock", T, look=0.0)
    st.number_counter(ctx, 640, 300, 0.9, 412, T, col="#ff5fb0", prefix="WATCHING: ")


def s_speaker(ctx, T, t0):
    ss.hallway(ctx, T)
    ss.pa_speaker(ctx, 640, 230, 1.3, T, crackle=1.0)
    st.sfx_word(ctx, 960, 160, "KSSHH!", T - t0, col=st.YELLOW, size=58)


def s_stone_mic(ctx, T, t0, hp_t=None):
    st.burst(ctx, T, "#ffb3b3", "#c0303a", cx=640, cy=360, spin=0.3)
    stand(ctx, "stone", 420, "smug", T, s=1.6, y=GROUND + 200, arms=("hold", "down"))
    style.block(ctx, 598, 470, 22, 300, 6, hexc("#3a3f55"), 4)
    style.block(ctx, 570, 430, 70, 60, 22, hexc("#5a5f7a"), 4)
    if hp_t is not None and T >= hp_t:
        ctx.save()
        ctx.translate(640, 140)
        sc = min(1.0, pop(T - hp_t) + 0.05)
        ctx.scale(sc, sc)
        ctx.translate(-640, -140)
        health(ctx, 1.0)
        ctx.restore()
        st.bold_text(ctx, "10,000 HP", 960, 260, 54, st.RED, scale=min(1.0, pop(T - hp_t) + 0.05))


def s_gym_loading(ctx, T, t0):
    st.game_sky(ctx, top="#4a2a6a", bottom="#f28a5a")
    st.baseplate(ctx, GROUND)
    style.block(ctx, 200, 260, 880, 380, 14, hexc("#b0743c"), 6)
    st.bold_text(ctx, "GYM", 640, 320, 70, (1, 1, 1))
    ss.loading_ring(ctx, 640, 470, 110, T, a=0.9)
    st.glow(ctx, 640, 470, 300, (1, 0.3, 0.3), 0.35 + 0.15 * math.sin(T * 5))
    st.bold_text(ctx, "LOADING...", 640, 620, 40, (1, 1, 1), shadow=False)


# ================================================================ subscribe CTA
def s_hallpass(ctx, T, t0):
    st.burst(ctx, T, "#fff1a8", "#f2b02e", cx=640, cy=360, spin=0.4)
    ss.hall_pass(ctx, 560, 340, 1.1, T)
    st.subscribe_button(ctx, 1040, 560, 1.0, pressed=clamp((T - t0 - 1.0) / 0.2))
    if T > t0 + 0.8:
        st.cursor(ctx, 1090, 600, 1.6, click=1.0 if T > t0 + 1.0 else 0.0)


def s_skip(ctx, T, t0, what="line"):
    if what == "line":
        ss.cafeteria(ctx, T, counter=True)
        for i in range(5):
            P[i].draw(ctx, 500 + i * 140, GROUND + 30, 0.7, "shock", T, look=-0.5)
        p = clamp((T - t0) / 0.8)
        stand(ctx, "kid", lerp(1300, 260, ease(p)), "laugh", T, s=0.8, y=GROUND + 30, pose="run", walk_phase=T * 5)
        ss.hall_pass(ctx, 1040, 160, 0.4, T)
    else:
        ss.classroom(ctx, T, board="TEST TODAY")
        p = clamp((T - t0) / 0.8)
        stand(ctx, "kid", lerp(640, 1250, ease(p)), "laugh", T, s=0.85, y=GROUND + 30 - 200 * math.sin(PI * p),
              pose="jump", arms=("up", "up"))
        st.speed_lines(ctx, T, 900, 360, n=16, r0=200, r1=700, a=0.3)
    st.sfx_word(ctx, 640, 150, "SKIP!", T - t0 - 0.1, col=st.GREEN, size=68)


def s_front_row(ctx, T, t0, stone=False):
    ss.classroom(ctx, T, board="FRONT ROW")
    st.glow(ctx, 600, 520, 300, (1, 1, 0.8), 0.5)
    stand(ctx, "kid", 560, "worried" if stone else "neutral", T, s=1.0, y=GROUND + 60)
    ss.desk(ctx, 560, GROUND + 70, 1.0)
    if stone:
        stand(ctx, "stone", 820, "smug", T, s=1.0, y=GROUND + 60, arms=("wave", "down"))
        ss.desk(ctx, 820, GROUND + 70, 1.0)


# ================================================================ Day 4: the note, the library
def s_note(ctx, T, t0, lines=("LIBRARY.", "NOW."), sign=None):
    st.void_bg(ctx, top="#3a2a10", bottom="#0d0806", y0=0, y1=720)
    st.glow(ctx, 640, 360, 420, (1, 0.9, 0.5), 0.4)
    ss.note_paper(ctx, 640, 360, 1.5, lines=lines, sign=sign)
    if sign:
        st.face_icon(ctx, 900, 520, 50, "#f0c9a8", "#1a1010", expr="smirk")


def s_library(ctx, T, t0, emma="neutral", kid=True):
    ss.library(ctx, T)
    stand(ctx, "emma", 420, emma, T, s=0.95, y=GROUND + 30, arms=("hold", "hold"))
    st.monitor(ctx, 700, GROUND - 160, 0.55, T, lambda c, x, y, w, h, TT: ss.admin_screen(c, x, y, w, h, TT,
                                                                                            red=4))
    if kid:
        stand(ctx, "kid", 1000, "shock", T, s=0.9, y=GROUND + 30)
    tag(ctx, 420, 0.95, "Shadow Ninja", y=GROUND + 30)


def s_panel(ctx, T, t0, red=4, extra_line=None, lines=None):
    st.void_bg(ctx, top="#141a2e", bottom="#05060f", y0=0, y1=720)
    st.monitor(ctx, 640, 640, 1.15, T, lambda c, x, y, w, h, TT: ss.admin_screen(c, x, y, w, h, TT, red=red,
                                                                                  lines=lines))


def s_summer(ctx, T, t0, deleted_t=None, restored=False):
    st.burst(ctx, T, "#fff6c4", "#8fd0ff", cx=640, cy=360, spin=0.3)
    d = clamp((T - deleted_t) / 0.4) if deleted_t is not None and T >= deleted_t else 0.0
    ss.summer_card(ctx, 640, 360, 1.25, T, deleted=d, restored=1.0 if restored else 0.0)


def s_crown(ctx, T, t0, text="NEW ADMIN?"):
    st.burst(ctx, T, "#fff1a8", "#f2b02e", cx=640, cy=360, spin=0.5)
    ss.crown(ctx, 640, 320, 1.6, T)
    lbl(ctx, text, 640, 560, 76, T, t0 + 0.3, bg=st.UI_DARK, fg=st.YELLOW)


def s_study(ctx, T, t0, xp=False, clock=None, level=None):
    ss.bedroom_ls(ctx, T)
    stand(ctx, "kid", 480, "determined", T, s=0.95, arms=("hold", "point"), pose="sit", look=0.5)
    ss.book(ctx, 700, GROUND - 200, 0.5, T, flip=((T - t0) * 1.2) % 1)
    if xp:
        for i in range(4):
            tt = t0 + 0.3 + i * 0.6
            if 0 <= T - tt < 1.0:
                st.bold_text(ctx, "+1 XP", 800 + (i % 2) * 120, 330 - (T - tt) * 140, 40, st.GREEN,
                             scale=min(1.0, pop(T - tt) + 0.1))
    if clock is not None:
        st.big_clock(ctx, 1080, 170, 80, clock, T)
    if level is not None:
        ss.level_pill(ctx, 600, 120, level, s=1.2, k=T - t0 - 0.6)


# ================================================================ Day 5: the final exam
def s_gym_doors(ctx, T, t0):
    ss.gym(ctx, T, doors=clamp((T - t0 - 1.2) / 0.8))
    st.big_clock(ctx, 1100, 140, 70, 14.98, T)
    lbl(ctx, "2:59 PM", 1100, 260, 48, T, t0 + 0.1, bg=st.UI_DARK, fg=st.YELLOW)


def s_boss(ctx, T, t0, s=0.7, x=640, jaw=None, rage=0.0, hp=None, label=None, label_t=None, kids=False,
           dmg=None, arms_t=None, teeth_t=None, look="wide"):
    j = jaw if jaw is not None else (0.6 + 0.4 * math.sin(T * 30) if talking("exam", T) else 0.15)
    boss_gym(ctx, T, boss_x=x, boss_s=s, jaw=j, rage=rage, hp=hp)
    if kids:
        for i, (who, xx) in enumerate((("kid", 150), ("leo", 280), ("priya", 1130))):
            stand(ctx, who, xx, "scared", T, s=0.6, y=GROUND + 40, arms=("up", "up"))
    if dmg is not None and T >= dmg[1]:
        st.damage_text(ctx, x + 140, 260, T - dmg[1], txt=dmg[0])
    if label:
        lbl(ctx, label, 640, 640, 70, T, label_t if label_t is not None else t0, bg=st.RED)


def s_fireball(ctx, T, t0):
    boss_gym(ctx, T, boss_x=1050, boss_s=0.5, jaw=0.8, rage=1.0)
    p = clamp((T - t0) / 1.6)
    ss.fireball(ctx, lerp(900, 250, p), lerp(200, 520, p * p), 1.0, T)
    for i, (who, x) in enumerate((("kid", 160), ("leo", 300))):
        stand(ctx, who, x, "scream", T, s=0.7, y=GROUND + 40, arms=("up", "up"))


def s_panic(ctx, T, t0):
    boss_gym(ctx, T, boss_x=1050, boss_s=0.5, jaw=0.9, rage=1.0)
    k = (T - t0)
    for i in range(6):
        x = (150 + i * 160 + k * (220 if i % 2 else -180)) % 1400 - 60
        P[i].draw(ctx, x, GROUND + 40, 0.66, "scream", T, pose="run", walk_phase=T * 4, arms=("up", "up"))
    if int(T * 2) % 3 == 0:
        st.shockwave(ctx, 640, 520, (T * 2) % 1, r_max=500)
    st.sfx_word(ctx, 640, 160, "AAAAH!", T - t0, col=st.RED, size=72)


def s_boom(ctx, T, t0):
    boss_gym(ctx, T, boss_x=1050, boss_s=0.5, jaw=0.6, rage=1.0)
    st.impact_star(ctx, 520, 420, 260, T - t0, txt="BOOM!")
    for i, (who, x) in enumerate((("kid", 180), ("leo", 860))):
        stand(ctx, who, x + math.sin(T * 9) * 20, "scared", T, s=0.7, y=GROUND + 40, pose="jump",
              arms=("cover", "cover"))


def s_answers(ctx, T, t0):
    boss_gym(ctx, T, boss_x=1050, boss_s=0.5, jaw=0.2, rage=0.5)
    for i, (x, a) in enumerate(((150, "52?"), (330, "56!"), (510, "48??"), (690, "7"))):
        P[i + 2].draw(ctx, x, GROUND + 40, 0.62, "determined", T, arms=("up", "down"))
        if T >= t0 + 0.15 * i:
            st.speech_bubble(ctx, x, 300, a, 34, T - t0 - 0.15 * i, tail=(0, 1))


def s_countdown(ctx, T, t0, n=60, msg="Summer deleted in:"):
    st.void_bg(ctx, top="#4a0b14", bottom="#12020a", y0=0, y1=720)
    st.system_message(ctx, 640, 360, 1.1, [msg, f"{n} SECONDS"], T - t0, T=T, typed=clamp((T - t0) / 0.6))


def s_bubbles(ctx, T, t0, crowd=False):
    boss_gym(ctx, T, boss_x=1080, boss_s=0.48, jaw=0.2, rage=0.3, dark_k=0.1)
    stand(ctx, "priya", 260, "smug", T, s=0.8, y=GROUND + 40, arms=("up", "point"))
    for i, (txt, dx) in enumerate((("42", 0), ("PHOTOSYNTHESIS", 1), ("1776", 2))):
        y = 280 - ((T - t0) * 60 + i * 70) % 260
        st.speech_bubble(ctx, 340 + dx * 230, max(150, y), txt, 38, 1.0, tail=(0, 1))
    if crowd:
        for i in range(8):
            x = 120 + i * 130
            P[i].draw(ctx, x, GROUND + 60, 0.5, "stars", T, arms=("up", "up"))
            if T >= t0 + 0.2 + i * 0.12:
                st.speech_bubble(ctx, x, 420, ("42", "1776", "PHOTO..")[i % 3], 24, T - t0 - 0.2 - i * 0.12,
                                 tail=(0, 1))


def s_combo(ctx, T, t0, text="COMBO x412", hp=None, dmg=None):
    boss_gym(ctx, T, boss_x=900, boss_s=0.6, jaw=0.9, rage=1.0, hp=hp)
    st.impact_star(ctx, 900, 340, 240, T - t0, txt=None)
    st.bold_text(ctx, text, 460, 360, 100, st.YELLOW, scale=min(1.0, pop(T - t0) + 0.05), tilt=-0.08)
    if dmg:
        st.damage_text(ctx, 1000, 220, T - t0 - 0.2, txt=dmg)


def s_hit(ctx, T, t0, hp=0.02):
    boss_gym(ctx, T, boss_x=1050, boss_s=0.5, jaw=0.5, rage=1.0)
    stand(ctx, "kid", 420, "cry", T, s=0.9, y=GROUND + 40, lean=-0.3, arms=("up", "up"))
    ss.fireball(ctx, 470, 360, 0.6, T, txt="QUIZ")
    if int(T * 4) % 2 == 0:
        st.tint(ctx, (1, 0, 0), 0.25)
    ctx.save()
    ctx.translate(0, 360)
    st.health_bar(ctx, hp, name="YOU", y=272)
    ctx.restore()


def s_juice_throw(ctx, T, t0):
    boss_gym(ctx, T, boss_x=1080, boss_s=0.45, jaw=0.3)
    stand(ctx, "leo", 220, "determined", T, s=0.85, y=GROUND + 40, arms=("up", "down"))
    stand(ctx, "kid", 960 - 300, "worried", T, s=0.8, y=GROUND + 40)
    p = clamp((T - t0 - 0.4) / 1.4)
    ss.juice_box(ctx, lerp(260, 640, p), 360 - math.sin(PI * p) * 220, 0.7, rot=p * 8)
    st.sfx_word(ctx, 300, 200, "YEET!", T - t0 - 0.4, col=st.PINK, size=56)


def s_heal(ctx, T, t0):
    st.burst(ctx, T, "#b8ffb0", "#2e9c46", cx=640, cy=360, spin=0.5)
    stand(ctx, "kid", 640, "laugh", T, s=1.4, y=GROUND + 200, arms=("up", "hold"))
    ss.juice_box(ctx, 760, 380, 0.7)
    ctx.save()
    ctx.translate(0, 360)
    st.health_bar(ctx, min(0.52, 0.02 + 0.5 * clamp((T - t0) / 0.8)), name="YOU", y=272)
    ctx.restore()
    st.bold_text(ctx, "+50 HP", 960, 180, 70, st.GREEN, scale=min(1.0, pop(T - t0) + 0.05))


def s_mom_unicorn(ctx, T, t0, toast=True):
    ss.gym(ctx, T, dark_k=0.1)
    p = clamp((T - t0) / 1.5)
    x = lerp(-300, 520, ease(p))
    ss.unicorn(ctx, x, GROUND + 40, 0.75, T)
    stand(ctx, "mom", x + 20, "laugh", T, s=0.75, y=GROUND - 120, arms=("up", "wave"), pose="sit")
    if toast:
        st.game_toast(ctx, 640, 110, "Supermom1987", "joined the game", T - t0, icon_col="#ff7a8a",
                      name_col="#ff9fb0", size=36)


def s_owned(ctx, T, t0):
    st.burst(ctx, T, "#c4d8ff", "#2f3f9a", cx=640, cy=360, spin=0.4)
    st.gamepass_card(ctx, 640, 360, 1.25, T, title="RUNNING", price="25", bought=1.0)
    st.check_mark(ctx, 900, 230, 80, (T - t0) / 0.25)
    st.bold_text(ctx, "OWNED!", 640, 620, 70, st.GREEN, scale=min(1.0, pop(T - t0 - 0.2) + 0.05))


def s_sprint_jump(ctx, T, t0, part=1):
    ss.gym(ctx, T, dark_k=0.1)
    if part == 1:
        ss.unicorn(ctx, 700, GROUND + 40, 0.75, T)
        stand(ctx, "mom", 720, "laugh", T, s=0.75, y=GROUND - 120, pose="sit", arms=("up", "up"))
        p = clamp((T - t0) / 2.6)
        x = lerp(-60, 1000, p)
        y = GROUND + 40 - (math.sin(PI * clamp((p - 0.45) / 0.4)) * 330 if p > 0.45 else 0)
        stand(ctx, "kid", x, "determined", T, s=0.75, y=y, pose="run" if p < 0.45 else "jump", walk_phase=T * 5,
              arms=("up", "up"))
        st.speed_lines(ctx, T, 640, 360, n=20, r0=300, r1=900, a=0.3)
    else:
        stand(ctx, "dad", 520, "laugh", T, s=0.95, y=GROUND + 40, arms=("up", "up"))
        st.stage_pill(ctx, 520, 110, "STAGE 40/40", s=1.1, col="#4fd16a")
        p = clamp((T - t0) / 1.6)
        stand(ctx, "kid", lerp(300, 900, p), "determined", T, s=0.7, y=GROUND - 360 - math.sin(PI * p) * 120,
              pose="jump", arms=("up", "up"))


def s_swing(ctx, T, t0):
    boss_gym(ctx, T, boss_x=900, boss_s=0.62, jaw=0.8, rage=1.0)
    ang = -1.4 + 2.4 * ease(clamp((T - t0 - 0.6) / 0.5))
    stand(ctx, "kid", 470, "scream", T, s=0.85, y=GROUND - 160, pose="jump", arms=("up", "up"))
    ss.eraser(ctx, 470 + math.cos(ang) * 220, 300 + math.sin(ang) * 220, 1.6, rot=ang + PI / 2)
    st.speed_lines(ctx, T, 640, 360, n=18, r0=260, r1=900, a=0.3)


def s_erased(ctx, T, t0):
    boss_gym(ctx, T, boss_x=760, boss_s=0.62, jaw=1.0, rage=1.0, erase=clamp((T - t0) / 0.8))
    st.stamp(ctx, 640, 360, "ERASED!", T - t0 - 0.2, size=150)
    for i in range(10):
        a = i * 0.63 + T
        r = (T - t0) * 500
        style.sparkle(ctx, 760 + math.cos(a) * r, 360 + math.sin(a) * r * 0.6, 26)


def s_new_admin(ctx, T, t0):
    st.burst(ctx, T, "#fff1a8", "#f2b02e", cx=640, cy=330, spin=0.6)
    land = clamp((T - t0 - 0.3) / 0.5)
    stand(ctx, "kid", 640, "stars", T, s=1.5, y=GROUND + 200, arms=("up", "up"))
    ss.crown(ctx, 640, lerp(-100, 380, ease(land)), 0.55, T)
    st.name_pill(ctx, 640, 640, "[ADMIN] ToiletDestroyer9000", size=34, col=st.YELLOW)


def s_cheer(ctx, T, t0):
    ss.gym(ctx, T)
    for i in range(7):
        x = 120 + i * 175
        P[i].draw(ctx, x, GROUND + 40, 0.66, "laugh", T, arms=("up", "up"), bob=1.5)
    stand(ctx, "kid", 640, "laugh", T, s=0.75, y=GROUND - 160, arms=("up", "up"), pose="jump")
    ss.crown(ctx, 640, 210, 0.35, T)
    st.confetti(ctx, T, t0, n=40)
    st.sfx_word(ctx, 640, 100, "TOILET DESTROYER!", T - t0, col=st.YELLOW, size=56)


# ================================================================ resolution
def s_normal(ctx, T, t0, what="lockers"):
    if what == "lockers":
        ss.hallway(ctx, T, wall_col="#e8e0d0")
        stand(ctx, "kid", 640, "happy", T, s=0.9, y=GROUND + 30)
    elif what == "meat":
        ss.cafeteria(ctx, T)
        ss.meat_tray(ctx, 640, 520, 1.1, T)
    elif what == "priya":
        ss.library(ctx, T)
        stand(ctx, "priya", 640, "happy", T, s=1.0, y=GROUND + 30, arms=("hold", "hold"))
        ss.book(ctx, 640, GROUND - 200, 0.4, T)
    elif what == "emma":
        ss.classroom(ctx, T, board="")
        stand(ctx, "emma", 640, "smirk", T, s=1.0, y=GROUND + 30, arms=("cross", "cross"))
        tag(ctx, 640, 1.0, "Shadow Ninja", y=GROUND + 30)
    elif what == "car":
        ss.home_street(ctx, T, sunset=1.0)
        x = lerp(-200, 700, clamp((T - t0) / 1.5))
        ss.family_car(ctx, x, GROUND + 62, 0.75, T, driver=lambda c, hx, hy: DAD.draw(
            c, hx, hy + 2.5 * U1 * 0.42, 0.42, "laugh", T, shadow=False))
    elif what == "home":
        ss.home_street(ctx, T, sunset=1.0)
        stand(ctx, "kid", 640, "happy", T, s=0.9, y=GROUND + 30)


def s_report(ctx, T, t0, k1=None, k2=None):
    st.burst(ctx, T, "#bfe3ff", "#2f6bd8", cx=640, cy=360, spin=0.3)
    ss.report_card(ctx, 640, 380, 1.1, T, k_lines=(T - k1 if k1 is not None else -1, T - k2 if k2 is not None else -1))


def s_comments(ctx, T, t0):
    """Comment call: a comments panel filling with 'XP' + the input box typing XP."""
    st.burst(ctx, T, "#c4d8ff", "#2f3f9a", cx=640, cy=360, spin=0.3)
    style.block(ctx, 290, 80, 700, 560, 28, hexc("#16181f"), 6)
    st.bold_text(ctx, "Comments  412", 330, 130, 34, (1, 1, 1), align="l", shadow=False, stroke=0.0)
    rows = (("Leo", "XP!!", "#ff8a3d"), ("Priya_99", "XP (lvl 99 btw)", "#9d5cff"), ("Shadow Ninja", "XP", "#2b2f45"),
            ("SuperMom1987", "XP sweetie!!", "#ff7a8a"))
    for i, (nm, txt, col) in enumerate(rows):
        k = T - (t0 + 0.2 + i * 0.35)
        if k < 0:
            continue
        y = 200 + i * 90
        ctx.new_sub_path()
        ctx.arc(350, y + 10, 26, 0, 2 * PI)
        ctx.set_source_rgb(*hexc(col))
        ctx.fill()
        st.bold_text(ctx, nm, 395, y - 6, 24, hexc("#9aa0b8"), align="l", shadow=False, stroke=0.0)
        st.bold_text(ctx, txt, 395, y + 26, 32, (1, 1, 1), align="l", shadow=False, stroke=0.0,
                     scale=min(1.0, pop(k) + 0.1))
    style.block(ctx, 320, 560, 640, 60, 30, hexc("#2c3350"), 3, gloss=False)
    st.bold_text(ctx, typed("XP", T, t0 + 1.4, 4) or "Add a comment...", 350, 590, 30,
                 (1, 1, 1) if T > t0 + 1.4 else hexc("#9aa0b8"), align="l", shadow=False, stroke=0.0)


def s_update(ctx, T, t0):
    ss.bedroom_ls(ctx, T)
    st.tint(ctx, (0.05, 0.06, 0.1), 0.5)
    st.roblox_dialog(ctx, 640, 360, 1.15, T - t0, "New update available",
                     "Roblox School 2. Install?", button="INSTALL", col="#2f6bd8")


# ================================================================ shots
S = []
SFX = []


def shot(t0, fn, cam=None, sfx=(), hud=False, players=412, whip=None, shake=None, **p):
    draw = (lambda ctx, t, d, fn=fn, t0=t0, p=p: fn(ctx, t0 + t, t0, **p))
    sh = dict(start=t0, draw=draw, keys=cam or [(t0, 1.0, C)], vignette=0.12)
    if hud:
        sh["overlay"] = (lambda ctx, t, d, t0=t0, pl=players: draw_hud(ctx, t0 + t, pl))
    if whip:
        sh["whip"] = whip
    if shake:
        sh["shake"] = shake
    S.append(sh)
    for dt, f, v in sfx:
        SFX.append((t0 + dt, f, v))


def punch(t0, tk, z=1.1, f=C, m=0.12):
    return [(t0, 1.0, C), (tk, z, f, m)]


def push(t0, z=1.0, f=C):
    return [(t0, z, f)]


POP, SW, HIT, BOOM, DING, TICK, SPARK = "pop.wav", "swish.wav", "hit.wav", "boom.wav", "ding.wav", "tick.wav", \
    "sparkle.wav"
Y = ("#ffe27a", "#f29a2e")
BLU = ("#bfe3ff", "#2f6bd8")
PUR = ("#e2c8ff", "#7a3fd8")
GRN = ("#c8ffb0", "#2e9c46")
RED_ = ("#ffb3b3", "#c0303a")
PNK = ("#ffc4ec", "#c0307a")
GRY = ("#c4c8e8", "#4a4f8a")

# ---- intro (0 - 34.7)
shot(0.0, s_hk_face, punch(0.0, 0.05, 1.06, (640, 360)), sfx=[(0.0, "sting.wav", 1.0), (0.05, HIT, 0.9)],
     shake=(0.05, 14))
shot(0.44, s_hk_slam, [(0.44, 1.0, C), (0.82, 1.05, (640, 380), 0.08)], sfx=[(0.1, "whoosh.wav", 0.8),
                                                                       (0.38, BOOM, 1.4)], shake=(0.38, 24))
shot(1.33, s_hk_become, push(1.33), sfx=[(0.03, SPARK, 1.0), (0.1, "whoosh.wav", 0.6)])
shot(1.8, s_hk_roblox, punch(1.8, 1.85, 1.08, (640, 330)), sfx=[(0.05, HIT, 1.0), (0.3, "chaching.wav", 0.7)],
     shake=(0.05, 16), hud=True)
shot(2.4, s_hk_days, push(2.4), sfx=[(0.05, POP, 0.7), (0.17, POP, 0.7), (0.29, POP, 0.7), (0.41, POP, 0.7),
                                     (0.53, POP, 0.8), (0.56, DING, 0.8)])
shot(4.06, s_hk_one, punch(4.06, 4.1, 1.08, (640, 330)), sfx=[(0.04, HIT, 1.0), (0.29, POP, 0.7)], shake=(0.04, 12))
shot(5.18, s_hk_friday, punch(5.18, 5.75, 1.1), sfx=[(0.0, TICK, 0.7), (0.3, TICK, 0.7), (0.57, HIT, 1.1)],
     shake=(0.57, 16))
shot(6.4, s_hk_charge, push(6.4), sfx=[(0.03, "whoosh.wav", 0.9), (0.4, "step.wav", 0.6), (0.8, "step.wav", 0.6),
                                       (1.38, HIT, 1.0)], whip=1)
shot(8.2, s_hk_boss, [(8.2, 1.0, C), (8.46, 1.06, (640, 360), 0.1)], sfx=[(0.0, "sting_low.wav", 0.9),
                                                                     (0.26, BOOM, 1.4), (0.63, HIT, 0.8)],
     shake=(0.26, 24))
shot(9.62, s_cu, sfx=[(0.1, TICK, 0.6)], who="kid", expr="cold", bg=RED_, arms=("hold", "hold"),
     prop=lambda c, T, hx, hy, s: ss.pencil(c, hx + 230, hy + 260, 1.6, -0.9), label="LITERALLY.", label_t=9.7)
shot(10.48, s_coldopen, punch(10.48, 10.6, 1.06, (520, 360)), sfx=[(0.0, BOOM, 1.2), (0.6, "buzz.wav", 0.5)],
     shake=(0.05, 14))
shot(12.12, s_cu, sfx=[(0.0, HIT, 0.9)], who="kid", expr="scream", bg=RED_, arms=("point", "up"),
     bubble="EQUIP THE ERASER!", btime=12.12, type_it=True,
     prop=lambda c, T, hx, hy, s: eraser_slot(c, T, sel=1, cx=860, y=620))
shot(13.86, s_cu, sfx=[(0.0, POP, 0.8)], who="leo", expr="grin", bg=GRN, arms=("up", "down"), bubble="GOT IT!",
     btime=13.86)
shot(14.56, s_cu, punch(14.56, 15.6, 1.1, (560, 340)), sfx=[(0.0, POP, 0.7), (1.0, "boing.wav", 0.8)],
     who="leo", expr="happy", bg=GRN, arms=("hold", "down"),
     prop=lambda c, T, hx, hy, s: ss.juice_box(c, hx + 200, hy + 330, 1.1), sfx_word=("JUICE?!", 15.4, st.PINK))
shot(16.78, s_cu, sfx=[(0.0, "whip.wav", 0.8)], who="kid", expr="worried", bg=GRY, arms=("shrug", "shrug"),
     bubble="OKAY, LET ME EXPLAIN.", btime=16.78, type_it=True)
shot(19.2, s_bedroom, push(19.2), sfx=[(0.0, "sting_soft.wav", 0.7), (0.4, TICK, 0.6)], clock=23.0, kid="sleepy")
shot(21.2, s_homework, punch(21.2, 21.8, 1.08), sfx=[(0.6, HIT, 0.8)])
shot(23.68, s_bedroom, push(23.68), sfx=[(0.3, "page.wav", 0.6)], kid="sad", talk_bubble="UGH...",
     paper=True)
shot(25.4, s_cu, sfx=[(0.0, POP, 0.6)], who="kid", expr="sleepy", bg=GRY, arms=("hold", "hold"),
     bubble="SCHOOL SHOULD JUST BE ROBLOX.", btime=25.2, type_it=True)
shot(27.16, s_tablet, punch(27.16, 27.4, 1.08), sfx=[(0.0, DING, 0.9)], lines=("REQUEST", "RECEIVED"))
shot(28.34, s_cu, sfx=[(0.0, HIT, 0.9)], who="kid", expr="shock", bg=BLU, arms=("up", "up"), snap=28.34,
     bubble="WAIT, WHAT?", btime=28.34)
shot(29.78, s_tablet, push(29.78), sfx=[(0.0, "type_key.wav", 0.6), (0.9, "buzz.wav", 0.6)],
     lines=("APPLYING TO:", "WHOLE SCHOOL"), prog=1.5)
shot(31.76, s_lightsout, push(31.76), sfx=[(0.8, "click.wav", 1.0), (1.2, "sting_low.wav", 0.8)])

# ---- Day 1 (34.68 - 109.26)
shot(34.68, s_card, sfx=[(0.0, BOOM, 1.1), (0.45, POP, 0.7)], word="DAY", num=1, sub="MONDAY", bg=GRN)
shot(36.26, s_school_wide, punch(36.26, 38.24, 1.08, (640, 330)), sfx=[(0.2, "step.wav", 0.5), (0.7, "step.wav",
     0.5), (1.98, HIT, 0.9)], walk=(36.26, 1.9), label="BLOCKS!", label_t=38.24, hud=True)
shot(39.28, s_blocks, punch(39.28, 40.9, 1.08), sfx=[(0.0, SPARK, 0.9), (1.6, POP, 0.8)])
shot(42.12, s_school_wide, punch(42.12, 43.2, 1.1, (640, 300)), sfx=[(0.3, SW, 0.6), (0.8, HIT, 0.8)],
     sign="WELCOME!", sign_t=42.6, kid="happy")
shot(44.74, s_school_wide, punch(44.74, 45.6, 1.25, (640, 300)), sfx=[(0.2, DING, 0.8), (1.0, "chaching.wav", 0.6)],
     sign="WELCOME, PLAYERS: 412", sign_t=44.0, kid="shock")
shot(47.56, s_crowd_tags, punch(47.56, 48.4, 1.06), sfx=[(0.3, POP, 0.6), (0.6, POP, 0.6), (0.9, POP, 0.6)],
     hud=True)
shot(49.78, s_hall, punch(49.78, 50.1, 1.06), sfx=[(0.0, SW, 0.5)], action="look", hud=True)
shot(50.6, s_inventory, push(50.6), sfx=[(0.0, "click.wav", 0.8), (0.1, POP, 0.6)], items=(None, None, None),
     label="INVENTORY", label_t=50.7)
shot(51.62, s_inventory, punch(51.62, 51.8, 1.08), sfx=[(0.0, DING, 0.7)], items=(None, None, None),
     label="3 SLOTS", label_t=51.62)
shot(52.58, s_inventory, push(52.58), sfx=[(0.1, POP, 0.8), (0.95, POP, 0.8), (1.85, POP, 0.8)],
     items=("pencil", "eraser", "juice"), k_times=(52.65, 53.5, 54.4))
shot(55.22, s_cu, sfx=[(0.0, TICK, 0.6)], who="kid", expr="worried", bg=Y, arms=("hold", "down"),
     bubble="WHY DO I HAVE A JUICE BOX?", btime=55.22, type_it=True,
     prop=lambda c, T, hx, hy, s: ss.juice_box(c, hx + 210, hy + 300, 0.9))
shot(57.18, s_juice_q, push(57.18, 1.0), sfx=[(0.0, "sting_soft.wav", 0.8)])
shot(59.3, class_scene, push(59.3), sfx=[(0.0, SW, 0.6), (0.4, "bell.wav", 0.5)], board="FIRST CLASS",
     hud=True)
shot(60.5, class_scene, punch(60.5, 61.6, 1.08, (760, 330)), sfx=[(0.3, POP, 0.7)], board="ATTENDANCE",
     list_k=60.6)
shot(63.18, s_cu, sfx=[(0.0, POP, 0.7)], who="pebble", expr="happy", bg=BLU, arms=("hold", "down"),
     bubble="SHADOW NINJA?", btime=63.18, type_it=True)
shot(64.1, class_scene, punch(64.1, 65.2, 1.12, (1000, 380)), sfx=[(0.5, SW, 0.5)], board="ATTENDANCE",
     students=[("leo", 420), ("priya", 860), ("emma", 1090)])
shot(66.8, class_scene, punch(66.8, 67.1, 1.06, (900, 380)), sfx=[(0.1, HIT, 0.9), (0.5, "murmur.wav", 0.6)],
     board="ATTENDANCE", heads_t=66.85, label="SHADOW NINJA", label_t=67.2)
shot(68.9, s_cu, sfx=[(0.0, SPARK, 0.7)], who="emma", expr="smirk", bg=PUR, arms=("cross", "cross"),
     label="xX SHADOW NINJA Xx", label_t=69.0, label_bg=st.UI_DARK)
shot(70.56, s_cu, sfx=[(0.0, POP, 0.7)], who="pebble", expr="happy", bg=BLU, bubble="PIZZA LOVER?", btime=70.56,
     type_it=True, arms=("hold", "down"))
shot(71.34, s_cu, sfx=[(0.0, POP, 0.8)], who="leo", expr="laugh", bg=GRN, arms=("up", "down"), bubble="PRESENT!",
     btime=71.34)
shot(72.1, s_cu, punch(72.1, 73.8, 1.1, (450, 300)), sfx=[(0.4, TICK, 0.5), (1.7, HIT, 0.9)], who="pebble",
     keys=[(0, "happy"), (73.6, "shock")], bg=BLU, bubble="AND... TOILET DESTROYER 9000?", btime=72.1,
     type_it=True, arms=("hold", "down"), snap=73.6)
shot(74.75, s_cu, sfx=[(0.0, "cricket.wav" if False else TICK, 0.5)], who="kid", expr="worried", bg=GRY,
     arms=("hold", "down"), bubble="...here.", btime=74.75)
shot(75.14, s_flashback6, push(75.14), sfx=[(0.0, "whip.wav", 0.6), (0.4, "type_key.wav", 0.5),
                                         (0.9, "type_key.wav", 0.5)])
shot(77.72, s_bell, punch(77.72, 77.9, 1.08), sfx=[(0.0, "bell.wav", 1.1)], ring=True)
shot(79.32, s_bell, push(79.32), sfx=[(0.2, TICK, 0.6)], ring=False)
shot(80.66, s_ui, push(80.66), sfx=[(0.0, SW, 0.7), (0.4, "sparkle.wav", 0.6)], kind="teleport",
     title="Teleporting...", msg="SCIENCE")
shot(82.7, class_scene, push(82.7), sfx=[(0.2, "whoosh.wav", 0.8)], board="HISTORY", poof_t=82.85)
shot(84.86, class_scene, punch(84.86, 85.3, 1.15, (640, 420)), sfx=[(0.1, TICK, 0.6)], board="HISTORY",
     poof_t=0.0, teacher=False, focus_kid="worried")
shot(85.7, s_ui, push(85.7), sfx=[(0.0, "buzz.wav", 0.8)], kind="dialog", title="Science is full",
     msg="This server is full (50/50).", button="OK", col="#e8323a", bg="game")
shot(87.48, s_ui, push(87.48), sfx=[(0.0, SW, 0.6)], kind="teleport", title="Joining another server...",
     msg="SCIENCE (SERVER 2)")
shot(89.26, s_adults, punch(89.26, 91.9, 1.08, (640, 380)), sfx=[(0.1, POP, 0.6), (2.6, HIT, 0.8)])
shot(91.9, s_adults, punch(91.9, 92.0, 1.12, (640, 400)), sfx=[(0.0, TICK, 0.5)])
shot(93.58, s_cu_adult, sfx=[(0.0, POP, 0.6)], bubble="YOU'RE LATE, NEW GUY.")
shot(94.94, s_cu, sfx=[(0.0, HIT, 0.8)], who="kid", expr="angry", bg=Y, arms=("punch", "punch"),
     bubble="I'M NINE!", btime=94.94, snap=94.94)
shot(96.18, s_adults, punch(96.18, 97.04, 1.08, (500, 300)), sfx=[(0.8, POP, 0.7)], focus="point",
     board="TAXES 101\n1040 FORM DUE")
shot(98.38, s_clock, push(98.38), sfx=[(0.0, TICK, 0.6), (0.6, TICK, 0.6), (1.2, DING, 0.7)], h0=13.0, h1=15.0,
     label="3:00 PM")
shot(99.9, s_parking, push(99.9), sfx=[(0.0, SW, 0.6)], stage=1, dad="wave", hud=True)
shot(100.72, s_parking, punch(100.72, 101.62, 1.06), sfx=[(0.9, HIT, 0.8)], stage=1, dad="wave",
     label="IT'S AN OBBY!", label_t=101.62)
shot(102.6, s_parking, punch(102.6, 102.8, 1.1, (640, 400)), sfx=[(0.1, DING, 0.8)], stage=1, dad="jump",
     label="40 STAGES", label_t=102.65)
shot(103.96, s_cu, sfx=[(0.0, POP, 0.7)], who="dad", expr="happy", bg=Y, arms=("up", "down"),
     bubble="DON'T WORRY, BUDDY!", btime=103.96, type_it=True)
shot(105.0, s_cu, sfx=[(0.0, SPARK, 0.6)], who="dad", expr="smug", bg=Y, arms=("up", "down"),
     bubble="FIVE MINUTES. TOPS.", btime=105.0, type_it=True)
shot(106.48, s_parking, push(106.48), sfx=[(0.3, "boing.wav", 0.6), (0.9, "thud.wav", 0.7)], stage=2, dad="sweat",
     label="STAGE 2", label_t=106.8, hud=True)
shot(108.12, s_walkhome, push(108.12), sfx=[(0.0, "step.wav", 0.5), (0.5, "step.wav", 0.5)])

# ---- Day 2 (109.26 - 175.94)
shot(109.26, s_card, sfx=[(0.0, BOOM, 1.1), (0.45, POP, 0.7)], word="DAY", num=2, sub="TUESDAY", bg=BLU)
shot(110.78, s_rules, push(110.78), sfx=[(0.3, "page.wav", 0.7), (0.55, POP, 0.5), (0.8, POP, 0.5)])
shot(112.3, s_big, sfx=[(0.0, HIT, 1.0)], text="RULE 1", sub="RIGHT ANSWER = XP", bg=GRN, size=150)
shot(113.04, class_scene, punch(113.04, 113.8, 1.06), sfx=[(0.5, DING, 0.7), (1.1, DING, 0.6)],
     board="2 + 2 = ?", xp=(113.5, 114.1, 114.7))
shot(115.26, s_cu, sfx=[(0.0, POP, 0.6)], who="priya", expr="smug", bg=PUR, arms=("point", "down"),
     bubble="THE MITOCHONDRIA IS...", btime=115.26, type_it=True)
shot(117.2, s_cu, sfx=[(0.0, SPARK, 0.6)], who="priya", expr="smug", bg=PUR, arms=("up", "point"), s=2.3,
     bubble="...THE POWERHOUSE OF THE CELL!", btime=117.2, type_it=True)
shot(119.2, s_levelup, sfx=[(0.0, "success.wav", 0.9)], n0=1, n1=2)
shot(119.84, s_levelup, sfx=[(0.3, DING, 0.6), (0.9, DING, 0.6), (1.5, "chaching.wav", 0.8)], n0=2, n1=99,
     label="LEVEL 99!")
shot(123.04, s_glow, push(123.04, 1.0), sfx=[(0.0, SPARK, 1.0)])
shot(124.62, s_still, push(124.62), sfx=[(0.3, TICK, 0.6)])
shot(126.06, s_still, punch(126.06, 126.2, 1.15, (640, 300)), sfx=[(0.0, TICK, 0.6)], n=2)
shot(126.8, s_big, sfx=[(0.0, HIT, 1.0)], text="RULE 2", sub="NO RUNNING", bg=RED_, size=150)
shot(127.8, s_hall, push(127.8), sfx=[(0.2, POP, 0.7)], action="look", sign="NO RUNNING", hud=True)
shot(129.36, s_hall, push(129.36), sfx=[(0.0, "step.wav", 0.4), (0.6, "step.wav", 0.4)], action="run_slow",
     sign="NO RUNNING")
shot(131.06, s_purchase, punch(131.06, 131.4, 1.06), sfx=[(0.0, POP, 0.8)], mode="card")
shot(132.84, s_purchase, punch(132.84, 133.0, 1.1), sfx=[(0.0, "chaching.wav", 0.8)], mode="card")
shot(134.6, s_purchase, push(134.6), sfx=[(0.6, "click.wav", 1.0), (0.9, "success.wav", 0.7)], mode="buy")
shot(135.92, s_hall, push(135.92), sfx=[(0.0, "whoosh.wav", 0.9)], action="sprint", hud=True)
shot(138.98, s_bonk, punch(138.98, 139.53, 1.1, (700, 360)), sfx=[(0.55, BOOM, 1.2)], shake=(0.55, 22))
shot(141.02, s_cu, punch(141.02, 142.6, 1.08, (560, 330)), sfx=[(0.2, SPARK, 0.9)], who="stone", expr="smug",
     bg=Y, arms=("hip", "down"), prop=crown_prop, label="GOLDEN CROWN", label_t=141.8, label_bg=st.UI_DARK)
shot(144.74, s_cu, sfx=[(0.0, HIT, 0.9)], who="stone", expr="smug", bg=RED_, arms=("cross", "cross"),
     label="[ADMIN]", label_t=144.8, label_bg=st.RED)
shot(146.38, s_command, sfx=[(0.1, "type_key.wav", 0.6), (0.5, "type_key.wav", 0.6), (0.9, HIT, 0.8)],
     cmd="/detention")
shot(147.68, s_ui, push(147.68), sfx=[(0.0, SW, 0.6), (0.3, "buzz.wav", 0.7)], kind="system",
     lines=("Teleported to:", "DETENTION"))
shot(150.54, s_roof, punch(150.54, 151.8, 1.1, (640, 400)), sfx=[(0.3, "thud.wav", 0.8), (1.2, TICK, 0.5)],
     hud=True)
shot(153.76, s_big, sfx=[(0.0, HIT, 1.0)], text="RULE 3", sub="CHAT BUBBLES", bg=PUR, size=150)
shot(154.56, class_scene, punch(154.56, 155.6, 1.06), sfx=[(0.4, POP, 0.6), (0.8, POP, 0.6), (1.2, POP, 0.6)],
     board="RULE 3", teacher=False, bubbles=((420, "hi", 154.8), (860, "lol", 155.2), (1090, "...", 155.6)),
     hud=True)
shot(158.14, s_whisper, punch(158.14, 159.6, 1.08, (640, 360)), sfx=[(0.3, SW, 0.4)])
shot(160.04, s_whisper, push(160.04, 1.05), sfx=[(0.0, POP, 0.9)], bubble="MS. PEBBLE LOOKS LIKE A BAKED POTATO",
     bt=160.04)
shot(162.28, class_scene, punch(162.28, 162.5, 1.06), sfx=[(0.1, HIT, 0.9), (0.4, "murmur.wav", 0.6)],
     board="BE QUIET", heads_t=162.3, teacher=False,
     bubbles=((640, "MS. PEBBLE LOOKS LIKE A BAKED POTATO", 162.0),))
shot(164.12, s_cu, sfx=[(0.0, "sting_low.wav", 0.8)], who="pebble", keys=[(0, "neutral"), (164.6, "cold")],
     bg=GRY, arms=("cross", "cross"), snap=164.6)
shot(165.5, s_cu, sfx=[(0.0, POP, 0.6)], who="pebble", expr="cold", bg=GRY, arms=("cross", "cross"),
     bubble="I CAN READ.", btime=165.5)
shot(166.46, s_command, sfx=[(0.1, "type_key.wav", 0.6), (0.6, HIT, 0.8)], cmd="/mute", who="pebble", bg=GRY)
shot(167.76, class_scene, push(167.76), sfx=[(0.3, TICK, 0.5), (1.5, TICK, 0.5), (2.7, TICK, 0.5)],
     board="SILENT READING", mute=True, clock_h=12.0, hud=True)
shot(170.4, s_cu, sfx=[(0.0, POP, 0.6)], who="kid", expr="sad", bg=GRY, bubble="...", btime=170.4)
shot(172.42, s_news, sfx=[(0.0, "sting.wav", 0.8)], text="DAD'S UPDATE?")
shot(173.38, s_parking, punch(173.38, 173.5, 1.08), sfx=[(0.1, DING, 0.7)], stage=7, dad="sweat", night=0.8,
     label="STAGE 7", label_t=173.4)
shot(174.26, s_cu, sfx=[(0.0, POP, 0.6)], who="dad", expr="worried", bg=GRY, arms=("up", "down"),
     bubble="ALMOST THERE, BUDDY.", btime=174.26, type_it=True)

# ---- Day 3 (175.94 - 244.62)
shot(175.94, s_card, sfx=[(0.0, BOOM, 1.1), (0.7, POP, 0.7)], word="DAY", num=3, sub="WEDNESDAY", bg=Y)
shot(177.62, s_cafe, punch(177.62, 177.8, 1.05), sfx=[(0.0, SW, 0.6)], crowd="sit", label="LUNCH!", label_t=177.65,
     hud=True)
shot(178.18, s_cafe, punch(178.18, 180.0, 1.1, (400, 330)), sfx=[(0.5, POP, 0.7), (1.0, POP, 0.7)],
     buttons=True, crowd="sit")
shot(180.74, s_cafe, push(180.74), sfx=[(0.2, DING, 0.6)], buttons=True, kid="neutral", crowd="sit", hud=True)
shot(182.32, s_buttons_cu, sfx=[(0.0, DING, 0.8)], sel=0)
shot(184.36, s_buttons_cu, sfx=[(0.0, DING, 0.8), (1.0, "buzz.wav", 0.4)], sel=1)
shot(185.88, s_cu, sfx=[(0.0, "buzz.wav", 0.7)], who="kid", expr="cry", bg=GRY, arms=("shrug", "shrug"),
     bubble="I SPENT ALL MY ROBUX ON RUNNING!", btime=185.88, type_it=True,
     prop=lambda c, T, hx, hy, s: st.number_counter(c, 900, 600, 0.8, 0, T, col="#ff4f5a", icon=True))
shot(189.0, s_cafe, punch(189.0, 189.6, 1.1, (560, 420)), sfx=[(0.4, "thud.wav", 0.8)], kid="neutral", tray=True,
     crowd="sit", label="MYSTERY MEAT", label_t=189.4)
shot(190.68, s_zombie, sfx=[(0.9, HIT, 1.0), (1.3, "sting.wav", 0.8)])
shot(193.2, s_zombie, punch(193.2, 194.1, 1.12), sfx=[(0.8, TICK, 0.6)])
shot(195.42, s_cafe, punch(195.42, 195.5, 1.08), sfx=[(0.0, BOOM, 1.2)], shake=(0.05, 20), kid="zs",
     crowd="scream", hud=True)
shot(197.6, s_cafe, push(197.6), sfx=[(0.0, "whoosh.wav", 0.9)], kid="z", crowd="run", hud=True)
shot(200.0, s_cafe, punch(200.0, 200.6, 1.06), sfx=[(0.4, POP, 0.8), (1.2, DING, 0.6)], kid="z", crowd="trade",
     trade=200.4)
shot(202.4, s_cafe, punch(202.4, 202.5, 1.12, (640, 330)), sfx=[(0.0, TICK, 0.6)], kid="z", crowd="trade",
     trade=200.0)
shot(204.3, s_toast, punch(204.3, 204.4, 1.08), sfx=[(0.0, POP, 0.9), (0.2, DING, 0.7)])
shot(206.18, s_cu, sfx=[(0.0, "sting_low.wav", 0.8)], who="zombie", expr="scared", bg=GRY, arms=("cover", "cover"),
     bubble="OH NO.", btime=206.3)
shot(207.6, s_mom_cu, sfx=[(0.0, POP, 0.7)], bubble="SWEETIE, YOU FORGOT YOUR LUNCH!",
     prop=lambda c, T, hx, hy, s: ss.juice_box(c, hx + 230, hy + 330, 0.9))
shot(210.54, s_cafe, push(210.54), sfx=[(0.2, "step.wav", 0.5), (0.8, SPARK, 0.8)], lunch=False, crowd="sit",
     mom=True, unicorn_x="walk", hud=True)
shot(212.6, s_cafe, punch(212.6, 213.3, 1.08, (420, 360)), sfx=[(0.6, SPARK, 0.9)], lunch=False, crowd="sit",
     mom=True, unicorn_x=200, label="PET UNICORN", label_t=213.3)
shot(215.1, s_cu, sfx=[(0.0, POP, 0.6)], who="zombie", expr="worried", bg=GRY, arms=("shrug", "shrug"),
     bubble="MOM, JUST LEAVE IT ON THE TABLE!", btime=215.1, type_it=True)
shot(216.9, s_cu, sfx=[(0.0, POP, 0.5)], who="zombie", expr="cry", bg=GRY, arms=("up", "up"), bubble="PLEASE!",
     btime=216.9)
shot(218.48, s_emote, sfx=[(0.0, SW, 0.6), (0.4, POP, 0.6)])
shot(219.92, s_emote, punch(219.92, 220.6, 1.1, (820, 360)), sfx=[(0.5, "click.wav", 0.9)], sel=5)
shot(221.86, s_kiss, punch(221.86, 222.4, 1.08), sfx=[(0.4, POP, 0.9)], hearts=False)
shot(223.98, s_kiss, push(223.98), sfx=[(0.0, SPARK, 1.0), (0.3, POP, 0.6), (0.6, POP, 0.6)], hearts=True)
shot(225.46, s_stare, punch(225.46, 226.6, 1.08), sfx=[(0.2, "murmur.wav", 0.7), (1.0, "chaching.wav", 0.5)],
     hud=True)
shot(228.66, s_cu, punch(228.66, 228.8, 1.12, (450, 260)), sfx=[(0.0, BOOM, 1.1)], shake=(0.1, 22), who="zombie",
     expr="scream", bg=RED_, arms=("up", "up"), bubble="MOOOM!", btime=228.7, snap=228.7)
shot(230.6, s_kiss, push(230.6), sfx=[(0.0, POP, 0.6)], hearts=True)
shot(233.2, s_mom_cu, sfx=[(0.0, SPARK, 0.7)], bubble="LOVE YOU, SWEETIE.", expr="laugh", arms=("wave", "down"))
shot(234.52, s_speaker, punch(234.52, 234.7, 1.08), sfx=[(0.0, "buzz.wav", 0.9)])
shot(236.1, s_stone_mic, punch(236.1, 236.2, 1.06), sfx=[(0.0, "sting.wav", 0.8)])
shot(237.26, s_stone_mic, punch(237.26, 239.8, 1.06), sfx=[(2.5, BOOM, 1.2)], hp_t=239.8)
shot(241.24, s_gym_loading, push(241.24), sfx=[(0.0, "sting_low.wav", 1.0), (1.5, "buzz.wav", 0.6)])

# ---- subscribe CTA (244.62 - 258.78)
shot(244.62, s_hallpass, push(244.62), sfx=[(0.0, SPARK, 0.9), (1.0, "click.wav", 0.9), (1.2, "success.wav", 0.7)])
shot(247.5, s_hallpass, punch(247.5, 247.6, 1.1, (560, 340)), sfx=[(0.0, "chaching.wav", 0.7)])
shot(249.98, s_skip, push(249.98), sfx=[(0.1, "whoosh.wav", 0.9)], what="line", hud=True)
shot(251.48, s_skip, push(251.48), sfx=[(0.1, "whoosh.wav", 0.9)], what="class")
shot(252.94, s_cu, sfx=[(0.0, TICK, 0.6)], who="kid", expr="smirk", bg=GRY, arms=("shrug", "shrug"),
     bubble="DON'T SUBSCRIBE?", btime=252.94)
shot(255.28, s_front_row, punch(255.28, 255.5, 1.08), sfx=[(0.0, POP, 0.7)], stone=False)
shot(256.04, s_front_row, punch(256.04, 256.4, 1.1, (700, 380)), sfx=[(0.2, "sting_low.wav", 0.8)], stone=True)
shot(257.86, s_big, sfx=[(0.0, BOOM, 1.1)], text="FOREVER.", bg=RED_, size=150)

# ---- Day 4 (258.78 - 321.74)
shot(258.78, s_card, sfx=[(0.0, BOOM, 1.1), (0.8, POP, 0.7)], word="DAY", num=4, sub="THURSDAY", bg=PUR)
shot(260.34, s_inventory, push(260.34), sfx=[(0.0, "click.wav", 0.8)], items=("pencil", "eraser", "juice"),
     bg="dark")
shot(261.9, s_inventory, punch(261.9, 262.3, 1.08, (900, 380)), sfx=[(0.3, "sparkle.wav", 0.9)],
     items=("pencil", "eraser", "juice"), extra=262.0, bg="dark")
shot(263.46, s_cu, sfx=[(0.0, HIT, 0.9)], who="kid", expr="shock", bg=PUR, arms=("up", "up"), snap=263.5,
     label="ONLY 3 SLOTS?!", label_t=263.6, label_bg=st.UI_DARK)
shot(265.28, s_inventory, punch(265.28, 265.9, 1.12, (900, 380)), sfx=[(0.3, "page.wav", 0.8)],
     items=("pencil", "eraser", "juice"), extra=0.0, bg="dark", label="A NOTE", label_t=265.6)
shot(267.04, s_note, punch(267.04, 267.96, 1.08), sfx=[(0.0, "page.wav", 0.7), (0.92, HIT, 0.7)])
shot(268.94, s_note, push(268.94, 1.04), sfx=[(0.2, "sting_soft.wav", 0.8)], sign="- Shadow Ninja")
shot(270.88, s_library, push(270.88), sfx=[(0.0, SW, 0.6), (1.5, "type_key.wav", 0.5)], hud=True)
shot(272.8, s_library, punch(272.8, 273.6, 1.12, (700, 360)), sfx=[(0.6, "type_key.wav", 0.6)], kid=False,
     emma="determined")
shot(274.68, s_panel, punch(274.68, 275.2, 1.1, (640, 500)), sfx=[(0.3, "buzz.wav", 0.7)], red=4)
shot(277.02, s_panel, punch(277.02, 277.2, 1.15, (640, 400)), sfx=[(0.0, DING, 0.8)], red=3)
shot(278.26, s_summer, push(278.26), sfx=[(0.2, SPARK, 0.8)])
shot(281.3, s_summer, push(281.3), sfx=[(0.0, BOOM, 1.2)], shake=(0.05, 18), deleted_t=281.3)
shot(282.42, s_cu, punch(282.42, 282.5, 1.12, (450, 260)), sfx=[(0.0, HIT, 1.0)], who="kid", expr="scream",
     bg=RED_, arms=("up", "up"), bubble="DELETED?!", btime=282.42, snap=282.45)
shot(283.14, s_cu, sfx=[(0.0, POP, 0.6)], who="emma", expr="determined", bg=PUR, arms=("cross", "cross"),
     bubble="HE LOVES ROBLOX SCHOOL SO MUCH...", btime=283.14, type_it=True)
shot(285.4, s_cu, sfx=[(0.0, POP, 0.5)], who="stone", expr="laugh", bg=Y, arms=("up", "up"),
     bubble="(NEVER ENDING!)", btime=285.5, side=-1)
shot(287.9, s_cu, sfx=[(0.0, HIT, 0.8)], who="kid", expr="worried", bg=GRY, arms=("shrug", "shrug"),
     bubble="HOW DO WE STOP HIM?!", btime=287.9, type_it=True)
shot(289.74, s_cu, sfx=[(0.0, POP, 0.7)], who="emma", expr="determined", bg=RED_, arms=("point", "down"),
     bubble="BEAT THE FINAL EXAM.", btime=289.74, type_it=True)
shot(291.46, s_crown, sfx=[(0.0, SPARK, 0.9), (1.5, DING, 0.6)], text="NEW ADMIN?")
shot(294.72, s_study, push(294.72), sfx=[(0.2, "page.wav", 0.7)])
shot(296.76, s_cu, sfx=[(0.0, SPARK, 0.7)], who="kid", expr="determined", bg=BLU, arms=("hold", "hold"),
     label="FIRST TIME EVER", label_t=297.2, label_bg=st.UI_DARK,
     prop=lambda c, T, hx, hy, s: ss.book(c, hx, hy + 400, 0.6, T, flip=(T * 1.3) % 1))
shot(299.36, s_study, punch(299.36, 300.0, 1.08), sfx=[(0.3, DING, 0.5), (0.9, DING, 0.5), (1.5, DING, 0.5),
                                                        (2.1, DING, 0.5)], xp=True)
shot(302.22, s_study, push(302.22), sfx=[(0.0, TICK, 0.6), (0.7, TICK, 0.6), (1.6, "success.wav", 0.8)],
     clock=24.0, level=2)
shot(304.94, s_levelup, sfx=[(0.0, "chaching.wav", 0.9)], n0=2, n1=2, who="kid", label="LEVEL 2!")
shot(306.14, class_scene, punch(306.14, 307.4, 1.1, (860, 380)), sfx=[(0.3, SPARK, 0.8)], board="",
     teacher=False, students=[("priya", 860)], kid_x=420, label="LEVEL 99", label_t=306.5)
shot(309.28, s_cu, sfx=[(0.0, POP, 0.6)], who="kid", expr="worried", bg=Y, arms=("up", "up"),
     bubble="PRIYA, WE NEED YOUR LEVEL 99!", btime=309.28, type_it=True)
shot(311.72, s_cu, sfx=[(0.0, TICK, 0.6)], who="priya", expr="cold", bg=PUR, arms=("cross", "cross"),
     bubble="I WORK ALONE.", btime=311.72, side=-1)
shot(313.6, s_cu, sfx=[(0.3, SPARK, 0.8)], who="priya", keys=[(0, "neutral"), (314.6, "happy")], bg=Y,
     arms=("cross", "cross"), bubble="...BUT I REALLY LIKE SUMMER.", btime=313.6, type_it=True, side=-1, snap=314.6)
shot(316.6, s_news, sfx=[(0.0, "sting.wav", 0.8)], text="DAD'S UPDATE")
shot(317.24, s_parking, punch(317.24, 317.4, 1.08), sfx=[(0.1, DING, 0.7)], stage=31, dad="sleep", night=1.0,
     label="STAGE 31", label_t=317.3)
shot(318.48, s_parking, punch(318.48, 319.6, 1.15, (560, 470)), sfx=[(0.3, "murmur.wav", 0.3)], stage=31,
     dad="sleep", night=1.0)
shot(320.32, s_cu, sfx=[(0.0, POP, 0.5)], who="dad", expr="sleepy", bg=GRY, arms=("up", "down"),
     bubble="ALMOST THERE, BUDDY...", btime=320.32, type_it=True)

# ---- Day 5 (321.74 - 426.8)
shot(321.74, s_card, sfx=[(0.0, BOOM, 1.2), (0.6, POP, 0.7)], word="DAY", num=5, sub="FRIDAY", bg=RED_)
shot(322.66, s_gym_doors, push(322.66), sfx=[(0.0, TICK, 0.7), (1.3, "sting_low.wav", 1.0), (1.6, "whoosh.wav",
                                                                                                0.7)])
shot(324.9, s_gym_doors, punch(324.9, 325.9, 1.15, (640, 420)), sfx=[(0.5, BOOM, 1.0)])
shot(326.8, s_boss, push(326.8, 0.95, (640, 380)), sfx=[(0.0, "sting.wav", 1.0), (0.4, BOOM, 1.3)],
     shake=(0.4, 18), s=0.62, label="FINAL EXAM", label_t=327.2, kids=True)
shot(330.04, s_boss, punch(330.04, 330.6, 1.1, (640, 250)), sfx=[(0.3, "whoosh.wav", 0.7)], s=0.7)
shot(331.6, s_boss, punch(331.6, 331.8, 1.3, (640, 200)), sfx=[(0.1, HIT, 0.8)], s=0.7, jaw=1.0, rage=1.0)
shot(332.6, s_boss, push(332.6), sfx=[(0.1, BOOM, 1.0)], s=0.62, hp=1.0, rage=1.0, label="10,000 HP",
     label_t=332.7)
shot(333.7, s_boss, punch(333.7, 333.8, 1.2, (640, 220)), sfx=[(0.0, "sting.wav", 0.9)], shake=(0.0, 16),
     s=0.7, rage=1.0)
shot(335.04, s_fireball, push(335.04), sfx=[(0.1, "whoosh.wav", 1.0), (1.5, BOOM, 1.2)], shake=(1.55, 20))
shot(338.5, s_panic, push(338.5), sfx=[(0.0, "sting.wav", 0.8), (0.4, "murmur.wav", 0.8)])
shot(340.6, s_boom, push(340.6), sfx=[(0.0, BOOM, 1.3)], shake=(0.0, 22))
shot(342.6, s_panic, punch(342.6, 343.4, 1.1), sfx=[(0.5, "whoosh.wav", 0.7), (1.2, HIT, 0.7)])
shot(344.66, s_answers, push(344.66), sfx=[(0.1, POP, 0.6), (0.3, POP, 0.6), (0.5, POP, 0.6)], hud=True)
shot(345.96, s_boss, punch(345.96, 346.1, 1.08), sfx=[(0.1, HIT, 0.8)], s=0.55, hp=0.9998, dmg=("-2", 346.0))
shot(346.92, s_countdown, sfx=[(0.0, "buzz.wav", 0.9), (1.2, TICK, 0.7), (2.2, TICK, 0.7)], n=60)
shot(349.78, s_cu, sfx=[(0.0, HIT, 0.8)], who="kid", expr="scream", bg=RED_, arms=("up", "up"),
     bubble="WE'RE TOO SLOW!", btime=349.78)
shot(351.18, s_cu, punch(351.18, 351.7, 1.1, (580, 330)), sfx=[(0.4, DING, 0.9)], who="kid",
     keys=[(0, "worried"), (351.6, "stars")], bg=PUR, arms=("point", "down"), bubble="WAIT. RULE 3.",
     btime=351.18, snap=351.6)
shot(352.32, s_cu, sfx=[(0.0, POP, 0.7)], who="kid", expr="determined", bg=Y, arms=("point", "up"),
     bubble="PRIYA, SAY EVERY ANSWER OUT LOUD!", btime=352.32, type_it=True)
shot(355.34, s_cu, sfx=[(0.0, POP, 0.8), (0.9, POP, 0.8), (2.4, POP, 0.8)], who="priya", expr="smug", bg=PUR,
     arms=("up", "point"), side=-1, bubble="42! PHOTOSYNTHESIS! 1776!", btime=355.34, type_it=True)
shot(358.98, s_bubbles, push(358.98, 1.0), sfx=[(0.3, SPARK, 0.8), (1.6, POP, 0.6)])
shot(362.42, s_bubbles, push(362.42), sfx=[(0.3, POP, 0.6), (0.6, POP, 0.6), (0.9, POP, 0.6), (1.2, POP, 0.6)],
     crowd=True)
shot(366.94, s_combo, punch(366.94, 367.1, 1.08), sfx=[(0.0, BOOM, 1.3), (0.4, "chaching.wav", 0.7)],
     shake=(0.05, 20), hp=1.0)
shot(370.16, s_combo, push(370.16), sfx=[(0.1, HIT, 1.0), (0.5, "sparkle.wav", 0.7)], text="-9,000!", hp=0.1,
     dmg="-9,000")
shot(371.78, s_countdown, sfx=[(0.0, "buzz.wav", 0.9)], n=30)
shot(373.38, s_boss, punch(373.38, 373.5, 1.2, (640, 220)), sfx=[(0.0, "sting.wav", 0.9)], shake=(0.1, 14),
     s=0.7, rage=1.0, hp=0.1)
shot(374.64, s_hit, push(374.64), sfx=[(0.0, BOOM, 1.1)], shake=(0.0, 20), hp=0.02)
shot(376.56, s_hit, punch(376.56, 377.2, 1.12, (420, 360)), sfx=[(0.1, HIT, 0.9), (0.6, "buzz.wav", 0.6)], hp=0.02)
shot(378.46, s_cu, sfx=[(0.0, POP, 0.8)], who="leo", expr="determined", bg=GRN, arms=("up", "down"),
     bubble="GOT IT!", btime=378.46)
shot(379.2, s_juice_throw, push(379.2), sfx=[(0.4, "swish.wav", 0.9), (1.8, POP, 0.7)])
shot(381.4, s_juice_throw, punch(381.4, 381.6, 1.15, (640, 300)), sfx=[(0.0, "whoosh.wav", 0.6)])
shot(382.78, s_heal, sfx=[(0.0, "success.wav", 1.0), (0.3, SPARK, 0.7)])
shot(385.12, s_cu, sfx=[(0.0, POP, 0.7)], who="kid", expr="laugh", bg=GRN, arms=("up", "hold"),
     bubble="THAT'S WHY I HAD A JUICE BOX!", btime=385.12, type_it=True,
     prop=lambda c, T, hx, hy, s: ss.juice_box(c, hx + 230, hy + 260, 0.9))
shot(387.6, s_mom_unicorn, push(387.6), sfx=[(0.0, POP, 0.9), (0.3, DING, 0.7), (0.8, SPARK, 0.9)], hud=True)
shot(389.6, s_mom_unicorn, punch(389.6, 389.7, 1.15, (560, 300)), sfx=[(0.2, "boing.wav", 0.7)], toast=False)
shot(391.32, s_mom_cu, sfx=[(0.0, POP, 0.7)], bubble="GO GET 'EM, SWEETIE!", expr="laugh", arms=("up", "up"))
shot(392.52, s_countdown, sfx=[(0.0, "buzz.wav", 0.9)], n=10)
shot(393.76, s_owned, sfx=[(0.0, "success.wav", 0.9), (0.3, DING, 0.7)])
shot(396.68, s_sprint_jump, push(396.68), sfx=[(0.1, "whoosh.wav", 0.9), (1.5, "boing.wav", 0.9)], part=1)
shot(399.72, s_sprint_jump, punch(399.72, 400.4, 1.1, (520, 300)), sfx=[(0.4, "chaching.wav", 0.8),
                                                                       (1.0, "boing.wav", 0.9)], part=2)
shot(401.9, s_sprint_jump, push(401.9), sfx=[(0.2, "whoosh.wav", 0.7)], part=2)
shot(403.88, s_cu, sfx=[(0.0, SPARK, 0.8)], who="dad", expr="laugh", bg=GRN, arms=("up", "up"),
     bubble="MADE IT, BUDDY!", btime=403.88)
shot(404.92, s_swing, push(404.92), sfx=[(0.6, "whoosh.wav", 1.0), (1.1, HIT, 1.0)])
shot(406.86, s_erased, push(406.86), sfx=[(0.0, BOOM, 1.4), (0.3, SPARK, 0.9)], shake=(0.0, 24))
shot(407.7, s_ui, push(407.7), sfx=[(0.0, "success.wav", 1.0)], kind="system",
     lines=("FINAL EXAM", "DEFEATED"))
shot(409.62, s_new_admin, push(409.62), sfx=[(0.3, "whoosh.wav", 0.6), (0.8, SPARK, 1.0), (1.2, "chaching.wav",
                                                                                              0.7)])
shot(413.1, s_cu, sfx=[(0.0, POP, 0.6)], who="stone", expr="worried", bg=GRY, arms=("point", "down"),
     bubble="/DETENTION?", btime=413.1)
shot(414.7, s_ui, push(414.7), sfx=[(0.0, "buzz.wav", 1.0)], kind="dialog", title="Error",
     msg="Command not found.", button="OK", col="#e8323a")
shot(416.2, s_cheer, push(416.2), sfx=[(0.3, "murmur.wav", 0.8), (1.2, POP, 0.6), (2.6, POP, 0.6)], hud=True)
shot(419.3, s_cheer, punch(419.3, 419.5, 1.1, (640, 250)), sfx=[(0.2, SPARK, 0.7)])
shot(420.42, s_cu, sfx=[(0.0, TICK, 0.6)], who="kid", expr="cold", bg=GRY, arms=("down", "down"),
     bubble="I REALLY NEED TO CHANGE THAT NAME.", btime=420.42, type_it=True,
     prop=lambda c, T, hx, hy, s: ss.crown(c, hx, hy - 0.95 * U1 * s, 0.35, T))
shot(423.08, s_command, sfx=[(0.1, "type_key.wav", 0.6), (0.6, "type_key.wav", 0.6), (1.1, DING, 0.8)],
     cmd="/summer", who="kid", bg=Y)
shot(424.56, s_summer, push(424.56), sfx=[(0.0, "success.wav", 1.0), (0.3, SPARK, 0.9)], restored=True)

# ---- resolution + loop (426.8 - 464.6)
shot(426.8, s_bell, punch(426.8, 427.9, 1.08), sfx=[(1.0, "bell.wav", 1.0)], ring=True)
shot(428.86, s_bell, push(428.86), sfx=[(0.1, "bell.wav", 0.8)], ring=True)
shot(429.98, s_normal, push(429.98), sfx=[(0.1, POP, 0.6)], what="lockers")
shot(431.72, s_normal, punch(431.72, 433.2, 1.1, (640, 470)), sfx=[(0.3, "thud.wav", 0.6)], what="meat")
shot(434.22, s_normal, push(434.22), sfx=[(0.2, "page.wav", 0.6)], what="priya")
shot(436.32, s_normal, push(436.32), sfx=[(0.2, SPARK, 0.6)], what="emma")
shot(437.88, s_normal, push(437.88), sfx=[(0.0, "whoosh.wav", 0.6)], what="car")
shot(439.64, s_normal, punch(439.64, 440.0, 1.15, (700, 520)), sfx=[(0.2, DING, 0.6)], what="car")
shot(441.2, s_cu, sfx=[(0.0, POP, 0.6)], who="dad", expr="laugh", bg=Y, arms=("up", "down"),
     bubble="TOLD YOU I'D MAKE IT, BUDDY!", btime=441.2, type_it=True)
shot(442.54, s_normal, push(442.54), sfx=[(0.3, "sting_soft.wav", 0.7)], what="home")
shot(444.44, s_cu, punch(444.44, 444.5, 1.08, (560, 360)), sfx=[(0.0, TICK, 0.6)], who="kid", expr="smirk",
     bg=GRY, arms=("down", "down"), label="MOSTLY.", label_t=444.5)
shot(444.88, s_mom_cu, sfx=[(0.0, POP, 0.7)], bubble="SWEETIE, YOUR REPORT CARD CAME!", expr="happy",
     arms=("up", "hold"))
shot(447.04, s_report, push(447.04), sfx=[(0.6, HIT, 0.8)], k1=447.6)
shot(449.88, s_report, punch(449.88, 450.5, 1.08, (640, 470)), sfx=[(0.3, "success.wav", 1.0)], k1=0.0, k2=450.2)
shot(452.2, s_mom_cu, sfx=[(0.0, POP, 0.6)], bubble="IS LEVEL 1 GOOD?", expr="worried", arms=("hold", "down"))
shot(453.34, s_cu, sfx=[(0.0, TICK, 0.6)], who="kid", expr="forced", bg=Y, arms=("down", "down"),
     bubble="...YES!", btime=453.34)
shot(454.28, s_comments, push(454.28), sfx=[(0.3, POP, 0.6), (0.9, "type_key.wav", 0.6), (1.3, "type_key.wav",
                                                                                                0.6)])
shot(457.0, s_update, punch(457.0, 459.0, 1.06), sfx=[(0.0, DING, 0.9), (2.0, TICK, 0.6)])
shot(461.42, s_mom_cu, sfx=[(0.0, POP, 0.7)], bubble="ALREADY PRESSED YES, SWEETIE!", expr="laugh",
     arms=("wave", "down"),
     prop=lambda c, T, hx, hy, s: st.tablet(c, hx + 260, hy + 330, 0.45, T))
shot(463.14, s_cu, punch(463.14, 463.2, 1.15, (450, 260)), sfx=[(0.0, BOOM, 1.2)], shake=(0.05, 22), who="kid",
     expr="scream", bg=RED_, arms=("up", "up"), bubble="MOM!", btime=463.14)
SHOTS = S
S.sort(key=lambda sh: sh["start"])
_rw_draw, _rw_ov = st.rewind_shot(SHOTS, [441.0, 381.0, 305.0, 225.0, 140.0, 0.0])
S.append(dict(start=463.75, draw=_rw_draw, keys=[(463.75, 1.0, C)], overlay=_rw_ov, blur=False, vignette=0.12))
SFX.append((463.75, "whip.wav", 0.9))
for k, s in enumerate(SHOTS):
    s["end"] = SHOTS[k + 1]["start"] if k + 1 < len(SHOTS) else TOTAL

if __name__ == "__main__":
    import json
    import audio
    json.dump([{"time": round(t, 3), "file": f, "volume": round(v * SFX_GAIN, 3)} for t, f, v in sorted(SFX)],
              open(sys.argv[2], "w"), indent=1)
    out_dir = os.path.dirname(os.path.abspath(sys.argv[2]))
    if not os.path.exists(os.path.join(out_dir, "music.wav")):
        audio.save(os.path.join(out_dir, "music.wav"), audio.music_game(TOTAL, **MUSIC))
    engine.set_voice(os.path.join(out_dir, "voice.mp3"))
    kw = {}
    if len(sys.argv) > 4:
        kw["frames"] = (int(sys.argv[3]), int(sys.argv[4]))
    render(SHOTS, TOTAL, sys.argv[1], xfade=0.0, grain=2, fade_out=0.0, fade_in=0.0, **kw)

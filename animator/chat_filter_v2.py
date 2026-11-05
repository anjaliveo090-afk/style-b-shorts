"""Story v2: "This Noob Is the REASON Roblox Has a Chat Filter" (Benny) - the engagement remake.

Same voice + SRT as chat_filter.py (output/chat_filter_v2/voice.mp3, 59.1 s). What changed from v1, and why:
  - every beat has its own place or framing (v1 held the house, the crowd and the hiding spot for 2-3.5 s);
  - stronger hook: the stake ("I'M WATCHING YOU" getting FILTERED) in the first frame, then 3 more pictures
    by 1.9 s (lessons.md rule 1), and the filter machine slamming in on "chat filter";
  - a visual metaphor for the payoff: the CHAT FILTER machine eats scary words and spits out '#' tiles;
  - big set pieces instead of static UI: a door peephole, a CCTV wall, a siren, a scrolling wall of scary
    messages, hiding spots that come back as the payoff, three different "####!" yells;
  - a sound-word sticker on every physical action, 6 whip pans, impact bumps, more moving FX (non-camera
    motion was 4.4 in v1).
Voiced bursts measured in the voice: "My name is ####!" 44.95-46.75, "He tried again." 46.8-47.45, then
"####!" x3 at 47.55, 48.75, 49.95 (each ~1.1 s). Benny's lip-sync runs only on those (the user's rule).

Scenes use ABSOLUTE time T; a shot wraps a scene with at(scene, start).
Run (from animator/):
  python3 chat_filter_v2.py ../output/chat_filter_v2/clips/animation.mp4 ../output/chat_filter_v2/cues.json"""
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
engine.LIPSYNC = True
TOTAL = 60.0
SFX_GAIN = 0.28
MUSIC = dict(bpm=128, perc=0.6, dips=[(42.9, 44.9)])     # quieter while Benny tries to explain himself
DIALOGUE = {"benny": [(44.95, 46.75), (47.55, 51.05)]}

BENNY = Block("#ff8a3d", pants="#2b3f8f", skin="#e9c22c", hair=None, sleeves="skin", shoes=None, cap="#ffd84a")
MOD = Block("#2f6bd8", pants="#2b2f45", skin="#f0c9a8", hair="smooth", hair_col="#3a2a2a", outfit="hoodie",
            shoes="dark", glasses=True)
DEV = Block("#3b3f5a", pants="#2b2f45", skin="#f0c9a8", hair="spiky", hair_col="#2a1a14", outfit="hoodie",
            glasses=True, headset="#4f8bff", shoes="dark")
P = [style.crowd_member(i) for i in range(14)]
LAVA_GUY, COZY = P[2], P[4]
NAMES = st.ROBLOX_NAMES

U1 = Block.HW * 64
FACE_S = 4.2
FACE_KEEP = [(165, 300, 555, 760)]
SCARY = ["I'M WATCHING YOU", "YOU'RE GOING TO DIE", "I KNOW WHERE YOU LIVE", "I HAVE EVERYONE'S NAMES"]


def talking(who, T):
    return any(a <= T <= b for a, b in DIALOGUE[who])


def snap_at(T, t0):
    return (T - t0) if T >= t0 else None


def at(fn, T0):
    return lambda ctx, t, d: fn(ctx, T0 + t, d)


def closeup(ctx, ch, expr, T, x=360, look=0.0, arms=("down", "down"), s=FACE_S, talk=False, bob=0.35, dy=0,
            snap=None):
    ch.draw(ctx, x, 560 + 2.5 * U1 * s + dy, s, expr, T, arms=arms, look=look, talk=talk, bob=bob, snap=snap)


def benny(ctx, x, y, s, expr, T, tag=True, name="Benny", **kw):
    BENNY.draw(ctx, x, y, s, expr, T, **kw)
    if tag:
        st.name_pill(ctx, x, y - 3.5 * U1 * s, name, size=max(20, 24 * s))


def world(ctx, T, y=1000):
    st.game_sky(ctx)
    st.block_clouds(ctx, T)
    st.baseplate(ctx, y)


def typed(txt, T, t0, cps=22):
    return txt[:max(0, int((T - t0) * cps))]


def halo(ctx, x, y, r, T):
    ctx.save()
    ctx.translate(x, y + math.sin(T * 4) * 6)
    ctx.scale(1, 0.32)
    ctx.new_sub_path()
    ctx.arc(0, 0, r, 0, 2 * PI)
    ctx.restore()
    ctx.set_source_rgb(*hexc("#9a6a1c"))
    ctx.set_line_width(22)
    ctx.stroke_preserve()
    ctx.set_source_rgb(*st.GOLD)
    ctx.set_line_width(14)
    ctx.stroke()


def shield(ctx, x, y, s, k):
    if k < 0:
        return
    sc = s * pop(k)
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(sc, sc)
    ctx.move_to(0, -120)
    ctx.curve_to(60, -100, 100, -100, 110, -90)
    ctx.curve_to(110, 20, 70, 90, 0, 130)
    ctx.curve_to(-70, 90, -110, 20, -110, -90)
    ctx.curve_to(-100, -100, -60, -100, 0, -120)
    ctx.close_path()
    style.shape_fill(ctx, hexc("#4fd16a"), 7, -120, 130)
    ctx.restore()
    st.check_mark(ctx, x, y, 60 * s, k / 0.25)


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


def pop_out(ctx, ch, x, y, s, T, t0, expr="happy", rise=1.0):
    """A character rising out of a hiding spot (drawn BEFORE the spot so the spot hides its body)."""
    k = clamp((T - t0) / 0.25) if T >= t0 else 0.0
    ch.draw(ctx, x, y + (1 - ease(k)) * 2.6 * U1 * s - (0.3 * U1 * s * rise if k > 0 else 0), s, expr, T,
            arms=("up", "up") if k > 0 else ("down", "down"), shadow=False)


# ================================================================ hook (0 - 2.7 s)
def s_hook(ctx, T, d):
    st.burst(ctx, T, "#d6a8ff", "#5a1fa0", cy=560, spin=0.5)
    closeup(ctx, BENNY, keyed(T, [(0, "crazy"), (0.32, "smug")]), T, arms=("hold", "hold"), snap=snap_at(T, 0.32))
    txt = "I'M WATCHING YOU" if T < 0.47 else "####"
    st.speech_bubble(ctx, 360, 250, txt, 50, 1.0, tail=(0, 1))
    if T >= 0.47:
        st.stamp(ctx, 360, 255, "FILTERED", T - 0.47, size=64)
    label(ctx, "THIS NOOB", 360, 955, 74, fg=st.YELLOW, scale=1.0)


def s_machine(ctx, T, d, t_land=2.0, words_t=2.15, out_t=2.45, glow_a=0.45):
    """The CHAT FILTER machine drops in and lands at t_land; a scary word falls into the funnel, '#' pops out."""
    st.burst(ctx, T, "#c4d8ff", "#2f3f9a", cy=600, spin=0.3)
    drop = 0.0 if T >= t_land else (1 - ease(clamp((T - (t_land - 0.25)) / 0.25))) * 700
    fx, fy, cx, cy = st.filter_machine(ctx, 280, 1000 - drop, 0.85, T, glow_a=glow_a if T >= t_land else 0.0)
    if T >= t_land:
        st.dust(ctx, 280, 1000, clamp((T - t_land) / 0.45), n=7, spread=200)
        st.sfx_word(ctx, 520, 420, "SLAM!", T - t_land, col=st.RED, size=52)
    k = T - words_t
    if 0 <= k < 0.4:
        p = clamp(k / 0.3)
        st.word_block(ctx, lerp(200, fx, p), lerp(220, fy, p * p), "DIE", 1.0 - 0.6 * p, rot=p * 2)
    for i in range(3):
        k2 = T - (out_t + i * 0.12)
        if k2 >= 0:
            p = clamp(k2 / 0.45)
            st.word_block(ctx, lerp(cx, 420 + i * 60, p), cy - 200 * math.sin(PI * p) + (975 - cy) * p, "#",
                          0.7 * min(1.0, pop(k2) + 0.2), col=st.GREEN)


# ================================================================ Benny + "safe"
def s_spawn(ctx, T, d):
    world(ctx, T, 1000)
    st.spawn_pad(ctx, 360, 1000, 1.4, beam=clamp(1 - (T - 2.75) / 0.6))
    k = T - 2.8
    if k >= 0:
        ctx.save()
        ctx.translate(360, 1000)
        ctx.scale(1, pop(k))
        ctx.translate(-360, -1000)
        benny(ctx, 360, 1000, 1.2, keyed(T, [(0, "happy"), (3.29, "grin")]), T, arms=("wave", "down"),
              snap=snap_at(T, 3.29))
        ctx.restore()
    st.sparkles(ctx, T, 360, 760, spread=220, n=12, seed=6, c=(1, 1, 1))
    label(ctx, "BENNY", 360, 300, 80, fg=st.GREEN, scale=pop(T - 3.29) if T >= 3.29 else 0.0)


def s_angel(ctx, T, d):
    st.burst(ctx, T, "#fff6c4", "#8fd0ff", cy=560, spin=0.3)
    closeup(ctx, BENNY, keyed(T, [(0, "happy"), (4.15, "stars")]), T, arms=("hold", "hold"), snap=snap_at(T, 4.15))
    halo(ctx, 360, 330, 150, T)
    st.hearts(ctx, T, 3.85, 360, 520, n=6, seed=4)


def s_safe(ctx, T, d):
    world(ctx, T, 1000)
    shield(ctx, 360, 600, 1.4, T - 5.14)
    for i, x in enumerate((120, 230, 490, 600)):
        P[i + 6].draw(ctx, x, 1000, 0.85, keyed(T, [(0, "neutral"), (5.14, "happy")]), T,
                      arms=("up", "up") if T >= 5.14 else ("down", "down"), look=0.4 if x < 360 else -0.4)
    benny(ctx, 360, 1000, 1.0, "laugh", T, arms=("up", "up"))
    label(ctx, "SAFE!", 360, 300, 84, fg=st.GREEN, scale=pop(T - 5.14) if T >= 5.14 else 0.0)


# ================================================================ obby: "I'm watching you"
def s_obby(ctx, T, d):
    tops = st.obby(ctx, T, y_lava=1060, y_top=930, x0=-80, dx=230, rise=-30, nums=False)
    (x0, y0), (x1, y1) = tops[0], tops[1]
    p = clamp((T - 5.7) / 0.6)
    x, y = lerp(x0 + 40, x1, p), lerp(y0, y1, p) - math.sin(PI * p) * 260
    benny(ctx, x, y, 0.95, "laugh" if p < 1 else "grin", T, arms=("up", "up"), pose="jump" if 0 < p < 1 else "stand",
          tag=p >= 1)
    st.sfx_word(ctx, x1 + 40, y1 - 300, "BOING!", T - 6.3, col=st.PINK, size=50)
    st.game_toast(ctx, 360, 210, "Benny", "joined the game", T - 5.62, icon_col=st.YELLOW)


def s_type(ctx, T, d):
    st.burst(ctx, T, "#ffe27a", "#f29a2e", cy=560, spin=0.4)
    closeup(ctx, BENNY, "grin", T, arms=("hold", "hold"), dy=40)
    st.keyboard(ctx, 360, 950, 1.0, T, mash=1.0)
    st.sfx_word(ctx, 180, 380, "TAP TAP", T - 6.8, col=st.BLUE, size=40, tilt=-0.15)


def s_watch(ctx, T, d):
    st.void_bg(ctx, top="#2a1340", bottom="#0b0614", y0=200, y1=1200)
    st.glow(ctx, 360, 560, 420, (0.7, 0.2, 0.9), 0.4)
    msg = typed("I'm watching you.", T, 7.21, cps=26)
    st.chat_box(ctx, 50, 380, 620, 260, [("Benny", msg, "#ffd84a")] if msg else [], T, size=46, title="Chat")
    for i, (x, y, txt) in enumerate(((180, 770, "??"), (520, 760, "bro"), (360, 900, "HUH"))):
        if T >= 7.95 + i * 0.1:
            st.speech_bubble(ctx, x, y, txt, 44, T - 7.95 - i * 0.1, tail=(0, -1))


def viewfinder(ctx, T, who="BloxKid"):
    ctx.set_source_rgb(1, 1, 1)
    ctx.set_line_width(9)
    for x, y, dx, dy in ((80, 330, 1, 1), (640, 330, -1, 1), (80, 960, 1, -1), (640, 960, -1, -1)):
        ctx.move_to(x, y + dy * 70)
        ctx.line_to(x, y)
        ctx.line_to(x + dx * 70, y)
    ctx.stroke()
    if int(T * 2.5) % 2 == 0:
        ctx.new_sub_path()
        ctx.arc(120, 375, 13, 0, 2 * PI)
        ctx.set_source_rgb(*st.RED)
        ctx.fill()
    st.bold_text(ctx, "REC", 168, 375, 30, (1, 1, 1), shadow=False, stroke=0.15)


def s_spectate(ctx, T, d):
    tops = st.obby(ctx, T, y_lava=1060, y_top=900, x0=-120, dx=260, rise=-20, nums=False)
    x, y = tops[1]
    hop = abs(math.sin((T - 8.17) * 5)) * 120
    P[0].draw(ctx, x + 60, y - hop, 0.95, "happy", T, arms=("up", "up"), pose="jump" if hop > 20 else "stand")
    viewfinder(ctx, T)
    st.spectate_pill(ctx, 360, 260, 1.2, txt="SPECTATING: BloxKid")
    st.face_icon(ctx, 590, 860, 34, "#e9c22c", "#ffd84a", expr="grin")


# ================================================================ the server runs away
def crowd_line(ctx, T, expr, y=1000, s=0.75, arms=("down", "down")):
    xs = (90, 180, 270, 450, 540, 630)
    for i, x in enumerate(xs):
        P[i].draw(ctx, x, y, s, expr, T, arms=arms, look=0.5 if x < 360 else -0.5)
    return xs


def s_freeze(ctx, T, d):
    world(ctx, T, 1000)
    shocked = T >= 9.53
    crowd_line(ctx, T, "shock" if shocked else "happy", arms=("up", "up") if shocked else ("wave", "down"))
    benny(ctx, 360, 1000, 0.95, "grin", T, arms=("wave", "down"))
    if shocked:
        for i, x in enumerate((90, 270, 450, 630)):
            st.bold_text(ctx, "!", x, 760, 60 * min(1.0, pop(T - 9.53 - i * 0.05) + 0.1), st.RED)


def s_run(ctx, T, d):
    world(ctx, T, 1000)
    k = clamp((T - 9.99) / 0.9)
    for i in range(6):                       # they run away into the distance (shrinking, inside the zone)
        x0 = 360 + (i - 2.5) * 70
        side = -1 if i < 3 else 1
        q = ease(k)
        x = lerp(x0, 360 + side * (120 + (i % 3) * 70), q)
        y = lerp(1000, 900, q)
        sc = lerp(0.8, 0.28, q)
        P[i].draw(ctx, x, y, sc, "scream", T, pose="run", walk_phase=T * 3.5, arms=("up", "up"))
        if k > 0:
            st.dust(ctx, x - side * 40 * sc, y, (T * 2 + i * 0.2) % 1, n=3, spread=40 * sc, r=18 * sc)
    st.speed_lines(ctx, T, 360, 800, n=18, r0=200, r1=700, a=0.3)
    benny(ctx, 360, 1000, 0.95, keyed(T, [(0, "grin"), (10.62, "worried")]), T, arms=("shrug", "shrug"))
    st.sfx_word(ctx, 360, 500, "ZOOM!", T - 10.0, col=st.BLUE, size=60)
    if T >= 10.62:
        st.speech_bubble(ctx, 470, 680, "?", 56, T - 10.62, tail=(-1, 1))


# ================================================================ the lava player
def s_spot(ctx, T, d):
    st.burst(ctx, T, "#bfe3ff", "#2f6bd8", cy=560, spin=0.4)
    closeup(ctx, BENNY, keyed(T, [(0, "neutral"), (11.36, "shock")]), T, arms=("hold", "hold"), snap=snap_at(T, 11.36))
    binoculars(ctx, 360, 545, 1.5)
    if T >= 11.36:
        st.speech_bubble(ctx, 560, 300, "!", 70, T - 11.36, tail=(-1, 1))


def s_edge(ctx, T, d):
    st.game_sky(ctx)
    st.block_clouds(ctx, T)
    st.lava(ctx, 1000, T)
    st.platform(ctx, 40, 780, 300, "#2cd5fc", h=80)
    wob = math.sin(T * 9) * 0.25
    LAVA_GUY.draw(ctx, 300, 780, 0.95, "scared", T, arms=("up", "down"), lean=wob)
    st.name_pill(ctx, 300, 780 - 3.45 * U1 * 0.95, "LavaJumper", size=24)
    style.sweat(ctx, 360, 600, 0.8, T)
    for i in range(4):
        bx = 380 + i * 70
        kk = (T * 1.5 + i * 0.3) % 1
        ctx.new_sub_path()
        ctx.arc(bx, 1000 - 40 * kk, 16 * (1 - kk) + 4, 0, 2 * PI)
        ctx.set_source_rgba(1, 0.85, 0.3, 0.8 * (1 - kk))
        ctx.fill()
    label(ctx, "NEAR LAVA", 360, 300, 72, bg=st.RED, scale=pop(T - 12.55) if T >= 12.55 else 0.0)


def s_die(ctx, T, d):
    st.void_bg(ctx, top="#4a0b14", bottom="#12020a", y0=200, y1=1200)
    closeup(ctx, BENNY, "cold", T, arms=("hold", "hold"))
    st.tint(ctx, (0.6, 0.0, 0.05), 0.25)
    st.glow(ctx, 360, 980, 380, (1, 0.3, 0.2), 0.45)                  # lit from below
    msg = typed("You're going to die.", T, 13.18, cps=24)
    if msg:
        st.speech_bubble(ctx, 360, 260, msg, 44, 1.0, tail=(0, 1), col=(1, 0.92, 0.92), fg=st.RED)


def s_what(ctx, T, d):
    st.burst(ctx, T, "#ffd27a", "#ff7a1a", cy=560, spin=0.5)
    closeup(ctx, LAVA_GUY, keyed(T, [(0, "worried"), (14.19, "scream")]), T, arms=("up", "up"), s=4.6, dy=30,
            snap=snap_at(T, 14.19))
    style.sweat(ctx, 570, 430, 1.2, T)
    label(ctx, "WHAT?!", 360, 300, 96, fg=st.YELLOW, scale=pop(T - 14.19) if T >= 14.19 else 0.0)


def s_innocent(ctx, T, d):
    st.burst(ctx, T, "#fff6c4", "#8fd0ff", cy=560, spin=0.3)
    closeup(ctx, BENNY, keyed(T, [(0, "worried"), (15.39, "forced")]), T, arms=("shrug", "shrug"),
            snap=snap_at(T, 15.39))
    halo(ctx, 360, 330, 150, T)
    style.sweat(ctx, 560, 440, 1.0, T)
    st.speech_bubble(ctx, 520, 250, "SORRY!", 52, T - 15.2, tail=(-1, 1))


def s_crack(ctx, T, d):
    st.game_sky(ctx)
    st.block_clouds(ctx, T)
    st.lava(ctx, 1000, T)
    st.platform(ctx, 40, 780, 260, "#2cd5fc", h=80)
    fall = max(0.0, T - 16.45)
    ctx.save()
    ctx.translate(500, 760 + 900 * fall * fall)
    ctx.rotate(fall * 1.5)
    st.platform(ctx, -100, 0, 200, "#fa3a9f", h=70)
    if T < 16.45:
        ctx.move_to(-20, 0)
        ctx.line_to(10, 30)
        ctx.line_to(-10, 50)
        ctx.line_to(20, 70)
        ctx.set_source_rgb(*style.INK)
        ctx.set_line_width(6)
        ctx.stroke()
    ctx.restore()
    LAVA_GUY.draw(ctx, 200, 780, 0.9, keyed(T, [(0, "neutral"), (16.45, "shock")]), T, arms=("up", "down"))
    st.sfx_word(ctx, 520, 560, "CRACK!", T - 16.45, col=st.RED, size=56)
    label(ctx, "NEXT JUMP", 360, 300, 74, bg=st.BLUE, scale=pop(T - 16.17) if T >= 16.17 else 0.0)


# ================================================================ roleplay town
def s_town(ctx, T, d):
    st.street(ctx, T, y_ground=1000)
    p = clamp((T - 16.95) / 1.2)
    benny(ctx, lerp(60, 360, ease(p)), 1000, 0.95, "happy", T, pose="walk" if p < 1 else "stand",
          walk_phase=T * 2, arms=("wave", "down"))
    st.stage_pill(ctx, 360, 300, "ROLEPLAY TOWN", s=1.0, col="#7a3fd8")
    st.game_toast(ctx, 360, 210, "Benny", "joined Roleplay Town", T - 17.3, icon_col=st.PINK)


def s_house(ctx, T, d):
    world(ctx, T, 1000)
    st.house_block(ctx, 330, 1000, 1.1, door_k=0.0, sign="HOME")
    ctx.save()                                                        # CozyCat waving inside the window
    ctx.rectangle(330 - 170 * 1.1, 1000 - 340 * 1.1, 110 * 1.1, 90 * 1.1)
    ctx.clip()
    COZY.draw(ctx, 205, 800, 0.42, "happy", T, arms=("wave", "down"), shadow=False)
    ctx.restore()
    st.name_pill(ctx, 205, 600, "CozyCat", size=22)
    st.arrow(ctx, 600, 440, 470, 600, k=ease(clamp((T - 18.92) / 0.2)))
    st.hearts(ctx, T, 18.7, 210, 620, n=4, seed=9)


def s_knock(ctx, T, d):
    world(ctx, T, 1000)
    sh = 0.0
    for tk in (19.83, 20.19):
        if T >= tk:
            sh += math.sin((T - tk) * 60) * 8 * math.exp(-(T - tk) * 10)
    st.house_block(ctx, 300 + sh, 1000, 1.05, door_k=0.0, sign="")
    benny(ctx, 590, 1000, 1.0, "grin", T, arms=("up", "down"), tag=False)
    st.sfx_word(ctx, 300, 560, "KNOCK!", T - 19.83, col=st.YELLOW, size=56, tilt=-0.15)
    st.sfx_word(ctx, 380, 720, "KNOCK!", T - 20.19, col=st.YELLOW, size=50, tilt=0.12, seed=5)


def s_peephole(ctx, T, d):
    ctx.set_source_rgb(*hexc("#1a1020"))
    ctx.paint()
    ctx.save()
    ctx.new_sub_path()
    ctx.arc(360, 620, 270, 0, 2 * PI)
    ctx.clip()
    st.street(ctx, T, y_ground=1250)
    ctx.translate(360, 620)
    ctx.scale(1.15, 1.15)
    ctx.translate(-360, -620)
    closeup(ctx, BENNY, "crazy", T, arms=("wave", "down"), dy=80)
    ctx.restore()
    ctx.new_sub_path()
    ctx.arc(360, 620, 270, 0, 2 * PI)
    ctx.set_source_rgb(*hexc("#8a90a8"))
    ctx.set_line_width(26)
    ctx.stroke()
    msg = typed("I know where you live.", T, 20.73, cps=24)
    if msg:
        st.speech_bubble(ctx, 360, 230, msg, 40, 1.0, tail=(0, 1), col=(1, 0.92, 0.92), fg=st.RED)


def s_runinside(ctx, T, d):
    st.day_room(ctx, T, y_floor=1000)
    p = clamp((T - 21.95) / 0.9)
    COZY.draw(ctx, lerp(560, 140, ease(p)), 1000, 1.0, "scream", T, pose="run", walk_phase=T * 3.5,
              arms=("up", "up"), look=-0.6)
    st.name_pill(ctx, lerp(560, 140, ease(p)), 1000 - 3.45 * U1, "CozyCat", size=24)
    st.sfx_word(ctx, 450, 470, "AAAH!", T - 22.0, col=st.RED, size=58)


def s_locks(ctx, T, d):
    st.day_room(ctx, T, y_floor=1000)
    for i, (x, tk) in enumerate(((150, 22.98), (360, 23.30), (570, 23.65))):
        st.block(ctx, x - 70, 560, 140, 440, 8, hexc("#b0743c"), 5)
        st.block(ctx, x - 52, 590, 104, 170, 6, hexc("#9a6430"), 3, gloss=False)
        if T >= tk:
            st.padlock(ctx, x, 800, 0.9, k=clamp((T - tk) / 0.12), open_k=0.0)
            st.sfx_word(ctx, x, 470, "CLICK!", T - tk, col=st.BLUE, size=40, seed=i + 2)
    label(ctx, "LOCKED!", 360, 300, 80, bg=st.UI_DARK, fg=st.YELLOW, scale=pop(T - 22.98) if T >= 22.98 else 0.0)


# ================================================================ security booth, names, hiding
def s_notdone(ctx, T, d):
    st.burst(ctx, T, "#e2c8ff", "#7a3fd8", cy=560, spin=0.5)
    closeup(ctx, BENNY, keyed(T, [(0, "smirk"), (24.43, "smug")]), T, arms=("down", "down"), snap=snap_at(T, 24.43))
    if T >= 24.43:
        style.sparkle(ctx, 450, 470, 46 * pop(T - 24.43))
    label(ctx, "NOT DONE", 360, 300, 80, fg=(1, 1, 1), scale=pop(T - 24.77) if T >= 24.77 else 0.0)


def s_booth(ctx, T, d):
    world(ctx, T, 1000)
    st.security_booth(ctx, 330, 1000, 1.1, T)
    ctx.save()                                                        # Benny behind the glass
    ctx.rectangle(330 - 140 * 1.1, 1000 - 300 * 1.1, 280 * 1.1, 180 * 1.1)
    ctx.clip()
    benny(ctx, 330, 1060, 0.95, "grin", T, arms=("hold", "wave"), tag=False)
    ctx.restore()
    shut = 1 - ease(clamp((T - 25.4) / 0.35))                         # the shutter rolls up
    if shut > 0:
        st.block(ctx, 330 - 154, 1000 - 330 * 1.1 + 22, 308, 198 * shut, 6, hexc("#8a90a8"), 4, gloss=False)
    st.sfx_word(ctx, 560, 520, "OPEN!", T - 25.75, col=st.GREEN, size=48)


def s_megaphone(ctx, T, d):
    st.burst(ctx, T, "#ffe27a", "#ff7a1a", cy=560, spin=0.6)
    closeup(ctx, BENNY, "laugh", T, arms=("hold", "down"), x=330)
    st.megaphone(ctx, 440, 640, 1.2, ang=-0.25, T=T)
    st.speech_bubble(ctx, 470, 270, "ATTENTION!", 48, T - 26.62, tail=(-1, 1))


def s_cctv(ctx, T, d):
    st.night_wall(ctx, 2000)
    k_on = [T - (27.12 + i * 0.12) for i in range(6)]
    hi = int((T - 27.5) * 5) % 6 if T >= 27.5 else -1
    st.cctv_wall(ctx, 60, 300, 3, 2, NAMES, T, hi=hi, k_on=k_on)
    benny(ctx, 360, 1000, 0.85, "smug", T, arms=("hold", "hold"), tag=False)
    label(ctx, "ALL NAMES", 360, 950, 60, bg=st.RED, scale=pop(T - 28.08) if T >= 28.08 else 0.0)


def s_clock(ctx, T, d):
    st.burst(ctx, T, "#c4d8ff", "#2f3f9a", cy=600, spin=0.3)
    st.big_clock(ctx, 360, 600, 230, 2 + (T - 28.66) * 12, T)
    label(ctx, "MINUTES LATER", 360, 300, 64, fg=st.YELLOW, scale=pop(T - 28.7))


def s_hide(ctx, T, d):
    world(ctx, T, 1000)
    st.trash_can(ctx, 140, 1000, 1.0, lid=0.4 + 0.2 * math.sin(T * 9))
    st.bush(ctx, 360, 1000, 1.0, T, shake=1.0)
    st.cardboard_box(ctx, 570, 1000, 0.9, peek=1.0, T=T)
    for x, y in ((140, 812), (360, 880)):
        for ex in (-14, 14):
            ctx.new_sub_path()
            ctx.arc(x + ex, y, 7, 0, 2 * PI)
        ctx.set_source_rgb(1, 1, 1)
        ctx.fill()
    n = int(lerp(0, 50, ease(clamp((T - 29.4) / 0.8))))
    st.number_counter(ctx, 360, 470, 0.85, n, T, col="#ff4f5a", prefix="HIDING: ")
    st.sfx_word(ctx, 360, 640, "HIDE!", T - 29.76, col=st.PINK, size=48)


# ================================================================ moderators panic
def mods(ctx, T, expr, run=False, slide=0.0):
    for i, x in enumerate((160, 360, 560)):
        xx = x + slide * (700 - x)
        if run:
            xx = x + math.sin(T * 6 + i * 2) * 60
        MOD.draw(ctx, xx, 1000, 0.85, expr, T, arms=("up", "up") if run else ("hip", "point"),
                 pose="run" if run else "stand", walk_phase=T * 3, bob=0.6)
        st.name_pill(ctx, xx, 1000 - 3.45 * U1 * 0.85, "[MOD]", size=22, col=st.RED)
        if run:
            style.sweat(ctx, xx + 0.5 * U1 * 0.85, 1000 - 2.6 * U1 * 0.85, 0.85, T + i * 0.2)


def s_mods(ctx, T, d):
    world(ctx, T, 1000)
    slide = 1 - ease(clamp((T - 30.68) / 0.3))
    mods(ctx, T, keyed(T, [(0, "determined"), (31.3, "shock")]), slide=slide)
    label(ctx, "3 MODS", 360, 300, 80, bg=st.BLUE, scale=pop(T - 31.0) if T >= 31.0 else 0.0)


def s_panic(ctx, T, d):
    st.night_wall(ctx, 1000, wall="#3a1a2a")
    st.block(ctx, -100, 1000, 920, 500, 0, hexc("#2a2f45"), 4, gloss=False)     # the floor
    st.siren(ctx, 360, 470, 1.1, T)
    mods(ctx, T, "scream", run=True)
    st.sfx_word(ctx, 150, 640, "ALERT!", T - 31.73, col=st.RED, size=46)
    label(ctx, "PANIC!", 360, 300, 84, bg=st.RED, scale=pop(T - 31.73) if T >= 31.73 else 0.0)


def s_still(ctx, T, d):
    st.burst(ctx, T, "#ffe27a", "#f29a2e", cy=560, spin=0.3)
    if int(T * 3) % 2 == 0:
        st.tint(ctx, (1, 0.1, 0.1), 0.18)                            # the siren still flashing outside
    closeup(ctx, BENNY, "happy", T, arms=("hold", "hold"), dy=40)
    st.keyboard(ctx, 360, 950, 1.0, T, mash=1.0)
    st.sfx_word(ctx, 540, 380, "TYPE TYPE", T - 32.92, col=st.BLUE, size=38, tilt=0.12)


def s_help(ctx, T, d):
    st.burst(ctx, T, "#fff6c4", "#8fd0ff", cy=560, spin=0.3)
    closeup(ctx, BENNY, keyed(T, [(0, "happy"), (34.14, "stars")]), T, arms=("down", "wave"), snap=snap_at(T, 34.14))
    halo(ctx, 360, 330, 150, T)
    msg = typed("I'm here to help :)", T, 33.66, cps=26)
    if msg:
        st.speech_bubble(ctx, 360, 230, msg, 44, 1.0, tail=(0, 1))


# ================================================================ developers + filter
def desk(ctx, y=900):
    st.block(ctx, -100, y, 920, 50, 8, hexc("#b9b4d8"), 5)
    st.block(ctx, -100, y + 50, 920, 700, 0, hexc("#7a6aa8"), 5, gloss=False)


def s_devs(ctx, T, d):
    st.office(ctx, T, night=0.6, y_desk=1000)
    for i, x in enumerate((150, 360, 570)):
        DEV.draw(ctx, x, 1000, 0.85, "cry", T, arms=("up", "up"), pose="sit", bob=0.8)
    st.speech_bubble(ctx, 360, 520, "PLEASE STOP!", 54, T - 35.06, tail=(0, 1))
    label(ctx, "DEVS BEGGED", 360, 300, 66, bg=st.UI_DARK, fg=st.YELLOW, scale=pop(T - 34.5))


def s_reports(ctx, T, d):
    st.night_wall(ctx, 2000)

    def scr(c, x, y, w, h, TT):
        c.set_source_rgb(*hexc("#141a2e"))
        c.rectangle(x, y, w, h)
        c.fill()
        st.bold_text(c, "REPORTS", x + w / 2, y + h * 0.25, h * 0.13, hexc("#9aa0b8"), shadow=False, stroke=0.0)
        v = int(9999 * ease(clamp((TT - 35.55) / 0.6)))
        st.bold_text(c, f"{v:,}", x + w / 2, y + h * 0.58, h * 0.3, st.RED, shadow=False, stroke=0.08)
    st.monitor(ctx, 360, 900, 1.08, T, scr)
    for i in range(5):                                                 # envelopes flying in
        k = (T - 35.5) * 1.6 - i * 0.18
        if 0 < k < 1:
            ex, ey = lerp(-60 if i % 2 else 780, 360, k), lerp(260 + i * 60, 600, k)
            st.block(ctx, ex - 40, ey - 26, 80, 52, 6, (1, 1, 1), 3, gloss=False)
            ctx.move_to(ex - 40, ey - 26)
            ctx.line_to(ex, ey + 4)
            ctx.line_to(ex + 40, ey - 26)
            ctx.set_source_rgb(*st.RED)
            ctx.set_line_width(4)
            ctx.stroke()
    st.sfx_word(ctx, 560, 300, "DING!", T - 35.7, col=st.YELLOW, size=42)


def s_wall(ctx, T, d):
    ctx.set_source_rgb(*hexc("#120a14"))
    ctx.paint()
    ctx.save()
    ctx.rectangle(40, 200, 640, 800)
    ctx.clip()
    off = (T - 36.24) * 520
    for i in range(16):
        y = 1000 - off + i * 70
        if 180 < y < 1040:
            txt = SCARY[i % len(SCARY)]
            st.bold_text(ctx, "Benny:", 70, y, 26, st.YELLOW, align="l", shadow=False, stroke=0.0)
            st.bold_text(ctx, txt, 175, y, 26, hexc("#ff4f5a"), align="l", shadow=False, stroke=0.0)
    ctx.restore()
    st.glitch(ctx, T, k=0.35, seed=int(T * 10) % 5)
    label(ctx, "TERRIFYING", 360, 300, 72, bg=st.RED, scale=pop(T - 36.3))


def s_dev(ctx, T, d):
    st.office(ctx, T, night=1.0, y_desk=900)
    DEV.draw(ctx, 230, 1070, 1.4, keyed(T, [(0, "sleepy"), (38.26, "determined")]), T, arms=("hold", "hold"),
             bob=0.4, snap=snap_at(T, 38.26))
    desk(ctx, 900)
    st.monitor(ctx, 500, 905, 0.42, T, lambda c, x, y, w, h, TT: st.code_screen(c, x, y, w, h, TT, typed=0.3))
    for i in range(6):
        st.coffee_cup(ctx, 70 + (i % 3) * 56, 905 - (i // 3) * 62, 0.85, steam_T=T if i == 5 else None)
    label(ctx, "FINALLY", 360, 330, 74, bg=st.UI_DARK, fg=st.YELLOW, scale=pop(T - 38.26) if T >= 38.26 else 0.0)


def s_code(ctx, T, d):
    st.night_wall(ctx, 2000)

    def scr(c, x, y, w, h, TT):
        st.code_screen(c, x, y, w, h, TT, typed=clamp((TT - 38.65) / 0.8))
        if TT >= 39.48:
            st.bold_text(c, "CHAT_FILTER = ON", x + w / 2, y + h * 0.82, 30, st.GREEN, shadow=False, stroke=0.0,
                         scale=pop(TT - 39.48))
    st.monitor(ctx, 360, 860, 1.12, T, scr)
    st.keyboard(ctx, 360, 1000, 1.0, T, mash=1.0)
    if T < 39.48:                                                     # the next shot is a close-up on the code
        label(ctx, "NEW SYSTEM", 360, 300, 72, fg=st.GREEN, scale=pop(T - 39.11) if T >= 39.11 else 0.0)


def s_feed(ctx, T, d):
    st.burst(ctx, T, "#c4d8ff", "#2f3f9a", cy=600, spin=0.3)
    fx, fy, cx, cy = st.filter_machine(ctx, 280, 1000, 0.85, T, glow_a=0.45, spin=3.0)
    for i, w in enumerate(("WATCHING", "DIE", "LIVE", "NAMES")):
        k = T - (40.95 + i * 0.22)
        if 0 <= k < 0.55:
            p = clamp(k / 0.45)
            sc = 0.9 - 0.7 * clamp((k - 0.4) / 0.15)
            st.word_block(ctx, lerp(120 + i * 140, fx, p), lerp(200, fy + 30, p * p), w, sc, rot=(p - 0.5) * 0.8)
    st.sfx_word(ctx, 560, 640, "GULP!", T - 41.2, col=st.PINK, size=46)


def s_hashout(ctx, T, d):
    st.burst(ctx, T, "#b8ffb0", "#2e9c46", cy=600, spin=0.3)
    fx, fy, cx, cy = st.filter_machine(ctx, 280, 1000, 0.85, T, glow_a=0.45, spin=3.0)
    for i in range(7):
        k = T - (41.95 + i * 0.13)
        if k < 0:
            continue
        p = clamp(k / 0.45)
        tx = 410 + (i % 4) * 50
        x = lerp(cx, tx, p)
        y = cy - 230 * math.sin(PI * p) + (965 - (i // 4) * 50 - cy) * p
        st.word_block(ctx, x, y, "#", 0.65 * min(1.0, pop(k) + 0.2), col=st.GREEN, rot=(1 - p) * 3)
    label(ctx, "HASHTAGS", 360, 300, 76, bg=st.PINK, scale=pop(T - 42.57) if T >= 42.57 else 0.0)


# ================================================================ Benny tries to explain
def s_explain(ctx, T, d):
    st.burst(ctx, T, "#c4c8e8", "#4a4f8a", cy=560, spin=0.15)
    closeup(ctx, BENNY, keyed(T, [(0, "worried"), (43.63, "sad")]), T, arms=("shrug", "shrug"), snap=snap_at(T, 43.63))
    style.sweat(ctx, 560, 440, 1.0, T)
    style.sweat(ctx, 170, 470, 0.8, T + 0.4)


def s_typefail(ctx, T, d):
    st.night_wall(ctx, 2000)
    raw = typed("I'm not scary!", T, 43.95, cps=20)
    shown = raw.replace("scary", "#####") if len(raw) >= 13 else raw
    st.chat_box(ctx, 50, 380, 620, 260, [("Benny", shown, "#ffd84a")] if shown else [], T, size=46, title="Chat")
    if len(raw) >= 13:
        st.stamp(ctx, 360, 760, "FILTERED", T - (43.95 + 13 / 20), size=70)


def s_name(ctx, T, d):
    st.burst(ctx, T, "#ffe27a", "#f29a2e", cy=560, spin=0.4)
    closeup(ctx, BENNY, keyed(T, [(0, "determined"), (45.46, "crazy")]), T, arms=("up", "point"),
            talk=talking("benny", T), snap=snap_at(T, 45.46))
    txt = "My name is" if T < 45.46 else "My name is ####!"
    st.speech_bubble(ctx, 360, 250, txt, 46, T - 44.95, tail=(0, 1))


def s_namelog(ctx, T, d):
    st.night_wall(ctx, 2000)
    st.chat_box(ctx, 50, 380, 620, 260, [("Benny", "My name is ####", "#ffd84a")], T, size=46, title="Chat")
    st.stamp(ctx, 360, 760, "FILTERED", T - 46.0, size=70)
    st.face_icon(ctx, 600, 300, 40, "#e9c22c", "#ffd84a", expr="smirk")


def s_again(ctx, T, d):
    st.burst(ctx, T, "#c4f0b0", "#2e9c46", cy=560, spin=0.5)
    closeup(ctx, BENNY, keyed(T, [(0, "angry"), (47.14, "determined")]), T, arms=("punch", "punch"),
            snap=snap_at(T, 47.14))
    style.anger_mark(ctx, 520, 380, 1.4, T)
    label(ctx, "AGAIN!", 360, 300, 88, bg=st.RED, scale=pop(T - 47.0) if T >= 47.0 else 0.0)


def s_yell1(ctx, T, d):
    st.burst(ctx, T, "#ffb3b3", "#c0303a", cy=560, spin=0.8)
    closeup(ctx, BENNY, "scream", T, arms=("up", "up"), talk=talking("benny", T), snap=snap_at(T, 47.55))
    st.speech_bubble(ctx, 360, 260, "####!", 80, T - 47.55, tail=(0, 1))
    style.shake_lines(ctx, 360, 560, 280, 260, T, n=3, lw=9)


def s_yell2(ctx, T, d):
    st.burst(ctx, T, "#bfe3ff", "#2f6bd8", cy=600, spin=-0.8)
    closeup(ctx, BENNY, "crazy", T, arms=("hold", "down"), x=335, talk=talking("benny", T), snap=snap_at(T, 48.75))
    st.megaphone(ctx, 445, 640, 1.2, ang=-0.3, T=T)
    for i in range(3):
        if T >= 48.8 + i * 0.15:
            st.speech_bubble(ctx, 470 - i * 70, 240 + i * 90, "####!", 56 - i * 6, T - 48.8 - i * 0.15,
                             tail=(-1, 1))


def s_yell3(ctx, T, d):
    st.street(ctx, T, y_ground=1000)
    for i, x in enumerate((110, 230, 490, 610)):
        P[i + 8].draw(ctx, x, 1000, 0.8, "scared", T, arms=("cover", "cover"))
    benny(ctx, 360, 1000, 0.9, "scream", T, arms=("up", "up"), talk=talking("benny", T))
    st.speech_bubble(ctx, 360, 430, "####!", 110, T - 49.95, tail=(0, 1))
    st.sfx_word(ctx, 150, 640, "LOUD!", T - 50.1, col=st.RED, size=44)


# ================================================================ payoff
def s_popout(ctx, T, d):
    world(ctx, T, 1000)
    pop_out(ctx, P[5], 140, 1000 - 120, 0.75, T, 51.2)
    st.trash_can(ctx, 140, 1000, 1.0, lid=1.0 if T >= 51.2 else 0.0)
    pop_out(ctx, P[6], 360, 1000 - 90, 0.75, T, 51.6)
    st.bush(ctx, 360, 1000, 1.0, T, shake=1.0 if T < 51.6 else 0.0)
    pop_out(ctx, P[7], 570, 1000 - 110, 0.7, T, 52.0)
    st.cardboard_box(ctx, 570, 1000, 0.9, peek=0.0)
    for x, tk in ((140, 51.2), (360, 51.6), (570, 52.0)):
        st.sfx_word(ctx, x, 520, "POP!", T - tk, col=st.GREEN, size=40)


def s_stop(ctx, T, d):
    world(ctx, T, 1000)
    p = clamp((T - 52.51) / 0.35)
    x = lerp(60, 330, 1 - (1 - p) ** 3)
    P[0].draw(ctx, x, 1000, 1.05, "scream" if p < 1 else "happy", T, pose="run" if p < 1 else "stand",
              walk_phase=T * 3, arms=("up", "up"), lean=-0.25 * (1 - p))
    if p > 0:
        st.dust(ctx, x - 40, 1000, clamp((T - 52.51) / 0.5), n=6, spread=90)
    st.sfx_word(ctx, 520, 600, "SKRRT!", T - 52.6, col=st.YELLOW, size=50)
    if T >= 52.95:
        st.speech_bubble(ctx, 470, 400, "PHEW!", 50, T - 52.95, tail=(-1, 1))


def s_crazy(ctx, T, d):
    st.burst(ctx, T, "#e2c8ff", "#7a3fd8", cy=560, spin=0.6)
    closeup(ctx, P[3], keyed(T, [(0, "neutral"), (53.62, "shock")]), T, arms=("up", "up"), snap=snap_at(T, 53.62))
    label(ctx, "CRAZY PART", 360, 300, 74, fg=st.YELLOW, scale=pop(T - 53.62) if T >= 53.62 else 0.0)


def s_rename(ctx, T, d):
    st.night_wall(ctx, 2000)
    if T < 54.7:
        name = "Benny"[:max(0, 5 - int((T - 54.3) * 14))]
    else:
        name = "####"[:int((T - 54.7) * 8)]
    st.monitor(ctx, 360, 900, 1.08, T, lambda c, x, y, w, h, TT: st.login_screen(
        c, x, y, w, h, TT, typed=name, title="CHANGE USERNAME", lock=False))
    if 55.1 < T < 55.7:
        kk = ease(clamp((T - 55.1) / 0.25))
        st.cursor(ctx, lerp(560, 380, kk), lerp(980, 820, kk), 1.8, click=1.0 if T > 55.4 else 0.0)
    st.sfx_word(ctx, 540, 320, "SAVED!", T - 55.45, col=st.GREEN, size=44)


def s_newname(ctx, T, d):
    world(ctx, T, 1000)
    name = "Benny" if T < 55.75 else "####"
    benny(ctx, 360, 1000, 1.2, keyed(T, [(0, "smirk"), (55.75, "grin")]), T, arms=("hold", "wave"), name=name,
          snap=snap_at(T, 55.75))
    if T >= 55.75:
        st.poof(ctx, 360, 1000 - 3.5 * U1 * 1.2, 80, (T - 55.75) / 0.4)
        st.sparkles(ctx, T, 360, 520, spread=180, n=8, seed=4, c=st.YELLOW)
    label(ctx, "NEW NAME", 360, 300, 76, bg=st.UI_DARK, fg=st.YELLOW, scale=pop(T - 56.11) if T >= 56.11 else 0.0)


def s_turn(ctx, T, d):
    world(ctx, T, 1000)
    snap = T >= 56.95
    for i, x in enumerate((100, 210, 510, 620)):
        P[i].draw(ctx, x, 1000, 0.8, "stars" if snap else "neutral", T, arms=("up", "up") if snap else ("down", "down"),
                  look=0.5 if x < 360 else -0.5, snap=snap_at(T, 56.95))
    benny(ctx, 360, 1000, 0.95, "grin", T, name="####", arms=("wave", "down"))
    if snap:
        st.hearts(ctx, T, 56.95, 360, 640, n=8, seed=3)


def s_friends(ctx, T, d):
    st.burst(ctx, T, "#b8ffb0", "#2e9c46", cy=600, spin=0.5)
    st.friends_count(ctx, 360, 290, int(1 + 998 * ease(clamp((T - 58.0) / 0.9))), s=1.3)
    benny(ctx, 360, 1000, 1.0, "laugh", T, name="####", arms=("up", "up"))
    for i, (x, y) in enumerate(((175, 450), (470, 500), (175, 640), (470, 690))):
        st.friend_card(ctx, x, y, 0.46, NAMES[i + 2], k=T - (58.0 + i * 0.18), state="pending")
    st.confetti(ctx, T, 58.2, n=40)


# ================================================================ shots
S = []


def shot(start, draw, keys, **kw):
    kw.setdefault("vignette", 0.15)
    S.append(dict(start=start, draw=draw, keys=keys, **kw))


def punch(t0, z0, c0, t_key, z1, c1, m=0.13):
    return [(t0, z0, c0), (t_key, z1, c1, m)]


C = (360, 700)
G = (360, 760)
CU = dict(closeup=True, keep=FACE_KEEP)
TOPK = (60, 220, 660, 380)          # the label / bubble band at the top

shot(0.00, s_hook, [(0.0, 1.0, (360, 680)), (0.47, 1.08, (360, 660), 0.1)], shake=(0.47, 10), closeup=True,
     keep=[(165, 200, 555, 760), (200, 920, 520, 990)])
shot(0.86, at(s_run, 10.4), punch(0.86, 1.0, G, 0.9, 1.06, (360, 740), 0.1))
shot(1.22, at(s_panic, 32.0), punch(1.22, 1.0, G, 1.26, 1.06, (360, 740), 0.1))
shot(1.91, at(s_machine, 1.91), punch(1.91, 1.0, (360, 640), 2.0, 1.06, (360, 640), 0.1), shake=(0.09, 14),
     keep=[(60, 300, 660, 1000)])
shot(2.72, at(s_spawn, 2.72), punch(2.72, 1.0, G, 3.29, 1.06, (360, 740), 0.12), keep=[(200, 240, 520, 1000)])
shot(3.76, at(s_angel, 3.76), punch(3.76, 1.0, C, 4.15, 1.08, (360, 660), 0.12), **CU)
shot(4.44, at(s_safe, 4.44), punch(4.44, 1.0, G, 5.14, 1.06, (360, 740), 0.12), keep=[(80, 240, 640, 1000)])
shot(5.60, at(s_obby, 5.6), punch(5.6, 1.0, G, 6.3, 1.05, (360, 740), 0.12), keep=[(60, 170, 660, 250)])
shot(6.71, at(s_type, 6.71), punch(6.71, 1.0, C, 6.85, 1.06, (360, 680), 0.1), **CU)
shot(7.21, at(s_watch, 7.21), punch(7.21, 1.0, (360, 640), 7.9, 1.06, (360, 620), 0.12), keep=[(50, 380, 670, 940)])
shot(8.17, at(s_spectate, 8.17), punch(8.17, 1.0, (360, 660), 8.8, 1.04, (360, 660), 0.12), keep=[(70, 220, 650, 980)])
shot(9.04, at(s_freeze, 9.04), punch(9.04, 1.0, G, 9.53, 1.06, (360, 740), 0.1), shake=(0.49, 8),
     keep=[(50, 700, 670, 1000)])
shot(9.99, at(s_run, 9.99), punch(9.99, 1.0, G, 10.3, 1.04, (360, 740), 0.12), whip=1)
shot(11.05, at(s_spot, 11.05), punch(11.05, 1.0, C, 11.36, 1.1, (360, 650), 0.1), **CU)
shot(12.15, at(s_edge, 12.15), punch(12.15, 1.0, (330, 760), 12.55, 1.08, (320, 740), 0.12), keep=[(160, 240, 560, 820)])
shot(13.18, at(s_die, 13.18), [(13.18, 1.0, C), (14.19, 1.12, (360, 640), 0.9)], closeup=True,
     keep=[(165, 200, 555, 760)])
shot(14.19, at(s_what, 14.19), punch(14.19, 1.0, C, 14.3, 1.1, (360, 650), 0.08), shake=(0.0, 22), closeup=True,
     keep=[(110, 220, 610, 760)])
shot(14.97, at(s_innocent, 14.97), punch(14.97, 1.0, C, 15.39, 1.08, (360, 660), 0.12), closeup=True,
     keep=[(165, 200, 640, 760)])
shot(16.10, at(s_crack, 16.1), punch(16.1, 1.0, (360, 740), 16.45, 1.08, (400, 760), 0.1), shake=(0.35, 10),
     keep=[(120, 230, 600, 820)])
shot(16.88, at(s_town, 16.88), punch(16.88, 1.0, G, 17.76, 1.05, (360, 740), 0.15), whip=-1,
     keep=[(60, 180, 660, 330)])
shot(18.57, at(s_house, 18.57), punch(18.57, 1.0, G, 19.29, 1.06, (340, 740), 0.12), keep=[(100, 400, 620, 1000)])
shot(19.72, at(s_knock, 19.72), [(19.72, 1.35, (330, 830)), (20.19, 1.45, (330, 840), 0.1)], shake=(0.11, 9),
     keep=[(200, 480, 520, 800)])
shot(20.73, at(s_peephole, 20.73), [(20.73, 1.0, (360, 640)), (21.89, 1.08, (360, 620), 1.0)], closeup=True,
     keep=[(90, 180, 630, 900)])
shot(21.89, at(s_runinside, 21.89), punch(21.89, 1.0, G, 22.36, 1.05, (360, 740), 0.12), keep=[(100, 400, 620, 1000)])
shot(22.98, at(s_locks, 22.98), punch(22.98, 1.0, (360, 720), 23.65, 1.05, (360, 720), 0.12), shake=(0.0, 8),
     keep=[(70, 220, 650, 1000)])
shot(24.02, at(s_notdone, 24.02), punch(24.02, 1.0, C, 24.43, 1.1, (380, 650), 0.12), **CU)
shot(25.26, at(s_booth, 25.26), punch(25.26, 1.0, G, 25.73, 1.06, (360, 740), 0.12), whip=1,
     keep=[(150, 380, 620, 1000)])
shot(26.53, at(s_megaphone, 26.53), punch(26.53, 1.0, C, 26.62, 1.08, (360, 660), 0.1), closeup=True,
     keep=[(110, 200, 640, 760)])
shot(27.09, at(s_cctv, 27.09), punch(27.09, 1.0, (360, 660), 27.48, 1.04, (360, 660), 0.12), keep=[(55, 290, 665, 1000)])
shot(27.90, at(s_cctv, 27.9), [(27.9, 1.6, (340, 380)), (28.6, 1.7, (340, 380), 0.6)])
shot(28.66, at(s_clock, 28.66), punch(28.66, 1.0, (360, 640), 28.93, 1.06, (360, 640), 0.1), keep=[(110, 260, 610, 840)])
shot(29.35, at(s_hide, 29.35), punch(29.35, 1.0, G, 29.76, 1.05, (360, 740), 0.12), keep=[(60, 380, 660, 1000)])
shot(30.68, at(s_mods, 30.68), punch(30.68, 1.0, G, 31.0, 1.05, (360, 740), 0.12), whip=1, keep=[(80, 240, 640, 1000)])
shot(31.62, at(s_panic, 31.62), punch(31.62, 1.0, G, 31.73, 1.06, (360, 740), 0.1), shake=(0.11, 8),
     keep=[(80, 240, 640, 1000)])
shot(32.33, at(s_still, 32.33), punch(32.33, 1.0, C, 32.92, 1.06, (360, 680), 0.12), **CU)
shot(33.66, at(s_help, 33.66), punch(33.66, 1.0, C, 34.14, 1.08, (360, 660), 0.12), closeup=True,
     keep=[(110, 180, 610, 760)])
shot(34.48, at(s_devs, 34.48), punch(34.48, 1.0, G, 35.06, 1.05, (360, 740), 0.12), keep=[(90, 240, 630, 1000)])
shot(35.50, at(s_reports, 35.5), punch(35.5, 1.0, (360, 700), 35.88, 1.06, (360, 680), 0.12), keep=[(80, 240, 640, 900)])
shot(36.24, at(s_wall, 36.24), punch(36.24, 1.0, (360, 640), 36.82, 1.06, (360, 640), 0.12), keep=[(50, 200, 670, 1000)])
shot(37.41, at(s_dev, 37.41), punch(37.41, 1.0, G, 38.26, 1.08, (320, 760), 0.12), whip=-1)
shot(38.65, at(s_code, 38.65), punch(38.65, 1.0, (360, 700), 39.11, 1.06, (360, 680), 0.12), keep=[(80, 240, 640, 840)])
shot(39.48, at(s_code, 39.48), [(39.48, 1.5, (360, 640)), (40.0, 1.6, (360, 640), 0.4)])
shot(40.10, at(lambda c, T, d: s_machine(c, T, d, t_land=40.18, words_t=99, out_t=99, glow_a=0.7), 40.1),
     punch(40.1, 1.0, (360, 640), 40.2, 1.06, (360, 640), 0.08), shake=(0.08, 14), keep=[(60, 300, 660, 1000)])
shot(40.93, at(s_feed, 40.93), punch(40.93, 1.0, (360, 640), 41.54, 1.05, (360, 640), 0.12), keep=[(60, 180, 660, 1000)])
shot(41.93, at(s_hashout, 41.93), punch(41.93, 1.0, (360, 700), 42.57, 1.06, (380, 720), 0.12), keep=[(60, 240, 640, 1000)])
shot(42.92, at(s_explain, 42.92), punch(42.92, 1.0, C, 43.63, 1.06, (360, 670), 0.12), **CU)
shot(43.89, at(s_typefail, 43.89), punch(43.89, 1.0, (360, 640), 44.8, 1.05, (360, 640), 0.12), keep=[(50, 380, 670, 840)])
shot(44.92, at(s_name, 44.92), punch(44.92, 1.0, C, 45.46, 1.1, (360, 650), 0.1), shake=(0.54, 8), closeup=True,
     keep=[(110, 200, 610, 760)])
shot(45.93, at(s_namelog, 45.93), punch(45.93, 1.0, (360, 640), 46.0, 1.05, (360, 640), 0.1), shake=(0.07, 8),
     keep=[(50, 260, 670, 840)])
shot(46.80, at(s_again, 46.8), punch(46.8, 1.0, C, 47.14, 1.1, (360, 650), 0.1), **CU)
shot(47.55, at(s_yell1, 47.55), punch(47.55, 1.0, C, 47.6, 1.12, (360, 650), 0.06), shake=(0.0, 18), closeup=True,
     keep=[(110, 180, 610, 760)])
shot(48.75, at(s_yell2, 48.75), punch(48.75, 1.0, C, 48.8, 1.1, (340, 650), 0.06), shake=(0.0, 14), closeup=True,
     keep=[(110, 180, 610, 760)], dutch=-0.08)
shot(49.95, at(s_yell3, 49.95), punch(49.95, 1.0, G, 50.0, 1.06, (360, 740), 0.06), shake=(0.0, 12),
     keep=[(60, 300, 660, 1000)])
shot(51.07, at(s_popout, 51.07), punch(51.07, 1.0, G, 51.6, 1.05, (360, 740), 0.12), whip=-1,
     keep=[(60, 480, 660, 1000)])
shot(52.51, at(s_stop, 52.51), punch(52.51, 1.0, G, 52.83, 1.06, (360, 740), 0.1), shake=(0.35, 8),
     keep=[(160, 330, 600, 1000)])
shot(53.17, at(s_crazy, 53.17), punch(53.17, 1.0, C, 53.62, 1.1, (360, 650), 0.1), shake=(0.45, 10), **CU)
shot(54.29, at(s_rename, 54.29), punch(54.29, 1.0, (360, 700), 54.73, 1.05, (360, 690), 0.12), keep=[(80, 280, 640, 1000)])
shot(55.64, at(s_newname, 55.64), punch(55.64, 1.0, G, 55.75, 1.08, (360, 720), 0.1), keep=[(150, 240, 570, 1000)])
shot(56.82, at(s_turn, 56.82), punch(56.82, 1.0, G, 56.95, 1.06, (360, 740), 0.1), keep=[(60, 300, 660, 1000)])
shot(57.96, at(s_friends, 57.96), punch(57.96, 1.0, (360, 660), 58.4, 1.04, (360, 660), 0.12), keep=[(60, 240, 640, 1000)])
SHOTS = S
_rw_draw, _rw_ov = st.rewind_shot(SHOTS, [57.5, 48.2, 40.5, 21.3, 14.4, 0.0])
shot(59.25, _rw_draw, [(59.25, 1.0, (360, 640))], overlay=_rw_ov, blur=False, closeup=True, keep=[])
S.sort(key=lambda sh: sh["start"])
for k, s in enumerate(SHOTS):
    s["end"] = SHOTS[k + 1]["start"] if k + 1 < len(SHOTS) else TOTAL

# ---------------------------------------------------------------- SFX (time, file, volume before SFX_GAIN)
# One sound per visual event, spaced >= ~0.25 s so each is heard; only 5 booms (sound_design.md, set 3).
SFX = [
    (0.03, "sting_low.wav", 0.9), (0.32, "pop.wav", 0.7), (0.47, "hit.wav", 1.2), (0.86, "whoosh.wav", 0.5),
    (1.22, "buzz.wav", 0.7), (2.0, "boom.wav", 1.5), (2.2, "pop.wav", 0.6), (2.45, "ding.wav", 0.7),
    (2.8, "sparkle.wav", 0.8), (3.29, "pop.wav", 0.8), (3.8, "sparkle.wav", 0.6), (4.15, "ding.wav", 0.6),
    (4.5, "pop.wav", 0.6), (5.14, "success.wav", 0.8), (5.62, "click.wav", 0.6), (5.9, "swish.wav", 0.5),
    (6.3, "boing.wav", 0.8), (6.75, "type_key.wav", 0.7), (7.05, "type_key.wav", 0.7), (7.3, "type_key.wav", 0.6),
    (7.6, "type_key.wav", 0.6), (7.95, "pop.wav", 0.6), (8.2, "click.wav", 0.6), (8.85, "boing.wav", 0.5),
    (9.1, "pop.wav", 0.5), (9.53, "hit.wav", 1.1), (9.99, "whoosh.wav", 0.7), (10.3, "pop.wav", 0.7),
    (10.62, "tick.wav", 0.6), (11.05, "swish.wav", 0.5), (11.36, "pop.wav", 0.8), (12.2, "boing.wav", 0.5),
    (12.55, "pop.wav", 0.7), (13.18, "sting_low.wav", 1.0), (13.5, "type_key.wav", 0.6),
    (13.8, "type_key.wav", 0.6), (14.19, "boom.wav", 1.4), (14.5, "pop.wav", 0.5), (15.0, "tick.wav", 0.5),
    (15.2, "pop.wav", 0.7), (15.6, "sparkle.wav", 0.6), (16.1, "tick.wav", 0.5), (16.45, "hit.wav", 1.2),
    (16.7, "pop.wav", 0.5), (16.88, "swish.wav", 0.6), (17.3, "click.wav", 0.6), (17.6, "step.wav", 0.5),
    (17.95, "step.wav", 0.5), (18.6, "pop.wav", 0.6), (18.92, "ding.wav", 0.6), (19.83, "hit.wav", 1.1),
    (20.19, "hit.wav", 1.1), (20.8, "sting_low.wav", 0.9), (21.1, "type_key.wav", 0.6), (21.4, "type_key.wav", 0.6),
    (21.95, "pop.wav", 0.7), (22.3, "step.wav", 0.6), (22.6, "step.wav", 0.6), (22.98, "click.wav", 1.0),
    (23.3, "click.wav", 1.0), (23.65, "click.wav", 1.0), (24.05, "tick.wav", 0.5), (24.43, "sparkle.wav", 0.8),
    (24.77, "pop.wav", 0.7), (25.26, "swish.wav", 0.6), (25.75, "pop.wav", 0.7), (26.62, "hit.wav", 1.0),
    (26.9, "pop.wav", 0.5), (27.12, "click.wav", 0.6), (27.95, "pop.wav", 0.6), (28.7, "tick.wav", 0.6),
    (29.0, "tick.wav", 0.6), (29.4, "pop.wav", 0.6), (29.76, "pop.wav", 0.8), (30.1, "chaching.wav", 0.6),
    (30.68, "swish.wav", 0.6), (31.0, "pop.wav", 0.7), (31.3, "hit.wav", 1.0), (31.73, "buzz.wav", 0.9),
    (32.05, "buzz.wav", 0.6), (32.4, "type_key.wav", 0.6), (32.7, "type_key.wav", 0.6), (32.95, "pop.wav", 0.6),
    (33.3, "type_key.wav", 0.6), (33.7, "type_key.wav", 0.6), (34.14, "sparkle.wav", 0.8), (34.5, "pop.wav", 0.6),
    (35.06, "pop.wav", 0.8), (35.55, "ding.wav", 0.7), (35.85, "ding.wav", 0.6), (36.24, "sting_low.wav", 0.8),
    (37.15, "buzz.wav", 0.5), (37.45, "swish.wav", 0.6), (38.26, "pop.wav", 0.8), (38.7, "type_key.wav", 0.6),
    (39.0, "type_key.wav", 0.6), (39.48, "ding.wav", 0.9), (40.18, "boom.wav", 1.5), (40.45, "sparkle.wav", 0.7),
    (40.95, "swish.wav", 0.5), (41.2, "pop.wav", 0.8), (41.45, "pop.wav", 0.6), (41.7, "pop.wav", 0.6),
    (41.95, "pop.wav", 0.7), (42.21, "pop.wav", 0.6), (42.47, "pop.wav", 0.6), (42.75, "ding.wav", 0.6),
    (44.0, "type_key.wav", 0.6), (44.3, "type_key.wav", 0.6), (44.8, "hit.wav", 0.9), (45.1, "pop.wav", 0.5),
    (45.46, "buzz.wav", 0.8), (46.0, "hit.wav", 1.0), (46.8, "pop.wav", 0.6), (47.14, "pop.wav", 0.7),
    (47.55, "boom.wav", 1.4), (47.9, "pop.wav", 0.5), (48.75, "hit.wav", 1.1), (49.0, "pop.wav", 0.6),
    (49.3, "pop.wav", 0.6), (49.95, "hit.wav", 1.2), (50.2, "pop.wav", 0.6), (51.07, "swish.wav", 0.6),
    (51.2, "pop.wav", 0.8), (51.6, "pop.wav", 0.8), (52.0, "pop.wav", 0.8), (52.6, "whoosh.wav", 0.6),
    (52.95, "ding.wav", 0.6), (53.2, "tick.wav", 0.5), (53.62, "hit.wav", 1.1), (53.95, "pop.wav", 0.5),
    (54.3, "type_key.wav", 0.6), (54.6, "type_key.wav", 0.6), (54.9, "type_key.wav", 0.6),
    (55.45, "click.wav", 0.9), (55.75, "pop.wav", 0.8), (56.11, "sparkle.wav", 0.7), (56.95, "ding.wav", 0.8),
    (57.3, "pop.wav", 0.5), (57.6, "pop.wav", 0.5), (58.0, "pop.wav", 0.7), (58.18, "pop.wav", 0.6),
    (58.4, "chaching.wav", 0.7), (58.7, "success.wav", 0.8), (59.25, "whip.wav", 0.9),
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

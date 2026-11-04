"""Story: "This Noob Is the REASON Roblox Has a Chat Filter" (Benny, who just wanted everyone to feel safe).

Voice: output/chat_filter/voice.mp3 (59.1 s, the user's voice tool, 99 % speech, no gap) + subs.srt; word times
from analysis/align_words.py. Quoted lines that Benny really says (lip-sync): "My name is ####!" (44.9-46.9) and
"####! ####! ####!" (47.5-51.0). Everything else is narration. Made with engine.profile("set3") (60 fps), the
Roblox-world props and lessons 1-6 in lessons.md. No subscribe / comment line exists in this voice.

Each scene is written with ABSOLUTE time T (the shot wraps it), so one scene can run in two shots.

Beats: hook 0-2.3 · name + "safe" 2.7-5.1 · obby + "I'm watching you" 5.6-10.6 · lava player 11-14 ·
roleplay house + knock + lock 16.9-23 · security booth + names + 50 hiding + 3 mods 24-34 · developers +
filter 34-41 · hashtags + Benny's lines 41-51 · username #### + friend requests 52-59 · loop.

Run (from animator/):
  python3 chat_filter.py ../output/chat_filter/clips/animation.mp4 ../output/chat_filter/cues.json"""
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
SFX_GAIN = 0.24
MUSIC = dict(bpm=128, perc=0.6, dips=[(49.6, 50.8)])      # quieter under "The entire server finally stopped"
DIALOGUE = {"benny": [(44.9, 46.9), (47.5, 51.0)]}

BENNY = Block("#ff8a3d", pants="#2b3f8f", skin="#e9c22c", hair=None, sleeves="skin", shoes=None, cap="#ffd84a")
MOD = Block("#2f6bd8", pants="#2b2f45", skin="#f0c9a8", hair="smooth", hair_col="#3a2a2a", outfit="hoodie",
            shoes="dark", glasses=True)
DEV = Block("#3b3f5a", pants="#2b2f45", skin="#f0c9a8", hair="spiky", hair_col="#2a1a14", outfit="hoodie",
            glasses=True, headset="#4f8bff", shoes="dark")
P = [style.crowd_member(i) for i in range(14)]
NAMES = st.ROBLOX_NAMES

U1 = Block.HW * 64
FACE_S = 4.2
FACE_KEEP = [(165, 300, 555, 760)]


def talking(who, T):
    return any(a <= T <= b for a, b in DIALOGUE[who])


def snap_at(T, t0):
    return (T - t0) if T >= t0 else None


def at(fn, T0):
    """A shot draw for a scene written with absolute time: the shot starts at T0."""
    return lambda ctx, t, d: fn(ctx, T0 + t, d)


def closeup(ctx, ch, expr, T, x=360, look=0.0, arms=("down", "down"), s=FACE_S, talk=False, bob=0.35, dy=0,
            snap=None):
    ch.draw(ctx, x, 560 + 2.5 * U1 * s + dy, s, expr, T, arms=arms, look=look, talk=talk, bob=bob, snap=snap)


def benny(ctx, x, y, s, expr, T, tag=True, ch=None, name="Benny", **kw):
    (ch or BENNY).draw(ctx, x, y, s, expr, T, **kw)
    if tag:
        st.name_pill(ctx, x, y - 3.5 * U1 * s, name, size=max(20, 24 * s))


def world(ctx, T, y=1000):
    st.game_sky(ctx)
    st.block_clouds(ctx, T)
    st.baseplate(ctx, y)


# ================================================================ hook (0-2.3 s)
def s_hook(ctx, T, d):
    st.burst(ctx, T, "#ffe27a", "#ff7a1a", cy=560, spin=0.4)
    closeup(ctx, BENNY, keyed(T, [(0, "crazy"), (0.36, "grin")]), T, arms=("wave", "down"), snap=snap_at(T, 0.36))
    st.chat_box(ctx, 60, 790, 600, 200, [("Benny", "####!", "#ffd84a")], T, size=34, title="Chat")
    label(ctx, "THIS NOOB", 340, 300, 66, fg=st.RED, scale=pop(T))


# ================================================================ name + "safe"
def s_named(ctx, T, d):
    st.burst(ctx, T, "#bfe3ff", "#2f6bd8", cy=560)
    closeup(ctx, BENNY, keyed(T, [(0, "happy"), (2.72, "grin")]), T, arms=("down", "wave"), snap=snap_at(T, 2.72))
    if T >= 2.72:
        st.name_pill(ctx, 360, 300, "Benny", size=44 * min(1.0, pop(T - 2.72) + 0.2))
    label(ctx, "BENNY", 360, 300, 66, fg=st.GREEN, scale=pop(T - 2.72))


def s_safe(ctx, T, d):
    world(ctx, T, 1000)
    for i, x in enumerate((110, 230, 490, 610)):
        P[i].draw(ctx, x, 1000, 0.85, "happy", T, arms=("up", "up") if i % 2 else ("wave", "down"), look=0.3)
    benny(ctx, 360, 1000, 1.1, "happy", T, arms=("hold", "hold"))
    st.sparkles(ctx, T, 360, 700, spread=260, n=10, seed=3, c=st.GREEN)
    label(ctx, "SAFE!", 360, 300, 66, fg=st.GREEN, scale=pop(T - 3.76) if T >= 3.76 else 0.0)


def s_safe2(ctx, T, d):
    st.burst(ctx, T, "#b8ffb0", "#2e9c46", cy=560)
    closeup(ctx, BENNY, keyed(T, [(0, "happy"), (4.6, "laugh")]), T, arms=("up", "up"), snap=snap_at(T, 4.6))
    st.hearts(ctx, T, 4.6, 360, 620, n=6)


# ================================================================ obby + "I'm watching you"
def s_obby(ctx, T, d):
    tops = st.obby(ctx, T, y_lava=1060, y_top=930, x0=-80, dx=230, rise=-30, nums=False)
    x, y = tops[1]
    benny(ctx, x, y, 0.9, "grin", T, arms=("up", "down"))
    st.game_toast(ctx, 360, 190, "Benny", "joined the game", T - 5.6, icon_col=st.YELLOW)


def s_typing(ctx, T, d):
    st.night_wall(ctx, 2000)
    n = int(clamp((T - 6.85) / 1.0) * 14)
    typed = "I'm watching you.".upper()[:n] if False else "I'm watching you."[:n]
    st.chat_box(ctx, 50, 330, 620, 360, [("Benny", typed, "#ffd84a")] if typed else [], T, size=40, title="Chat")
    st.keyboard(ctx, 360, 1000, 1.0, T, mash=1.0)


def s_watch(ctx, T, d):
    st.burst(ctx, T, "#c4d8ff", "#2f3f9a", cy=560)
    closeup(ctx, BENNY, keyed(T, [(0, "smug"), (7.9, "crazy")]), T, arms=("hold", "hold"), snap=snap_at(T, 7.9))
    st.speech_bubble(ctx, 420, 320, "I'M WATCHING YOU", 40, T - 7.9, tail=(-1, 1))


def s_spectate(ctx, T, d):
    world(ctx, T, 1000)
    st.spectate_pill(ctx, 360, 260, 1.4)
    for i, x in enumerate((120, 260, 460, 600)):
        P[i + 4].draw(ctx, x, 1000, 0.85, "neutral", T, arms=("down", "down"), look=-0.4)
    benny(ctx, 360, 1000, 0.95, "smirk", T, arms=("hold", "hold"))


def s_run(ctx, T, d):
    """Everyone runs away from Benny (the teaser shows the same scene at 9.9 s)."""
    world(ctx, T, 1000)
    k = clamp((T - 9.04) / 1.0)
    for i in range(6):
        x0 = 360 + (i - 2.5) * 50
        x1 = 80 if i % 2 == 0 else 640
        x = lerp(x0, x1, ease(k)) if k > 0 else x0
        P[i].draw(ctx, x, 1000, 0.8, "scared" if k > 0 else "worried", T, pose="run" if k > 0 else "stand",
                  walk_phase=T * 3, arms=("up", "up") if k > 0 else ("down", "down"))
    st.dust(ctx, 360, 1000, clamp((T - 9.04) / 0.5), n=6, spread=160)
    benny(ctx, 360, 1000, 0.9, "smirk", T, arms=("hold", "hold"))
    st.sfx_word(ctx, 360, 520, "ZOOM!", T - 9.1, col=st.BLUE, size=54) if T >= 9.1 else None


# ================================================================ lava player
def s_lava(ctx, T, d):
    tops = st.obby(ctx, T, y_lava=1060, y_top=930, x0=-80, dx=230, rise=-30, nums=False)
    x, y = tops[1]
    P[2].draw(ctx, x, y, 0.95, keyed(T, [(0, "worried"), (12.2, "scared")]), T, arms=("down", "down"))
    st.name_pill(ctx, x, y - 3.45 * U1 * 0.95, "LavaJumper", size=24)
    label(ctx, "NEAR LAVA", 360, 300, 66, bg=st.RED, scale=pop(T - 11.05) if T >= 11.05 else 0.0)


def s_die(ctx, T, d):
    st.burst(ctx, T, "#ffb3b3", "#c0303a", cy=560)
    closeup(ctx, BENNY, keyed(T, [(0, "smug"), (13.18, "cold")]), T, arms=("hip", "down"), snap=snap_at(T, 13.18))
    st.speech_bubble(ctx, 430, 300, "GOING TO DIE.", 46, T - 13.18, tail=(-1, 1))


def s_what(ctx, T, d):
    st.burst(ctx, T, "#ffd27a", "#ff7a1a", cy=560, spin=0.3)
    closeup(ctx, P[2], keyed(T, [(0, "worried"), (14.19, "scream")]), T, arms=("up", "up"), snap=snap_at(T, 14.19))
    style.sweat(ctx, 560, 420, 1.0, T)
    label(ctx, "WHAT?!", 360, 300, 66, fg=st.YELLOW, scale=pop(T - 14.19) if T >= 14.19 else 0.0)


def s_warn(ctx, T, d):
    world(ctx, T, 1000)
    P[2].draw(ctx, 230, 1000, 1.0, "angry" if T < 15.16 else "neutral", T, arms=("hip", "down"))
    benny(ctx, 470, 1000, 1.0, "grin", T, arms=("wave", "down"))
    st.speech_bubble(ctx, 470, 720, "NEXT JUMP!", 48, T - 15.16, tail=(0, 1))


def s_nextjump(ctx, T, d):
    tops = st.obby(ctx, T, y_lava=1060, y_top=930, x0=-80, dx=230, rise=-30, nums=False)
    x0, y0 = tops[1]
    x1, y1 = tops[2]
    st.arrow(ctx, x0 + 40, y0 - 260, x1 - 40, y1 - 150, k=ease(clamp((T - 16.1) / 0.2)))
    label(ctx, "NEXT JUMP", 360, 300, 66, bg=st.BLUE, scale=pop(T - 16.1) if T >= 16.1 else 0.0)


# ================================================================ roleplay house
def s_roleplay(ctx, T, d):
    world(ctx, T, 1000)
    st.house_block(ctx, 300, 1000, 1.05, door_k=0.0)
    st.stage_pill(ctx, 360, 300, "ROLEPLAY", s=1.0, col="#7a3fd8")
    st.arrow(ctx, 560, 560, 420, 760, k=ease(clamp((T - 17.4) / 0.2)))


def s_knock(ctx, T, d):
    world(ctx, T, 1000)
    shake = math.sin(T * 40) * 6 * math.exp(-max(0, T - 19.72) * 6) if T >= 19.72 else 0.0
    st.house_block(ctx, 300 + shake, 1000, 1.05, door_k=0.0)
    benny(ctx, 560, 1000, 0.95, keyed(T, [(0, "determined"), (19.8, "grin")]), T, arms=("up", "down"))
    if T >= 19.72:
        st.sfx_word(ctx, 470, 520, "KNOCK!", T - 19.72, col=st.YELLOW, size=54, tilt=-0.12)


def s_threat(ctx, T, d):
    st.tint(ctx, (0.1, 0.0, 0.15), 0.35)
    closeup(ctx, BENNY, keyed(T, [(0, "smug"), (20.9, "crazy")]), T, arms=("hold", "hold"), snap=snap_at(T, 20.9))
    label(ctx, "UH OH", 360, 300, 66, bg=st.RED, scale=pop(T - 20.9) if T >= 20.9 else 0.0)


def s_lock(ctx, T, d):
    world(ctx, T, 1000)
    st.house_block(ctx, 300, 1000, 1.05, door_k=0.0)
    k = clamp((T - 21.9) / 0.15)
    st.padlock(ctx, 300, 880, 1.0, k=k, open_k=0.0)
    run = clamp((T - 21.9) / 1.2)
    P[1].draw(ctx, lerp(560, 640, ease(run)), 1000, 0.85, "scared", T, pose="run", walk_phase=T * 3,
              arms=("up", "up"))
    if T >= 21.9:
        st.sfx_word(ctx, 430, 640, "CLICK!", T - 21.9, col=st.BLUE, size=50)
    label(ctx, "LOCKED!", 360, 300, 66, bg=st.UI_DARK, fg=st.YELLOW, scale=pop(T - 21.9) if T >= 21.9 else 0.0)


def s_finished(ctx, T, d):
    st.burst(ctx, T, "#e2c8ff", "#7a3fd8", cy=560)
    closeup(ctx, BENNY, keyed(T, [(0, "smirk"), (24.1, "smug")]), T, arms=("down", "down"),
            snap=snap_at(T, 24.1))
    if T >= 24.1:
        style.sparkle(ctx, 450, 470, 40 * pop(T - 24.1))
    label(ctx, "NOT DONE", 360, 300, 66, fg=(1, 1, 1), scale=pop(T - 24.1) if T >= 24.1 else 0.0)


# ================================================================ security booth + names + hiding
def s_booth(ctx, T, d):
    world(ctx, T, 1000)
    st.security_booth(ctx, 330, 1000, 1.1, T)
    benny(ctx, 560, 1000, 0.95, "grin", T, arms=("hold", "wave"))
    label(ctx, "THE BOOTH", 360, 300, 66, bg=st.RED, scale=pop(T - 25.26) if T >= 25.26 else 0.0)


def s_names(ctx, T, d):
    st.burst(ctx, T, "#c4d8ff", "#2f3f9a", cy=600)
    st.player_list(ctx, 170, 330, NAMES[:8], T, s=1.4, me="Benny")
    label(ctx, "EVERYONE'S", 360, 950, 56, bg=st.UI_DARK, fg=st.YELLOW,
             scale=pop(T - 27.09) if T >= 27.09 else 0.0)


def s_count50(ctx, T, d):
    st.burst(ctx, T, "#ffb3b3", "#c0303a", cy=600)
    st.number_counter(ctx, 360, 560, 1.2, 50 if T >= 28.5 else int(lerp(1, 50, clamp((T - 28.1) / 0.4))), T,
                      col="#ff4f5a", prefix="Players ")
    label(ctx, "HIDING", 360, 300, 80, bg=st.UI_DARK, fg=st.YELLOW, scale=pop(T - 28.5) if T >= 28.5 else 0.0)


def s_hiding(ctx, T, d):
    world(ctx, T, 1000)
    for i, x in enumerate((70, 180, 290, 400, 510, 620)):
        P[i + 3].draw(ctx, x, 1000, 0.9, "scared", T, arms=("up", "up"), look=0.4 if i % 2 else -0.4)
    st.brick_wall(ctx, -20, 1000, 760, 180)
    if T >= 29.8:
        for i, x in enumerate((130, 330, 540)):
            st.speech_bubble(ctx, x, 620 - (i % 2) * 60, "?", 60, T - 29.8 - i * 0.1, tail=(0, 1))
    st.game_hud(ctx, T, players=50, y=300)


# ================================================================ moderators
def s_mods(ctx, T, d):
    world(ctx, T, 1000)
    for i, x in enumerate((150, 360, 570)):
        MOD.draw(ctx, x, 1000, 0.85, keyed(T, [(0, "worried"), (30.9, "scared")]), T, arms=("up", "hip"), bob=0.6)
        st.name_pill(ctx, x, 1000 - 3.45 * U1 * 0.85, "[MOD]", size=22, col=st.RED)
        style.sweat(ctx, x + 0.5 * U1 * 0.85, 1000 - 2.6 * U1 * 0.85, 0.85, T + i * 0.2)
    label(ctx, "PANIC!", 360, 300, 66, bg=st.RED, scale=pop(T - 30.68) if T >= 30.68 else 0.0)


def s_mods2(ctx, T, d):
    st.burst(ctx, T, "#c4c8e8", "#4a4f8a", cy=560)
    closeup(ctx, MOD, keyed(T, [(0, "worried"), (31.9, "scared")]), T, arms=("up", "up"), snap=snap_at(T, 31.9))
    style.shake_lines(ctx, 360, 560, 260, 240, T, n=3, lw=8)
    label(ctx, "MODS!!", 360, 300, 66, bg=st.RED, scale=pop(T - 31.9) if T >= 31.9 else 0.0)


def s_help(ctx, T, d):
    st.burst(ctx, T, "#ffe27a", "#f29a2e", cy=560)
    closeup(ctx, BENNY, keyed(T, [(0, "smirk"), (33.9, "happy")]), T, arms=("down", "wave"), snap=snap_at(T, 33.9))
    st.chat_box(ctx, 60, 790, 600, 200, [("Benny", "I'm here to help.", "#ffd84a")], T, size=34, title="Chat")


# ================================================================ developers + filter
def s_devs(ctx, T, d):
    world(ctx, T, 1000)
    for i, x in enumerate((130, 250, 470, 580)):
        P[i + 8].draw(ctx, x, 1000, 0.85, "cry" if i % 2 else "worried", T, arms=("up", "up"),
                      pose="sit" if i % 2 else "stand")
    if T >= 34.5:
        st.speech_bubble(ctx, 360, 420, "PLEASE STOP!", 50, T - 34.5, tail=(0, 1))


def s_reports(ctx, T, d):
    office_t = T
    st.office(ctx, office_t, night=1.0, y_desk=900)
    DEV.draw(ctx, 230, 1070, 1.4, keyed(T, [(0, "tired"), (35.5, "shock")]), T, arms=("hold", "hold"), bob=0.4)
    style.block(ctx, -100, 900, 920, 50, 8, hexc("#b9b4d8"), 5)
    style.block(ctx, -100, 950, 920, 700, 0, hexc("#7a6aa8"), 5, gloss=False)
    st.monitor(ctx, 500, 905, 0.42, T, lambda c, x, y, w, h, TT: st.bold_text(
        c, "REPORTS 4,021", x + w / 2, y + h / 2, 22, st.RED, shadow=False, stroke=0.0))
    label(ctx, "TERRIFYING", 360, 300, 66, bg=st.UI_DARK, fg=st.RED, scale=pop(T - 35.5) if T >= 35.5 else 0.0)


def s_code(ctx, T, d):
    st.night_wall(ctx, 2000)
    st.monitor(ctx, 360, 860, 1.12, T, lambda c, x, y, w, h, TT: st.code_screen(
        c, x, y, w, h, TT, typed=clamp((TT - 37.41) / 1.0)))
    st.keyboard(ctx, 360, 1000, 1.0, T, mash=1.0)
    label(ctx, "NEW SYSTEM", 360, 300, 66, fg=st.GREEN, scale=pop(T - 37.41) if T >= 37.41 else 0.0)


def s_code2(ctx, T, d):
    st.night_wall(ctx, 2000)

    def scr(c, x, y, w, h, TT):
        st.code_screen(c, x, y, w, h, TT, typed=1.0)
        if TT >= 38.7:
            st.bold_text(c, "CHAT_FILTER = ON", x + w / 2, y + h * 0.82, 30, st.GREEN, shadow=False, stroke=0.0,
                         scale=pop(TT - 38.7))
    st.monitor(ctx, 360, 860, 1.12, T, scr)
    st.keyboard(ctx, 360, 1000, 1.0, T, mash=0.0)


def s_dialog(ctx, T, d):
    st.burst(ctx, T, "#c4d8ff", "#2f3f9a", cy=600)
    st.roblox_dialog(ctx, 360, 600, 1.05, T - 40.1, "Chat Filter Enabled",
                     "Scary words will now show as ####.", "OK", col="#4f8bff")


def s_hash(ctx, T, d):
    """Scary words turn into hashtags: the chat fills with ####, and bubbles pop over Benny."""
    world(ctx, T, 1000)
    n = 3 + int(clamp((T - 40.93) / 0.6) * 3)
    lines = [("Benny", "####", "#ffd84a")] * n
    st.chat_box(ctx, 50, 330, 620, 380, lines, T, size=40, title="Chat")
    for i, (x, y) in enumerate(((190, 760), (480, 730), (330, 830))):
        if T >= 40.93 + i * 0.2:
            st.speech_bubble(ctx, x, y, "####!", 52, T - 40.93 - i * 0.2, tail=(0, 1))
    label(ctx, "HASHTAGS", 360, 300, 66, bg=st.BLUE, scale=pop(T - 40.93) if T >= 40.93 else 0.0)


def s_sad(ctx, T, d):
    st.burst(ctx, T, "#c4d8ff", "#2f3f9a", cy=560, spin=0.05)
    closeup(ctx, BENNY, keyed(T, [(0, "sad"), (43.9, "sad")]), T, arms=("down", "down"))
    style.sweat(ctx, 560, 440, 1.0, T)
    if T >= 42.9:
        st.speech_bubble(ctx, 500, 320, "...", 60, T - 42.9, tail=(-1, 1))


def s_say(ctx, T, d):
    st.burst(ctx, T, "#ffe27a", "#f29a2e", cy=560)
    closeup(ctx, BENNY, keyed(T, [(0, "determined"), (45.5, "crazy")]), T, arms=("up", "point"),
            talk=talking("benny", T), snap=snap_at(T, 45.5))
    st.speech_bubble(ctx, 360, 290, "My name is ####!", 46, T - 44.92, tail=(0, 1))


def s_try(ctx, T, d):
    st.burst(ctx, T, "#c4f0b0", "#2e9c46", cy=560)
    closeup(ctx, BENNY, keyed(T, [(0, "determined"), (47.0, "crazy")]), T, arms=("down", "punch"),
            snap=snap_at(T, 47.0))
    label(ctx, "AGAIN!", 360, 300, 66, bg=st.RED, scale=pop(T - 46.86) if T >= 46.86 else 0.0)


def s_yell(ctx, T, d):
    st.burst(ctx, T, "#ffb3b3", "#c0303a", cy=560, spin=0.4)
    closeup(ctx, BENNY, "crazy", T, arms=("up", "up"), talk=talking("benny", T))
    for i, (x, y) in enumerate(((200, 300), (520, 310), (360, 420))):
        if T >= 47.51 + i * 0.25:
            st.speech_bubble(ctx, x, y, "####!", 50, T - 47.51 - i * 0.25, tail=(0, 1))


# ================================================================ relief, turn, username, friends
def s_relief(ctx, T, d):
    world(ctx, T, 1000)
    for i, x in enumerate((90, 220, 350, 480, 610)):
        P[i].draw(ctx, x, 1000, 0.85, "happy" if i % 2 else "stars", T, arms=("up", "wave") if i % 2 else ("hold", "down"),
                  look=0.2)
    if T >= 49.72:
        st.sfx_word(ctx, 360, 540, "PHEW!", T - 49.72, col=st.GREEN, size=60)
    label(ctx, "STOPPED!", 360, 300, 66, bg=st.GREEN, scale=pop(T - 49.72) if T >= 49.72 else 0.0)


def s_crazy(ctx, T, d):
    st.burst(ctx, T, "#e2c8ff", "#7a3fd8", cy=560, spin=0.5)
    closeup(ctx, P[3], keyed(T, [(0, "neutral"), (53.17, "shock")]), T, arms=("up", "up"), snap=snap_at(T, 53.17))
    label(ctx, "CRAZY PART", 360, 300, 66, fg=st.YELLOW, scale=pop(T - 53.17) if T >= 53.17 else 0.0)


def s_username(ctx, T, d):
    typed = "####"[:int(clamp((T - 54.29) / 0.9) * 4)]
    st.night_wall(ctx, 2000)
    st.monitor(ctx, 360, 900, 1.08, T, lambda c, x, y, w, h, TT: st.login_screen(
        c, x, y, w, h, TT, typed=typed, title="CHANGE USERNAME", lock=False))
    label(ctx, "USERNAME", 360, 300, 66, bg=st.BLUE, scale=pop(T - 54.29) if T >= 54.29 else 0.0)


def s_newname(ctx, T, d):
    world(ctx, T, 1000)
    name = "Benny" if T < 55.5 else "####"
    benny(ctx, 360, 1000, 1.1, keyed(T, [(0, "smirk"), (55.5, "grin")]), T, arms=("hold", "wave"), name=name)
    label(ctx, "NEW NAME", 360, 300, 66, bg=st.UI_DARK, fg=st.YELLOW, scale=pop(T - 55.5) if T >= 55.5 else 0.0)


def s_friends(ctx, T, d):
    st.burst(ctx, T, "#b8ffb0", "#2e9c46", cy=600)
    st.friends_count(ctx, 360, 300, int(1 + 998 * ease(clamp((T - 57.0) / 0.9))), s=1.3)
    for i, (x, y) in enumerate(((180, 470), (470, 540), (180, 760), (470, 820), (330, 650))):
        st.friend_card(ctx, x, y, 0.48, NAMES[i + 2], k=T - (56.82 + i * 0.2), state="pending")


def s_final(ctx, T, d):
    st.burst(ctx, T, "#ffe27a", "#ff8a3d", cy=560)
    closeup(ctx, BENNY, keyed(T, [(0, "smug"), (58.4, "wink")]), T, arms=("shrug", "shrug"),
            snap=snap_at(T, 58.4))
    st.speech_bubble(ctx, 560, 320, "?!", 70, T - 58.4, tail=(-1, 1))


def s_door(ctx, T, d):
    """A close-up of the roleplay door: Benny's fist knocks on it (the cut that breaks the 17-21 s stretch)."""
    world(ctx, T, 1000)
    shake = math.sin(T * 40) * 6 * math.exp(-max(0, T - 19.72) * 6) if T >= 19.72 else 0.0
    st.house_block(ctx, 300 + shake, 1000, 1.05, door_k=0.0, sign="")
    benny(ctx, 600, 1000, 1.0, "determined", T, arms=("up", "down"))


def s_devface(ctx, T, d):
    st.burst(ctx, T, "#c4d8ff", "#2f3f9a", cy=560)
    closeup(ctx, DEV, keyed(T, [(0, "determined"), (39.6, "shock")]), T, arms=("up", "down"),
            snap=snap_at(T, 39.6))
    st.label(ctx, "FILTERED", 360, 300, 66, bg=st.RED, scale=pop(T - 39.6) if T >= 39.6 else 0.0)


def s_crowdface(ctx, T, d):
    st.burst(ctx, T, "#b8ffb0", "#2e9c46", cy=560)
    closeup(ctx, P[1], keyed(T, [(0, "worried"), (51.9, "stars")]), T, arms=("hold", "wave"), snap=snap_at(T, 51.9))


# ================================================================ shots
S = []


def shot(start, draw, keys, **kw):
    kw.setdefault("vignette", 0.15)
    S.append(dict(start=start, draw=draw, keys=keys, **kw))


def punch(t0, z0, c0, t_key, z1, c1, m=0.14):
    return [(t0, z0, c0), (t_key, z1, c1, m)]


C = (360, 700)
G = (360, 760)
CU = dict(closeup=True, keep=FACE_KEEP)

shot(0.00, s_hook, [(0.0, 1.12, (360, 640)), (0.36, 1.0, (360, 680), 0.12)], shake=(0.36, 10), closeup=True,
     keep=[(110, 180, 610, 760), (60, 790, 660, 990)])
shot(0.86, at(s_run, 9.9), punch(0.86, 1.0, C, 0.9, 1.06, (360, 700), 0.1), shake=(0.0, 8))
shot(1.22, at(s_hash, 41.6), punch(1.22, 1.0, G, 1.25, 1.06, (360, 720), 0.1), keep=[(50, 330, 670, 710)])
shot(1.91, at(s_lock, 22.2), punch(1.91, 1.0, G, 1.95, 1.05, (360, 740), 0.1))
shot(2.72, at(s_named, 2.72), punch(2.72, 1.0, C, 3.1, 1.08, (360, 660), 0.12), **CU)
shot(3.76, at(s_safe, 3.76), punch(3.76, 1.0, G, 4.2, 1.06, (360, 740), 0.12), keep=[(90, 230, 630, 1000)])
shot(4.60, at(s_safe2, 4.6), punch(4.6, 1.0, C, 4.9, 1.06, (360, 660), 0.12), **CU)
shot(5.60, at(s_obby, 5.6), punch(5.6, 1.0, G, 6.2, 1.06, (360, 740), 0.12), keep=[(60, 150, 660, 1000)])
shot(6.85, at(s_typing, 6.85), punch(6.85, 1.0, (360, 640), 7.2, 1.04, (360, 640), 0.12), keep=[(50, 330, 670, 690)])
shot(7.72, at(s_watch, 7.72), punch(7.72, 1.0, C, 7.9, 1.1, (360, 660), 0.12), **CU)
shot(8.17, at(s_spectate, 8.17), punch(8.17, 1.0, G, 8.6, 1.05, (360, 740), 0.12), keep=[(60, 200, 660, 290)])
shot(9.04, at(s_run, 9.04), punch(9.04, 1.0, G, 9.5, 1.06, (360, 740), 0.12), shake=(0.5, 6))
shot(10.00, at(s_run, 10.0), punch(10.0, 1.0, G, 10.5, 1.05, (360, 740), 0.12))
shot(11.05, at(s_lava, 11.05), punch(11.05, 1.0, (360, 700), 11.4, 1.06, (360, 700), 0.12),
     keep=[(60, 230, 660, 340)])
shot(12.20, at(s_lava, 12.2), punch(12.2, 1.0, (360, 760), 12.6, 1.08, (320, 760), 0.12), keep=[(120, 700, 600, 960)])
shot(13.18, at(s_die, 13.18), punch(13.18, 1.0, C, 13.5, 1.08, (360, 660), 0.12), **CU)
shot(14.19, at(s_what, 14.19), punch(14.19, 1.0, C, 14.3, 1.1, (360, 650), 0.1), shake=(0.2, 14), **CU)
shot(15.16, at(s_warn, 15.16), punch(15.16, 1.0, G, 15.5, 1.05, (360, 740), 0.12), keep=[(120, 300, 620, 1000)])
shot(16.10, at(s_nextjump, 16.1), punch(16.1, 1.0, (360, 700), 16.45, 1.06, (360, 700), 0.12),
     keep=[(60, 200, 660, 960)])
shot(16.88, at(s_roleplay, 16.88), punch(16.88, 1.0, G, 17.4, 1.06, (360, 740), 0.12), keep=[(100, 230, 620, 1000)])
shot(17.90, at(s_roleplay, 17.9), punch(17.9, 1.0, (360, 740), 18.5, 1.06, (340, 760), 0.12), keep=[(240, 250, 480, 330)])
shot(19.72, at(s_knock, 19.72), punch(19.72, 1.0, G, 19.8, 1.06, (360, 740), 0.1), shake=(0.0, 10),
     keep=[(60, 300, 660, 1000)])
shot(20.73, at(s_threat, 20.73), punch(20.73, 1.0, C, 20.9, 1.1, (360, 660), 0.12), shake=(0.17, 10), **CU)
shot(21.89, at(s_lock, 21.89), punch(21.89, 1.0, G, 22.2, 1.06, (360, 740), 0.12), keep=[(120, 240, 600, 1000)])
shot(22.90, at(s_lock, 22.9), punch(22.9, 1.0, (360, 740), 23.4, 1.05, (340, 760), 0.12))
shot(24.02, at(s_finished, 24.02), punch(24.02, 1.0, C, 24.3, 1.08, (360, 660), 0.12), **CU)
shot(25.26, at(s_booth, 25.26), punch(25.26, 1.0, G, 25.8, 1.06, (360, 740), 0.12), keep=[(90, 280, 650, 1000)])
shot(26.40, at(s_booth, 26.4), punch(26.4, 1.0, (360, 740), 26.9, 1.05, (360, 740), 0.12))
shot(27.09, at(s_names, 27.09), punch(27.09, 1.0, (360, 640), 27.6, 1.04, (360, 640), 0.12), keep=[(160, 320, 600, 900)])
shot(28.10, at(s_count50, 28.1), punch(28.1, 1.0, (360, 640), 28.5, 1.06, (360, 640), 0.12), keep=[(90, 260, 630, 760)])
shot(28.66, at(s_hiding, 28.66), punch(28.66, 1.0, G, 29.2, 1.05, (360, 740), 0.12), keep=[(40, 230, 680, 1010)])
shot(29.80, at(s_hiding, 29.8), punch(29.8, 1.0, (360, 740), 30.3, 1.05, (360, 740), 0.12))
shot(30.68, at(s_mods, 30.68), punch(30.68, 1.0, G, 31.2, 1.05, (360, 740), 0.12), keep=[(90, 240, 640, 1000)])
shot(31.70, at(s_mods2, 31.7), punch(31.7, 1.0, C, 31.9, 1.08, (360, 660), 0.12), shake=(0.2, 8), **CU)
shot(33.66, at(s_help, 33.66), punch(33.66, 1.0, C, 33.9, 1.08, (360, 660), 0.12), **CU)
shot(34.48, at(s_devs, 34.48), punch(34.48, 1.0, G, 35.0, 1.05, (360, 740), 0.12), keep=[(70, 300, 650, 1010)])
shot(35.50, at(s_reports, 35.5), punch(35.5, 1.0, (360, 700), 36.0, 1.05, (360, 700), 0.12))
shot(37.41, at(s_code, 37.41), punch(37.41, 1.0, (360, 700), 37.9, 1.06, (360, 680), 0.12), keep=[(80, 470, 640, 840)])
shot(38.60, at(s_code2, 38.6), punch(38.6, 1.0, (360, 700), 38.9, 1.06, (360, 680), 0.12), keep=[(80, 470, 640, 840)])
shot(40.10, at(s_dialog, 40.1), punch(40.1, 1.0, (360, 640), 40.12, 1.08, (360, 640), 0.1), shake=(0.02, 10),
     keep=[(80, 430, 640, 770)])
shot(40.93, at(s_hash, 40.93), punch(40.93, 1.0, (360, 700), 41.3, 1.05, (360, 700), 0.12),
     keep=[(50, 330, 670, 710)])
shot(42.00, at(s_hash, 42.0), punch(42.0, 1.0, (360, 700), 42.5, 1.05, (360, 700), 0.12), keep=[(50, 330, 670, 710)])
shot(42.92, at(s_sad, 42.92), punch(42.92, 1.0, C, 43.2, 1.06, (360, 660), 0.12), **CU)
shot(44.92, at(s_say, 44.92), punch(44.92, 1.0, C, 45.3, 1.08, (360, 660), 0.12), closeup=True,
     keep=[(165, 300, 555, 760), (80, 220, 640, 380)])
shot(46.86, at(s_try, 46.86), punch(46.86, 1.0, C, 47.0, 1.08, (360, 660), 0.12), **CU)
shot(47.51, at(s_yell, 47.51), punch(47.51, 1.0, C, 47.8, 1.1, (360, 650), 0.1), shake=(0.1, 14), **CU)
shot(48.80, at(s_yell, 48.8), punch(48.8, 1.0, C, 49.2, 1.06, (360, 660), 0.1), **CU)
shot(49.72, at(s_relief, 49.72), punch(49.72, 1.0, G, 50.2, 1.05, (360, 740), 0.12), keep=[(60, 300, 660, 1000)])
shot(50.80, at(s_relief, 50.8), punch(50.8, 1.0, (360, 740), 51.3, 1.05, (360, 740), 0.12))
shot(53.17, at(s_crazy, 53.17), punch(53.17, 1.0, C, 53.5, 1.08, (360, 660), 0.12), **CU)
shot(54.29, at(s_username, 54.29), punch(54.29, 1.0, (360, 700), 54.6, 1.05, (360, 700), 0.12),
     keep=[(80, 470, 640, 840)])
shot(55.50, at(s_newname, 55.5), punch(55.5, 1.0, G, 55.9, 1.06, (360, 740), 0.12), keep=[(150, 300, 570, 1000)])
shot(56.82, at(s_friends, 56.82), punch(56.82, 1.0, (360, 640), 57.3, 1.04, (360, 640), 0.12),
     keep=[(50, 280, 640, 900)])
shot(58.40, at(s_final, 58.4), punch(58.4, 1.0, C, 58.7, 1.1, (360, 650), 0.1), shake=(0.4, 10), **CU)
SHOTS = S
_rw_draw, _rw_ov = st.rewind_shot(SHOTS, [56.9, 46.9, 36.0, 24.1, 12.0, 0.0])
shot(10.60, at(s_run, 10.6), punch(10.6, 1.45, (200, 900), 11.0, 1.5, (200, 900), 0.3))
shot(18.55, at(s_door, 18.55), punch(18.55, 1.45, (300, 880), 19.6, 1.55, (300, 880), 0.6), shake=(1.17, 8))
shot(30.20, at(s_hiding, 30.2), punch(30.2, 1.4, (360, 880), 30.8, 1.5, (360, 880), 0.4))
shot(39.30, at(s_devface, 39.3), punch(39.3, 1.0, C, 39.6, 1.1, (360, 660), 0.12), **CU)
shot(51.90, at(s_crowdface, 51.9), punch(51.9, 1.0, C, 52.2, 1.1, (360, 660), 0.12), **CU)
shot(59.30, _rw_draw, [(59.30, 1.0, (360, 640))], overlay=_rw_ov, blur=False, closeup=True, keep=[])
S.sort(key=lambda sh: sh["start"])
for k, s in enumerate(SHOTS):
    s["end"] = SHOTS[k + 1]["start"] if k + 1 < len(SHOTS) else TOTAL

# ---------------------------------------------------------------- SFX (time, file, volume before SFX_GAIN)
SFX = [
    (0.03, "boom.wav", 1.3), (0.36, "hit.wav", 1.1), (0.6, "pop.wav", 0.6), (0.86, "whoosh.wav", 0.5),
    (1.22, "pop.wav", 0.6), (1.91, "click.wav", 0.8), (2.72, "ding.wav", 0.8), (3.1, "pop.wav", 0.6),
    (3.76, "sparkle.wav", 0.8), (4.2, "pop.wav", 0.6), (4.6, "pop.wav", 0.7), (4.9, "sparkle.wav", 0.5),
    (5.6, "ding.wav", 0.7), (6.2, "boing.wav", 0.6), (6.85, "type_key.wav", 0.6), (7.2, "type_key.wav", 0.6),
    (7.5, "type_key.wav", 0.6), (7.72, "tick.wav", 0.6), (7.9, "hit.wav", 1.0), (8.17, "pop.wav", 0.6),
    (8.6, "tick.wav", 0.5), (9.04, "swish.wav", 0.6), (9.1, "pop.wav", 0.7), (9.5, "whoosh.wav", 0.6),
    (10.0, "swish.wav", 0.6), (10.5, "pop.wav", 0.5), (11.05, "ding.wav", 0.7), (11.4, "tick.wav", 0.5),
    (12.2, "hit.wav", 1.0), (12.6, "pop.wav", 0.6), (13.18, "pop.wav", 0.7), (13.5, "hit.wav", 1.0),
    (14.19, "hit.wav", 1.1), (14.3, "boom.wav", 1.3), (15.16, "pop.wav", 0.7), (15.5, "boing.wav", 0.6),
    (16.1, "ding.wav", 0.7), (16.45, "tick.wav", 0.5), (16.88, "swish.wav", 0.5), (17.4, "pop.wav", 0.6),
    (17.9, "step.wav", 0.5), (18.5, "step.wav", 0.5), (19.72, "hit.wav", 1.2), (19.8, "pop.wav", 0.7),
    (20.73, "sting_low.wav", 0.8), (20.9, "pop.wav", 0.6), (21.9, "click.wav", 1.0), (22.2, "tick.wav", 0.5),
    (22.9, "step.wav", 0.5), (23.4, "tick.wav", 0.5), (24.02, "sparkle.wav", 0.7), (24.3, "pop.wav", 0.6),
    (25.26, "pop.wav", 0.7), (25.8, "tick.wav", 0.5), (26.4, "chaching.wav", 0.6), (26.9, "pop.wav", 0.5),
    (27.09, "click.wav", 0.7), (27.6, "tick.wav", 0.5), (28.1, "tick.wav", 0.5), (28.5, "pop.wav", 0.8),
    (28.66, "hit.wav", 1.0), (29.2, "pop.wav", 0.6), (29.8, "pop.wav", 0.6), (30.3, "tick.wav", 0.5),
    (30.68, "boom.wav", 1.2), (31.2, "pop.wav", 0.6), (31.7, "tick.wav", 0.5), (31.9, "hit.wav", 1.1),
    (33.66, "type_key.wav", 0.6), (33.9, "ding.wav", 0.7), (34.48, "pop.wav", 0.7), (35.0, "tick.wav", 0.5),
    (35.5, "buzz.wav", 0.8), (36.0, "tick.wav", 0.5), (37.41, "type_key.wav", 0.6), (37.9, "pop.wav", 0.6),
    (38.6, "type_key.wav", 0.6), (38.7, "ding.wav", 0.8), (38.9, "pop.wav", 0.6), (40.1, "ding.wav", 0.9),
    (40.12, "sparkle.wav", 0.6), (40.93, "pop.wav", 0.8), (41.13, "pop.wav", 0.7), (41.33, "pop.wav", 0.7),
    (41.3, "tick.wav", 0.5), (42.0, "pop.wav", 0.6), (42.5, "tick.wav", 0.5), (42.92, "tick.wav", 0.5),
    (43.2, "pop.wav", 0.6), (44.92, "pop.wav", 0.7), (45.3, "tick.wav", 0.5), (46.86, "click.wav", 0.7),
    (47.0, "hit.wav", 1.0), (47.51, "boom.wav", 1.2), (47.76, "pop.wav", 0.7), (48.01, "pop.wav", 0.7),
    (48.8, "tick.wav", 0.5), (49.2, "pop.wav", 0.6), (49.72, "sparkle.wav", 0.8), (50.2, "tick.wav", 0.5),
    (50.8, "step.wav", 0.5), (51.3, "pop.wav", 0.5), (53.17, "hit.wav", 1.1), (53.5, "pop.wav", 0.6),
    (54.29, "type_key.wav", 0.6), (54.6, "type_key.wav", 0.6), (54.9, "type_key.wav", 0.6), (55.5, "ding.wav", 0.8),
    (55.9, "pop.wav", 0.6), (56.82, "pop.wav", 0.7), (57.0, "chaching.wav", 0.6), (57.3, "pop.wav", 0.6),
    (58.4, "hit.wav", 1.0), (58.7, "pop.wav", 0.6), (59.3, "whip.wav", 0.9),
    (10.6, "swish.wav", 0.5), (10.9, "pop.wav", 0.6), (18.55, "tick.wav", 0.6), (19.2, "pop.wav", 0.6),
    (30.2, "tick.wav", 0.5), (30.6, "pop.wav", 0.6), (39.3, "type_key.wav", 0.6), (39.6, "pop.wav", 0.7),
    (51.9, "pop.wav", 0.6), (52.4, "sparkle.wav", 0.5), (35.0, "ding.wav", 0.5),
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

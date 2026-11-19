"""Story: "How long could you survive playing Roblox without taking a single break?"

Voice: output/no_break/voice.mp3 (59.3 s) + subs.srt; word times from analysis/align_words.py.
A time-ladder story (hour 1 -> year 50): every chapter gets a painted card (visual_grammar row 5)
and a PLAYTIME HUD pill that jumps forward (row 24). "You" are KID, who grows a beard by year 10
and is a grey-bearded grandpa by year 50, still in the same teal star shirt.

Run (from animator/):
  python3 no_break.py ../output/no_break/clips/animation.mp4 ../output/no_break/cues.json
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

TOTAL = 59.7
engine.LIPSYNC = False
engine.DRIFT = (0.035, 9, -6)      # a bit livelier hold: measured camera median 1.76 at (0.02, 5, -3)
engine.ENERGY = 3.0
SFX_GAIN = 0.4                      # real recorded voice (sound_design.md section 3)
MUSIC = dict(dips=[(48.6, 50.0)])   # quieter under the whispered "But then they notice something"

KID = style.KID
GAMER = Block("#2fbf8f", pants="#2b3f8f", skin="#e6ddd6", hair="bowl", hair_col="#4a2f22", emblem="star",
              emblem_col="#ffd84a", shoes="white", headset="rgb")
ADULT = Block("#2fbf8f", pants="#2b3f8f", skin="#e6ddd6", hair="bowl", hair_col="#4a2f22", emblem="star",
              emblem_col="#ffd84a", shoes="white", headset="rgb", beard="#4a2f22")
GRANDPA = Block("#2fbf8f", pants="#2b3f8f", skin="#e6ddd6", hair="bowl", hair_col="#d8d8e4", emblem="star",
                emblem_col="#ffd84a", shoes="white", headset="rgb", glasses=True, beard="#f2f2f6",
                brow_col="#b8b8c4")
KID_SH = Block("#2fbf8f", pants="#2b3f8f", skin="#e6ddd6", hair="bowl", hair_col="#4a2f22", emblem="star",
               emblem_col="#ffd84a", shoes="white", shades=True)
MOM = style.MOM
AVATAR = style.KID_GAME
GK1 = Block("#ff5fa2", pants="#5a4fb0", skin="#c89f82", hair="pony", hair_col="#4a2f22", lashes=True, shoes="white")
GK2 = Block("#ffb02e", pants="#2b45a6", skin="#e6ddd6", hair="spiky", hair_col="#8a5a3a", shoes="white")
FRIENDS = [style.crowd_member(i) for i in range(5)]

U1 = Block.HW * 64
FACE_S = 4.2
FACE_KEEP = [(165, 300, 555, 760)]


def closeup(ctx, ch, expr, T, x=360, look=0.0, arms=("down", "down"), s=FACE_S):
    ch.draw(ctx, x, 560 + 2.5 * U1 * s, s, expr, T, arms=arms, look=look)


def card(ctx, T, txt, t0):
    st.day_text(ctx, txt, 360, 400, T - t0, size=120)


def desk_scene(ctx, T, ch, expr, arms=("hold", "hold"), look=0.0, boxes=0, cob=0.0, cans=2, dark=0.0):
    """The gamer bedroom at night: ch behind the desk, laptop lid toward us glowing on the face."""
    st.night_wall(ctx, 2000)
    st.window(ctx, 40, 200, 230, 300, T, night=True)
    st.poster(ctx, 590, 300, 0.85)
    if boxes:
        st.pizza_tower(ctx, 620, 1000, boxes, w=170, T=T)
    ch.draw(ctx, 360, 1020, 1.35, expr, T, arms=arms, look=look)
    st.block(ctx, -100, 900, 920, 50, 8, hexc("#b9b4d8"), 5)
    st.block(ctx, -100, 950, 920, 700, 0, hexc("#7a6aa8"), 5, gloss=False)
    st.laptop(ctx, 360, 905, 0.5, T, back=True)
    for i in range(cans):
        st.energy_can(ctx, 90 + i * 55, 900, 0.8)
    if cob > 0:
        st.cobweb(ctx, 190, 640, 170, cob, corner=(1, 1))
        st.cobweb(ctx, 560, 905, 140, cob, corner=(-1, -1))
    if dark:
        st.tint(ctx, (0.05, 0.05, 0.2), dark)


def monitor_scene(ctx, T, screen, s=1.15):
    st.night_wall(ctx, 2000)
    st.monitor(ctx, 360, 900, s, T, screen)


def obby_screen(stage="STAGE 1", fail=None, avatar_expr="happy", jump=0.0):
    def fn(c, x, y, w, h, T):
        def av(cc, ax, ay, s, TT):
            hop = abs(math.sin(TT * 5)) * 60 * jump
            AVATAR.draw(cc, ax + (TT * 90 * jump) % (w * 0.6), ay - hop, s * 1.4, avatar_expr, TT, arms=("up", "up"),
                        pose="jump" if jump else "stand")
        st.screen_obby(c, x, y, w, h, T, av, stage, fail)
    return fn


# ================================================================ hook
def s_hook(ctx, t, d, T0=0.0, frozen=False):
    T = T0 + (0.0 if frozen else t)
    st.burst(ctx, T, "#c4a8ff", "#4a2fb0", cy=560, spin=0.4)
    st.glow(ctx, 360, 700, 520, (0.5, 0.9, 1.0), 0.35)
    closeup(ctx, GAMER, keyed(T, [(0, "crazy"), (0.73, "determined")]), T, arms=("hold", "hold"))
    label(ctx, "HOW LONG?", 360, 300, 80, fg=st.YELLOW, scale=pop(T - 0.0))


def s_playing(ctx, t, d):
    T = 1.05 + t
    monitor_scene(ctx, T, obby_screen(jump=1.0), s=1.1)
    style.back_figure(ctx, 170, 1290, 2.2, GAMER.hair_col, GAMER.shirt)
    label(ctx, "ROBLOX", 360, 300, 64, bg=st.RED, scale=pop(T - 1.34))


def s_nobreak(ctx, t, d):
    T = 1.75 + t
    st.burst(ctx, T, "#ff8a7a", "#a8202e", cy=640)
    GAMER.draw(ctx, 360, 1000, 1.25, "determined", T, arms=("cross", "cross"))
    for i, (txt, bg, x, y, tk) in enumerate((("SLEEP", st.BLUE, 170, 330, 2.02), ("FOOD", "#ff8a3d", 550, 420, 2.32),
                                              ("BATH", "#4fb0e8", 190, 560, 2.65))):
        label(ctx, txt, x, y, 52, bg=bg, scale=pop(T - tk), tilt=-0.08 + i * 0.07)
        st.red_x(ctx, x, y, 55, (T - tk - 0.08) / 0.15)
    label(ctx, "NO BREAKS!", 360, 280, 60, fg=(1, 1, 1), scale=pop(T - 2.65) if T > 2.65 else 0.0)


# ================================================================ hours
def s_hour1(ctx, t, d):
    T = 3.0 + t
    desk_scene(ctx, T, GAMER, "happy")
    card(ctx, T, "HOUR 1", 3.0)


def s_best(ctx, t, d):
    T = 4.0 + t
    desk_scene(ctx, T, GAMER, keyed(T, [(0, "happy"), (4.81, "laugh")]), arms=("up", "up"))
    st.confetti(ctx, T, 4.5, n=40)
    label(ctx, "VICTORY x50", 360, 330, 60, bg=st.GREEN, scale=pop(T - 4.5))
    label(ctx, "BEST SESSION EVER", 360, 440, 44, fg=st.YELLOW, scale=pop(T - 5.1))


def s_hour5(ctx, t, d):
    T = 6.0 + t
    desk_scene(ctx, T, GAMER, keyed(T, [(0, "neutral"), (6.48, "worried")]), cans=6, dark=0.15)
    card(ctx, T, "HOUR 5", 6.0)


def s_mom_yells(ctx, t, d):
    T = 7.3 + t
    st.stairs(ctx, T)
    MOM.draw(ctx, 170, 1180, 1.3, keyed(T, [(0, "cold"), (7.76, "angry")]), T, arms=("up", "up"), look=0.6)
    if T > 7.76:   # shout waves climbing the stairs
        for k in range(3):
            ph = ((T - 7.76) * 1.5 + k / 3) % 1
            r = 80 + ph * 300
            ctx.new_sub_path()
            ctx.arc(250, 800, r, -1.2, -0.3)
            ctx.set_source_rgba(1, 1, 1, 0.8 * (1 - ph))
            ctx.set_line_width(10)
            ctx.stroke()
    label(ctx, "DOWNSTAIRS", 420, 330, 52, bg="#8a5a3a", scale=pop(T - 8.2))


def s_dinner(ctx, t, d):
    T = 8.85 + t
    st.kitchen(ctx, T, night=False)
    closeup(ctx, MOM, "angry", T, arms=("up", "down"))
    st.speech_bubble(ctx, 380, 320, "DINNER'S READY!", 50, T - 8.91, tail=(1, 1))


def s_scream_back(ctx, t, d):
    T = 9.6 + t
    desk_scene(ctx, T, GAMER, keyed(T, [(0, "neutral"), (10.0, "angry")]), look=-1.0, cans=6)
    if T > 10.0:
        style.shake_lines(ctx, 360, 700, 160, 150, T, lw=6)
    st.speech_bubble(ctx, 210, 360, "WHAT?!", 50, T - 10.54, tail=(1, 1))


def s_five_more(ctx, t, d):
    T = 10.8 + t
    st.burst(ctx, T, "#ffd0e6", "#ff5fa2", cy=560)
    closeup(ctx, GAMER, keyed(T, [(0, "cry"), (11.67, "forced")]), T, arms=("up", "up"))
    st.speech_bubble(ctx, 360, 320, "5 MORE MINUTES!", 52, T - 10.85, tail=(-1, 1))


# ================================================================ days
def bed_kid(ctx, T, expr, tablet_fn=None, smear=0.0):
    st.night_bedroom(ctx, T)
    GAMER.draw(ctx, 230, 1150, 1.5, expr, T, arms=("hold", "hold"), pose="sit")
    st.checker(ctx, -60, 1075, 470, 200, n=7)
    st.tablet(ctx, 230, 1000, 0.6, T, tablet_fn, smear=smear)


def s_day1(ctx, t, d):
    T = 12.25 + t
    bed_kid(ctx, T, "happy", obby_screen())
    card(ctx, T, "DAY 1", 12.25)


def s_pb(ctx, t, d):
    T = 13.1 + t
    st.burst(ctx, T, "#ffe0b0", "#c98a3e", cy=600)
    for side in (-1, 1):   # the kid's blocky hands holding the iPad
        st.block(ctx, 360 + side * 290 - 60, 700, 120, 260, 18, KID.shirt, 5)
    st.tablet(ctx, 360, 700, 1.35, T, obby_screen(), smear=clamp((T - 13.6) / 0.6))
    if T > 14.5:
        ctx.save()
        sc = pop(T - 14.5)
        ctx.translate(560, 1130)
        ctx.scale(sc, sc)
        st.pb_jar(ctx, 0, 0, 0.85)
        ctx.restore()
    label(ctx, "PEANUT BUTTER", 330, 330, 54, bg="#c98a3e", scale=pop(T - 14.5))


def s_glued(ctx, t, d):
    T = 15.15 + t
    st.night_bedroom(ctx, T)
    shake = math.sin(T * 30) * 25 if T > 15.3 else 0
    GAMER.draw(ctx, 360 + shake * 0.3, 1040, 1.35, keyed(T, [(0, "worried"), (15.86, "scared")]), T,
               arms=("hold", "hold"))
    st.tablet(ctx, 360 + shake, 870, 0.62, T, obby_screen(), smear=1.0, tilt=shake * 0.004)
    label(ctx, "STUCK!", 360, 330, 84, fg=hexc("#c98a3e"), scale=pop(T - 15.86))


def s_day3(ctx, t, d):
    T = 16.75 + t
    desk_scene(ctx, T, GAMER, "sleepy", arms=("hold", "hold"), cans=6, dark=0.2)
    st.zzz(ctx, 470, 620, T)
    card(ctx, T, "DAY 3", 16.75)


def s_afk(ctx, t, d):
    T = 17.9 + t
    desk_scene(ctx, T, GAMER, "sleepy", cans=6, cob=clamp((T - 18.2) / 1.0), dark=0.2)
    st.zzz(ctx, 470, 620, T)
    label(ctx, "AFK", 360, 330, 90, bg="#7a7f90", scale=pop(T - 17.94))


def s_avatar_looks(ctx, t, d):
    T = 19.4 + t

    def screen(c, x, y, w, h, TT):
        st.screen_obby(c, x, y, w, h, TT, None, "STAGE 37")
        AVATAR.draw(c, x + w / 2, y + h * 0.9, w / 620, keyed(TT, [(0, "neutral"), (19.79, "smirk")]), TT,
                    arms=("down", "down"), look=-0.6 if TT < 19.79 else 0.0)
    monitor_scene(ctx, T, screen, s=1.15)
    st.glow(ctx, 360, 600, 380, (0.6, 0.9, 1), 0.2)


def s_plays_itself(ctx, t, d):
    T = 20.3 + t
    st.night_wall(ctx, 2000)
    st.monitor(ctx, 360, 720, 0.95, T, obby_screen("STAGE 99", jump=1.0, avatar_expr="smug"))
    st.keyboard(ctx, 360, 990, 1.0, T, mash=1.0)
    label(ctx, "BY ITSELF?!", 360, 300, 66, fg=st.YELLOW, scale=pop(T - 21.34))


# ================================================================ weeks
def s_week1(ctx, t, d):
    T = 22.25 + t
    desk_scene(ctx, T, GAMER, "smirk", cans=6, boxes=6)
    card(ctx, T, "WEEK 1", 22.25)


def s_wifi_dead(ctx, t, d):
    T = 23.05 + t
    st.night_wall(ctx, 2000)
    st.block(ctx, -100, 960, 920, 400, 0, hexc("#7a6aa8"), 5, gloss=False)
    st.router(ctx, 360, 960, 1.2, T, dead=1.0 if T > 24.05 else 0.0)
    if T > 24.05:
        st.impact_star(ctx, 360, 780, 120, T - 24.05)
    label(ctx, "NO INTERNET", 360, 330, 64, bg=st.RED, scale=pop(T - 24.3))


def s_sneak(ctx, t, d):
    T = 24.45 + t
    st.night_bedroom(ctx, T, door_open=0.0)
    st.tint(ctx, (0.03, 0.03, 0.15), 0.35)
    k = ease((T - 24.5) / 1.2)
    KID_SH.draw(ctx, lerp(220, 440, k), 1030, 1.2, "smirk", T, pose="walk", walk_phase=T * 1.2,
                arms=("hold", "hold"))
    st.laptop(ctx, lerp(220, 440, k), 905, 0.35, T, back=True)
    st.speech_bubble(ctx, 470, 380, "SHHH...", 50, T - 24.89, tail=(-1, 1))


def s_neighbor(ctx, t, d):
    T = 25.8 + t
    st.burst(ctx, T, "#a8e6ff", "#4fb0e8", cy=600)
    st.wifi_list(ctx, 360, 280, 1.0, T, ["NEIGHBOR_5G", "Grandma's WiFi", "FBI_Van_3"], connected_t=25.9)
    KID.draw(ctx, 360, 1010, 0.75, "smug", T, arms=("hip", "hip"))


def s_week2(ctx, t, d):
    T = 26.7 + t
    desk_scene(ctx, T, GAMER, "happy", cans=6, boxes=10)
    card(ctx, T, "WEEK 2", 26.7)


def s_pizza(ctx, t, d):
    T = 27.55 + t
    st.night_bedroom(ctx, T)
    n = 3 + int(clamp((T - 27.6) / 0.9) * 17)
    st.pizza_tower(ctx, 470, 1100, n, w=260, T=T)
    KID.draw(ctx, 200, 1100, 0.95, keyed(T, [(0, "happy"), (28.42, "shock")]), T, arms=("down", "down"),
             look=0.8)
    label(ctx, "PIZZA MOUNTAIN", 360, 300, 56, bg=st.RED, scale=pop(T - 28.14))


def s_taller(ctx, t, d):
    T = 29.3 + t
    st.night_bedroom(ctx, T)
    top = st.pizza_tower(ctx, 470, 1100, 20, w=260, T=T)
    KID.draw(ctx, 200, 1100, 0.95, "shock", T, arms=("up", "up"), look=0.8)
    kid_top = 1100 - 3.3 * U1 * 0.95
    for xx, yt, c in ((640, top, st.RED), (70, kid_top, st.BLUE)):   # height arrows
        st.arrow(ctx, xx, 1090, xx, yt + 30, col=c, w=16, k=clamp((T - 29.48) / 0.3))
    label(ctx, "TALLER THAN YOU", 360, 300, 52, fg=st.YELLOW, scale=pop(T - 29.48))


def s_not_much(ctx, t, d):
    T = 30.35 + t
    st.night_wall(ctx, 2000)
    closeup(ctx, KID, keyed(T, [(0, "smirk"), (30.9, "forced")]), T)
    label(ctx, "NOT SAYING MUCH...", 360, 300, 50, fg=(1, 1, 1), scale=pop(T - 30.74))


def s_short(ctx, t, d):
    T = 31.5 + t
    st.night_bedroom(ctx, T, door_open=0.0)
    st.height_ruler(ctx, 520, 1100, 500)
    KID.draw(ctx, 400, 1100, 0.42, "sad", T, arms=("down", "down"), look=0.5)
    st.arrow(ctx, 300, 820, 390, 960, k=clamp((T - 31.97) / 0.25))
    label(ctx, "REALLY SHORT!", 360, 330, 66, bg=st.PINK, scale=pop(T - 31.97))


# ================================================================ years
def s_year1(ctx, t, d):
    T = 32.7 + t
    desk_scene(ctx, T, GAMER, "determined", cans=6, boxes=14, cob=0.5)
    card(ctx, T, "YEAR 1", 32.7)


def s_graduate(ctx, t, d):
    T = 33.45 + t
    st.burst(ctx, T, "#ffe27a", "#f29a2e", cy=600)
    thrown = T > 34.15
    for i, x in enumerate((100, 230, 360, 490, 620)):
        y = 1000 + (i % 2) * 40
        s = 0.8
        FRIENDS[i].draw(ctx, x, y, s, "laugh" if thrown else "happy", T, arms=("up", "up") if thrown else
                        ("down", "show"))
        head_top = y - 3.0 * U1 * s
        if thrown:
            h = (T - 34.15) * 700 - (T - 34.15) ** 2 * 600
            st.grad_cap(ctx, x + (i - 2) * 20 * (T - 34.15), head_top - h, 0.6, tilt=(T - 34.15) * 4 * (1 if i % 2 else -1))
        else:
            st.grad_cap(ctx, x, head_top + 10, 0.6)
    st.confetti(ctx, T, 34.15, n=40)
    label(ctx, "GRADUATED!", 360, 300, 70, bg=st.BLUE, scale=pop(T - 34.15))


def s_same_obby(ctx, t, d):
    T = 35.2 + t
    n = int(lerp(1, 9999, ease((T - 35.25) / 0.9)))
    monitor_scene(ctx, T, obby_screen("STAGE 1", fail=f"FAILS: {n:,}", avatar_expr="cry"), s=1.15)
    st.red_x(ctx, 580, 470, 50, (T - 35.21) / 0.2)


def s_same_cry(ctx, t, d):
    T = 36.4 + t
    st.night_wall(ctx, 2000)
    closeup(ctx, GAMER, "cry", T)
    label(ctx, "SAME OBBY...", 360, 300, 64, fg=(1, 1, 1), scale=pop(T - 37.25))


def s_year10(ctx, t, d):
    T = 37.7 + t
    desk_scene(ctx, T, ADULT, "determined", cans=6, boxes=16, cob=0.7)
    card(ctx, T, "YEAR 10", 37.7)


def s_trophy_box(ctx, t, d):
    T = 38.5 + t
    st.dark_glow_bg(ctx, T, glow_col="#ffcc33", base="#2a1a3a")
    rise = ease((T - 40.07) / 0.5)
    if T > 40.0:
        st.trophy(ctx, 360, 1040 - rise * 260, 0.9 * (0.4 + 0.6 * rise), T)
    st.delivery_box(ctx, 360, 1120, 1.1, open_k=ease((T - 39.61) / 0.3))
    label(ctx, "FROM ROBLOX HQ", 360, 300, 50, bg=st.RED, scale=pop(T - 38.56))


def s_longest(ctx, t, d):
    T = 40.85 + t
    st.burst(ctx, T, "#ffe27a", "#f29a2e", cy=560)
    ADULT.draw(ctx, 360, 1080, 1.3, keyed(T, [(0, "stars"), (42.2, "grin")]), T, arms=("up", "up"))
    st.trophy(ctx, 360, 680, 0.55, T, plaque="#1 PLAYER")
    label(ctx, "LONGEST ONLINE", 360, 300, 54, fg=st.YELLOW, scale=pop(T - 41.3))
    label(ctx, "PLAYER EVER", 360, 375, 54, fg=st.YELLOW, scale=pop(T - 42.2))


def s_year50(ctx, t, d):
    T = 42.85 + t
    desk_scene(ctx, T, GRANDPA, "happy", cans=6, boxes=20, cob=1.0)
    card(ctx, T, "YEAR 50", 42.85)


def s_grandkids(ctx, t, d):
    T = 44.0 + t
    st.night_bedroom(ctx, T, door_open=ease((T - 44.47) / 0.3))
    GRANDPA.draw(ctx, 210, 1060, 1.1, "happy", T, arms=("hold", "hold"), look=0.8)
    k = ease((T - 44.9) / 0.8)
    for g, x0, x1, s in ((GK1, 640, 480, 0.75), (GK2, 700, 590, 0.65)):
        if T > 44.6:
            g.draw(ctx, lerp(x0, x1, k), 1060, s, "happy", T, pose="walk" if k < 1 else "stand",
                   walk_phase=T * 2.2, look=-0.6)
    label(ctx, "GRANDKIDS", 360, 300, 60, bg=st.PINK, scale=pop(T - 44.47))


def s_grandpa_call(ctx, t, d):
    T = 45.85 + t
    st.burst(ctx, T, "#ffd0e6", "#ff5fa2", cy=560)
    closeup(ctx, GK1, "happy", T, arms=("wave", "down"))
    st.speech_bubble(ctx, 360, 320, "GRANDPA!", 64, T - 45.95, tail=(1, 1))


def s_help_obby(ctx, t, d):
    T = 46.95 + t
    st.night_bedroom(ctx, T)
    GK2.draw(ctx, 260, 1060, 1.15, "grin", T, arms=("show", "show"))
    st.tablet(ctx, 260, 760, 0.6, T, obby_screen("STAGE 1"))
    st.speech_bubble(ctx, 520, 470, "HELP US?", 50, T - 47.16, tail=(-1, 1))


def s_notice(ctx, t, d):
    T = 48.65 + t
    st.night_bedroom(ctx, T)
    st.tint(ctx, (0.05, 0.05, 0.2), 0.3)
    for g, x, s in ((GK1, 420, 0.95), (GK2, 590, 0.85)):
        g.draw(ctx, x, 1060, s, keyed(T, [(0, "worried"), (49.3, "shock")]), T, look=-1.0)
    GRANDPA.draw(ctx, 170, 1060, 1.1, "happy", T, arms=("hold", "hold"), look=0.6)
    st.stink_lines(ctx, 170, 780, 120, T, k=clamp((T - 49.15) / 0.4))
    label(ctx, "?!", 500, 380, 90, fg=st.YELLOW, scale=pop(T - 49.56))


def s_stink(ctx, t, d):
    T = 49.95 + t
    st.burst(ctx, T, "#c8f0a0", "#4a9a3a", cy=600)
    GRANDPA.draw(ctx, 180, 1060, 1.15, "happy", T, arms=("wave", "down"))
    st.stink_lines(ctx, 180, 760, 160, T)
    st.flies(ctx, 180, 650, 140, T)
    for g, x, s in ((GK1, 430, 1.0), (GK2, 590, 0.9)):
        g.draw(ctx, x, 1060, s, "disgust", T, arms=("cover", "down"), look=-1.0)
    label(ctx, "EWW!", 470, 330, 90, fg=hexc("#7ccf3a"), scale=pop(T - 50.15))
    label(ctx, "YOU STINK!", 360, 450, 70, fg=(1, 1, 1), scale=pop(T - 51.12))


# ================================================================ ending
def s_legend(ctx, t, d):
    T = 52.4 + t
    st.dark_glow_bg(ctx, T, glow_col="#ffcc33", base="#2a1a3a")
    k = ease((T - 52.45) / 0.5)
    st.scroll(ctx, 360, 680, 1.0, T, open_k=k)
    if k > 0.8:
        GRANDPA.draw(ctx, 360, 900, 0.85, "smug", T, arms=("hold", "hold"), bob=0.3)
        st.tint(ctx, (0.8, 0.6, 0.3), 0.1)
    label(ctx, "LEGEND SAYS...", 360, 300, 60, fg=st.YELLOW, scale=pop(T - 53.06))


def s_likesub(ctx, t, d):
    T = 53.85 + t
    st.burst(ctx, T, "#a8e6ff", "#4fb0e8", cy=640)
    st.like_button(ctx, 360, 470, 1.1, pressed=1.0 if T > 54.2 else 0.0)
    st.subscribe_button(ctx, 360, 780, 1.1, pressed=clamp((T - 54.53) * 4))
    kx, ky = (420, 520) if T < 54.4 else (420, 820)
    st.cursor(ctx, kx, ky, 1.6, click=1.0 if (54.2 < T < 54.32 or 54.53 < T < 54.65) else 0.0)


def s_comment(ctx, t, d):
    T = 55.2 + t
    st.night_bedroom(ctx, T)
    typed = "SHOWER"[:int(clamp((T - 55.45) / 0.35) * 6)]
    st.comments_sheet(ctx, T, [("@gamer_kid", "grandpa is a legend", "#ff5fa2"),
                               ("@blockfan", "he needs a SHOWER", "#4f8bff")], typed=typed, y0=560, likes_t=55.85)
    label(ctx, "COMMENT \"SHOWER\"", 360, 330, 50, bg=st.RED, scale=pop(T - 55.45))


def bathroom(ctx, T):
    ctx.rectangle(-3000, -5000, 7000, 10000)
    ctx.set_source_rgb(*hexc("#bfe6f5"))
    ctx.fill()
    for i in range(-10, 20):
        for j in range(-4, 20):
            ctx.rectangle(i * 80 + 3, j * 80 + 3, 74, 74)
    ctx.set_source_rgba(1, 1, 1, 0.35)
    ctx.fill()
    st.floor(ctx, 1140, "#8ab8d0", "#7aa8c0")


def s_bath(ctx, t, d):
    T = 56.35 + t
    bathroom(ctx, T)
    GRANDPA.draw(ctx, 360, 1240, 1.2, keyed(T, [(0, "happy"), (57.61, "laugh")]), T, arms=("up", "up"), bob=0.6)
    st.bathtub(ctx, 360, 1140, 1.1, T, bubbles=1.0)
    st.rubber_duck(ctx, 520, 860, 0.8, T)
    label(ctx, "FIRST BATH", 360, 330, 72, bg=st.BLUE, scale=pop(T - 57.61))


def s_fifty(ctx, t, d):
    T = 58.3 + t
    st.burst(ctx, T, "#a8e6ff", "#4fb0e8", cy=560)
    closeup(ctx, GRANDPA, "laugh", T, arms=("up", "up"))
    st.rubber_duck(ctx, 600, 470, 0.8, T)
    st.sparkles(ctx, T, 360, 600, spread=300, n=12, seed=3)
    label(ctx, "50 YEARS!", 360, 290, 80, fg=st.YELLOW, scale=pop(T - 58.34))


def s_end(ctx, t, d):
    s_hook(ctx, t, d, T0=0.0, frozen=True)   # the first frame again: the Short loops


# ================================================================ shots
S = []


def shot(start, draw, keys, **kw):
    kw.setdefault("vignette", 0.15)
    kw.setdefault("top", 250)                # every shot carries the playtime HUD
    S.append(dict(start=start, draw=draw, keys=keys, **kw))


def punch(t0, z0, c0, t_key, z1, c1, m=0.16):
    return [(t0, z0, c0), (t_key, z1, c1, m)]


C = (360, 700)
CU = dict(closeup=True, keep=FACE_KEEP)
CARD = [(170, 330, 550, 470)]               # the painted chapter card
shot(0.00, s_hook, [(0.0, 1.25, (360, 640)), (0.12, 1.0, (360, 700), 0.12), (0.73, 1.1, (360, 660), 0.12)],
     shake=(0.73, 10), **CU)
shot(1.05, s_playing, punch(1.05, 1.0, C, 1.34, 1.08, (360, 680), 0.14))
shot(1.75, s_nobreak, punch(1.75, 1.0, C, 2.65, 1.06, (360, 700), 0.12), shake=(0.9, 14),
     keep=[(100, 280, 620, 620)])
shot(3.0, s_hour1, punch(3.0, 1.0, C, 3.45, 1.06, (360, 680), 0.15), keep=CARD)
shot(4.0, s_best, punch(4.0, 1.0, C, 4.81, 1.1, (360, 660), 0.14), shake=(0.81, 8))
shot(6.0, s_hour5, punch(6.0, 1.0, C, 6.48, 1.08, (360, 700), 0.15), keep=CARD)
shot(7.3, s_mom_yells, punch(7.3, 1.0, C, 7.76, 1.08, (300, 760), 0.14), shake=(0.46, 10))
shot(8.85, s_dinner, punch(8.85, 1.0, C, 8.91, 1.1, (360, 660), 0.1), shake=(0.06, 16), closeup=True,
     keep=FACE_KEEP + [(120, 270, 640, 370)])
shot(9.6, s_scream_back, punch(9.6, 1.0, C, 10.0, 1.12, (360, 660), 0.12), shake=(0.4, 12))
shot(10.8, s_five_more, punch(10.8, 1.0, C, 10.85, 1.1, (360, 660), 0.1), shake=(0.05, 12), closeup=True,
     keep=FACE_KEEP + [(120, 270, 640, 370)])
shot(12.25, s_day1, punch(12.25, 1.0, (360, 760), 12.5, 1.06, (360, 740), 0.15), keep=CARD)
shot(13.1, s_pb, punch(13.1, 1.0, C, 14.5, 1.08, (380, 720), 0.14), keep=[(80, 560, 640, 840)])
shot(15.15, s_glued, punch(15.15, 1.0, C, 15.86, 1.1, (360, 700), 0.12), shake=(0.71, 12))
shot(16.75, s_day3, punch(16.75, 1.0, C, 17.24, 1.06, (360, 700), 0.15), keep=CARD)
shot(17.9, s_afk, punch(17.9, 1.0, C, 17.94, 1.1, (360, 680), 0.12))
shot(19.4, s_avatar_looks, punch(19.4, 1.0, (360, 640), 19.79, 1.25, (360, 600), 0.16),
     keep=[(100, 340, 620, 700)])
shot(20.3, s_plays_itself, punch(20.3, 1.0, C, 21.34, 1.08, (360, 680), 0.14), shake=(1.04, 8))
shot(22.25, s_week1, punch(22.25, 1.0, C, 22.73, 1.06, (360, 700), 0.15), keep=CARD)
shot(23.05, s_wifi_dead, punch(23.05, 1.0, C, 24.05, 1.12, (360, 760), 0.12), shake=(1.0, 14),
     keep=[(150, 660, 570, 960)])
shot(24.45, s_sneak, punch(24.45, 1.0, (360, 760), 24.89, 1.06, (380, 760), 0.2))
shot(25.8, s_neighbor, punch(25.8, 1.0, C, 25.9, 1.05, (360, 680), 0.1), keep=[(80, 280, 640, 720)])
shot(26.7, s_week2, punch(26.7, 1.0, C, 27.23, 1.06, (360, 700), 0.15), keep=CARD)
shot(27.55, s_pizza, [(27.55, 1.0, (360, 760)), (28.42, 1.0, (360, 700), 0.6)])
shot(29.3, s_taller, punch(29.3, 1.0, (360, 720), 29.48, 1.04, (360, 720), 0.15))
shot(30.35, s_not_much, punch(30.35, 1.0, C, 30.74, 1.06, (360, 680), 0.14), **CU)
shot(31.5, s_short, [(31.5, 1.5, (400, 900)), (31.97, 1.0, (360, 760), 0.25)], keep=[(300, 590, 560, 1100)])
shot(32.7, s_year1, punch(32.7, 1.0, C, 33.09, 1.06, (360, 700), 0.15), keep=CARD)
shot(33.45, s_graduate, punch(33.45, 1.0, (360, 760), 34.15, 1.06, (360, 720), 0.14))
shot(35.2, s_same_obby, punch(35.2, 1.0, C, 35.8, 1.1, (360, 640), 0.15), keep=[(90, 340, 630, 700)])
shot(36.4, s_same_cry, punch(36.4, 1.0, C, 37.25, 1.08, (360, 660), 0.14), **CU)
shot(37.7, s_year10, punch(37.7, 1.0, C, 38.28, 1.06, (360, 700), 0.15), keep=CARD)
shot(38.5, s_trophy_box, punch(38.5, 1.0, C, 40.07, 1.08, (360, 760), 0.15), keep=[(150, 560, 570, 1120)])
shot(40.85, s_longest, punch(40.85, 1.0, C, 41.3, 1.06, (360, 680), 0.14), keep=[(100, 260, 620, 420)])
shot(42.85, s_year50, punch(42.85, 1.0, C, 43.54, 1.06, (360, 700), 0.15), keep=CARD)
shot(44.0, s_grandkids, punch(44.0, 1.0, (360, 760), 44.47, 1.04, (380, 760), 0.15))
shot(45.85, s_grandpa_call, punch(45.85, 1.0, C, 45.95, 1.1, (360, 660), 0.1), shake=(0.1, 10), closeup=True,
     keep=FACE_KEEP + [(140, 270, 600, 370)])
shot(46.95, s_help_obby, punch(46.95, 1.0, C, 47.16, 1.06, (360, 700), 0.12), keep=[(110, 640, 410, 880)])
shot(48.65, s_notice, [(48.65, 1.0, (360, 760)), (49.56, 1.08, (300, 760), 0.6)])
shot(49.95, s_stink, punch(49.95, 1.0, C, 50.15, 1.1, (360, 700), 0.1), shake=(0.2, 16))
shot(52.4, s_legend, punch(52.4, 1.0, C, 53.06, 1.06, (360, 700), 0.15), keep=[(120, 380, 600, 980)])
shot(53.85, s_likesub, punch(53.85, 1.0, C, 54.53, 1.06, (360, 680), 0.15), keep=[(120, 360, 600, 860)])
shot(55.2, s_comment, punch(55.2, 1.0, C, 55.81, 1.04, (360, 720), 0.2))
shot(56.35, s_bath, punch(56.35, 1.0, (360, 760), 57.61, 1.06, (360, 740), 0.15), keep=[(90, 800, 620, 1000)])
shot(58.3, s_fifty, punch(58.3, 1.0, C, 58.34, 1.08, (360, 660), 0.1), shake=(0.04, 12), closeup=True,
     keep=FACE_KEEP + [(160, 240, 560, 340)])
shot(59.35, s_end, [(59.35, 1.0, C)], **CU)
SHOTS = S
for k, s in enumerate(SHOTS):
    s["end"] = SHOTS[k + 1]["start"] if k + 1 < len(SHOTS) else TOTAL

# ---------------------------------------------------------------- the playtime HUD (screen space, every shot)
HUD = [(3.0, "1:00:00"), (6.0, "5:00:00"), (12.25, "DAY 1"), (16.75, "DAY 3"), (22.25, "WEEK 1"),
       (26.7, "WEEK 2"), (32.7, "YEAR 1"), (37.7, "YEAR 10"), (42.85, "YEAR 50")]


def hud_text(T):
    cur = (0.0, f"0:00:{min(59, int(T * 20)):02d}")   # the hook: seconds racing up
    for ts, txt in HUD:
        if T >= ts:
            cur = (ts, txt)
    return cur


def make_overlay(T0, frozen=False):
    def ov(ctx, t, d):
        T = T0 if frozen else T0 + t
        ts, txt = hud_text(T)
        st.hud_timer(ctx, txt, bump=math.exp(-9 * (T - ts)) if ts > 0 else 0.0)
    return ov


for s in SHOTS:
    s["overlay"] = make_overlay(0.0, frozen=True) if s["draw"] is s_end else make_overlay(s["start"])

# ---------------------------------------------------------------- SFX (time, file, volume before SFX_GAIN)
SFX = [
    (0.03, "boom.wav", 1.6), (0.21, "pop.wav", 0.7), (0.73, "hit.wav", 1.3), (1.1, "type_key.wav", 0.6),
    (1.34, "pop.wav", 0.6), (2.02, "hit.wav", 1.3), (2.32, "hit.wav", 1.3), (2.65, "boom.wav", 1.6),
    (3.0, "hit.wav", 1.3), (3.05, "tick.wav", 0.7), (4.5, "pop.wav", 0.7), (4.81, "ding.wav", 0.8),
    (5.61, "pop.wav", 0.7), (6.0, "hit.wav", 1.3), (6.05, "tick.wav", 0.7), (7.51, "pop.wav", 0.7),
    (7.76, "hit.wav", 1.3), (8.2, "pop.wav", 0.6), (8.91, "boom.wav", 1.6), (10.0, "swish.wav", 0.7),
    (10.54, "hit.wav", 1.3), (10.85, "pop.wav", 0.8), (11.67, "pop.wav", 0.7),
    (12.25, "hit.wav", 1.3), (12.3, "tick.wav", 0.7), (13.19, "pop.wav", 0.6), (13.63, "pop.wav", 0.6),
    (14.11, "pop.wav", 0.6), (14.5, "ding.wav", 0.8), (15.3, "boing.wav", 0.7), (15.86, "hit.wav", 1.3),
    (16.33, "boing.wav", 0.6), (16.75, "hit.wav", 1.3), (16.8, "tick.wav", 0.7), (17.94, "pop.wav", 0.8),
    (19.53, "pop.wav", 0.7), (19.79, "sparkle.wav", 0.7),
    (20.32, "type_key.wav", 0.6), (20.6, "type_key.wav", 0.6), (20.93, "pop.wav", 0.7), (21.34, "ding.wav", 0.8),
    (22.25, "hit.wav", 1.3), (22.3, "tick.wav", 0.7), (23.26, "pop.wav", 0.6), (24.05, "buzz.wav", 0.8),
    (24.3, "boom.wav", 1.4), (24.89, "step.wav", 0.6), (25.2, "step.wav", 0.6), (25.9, "success.wav", 0.8),
    (26.26, "pop.wav", 0.6), (26.7, "hit.wav", 1.3), (26.75, "tick.wav", 0.7), (28.14, "tick.wav", 0.6), (28.42, "pop.wav", 0.7), (28.97, "pop.wav", 0.6),
    (29.48, "hit.wav", 1.3), (30.39, "pop.wav", 0.6), (30.9, "pop.wav", 0.5), (31.52, "swish.wav", 0.6),
    (31.97, "boing.wav", 0.8), (32.28, "hit.wav", 1.0), (32.7, "hit.wav", 1.3), (32.75, "tick.wav", 0.7),
    (33.76, "pop.wav", 0.7), (34.15, "ding.wav", 0.8), (34.78, "pop.wav", 0.7), (35.21, "buzz.wav", 0.8),
    (37.25, "pop.wav", 0.7), (37.52, "hit.wav", 1.0),
    (37.7, "hit.wav", 1.3), (37.75, "tick.wav", 0.7), (38.56, "pop.wav", 0.6), (39.61, "swish.wav", 0.6),
    (40.07, "sparkle.wav", 0.9), (40.46, "ding.wav", 0.9), (41.3, "chaching.wav", 0.9), (42.2, "pop.wav", 0.7),
    (42.52, "hit.wav", 1.3), (42.85, "hit.wav", 1.3), (42.9, "tick.wav", 0.7), (43.54, "pop.wav", 0.6),
    (44.47, "pop.wav", 0.7), (45.06, "step.wav", 0.6), (45.35, "step.wav", 0.6), (45.95, "pop.wav", 0.8),
    (46.95, "pop.wav", 0.7), (47.63, "pop.wav", 0.6), (48.1, "ding.wav", 0.7), (49.56, "pop.wav", 0.6), (50.15, "boom.wav", 1.6), (51.12, "hit.wav", 1.3),
    (51.5, "pop.wav", 0.6), (52.45, "swish.wav", 0.7), (53.06, "ding.wav", 0.8), (54.2, "click.wav", 0.9),
    (54.22, "pop.wav", 0.6), (54.53, "click.wav", 0.9), (55.5, "type_key.wav", 0.6), (55.65, "type_key.wav", 0.6),
    (55.81, "ding.wav", 0.8), (56.41, "swish.wav", 0.6), (56.96, "pop.wav", 0.7), (57.61, "pop.wav", 0.7),
    (57.9, "sparkle.wav", 0.8), (58.34, "hit.wav", 1.3), (58.82, "boom.wav", 1.4), (59.35, "whip.wav", 0.8),
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

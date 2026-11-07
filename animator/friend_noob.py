"""Story: "This Noob Is the REASON Roblox Has a Friend Limit... 😭" (Milo, the noob who friends everyone).

Voice: output/friend_noob/voice.mp3 (59.4 s, the user's voice tool, ~99 % speech) + subs.srt; word times from
analysis/align_words.py (they match the SRT). One voice acts every part; by pitch, the dialogue lines are
Milo "Best friend." (10.63) and "That's my friend!" (15.97), and the moderator "Please stop inviting me." (31.49).
Made with engine.profile("set3") (60 fps), the Roblox-world props and the analytics rules in lessons.md:
the first frame is the stake (Milo + friend requests + a friends counter near the limit), a new picture every
<= 0.8 s in the first 3 s, the punchline is the last line.

Shot plan (time | words | row | what is shown):
  0.00 This noob is the | hook | Milo close-up, friend-request cards popping, friends counter 9,990 -> 9,999
  0.89 reason / 1.30 Roblox has | teaser | flashes: 20 FULL servers, the moderator getting a bracelet
  1.73 a friend limit | game UI | "Friend Limit Reached" dialog slams in
  2.70 His name was Milo | named | close-up, the name pill pops on "Milo"
  3.76 and he had one rule | rule | Milo with the rule book, ONE RULE
  4.86 Nobody was allowed to be a stranger | action | a lonely player; Milo runs in and hugs him (HUG!)
  6.62 First, he added everyone / 7.53 everyone in his obby | list | obby + "request sent" toasts; friends counter climbs
  8.68 Even the guy who / 9.56 kept pushing him into lava | action | the bully's smug close-up; SHOVE! SPLASH!
 10.63 Best friend. | dialogue | Milo in the lava, thumbs up, a friend request to the bully
 11.49 Then he joined a racing game / 12.89 and added every driver | place + list | race car; three drivers get requests
 14.23 Whenever someone passed him / 15.57 he yelled, That's my friend! | action + dialogue | ZOOM!, Milo yelling
 16.95 By lunchtime / 18.12 so many friends / 19.03 his screen was just names | time + counter | clock; list; names
 20.38 But Milo wasn't finished | turn | smug close-up
 21.74 He invited them all / 22.91 to his birthday party | game UI | invite card; cake + party hats
 23.69 One server filled up / 24.98 Then another / 25.63 Then 20 more | counter | FULL servers: 1, 2, 20
 26.63 Players couldn't even play / 27.78 because Milo kept sending / 29.01 party invitations | action | invites cover the game; Milo mashing; a flood of invites
 30.10 Even the moderator got one / 31.49 Please stop inviting me | new character + dialogue | [MOD], begging close-up
 32.82 Milo sent him a friendship bracelet | gift | GIFT SENT, the bracelet
 34.63 Players started begging / 35.71 the developers to stop him | crowd + chat | kneeling crowd; chat lines
 36.93 So one developer finally / 38.65 created a brand new rule | place | dev at night; code
 39.60 Friend limit reached | reveal | the dialog, bump
 40.71 Milo tried adding another player / 42.39 Nothing happened | action | Add Friend button, greyed out, "..."
 43.34 For the first time / 44.35 he couldn't make a new friend | low beat (music dip) | Milo alone; crying close-up
 45.59 The entire server celebrated | payoff | crowd party
 47.30 But here's the crazy part / 48.56 Milo wasn't upset / 49.74 He had a plan | turn | shocked player; smug Milo; lightbulb
 50.49 He opened a brand new / 51.47 Roblox account | game UI | CREATE ACCOUNT screen; Milo_2 spawns
 52.33 And his very first friend request? / 54.02 He sent it to his original account | twist | card "?"; two Milos
 55.64 But Roblox rejected it | stamp | DECLINED
 57.00 Because even Milo / 58.35 couldn't be friends with himself | punchline | both Milos shrug; confused close-up
 59.30 REWIND to the first frame

Run (from animator/):
  python3 friend_noob.py ../output/friend_noob/clips/animation.mp4 ../output/friend_noob/cues.json"""
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
TOTAL = 60.2
SFX_GAIN = 0.2
MUSIC = dict(bpm=128, perc=0.6, dips=[(43.3, 45.55)])   # quieter under "he couldn't make a new friend"
DIALOGUE = {"milo": [(10.6, 11.3), (15.95, 16.85)], "mod": [(31.45, 32.78)]}

MILO = Block("#1a68cf", pants="#9bbc36", skin="#e9c22c", hair=None, sleeves="skin", shoes=None, cap="#4fd16a")
MILO2 = Block("#ff8a3d", pants="#2b3f8f", skin="#e9c22c", hair=None, sleeves="skin", shoes=None, cap="#4fd16a")
BULLY = Block("#e8323a", pants="#2b2f45", skin="#c89f82", hair="spiky", hair_col="#2a1a14", shoes="dark")
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


def closeup(ctx, ch, expr, T, x=360, look=0.0, arms=("down", "down"), s=FACE_S, talk=False, bob=0.35, dy=0,
            snap=None):
    ch.draw(ctx, x, 560 + 2.5 * U1 * s + dy, s, expr, T, arms=arms, look=look, talk=talk, bob=bob, snap=snap)


def milo(ctx, x, y, s, expr, T, tag=True, ch=None, name="Milo", **kw):
    (ch or MILO).draw(ctx, x, y, s, expr, T, **kw)
    if tag:
        st.name_pill(ctx, x, y - 3.5 * U1 * s, name, size=max(20, 24 * s))


def world(ctx, T, y=1000):
    st.game_sky(ctx)
    st.block_clouds(ctx, T)
    st.baseplate(ctx, y)


def lobby(ctx, T, y=1000):
    """Game lobby: sky, a rainbow arch, the studded baseplate."""
    st.game_sky(ctx)
    st.block_clouds(ctx, T)
    for i, c in enumerate(("#ff4f5a", "#ff8a3d", "#ffd84a", "#4fd16a", "#2f6bd8", "#9d5cff")):
        ctx.new_sub_path()
        ctx.arc(360, y - 40, 330 - i * 26, PI, 2 * PI)
        ctx.set_source_rgb(*hexc(c))
        ctx.set_line_width(26)
        ctx.stroke()
    st.baseplate(ctx, y)


def snap_at(T, t0):
    return (T - t0) if T >= t0 else None


# ================================================================ hook
def s_hook(ctx, t, d, T0=0.0, frozen=False):
    T = T0 + (0.0 if frozen else t)
    st.burst(ctx, T, "#b8ffb0", "#2e9c46", cy=560, spin=0.4)
    closeup(ctx, MILO, keyed(T, [(0, "grin"), (0.3, "crazy")]), T, arms=("wave", "down"), snap=snap_at(T, 0.3))
    for i, (x, y, tk) in enumerate(((180, 430, 0.0), (545, 520, 0.18), (180, 640, 0.36), (545, 330, 0.54))):
        st.friend_card(ctx, x, y, 0.48, NAMES[i + 1], k=T - tk if not frozen else 1.0, state="sent")
    st.friends_count(ctx, 330, 960, 9990 + min(9, int(T / 0.09)), s=1.0)
    label(ctx, "THIS NOOB", 340, 215, 74, fg=st.YELLOW, scale=1.0 if frozen else pop(T + 0.05))


def s_teaser(fn, t_off):
    def draw(ctx, t, d):
        fn(ctx, t + t_off, d)
        st.flash(ctx, 0.5 * math.exp(-25 * t))
    draw.__name__ = "teaser_" + fn.__name__
    return draw


def s_limit(ctx, t, d):
    T = 1.73 + t
    lobby(ctx, T)
    milo(ctx, 360, 1000, 1.0, keyed(T, [(0, "grin"), (1.91, "shock")]), T, arms=("point", "down"))
    st.roblox_dialog(ctx, 360, 470, 0.95, T - 1.91, "Friend Limit Reached", "You can't add any more friends.")


# ================================================================ intro
def s_named(ctx, t, d):
    T = 2.7 + t
    st.burst(ctx, T, "#bfe3ff", "#2f6bd8", cy=560)
    closeup(ctx, MILO, keyed(T, [(0, "happy"), (3.19, "grin")]), T, arms=("down", "wave"), snap=snap_at(T, 3.19))
    if T >= 3.19:
        st.name_pill(ctx, 360, 300, "Milo", size=44 * pop(T - 3.19) if T < 3.6 else 44)
    label(ctx, "MILO", 360, 215, 80, fg=st.GREEN, scale=pop(T - 3.19) if T >= 3.19 else 0.0)


def s_rule(ctx, t, d):
    T = 3.76 + t
    st.day_room(ctx, T, y_floor=1000)
    milo(ctx, 210, 1000, 1.05, "determined", T, arms=("point", "down"), look=0.5)
    st.rule_book(ctx, 470, 760, 0.7, T, title="RULE #1")
    label(ctx, "ONE RULE", 360, 260, 76, bg=st.RED, scale=pop(T - 4.09) if T >= 4.09 else 0.0)


def s_stranger(ctx, t, d):
    T = 4.86 + t
    world(ctx, T, 980)
    hug = 5.99
    P[1].draw(ctx, 470, 990, 1.0, "sad" if T < hug else "shock", T, pose="sit", arms=("down", "down"))
    if T < hug:
        st.speech_bubble(ctx, 520, 600, "...", 50, T - 5.0, tail=(-1, 1))
        x = lerp(80, 330, ease(clamp((T - 4.86) / (hug - 4.86))))
        milo(ctx, x, 1000, 1.0, "laugh", T, pose="run", walk_phase=T * 2.5, arms=("up", "up"), look=0.6)
    else:
        milo(ctx, 370, 1000, 1.0, "laugh", T, arms=("up", "up"), look=0.6)
        st.sfx_word(ctx, 420, 560, "HUG!", T - hug, col=st.PINK, size=56)
        st.hearts(ctx, T, hug, 420, 640, n=5)
    label(ctx, "NO STRANGERS!", 360, 250, 62, fg=st.YELLOW, scale=pop(T - hug) if T >= hug else 0.0)


# ================================================================ obby friends + lava
def s_obby_add(ctx, t, d):
    T = 6.62 + t
    tops = st.obby(ctx, T, y_lava=1060, y_top=930, x0=-80, dx=230, rise=-30, nums=False)
    x, y = tops[1]
    milo(ctx, x, y, 0.9, "grin", T, arms=("point", "down"), look=0.6)
    for i, (px, py) in enumerate(tops[2:4]):
        P[i + 2].draw(ctx, px, py, 0.8, "neutral", T, look=-0.5)
    for i, tk in enumerate((7.04, 7.24, 7.4)):
        st.game_toast(ctx, 360, 190 + i * 52, "Milo", f"sent {NAMES[i + 2]} a request", T - tk, icon_col=st.GREEN)
    st.sfx_word(ctx, 420, 480, "ADD!", T - 7.24, col=st.GREEN, size=50)


def s_count(ctx, t, d):
    T = 7.53 + t
    st.burst(ctx, T, "#b8ffb0", "#2e9c46", cy=600)
    n = int(3 + 45 * ease(clamp((T - 7.53) / 1.0)))
    st.friends_count(ctx, 360, 300, n, s=1.4)
    for i, (x, y, tk) in enumerate(((220, 560, 7.6), (500, 650, 7.85), (240, 800, 8.1))):
        st.friend_card(ctx, x, y, 0.55, NAMES[i + 4], k=T - tk, state="sent")
    st.sfx_word(ctx, 540, 450, "DING!", T - 7.6, col=st.YELLOW, size=44)


def s_bully(ctx, t, d):
    T = 8.68 + t
    st.obby(ctx, T, y_lava=1200, y_top=1150, nums=False)
    closeup(ctx, BULLY, keyed(T, [(0, "smirk"), (9.25, "smug")]), T, arms=("down", "hip"), snap=snap_at(T, 9.25))
    st.name_pill(ctx, 360, 300, "LavaJumper", size=36)


def s_push(ctx, t, d):
    T = 9.56 + t
    st.game_sky(ctx)
    st.block_clouds(ctx, T)
    st.lava(ctx, 1000, T)
    st.platform(ctx, 60, 760, 400, "#2cd5fc", h=70)
    BULLY.draw(ctx, 230, 760, 1.0, "laugh", T, arms=("punch", "down"), look=0.6)
    shove = 9.7
    if T < shove:
        milo(ctx, 360, 760, 1.0, "grin", T, tag=False)
    else:
        k = T - shove
        x = 360 + 300 * k
        y = 760 - 280 * k + 900 * k * k
        if y < 1000:
            ctx.save()
            ctx.translate(x, y - 120)
            ctx.rotate(k * 5)
            MILO.draw(ctx, 0, 120, 1.0, "scared", T, arms=("up", "up"), pose="jump", shadow=False)
            ctx.restore()
        st.sfx_word(ctx, 330, 560, "SHOVE!", k, col=st.RED, size=50)
    st.sfx_word(ctx, 480, 880, "SPLASH!", T - 10.11, col="#ff8a3d", size=52, tilt=0.12)
    if T >= 10.11:
        st.poof(ctx, 520, 1000, 70, (T - 10.11) / 0.5)


def s_bestfriend(ctx, t, d):
    T = 10.63 + t
    st.game_sky(ctx)
    st.block_clouds(ctx, T)
    milo(ctx, 300, 1080, 1.2, keyed(T, [(0, "laugh"), (10.97, "stars")]), T, arms=("up", "point"),
         talk=talking("milo", T), tag=False)
    st.lava(ctx, 900, T)                               # drawn over him: he is chest-deep in the lava
    st.friend_card(ctx, 360, 320, 0.8, "LavaJumper", k=T - 10.97, state="sent")
    st.hearts(ctx, T, 10.7, 300, 620, n=6)


# ================================================================ racing
def road(ctx, T, y=980, speed=1400):
    st.game_sky(ctx)
    st.block_clouds(ctx, T, drift=-300)
    ctx.rectangle(-3000, y - 20, 7000, 3000)
    ctx.set_source_rgb(*hexc("#51c844"))
    ctx.fill()
    style.block(ctx, -100, y, 920, 180, 0, hexc("#4a4f5e"), 5, gloss=False)
    for i in range(8):
        x = (i * 200 - (T * speed) % 200) - 100
        style.block(ctx, x, y + 80, 110, 16, 6, (1, 1, 1), 2, gloss=False)


def driver(ch, expr, T, s=0.75, talk=False):
    def fn(c, hx, hy):
        ch.draw(c, hx, hy + 150 * s * 1.06, s, expr, T, shadow=False, talk=talk)
    return fn


def s_race(ctx, t, d):
    T = 11.49 + t
    road(ctx, T)
    st.speed_lines(ctx, T, 360, 800, n=16, r0=240, r1=800, a=0.3)
    st.race_car(ctx, 340 + math.sin(T * 20) * 3, 1000, 1.0, T, driver=driver(MILO, "grin", T, s=0.9), speed=2.0,
                col="#4fd16a", num="7")
    st.name_pill(ctx, 290, 520, "Milo", size=30)
    label(ctx, "RACING!", 360, 250, 84, bg=st.RED, scale=pop(T - 12.18) if T >= 12.18 else 0.0)


def s_drivers(ctx, t, d):
    T = 12.89 + t
    road(ctx, T, y=1000, speed=600)
    for i, (x, col) in enumerate(((140, "#e8323a"), (360, "#ffd84a"), (580, "#9d5cff"))):
        st.race_car(ctx, x, 1100, 0.45, T, driver=driver(P[i + 5], "neutral", T, s=0.4), col=col, num=str(i + 1))
    for i, tk in enumerate((13.06, 13.38, 13.7)):
        st.friend_card(ctx, 360, 400 + i * 150, 0.7, NAMES[i + 6], k=T - tk, state="sent")
    label(ctx, "EVERY DRIVER", 360, 230, 64, fg=st.YELLOW, scale=pop(T - 13.38) if T >= 13.38 else 0.0)


def s_passed(ctx, t, d):
    T = 14.23 + t
    road(ctx, T, speed=900)
    p = ease(clamp((T - 14.5) / 0.5))
    st.race_car(ctx, lerp(-300, 470, p), 900, 0.7, T, driver=driver(P[8], "smug", T, s=0.62), col="#e8323a",
                num="1", speed=3.0)
    st.race_car(ctx, 330, 1110, 0.8, T, driver=driver(MILO, keyed(T, [(0, "grin"), (14.86, "shock")]), T),
                col="#4fd16a", num="7")
    if 14.6 < T < 15.4:
        st.speed_lines(ctx, T, lerp(-300, 470, p), 820, n=12, r0=100, r1=400, a=0.45)
    st.sfx_word(ctx, 470, 600, "ZOOM!", T - 14.86, col=st.BLUE, size=56)


def s_yell(ctx, t, d):
    T = 15.57 + t
    road(ctx, T, y=1300, speed=900)
    closeup(ctx, MILO, keyed(T, [(0, "determined"), (15.97, "crazy")]), T, arms=("up", "point"),
            talk=talking("milo", T), snap=snap_at(T, 15.97))
    st.speech_bubble(ctx, 360, 300, "THAT'S MY FRIEND!", 50, T - 16.0, tail=(0, 1))


# ================================================================ so many friends
def s_lunch(ctx, t, d):
    T = 16.95 + t
    st.kitchen(ctx, T, night=False)
    st.big_clock(ctx, 360, 520, 170, 11.5 + 0.5 * ease(clamp((T - 16.95) / 0.6)), T)
    label(ctx, "LUNCHTIME", 360, 240, 74, bg=st.UI_DARK, fg=st.YELLOW, scale=pop(T - 17.16) if T >= 17.16 else 0.0)
    milo(ctx, 360, 1000, 0.9, "grin", T, arms=("hold", "phone"))


def s_friendlist(ctx, t, d):
    T = 18.12 + t
    st.burst(ctx, T, "#b8ffb0", "#2e9c46", cy=600)
    n = int(48 + 9951 * ease(clamp((T - 18.2) / 0.7)))
    st.friends_count(ctx, 360, 280, n, s=1.5)
    st.player_list(ctx, 150, 400, NAMES[:9], T, s=1.4)
    st.sfx_word(ctx, 560, 380, "WOW!", T - 18.56, col=st.GREEN, size=44)


def s_names(ctx, t, d):
    T = 19.03 + t

    def screen(c, x, y, w, h, TT):
        c.set_source_rgb(*hexc("#20222b"))
        c.rectangle(x, y, w, h)
        c.fill()
        off = (TT * 260) % 40
        for i in range(int(h / 40) + 2):
            nm = NAMES[(i + int(TT * 6.5)) % len(NAMES)]
            st.bold_text(c, nm, x + 30 + (i % 3) * 150, y + i * 40 - off, 22, (1, 1, 1), align="l", shadow=False,
                         stroke=0.0)
    st.night_wall(ctx, 2000)
    st.monitor(ctx, 360, 900, 1.08, T, screen)
    st.face_icon(ctx, 600, 300, 34, "#e9c22c", "#4fd16a", expr="grin")
    label(ctx, "JUST NAMES", 360, 230, 70, fg=st.YELLOW, scale=pop(T - 19.79) if T >= 19.79 else 0.0)


def s_notfinished(ctx, t, d):
    T = 20.38 + t
    st.burst(ctx, T, "#e2c8ff", "#7a3fd8", cy=560)
    closeup(ctx, MILO, keyed(T, [(0, "smirk"), (21.24, "smug")]), T, arms=("down", "down"), snap=snap_at(T, 21.24))
    if T >= 21.24:
        style.sparkle(ctx, 450, 470, 40 * pop(T - 21.24))


# ================================================================ birthday party
def s_invite(ctx, t, d):
    T = 21.74 + t
    lobby(ctx, T)
    for i in range(4):
        st.invite_card(ctx, 380 + i * 18, 380 + i * 120, 0.8, "Milo", "Milo's Birthday Party!", T - (21.84 + i * 0.2))
    st.sfx_word(ctx, 200, 300, "POP!", T - 22.25, col=st.PINK, size=44)


def s_cake(ctx, t, d):
    T = 22.91 + t
    st.burst(ctx, T, "#ffd6ef", "#ff5fb0", cy=600)
    st.cake(ctx, 480, 990, 1.0, T)
    milo(ctx, 210, 1000, 1.0, "laugh", T, arms=("up", "up"), tag=False)
    st.party_hat(ctx, 210, 1000 - 3.0 * U1 * 1.0, 0.8)
    st.confetti(ctx, T, 22.95, n=40)
    label(ctx, "PARTY!", 360, 260, 90, fg=st.PINK, scale=pop(T - 23.29) if T >= 23.29 else 0.0)


def s_server1(ctx, t, d):
    T = 23.69 + t
    st.burst(ctx, T, "#c4d8ff", "#2f3f9a", cy=600)
    n = int(lerp(12, 50, clamp((T - 23.7) / 0.6)))
    if T < 24.32:                                          # the server fills up, then turns FULL
        style.block(ctx, 140, 430, 440, 270, 12, hexc("#2b2d36"), 3, outline=hexc("#15161c"))
        st.bold_text(ctx, "SERVER 1", 360, 520, 70, (1, 1, 1), shadow=False, stroke=0.0)
        st.bold_text(ctx, f"{n}/50", 360, 620, 56, st.GREEN, shadow=False, stroke=0.0)
    st.server_grid(ctx, 140, 430, 1, T, cols=1, k_rows=[T - 24.32], w=440, h=270)
    st.game_hud(ctx, T, players=n, y=300)
    st.sfx_word(ctx, 450, 780, "FULL!", T - 24.32, col=st.RED, size=50)


def s_server2(ctx, t, d):
    T = 24.98 + t
    st.burst(ctx, T, "#c4d8ff", "#2f3f9a", cy=600)
    st.server_grid(ctx, 70, 420, 2, T, cols=2, k_rows=[1.0, T - 25.14], w=280, h=260)


def s_server20(ctx, t, d):
    T = 25.63 + t
    st.burst(ctx, T, "#ffb3b3", "#c0303a", cy=600)
    st.server_grid(ctx, 55, 250, 20, T, cols=4, k_rows=[T - 25.65 - i * 0.025 for i in range(20)], w=140, h=120)
    label(ctx, "+20 MORE", 330, 940, 64, bg=st.RED, scale=pop(T - 25.89) if T >= 25.89 else 0.0)


def s_cantplay(ctx, t, d):
    T = 26.63 + t
    tops = st.obby(ctx, T, y_lava=1060, y_top=930, x0=-80, dx=230, rise=-30, nums=False)
    for i, (px, py) in enumerate(tops[1:4]):
        P[i].draw(ctx, px, py, 0.8, "angry", T, arms=("hip", "hip"))
    for i in range(3):
        st.invite_card(ctx, 360 + (i - 1) * 40, 300 + i * 150, 0.7, "Milo", "Birthday Party!", T - (26.7 + i * 0.25))
    label(ctx, "CAN'T PLAY", 360, 960, 60, bg=st.RED, scale=pop(T - 27.44) if T >= 27.44 else 0.0)


def s_spam(ctx, t, d):
    T = 27.78 + t
    st.gamer_desk(ctx, T, y_desk=900)
    milo(ctx, 360, 1060, 1.3, "crazy", T, arms=("hold", "hold"), tag=False)
    st.keyboard(ctx, 360, 950, 1.0, T, mash=1.0)
    st.sfx_word(ctx, 160, 420, "CLICK!", T - 28.06, col=st.BLUE, size=44)
    st.sfx_word(ctx, 540, 360, "CLICK!", T - 28.4, col=st.BLUE, size=44, tilt=0.15)


def s_flood(ctx, t, d):
    T = 29.01 + t
    st.burst(ctx, T, "#ffd6ef", "#ff5fb0", cy=600)
    for i in range(9):
        k = T - (29.03 + i * 0.1)
        st.invite_card(ctx, 330 + ((i * 53) % 90 - 45), 260 + i * 80, 0.62, "Milo", "Party! JOIN NOW",  k)
    st.friends_count(ctx, 340, 960, int(1 + 999 * ease(clamp((T - 29.1) / 0.8))), label="Invites", col=st.PINK)


# ================================================================ the moderator
def s_mod(ctx, t, d):
    T = 30.1 + t
    world(ctx, T, 1000)
    MOD.draw(ctx, 360, 1000, 1.2, keyed(T, [(0, "neutral"), (30.97, "shock")]), T, arms=("down", "hold"))
    st.staff_badge(ctx, 360, 1000 - 1.55 * U1 * 1.2, 0.9, txt="MOD")
    st.name_pill(ctx, 360, 1000 - 3.45 * U1 * 1.2, "[MOD] Officer_Kai", size=28, col=st.RED)
    st.invite_card(ctx, 360, 380, 0.75, "Milo", "Milo's Birthday Party!", T - 30.97)


def s_mod_please(ctx, t, d):
    T = 31.49 + t
    st.burst(ctx, T, "#c4c8e8", "#4a4f8a", cy=560)
    closeup(ctx, MOD, keyed(T, [(0, "worried"), (31.78, "cry")]), T, arms=("up", "up"), talk=talking("mod", T),
            snap=snap_at(T, 31.78))
    style.sweat(ctx, 560, 470, 1.0, T)
    st.speech_bubble(ctx, 360, 290, "PLEASE STOP!", 54, T - 31.78, tail=(0, 1))


def s_bracelet(ctx, t, d):
    T = 32.82 + t
    st.burst(ctx, T, "#ffd6ef", "#ff5fb0", cy=600)
    st.game_toast(ctx, 360, 230, "Milo", "sent you a gift", T - 32.99, icon_col=st.PINK)
    if T < 33.68:                                          # the gift box shakes, then pops open
        ctx.save()
        ctx.translate(360, 640)
        ctx.rotate(math.sin(T * 30) * 0.08)
        style.block(ctx, -130, -100, 260, 200, 16, hexc("#ff5fb0"), 6)
        style.block(ctx, -150, -140, 300, 60, 14, hexc("#ff8ac8"), 6)
        style.block(ctx, -20, -140, 40, 240, 6, st.YELLOW, 4, gloss=False)
        ctx.restore()
    else:
        k = T - 33.68
        st.bracelet(ctx, 360, 620, 1.6 * (pop(k) if k < 0.6 else 1.0), T)
        st.hearts(ctx, T, 33.7, 360, 640, n=7)
    st.sfx_word(ctx, 460, 860, "AWW!", T - 34.13, col=st.PINK, size=50)


# ================================================================ the developers
def s_beg(ctx, t, d):
    T = 34.63 + t
    world(ctx, T, 1000)
    for i, x in enumerate((130, 250, 470, 580)):
        P[i + 8].draw(ctx, x, 1000, 0.85, "cry" if i % 2 else "worried", T, arms=("up", "up"),
                      pose="sit" if i % 2 else "stand")
    label(ctx, "PLEASE!", 360, 300, 84, fg=st.YELLOW, scale=pop(T - 35.33) if T >= 35.33 else 0.0)


def s_chat(ctx, t, d):
    T = 35.71 + t
    st.burst(ctx, T, "#c4d8ff", "#2f3f9a", cy=600)
    lines = [("BloxKid", "devs pls stop milo", "#ff5fb0"), ("ObbyQueen", "100 invites today", "#4fd16a"),
             ("SpeedyTom", "HE SENT ME 9 BRACELETS", "#ffd84a"), ("Builder_Bob", "DEVS HELP", "#6fc3ff")]
    n = min(4, int((T - 35.75) / 0.22) + 1)
    st.chat_box(ctx, 60, 330, 600, 330, lines[:n], T, size=30, title="Chat")
    label(ctx, "DEVS?!", 360, 250, 70, fg=st.RED, scale=pop(T - 35.71))


def desk_front(ctx, y_desk):
    style.block(ctx, -100, y_desk, 920, 50, 8, hexc("#b9b4d8"), 5)
    style.block(ctx, -100, y_desk + 50, 920, 700, 0, hexc("#7a6aa8"), 5, gloss=False)


def s_dev(ctx, t, d):
    T = 36.93 + t
    st.office(ctx, T, night=1.0, y_desk=900)
    DEV.draw(ctx, 230, 1070, 1.4, keyed(T, [(0, "tired"), (37.8, "determined")]), T, arms=("hold", "hold"), lean=0.05,
             bob=0.4)
    desk_front(ctx, 900)
    st.monitor(ctx, 500, 905, 0.42, T, lambda c, x, y, w, h, TT: st.code_screen(c, x, y, w, h, TT, typed=0.6))
    for i in range(4):
        st.coffee_cup(ctx, 70 + i * 56, 905, 0.85, steam_T=T if i == 3 else None)
    label(ctx, "FINALLY", 360, 320, 70, bg=st.UI_DARK, fg=st.YELLOW, scale=pop(T - 37.8) if T >= 37.8 else 0.0)


def s_code(ctx, t, d):
    T = 38.65 + t

    def screen(c, x, y, w, h, TT):
        st.code_screen(c, x, y, w, h, TT, typed=clamp((TT - 38.65) / 0.6))
        if TT >= 39.0:
            st.bold_text(c, "MAX_FRIENDS = 1000", x + w / 2, y + h * 0.82, 30, st.GREEN, shadow=False, stroke=0.0,
                         scale=pop(TT - 39.0))
    st.night_wall(ctx, 2000)
    st.monitor(ctx, 360, 860, 1.12, T, screen)
    st.keyboard(ctx, 360, 1000, 1.0, T, mash=1.0)
    label(ctx, "NEW RULE", 360, 250, 74, fg=st.GREEN, scale=pop(T - 39.18) if T >= 39.18 else 0.0)


def s_limit_reveal(ctx, t, d):
    T = 39.6 + t
    st.burst(ctx, T, "#ffb3b3", "#c0303a", cy=560, spin=0.3)
    st.roblox_dialog(ctx, 360, 600, 1.05, T - 39.62, "Friend Limit Reached",
                     "You have reached the maximum number of friends.")


# ================================================================ nothing happened
def s_try(ctx, t, d):
    T = 40.71 + t
    lobby(ctx, T)
    milo(ctx, 190, 1000, 1.0, "grin", T, arms=("point", "down"), look=0.6)
    P[3].draw(ctx, 520, 1000, 1.0, "neutral", T, look=-0.6)
    st.name_pill(ctx, 520, 1000 - 3.45 * U1, NAMES[10], size=24)
    block_y = 470
    style.block(ctx, 380, block_y - 40, 260, 80, 16, hexc("#00b06f"), 4)
    st.bold_text(ctx, "Add Friend", 510, block_y, 32, (1, 1, 1), shadow=False, stroke=0.0)
    if 41.3 < T < 42.2:
        kk = ease(clamp((T - 41.3) / 0.3))
        st.cursor(ctx, lerp(300, 470, kk), lerp(700, block_y + 10, kk), 1.8, click=1.0 if T > 41.66 else 0.0)
    st.tap_ripple(ctx, 500, block_y, (T - 41.66) / 0.4)


def s_nothing(ctx, t, d):
    T = 42.39 + t
    st.burst(ctx, T, "#d8dbe6", "#5a5f7a", cy=560, spin=0.05)
    closeup(ctx, MILO, keyed(T, [(0, "neutral"), (42.78, "worried")]), T, arms=("down", "point"), snap=snap_at(T, 42.78))
    style.block(ctx, 70, 200, 260, 80, 16, hexc("#5a5d6a"), 4, gloss=False)
    st.bold_text(ctx, "Add Friend", 200, 240, 32, hexc("#a0a3b0"), shadow=False, stroke=0.0)
    st.red_x(ctx, 200, 240, 50, (T - 42.78) / 0.25)
    st.speech_bubble(ctx, 560, 290, "...", 60, T - 42.5, tail=(-1, 1))


def s_alone(ctx, t, d):
    T = 43.34 + t
    st.void_bg(ctx, top="#6a7090", bottom="#2a2f45", y0=400, y1=1300)
    st.baseplate(ctx, 1000, "#5f8a5a")
    milo(ctx, 360, 1000, 1.1, "sad", T, pose="sit", arms=("down", "down"), tag=False)
    for i in range(12):                                  # rain
        x = (i * 67 + T * 40) % 720
        y = (i * 113 + T * 900) % 1000
        ctx.move_to(x, y)
        ctx.line_to(x - 8, y + 40)
    ctx.set_source_rgba(0.7, 0.8, 1.0, 0.5)
    ctx.set_line_width(4)
    ctx.stroke()
    label(ctx, "FIRST TIME", 360, 340, 66, fg=(1, 1, 1), scale=pop(T - 43.51) if T >= 43.51 else 0.0)


def s_cry(ctx, t, d):
    T = 44.35 + t
    st.void_bg(ctx, top="#6a7090", bottom="#2a2f45", y0=200, y1=1300)
    closeup(ctx, MILO, "cry", T, arms=("down", "down"))
    st.friends_count(ctx, 360, 290, 1000, s=1.1, col=st.RED)


def s_celebrate(ctx, t, d):
    T = 45.59 + t
    world(ctx, T, 920)
    st.confetti(ctx, T, 45.6, n=50)
    for i in range(6):
        x = 105 + i * 100
        hop = abs(math.sin(T * 7 + i)) * 40
        P[i].draw(ctx, x, 980 - hop - (i % 2) * 40, 0.75, "laugh" if i % 2 else "stars", T, arms=("up", "up"),
                  pose="jump")
    MOD.draw(ctx, 360, 1000 - abs(math.sin(T * 7)) * 30, 0.95, "laugh", T, arms=("up", "up"), pose="jump")
    label(ctx, "FREEDOM!", 360, 260, 84, fg=st.YELLOW, scale=pop(T - 46.19) if T >= 46.19 else 0.0)


# ================================================================ the plan
def s_crazy(ctx, t, d):
    T = 47.3 + t
    st.burst(ctx, T, "#e2c8ff", "#7a3fd8", cy=560, spin=0.5)
    closeup(ctx, P[3], keyed(T, [(0, "neutral"), (47.81, "shock")]), T, arms=("up", "up"), snap=snap_at(T, 47.81))
    label(ctx, "CRAZY PART", 360, 240, 70, fg=st.YELLOW, scale=pop(T - 47.81) if T >= 47.81 else 0.0)


def s_notupset(ctx, t, d):
    T = 48.56 + t
    st.burst(ctx, T, "#b8ffb0", "#2e9c46", cy=560)
    closeup(ctx, MILO, keyed(T, [(0, "sad"), (48.95, "smirk")]), T, arms=("down", "down"), snap=snap_at(T, 48.95))


def s_plan(ctx, t, d):
    T = 49.74 + t
    st.night_wall(ctx, 2000)
    st.dark_glow_bg(ctx, T, glow_col="#ffcc33", base="#1b1426")
    milo(ctx, 360, 1000, 1.25, "smug", T, arms=("hold", "hold"), tag=False)
    st.lightbulb(ctx, 540, 340, 0.8, T - 49.85, T)
    label(ctx, "A PLAN", 300, 260, 76, fg=st.YELLOW, scale=pop(T - 50.01) if T >= 50.01 else 0.0)


def s_newacc(ctx, t, d):
    T = 50.49 + t
    typed = "Milo_2"[:max(0, int((T - 50.7) / 0.1))]
    st.night_wall(ctx, 2000)
    st.monitor(ctx, 360, 900, 1.08, T, lambda c, x, y, w, h, TT: st.login_screen(c, x, y, w, h, TT, typed=typed,
                                                                                    title="CREATE ACCOUNT", lock=False))
    label(ctx, "NEW ACCOUNT", 360, 250, 64, bg=st.BLUE, scale=pop(T - 50.95) if T >= 50.95 else 0.0)


def s_spawn2(ctx, t, d):
    T = 51.47 + t
    world(ctx, T, 980)
    st.spawn_pad(ctx, 360, 1000, 1.4, beam=clamp(1 - (T - 51.5) / 0.6))
    if T >= 51.55:
        ctx.save()
        ctx.translate(360, 1000)
        ctx.scale(1, pop(T - 51.55))
        ctx.translate(-360, -1000)
        milo(ctx, 360, 1000, 1.1, "grin", T, ch=MILO2, name="Milo_2", arms=("wave", "down"))
        ctx.restore()
    st.game_toast(ctx, 360, 230, "Milo_2", "joined the game", T - 51.6, icon_col=st.GREEN)


def s_request(ctx, t, d):
    T = 52.33 + t
    st.burst(ctx, T, "#c4d8ff", "#2f6bd8", cy=600)
    st.friend_card(ctx, 360, 600, 1.0, "Milo_2", k=T - 52.35, state="pending", title="First Friend Request")
    st.speech_bubble(ctx, 560, 360, "?", 70, T - 53.4, tail=(-1, 1))


def s_two(ctx, t, d):
    T = 54.02 + t
    lobby(ctx, T)
    milo(ctx, 190, 1000, 1.0, keyed(T, [(0, "neutral"), (54.73, "shock")]), T, arms=("down", "down"), look=0.6)
    milo(ctx, 520, 1000, 1.0, "grin", T, ch=MILO2, name="Milo_2", arms=("point", "down"), look=-0.6)
    st.arrow(ctx, 470, 560, 260, 620, k=ease(clamp((T - 54.3) / 0.2)))
    st.friend_card(ctx, 360, 380, 0.6, "Milo", k=T - 54.73, state="sent", title="Friend Request")


def s_rejected(ctx, t, d):
    T = 55.64 + t
    st.burst(ctx, T, "#ffb3b3", "#c0303a", cy=600)
    st.friend_card(ctx, 360, 600, 1.0, "Milo", k=1.0, state="declined" if T >= 56.29 else "sent",
                   title="Friend Request")
    st.sfx_word(ctx, 530, 400, "NOPE!", T - 56.4, col=st.RED, size=50)


def s_himself(ctx, t, d):
    T = 57.0 + t
    lobby(ctx, T)
    milo(ctx, 200, 1000, 1.0, "sad", T, arms=("shrug", "shrug"), look=0.6)
    milo(ctx, 510, 1000, 1.0, "sad", T, ch=MILO2, name="Milo_2", arms=("shrug", "shrug"), look=-0.6)
    st.red_x(ctx, 355, 560, 90, (T - 57.56) / 0.25)


def s_final(ctx, t, d):
    T = 58.35 + t
    st.burst(ctx, T, "#ffe27a", "#ff8a3d", cy=560)
    closeup(ctx, MILO, keyed(T, [(0, "worried"), (58.78, "crazy")]), T, arms=("shrug", "shrug"), snap=snap_at(T, 58.78))
    st.speech_bubble(ctx, 560, 320, "?!", 70, T - 58.8, tail=(-1, 1))


# ================================================================ shots
S = []


def shot(start, draw, keys, **kw):
    kw.setdefault("vignette", 0.15)
    S.append(dict(start=start, draw=draw, keys=keys, **kw))


def punch(t0, z0, c0, t_key, z1, c1, m=0.14):
    return [(t0, z0, c0), (t_key, z1, c1, m)]


C = (360, 700)
CU = dict(closeup=True, keep=FACE_KEEP)
G = (360, 760)

shot(0.00, s_hook, [(0.0, 1.12, (360, 640)), (0.3, 1.0, (360, 680), 0.12)], shake=(0.3, 10), closeup=True,
     keep=[(110, 180, 610, 760), (180, 920, 480, 1000)])
shot(0.89, s_teaser(lambda c, t, d: s_server20(c, t + 0.6, d), 0.0), punch(0.89, 1.0, (360, 640), 0.92, 1.05, (360, 640), 0.1),
     shake=(0.0, 8), closeup=True, keep=[(55, 250, 640, 900)])
shot(1.30, s_teaser(lambda c, t, d: s_bracelet(c, t + 1.0, d), 0.0), punch(1.30, 1.0, (360, 640), 1.33, 1.05, (360, 640), 0.1),
     shake=(0.0, 8), closeup=True, keep=[(160, 480, 560, 760)])
shot(1.73, s_limit, punch(1.73, 1.0, G, 1.91, 1.06, (360, 700), 0.12), shake=(0.18, 10), keep=[(80, 300, 640, 640)])
shot(2.70, s_named, punch(2.70, 1.0, C, 3.19, 1.08, (360, 660), 0.12), **CU)
shot(3.76, s_rule, punch(3.76, 1.0, G, 4.09, 1.06, (360, 740), 0.12))
shot(4.86, s_stranger, punch(4.86, 1.0, G, 5.99, 1.08, (380, 740), 0.12), shake=(1.13, 8))
shot(6.62, s_obby_add, punch(6.62, 1.0, G, 7.24, 1.06, (360, 740), 0.12), top=250, keep=[(60, 160, 660, 330)])
shot(7.53, s_count, punch(7.53, 1.0, (360, 640), 7.85, 1.04, (360, 640), 0.12), keep=[(90, 240, 630, 900)])
shot(8.68, s_bully, punch(8.68, 1.0, C, 9.25, 1.1, (360, 660), 0.12), whip=1, **CU)
shot(9.56, s_push, punch(9.56, 1.0, G, 9.7, 1.08, (380, 760), 0.12), shake=(0.14, 10))
shot(10.63, s_bestfriend, punch(10.63, 1.0, C, 10.97, 1.06, (360, 680), 0.12), closeup=True,
     keep=[(140, 210, 580, 430), (200, 560, 420, 800)])
shot(11.49, s_race, punch(11.49, 1.0, (360, 700), 12.18, 1.06, (360, 700), 0.12), whip=1)
shot(12.89, s_drivers, punch(12.89, 1.0, (360, 700), 13.38, 1.04, (360, 700), 0.12), keep=[(190, 320, 530, 780)])
shot(14.23, s_passed, punch(14.23, 1.0, G, 14.86, 1.08, (360, 780), 0.1), shake=(0.63, 8))
shot(15.57, s_yell, punch(15.57, 1.0, C, 15.97, 1.12, (360, 640), 0.12), shake=(0.4, 20), closeup=True,
     keep=[(110, 220, 610, 760)])
shot(16.95, s_lunch, punch(16.95, 1.0, (360, 700), 17.16, 1.05, (360, 700), 0.12), keep=[(190, 350, 530, 690)])
shot(18.12, s_friendlist, punch(18.12, 1.0, (360, 640), 18.56, 1.05, (360, 640), 0.12), keep=[(130, 230, 600, 820)])
shot(19.03, s_names, punch(19.03, 1.0, (360, 700), 19.79, 1.08, (360, 680), 0.12), keep=[(80, 470, 640, 840)])
shot(20.38, s_notfinished, punch(20.38, 1.0, C, 21.24, 1.1, (380, 640), 0.12), **CU)
shot(21.74, s_invite, punch(21.74, 1.0, (360, 700), 22.25, 1.04, (360, 700), 0.12), keep=[(120, 270, 640, 800)])
shot(22.91, s_cake, punch(22.91, 1.0, G, 23.29, 1.06, (360, 740), 0.12))
shot(23.69, s_server1, punch(23.69, 1.0, (360, 640), 24.32, 1.06, (360, 620), 0.12), shake=(0.63, 8),
     keep=[(130, 270, 590, 710)])
shot(24.98, s_server2, punch(24.98, 1.0, (360, 640), 25.14, 1.05, (360, 640), 0.12), shake=(0.16, 8),
     keep=[(60, 410, 650, 690)])
shot(25.63, s_server20, punch(25.63, 1.0, (360, 640), 25.89, 1.04, (360, 640), 0.12), keep=[(50, 245, 665, 900)])
shot(26.63, s_cantplay, punch(26.63, 1.0, G, 27.44, 1.05, (360, 740), 0.12), keep=[(110, 200, 610, 700)])
shot(27.78, s_spam, punch(27.78, 1.0, (360, 760), 28.25, 1.08, (360, 740), 0.12), shake=(0.28, 6))
shot(29.01, s_flood, punch(29.01, 1.0, (360, 640), 29.33, 1.04, (360, 640), 0.12), keep=[(80, 200, 620, 1000)])
shot(30.10, s_mod, punch(30.10, 1.0, G, 30.97, 1.06, (360, 720), 0.12), whip=-1, keep=[(110, 280, 610, 480)])
shot(31.49, s_mod_please, punch(31.49, 1.0, C, 31.78, 1.1, (360, 660), 0.12), shake=(0.29, 12), closeup=True,
     keep=[(110, 220, 610, 760)])
shot(32.82, s_bracelet, punch(32.82, 1.0, (360, 640), 33.68, 1.06, (360, 640), 0.12), keep=[(160, 180, 600, 870)])
shot(34.63, s_beg, punch(34.63, 1.0, G, 35.33, 1.06, (360, 740), 0.12))
shot(35.71, s_chat, punch(35.71, 1.0, (360, 640), 36.25, 1.04, (360, 640), 0.12), keep=[(60, 200, 660, 660)])
shot(36.93, s_dev, [(36.93, 1.0, (360, 760)), (38.6, 1.06, (320, 760), 1.3)], whip=1)
shot(38.65, s_code, punch(38.65, 1.0, (360, 700), 39.18, 1.08, (360, 680), 0.12), keep=[(80, 470, 640, 840)])
shot(39.60, s_limit_reveal, punch(39.60, 1.0, (360, 640), 39.62, 1.08, (360, 640), 0.1), shake=(0.02, 12),
     keep=[(80, 430, 640, 770)])
shot(40.71, s_try, punch(40.71, 1.0, G, 41.66, 1.06, (400, 720), 0.12), keep=[(370, 420, 650, 520)])
shot(42.39, s_nothing, punch(42.39, 1.0, C, 42.78, 1.06, (360, 680), 0.14), closeup=True,
     keep=[(165, 300, 555, 760), (60, 190, 340, 290)])
shot(43.34, s_alone, [(43.34, 1.0, G), (44.35, 1.1, (360, 800), 1.0)])
shot(44.35, s_cry, [(44.35, 1.0, C), (45.59, 1.08, (360, 640), 1.2)], closeup=True,
     keep=[(165, 240, 555, 760)])
shot(45.59, s_celebrate, punch(45.59, 1.0, G, 46.19, 1.06, (360, 760), 0.12))
shot(47.30, s_crazy, punch(47.30, 1.0, C, 47.81, 1.1, (360, 650), 0.1), shake=(0.51, 10), **CU)
shot(48.56, s_notupset, punch(48.56, 1.0, C, 48.95, 1.08, (360, 660), 0.12), **CU)
shot(49.74, s_plan, punch(49.74, 1.0, G, 50.01, 1.06, (360, 740), 0.12), keep=[(420, 230, 660, 450)])
shot(50.49, s_newacc, punch(50.49, 1.0, (360, 700), 50.95, 1.06, (360, 680), 0.12), keep=[(80, 470, 640, 840)])
shot(51.47, s_spawn2, punch(51.47, 1.0, G, 51.95, 1.06, (360, 760), 0.12), keep=[(110, 200, 610, 260)])
shot(52.33, s_request, punch(52.33, 1.0, (360, 640), 53.23, 1.06, (360, 620), 0.12), keep=[(110, 300, 640, 720)])
shot(54.02, s_two, punch(54.02, 1.0, G, 54.73, 1.05, (360, 740), 0.12), keep=[(200, 300, 520, 460)])
shot(55.64, s_rejected, punch(55.64, 1.0, (360, 640), 56.29, 1.08, (360, 620), 0.1), shake=(0.65, 12),
     keep=[(110, 470, 610, 730)])
shot(57.00, s_himself, punch(57.00, 1.0, G, 57.56, 1.05, (360, 740), 0.12), whip=-1)
shot(58.35, s_final, punch(58.35, 1.0, C, 58.78, 1.1, (360, 650), 0.1), shake=(0.43, 10), **CU)
SHOTS = S
_rw_draw, _rw_ov = st.rewind_shot(SHOTS, [56.5, 46.2, 34.2, 26.3, 9.9, 0.0])
shot(59.30, _rw_draw, [(59.30, 1.0, (360, 640))], overlay=_rw_ov, blur=False, closeup=True, keep=[])
for k, s in enumerate(SHOTS):
    s["end"] = SHOTS[k + 1]["start"] if k + 1 < len(SHOTS) else TOTAL

# ---------------------------------------------------------------- SFX (time, file, volume before SFX_GAIN)
SFX = [
    (0.03, "pop.wav", 0.8), (0.3, "hit.wav", 1.1), (0.36, "ding.wav", 0.6), (0.54, "pop.wav", 0.6),
    (0.89, "pop.wav", 0.7), (1.30, "sparkle.wav", 0.6), (1.91, "boom.wav", 1.5), (2.45, "tick.wav", 0.6),
    (3.19, "ding.wav", 0.8), (3.8, "swish.wav", 0.5), (4.09, "pop.wav", 0.8), (4.43, "tick.wav", 0.6),
    (5.0, "step.wav", 0.5), (5.4, "step.wav", 0.5), (5.99, "pop.wav", 0.9), (6.1, "sparkle.wav", 0.6),
    (7.04, "click.wav", 0.7), (7.24, "pop.wav", 0.8), (7.4, "click.wav", 0.7), (7.6, "ding.wav", 0.7),
    (7.85, "pop.wav", 0.6), (8.1, "pop.wav", 0.6), (8.68, "swish.wav", 0.6), (9.25, "tick.wav", 0.6),
    (9.7, "hit.wav", 1.2), (10.11, "boom.wav", 1.3), (10.97, "ding.wav", 0.8), (11.1, "sparkle.wav", 0.5),
    (11.49, "swish.wav", 0.6), (12.18, "pop.wav", 0.8), (13.06, "click.wav", 0.7), (13.38, "click.wav", 0.7),
    (13.7, "click.wav", 0.7), (14.86, "whoosh.wav", 0.7), (14.9, "hit.wav", 1.0), (15.97, "pop.wav", 0.8),
    (16.46, "hit.wav", 1.0), (17.16, "bell.wav", 0.7), (17.6, "tick.wav", 0.5), (18.2, "tick.wav", 0.5),
    (18.56, "chaching.wav", 0.7), (19.1, "type_key.wav", 0.5), (19.79, "pop.wav", 0.8), (20.4, "tick.wav", 0.5),
    (21.24, "sparkle.wav", 0.8), (21.84, "pop.wav", 0.7), (22.04, "pop.wav", 0.6), (22.25, "pop.wav", 0.7),
    (22.44, "pop.wav", 0.6), (22.95, "success.wav", 0.8), (23.29, "pop.wav", 0.8), (24.32, "hit.wav", 1.1),
    (25.14, "hit.wav", 1.0), (25.65, "tick.wav", 0.6), (25.9, "boom.wav", 1.3), (26.7, "pop.wav", 0.6),
    (26.95, "pop.wav", 0.6), (27.2, "pop.wav", 0.6), (27.44, "buzz.wav", 0.9), (28.06, "type_key.wav", 0.7),
    (28.4, "type_key.wav", 0.7), (28.7, "type_key.wav", 0.6), (29.03, "pop.wav", 0.6), (29.23, "pop.wav", 0.6),
    (29.43, "pop.wav", 0.6), (29.63, "pop.wav", 0.6), (30.1, "swish.wav", 0.6), (30.97, "ding.wav", 0.8),
    (31.78, "hit.wav", 1.1), (32.99, "pop.wav", 0.7), (33.2, "tick.wav", 0.5), (33.68, "sparkle.wav", 0.9), (34.13, "pop.wav", 0.8),
    (34.7, "tick.wav", 0.5), (35.33, "pop.wav", 0.8), (35.75, "type_key.wav", 0.6), (35.97, "type_key.wav", 0.6),
    (36.2, "type_key.wav", 0.6), (36.93, "swish.wav", 0.6), (37.4, "tick.wav", 0.5), (37.8, "pop.wav", 0.7),
    (38.7, "type_key.wav", 0.6), (39.0, "ding.wav", 0.8), (39.18, "pop.wav", 0.7), (39.62, "boom.wav", 1.5),
    (41.66, "click.wav", 0.9), (42.0, "tick.wav", 0.4), (42.78, "buzz.wav", 0.8), (43.5, "pop.wav", 0.5),
    (44.4, "tick.wav", 0.4), (45.6, "success.wav", 0.9), (46.19, "pop.wav", 0.8), (46.6, "pop.wav", 0.5),
    (47.81, "hit.wav", 1.2), (48.95, "sparkle.wav", 0.7), (49.85, "ding.wav", 0.8), (50.01, "pop.wav", 0.6),
    (50.75, "type_key.wav", 0.6), (50.95, "pop.wav", 0.7), (51.1, "type_key.wav", 0.6), (51.55, "sparkle.wav", 0.8),
    (51.6, "pop.wav", 0.6), (52.5, "pop.wav", 0.7), (53.4, "tick.wav", 0.6), (54.3, "swish.wav", 0.5),
    (54.73, "pop.wav", 0.7), (56.29, "hit.wav", 1.2), (56.4, "buzz.wav", 0.8), (57.0, "swish.wav", 0.5),
    (57.56, "pop.wav", 0.7), (58.78, "hit.wav", 1.0), (59.3, "whip.wav", 0.9),
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

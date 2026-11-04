"""Side-by-side test of the reference set 3 motion (engine.profile("set3"), 60 fps).

Five moments copied in TIMING and MOTION (not in drawing) from the two set-3 references, to compare frame by frame:
  A 0.00-1.30  DAY 1 card writes on over the kitchen            (never_stop 9.18-9.7)
  B 1.30-2.50  shock reaction: snap + burst + bump on "WHAT?!"   (bff_quit 5.95-6.45)
  C 2.50-3.40  mom -> whip pan -> kid                            (never_stop 6.2-6.5)
  D 3.40-4.80  SPLAT! sticker on an action + game toast + HUD   (never_stop 12.38-12.6, bff_quit 1.5)
  E 4.80-6.20  SYSTEM MESSAGE dialog types on                   (never_stop 40.7-42.2)
Run (from animator/): python3 set3_test.py ../output/set3_test/test.mp4"""
import math
import sys

import engine
import sets as st
import style
from engine import clamp, keyed, pop, render
from sets import label

engine.profile("set3")
engine.ENERGY = 3.0
engine.LIPSYNC = False
TOTAL = 6.2
KID, MOM = style.KID, style.MOM_ROBE
U1 = style.Block.HW * 64


def closeup(ctx, ch, expr, T, x=360, s=4.2, arms=("down", "down"), snap=None, bob=0.35, dy=0):
    ch.draw(ctx, x, 560 + 2.5 * U1 * s + dy, s, expr, T, arms=arms, bob=bob, snap=snap)


def s_day(ctx, t, d):
    T = t
    st.kitchen(ctx, T, night=False)
    MOM.draw(ctx, 200, 1150, 1.3, "smirk", T, arms=("down", "hold"))
    KID.draw(ctx, 520, 1150, 1.3, "grin", T, arms=("hold", "hold"))
    st.tablet(ctx, 520, 960, 0.5, T)
    st.day_write(ctx, "DAY", 1, 330, 330, T - 0.12, size=120)


def s_what(ctx, t, d):
    T = 1.3 + t
    hit = 1.82
    if T < hit:
        st.street(ctx, T)
    else:
        st.burst(ctx, T, "#ffd27a", "#ff7a1a", cy=560, spin=0.3)
    closeup(ctx, KID, "happy" if T < hit else "scream", T, arms=("show", "show"),
            snap=(T - hit) if T >= hit else None)
    if T >= hit:
        style.sweat(ctx, 560, 420, 1.0, T)
        label(ctx, "WHAT?!", 360, 260, 92, fg=st.YELLOW, scale=pop(T - hit))


def s_mom(ctx, t, d):
    T = 2.5 + t
    st.night_bedroom(ctx, T, door_x=360, stand_x=640)
    MOM.draw(ctx, 400, 1060, 1.4, "angry", T, arms=("point", "hip"), talk=True)


def s_kid(ctx, t, d):
    T = 2.92 + t
    st.night_bedroom(ctx, T)
    KID.draw(ctx, 360, 1100, 1.5, "smug", T, arms=("hold", "hold"))
    st.tablet(ctx, 360, 900, 0.55, T)


def s_splat(ctx, t, d):
    T = 3.4 + t
    st.kitchen(ctx, T, night=False)
    closeup(ctx, KID, keyed(T, [(0, "grin"), (3.9, "crazy")]), T, arms=("hold", "hold"),
            snap=(T - 3.9) if T >= 3.9 else None)
    st.name_pill(ctx, 360, 290, "BloxKid", size=28)
    st.sfx_word(ctx, 200, 420, "SPLAT!", T - 3.9, col="#ff4f5a", size=52, tilt=-0.2)


def ov_splat(ctx, t, d):
    T = 3.4 + t
    st.game_hud(ctx, T, streak=72 + int(clamp((T - 3.9) / 0.3) * 8), coins=1268, y=190)
    st.game_toast(ctx, 360, 260, "MaxPro99", "left the game", T - 4.2)


def s_system(ctx, t, d):
    T = 4.8 + t
    st.night_bedroom(ctx, T)
    st.system_message(ctx, 360, 600, 1.0, ["Please...", "take a break."], T - 4.9, T=T,
                      typed=clamp((T - 5.1) / 0.9))


S = []


def shot(start, draw, keys, **kw):
    kw.setdefault("vignette", 0.15)
    S.append(dict(start=start, draw=draw, keys=keys, **kw))


C = (360, 700)
shot(0.0, s_day, [(0.0, 1.0, (360, 720)), (0.6, 1.04, (360, 700), 0.15)])
shot(1.3, s_what, [(1.3, 1.0, C), (1.82, 1.1, (360, 650), 0.13)], shake=(0.52, 26), closeup=True)
shot(2.5, s_mom, [(2.5, 1.0, (380, 760))])
shot(2.92, s_kid, [(2.92, 1.0, (360, 760)), (3.2, 1.06, (360, 740), 0.13)], whip=1)
shot(3.4, s_splat, [(3.4, 1.0, C), (3.9, 1.08, (360, 660), 0.12)], shake=(0.5, 6), overlay=ov_splat, closeup=True)
shot(4.8, s_system, [(4.8, 1.0, C), (5.1, 1.06, (360, 640), 0.13)])
for k, s in enumerate(S):
    s["end"] = S[k + 1]["start"] if k + 1 < len(S) else TOTAL

if __name__ == "__main__":
    render(S, TOTAL, sys.argv[1], xfade=0.0, grain=2, fade_out=0.0, fade_in=0.0)

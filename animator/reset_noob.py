"""Story: "This noob is the reason Roblox has a reset button" (Oliver, the noob who gets stuck everywhere).

Voice: output/reset_noob/voice.mp3 (75.4 s, the user's voice tool, ~98% speech) + subs.srt.
Word times from analysis/align_words.py; "Oliver pressed it. Boom! Back at spawn" was re-timed from the
loudness (pressed 57.0, Boom 57.53, Back 58.07, the whole server 58.92), where the aligner slipped.
Delivered WITHOUT captions (the user's request for this video).

Shot plan (time | words | row | what is shown):
  0.00 This noob is the | hook | Oliver stuck chest-deep in the floor, THIS NOOB + arrow, players laugh
  0.86 reason Roblox has | teaser | 0.3 s flashes: on sale in the machine, the crowd under the map
  1.56 a reset button | game thing | RESET button slams down, a cursor presses it on "button", Oliver poofs
  2.76 His name was Oliver | named | close-up, OLIVER pops on the name
  3.84 loved exploring | action | walking the baseplate, hearts
  4.97 every corner of Roblox | list | 2x2 worlds pop in, Oliver peeking from each corner
  6.43 The problem? | question | worried close-up
  7.09 get into anything | action | dives into a chest, only kicking legs, check mark
  8.31 never get out | disbelief | inside the dark chest, red X
  9.59 crawled inside a vending machine | action | legs sticking out of the flap
 11.45 for free chips | payoff | behind the glass hugging chips
 12.40 Help! I'm on sale! | dialogue (lip-sync) | face on the glass, price tag swings in on "sale"
 13.72 A player bought chips | action | coin into the slot
 14.78 and got Oliver instead | twist | Oliver drops out of the flap, the buyer shocked
 16.10 friends pulled him out | action | tug of war, POP
 17.13 one got stuck in his place | twist | the friend behind the glass with the price tag
 18.70 joined an obby | place | spawn beam on the obby
 19.97 jumped straight into | action | the jump arc
 21.16 a tiny gap between two platforms | literal | squeezed into the gap, arrow
 23.13 Guys! / 23.69 I found a secret room! | dialogue (lip-sync) | dark gap close-up, then the sign
 24.86 It wasn't a room | correction | the sign gets a red X
 25.79 it was the floor | reveal | cross-section, Oliver flat inside the floor
 26.68 waved at the camera | literal | REC frame, a tiny waving hand in the gap
 27.78 nobody could see him | reaction | players run past with "?"
 28.90 An admin teleported him | new character | admin close-up with a wand
 30.01 to safety | payoff | spawn beam, check
 30.73 promised to be careful | promise | halo close-up
 32.19 Five seconds later | SECONDS card | 5 SECONDS card
 33.16 drove a race car | action | race car, speed lines
 34.14 through a wall | impact | bricks fly
 34.96 fell underneath the entire map | reveal | map cross-section, falling into the void
 36.57 ropes / 37.98 a crane / 38.55 a giant rocket | list | one item per word
 39.69 The rocket exploded | impact | BOOM
 40.81 sending 20 more players under the map | number counter | players fall, +20
 42.91 Even the admin fell in | escalation | admin falling
 44.22 Now everyone was stuck | low beat | the crowd under the map (music dip)
 45.58 Admins couldn't teleport / 46.93 fast enough | struggle | sweating admin, then the request pile
 47.76 Players begged the developers | chat | chat box fills
 49.13 one way to escape / 50.22 without asking for help | rule | EXIT?, a HELP bubble crossed out
 51.36 That night, a tired developer | place | dev at the desk at night
 52.95 a brand new button | build | code types in, the button forms
 54.49 with two words | tease | dev smirk, 2 WORDS
 55.42 Reset character | reveal | the RESET CHARACTER button (music dip)
 56.51 Oliver pressed it / 57.50 Boom! | action | cursor click, Oliver breaks apart
 58.05 Back at spawn / 58.90 the whole server celebrated | payoff | spawn beam, then the party
 60.34 next morning / 61.60 thousands of resets / 63.15 the same player | twist | office, counter, log
 64.35 a new hobby / 66.14 testing every place / 66.90 he could get stuck | list | tree, checklist
 68.06 the crazy part | turn | dev shocked
 69.18 hired Oliver / 70.50 as a game tester | twist | HIRED stamp, TESTER badge
 71.43 His job? / 72.06 stuck on purpose | punchline | dives into a wall on purpose
 73.31 guess what? / 74.08 best employee | loop setup | employee of the month frame
 75.30 REWIND montage, lands on the first frame

Run (from animator/):
  python3 reset_noob.py ../output/reset_noob/clips/animation.mp4 ../output/reset_noob/cues.json"""
import math
import os
import sys

import engine
import sets as st
import style
from engine import PI, clamp, ease, hexc, keyed, lerp, pop, render
from sets import label
from style import Block

TOTAL = 76.2
engine.LIPSYNC = True
engine.DRIFT = (0.035, 9, -6)
engine.ENERGY = 3.0
SFX_GAIN = 0.28                      # this voice tool: 0.28 measured right on grandma_pro and sneeze
MUSIC = dict(dips=[(44.2, 45.6), (55.3, 56.5)])   # quieter under "Now everyone was stuck" and the button reveal
DIALOGUE = {"oliver": [(12.42, 13.61), (23.13, 24.77)]}
PRESS, BOOM, BACK = 57.3, 57.53, 58.07

OLIVER = Block("#1a68cf", pants="#9bbc36", skin="#e9c22c", hair=None, sleeves="skin", shoes=None, cap="#ff7a1a")
ADMIN = Block("#e8323a", pants="#2b2f45", skin="#f0c9a8", hair="smooth", hair_col="#f2c14e", outfit="hoodie",
              shades=True, shoes="dark")
DEV = Block("#3b3f5a", pants="#2b2f45", skin="#f0c9a8", hair="spiky", hair_col="#2a1a14", outfit="hoodie",
            glasses=True, headset="#4f8bff", shoes="dark")
P = [style.crowd_member(i) for i in range(14)]

U1 = Block.HW * 64
FACE_S = 4.2
FACE_KEEP = [(165, 300, 555, 760)]
VOID = "#140f30"


def talking(who, T):
    return any(a <= T <= b for a, b in DIALOGUE[who])


def closeup(ctx, ch, expr, T, x=360, look=0.0, arms=("down", "down"), s=FACE_S, talk=False, bob=0.35, dy=0):
    ch.draw(ctx, x, 560 + 2.5 * U1 * s + dy, s, expr, T, arms=arms, look=look, talk=talk, bob=bob)


def oliver(ctx, x, y, s, expr, T, tag=True, **kw):
    OLIVER.draw(ctx, x, y, s, expr, T, **kw)
    if tag:
        st.nametag(ctx, x, y - 3.45 * U1 * s, "Oliver", size=max(22, 26 * s))


def admin(ctx, x, y, s, expr, T, tag=True, **kw):
    ADMIN.draw(ctx, x, y, s, expr, T, **kw)
    if tag:
        st.nametag(ctx, x, y - 3.35 * U1 * s, "[ADMIN]", size=max(22, 26 * s), col=st.RED)


def legs_out(ctx, x, edge, s, T, ch=OLIVER, side="up", vis=1.2, kick=3.0):
    """Stuck head-first: only the kicking legs show past the edge. side 'up': legs above y=edge at x;
    'left': legs stick out left of x=edge at height x (x is then the y of the body axis)."""
    u = U1 * s
    ctx.save()
    if side == "up":
        ctx.rectangle(-3000, -5000, 7000, edge + 5000)
        ctx.clip()
        ctx.translate(x, edge)
        ctx.rotate(PI)
    else:
        ctx.rectangle(-3000, -5000, edge + 3000, 10000)
        ctx.clip()
        ctx.translate(edge, x)
        ctx.rotate(PI / 2)
    ch.draw(ctx, 0, vis * u, s, "scared", T, pose="run" if kick else "stand", walk_phase=T * kick,
            shadow=False, bob=0.3)
    ctx.restore()


def lying(ctx, ch, x, y, s, expr, T, head_right=True, squash=1.0, **kw):
    """A character lying flat, feet at (x, y)."""
    ctx.save()
    ctx.translate(x, y)
    ctx.rotate(PI / 2 if head_right else -PI / 2)
    ctx.scale(1.0, 1.0)
    ctx.scale(squash, 1.0)
    ch.draw(ctx, 0, 0, s, expr, T, shadow=False, bob=0.3, **kw)
    ctx.restore()


def world(ctx, T, y=1000):
    st.game_sky(ctx)
    st.block_clouds(ctx, T)
    st.baseplate(ctx, y)


def under_map(ctx, T, y_top=-120, thick=260, hole=None):
    """Under the map: the dark void, the slab's bottom at the top of the frame, a faint invisible floor."""
    st.void_bg(ctx, top="#3a3f8a", bottom=VOID, y0=300, y1=1300)
    st.sparkles(ctx, T, 360, 700, spread=420, n=14, seed=21, c=(0.7, 0.75, 1.0), size=10)
    st.map_slab(ctx, T, y_top=y_top, thick=thick, hole=hole, trees=False)


def invisible_floor(ctx, y):
    for i in range(-2, 14):
        ctx.move_to(i * 60, y)
        ctx.line_to(i * 60 - 40, y + 60)
    ctx.move_to(-100, y)
    ctx.line_to(820, y)
    ctx.set_source_rgba(0.6, 0.65, 1.0, 0.25)
    ctx.set_line_width(3)
    ctx.stroke()


def break_apart(ctx, x, y, s, k):
    """Oliver falls apart into his blocks (a game death), k = seconds since."""
    u = U1 * s
    parts = [("#e9c22c", 0.0, -2.05, 0.95, 0.9, -0.6, -3.2, 5), ("#ff7a1a", 0.0, -2.55, 0.9, 0.3, 0.8, -3.8, -4),
             ("#1a68cf", 0.0, -1.5, 1.1, 1.05, 0.1, -1.6, 2), ("#e9c22c", -0.75, -1.5, 0.42, 1.0, -2.6, -2.2, 7),
             ("#e9c22c", 0.75, -1.5, 0.42, 1.0, 2.6, -2.4, -7), ("#9bbc36", -0.28, -0.5, 0.52, 1.0, -1.4, -1.0, 4),
             ("#9bbc36", 0.28, -0.5, 0.52, 1.0, 1.5, -1.1, -4)]
    for col, px, py, w, h, vx, vy, spin in parts:
        cx = x + px * u + vx * 300 * k
        cy = y + py * u + vy * 300 * k + 900 * k * k
        ctx.save()
        ctx.translate(cx, cy)
        ctx.rotate(spin * k)
        style.block(ctx, -w * u / 2, -h * u / 2, w * u, h * u, 0.1 * u, hexc(col), 4)
        ctx.restore()


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


def sign(ctx, x, y, s, txt, tilt=-0.06):
    """Hand-made wooden sign on a stick."""
    ctx.save()
    ctx.translate(x, y)
    ctx.rotate(tilt)
    ctx.scale(s, s)
    style.block(ctx, -10, -40, 20, 220, 4, hexc("#8a5a3a"), 4, gloss=False)
    style.block(ctx, -170, -150, 340, 130, 10, hexc("#c99a5e"), 6)
    st.bold_text(ctx, txt, 0, -85, 46, (1, 1, 1), outline=hexc("#6a3f1a"), shadow=False, stroke=0.16)
    ctx.restore()


# ================================================================ hook
def s_hook(ctx, t, d, T0=0.0, frozen=False):
    """0.00-0.86 "This noob is the": Oliver stuck chest-deep in the floor, THIS NOOB + arrow, players laugh."""
    T = T0 + (0.0 if frozen else t)
    st.burst(ctx, T, "#ffe27a", "#ff7a1a", cy=560, spin=0.4)
    closeup(ctx, OLIVER, keyed(T, [(0, "scared"), (0.36, "crazy")]), T, arms=("up", "up"), dy=60)
    style.block(ctx, -100, 905, 920, 60, 10, hexc("#51c844"), 6)            # the floor he is stuck in
    style.block(ctx, -100, 960, 920, 500, 0, hexc("#9a6a3c"), 6, gloss=False)
    for i, (cx, cy) in enumerate(((210, 935), (300, 925), (440, 930), (520, 940))):   # cracks
        st.dust(ctx, cx, cy, ((T + i * 0.2) % 0.8) / 0.8, n=3, spread=40, r=14)
    for x, i, look in ((100, 2, 0.6), (540, 4, -0.6)):
        P[i].draw(ctx, x, 1000, 0.8, "laugh", T, arms=("point", "cover") if x < 360 else ("cover", "point"),
                  look=look)
    st.arrow(ctx, 620, 260, 520, 380, k=0.6 + ease(T / 0.15) * 0.4)
    label(ctx, "THIS NOOB", 330, 230, 76, fg=st.RED, scale=pop(T - 0.36) if T >= 0.36 else 0.0)


def s_teaser(fn, t_off):
    """A 0.3 s flash of a later scene at its peak moment (the 'reason' montage)."""
    def draw(ctx, t, d):
        fn(ctx, t + t_off, d)
        st.flash(ctx, 0.55 * math.exp(-25 * t))
    draw.__name__ = "teaser_" + fn.__name__
    return draw


def s_button(ctx, t, d):
    """1.56-2.76 "a reset button": the button slams down, a cursor presses it, Oliver poofs."""
    T = 1.56 + t
    world(ctx, T, 860)
    bx, base = 320, 900
    k = clamp((T - 1.56) / 0.1)
    by = lerp(base - 200, base, k * k)
    if T >= 1.66:
        st.shockwave(ctx, bx, base + 40, (T - 1.66) / 0.5, r_max=440)
        st.dust(ctx, bx, base + 40, (T - 1.66) / 0.4, n=6, spread=110)
    pressed = T > 2.41
    st.reset_button(ctx, bx, by, 0.85, T, pressed=1.0 if pressed else 0.0, glow_a=0.5)
    top = by - 102 + (26 if pressed else 0)
    if T < 2.43:
        oliver(ctx, bx + 150, top, 0.75, keyed(T, [(0, "shock"), (1.9, "grin")]), T, arms=("wave", "down"))
    else:
        st.poof(ctx, bx + 150, top - 110, 90, (T - 2.43) / 0.4)
        st.sparkles(ctx, T, bx + 150, top - 160, spread=120, n=8, seed=4, c=st.YELLOW)
    if 2.15 < T < 2.6:
        kk = ease((T - 2.15) / 0.26)
        st.cursor(ctx, lerp(60, 210, kk), lerp(520, 820, kk), 2.0, click=1.0 if pressed else 0.0)
    if T >= 1.66:
        st.flash(ctx, 0.6 * math.exp(-18 * (T - 1.66)))


# ================================================================ intro
def s_named(ctx, t, d):
    T = 2.76 + t
    st.burst(ctx, T, "#bfe3ff", "#2f6bd8", cy=560)
    closeup(ctx, OLIVER, keyed(T, [(0, "happy"), (3.29, "grin")]), T, arms=("down", "wave"))
    label(ctx, "OLIVER", 360, 250, 92, fg=st.YELLOW, scale=pop(T - 3.29) if T >= 3.29 else 0.0)


def s_explore(ctx, t, d):
    T = 3.84 + t
    world(ctx, T, 980)
    x = 180 + (T - 3.84) * 220
    oliver(ctx, x, 1130, 1.15, "happy", T, pose="walk", walk_phase=T * 1.8, arms=("point", "down"), look=0.6)
    st.hearts(ctx, T, 4.1, x, 760, n=5)
    label(ctx, "EXPLORER", 360, 270, 70, bg=st.GREEN, scale=pop(T - 4.47) if T >= 4.47 else 0.0)


def _w_lava(ctx, T):
    st.obby(ctx, T, y_lava=1000, y_top=860, x0=60, dx=220)


def _w_snow(ctx, T):
    st.game_sky(ctx, "#9fc4ff", "#e8f2ff")
    st.baseplate(ctx, 900, "#eef6ff")
    for x in (120, 520):
        ctx.move_to(x - 90, 900)
        ctx.line_to(x, 640)
        ctx.line_to(x + 90, 900)
        ctx.close_path()
        style.shape_fill(ctx, hexc("#2f8f5a"), 5, 640, 900)


def _w_city(ctx, T):
    st.street(ctx, T, y_ground=960)


def _w_space(ctx, T):
    st.void_bg(ctx, top="#1b1f4a", bottom="#0a0820", y0=200, y1=1200)
    st.sparkles(ctx, T, 360, 600, spread=420, n=20, seed=9, size=12)
    ctx.new_sub_path()
    ctx.arc(480, 560, 150, 0, 2 * PI)
    style.shape_fill(ctx, hexc("#9d5cff"), 6, 410, 710)
    style.block(ctx, -100, 900, 920, 400, 20, hexc("#8a90a8"), 6)


PANELS = [(55, 230, _w_lava, 4.99, (1, 1)), (325, 230, _w_snow, 5.33, (-1, 1)),
          (55, 620, _w_city, 5.6, (1, -1)), (325, 620, _w_space, 5.85, (-1, -1))]


def s_corners(ctx, t, d):
    T = 4.97 + t
    st.burst(ctx, T, "#ffe27a", "#ff8a3d", cy=640)
    pw, ph = 250, 370
    for x, y, fn, tk, (sx, sy) in PANELS:
        k = T - tk
        if k < 0:
            continue
        sc = pop(k)
        ctx.save()
        ctx.translate(x + pw / 2, y + ph / 2)
        ctx.scale(sc, sc)
        ctx.translate(-pw / 2, -ph / 2)
        style.block(ctx, -8, -8, pw + 16, ph + 16, 22, (1, 1, 1), 6, outline=style.INK, gloss=False)
        ctx.save()
        engine.rrect(ctx, 0, 0, pw, ph, 16)
        ctx.clip()
        ctx.scale(pw / 540, pw / 540)
        ctx.translate(-90, -(1120 - ph * 540 / pw))
        fn(ctx, T)
        ctx.restore()
        cx = pw * (0.12 if sx > 0 else 0.88)                 # Oliver peeks around the panel's corner
        cy = ph * (0.98 if sy > 0 else 0.98)
        ctx.save()
        engine.rrect(ctx, 0, 0, pw, ph, 16)
        ctx.clip()
        oliver(ctx, cx, cy + 60, 1.0, keyed(T, [(0, "happy"), (tk + 0.1, "grin")]), T, tag=False,
               arms=("wave", "down") if sx > 0 else ("down", "wave"), look=0.5 * sx)
        ctx.restore()
        ctx.restore()


def s_problem(ctx, t, d):
    T = 6.43 + t
    st.burst(ctx, T, "#c4c8e8", "#4a4f8a", cy=560)
    closeup(ctx, OLIVER, keyed(T, [(0, "neutral"), (6.58, "worried")]), T, arms=("down", "shrug"))
    style.sweat(ctx, 560, 470, 1.0, T)
    label(ctx, "THE PROBLEM?", 360, 250, 62, fg=(1, 1, 1), scale=pop(T - 6.58) if T >= 6.58 else 0.0)


def s_getinto(ctx, t, d):
    T = 7.09 + t
    world(ctx, T, 960)
    st.chest(ctx, 360, 1010, 1.8, T, open_k=1.0)
    if T < 7.45:                                           # the dive
        p = (T - 7.09) / 0.36
        ctx.save()
        ox, oy = lerp(140, 360, p), lerp(860, 760, p) - math.sin(p * PI) * 220
        ctx.translate(ox, oy)
        ctx.rotate(p * PI)
        OLIVER.draw(ctx, 0, 120, 1.25, "grin", T, pose="jump", arms=("up", "up"), shadow=False)
        ctx.restore()
    else:
        legs_out(ctx, 360, 790, 1.3, T, vis=1.25)
        st.dust(ctx, 360, 790, (T - 7.45) / 0.4, n=6, spread=140)
    st.check_mark(ctx, 580, 520, 80, (T - 7.7) / 0.2)
    label(ctx, "GET IN?", 300, 300, 70, fg=st.GREEN, scale=pop(T - 7.7) if T >= 7.7 else 0.0)


def s_never(ctx, t, d):
    T = 8.31 + t
    ctx.set_source_rgb(*hexc("#2a1a14"))
    ctx.paint()
    for i in range(7):                                      # wooden planks inside the chest
        style.block(ctx, -40 + i * 120, -100, 112, 1500, 6, hexc("#5a3a22"), 4, gloss=False)
    st.glow(ctx, 360, 200, 300, (1, 0.9, 0.6), 0.5)          # light through the keyhole
    closeup(ctx, OLIVER, keyed(T, [(0, "worried"), (8.72, "scared")]), T, arms=("up", "up"))
    style.sweat(ctx, 570, 460, 1.0, T)
    style.shake_lines(ctx, 360, 560, 260, 240, T)
    st.red_x(ctx, 360, 900, 110, (T - 8.72) / 0.25)
    label(ctx, "GET OUT?", 360, 250, 74, fg=st.RED, scale=pop(T - 9.11) if T >= 9.11 else 0.0)


# ================================================================ vending machine
VM_X, VM_Y = 400, 1060


def s_vend_crawl(ctx, t, d):
    T = 9.59 + t
    st.street(ctx, T, y_ground=1000)
    st.vending_machine(ctx, VM_X, VM_Y, 0.95, T)
    fx, fy = VM_X - 152, VM_Y - 105
    if T < 10.35:
        p = (T - 9.59) / 0.76
        oliver(ctx, lerp(110, 200, p), 1000, 0.95, "grin", T, pose="walk", walk_phase=T * 2, look=0.6,
               arms=("point", "down"))
    else:
        legs_out(ctx, fy - 10, fx + 12, 1.1, T, side="left", vis=1.45, kick=2.5)
        st.dust(ctx, fx - 10, fy + 70, (T - 10.35) / 0.4, n=4, spread=50, r=18)
    if T >= 10.75:
        st.arrow(ctx, 120, 330, 230, 440, k=ease((T - 10.75) / 0.15))
    label(ctx, "SNACK TIME", 330, 260, 64, bg=st.RED, scale=pop(T - 10.04) if T >= 10.04 else 0.0)


def _chips_inside(T, who="oliver", expr="grin", talk=False, tag_k=None):
    def inside(c, gx, gy, gw, gh):
        if who == "oliver":
            OLIVER.draw(c, gx + gw * 0.5, gy + gh - 18, 1.05 * gw / 460, expr, T, arms=("hold", "hold"),
                        talk=talk, shadow=False)
        else:
            P[3].draw(c, gx + gw * 0.5, gy + gh - 18, 1.05 * gw / 460, expr, T, arms=("up", "up"), shadow=False)
        if tag_k is not None and tag_k >= 0:
            st.price_tag(c, gx + gw * 0.5, gy + gh * 0.52, gw / 460 * 1.1 * pop(tag_k), tilt=0.25 + 0.15 *
                         math.sin(T * 8) * math.exp(-2 * tag_k))
    return inside


def s_chips(ctx, t, d):
    T = 11.45 + t
    st.street(ctx, T, y_ground=1000)
    st.vending_machine(ctx, 470, 1530, 2.2, T, texts=False, inside=_chips_inside(T, expr=keyed(T, [(0, "happy"), (11.61, "stars")])),
                       gone=((2, 1), (3, 1)))
    for i in range(5):                                       # chips raining down inside
        k = (T - 11.6 - i * 0.12)
        if k > 0:
            st.chips_bag(ctx, 160 + i * 70, 560 + 380 * k * k, 0.9, st.CHIP_COLS[i], tilt=k * 4)
    label(ctx, "FREE!", 360, 280, 96, fg=st.YELLOW, scale=pop(T - 11.61) if T >= 11.61 else 0.0)


def s_onsale(ctx, t, d):
    T = 12.4 + t
    ctx.set_source_rgb(*hexc("#bfe6ff"))
    ctx.paint()
    for r in range(3):                                       # shelves behind him
        style.block(ctx, -100, 330 + r * 330, 920, 18, 4, hexc("#8a90a8"), 3, gloss=False)
        for k in range(5):
            st.chips_bag(ctx, 40 + k * 160, 270 + r * 330, 1.2, st.CHIP_COLS[(r + k) % 6])
    closeup(ctx, OLIVER, keyed(T, [(0, "scared"), (12.93, "shock")]), T, arms=("up", "up"),
            talk=talking("oliver", T))
    if T >= 13.24:
        k = T - 13.24
        st.price_tag(ctx, 360, 870, 1.4 * pop(k), tilt=0.2 + 0.3 * math.sin(k * 10) * math.exp(-3 * k))
    ctx.move_to(60, 150)                                      # the glass: frame + shine
    ctx.line_to(200, 150)
    ctx.line_to(40, 600)
    ctx.line_to(-100, 600)
    ctx.close_path()
    ctx.set_source_rgba(1, 1, 1, 0.3)
    ctx.fill()
    st.speech_bubble(ctx, 500, 330, "HELP!", 60, T - 12.42, tail=(-1, 1))
    if 12.5 < T < 13.0:                                      # banging on the glass
        st.impact_star(ctx, 170, 520, 70, (T - 12.5) % 0.25)


def s_bought(ctx, t, d):
    T = 13.72 + t
    st.street(ctx, T, y_ground=1000)
    st.vending_machine(ctx, 300, 1080, 1.0, T, inside=_chips_inside(T, expr="worried"))
    P[2].draw(ctx, 560, 1170, 1.1, keyed(T, [(0, "happy"), (14.19, "grin")]), T, arms=("point", "down"),
              look=-0.6)
    k = T - 13.9
    if 0 <= k < 0.3:                                          # a coin flies into the slot
        st.coin(ctx, lerp(520, 420, k / 0.3), lerp(700, 640, k / 0.3), 0.6, spin=T * 8)
    st.toast(ctx, 360, 330, "Chips: 1 R$ paid", T - 14.19, col=st.GREEN)


def s_gotoliver(ctx, t, d):
    T = 14.78 + t
    st.street(ctx, T, y_ground=1000)
    st.vending_machine(ctx, 290, 1000, 0.95, T, gone=((3, 0), (3, 1), (3, 2)))
    if T < 15.13:
        legs_out(ctx, 900, 158, 0.7, T, side="left", vis=0.6)
    else:
        k = T - 15.13
        st.poof(ctx, 200, 920, 70, k / 0.4)
        oliver(ctx, 200, 1000, 0.9, "crazy", T, arms=("wave", "down"), pose="sit" if k > 0.25 else "jump")
    P[2].draw(ctx, 500, 1000, 1.0, keyed(T, [(0, "neutral"), (15.13, "shock")]), T, arms=("up", "up"), look=-0.6)
    if T >= 15.13:
        st.speech_bubble(ctx, 500, 500, "?!", 70, T - 15.2, tail=(0, 1))


def s_pull(ctx, t, d):
    T = 16.1 + t
    st.street(ctx, T, y_ground=1000)
    st.vending_machine(ctx, 520, 1080, 1.0, T)
    out = T >= 16.92
    tug = math.sin(T * 30) * 8 if not out else 0.0
    fx, fy = 520 - 160, 1080 - 110
    if not out:
        ctx.save()
        ctx.rectangle(-3000, -5000, fx + 10 + 3000, 10000)
        ctx.clip()
        lying(ctx, OLIVER, fx + 120 + tug, fy, 0.85, "scared", T, head_right=False, arms=("up", "up"))
        ctx.restore()
        for i, x in enumerate((205, 125)):
            P[3 + i].draw(ctx, x + tug, 1170, 1.0, "angry", T, arms=("point", "point"), look=0.7, lean=-0.15)
    else:
        k = T - 16.92
        st.impact_star(ctx, fx, fy, 110, k, "POP!")
        oliver(ctx, lerp(fx - 60, 300, ease(k / 0.3)), 1170, 1.0, "laugh", T, arms=("up", "up"), pose="jump")
        for i, x in enumerate((205, 125)):
            P[3 + i].draw(ctx, x - 15 * ease(k / 0.3), 1170, 1.0, "shock", T, arms=("up", "up"), pose="sit")


def s_swap(ctx, t, d):
    T = 17.13 + t
    st.street(ctx, T, y_ground=1000)
    st.vending_machine(ctx, 390, 1080, 1.0, T,
                       inside=_chips_inside(T, who="friend", expr=keyed(T, [(0, "shock"), (17.74, "cry")]),
                                            tag_k=T - 17.74))
    oliver(ctx, 140, 1000, 0.9, "grin", T, arms=("shrug", "shrug"))
    label(ctx, "STUCK!", 390, 250, 80, fg=st.RED, scale=pop(T - 17.74) if T >= 17.74 else 0.0)


# ================================================================ obby
def s_obby(ctx, t, d):
    T = 18.7 + t
    tops = st.obby(ctx, T, y_lava=1080, y_top=900, x0=-60, dx=240)
    x, y = tops[1]
    st.spawn_pad(ctx, x, y, 1.0, beam=clamp(1 - (T - 18.97) / 0.6))
    if T >= 18.97:
        st.poof(ctx, x, y - 120, 80, (T - 18.97) / 0.4)
        oliver(ctx, x, y, 1.0, keyed(T, [(0, "shock"), (19.32, "grin")]), T, arms=("up", "down"))
        st.sparkles(ctx, T, x, y - 200, spread=120, n=8, seed=5)
    label(ctx, "OBBY!", 360, 270, 96, fg=st.YELLOW, scale=pop(T - 19.8) if T >= 19.8 else 0.0)


def s_jump(ctx, t, d):
    T = 19.97 + t
    tops = st.obby(ctx, T, y_lava=1100, y_top=980, x0=-200, dx=300, rise=-20)
    p = clamp((T - 19.97) / 1.1)
    x0, y0 = tops[1]
    x1, y1 = tops[2]
    x = lerp(x0, x1 - 100, p)
    y = lerp(y0, y1 + 100, p) - math.sin(p * PI) * 380
    st.speed_lines(ctx, T, x, y - 150, n=14, r0=160, r1=500, a=0.4)
    ctx.save()
    ctx.translate(x, y - 120)
    ctx.rotate(p * 2 * PI * (1 if T > 20.57 else 0.3))
    OLIVER.draw(ctx, 0, 120, 1.0, "crazy", T, pose="jump", arms=("up", "up"), shadow=False)
    ctx.restore()
    label(ctx, "STRAIGHT IN", 360, 270, 64, bg=st.PINK, scale=pop(T - 20.57) if T >= 20.57 else 0.0)


def s_gap(ctx, t, d):
    T = 21.16 + t
    st.game_sky(ctx)
    st.block_clouds(ctx, T)
    st.lava(ctx, 1150, T)
    gx = 360
    drop = ease(clamp((T - 21.16) / 0.4))
    ctx.save()                                               # Oliver squeezed into the gap
    ctx.translate(gx, 0)
    ctx.scale(0.45, 1)
    OLIVER.draw(ctx, 0, lerp(700, 1080, drop), 1.2, "scared", T, arms=("up", "up"), shadow=False, bob=0.3)
    ctx.restore()
    st.platform(ctx, -60, 820, gx - 25 + 60, "#2cd5fc", h=200)
    st.platform(ctx, gx + 25, 820, 400, "#fa3a9f", h=200)
    if T >= 21.6:
        st.arrow(ctx, 600, 470, 420, 760, k=ease((T - 21.6) / 0.15))
    label(ctx, "TINY GAP", 330, 300, 80, fg=st.YELLOW, scale=pop(T - 21.6) if T >= 21.6 else 0.0)


def _dark_gap(ctx, T):
    ctx.set_source_rgb(*hexc("#1b1f4a"))
    ctx.paint()
    style.block(ctx, -100, -200, 400, 2000, 0, hexc("#1a8fb0"), 6, gloss=False)    # the platform walls
    style.block(ctx, 420, -200, 500, 2000, 0, hexc("#b02a74"), 6, gloss=False)
    st.glow(ctx, 360, 120, 260, (0.8, 0.95, 1), 0.6)


def s_guys(ctx, t, d):
    T = 23.13 + t
    _dark_gap(ctx, T)
    ctx.save()
    ctx.translate(360, 0)
    ctx.scale(0.82, 1)
    ctx.translate(-360, 0)
    closeup(ctx, OLIVER, "stars", T, arms=("wave", "wave"), talk=talking("oliver", T))
    ctx.restore()
    st.speech_bubble(ctx, 360, 290, "GUYS!", 70, T - 23.16, tail=(0, 1))


def s_secret(ctx, t, d):
    T = 23.69 + t
    _dark_gap(ctx, T)
    sign(ctx, 480, 1000, 0.9, "SECRET ROOM", tilt=0.04)
    oliver(ctx, 170, 1160, 1.05, keyed(T, [(0, "grin"), (24.08, "stars")]), T, arms=("show", "down"),
           talk=talking("oliver", T))
    st.sparkles(ctx, T, 400, 760, spread=220, n=10, seed=13, c=st.YELLOW)


def s_notroom(ctx, t, d):
    T = 24.86 + t
    _dark_gap(ctx, T)
    sign(ctx, 360, 900, 1.3, "SECRET ROOM", tilt=-0.03)
    st.red_x(ctx, 360, 690, 200, (T - 25.12) / 0.25)
    label(ctx, "NOPE", 360, 280, 90, fg=st.RED, scale=pop(T - 25.37) if T >= 25.37 else 0.0)


def s_floor(ctx, t, d):
    T = 25.79 + t
    st.game_sky(ctx)
    st.block_clouds(ctx, T)
    st.lava(ctx, 1150, T)
    style.block(ctx, 50, 560, 540, 360, 14, hexc("#2cd5fc"), 7)            # the platform, cut open
    style.block(ctx, 95, 700, 450, 110, 10, style.dark(hexc("#2cd5fc"), 0.45), 5, gloss=False)
    ctx.save()                                                              # Oliver, flat as a pancake
    ctx.rectangle(95, 700, 450, 110)
    ctx.clip()
    lying(ctx, OLIVER, 140, 760, 0.85, "forced", T, head_right=True, squash=0.45)
    ctx.restore()
    if T >= 26.08:
        st.arrow(ctx, 560, 420, 440, 680, k=ease((T - 26.08) / 0.15))
    label(ctx, "THE FLOOR", 330, 330, 80, fg=st.YELLOW, scale=pop(T - 26.08) if T >= 26.08 else 0.0)


def rec_overlay(ctx, t, d):
    rec_frame(ctx, 26.68 + t)


def rec_frame(ctx, T):
    ctx.set_source_rgb(1, 1, 1)
    ctx.set_line_width(10)
    for (x, y, dx, dy) in ((70, 200, 1, 1), (650, 200, -1, 1), (70, 1000, 1, -1), (650, 1000, -1, -1)):
        ctx.move_to(x, y + dy * 80)
        ctx.line_to(x, y)
        ctx.line_to(x + dx * 80, y)
    ctx.stroke()
    if int(T * 2.5) % 2 == 0:
        ctx.new_sub_path()
        ctx.arc(120, 250, 16, 0, 2 * PI)
        ctx.set_source_rgb(*st.RED)
        ctx.fill()
    st.bold_text(ctx, "REC", 180, 250, 36, (1, 1, 1), shadow=False, stroke=0.15)


def _gap_top(ctx, T, wave=True, gx=360, hand_y=790):
    st.game_sky(ctx)
    st.block_clouds(ctx, T)
    st.lava(ctx, 1150, T)
    if wave:                                                    # a tiny waving hand in the gap
        ctx.save()
        ctx.translate(gx, hand_y)
        ctx.rotate(math.sin(T * 14) * 0.4)
        style.block(ctx, -15, -70, 30, 80, 10, hexc("#e9c22c"), 3)
        ctx.restore()
    st.platform(ctx, -60, 820, gx - 15 + 60, "#2cd5fc", h=200)
    st.platform(ctx, gx + 15, 820, 400, "#fa3a9f", h=200)
    if wave:                                                    # the hand pokes out over the front edge
        ctx.save()
        ctx.rectangle(gx - 40, 600, 80, 196)
        ctx.clip()
        ctx.translate(gx, hand_y)
        ctx.rotate(math.sin(T * 14) * 0.4)
        style.block(ctx, -15, -70, 30, 80, 10, hexc("#e9c22c"), 3)
        ctx.restore()


def s_wave(ctx, t, d):
    T = 26.68 + t
    _gap_top(ctx, T)
    label(ctx, "HI CAMERA!", 380, 560, 56, bg=st.UI_DARK, fg=st.YELLOW, scale=pop(T - 27.14) if T >= 27.14 else 0.0)


def s_nobody(ctx, t, d):
    T = 27.78 + t
    _gap_top(ctx, T)
    for i, (x0, sp, tq) in enumerate(((100, 380, 27.93), (590, -380, 28.2))):
        x = x0 + sp * (T - 27.78)
        P[5 + i].draw(ctx, x, 800, 1.0, "neutral" if T < tq else "worried", T, pose="run", walk_phase=T * 2.5,
                      look=0.6 if sp > 0 else -0.6)
        st.speech_bubble(ctx, x, 440, "?", 56, T - tq, tail=(0, 1))
    label(ctx, "NOBODY SAW", 360, 260, 66, fg=(1, 1, 1), scale=pop(T - 28.35) if T >= 28.35 else 0.0)


def s_admin(ctx, t, d):
    T = 28.9 + t
    st.burst(ctx, T, "#e2c8ff", "#7a3fd8", cy=560)
    closeup(ctx, ADMIN, keyed(T, [(0, "smug"), (29.48, "determined")]), T, arms=("down", "up"), x=330)
    st.nametag(ctx, 330, 300, "[ADMIN]", size=60, col=st.RED)
    st.wand(ctx, 560, 600, 1.4, ang=0.3, T=T)
    if T >= 29.48:
        st.sparkles(ctx, T, 600, 420, spread=160, n=10, seed=7, c=st.YELLOW)
        st.flash(ctx, 0.5 * math.exp(-12 * (T - 29.48)))


def s_safe(ctx, t, d):
    T = 30.01 + t
    world(ctx, T, 980)
    st.spawn_pad(ctx, 360, 1080, 1.4, beam=clamp(1 - (T - 30.03) / 0.6))
    if T >= 30.08:
        oliver(ctx, 360, 1080, 1.2, "happy", T, arms=("up", "up"))
        st.poof(ctx, 360, 930, 90, (T - 30.08) / 0.4)
    st.check_mark(ctx, 560, 420, 80, (T - 30.23) / 0.2)
    label(ctx, "SAFE!", 330, 290, 90, fg=st.GREEN, scale=pop(T - 30.23) if T >= 30.23 else 0.0)


def s_promise(ctx, t, d):
    T = 30.73 + t
    st.burst(ctx, T, "#fff6c4", "#8fd0ff", cy=560)
    closeup(ctx, OLIVER, keyed(T, [(0, "happy"), (31.0, "forced")]), T, arms=("down", "up"))
    halo(ctx, 360, 330, 150, T)
    label(ctx, "I PROMISE!", 360, 230, 70, fg=(1, 1, 1), scale=pop(T - 31.0) if T >= 31.0 else 0.0)


# ================================================================ race car + under the map
def s_5sec(ctx, t, d):
    T = 32.19 + t
    st.burst(ctx, T, "#c4d8ff", "#2f3f9a", cy=600)
    st.second_card(ctx, 360, 560, 5, T - 32.24, word="SECONDS")
    st.day_text(ctx, "LATER...", 360, 760, T - 32.83, size=90)


def s_car(ctx, t, d):
    T = 33.16 + t
    st.game_sky(ctx)
    st.block_clouds(ctx, T, drift=-400)
    ctx.rectangle(-3000, 980, 7000, 3000)
    ctx.set_source_rgb(*hexc("#51c844"))
    ctx.fill()
    style.block(ctx, -100, 1000, 920, 160, 0, hexc("#4a4f5e"), 5, gloss=False)    # the road
    for i in range(8):
        x = (i * 200 - (T * 1400) % 200) - 100
        style.block(ctx, x, 1070, 110, 16, 6, (1, 1, 1), 2, gloss=False)
    st.speed_lines(ctx, T, 360, 900, n=20, r0=260, r1=900, a=0.35)

    def drv(c, hx, hy):
        OLIVER.draw(c, hx, hy + 150 * 0.9, 0.85, keyed(T, [(0, "grin"), (33.96, "crazy")]), T, shadow=False)
    st.race_car(ctx, 360 + math.sin(T * 20) * 4, 1120, 0.9, T, driver=drv, speed=2.0)
    for i in range(4):
        st.poof(ctx, 60 - i * 40, 1080 - i * 10, 30, ((T * 3 + i * 0.25) % 1))
    label(ctx, "RACE CAR", 360, 270, 76, bg=st.RED, scale=pop(T - 33.6) if T >= 33.6 else 0.0)


def s_wall(ctx, t, d):
    T = 34.14 + t
    world(ctx, T, 1000)
    hit = 34.4
    wx = 470
    if T < hit:
        st.brick_wall(ctx, wx, 1080, 180, 520)
    p = clamp((T - 34.14) / (hit - 34.14))

    def drv(c, hx, hy):
        OLIVER.draw(c, hx, hy + 150 * 0.8, 0.75, "crazy" if T < hit else "shock", T, shadow=False)
    st.race_car(ctx, lerp(-150, 330, p) + (T - hit) * 300 * (T > hit), 1100, 0.8, T, driver=drv, speed=2.0)
    if T >= hit:
        k = T - hit
        for i in range(14):                                     # bricks flying
            a = -1.2 + i * 0.17
            bx = wx + 90 + math.cos(a) * 700 * k
            by = 800 + i * 20 + math.sin(a) * 600 * k + 1500 * k * k
            ctx.save()
            ctx.translate(bx, by)
            ctx.rotate(k * (6 + i))
            style.block(ctx, -32, -15, 64, 30, 4, hexc("#aaafbc"), 3)
            ctx.restore()
        st.impact_star(ctx, wx - 60, 750, 150, k, "CRASH!")
        st.flash(ctx, 0.6 * math.exp(-14 * k))


def s_fall(ctx, t, d):
    T = 34.96 + t
    st.void_bg(ctx, top="#84d4fb", bottom=VOID, y0=500, y1=1300)
    st.map_slab(ctx, T, y_top=380, thick=230, hole=(330, 130))
    p = clamp((T - 34.98) / 1.4)
    q = ease(p)
    cx, cy = lerp(400, 370, q), lerp(560, 880, q)      # it falls away into the void, shrinking
    ctx.save()
    ctx.translate(cx, cy)
    ctx.rotate(p * 5)
    ctx.scale(lerp(1.0, 0.3, q), lerp(1.0, 0.3, q))
    ctx.translate(-cx, -cy)

    def drv(c, hx, hy):
        OLIVER.draw(c, hx, hy + 150 * 0.55, 0.5, "scared", T, shadow=False)
    st.race_car(ctx, cx, cy + 40, 0.55, T, driver=drv)
    ctx.restore()
    st.speed_lines(ctx, T, cx, cy, n=10, r0=120, r1=400, a=0.35)
    label(ctx, "UNDER THE MAP", 360, 230, 62, bg=st.UI_DARK, fg=st.YELLOW,
          scale=pop(T - 35.65) if T >= 35.65 else 0.0)


def _rescue_top(ctx, T, y_top=500):
    st.void_bg(ctx, top="#84d4fb", bottom=VOID, y0=y_top + 200, y1=y_top + 900)
    st.block_clouds(ctx, T, y0=60, y1=300, n=3)
    st.map_slab(ctx, T, y_top=y_top, thick=230, hole=(300, 140), trees=False)


def s_ropes(ctx, t, d):
    T = 36.57 + t
    _rescue_top(ctx, T)
    rope_end = 500 + 260 + 160 * ease(clamp((T - 37.0) / 0.6))
    ctx.move_to(370, 460)
    ctx.curve_to(372, 600, 368, 700, 370, rope_end)
    ctx.set_source_rgb(*hexc("#8a5a3a"))
    ctx.set_line_width(12)
    ctx.stroke()
    for i, x in enumerate((250, 150)):
        P[3 + i].draw(ctx, x, 510, 0.9, "determined", T, arms=("hold", "hold"), look=0.6, lean=-0.1)
    P[5].draw(ctx, 520, 510, 0.9, "worried", T, arms=("point", "down"), look=-0.6)
    oliver(ctx, 370, 1000, 0.6, "worried", T, arms=("up", "up"))
    label(ctx, "ROPES", 360, 260, 82, fg=st.YELLOW, scale=pop(T - 37.49) if T >= 37.49 else 0.0)


def s_crane(ctx, t, d):
    T = 37.98 + t
    _rescue_top(ctx, T)
    k = ease(clamp((T - 37.98) / 0.3))
    hx, hy = st.crane(ctx, lerp(800, 600, k), 510, 0.55, T, hook_y=lerp(260, 820, ease(clamp((T - 38.1) / 0.4))))
    oliver(ctx, 370, 1000, 0.6, "shock", T, arms=("up", "up"))
    label(ctx, "A CRANE", 300, 260, 80, fg=st.YELLOW, scale=pop(T - 38.08) if T >= 38.08 else 0.0)


def s_rocket(ctx, t, d):
    T = 38.55 + t
    _rescue_top(ctx, T, y_top=820)
    gs = 0.7 + 0.25 * pop(T - 38.79) if T >= 38.79 else 0.7
    st.rocket(ctx, 480, 830, gs, T, label_txt="SAVE")
    for i, x in enumerate((130, 240)):
        P[3 + i].draw(ctx, x, 830, 0.9, "stars", T, arms=("up", "up"), pose="jump" if (T * 3 + i) % 1 < 0.5 else "stand")
    label(ctx, "GIANT!", 220, 330, 80, bg=st.RED, scale=pop(T - 38.79) if T >= 38.79 else 0.0)


def s_explode(ctx, t, d):
    T = 39.69 + t
    _rescue_top(ctx, T, y_top=820)
    boom = 40.16
    if T < boom:
        st.rocket(ctx, 480, 830 - (T - 39.69) * 120, 0.95, T, flame=1.0, label_txt="SAVE",
                  tilt=math.sin(T * 30) * 0.05)
    else:
        k = T - boom
        st.shockwave(ctx, 500, 600, k / 0.6, r_max=700)
        e = ease(clamp(k / 0.5))
        for i in range(8):                                    # players blown up and out
            a = i * 0.8
            P[i].draw(ctx, 390 + math.cos(a) * 160 * e, 720 + math.sin(a) * 150 * e - 120 * e, 0.55, "scared",
                      T, arms=("up", "up"), pose="jump")
        st.impact_star(ctx, 420, 560, 200, k, "BOOM!", c1="#fff3a8", c2="#ff5a1a")
        st.flash(ctx, 0.8 * math.exp(-10 * k))


def s_twenty(ctx, t, d):
    T = 40.81 + t
    st.void_bg(ctx, top="#84d4fb", bottom=VOID, y0=300, y1=1300)
    st.map_slab(ctx, T, y_top=200, thick=220, hole=(290, 160), trees=False)
    n = 0
    for i in range(20):
        t0 = 40.85 + i * 0.07
        k = T - t0
        if k < 0:
            continue
        n += 1
        q = ease(clamp(k / 1.1))
        if q >= 1:
            continue
        off = (i * 53) % 260 - 130
        x = 370 + off * lerp(1.0, 0.35, q)
        y = lerp(420, 800, q)
        ctx.save()
        ctx.translate(x, y)
        ctx.rotate(k * (2 + i % 3) * (1 if i % 2 else -1))
        ctx.scale(1 - 0.85 * q, 1 - 0.85 * q)
        P[i % 14].draw(ctx, 0, 60, 0.45, "scared", T, arms=("up", "up"), pose="jump", shadow=False)
        ctx.restore()
    st.number_counter(ctx, 360, 935, 0.6, n, T, prefix="+", col=st.RED)
    label(ctx, "20 MORE!", 360, 140 + 90, 70, bg=st.RED, scale=pop(T - 41.23) if T >= 41.23 else 0.0)


def s_admin_fall(ctx, t, d):
    T = 42.91 + t
    st.void_bg(ctx, top="#3a3f8a", bottom=VOID, y0=0, y1=1300)
    st.speed_lines(ctx, T, 360, 640, n=24, r0=300, r1=1200, a=0.35, col=(0.7, 0.75, 1.0))
    ctx.save()
    ctx.translate(360, 700)
    ctx.rotate(math.sin(T * 6) * 0.25)
    admin(ctx, 0, 300, 1.5, keyed(T, [(0, "shock"), (43.76, "scared")]), T, arms=("up", "up"), pose="jump")
    ctx.restore()
    label(ctx, "EVEN ADMIN?!", 360, 230, 60, fg=st.RED, scale=pop(T - 43.31) if T >= 43.31 else 0.0)


CROWD_STUCK = [(115, 960, 0.8, 0, "cry"), (210, 990, 0.85, 1, "sad"), (450, 990, 0.85, 2, "worried"),
               (530, 950, 0.75, 3, "cry"), (165, 870, 0.62, 4, "sad"), (500, 860, 0.6, 5, "sad"),
               (270, 860, 0.58, 6, "worried"), (410, 860, 0.58, 7, "cry")]


def s_stuck(ctx, t, d):
    T = 44.22 + t
    under_map(ctx, T, y_top=-80)
    invisible_floor(ctx, 995)
    for x, y, s, i, e in sorted(CROWD_STUCK, key=lambda c: c[1]):
        P[i].draw(ctx, x, y, s, e, T, arms=("down", "down"), bob=0.5)
    admin(ctx, 385, 1000, 0.9, "sad", T, tag=False, arms=("shrug", "shrug"))
    oliver(ctx, 300, 1005, 0.95, "forced", T, arms=("shrug", "shrug"))
    label(ctx, "STUCK", 360, 320, 100, fg=st.RED, scale=pop(T - 45.18) if T >= 45.18 else 0.0)


def s_queue(ctx, t, d):
    T = 45.58 + t
    under_map(ctx, T, y_top=-160)
    closeup(ctx, ADMIN, keyed(T, [(0, "worried"), (46.12, "scared")]), T, arms=("down", "up"), x=330)
    st.wand(ctx, 560, 600, 1.4, ang=0.3 + math.sin(T * 25) * 0.2, T=T)
    style.sweat(ctx, 540, 450, 1.0, T)
    style.sweat(ctx, 170, 500, 1.0, T + 0.3)
    for i in range(6):                                          # zap, zap, zap
        k = T - (45.7 + i * 0.22)
        if 0 <= k < 0.2:
            st.flash(ctx, 0.35 * (1 - k / 0.2))
            st.poof(ctx, 600, 380, 60, k / 0.2)
    label(ctx, "TOO SLOW!", 360, 250, 72, fg=st.YELLOW, scale=pop(T - 46.37) if T >= 46.37 else 0.0)


def s_requests(ctx, t, d):
    T = 46.93 + t
    st.burst(ctx, T, "#ffb3b3", "#c0303a", cy=640)
    style.block(ctx, 60, 170, 600, 860, 30, st.UI_DARK, 6, outline=style.INK)
    st.bold_text(ctx, "TELEPORT REQUESTS", 360, 220, 38, st.YELLOW, shadow=False)
    names = ["Oliver", "BloxKid", "Pizza99", "Zuzu", "NoobMaster", "Kira", "Gamer_7", "Bob"]
    n = min(len(names), int((T - 46.93) / 0.09) + 2)
    for i in range(n):
        y = 290 + i * 80
        style.block(ctx, 90, y - 30, 540, 64, 14, hexc("#2f3550"), 3, gloss=False)
        st.bold_text(ctx, names[i], 120, y, 30, (1, 1, 1), align="l", shadow=False, stroke=0.0)
        st.bold_text(ctx, "WAITING", 600, y, 26, st.RED, align="r", shadow=False, stroke=0.0)
    label(ctx, "999+", 520, 955, 70, bg=st.RED, scale=pop(T - 47.1) if T >= 47.1 else 0.0)


def s_beg(ctx, t, d):
    T = 47.76 + t
    under_map(ctx, T, y_top=-200)
    invisible_floor(ctx, 995)
    lines = [("Zuzu", "pls devs", "#ff5fb0"), ("Bob", "HELP US", "#4fd16a"), ("Kira", "add a way out!!", "#ffd84a"),
             ("Oliver", "sorry :(", "#ff8a3d"), ("Pizza99", "DEVS PLEASE", "#6fc3ff")]
    n = min(len(lines), int((T - 47.8) / 0.25) + 1)
    st.chat_box(ctx, 60, 200, 600, 330, lines[:n], T, size=32, title="Chat")
    for i, x in enumerate((130, 225, 435, 515)):
        P[i + 8].draw(ctx, x, 990, 0.8, "cry" if i % 2 else "worried", T, arms=("up", "up"),
                      pose="sit" if i % 2 else "stand")
    oliver(ctx, 330, 1000, 0.95, "sad", T, tag=False, arms=("up", "up"))
    label(ctx, "DEVS!", 330, 610, 80, fg=st.YELLOW, scale=pop(T - 48.6) if T >= 48.6 else 0.0)


def s_exit(ctx, t, d):
    T = 49.13 + t
    under_map(ctx, T, y_top=-200)
    st.glow(ctx, 360, 700, 380, (0.5, 1.0, 0.6), 0.6)
    style.block(ctx, 250, 500, 220, 380, 16, hexc("#2e9c46"), 7)
    style.block(ctx, 280, 540, 160, 320, 10, hexc("#bff7c8"), 4, gloss=False)
    style.block(ctx, 240, 420, 240, 70, 12, st.GREEN, 5)
    st.bold_text(ctx, "EXIT", 360, 455, 46, (1, 1, 1), shadow=False, stroke=0.14)
    st.speech_bubble(ctx, 560, 380, "?", 70, T - 49.26, tail=(-1, 1))
    for i, x in enumerate((130, 520)):
        P[i].draw(ctx, x, 1000, 0.95, "worried", T, arms=("point", "down") if i == 0 else ("down", "point"),
                  look=0.5 if i == 0 else -0.5)
    label(ctx, "1 WAY OUT?", 360, 230, 72, fg=st.GREEN, scale=pop(T - 49.26) if T >= 49.26 else 0.0)


def s_nohelp(ctx, t, d):
    T = 50.22 + t
    st.burst(ctx, T, "#c4c8e8", "#3a3f8a", cy=600)
    P[1].draw(ctx, 200, 1000, 1.1, "worried", T, arms=("up", "down"))
    st.speech_bubble(ctx, 380, 480, "ADMIN, HELP!", 50, T - 50.26, tail=(-1, 1))
    st.red_x(ctx, 380, 480, 150, (T - 50.88) / 0.25)
    label(ctx, "NO HELP", 360, 250, 84, fg=st.RED, scale=pop(T - 50.88) if T >= 50.88 else 0.0)


# ================================================================ developer
def desk_front(ctx, y_desk):
    style.block(ctx, -100, y_desk, 920, 50, 8, hexc("#b9b4d8"), 5)
    style.block(ctx, -100, y_desk + 50, 920, 700, 0, hexc("#7a6aa8"), 5, gloss=False)


def _reset_code(typed, btn_k):
    def fn(c, x, y, w, h, TT):
        st.code_screen(c, x, y, w, h, TT, typed=typed)
        if btn_k > 0:
            st.reset_button(c, x + w * 0.5, y + h * 0.62, 0.42 * w / 560 * pop(btn_k), TT, glow_a=0.4)
    return fn


def dev_at_desk(ctx, T, expr, night, sun=0.0, n_cups=1, lean=0.0):
    st.office(ctx, T, night=night, sun=sun, y_desk=900)
    DEV.draw(ctx, 230, 1070, 1.4, expr, T, arms=("hold", "hold"), lean=lean, bob=0.4 if lean else 1.0)
    desk_front(ctx, 900)
    st.monitor(ctx, 500, 905, 0.42, T, _reset_code(0.6, 0.0))
    for i in range(n_cups):
        st.coffee_cup(ctx, 70 + (i % 4) * 56, 905 - (i // 4) * 62, 0.85, steam_T=T if i == n_cups - 1 else None)


def s_night(ctx, t, d):
    T = 51.36 + t
    dev_at_desk(ctx, T, keyed(T, [(0, "tired"), (52.12, "sleepy")]), 1.0, n_cups=1 + int(clamp((T - 51.6) / 1.0) * 6),
                lean=0.06)
    st.zzz(ctx, 330, 520, T)
    label(ctx, "THAT NIGHT", 360, 330, 64, bg=st.UI_DARK, fg=st.YELLOW, scale=pop(T - 51.63) if T >= 51.63 else 0.0)


def s_code(ctx, t, d):
    T = 52.95 + t
    st.night_wall(ctx, 2000)
    st.monitor(ctx, 360, 860, 1.12, T, _reset_code(clamp((T - 52.97) / 1.0), T - 54.11 if T > 54.11 else 0.0))
    st.keyboard(ctx, 360, 1080, 1.0, T, mash=1.0)
    label(ctx, "NEW BUTTON", 360, 250, 64, fg=st.GREEN, scale=pop(T - 54.11) if T >= 54.11 else 0.0)


def s_two(ctx, t, d):
    T = 54.49 + t
    st.office(ctx, T, night=1.0)
    closeup(ctx, DEV, "smirk", T, arms=("down", "up"))
    label(ctx, "2 WORDS", 360, 250, 84, fg=st.YELLOW, scale=pop(T - 54.69) if T >= 54.69 else 0.0)


def s_reveal(ctx, t, d):
    T = 55.42 + t
    st.burst(ctx, T, "#ffe27a", "#e8323a", cy=640, spin=0.3)
    st.reset_button(ctx, 340, 560, 0.95 * (pop(T - 55.44) if T >= 55.44 else 0.0), T, glow_a=0.7)
    st.sparkles(ctx, T, 340, 560, spread=300, n=16, seed=3, c=st.YELLOW, size=22)
    if T >= 55.44:
        st.flash(ctx, 0.5 * math.exp(-12 * (T - 55.44)))


def s_press(ctx, t, d):
    T = 56.51 + t
    under_map(ctx, T, y_top=-200)
    invisible_floor(ctx, 995)
    for x, y, s, i, e in CROWD_STUCK[:4]:
        P[i].draw(ctx, x, y, s, "worried", T, arms=("down", "down"), bob=0.5)
    oliver(ctx, 330, 1005, 1.05, keyed(T, [(0, "determined"), (PRESS, "grin")]), T, arms=("down", "point"))
    pressed = T >= PRESS
    st.reset_button(ctx, 330, 400, 0.8, T, pressed=1.0 if pressed else 0.0, glow_a=0.4)
    if T < PRESS + 0.2:
        kk = ease(clamp((T - 56.7) / (PRESS - 56.7)))
        st.cursor(ctx, lerp(580, 390, kk), lerp(700, 420, kk), 2.0, click=1.0 if pressed else 0.0)
    st.tap_ripple(ctx, 370, 410, (T - PRESS) / 0.4)


def s_boom(ctx, t, d):
    T = 57.5 + t
    st.burst(ctx, T, "#fff3a8", "#ff7a1a", cy=700, spin=0.6)
    k = T - BOOM
    if k < 0:
        oliver(ctx, 340, 1000, 1.2, "grin", T, tag=False)
    else:
        break_apart(ctx, 340, 1000, 1.2, k)
        st.impact_star(ctx, 350, 600, 240, k, "BOOM!", c1="#fff3a8", c2="#ff5a1a")
        st.flash(ctx, 0.7 * math.exp(-12 * k))


def s_spawn(ctx, t, d):
    T = 58.05 + t
    world(ctx, T, 980)
    st.spawn_pad(ctx, 360, 1080, 1.4, beam=clamp(1 - (T - BACK) / 0.7))
    k = T - (BACK + 0.06)
    if k >= 0:
        ctx.save()
        ctx.translate(360, 1080)
        ctx.scale(1, pop(k))
        ctx.translate(-360, -1080)
        oliver(ctx, 360, 1080, 1.2, keyed(T, [(0, "shock"), (58.4, "laugh")]), T, arms=("up", "up"))
        ctx.restore()
    st.sparkles(ctx, T, 360, 800, spread=200, n=12, seed=6, c=(1, 1, 1))
    label(ctx, "SPAWN", 360, 280, 90, fg=st.GREEN, scale=pop(T - 58.52) if T >= 58.52 else 0.0)


def s_party(ctx, t, d):
    T = 58.9 + t
    world(ctx, T, 920)
    st.confetti(ctx, T, 58.95, n=50)
    for i in range(6):
        x = 105 + i * 88
        y = 900 + (i % 2) * 40
        hop = abs(math.sin(T * 7 + i)) * 40
        P[i].draw(ctx, x, y - hop, 0.7, "laugh" if i % 2 else "stars", T, arms=("up", "up"), pose="jump")
    admin(ctx, 460, 1000 - abs(math.sin(T * 7)) * 30, 0.9, "laugh", T, arms=("up", "up"), pose="jump")
    oliver(ctx, 230, 1000 - abs(math.sin(T * 7 + 1)) * 40, 1.0, "stars", T, arms=("up", "up"), pose="jump")
    label(ctx, "FREEDOM!", 360, 270, 84, fg=st.YELLOW, scale=pop(T - 59.27) if T >= 59.27 else 0.0)


def s_morning(ctx, t, d):
    T = 60.34 + t
    dev_at_desk(ctx, T, keyed(T, [(0, "happy"), (61.24, "neutral")]), 0.0, sun=1.0, n_cups=1)
    label(ctx, "NEXT MORNING", 360, 260, 60, bg=st.UI_DARK, fg=st.YELLOW, scale=pop(T - 60.55) if T >= 60.55 else 0.0)


def _reset_stats(T):
    def fn(c, x, y, w, h, TT):
        c.set_source_rgb(*hexc("#141a2e"))
        c.rectangle(x, y, w, h)
        c.fill()
        st.bold_text(c, "RESETS TODAY", x + w / 2, y + h * 0.14, h * 0.09, hexc("#9aa0b8"), shadow=False, stroke=0.0)
        v = int(12483 * ease(clamp((TT - 61.7) / 1.1)))
        st.bold_text(c, f"{v:,}", x + w / 2, y + h * 0.34, h * 0.2, st.RED, shadow=False, stroke=0.1)
        c.move_to(x + w * 0.08, y + h * 0.9)                    # graph line shooting up
        n = 12
        for i in range(n + 1):
            p = i / n
            q = min(p, clamp((TT - 61.7) / 1.1))
            c.line_to(x + w * (0.08 + 0.84 * q), y + h * (0.9 - 0.4 * q ** 3))
        c.set_source_rgb(*st.RED)
        c.set_line_width(h * 0.025)
        c.stroke()
    return fn


def s_resets(ctx, t, d):
    T = 61.6 + t
    st.night_wall(ctx, 2000)
    st.monitor(ctx, 360, 950, 1.12, T, _reset_stats(T))
    DEV.draw(ctx, 190, 1330, 2.0, keyed(T, [(0, "neutral"), (62.09, "shock")]), T, arms=("down", "down"), look=0.6,
             bob=0.4)
    label(ctx, "THOUSANDS?!", 360, 250, 62, fg=st.YELLOW, scale=pop(T - 62.09) if T >= 62.09 else 0.0)


def s_same(ctx, t, d):
    T = 63.15 + t
    st.burst(ctx, T, "#c4d8ff", "#2f3f9a", cy=640)
    style.block(ctx, 60, 200, 600, 820, 30, st.UI_DARK, 6, outline=style.INK)
    st.bold_text(ctx, "RESET LOG", 360, 250, 40, st.YELLOW, shadow=False)
    n = min(8, int((T - 63.15) / 0.08) + 2)
    for i in range(n):
        y = 320 + i * 86
        style.block(ctx, 90, y - 32, 540, 68, 14, hexc("#2f3550"), 3, gloss=False)
        st.face_icon(ctx, 140, y, 26, "#e9c22c", "#ff7a1a", expr="grin")
        st.bold_text(ctx, "Oliver", 190, y, 32, (1, 1, 1), align="l", shadow=False, stroke=0.0)
        st.bold_text(ctx, "RESET", 600, y, 28, st.RED, align="r", shadow=False, stroke=0.0)
    if T >= 63.66:
        k = ease((T - 63.66) / 0.2)
        ctx.save()
        ctx.translate(245, 620)
        ctx.scale(1, 3.0)
        ctx.new_sub_path()
        ctx.arc(0, 0, 110 * k + 1, 0, 2 * PI * k)
        ctx.restore()
        ctx.set_source_rgb(*st.RED)
        ctx.set_line_width(12)
        ctx.stroke()
    label(ctx, "SAME PLAYER", 360, 965, 60, bg=st.RED, scale=pop(T - 63.66) if T >= 63.66 else 0.0)


def s_hobby(ctx, t, d):
    T = 64.35 + t
    st.burst(ctx, T, "#ffe27a", "#f29a2e", cy=560)
    closeup(ctx, OLIVER, keyed(T, [(0, "grin"), (64.91, "stars")]), T, arms=("down", "point"))
    st.lightbulb(ctx, 570, 330, 0.8, T - 64.91, T)
    label(ctx, "NEW HOBBY", 330, 240, 76, fg=(1, 1, 1), scale=pop(T - 65.4) if T >= 65.4 else 0.0)


def s_test1(ctx, t, d):
    T = 66.14 + t
    world(ctx, T, 1000)
    style.block(ctx, 300, 720, 120, 300, 10, hexc("#8a5a3a"), 6)         # a tree he dived into
    style.block(ctx, 130, 420, 460, 360, 80, hexc("#3fae4a"), 7)
    legs_out(ctx, 360, 440, 1.0, T, vis=1.25)
    st.check_mark(ctx, 570, 820, 70, (T - 66.58) / 0.2)
    label(ctx, "TREE!", 330, 230, 80, fg=st.GREEN, scale=pop(T - 66.58) if T >= 66.58 else 0.0)


def s_test2(ctx, t, d):
    T = 66.9 + t
    st.burst(ctx, T, "#c4f0b0", "#2e9c46", cy=640)
    rows = ["TREES", "PIPES", "WALLS", "MAILBOX"]
    ks = [T - (66.95 + i * 0.25) for i in range(4)]
    st.clipboard(ctx, 320, 300, 1.05, rows, T, k_rows=ks)
    oliver(ctx, 490, 1000, 0.8, "smug", T, arms=("down", "show"))
    label(ctx, "STUCK TESTS", 330, 220, 58, bg=st.BLUE, scale=pop(T - 67.44) if T >= 67.44 else 0.0)


def s_crazy(ctx, t, d):
    T = 68.06 + t
    st.burst(ctx, T, "#e2c8ff", "#7a3fd8", cy=560, spin=0.5)
    closeup(ctx, DEV, keyed(T, [(0, "neutral"), (68.5, "shock")]), T, arms=("up", "up"))
    style.shake_lines(ctx, 360, 560, 260, 240, T)
    label(ctx, "CRAZY PART", 360, 250, 72, fg=st.YELLOW, scale=pop(T - 68.5) if T >= 68.5 else 0.0)


def s_hired(ctx, t, d):
    T = 69.18 + t
    st.office(ctx, T)
    DEV.draw(ctx, 520, 1150, 1.2, "happy", T, arms=("point", "down"), look=-0.6)
    oliver(ctx, 210, 1150, 1.2, keyed(T, [(0, "shock"), (69.76, "stars")]), T, arms=("down", "point"), look=0.6)
    st.stamp(ctx, 360, 520, "HIRED!", T - 69.76, col=st.GREEN, size=100)
    if T >= 69.76:
        st.confetti(ctx, T, 69.76, n=30, seed=7)


def s_tester(ctx, t, d):
    T = 70.5 + t
    st.burst(ctx, T, "#bfe3ff", "#2f6bd8", cy=560)
    closeup(ctx, OLIVER, keyed(T, [(0, "grin"), (70.75, "smug")]), T, arms=("down", "show"))
    if T >= 70.75:
        st.staff_badge(ctx, 360, 960, 1.6 * pop(T - 70.75), txt="TESTER")
    st.sparkles(ctx, T, 360, 600, spread=300, n=10, seed=8, c=st.YELLOW)
    label(ctx, "GAME TESTER", 360, 250, 70, fg=st.YELLOW, scale=pop(T - 70.75) if T >= 70.75 else 0.0)


def s_job(ctx, t, d):
    T = 71.43 + t
    st.office(ctx, T)
    oliver(ctx, 240, 1000, 1.15, "smirk", T, arms=("down", "hold"))
    st.clipboard(ctx, 440, 560, 0.6, ["STUCK?"], T, k_rows=[None])
    label(ctx, "HIS JOB?", 360, 270, 84, fg=st.YELLOW, scale=pop(T - 71.63) if T >= 71.63 else 0.0)


def s_purpose(ctx, t, d):
    T = 72.06 + t
    world(ctx, T, 1000)
    st.brick_wall(ctx, 430, 1080, 340, 640)
    if T < 72.32:
        p = (T - 72.06) / 0.26
        oliver(ctx, lerp(150, 300, p), 1000, 1.0, "determined", T, pose="run", walk_phase=T * 3, look=0.6, tag=False)
    else:
        st.impact_star(ctx, 470, 790, 80, T - 72.32)
        legs_out(ctx, 900, 440, 1.15, T, side="left", vis=1.4, kick=1.5)
        st.check_mark(ctx, 220, 600, 80, (T - 72.67) / 0.2)
    label(ctx, "ON PURPOSE", 360, 260, 62, bg=st.GREEN, scale=pop(T - 72.67) if T >= 72.67 else 0.0)


def s_guess(ctx, t, d):
    T = 73.31 + t
    st.burst(ctx, T, "#ffe27a", "#ff8a3d", cy=560)
    closeup(ctx, DEV, keyed(T, [(0, "smirk"), (73.54, "wink")]), T, arms=("down", "point"))
    label(ctx, "GUESS WHAT?", 360, 250, 64, fg=(1, 1, 1), scale=pop(T - 73.54) if T >= 73.54 else 0.0)


def s_best(ctx, t, d):
    T = 74.08 + t
    st.office(ctx, T)

    def portrait(c, px, py, pw, ph):
        OLIVER.draw(c, px + pw / 2, py + ph + 560, 3.0, keyed(T, [(0, "grin"), (74.47, "stars")]), T, shadow=False,
                    bob=0.35)
    st.employee_frame(ctx, 345, 640, 1.0, T, portrait=portrait, k=T - 74.1)
    st.confetti(ctx, T, 74.47, n=40, seed=12)
    if T >= 74.47:
        st.sparkles(ctx, T, 360, 600, spread=320, n=12, seed=2, c=st.YELLOW, size=22)
    label(ctx, "BEST EVER", 360, 205, 76, fg=st.YELLOW, scale=pop(T - 74.47) if T >= 74.47 else 0.0)


# ================================================================ shots
S = []


def shot(start, draw, keys, **kw):
    kw.setdefault("vignette", 0.15)
    S.append(dict(start=start, draw=draw, keys=keys, **kw))


def punch(t0, z0, c0, t_key, z1, c1, m=0.16):
    return [(t0, z0, c0), (t_key, z1, c1, m)]


C = (360, 700)
CU = dict(closeup=True, keep=FACE_KEEP)
LBL = (60, 170, 660, 340)                       # the label band at the top

shot(0.00, s_hook, [(0.0, 1.3, (360, 600)), (0.12, 1.0, (360, 680), 0.12), (0.36, 1.12, (360, 620), 0.1)],
     shake=(0.36, 12), closeup=True, keep=[(110, 180, 610, 760), (50, 740, 590, 860)])
shot(0.86, s_teaser(s_onsale, 1.1), punch(0.86, 1.08, C, 0.9, 1.12, (360, 660), 0.1), shake=(0.0, 8), **CU)
shot(1.21, s_teaser(s_stuck, 1.0), punch(1.21, 1.06, (360, 760), 1.25, 1.1, (360, 760), 0.1), shake=(0.0, 8))
shot(1.56, s_button, punch(1.56, 1.0, (360, 720), 1.91, 1.08, (360, 720), 0.14), shake=(0.1, 10),
     keep=[(70, 560, 560, 1000)])
shot(2.76, s_named, punch(2.76, 1.0, C, 3.29, 1.1, (360, 660), 0.12), **CU)
shot(3.84, s_explore, [(3.84, 1.0, (300, 760)), (4.97, 1.06, (420, 760), 1.1)])
shot(4.97, s_corners, punch(4.97, 1.0, (330, 620), 5.85, 1.03, (330, 620), 0.3), closeup=True,
     keep=[(45, 222, 585, 998)])
shot(6.43, s_problem, punch(6.43, 1.0, C, 6.58, 1.1, (360, 660), 0.12), **CU)
shot(7.09, s_getinto, punch(7.09, 1.0, (360, 760), 7.7, 1.08, (360, 780), 0.14), shake=(0.36, 8), closeup=True,
     keep=[(200, 560, 520, 1010)])
shot(8.31, s_never, punch(8.31, 1.0, C, 8.72, 1.12, (360, 660), 0.12), shake=(0.41, 8), **CU)
shot(9.59, s_vend_crawl, [(9.59, 1.0, (330, 760)), (10.75, 1.1, (400, 740), 0.15)], closeup=True, keep=[(40, 340, 595, 1000)])
shot(11.45, s_chips, punch(11.45, 1.0, C, 11.61, 1.08, (360, 680), 0.12), keep=[(110, 420, 600, 1000)])
shot(12.40, s_onsale, punch(12.40, 1.0, C, 13.24, 1.12, (360, 680), 0.12), shake=(0.84, 7), **CU)
shot(13.72, s_bought, punch(13.72, 1.0, (360, 760), 14.37, 1.06, (380, 740), 0.15), keep=[(110, 340, 670, 1000)])
shot(14.78, s_gotoliver, punch(14.78, 1.0, (360, 760), 15.58, 1.1, (420, 760), 0.14), shake=(0.35, 7), closeup=True,
     keep=[(60, 420, 595, 1005)])
shot(16.10, s_pull, punch(16.10, 1.0, (360, 760), 16.92, 1.1, (300, 780), 0.12), shake=(0.82, 9), closeup=True,
     keep=[(40, 700, 600, 1010)])
shot(17.13, s_swap, punch(17.13, 1.0, (380, 740), 17.74, 1.1, (430, 700), 0.14), keep=[(195, 290, 595, 1000)])
shot(18.70, s_obby, punch(18.70, 1.0, (360, 760), 19.32, 1.08, (240, 760), 0.14))
shot(19.97, s_jump, [(19.97, 1.0, (360, 700)), (20.57, 1.1, (400, 680), 0.14)])
shot(21.16, s_gap, punch(21.16, 1.0, (360, 760), 21.6, 1.14, (360, 760), 0.14), shake=(0.4, 8),
     closeup=True, keep=[(200, 640, 520, 900)])
shot(23.13, s_guys, punch(23.13, 1.0, C, 23.15, 1.1, (360, 660), 0.1), shake=(0.03, 8), **CU)
shot(23.69, s_secret, punch(23.69, 1.0, (360, 760), 24.08, 1.08, (360, 760), 0.14), keep=[(100, 690, 650, 1000)])
shot(24.86, s_notroom, punch(24.86, 1.0, C, 25.12, 1.08, (360, 700), 0.12), shake=(0.26, 8))
shot(25.79, s_floor, punch(25.79, 1.0, (360, 700), 26.17, 1.08, (360, 720), 0.12), closeup=True, keep=[(45, 300, 595, 925)])
shot(26.68, s_wave, [(26.68, 1.0, (360, 760)), (27.78, 1.12, (360, 780), 1.0)], overlay=rec_overlay,
     keep=[(300, 700, 420, 820)])
shot(27.78, s_nobody, punch(27.78, 1.0, (360, 760), 27.93, 1.05, (360, 760), 0.14), closeup=True,
     keep=[(300, 700, 420, 820), (130, 400, 590, 820)])
shot(28.90, s_admin, punch(28.90, 1.0, C, 29.48, 1.12, (380, 640), 0.12), **CU)
shot(30.01, s_safe, punch(30.01, 1.0, (360, 760), 30.23, 1.08, (360, 760), 0.12), keep=[(160, 250, 650, 1000)])
shot(30.73, s_promise, punch(30.73, 1.0, C, 31.0, 1.08, (360, 660), 0.14), **CU)
shot(32.19, s_5sec, punch(32.19, 1.0, (360, 640), 32.24, 1.06, (360, 640), 0.15), keep=[(150, 430, 570, 860)])
shot(33.16, s_car, punch(33.16, 1.0, (360, 800), 33.96, 1.1, (360, 820), 0.14))
shot(34.14, s_wall, punch(34.14, 1.0, (360, 800), 34.40, 1.12, (430, 800), 0.1), shake=(0.26, 12))
shot(34.96, s_fall, [(34.96, 1.0, (380, 640)), (35.76, 1.0, (420, 760), 0.6)], closeup=True, keep=[(100, 170, 620, 900)])
shot(36.57, s_ropes, punch(36.57, 1.0, (360, 700), 37.49, 1.06, (360, 720), 0.14))
shot(37.98, s_crane, punch(37.98, 1.0, (360, 700), 38.08, 1.06, (380, 700), 0.12))
shot(38.55, s_rocket, punch(38.55, 1.0, (360, 640), 38.79, 1.06, (380, 620), 0.12), keep=[(380, 180, 595, 820)])
shot(39.69, s_explode, punch(39.69, 1.0, (360, 640), 40.16, 1.14, (420, 620), 0.1), shake=(0.47, 14), closeup=True,
     keep=[(250, 300, 680, 820)])
shot(40.81, s_twenty, punch(40.81, 1.0, (360, 640), 41.23, 1.05, (360, 640), 0.15), closeup=True, keep=[(210, 200, 510, 1010)])
shot(42.91, s_admin_fall, punch(42.91, 1.0, C, 43.31, 1.1, (360, 680), 0.14), closeup=True,
     keep=[(250, 480, 470, 760)])
shot(44.22, s_stuck, [(44.22, 1.0, (360, 760)), (45.58, 1.1, (360, 800), 1.3)])
shot(45.58, s_queue, punch(45.58, 1.0, C, 46.12, 1.1, (360, 660), 0.12), shake=(0.54, 6), **CU)
shot(46.93, s_requests, punch(46.93, 1.0, (360, 640), 47.1, 1.05, (360, 680), 0.14), keep=[(60, 170, 660, 1010)])
shot(47.76, s_beg, punch(47.76, 1.0, (360, 700), 48.21, 1.06, (360, 720), 0.14), keep=[(60, 200, 660, 530)])
shot(49.13, s_exit, punch(49.13, 1.0, (360, 700), 49.54, 1.08, (360, 680), 0.14), keep=[(240, 410, 480, 890)])
shot(50.22, s_nohelp, punch(50.22, 1.0, C, 50.88, 1.08, (400, 640), 0.12), shake=(0.66, 7))
shot(51.36, s_night, [(51.36, 1.0, (360, 760)), (52.95, 1.1, (300, 780), 1.4)])
shot(52.95, s_code, punch(52.95, 1.0, (360, 700), 54.11, 1.1, (360, 680), 0.14), keep=[(80, 470, 640, 840)])
shot(54.49, s_two, punch(54.49, 1.0, C, 54.69, 1.1, (360, 660), 0.12), **CU)
shot(55.42, s_reveal, punch(55.42, 1.0, (360, 640), 55.44, 1.1, (360, 640), 0.1), shake=(0.03, 10),
     keep=[(85, 430, 600, 670)])
shot(56.51, s_press, punch(56.51, 1.0, (360, 700), PRESS, 1.08, (380, 600), 0.14), keep=[(100, 270, 560, 520)])
shot(57.50, s_boom, punch(57.50, 1.0, (360, 760), BOOM, 1.14, (360, 720), 0.08), shake=(0.03, 16), closeup=True,
     keep=[(160, 520, 560, 1000)])
shot(58.05, s_spawn, punch(58.05, 1.0, (360, 760), 58.52, 1.08, (360, 760), 0.12))
shot(58.90, s_party, [(58.90, 1.0, (360, 760)), (60.34, 1.06, (360, 760), 1.4)])
shot(60.34, s_morning, punch(60.34, 1.0, (360, 760), 60.86, 1.06, (320, 760), 0.15))
shot(61.60, s_resets, punch(61.60, 1.0, (360, 700), 62.09, 1.1, (360, 660), 0.12), closeup=True, keep=[(80, 420, 600, 900)])
shot(63.15, s_same, punch(63.15, 1.0, (360, 640), 63.66, 1.06, (320, 660), 0.14), keep=[(60, 200, 660, 1020)])
shot(64.35, s_hobby, punch(64.35, 1.0, C, 64.91, 1.1, (380, 640), 0.12), **CU)
shot(66.14, s_test1, punch(66.14, 1.0, (360, 760), 66.58, 1.06, (360, 740), 0.12), closeup=True, keep=[(130, 160, 600, 1010)])
shot(66.90, s_test2, punch(66.90, 1.0, (360, 700), 67.44, 1.05, (360, 680), 0.14), keep=[(100, 280, 545, 760)])
shot(68.06, s_crazy, punch(68.06, 1.0, C, 68.5, 1.12, (360, 640), 0.1), shake=(0.44, 8), **CU)
shot(69.18, s_hired, punch(69.18, 1.0, (360, 760), 69.76, 1.08, (360, 740), 0.12), shake=(0.58, 8))
shot(70.50, s_tester, punch(70.50, 1.0, C, 70.75, 1.08, (360, 700), 0.12), closeup=True,
     keep=[(165, 300, 555, 1010)])
shot(71.43, s_job, punch(71.43, 1.0, (360, 760), 71.63, 1.08, (340, 760), 0.12))
shot(72.06, s_purpose, punch(72.06, 1.0, (360, 760), 72.32, 1.1, (380, 780), 0.1), shake=(0.26, 10), closeup=True,
     keep=[(150, 440, 595, 1000)])
shot(73.31, s_guess, punch(73.31, 1.0, C, 73.54, 1.1, (360, 660), 0.12), **CU)
shot(74.08, s_best, punch(74.08, 1.0, (360, 680), 74.47, 1.08, (360, 660), 0.14), closeup=True, keep=[(115, 360, 575, 920)])
SHOTS = S
_rw_draw, _rw_ov = st.rewind_shot(SHOTS, [72.6, 59.4, 40.3, 23.9, 12.9, 0.0])
shot(75.30, _rw_draw, [(75.30, 1.0, (360, 640))], overlay=_rw_ov, blur=False, closeup=True, keep=[])
for k, s in enumerate(SHOTS):
    s["end"] = SHOTS[k + 1]["start"] if k + 1 < len(SHOTS) else TOTAL

# ---------------------------------------------------------------- SFX (time, file, volume before SFX_GAIN)
SFX = [
    (0.03, "boom.wav", 1.3), (0.36, "hit.wav", 1.3), (0.6, "pop.wav", 0.6), (0.9, "pop.wav", 0.6),
    (1.21, "pop.wav", 0.7), (1.66, "boom.wav", 1.6), (1.91, "ding.wav", 0.7), (2.41, "click.wav", 1.0),
    (2.43, "pop.wav", 0.9), (2.5, "sparkle.wav", 0.6), (3.29, "ding.wav", 0.8), (4.47, "pop.wav", 0.7),
    (4.99, "pop.wav", 0.7), (5.33, "pop.wav", 0.7), (5.6, "pop.wav", 0.7), (5.85, "pop.wav", 0.7),
    (6.58, "sting_low.wav", 0.8), (7.15, "swish.wav", 0.6), (7.45, "boing.wav", 0.7), (7.7, "ding.wav", 0.8),
    (8.72, "buzz.wav", 0.9), (9.11, "hit.wav", 1.1), (10.35, "swish.wav", 0.6), (10.75, "hit.wav", 1.1),
    (11.61, "chaching.wav", 0.8), (12.5, "hit.wav", 0.8), (12.75, "hit.wav", 0.8), (13.24, "ding.wav", 0.9),
    (13.9, "coin.wav", 0.8), (14.19, "chaching.wav", 0.8), (15.13, "pop.wav", 0.9), (15.4, "boing.wav", 0.6),
    (15.58, "hit.wav", 1.1), (16.92, "pop.wav", 1.0), (16.95, "boom.wav", 1.2), (17.74, "hit.wav", 1.3),
    (18.0, "ding.wav", 0.6), (18.97, "sparkle.wav", 0.8), (19.32, "pop.wav", 0.6), (19.8, "pop.wav", 0.8), (20.05, "boing.wav", 0.7),
    (20.57, "whoosh.wav", 0.6), (20.6, "pop.wav", 0.6), (21.4, "hit.wav", 1.0), (21.6, "pop.wav", 0.8),
    (23.15, "hit.wav", 1.0), (23.71, "sparkle.wav", 0.7), (24.08, "ding.wav", 0.7), (25.12, "buzz.wav", 1.0),
    (25.37, "hit.wav", 1.1), (26.17, "boing.wav", 0.8), (26.75, "click.wav", 0.6), (27.14, "pop.wav", 0.6),
    (27.93, "pop.wav", 0.6), (28.2, "pop.wav", 0.6), (29.48, "sparkle.wav", 0.9), (29.5, "hit.wav", 1.0),
    (30.08, "pop.wav", 0.8), (30.23, "success.wav", 0.8), (31.0, "ding.wav", 0.7), (32.24, "hit.wav", 1.3),
    (32.83, "tick.wav", 0.6), (33.2, "whoosh.wav", 0.6), (33.6, "pop.wav", 0.7), (34.4, "boom.wav", 1.6),
    (34.5, "hit.wav", 1.2), (35.0, "whoosh.wav", 0.6), (35.65, "pop.wav", 0.7), (36.2, "boom.wav", 1.2),
    (37.49, "pop.wav", 0.8), (38.08, "hit.wav", 1.0), (38.3, "click.wav", 0.6), (38.79, "boom.wav", 1.2),
    (39.75, "whoosh.wav", 0.6), (40.16, "boom.wav", 1.6), (40.2, "hit.wav", 1.3), (41.23, "ding.wav", 0.8),
    (43.31, "hit.wav", 1.2), (43.76, "boing.wav", 0.6), (44.6, "sting_low.wav", 0.8), (45.18, "hit.wav", 1.1),
    (46.37, "buzz.wav", 0.9), (47.1, "hit.wav", 1.1), (47.85, "type_key.wav", 0.6), (48.1, "type_key.wav", 0.6),
    (48.35, "type_key.wav", 0.6), (48.6, "pop.wav", 0.8), (49.26, "ding.wav", 0.8), (50.26, "pop.wav", 0.6),
    (50.88, "buzz.wav", 1.0), (51.63, "pop.wav", 0.7), (53.0, "type_key.wav", 0.6), (53.3, "type_key.wav", 0.6),
    (53.63, "type_key.wav", 0.6), (54.11, "ding.wav", 0.9), (54.69, "pop.wav", 0.8), (55.44, "boom.wav", 1.5),
    (55.5, "sparkle.wav", 0.8), (PRESS, "click.wav", 1.1), (BOOM, "boom.wav", 1.6), (BOOM + 0.05, "hit.wav", 1.3),
    (BACK, "sparkle.wav", 0.8), (58.52, "success.wav", 0.8), (58.95, "pop.wav", 0.6), (59.27, "pop.wav", 0.8),
    (59.6, "bell.wav", 0.6), (60.55, "pop.wav", 0.7), (61.7, "tick.wav", 0.6), (62.09, "hit.wav", 1.2),
    (62.71, "chaching.wav", 0.6), (63.66, "hit.wav", 1.1), (64.91, "ding.wav", 0.9), (65.4, "pop.wav", 0.8),
    (66.2, "swish.wav", 0.6), (66.58, "ding.wav", 0.8), (66.95, "pop.wav", 0.6), (67.2, "pop.wav", 0.6),
    (67.45, "pop.wav", 0.6), (67.7, "pop.wav", 0.6), (68.5, "sting_low.wav", 0.9), (68.52, "hit.wav", 1.1),
    (69.76, "boom.wav", 1.3), (69.8, "success.wav", 0.7), (70.75, "sparkle.wav", 0.8), (71.0, "pop.wav", 0.6),
    (71.63, "pop.wav", 0.8), (72.1, "swish.wav", 0.6), (72.32, "hit.wav", 1.3), (72.67, "ding.wav", 0.8),
    (73.54, "pop.wav", 0.7), (74.1, "pop.wav", 0.7), (74.47, "success.wav", 0.9), (74.85, "sparkle.wav", 0.7),
    (75.3, "whip.wav", 0.9),
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

"""Long-video thumbnail (16:9, 1920x1080): "What If the WHOLE SCHOOL Became Roblox? 😱" (story whole_school).

thumbnail_dna.md section 9, family L1 "Crossover split":
  background  split at a glowing seam: a plain grey everyday school (left) | the red studded Roblox school (right)
  subject     our KID big in the middle, shocked + sweat; the half of him past the seam is turning into studded
              blocks that break off into flying cubes
  easter egg  THE FINAL EXAM (the boss of the video) peeking over the Roblox roof, angry
  text        SCHOOL IS (white, navy outline) / ROBLOX?! (gold), top centre
  safe area   nothing important in the bottom-right 15 % (the duration badge)
Drawn in the 1280x720 world of the long video (school_sets.py) scaled 1.5x.
Run (from animator/):  python3 thumb_whole_school.py"""
import os
os.environ["STYLEB_ASPECT"] = "16x9"
import math    # noqa: E402

import school_sets as ss   # noqa: E402
import sets as st          # noqa: E402
import style               # noqa: E402
import thumbkit as tk      # noqa: E402
from engine import hexc     # noqa: E402
from style import Block    # noqa: E402

TITLE = "What If the WHOLE SCHOOL Became Roblox? 😱"
KID = style.KID
T = 0.42
U1 = Block.HW * 64
SEAM = 690                       # world x of the real | Roblox seam
SCHOOL_S = 0.5
GROUND = ss.GROUND
WHITE = [(0.0, "#ffffff"), (1.0, "#eef3ff")]
NAVY = (0.12, 0.16, 0.36)
tk.landscape()


def world(ctx):
    ctx.scale(1.5, 1.5)


def normal_school(ctx, cx=640, s=1.0):
    ctx.save()
    ctx.translate(cx, GROUND)
    ctx.scale(s, s)
    style.block(ctx, -560, -420, 1120, 420, 4, hexc("#c8bfae"), 5, gloss=False)
    style.block(ctx, -150, -560, 300, 160, 4, hexc("#b8af9e"), 5, gloss=False)
    for row in range(2):
        for i in (-4, -3, -2, 2, 3, 4):
            style.block(ctx, i * 110 - 40, -360 + row * 150, 80, 90, 2, hexc("#8fa3b8"), 3, gloss=False)
    style.block(ctx, -95, -230, 190, 230, 4, hexc("#7a5a3a"), 5, gloss=False)
    ctx.restore()


def background(ctx):
    world(ctx)
    ctx.save()                                                         # the real side
    ctx.rectangle(-100, -100, SEAM + 100, 900)
    ctx.clip()
    st.game_sky(ctx, top="#9fd3f5", bottom="#e8f4fb")
    ctx.new_sub_path()
    ctx.arc(150, 110, 60, 0, 2 * math.pi)
    style.shape_fill(ctx, hexc("#ffd84a"), 5, 50, 170)
    st.baseplate(ctx, GROUND, col="#7ab85a")
    normal_school(ctx, cx=230, s=SCHOOL_S)
    for tx in (520, 620):                                                # trees on the everyday side
        style.block(ctx, tx - 12, GROUND - 120, 24, 120, 4, hexc("#8a5a3a"), 4, gloss=False)
        ctx.new_sub_path()
        ctx.arc(tx, GROUND - 170, 70, 0, 2 * math.pi)
        style.shape_fill(ctx, hexc("#4fae4a"), 5, GROUND - 240, GROUND - 100)
    ctx.restore()
    ctx.save()                                                         # the Roblox side
    ctx.rectangle(SEAM, -100, 1400, 900)
    ctx.clip()
    ss.school_ext(ctx, T, cx=1050, s=SCHOOL_S)
    style.block(ctx, 1080, 60, 120, 120, 14, hexc("#ffe27a"), 6)       # a cube sun
    st.glow(ctx, 1140, 120, 200, (1, 0.95, 0.6), 0.5)
    ctx.restore()
    st.glow(ctx, SEAM, 360, 260, (1, 1, 0.9), 0.85)                     # the glowing seam
    ctx.set_source_rgba(1, 1, 1, 0.9)
    ctx.rectangle(SEAM - 10, -100, 20, 1000)
    ctx.fill()
    st.sparkles(ctx, T, SEAM, 380, spread=260, n=14, seed=5, c=(1, 1, 1))


def boss(ctx):
    world(ctx)
    ctx.save()
    ctx.rectangle(1100, -100, 400, GROUND - 420 * SCHOOL_S + 100)      # peeking over the roof
    ctx.clip()
    ss.exam_boss(ctx, 1200, 640, 0.36, T, jaw=0.7, rage=1.0)
    ctx.restore()


def kid(ctx):
    world(ctx)
    s, x, feet = 2.4, 580, 1000

    def draw(c):
        KID.draw(c, x, feet, s, "shock", T, arms=("down", "up"), bob=0.0, shadow=False)
    draw(ctx)
    ctx.push_group()                                                    # his silhouette, used as a mask
    draw(ctx)
    body = ctx.pop_group()
    ctx.push_group()                                                    # studs on the half past the seam
    ctx.rectangle(SEAM, -100, 900, 1000)
    ctx.clip()
    for yy in range(70, 760, 30):
        for xx in range(SEAM + 14, 1000, 30):
            ctx.new_sub_path()
            ctx.arc(xx, yy, 7.5, 0, 2 * math.pi)
    ctx.set_source_rgba(1, 1, 1, 0.5)
    ctx.fill()
    ctx.rectangle(SEAM - 3, -100, 6, 1000)
    ctx.set_source_rgba(1, 1, 1, 0.9)
    ctx.fill()
    dots = ctx.pop_group()
    ctx.set_source(dots)
    ctx.mask(body)
    style.sweat(ctx, x + 150, feet - 2.5 * U1 * s - 70, 2.0, T)


def cubes(ctx):
    world(ctx)
    cols = ("#ff4f5a", "#4f8bff", "#4fd16a", "#ffd84a", "#9d5cff", "#ff8a3d", "#2fbf8f")
    pts = ((780, 330, 46, 0.3), (850, 270, 34, -0.5), (900, 360, 28, 0.8), (820, 430, 30, 1.2), (930, 290, 22, 0.1),
           (960, 420, 20, 0.6), (760, 230, 24, 1.4), (1000, 340, 18, -0.2))
    for i, (x, y, sz, rot) in enumerate(pts):
        ctx.save()
        ctx.translate(x, y)
        ctx.rotate(rot)
        style.block(ctx, -sz / 2, -sz / 2, sz, sz, 5, hexc(cols[i % len(cols)]), 4)
        ctx.new_sub_path()
        ctx.arc(0, -sz * 0.15, sz * 0.2, 0, 2 * math.pi)
        ctx.set_source_rgba(1, 1, 1, 0.5)
        ctx.fill()
        ctx.restore()


def text(ctx):
    tk.headline(ctx, "SCHOOL IS", 960, 120, 150, fill=WHITE, outline=NAVY, tilt=-0.03, max_w=1100, arc=0.03)
    tk.headline(ctx, "ROBLOX?!", 968, 285, 210, fill=tk.GOLD, tilt=-0.03, max_w=1150, arc=0.03)


def main():
    surf, ctx = tk.new()
    ctx.save()
    background(ctx)
    ctx.restore()
    tk.sticker(ctx, tk.layer(boss), r=14)
    tk.sticker(ctx, tk.layer(kid), r=18)
    tk.sticker(ctx, tk.layer(cubes), r=8)
    text(ctx)
    print(tk.save(surf, TITLE))


if __name__ == "__main__":
    main()

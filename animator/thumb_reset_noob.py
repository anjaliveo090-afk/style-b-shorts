"""Thumbnail: "This Noob Is the REASON Roblox Has a Reset Button... 😭" (story reset_noob), thumbnail_dna.md.

Family A (antagonist + shocked kid):
  subject   Oliver the noob, huge in the middle, stuck chest-deep in the floor, crying (the 😭 of the title)
  kid       our KID, shocked, bottom-left over the panel edge
  proof     the RESET CHARACTER button with a cursor about to click it, red circle (the "reason" of the title;
            not pressed: the ending stays open)
  burst     purple-pink (absurd)
  text      STUCK (punch word, cream) / FOREVER?! (gold): the premise, as a shocked question
Run (from animator/):  python3 thumb_reset_noob.py"""
import math

from engine import PI

import sets as st
import style
import thumbkit as tk
from style import Block

TITLE = "This Noob Is the REASON Roblox Has a Reset Button... 😭"
OLIVER = Block("#1a68cf", pants="#9bbc36", skin="#e9c22c", hair=None, sleeves="skin", shoes=None, cap="#ff7a1a")
KID = style.KID
T = 0.42            # a frozen moment of the idle motion (arms/eyes)
FLOOR_Y = 1350


def background(ctx):
    st.burst(ctx, 1.3, "#ff8ad8", "#7a2fd0", cx=540, cy=900, n=22, spin=0.0, glow_a=0.75)
    st.glow(ctx, 540, 900, 700, (1.0, 0.85, 0.98), 0.55)


def teardrop(ctx, x, y, r, ang):
    ctx.save()
    ctx.translate(x, y)
    ctx.rotate(ang)
    ctx.move_to(0, -r * 2.1)
    ctx.curve_to(r * 0.9, -r * 0.6, r, 0, r, r * 0.2)
    ctx.arc(0, r * 0.2, r, 0, PI)
    ctx.curve_to(-r, 0, -r * 0.9, -r * 0.6, 0, -r * 2.1)
    ctx.close_path()
    style.shape_fill(ctx, style.TEAR, max(3, r * 0.14), -r * 2.1, r * 1.2, outline=style.col("#2f8fd8"))
    ctx.restore()


def oliver(ctx):
    s = 5.0
    u = Block.HW * 64 * s
    OLIVER.draw(ctx, 540, 930 + 2.5 * u, s, "cry", T, arms=("up", "up"), bob=0.0, shadow=False)
    for side in (-1, 1):                              # 😭 tear streams down both cheeks + a drop flying off
        x = 540 + side * 0.2 * u
        w = 0.11 * u
        ctx.move_to(x - w / 2, 965)
        ctx.line_to(x - w / 2, 1120)
        ctx.curve_to(x - w / 2, 1150, x + w / 2, 1150, x + w / 2, 1120)
        ctx.line_to(x + w / 2, 965)
        ctx.close_path()
        style.shape_fill(ctx, style.TEAR, 6, 965, 1150, outline=style.col("#2f8fd8"))
        ctx.move_to(x - w * 0.15, 985)
        ctx.line_to(x - w * 0.15, 1100)
        ctx.set_source_rgba(1, 1, 1, 0.6)
        ctx.set_line_width(7)
        ctx.stroke()
        teardrop(ctx, 540 + side * 0.5 * u, 900, 22, side * 1.1)
    style.sweat(ctx, 800, 760, 2.4, T)
    style.shake_lines(ctx, 540, 900, 400, 340, T, n=3, lw=10)
    # the floor he is stuck in (grass + dirt, cracks round him)
    style.block(ctx, -40, FLOOR_Y, 1160, 70, 14, style.col("#51c844"), 8)
    style.block(ctx, -40, FLOOR_Y + 66, 1160, 700, 0, style.col("#9a6a3c"), 8, gloss=False)
    ctx.set_source_rgb(*style.col("#3a8a2e"))
    ctx.set_line_width(9)
    for x, d in ((290, -1), (360, 1), (720, 1), (790, -1)):
        ctx.move_to(x, FLOOR_Y + 4)
        ctx.line_to(x + d * 30, FLOOR_Y + 40)
        ctx.line_to(x + d * 10, FLOOR_Y + 66)
        ctx.stroke()


def kid(ctx):
    s = 3.5
    u = Block.HW * 64 * s
    KID.draw(ctx, 185, 1590 + 2.5 * u, s, "shock", T, arms=("up", "down"), look=0.5, bob=0.0, shadow=False)
    style.sweat(ctx, 330, 1430, 1.6, T)


def button(ctx):
    st.reset_button(ctx, 800, 1590, 0.74, T, glow_a=0.0)
    st.cursor(ctx, 860, 1600, 3.4)


def help_sticker(ctx):
    ctx.save()
    ctx.translate(870, 770)
    ctx.rotate(0.16)
    style.block(ctx, -150, -62, 300, 124, 50, (1, 1, 1), 8, outline=style.INK)
    ctx.move_to(-70, 55)
    ctx.line_to(-120, 120)
    ctx.line_to(-20, 58)
    ctx.close_path()
    style.shape_fill(ctx, (1, 1, 1), 8, 55, 120, outline=style.INK)
    style.block(ctx, -144, -56, 288, 112, 46, (1, 1, 1), 0, outline=(1, 1, 1), gloss=False)
    ctx.restore()
    tk.headline(ctx, "HELP!", 868, 770, 78, fill="#ff3b4a", outline=style.INK, white=False, tilt=0.16)


def text(ctx):
    tk.headline(ctx, "STUCK", 540, 300, 250, fill=tk.CREAM, tilt=-0.05, max_w=860, arc=0.05)
    tk.headline(ctx, "FOREVER?!", 548, 520, 150, fill=tk.GOLD, tilt=-0.05, max_w=880, arc=0.04)


def main():
    surf, ctx = tk.new()
    background(ctx)
    tk.sticker(ctx, tk.layer(oliver), r=18)
    tk.sticker(ctx, tk.layer(help_sticker), r=12)
    tk.sticker(ctx, tk.layer(button), r=16)
    tk.red_ring(ctx, 800, 1585, 255, 150, w=20)
    tk.sticker(ctx, tk.layer(kid), r=18)
    text(ctx)
    print(tk.save(surf, TITLE))


if __name__ == "__main__":
    main()

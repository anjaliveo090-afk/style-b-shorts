"""Thumbnail: "What If Your Roblox Time Was Only 10 SECONDS?" (the improved 10-seconds script), thumbnail_dna.md.

Family B (giant kid face + proof), because the subject is "you" with a time limit. It is built differently
from the user's earlier "10 Seconds" thumbnail (mom holding a clock), so the two do not look like a repeat:
  subject   our KID's face filling ~80 % of the width, screaming, sweat, shake lines, holding a tablet
  proof     the Roblox-style countdown pill on the tablet, red "0:10", circled in red (the stake)
  extra     a big Robux icon flying off the tablet (what he is about to lose) - no ending shown
  burst     orange-red (time and money)
  text      ONLY 10 (cream, punch number) / SECONDS?! (gold)
Run (from animator/):  python3 thumb_ten_seconds.py"""
import sets as st
import style
import thumbkit as tk
from engine import PI
from style import Block

TITLE = "What If Your Roblox Time Was Only 10 SECONDS?"
KID = style.KID
T = 0.42
S = 8.4                          # the kid's Block scale: the head is ~780 px wide
U = Block.HW * 64 * S
HEAD_Y = 1080                    # head centre


def background(ctx):
    st.burst(ctx, 1.3, "#ffd27a", "#ff4a1a", cx=540, cy=1000, n=22, spin=0.0, glow_a=0.7)
    st.glow(ctx, 540, 1050, 760, (1.0, 0.9, 0.7), 0.5)


def kid(ctx):
    KID.draw(ctx, 540, HEAD_Y + 2.5 * U, S, "scream", T, arms=("down", "down"), bob=0.0, shadow=False)


def tablet(ctx):
    """The tablet he holds up at the bottom, its game screen showing the countdown pill."""
    def screen(c, x, y, w, h, TT):
        st.game_sky(c)
        st.baseplate(c, y + h * 0.72)
        c.save()
        c.translate(x + w / 2, y + h * 0.4)
        c.scale(1.6, 1.6)
        c.translate(-360, -180)
        st.hud_timer(c, "0:10", urgent=True, y=180)
        c.restore()
    ctx.save()
    ctx.translate(540, 1690)
    ctx.rotate(-0.05)
    ctx.scale(1.55, 1.55)
    ctx.translate(-540, -1690)
    st.tablet(ctx, 540, 1690, 1.0, T, fn=screen)
    ctx.restore()
    for side in (-1, 1):                              # his hands gripping the tablet's sides
        style.block(ctx, 540 + side * 345 - 55, 1610, 110, 150, 34, style.col("#e6ddd6"), 7)


def robux_flying(ctx):
    st.robux(ctx, 905, 760, 2.3, spin=0.5)
    st.robux(ctx, 160, 820, 1.6, spin=-0.7)


def text(ctx):
    tk.headline(ctx, "ONLY 10", 540, 290, 250, fill=tk.CREAM, tilt=-0.05, max_w=900, arc=0.05)
    tk.headline(ctx, "SECONDS?!", 548, 520, 160, fill=tk.GOLD, tilt=-0.05, max_w=900, arc=0.04)


def main():
    surf, ctx = tk.new()
    background(ctx)
    tk.sticker(ctx, tk.layer(kid), r=18)
    tk.sticker(ctx, tk.layer(robux_flying), r=12)
    tk.sticker(ctx, tk.layer(tablet), r=16)
    tk.red_ring(ctx, 535, 1652, 285, 118, w=20)
    text(ctx)
    print(tk.save(surf, TITLE))


if __name__ == "__main__":
    main()

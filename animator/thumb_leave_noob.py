"""Thumbnail: "This Noob Is the REASON Roblox Has a Leave Button... 😭" (story leave_noob), thumbnail_dna.md.

Family A (subject + shocked kid), the same series layout as the reset / friend-limit / chat-filter noob thumbnails:
  subject   Toby the noob, huge in the middle, over-friendly crazy grin, waving, party hat, a bunch of balloons
            (the "make every player feel welcome" noob)
  kid       our KID, shocked, bottom-left over the panel edge
  proof     the Roblox LEAVE GAME button with a cursor about to click it, red circle (the "reason" of the title;
            not pressed: the ending stays open)
  burst     blue (the empty server), new for the series after purple / green / red-orange
  text      EVERYONE (cream) / LEFT?! (gold, the punch)
Run (from animator/):  python3 thumb_leave_noob.py"""
import sets as st
import style
import thumbkit as tk
from style import Block

TITLE = "This Noob Is the REASON Roblox Has a Leave Button... 😭"
TOBY = Block("#22b8c8", pants="#9bbc36", skin="#e9c22c", hair=None, sleeves="skin", shoes=None)
KID = style.KID
T = 0.42
U1 = Block.HW * 64
BTN = (770, 1600, 0.74)                 # leave button x, y, scale


def background(ctx):
    st.burst(ctx, 1.3, "#c4e4ff", "#1f5fd0", cx=540, cy=900, n=22, spin=0.0, glow_a=0.75)
    st.glow(ctx, 540, 900, 700, (0.85, 0.93, 1.0), 0.55)


def balloons(ctx):
    st.balloons(ctx, 330, 1330, 1.55, T, n=5, seed=3, lean=-0.3)


def toby(ctx):
    s = 4.2
    hy = 1080                                      # head centre: the hat tip stays below the headline
    TOBY.draw(ctx, 540, hy + 2.5 * U1 * s, s, "crazy", T, arms=("down", "wave"), bob=0.0, shadow=False)
    ctx.save()
    ctx.translate(540, hy - 0.5 * U1 * s)
    ctx.rotate(-0.15)
    st.party_hat(ctx, 0, 0, 0.0042 * U1 * s, col="#ff5fb0")
    ctx.restore()


def kid(ctx):
    s = 3.3
    u = U1 * s
    KID.draw(ctx, 168, 1610 + 2.5 * u, s, "shock", T, arms=("up", "down"), look=0.5, bob=0.0, shadow=False)
    style.sweat(ctx, 300, 1460, 1.5, T)


def button(ctx):
    x, y, s = BTN
    st.leave_button(ctx, x, y, s, T, glow_a=0.0)
    st.cursor(ctx, x + 70, y + 20, 3.2)


def text(ctx):
    tk.headline(ctx, "EVERYONE", 540, 280, 200, fill=tk.CREAM, tilt=-0.05, max_w=880, arc=0.05)
    tk.headline(ctx, "LEFT?!", 548, 505, 260, fill=tk.GOLD, tilt=-0.05, max_w=880, arc=0.04)


def main():
    surf, ctx = tk.new()
    background(ctx)
    tk.sticker(ctx, tk.layer(balloons), r=12)
    tk.sticker(ctx, tk.layer(toby), r=18)
    tk.sticker(ctx, tk.layer(button), r=16)
    x, y, s = BTN
    tk.red_ring(ctx, x, y - 10, 270 * s + 40, 150 * s + 40, w=20)
    tk.sticker(ctx, tk.layer(kid), r=18)
    text(ctx)
    print(tk.save(surf, TITLE))


if __name__ == "__main__":
    main()

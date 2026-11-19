"""Thumbnail: "This Noob Is the REASON Roblox Has a Chat Filter... 😭" (story chat_filter_v2), thumbnail_dna.md.

Family A (subject + shocked kid), the same series layout as the reset / friend-limit noob thumbnails:
  subject   Benny the noob, huge in the middle, sweet innocent smile, waving, with a gold halo
            ("I'm here to help :)"): the contradiction with what he typed
  kid       our KID, shocked, bottom-left over the panel edge
  proof     the Roblox chat window with his scary messages, red circle on "I know where you live."
            (the reason for the filter; the #### ending stays hidden)
  burst     red-orange (danger), new for the series
  text      HE TYPED (cream) / WHAT?! (gold, the punch)
Run (from animator/):  python3 thumb_chat_filter.py"""
import math

import sets as st
import style
import thumbkit as tk
from style import Block

TITLE = "This Noob Is the REASON Roblox Has a Chat Filter... 😭"
BENNY = Block("#ff8a3d", pants="#2b3f8f", skin="#e9c22c", hair=None, sleeves="skin", shoes=None, cap="#ffd84a")
KID = style.KID
T = 0.42
PANEL = (486, 1470, 556, 300)          # chat window x, y, w, h
LH = 74                                # line height in the chat
LINES = [("Benny:", "I'm watching you.", "#ffd84a"),
         ("Benny:", "I know where you live.", "#ffd84a"),
         ("ObbyQueen:", "RUNNN!!", "#ff5fb0")]


def background(ctx):
    st.burst(ctx, 1.3, "#ffc46b", "#e2381f", cx=540, cy=900, n=22, spin=0.0, glow_a=0.75)
    st.glow(ctx, 540, 900, 700, (1.0, 0.93, 0.8), 0.55)


def halo(ctx, x, y, r):
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(1, 0.3)
    ctx.new_sub_path()
    ctx.arc(0, 0, r, 0, 2 * math.pi)
    ctx.restore()
    ctx.set_source_rgb(*style.col("#9a6a1c"))
    ctx.set_line_width(34)
    ctx.stroke_preserve()
    ctx.set_source_rgb(*st.GOLD)
    ctx.set_line_width(22)
    ctx.stroke()


def benny(ctx):
    s = 4.3
    u = Block.HW * 64 * s
    hy = 1030                                      # head centre: the cap stays below the headline
    BENNY.draw(ctx, 540, hy + 2.5 * u, s, "happy", T, arms=("down", "wave"), bob=0.0, shadow=False)
    halo(ctx, 540, 752, 0.6 * u)                   # just above the cap


def kid(ctx):
    s = 3.3
    u = Block.HW * 64 * s
    KID.draw(ctx, 168, 1610 + 2.5 * u, s, "shock", T, arms=("up", "down"), look=0.5, bob=0.0, shadow=False)
    style.sweat(ctx, 300, 1460, 1.5, T)


def chat(ctx):
    x, y, w, h = PANEL
    style.block(ctx, x, y, w, h, 26, style.col("#1c2132"), 8, outline=style.INK, gloss=False)
    style.block(ctx, x, y, w, 56, 26, style.col("#2c3350"), 0, outline=style.col("#2c3350"), gloss=False)
    ctx.rectangle(x, y + 30, w, 26)
    ctx.set_source_rgb(*style.col("#2c3350"))
    ctx.fill()
    st.bold_text(ctx, "Chat", x + 26, y + 29, 32, (0.85, 0.88, 0.95), align="l", shadow=False, stroke=0.0)
    size = 44                                      # one font size that fits the longest line
    while size > 20 and max(st.text_width(ctx, n, size) + size * 0.32 + st.text_width(ctx, m, size) for n, m, _ in LINES) > w - 52:
        size -= 1
    for i, (name, msg, col) in enumerate(LINES):
        yy = y + 56 + LH * (i + 0.62)
        st.bold_text(ctx, name, x + 26, yy, size, style.col(col), align="l", shadow=False, stroke=0.0)
        tx = x + 26 + st.text_width(ctx, name, size) + size * 0.32
        st.bold_text(ctx, msg, tx, yy, size, (1, 1, 1), align="l", shadow=False, stroke=0.0)


def text(ctx):
    tk.headline(ctx, "HE TYPED", 540, 280, 190, fill=tk.CREAM, tilt=-0.05, max_w=860, arc=0.05)
    tk.headline(ctx, "WHAT?!", 548, 500, 250, fill=tk.GOLD, tilt=-0.05, max_w=880, arc=0.04)


def main():
    surf, ctx = tk.new()
    background(ctx)
    tk.sticker(ctx, tk.layer(benny), r=18)
    tk.sticker(ctx, tk.layer(chat), r=14)
    x, y, w, h = PANEL
    tk.red_ring(ctx, x + w / 2, y + 56 + LH * 1.62, w * 0.55, LH * 0.62, w=14, tilt=-0.03)
    tk.sticker(ctx, tk.layer(kid), r=18)
    text(ctx)
    print(tk.save(surf, TITLE))


if __name__ == "__main__":
    main()

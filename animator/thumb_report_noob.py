"""Thumbnail: "This Noob Is the REASON Roblox Has a Report Button... 😭" (story report_noob), thumbnail_dna.md.

Family A (antagonist + kid):
  subject   Kevin the noob, huge in the middle, crazy over-friendly grin, waving; HI! spam bubbles round him
            (the story: he spammed hello a thousand times to make friends)
  kid       our KID, annoyed, bottom-left over the panel edge
  proof     the REPORT button with a cursor about to click it, red circle (the "reason" of the title;
            not pressed: the ending, Kevin reviewing reports, stays hidden)
  burst     blue (the "friend" colour: all Kevin wanted was friends)
  text      10,000 (punch number, cream) / REPORTS?! (gold): a fact from the video, as a shocked question
Run (from animator/):  python3 thumb_report_noob.py"""
import sets as st
import style
import thumbkit as tk
from style import Block

TITLE = "This Noob Is the REASON Roblox Has a Report Button... 😭"
KEVIN = Block("#1a68cf", pants="#9bbc36", skin="#e9c22c", hair=None, sleeves="skin", shoes=None)
KID = style.KID
T = 0.42
HIS = [(185, 760, 96, -0.18, (1, 1)), (900, 820, 88, 0.16, (-1, 1)), (165, 1110, 80, -0.1, (1, -1)),
       (935, 1170, 72, 0.12, (-1, -1))]


def background(ctx):
    st.burst(ctx, 1.3, "#9fe0ff", "#2456c8", cx=540, cy=900, n=22, spin=0.0, glow_a=0.75)
    st.glow(ctx, 540, 900, 700, (0.85, 0.95, 1.0), 0.55)


def kevin(ctx):
    s = 5.0
    u = Block.HW * 64 * s
    KEVIN.draw(ctx, 540, 930 + 2.5 * u, s, "crazy", T, arms=("down", "wave"), bob=0.0, shadow=False)


def hi_bubble(x, y, size, tilt, tail):
    def fn(ctx):
        st.speech_bubble(ctx, x, y, "HI!", size, 1.0, tail=tail, tilt=tilt)
    return fn


def kid(ctx):
    s = 3.5
    u = Block.HW * 64 * s
    KID.draw(ctx, 185, 1590 + 2.5 * u, s, "angry", T, arms=("up", "down"), look=0.5, bob=0.0, shadow=False)
    style.anger_mark(ctx, 320, 1420, 2.2, T)


def button(ctx):
    st.report_button(ctx, 800, 1600, 0.74, T)
    st.cursor(ctx, 860, 1610, 3.4)


def text(ctx):
    tk.headline(ctx, "10,000", 540, 300, 250, fill=tk.CREAM, tilt=-0.05, max_w=860, arc=0.05)
    tk.headline(ctx, "REPORTS?!", 548, 520, 150, fill=tk.GOLD, tilt=-0.05, max_w=880, arc=0.04)


def main():
    surf, ctx = tk.new()
    background(ctx)
    tk.sticker(ctx, tk.layer(kevin), r=18)
    for x, y, size, tilt, tail in HIS:
        tk.sticker(ctx, tk.layer(hi_bubble(x, y, size, tilt, tail)), r=10)
    tk.sticker(ctx, tk.layer(button), r=16)
    tk.red_ring(ctx, 800, 1590, 255, 150, w=20)
    tk.sticker(ctx, tk.layer(kid), r=18)
    text(ctx)
    print(tk.save(surf, TITLE))


if __name__ == "__main__":
    main()

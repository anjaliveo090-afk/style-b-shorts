"""Thumbnail: "This Noob Is the REASON Roblox Has a Friend Limit... 😭" (story friend_noob), thumbnail_dna.md.

Family A (subject + shocked kid), the same series layout as the reset / report noob thumbnails:
  subject   Milo the noob, huge in the middle, crazy over-friendly grin, waving, surrounded by friend-request cards
  kid       our KID, shocked, bottom-left over the panel edge
  proof     the Roblox "Friend Limit Reached" dialog, red circle (the "reason" of the title; the Milo_2 twist
            stays hidden)
  burst     green (the video's first frame is a green burst, so thumbnail and hook match)
  text      TOO MANY (cream) / FRIENDS?! (gold)
Run (from animator/):  python3 thumb_friend_noob.py"""
import sets as st
import style
import thumbkit as tk
from style import Block

TITLE = "This Noob Is the REASON Roblox Has a Friend Limit... 😭"
MILO = Block("#1a68cf", pants="#9bbc36", skin="#e9c22c", hair=None, sleeves="skin", shoes=None, cap="#4fd16a")
KID = style.KID
T = 0.42
NAMES = st.ROBLOX_NAMES


def background(ctx):
    st.burst(ctx, 1.3, "#c8ffb8", "#22a046", cx=540, cy=900, n=22, spin=0.0, glow_a=0.75)
    st.glow(ctx, 540, 900, 700, (0.92, 1.0, 0.9), 0.55)


def milo(ctx):
    s = 5.0
    u = Block.HW * 64 * s
    MILO.draw(ctx, 540, 930 + 2.5 * u, s, "crazy", T, arms=("down", "wave"), bob=0.0, shadow=False)
    st.name_pill(ctx, 540, 640, "Milo", size=40)


def cards(ctx):
    for x, y, s, i in ((185, 760, 0.62, 1), (895, 820, 0.62, 2), (175, 1120, 0.55, 3)):
        st.friend_card(ctx, x, y, s, NAMES[i], k=1.0, state="sent")


def kid(ctx):
    s = 3.5
    u = Block.HW * 64 * s
    KID.draw(ctx, 185, 1590 + 2.5 * u, s, "shock", T, arms=("up", "down"), look=0.5, bob=0.0, shadow=False)


def dialog(ctx):
    st.roblox_dialog(ctx, 770, 1590, 0.78, 1.0, "Friend Limit Reached", "You can't add any more friends.")


def text(ctx):
    tk.headline(ctx, "TOO MANY", 540, 290, 230, fill=tk.CREAM, tilt=-0.05, max_w=880, arc=0.05)
    tk.headline(ctx, "FRIENDS?!", 548, 510, 160, fill=tk.GOLD, tilt=-0.05, max_w=900, arc=0.04)


def main():
    surf, ctx = tk.new()
    background(ctx)
    tk.sticker(ctx, tk.layer(milo), r=18)
    tk.sticker(ctx, tk.layer(cards), r=12)
    tk.sticker(ctx, tk.layer(dialog), r=16)
    tk.red_ring(ctx, 770, 1590, 280, 178, w=20)
    tk.sticker(ctx, tk.layer(kid), r=18)
    text(ctx)
    print(tk.save(surf, TITLE))


if __name__ == "__main__":
    main()

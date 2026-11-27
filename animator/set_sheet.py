"""Contact sheet of every set / prop / UI piece in sets.py (for checking the look).
Usage: python3 set_sheet.py out.png"""
import sys

import cairo

import sets as st
import style
from engine import H, W

T = 1.3


def s_bedroom(c):
    st.night_bedroom(c, T)
    style.MOM.draw(c, 605, 1060, 1.1, "smirk", T, arms=("down", "hip"))
    style.KID.draw(c, 250, 1150, 1.3, "shock", T, arms=("hold", "hold"))


def s_day(c):
    st.day_room(c, T)
    style.MOM_ROBE.draw(c, 360, 1150, 1.5, "wink", T, arms=("show", "down"))


def s_kitchen(c):
    st.kitchen(c, T)
    style.KID.draw(c, 300, 1150, 1.3, "happy", T, arms=("point", "down"))


def s_desk(c):
    st.gamer_desk(c, T)
    st.laptop(c, 360, 900, 1.1, T, lambda cc, x, y, w, h, TT: st.login_screen(cc, x, y, w, h, TT, typed="******"))


def s_spawn(c):
    st.game_sky(c)
    st.block_clouds(c, T)
    st.baseplate(c, 760)
    st.brick_wall(c, 560, 900, 220, 520)
    st.spawn_pad(c, 300, 960, beam=0.6)
    style.NOOB.draw(c, 300, 960, 1.4, "happy", T, arms=("up", "down"))
    st.joystick_ui(c, T)
    st.toast(c, 360, 150, "xX_Mom_Xx joined the game.", 1.0)


def s_obby(c):
    st.obby(c, T)
    style.KID_GAME.draw(c, 110, 880, 1.0, "smug", T, arms=("cross", "cross"))
    st.stage_pill(c, 360, 260, "STAGE 97")
    st.finish_flag(c, 600, 640, 1.0, T)


def s_arena(c):
    st.arena(c, T)
    style.BOSS.draw(c, 460, 1050, 2.0, "angry", T, arms=("up", "up"))
    st.health_bar(c, 0.6, "NOOB BOSS")
    st.damage_text(c, 300, 600, 0.4)


def s_throne(c):
    st.throne_room(c, T)
    style.MOM.draw(c, 360, 1000, 1.5, "smug", T, arms=("show", "down"))
    style.MOM.crown = False


def s_burst(c):
    st.burst(c, T)
    st.coin_pile(c, 360, 1150, 700, 300, T)
    st.counter(c, 999999999, 360, 300, 60, st.YELLOW)
    st.second_card(c, 360, 560, 8, 0.6)


def s_reveal(c):
    st.dark_glow_bg(c, T)
    st.gamepass_card(c, 360, 640, 1.2, T)


def s_board(c):
    st.burst(c, T, "#7fb8ff", "#2f4bb0")
    rows = [("MomIsBoss", "999,999", lambda cc, x, y, TT: st.face_icon(cc, x, y, 26, "#c89f82", "#a0442a", True)),
            ("You", "12,450", lambda cc, x, y, TT: st.face_icon(cc, x, y, 26)), ("ObbyKing", "9,871", None),
            ("BlockPro", "7,302", None)]
    st.leaderboard(c, 360, 300, 1.0, rows, T)
    st.day_text(c, "DAY 4", 360, 960, 0.8)


def s_shop(c):
    st.burst(c, T, "#a8e6ff", "#4fb0e8")
    items = [("SPEED", "#4f8bff"), ("FLY", "#9d5cff"), ("x2 COINS", "#ffb02e"), ("PET", "#ff5fa2"),
             ("TRAIL", "#2fbf8f"), ("GIANT", "#e8323a")]
    st.shop_grid(c, T, items, owned_t=[0, 0.3, 0.6, None, None, None])
    st.subscribe_button(c, 360, 1000, 1.0)


def s_comments(c):
    st.night_bedroom(c, T)
    st.comments_sheet(c, T, [("@gamer_kid", "my mom did this lol", "#ff5fa2"), ("@noob99", "LOOP", "#4f8bff")],
                      typed="LOOP", likes_t=0.5)


def s_props(c):
    st.burst(c, T, "#ffd0e6", "#ff8fc8")
    st.cake(c, 200, 600, 0.9, T)
    st.padlock(c, 520, 450, 0.9)
    st.alarm_clock(c, 200, 850, 1.0, "0:10")
    st.sticky_note(c, 520, 830, 0.7, ["MOM IS", "THE BOSS", "123"])
    st.egg(c, 360, 1120, 0.8, T, crack=1)
    st.red_x(c, 120, 1120, 60, 1)
    st.check_mark(c, 600, 1120, 60, 1)
    st.impact_star(c, 360, 300, 110, 0.15, "BONK!")


PANELS = [s_bedroom, s_day, s_kitchen, s_desk, s_spawn, s_obby, s_arena, s_throne, s_burst, s_reveal, s_board,
          s_shop, s_comments, s_props]

if __name__ == "__main__":
    sc = 0.4
    cols = 7
    rows = (len(PANELS) + cols - 1) // cols
    out = cairo.ImageSurface(cairo.FORMAT_RGB24, int(W * sc) * cols, int(H * sc) * rows)
    oc = cairo.Context(out)
    for i, fn in enumerate(PANELS):
        s = cairo.ImageSurface(cairo.FORMAT_RGB24, W, H)
        c = cairo.Context(s)
        fn(c)
        oc.save()
        oc.translate((i % cols) * W * sc, (i // cols) * H * sc)
        oc.scale(sc, sc)
        oc.set_source_surface(s)
        oc.paint()
        oc.restore()
    out.write_to_png(sys.argv[1])

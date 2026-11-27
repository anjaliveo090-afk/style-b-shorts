"""Landscape (16:9) places and props for the long video "What If the WHOLE SCHOOL Became Roblox?" (whole_school.py).

Drawn in the 1280x720 world (engine STYLEB_ASPECT=16x9), same flat-vector look as sets.py: style.block /
shape_fill, self-coloured outlines, the measured palette, studs on every Roblox surface.
  places   school_ext, classroom, desk_row, hallway, cafeteria, gym, library, roof, bedroom_ls, home_street,
           parking_obby
  props    school_bell, juice_box, eraser, pencil, inventory, homework, unicorn, exam_boss, fireball, shop_buttons,
           meat_tray, emote_wheel, pa_speaker, cage, note_paper, admin_screen, summer_card, hall_pass, report_card,
           trade_window, level_pill, command_bar, book, family_car, crown, loading_ring
Ground line of the places: y 640 (characters stand there)."""
import math
import random

from engine import H, PI, W, clamp, ease, ellipse, hexc, lerp, pop, rrect
import sets as st
from sets import bold_text, glow, text_width
from style import INK, block, dark, light, shape_fill

GROUND = 640


def studs(ctx, x0, y0, x1, y1, col, step=34, r=8):
    """Roblox studs on a surface (a dot grid with a light top)."""
    for yy in range(int(y0) + step // 2, int(y1), step):
        for xx in range(int(x0) + step // 2, int(x1), step):
            ctx.new_sub_path()
            ctx.arc(xx, yy, r, 0, 2 * PI)
    ctx.set_source_rgba(*light(col, 0.12), 0.55)
    ctx.fill()


def floor(ctx, y=GROUND, col="#c98a4a", planks=True):
    c = hexc(col)
    block(ctx, -200, y, W + 400, H - y + 300, 0, c, 4, gloss=False)
    if planks:
        ctx.set_source_rgba(*dark(c, 0.18), 1)
        ctx.set_line_width(3)
        for i in range(1, 6):
            yy = y + i * 18 * i * 0.6
            ctx.move_to(-200, yy)
            ctx.line_to(W + 200, yy)
        ctx.stroke()


def wall(ctx, col, y1=GROUND, stud=True):
    c = hexc(col)
    ctx.set_source_rgb(*c)
    ctx.rectangle(-300, -300, W + 600, y1 + 300)
    ctx.fill()
    if stud:
        studs(ctx, -300, -300, W + 300, y1, c, step=48, r=9)


# ================================================================ places
def school_ext(ctx, T, cx=640, s=1.0, sign=None, sign_k=1.0, lights=1.0, bell_T=None, lift=0.0, ground=True):
    """The school as a giant Roblox build: red studded blocks, white trim, windows, a door, a bell tower, a flag.
    (cx, GROUND) = middle of the front door. sign = text on the banner over the door (pops in with sign_k)."""
    if ground:
        st.game_sky(ctx)
        st.block_clouds(ctx, T, y0=40, y1=260, n=6)
        st.baseplate(ctx, GROUND)
    ctx.save()
    ctx.translate(cx, GROUND - lift)
    ctx.scale(s, s)
    red = hexc("#d8433a")
    block(ctx, -560, -420, 1120, 420, 10, red, 6)                     # main block
    studs(ctx, -560, -420, 560, 0, red, step=40, r=9)
    block(ctx, -150, -560, 300, 160, 10, red, 6)                      # tower
    studs(ctx, -150, -560, 150, -400, red, step=40, r=9)
    block(ctx, -170, -580, 340, 34, 8, (1, 1, 1), 5)
    block(ctx, -580, -440, 1160, 34, 8, (1, 1, 1), 5)                 # roof trim
    ctx.move_to(0, -560)                                               # flag
    ctx.line_to(0, -700)
    ctx.set_source_rgb(*INK)
    ctx.set_line_width(6)
    ctx.stroke()
    ctx.move_to(0, -700)
    ctx.line_to(80, -680 + math.sin(T * 6) * 6)
    ctx.line_to(0, -655)
    ctx.close_path()
    shape_fill(ctx, hexc("#4fd16a"), 4, -700, -655)
    school_bell(ctx, 0, -490, 0.55, bell_T)
    win = hexc("#ffe9a8") if lights > 0.5 else hexc("#2a3050")
    for row in range(2):
        for i in (-4, -3, -2, 2, 3, 4):
            block(ctx, i * 110 - 40, -360 + row * 150, 80, 90, 8, win, 4, outline=INK)
            ctx.move_to(i * 110, -360 + row * 150)
            ctx.line_to(i * 110, -270 + row * 150)
            ctx.set_source_rgb(1, 1, 1)
            ctx.set_line_width(4)
            ctx.stroke()
    block(ctx, -95, -230, 190, 230, 14, hexc("#5a3a8f"), 6)           # door
    block(ctx, -4, -230, 8, 230, 0, dark(hexc("#5a3a8f"), 0.2), 0, gloss=False)
    for dx in (-24, 24):
        ctx.new_sub_path()
        ctx.arc(dx, -110, 8, 0, 2 * PI)
        ctx.set_source_rgb(*hexc("#ffcc33"))
        ctx.fill()
    ctx.restore()
    if sign:
        k = clamp(sign_k)
        y = GROUND - (300 + (1 - ease(k)) * 300) * s
        sc = s * (0.6 + 0.4 * ease(k))
        ctx.save()
        ctx.translate(cx, y)
        ctx.scale(sc, sc)
        for dx in (-230, 230):
            ctx.move_to(dx, -60)
            ctx.line_to(dx * 0.8, -140)
        ctx.set_source_rgb(*INK)
        ctx.set_line_width(5)
        ctx.stroke()
        block(ctx, -300, -70, 600, 120, 22, hexc("#ffd84a"), 7)
        size = 46
        while size > 20 and text_width(ctx, sign, size) > 540:
            size -= 2
        bold_text(ctx, sign, 0, -10, size, (1, 1, 1), shadow=False)
        ctx.restore()


def classroom(ctx, T, board="", board_col=(1, 1, 1), y=GROUND, clock_h=9.0, window=True, wall_col="#8fd0e8"):
    """Classroom: studded wall, a green chalkboard with text, a wall clock, a window."""
    wall(ctx, wall_col, y)
    block(ctx, 300, 90, 680, 300, 16, hexc("#8a5a3a"), 6)
    block(ctx, 320, 108, 640, 264, 10, hexc("#2e6b4a"), 4, gloss=False)
    if board:
        lines = board.split("\n")
        size = 54 if len(lines) == 1 else 44
        for i, ln in enumerate(lines):
            while size > 18 and text_width(ctx, ln, size) > 600:
                size -= 2
            bold_text(ctx, ln, 640, 240 + (i - (len(lines) - 1) / 2) * size * 1.2, size, board_col, outline=None,
                      shadow=False, stroke=0.0)
    st.big_clock(ctx, 1110, 170, 62, clock_h, T)
    if window:
        block(ctx, 60, 120, 180, 200, 10, (1, 1, 1), 5)
        block(ctx, 74, 134, 152, 172, 6, hexc("#84d4fb"), 3, gloss=False)
        ctx.move_to(150, 134)
        ctx.line_to(150, 306)
        ctx.move_to(74, 220)
        ctx.line_to(226, 220)
        ctx.set_source_rgb(1, 1, 1)
        ctx.set_line_width(6)
        ctx.stroke()
    floor(ctx, y, "#c98a4a")


def desk(ctx, x, y=GROUND, s=1.0, col="#e0a050"):
    """A school desk seen from the front (its top at y - 110 s)."""
    c = hexc(col)
    for dx in (-80, 66):
        block(ctx, x + dx * s, y - 100 * s, 14 * s, 100 * s, 3 * s, hexc("#7a7f9a"), 3, gloss=False)
    block(ctx, x - 95 * s, y - 128 * s, 190 * s, 34 * s, 8 * s, c, 4)


def desk_row(ctx, xs, y=GROUND, s=1.0):
    for x in xs:
        desk(ctx, x, y, s)


def hallway(ctx, T, sign=None, y=GROUND, n=11, wall_col="#ffe3a8"):
    """A hallway: a row of tall Roblox-block lockers on a studded wall, a shiny floor, an optional sign."""
    wall(ctx, wall_col, y)
    cols = ("#4f8bff", "#ff5fb0", "#4fd16a", "#ffd84a", "#9d5cff")
    for i in range(n):
        x = 40 + i * 112
        c = hexc(cols[i % len(cols)])
        block(ctx, x, 200, 100, y - 200, 8, c, 5)
        for j in range(3):
            ctx.rectangle(x + 24, 230 + j * 14, 52, 6)
        ctx.set_source_rgba(*dark(c, 0.3), 1)
        ctx.fill()
        block(ctx, x + 74, 380, 12, 40, 4, hexc("#c9cde0"), 2, gloss=False)
    floor(ctx, y, "#b8c4d8", planks=False)
    if sign:
        block(ctx, 440, 70, 400, 90, 18, hexc("#e8323a"), 6)
        bold_text(ctx, sign, 640, 115, 40, (1, 1, 1), shadow=False)


def cafeteria(ctx, T, y=GROUND, counter=True):
    """Cafeteria: tiled wall, a serving counter with trays, long tables."""
    wall(ctx, "#bfe7d0", y, stud=False)
    for yy in range(0, y, 46):
        for xx in range(-20, W + 40, 46):
            ctx.rectangle(xx + 3, yy + 3, 40, 40)
    ctx.set_source_rgba(1, 1, 1, 0.35)
    ctx.fill()
    block(ctx, 360, 60, 560, 70, 16, hexc("#ff8a3d"), 6)
    bold_text(ctx, "CAFETERIA", 640, 95, 42, (1, 1, 1), shadow=False)
    floor(ctx, y, "#d8c8b0", planks=False)
    if counter:
        block(ctx, -40, y - 170, 520, 170, 10, hexc("#c9cde0"), 5)
        block(ctx, -40, y - 190, 520, 30, 8, hexc("#e8ecf5"), 4)


def long_table(ctx, x, y=GROUND, w=420, s=1.0):
    block(ctx, x - w / 2 * s, y - 90 * s, w * s, 26 * s, 6, hexc("#e0a050"), 4)
    for dx in (-w / 2 + 30, w / 2 - 44):
        block(ctx, x + dx * s, y - 64 * s, 14 * s, 64 * s, 3, hexc("#7a7f9a"), 3, gloss=False)


def gym(ctx, T, y=GROUND, doors=0.0, dark_k=0.0):
    """The gym: wooden floor with court lines, a scoreboard, bleachers, basketball hoops, big doors."""
    wall(ctx, "#f0b866", y)
    for i in range(4):                                                 # bleachers
        block(ctx, -100, 300 + i * 70, 360, 30, 4, hexc("#b0743c"), 4, gloss=False)
        block(ctx, W - 260, 300 + i * 70, 360, 30, 4, hexc("#b0743c"), 4, gloss=False)
    block(ctx, 520, 40, 240, 110, 14, hexc("#1e2230"), 5)              # scoreboard
    bold_text(ctx, "HOME 0 : 0 EXAM", 640, 95, 26, hexc("#ff4f5a"), shadow=False, stroke=0.0)
    for x in (130, W - 130):                                           # hoops
        block(ctx, x - 70, 160, 140, 100, 8, (1, 1, 1), 5)
        ctx.new_sub_path()
        ctx.arc(x, 268, 34, 0, PI)
        ctx.set_source_rgb(*hexc("#ff7a1a"))
        ctx.set_line_width(7)
        ctx.stroke()
    floor(ctx, y, "#e8b070")
    ctx.set_source_rgba(1, 1, 1, 0.8)
    ctx.set_line_width(5)
    ellipse(ctx, 640, y + 60, 220, 40)
    ctx.stroke()
    if doors > 0:
        g = doors
        block(ctx, 440, 200, 400, y - 200, 10, hexc("#5a5f7a"), 6)
        ctx.rectangle(440 + 200 * (1 - g), 200, 400 * g, y - 200)
        ctx.set_source_rgb(1, 1, 0.9)
        ctx.fill()
        glow(ctx, 640, 420, 420, (1, 1, 0.85), 0.6 * g)
    if dark_k > 0:
        ctx.set_source_rgba(0.05, 0.03, 0.12, 0.6 * dark_k)
        ctx.rectangle(-300, -300, W + 600, H + 600)
        ctx.fill()


def library(ctx, T, y=GROUND):
    """Library: tall shelves of coloured books, a lamp glow."""
    wall(ctx, "#6b4a8a", y, stud=False)
    rnd = random.Random(4)
    for sx in (-40, 330, 700, 1070):
        block(ctx, sx, 60, 300, y - 60, 8, hexc("#8a5a3a"), 5)
        for row in range(5):
            yy = 80 + row * 110
            block(ctx, sx + 10, yy + 86, 280, 14, 2, hexc("#6a4228"), 2, gloss=False)
            xx = sx + 18
            while xx < sx + 270:
                bw = rnd.randint(16, 30)
                bh = rnd.randint(56, 84)
                block(ctx, xx, yy + 86 - bh, bw, bh, 3,
                      hexc(rnd.choice(("#ff4f5a", "#4f8bff", "#4fd16a", "#ffd84a", "#9d5cff", "#ff8a3d"))), 2,
                      gloss=False)
                xx += bw + 3
    glow(ctx, 640, 200, 500, (1, 0.9, 0.6), 0.25)
    floor(ctx, y, "#8a5a3a")


def roof(ctx, T, y=GROUND):
    """The school roof: sky, a studded red roof surface, the bell tower edge."""
    st.game_sky(ctx)
    st.block_clouds(ctx, T, y0=40, y1=300, n=6)
    red = hexc("#d8433a")
    block(ctx, -200, y - 40, W + 400, H, 0, red, 5, gloss=False)
    studs(ctx, -200, y - 40, W + 200, H, red, step=40, r=9)
    block(ctx, -200, y - 60, W + 400, 26, 6, (1, 1, 1), 4)


def bedroom_ls(ctx, T, y=GROUND, lights=1.0, moon=True):
    """Night bedroom (landscape): navy wall, a window with the moon, a bed, a desk with a lamp."""
    wall(ctx, "#272b6d", y, stud=False)
    block(ctx, 120, 90, 260, 230, 12, hexc("#8a90a8"), 6)
    block(ctx, 136, 106, 228, 198, 8, hexc("#141a3e"), 3, gloss=False)
    if moon:
        ctx.new_sub_path()
        ctx.arc(300, 160, 34, 0, 2 * PI)
        ctx.set_source_rgb(*hexc("#fff3c4"))
        ctx.fill()
    for i in range(6):
        ctx.new_sub_path()
        ctx.arc(160 + i * 34, 250 - (i % 3) * 30, 3, 0, 2 * PI)
    ctx.set_source_rgb(1, 1, 1)
    ctx.fill()
    block(ctx, 900, y - 150, 420, 150, 16, hexc("#5a4fb0"), 5)          # bed
    block(ctx, 920, y - 190, 120, 60, 18, (1, 1, 1), 4)
    floor(ctx, y, "#3a3f6a")
    block(ctx, 420, y - 200, 380, 30, 8, hexc("#8a5a3a"), 5)            # desk
    for dx in (440, 760):
        block(ctx, dx, y - 170, 22, 170, 4, hexc("#6a4228"), 3, gloss=False)
    if lights > 0:
        glow(ctx, 520, y - 260, 260, (1, 0.9, 0.55), 0.5 * lights)
    block(ctx, 500, y - 300, 16, 100, 4, hexc("#c9cde0"), 3, gloss=False)  # lamp
    ctx.move_to(470, y - 300)
    ctx.line_to(546, y - 300)
    ctx.line_to(530, y - 340)
    ctx.line_to(486, y - 340)
    ctx.close_path()
    shape_fill(ctx, hexc("#ffd84a") if lights > 0.5 else hexc("#8a7a4a"), 4, y - 340, y - 300)
    if lights < 1:
        ctx.set_source_rgba(0.02, 0.02, 0.08, 0.75 * (1 - lights))
        ctx.rectangle(-300, -300, W + 600, H + 600)
        ctx.fill()


def home_street(ctx, T, y=GROUND, sunset=0.0, night=0.0, lit=0.0):
    """A street of houses (engine.houses) with a sidewalk; sunset / night tints."""
    import engine
    if night > 0.5:
        st.game_sky(ctx, top="#141a3e", bottom="#2a3070")
    elif sunset > 0.5:
        st.game_sky(ctx, top="#f28a5a", bottom="#ffd9a8")
    else:
        st.game_sky(ctx)
        st.block_clouds(ctx, T, y0=40, y1=250, n=5)
    engine.houses(ctx, y, 5, 1.6, hexc("#ffd27a"), hexc("#d8433a"), hexc("#ffe9a8") if lit else hexc("#84d4fb"),
                  lit=lit, x0=-300, x1=W + 300)
    block(ctx, -200, y, W + 400, 60, 0, hexc("#c9cde0"), 4, gloss=False)
    block(ctx, -200, y + 60, W + 400, H, 0, hexc("#4a4f66"), 4, gloss=False)
    off = 0
    for i in range(10):
        block(ctx, -100 + i * 160 + off, y + 130, 90, 12, 4, (1, 1, 1), 0, gloss=False)


def parking_obby(ctx, T, stage=1, y_lava=660):
    """The school parking lot turned into an obby: lava, coloured platforms, parked cars, a STAGE pill."""
    st.game_sky(ctx)
    st.block_clouds(ctx, T, y0=40, y1=220, n=5)
    st.lava(ctx, y_lava, T)
    cols = ("#2cd5fc", "#fa3a9f", "#f7e04a", "#a694e1", "#4fd16a")
    for i in range(7):
        x = -60 + i * 210
        yy = y_lava - 70 - (i % 2) * 40
        st.platform(ctx, x, yy, 140, cols[i % len(cols)], h=50)
    for x in (230, 860):
        family_car(ctx, x, y_lava - 120, 0.45, T, col="#9aa0b8")
    st.stage_pill(ctx, 1040, 160, f"STAGE {stage}/40", s=1.1, col="#e8323a")


# ================================================================ props
def school_bell(ctx, x, y, s, ring_T=None):
    """A brass school bell; ring_T = seconds since it started ringing (swings + ring lines)."""
    if s <= 0.01:
        return
    sw = math.sin(ring_T * 22) * 0.35 * math.exp(-ring_T * 0.6) if ring_T is not None and ring_T >= 0 else 0.0
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s, s)
    ctx.rotate(sw)
    ctx.move_to(-90, 60)
    ctx.curve_to(-90, -40, -60, -110, 0, -110)
    ctx.curve_to(60, -110, 90, -40, 90, 60)
    ctx.line_to(110, 80)
    ctx.line_to(-110, 80)
    ctx.close_path()
    shape_fill(ctx, hexc("#ffcc33"), 6, -110, 80)
    ctx.new_sub_path()
    ctx.arc(0, 92, 20, 0, 2 * PI)
    shape_fill(ctx, hexc("#b0743c"), 4, 72, 112)
    block(ctx, -16, -140, 32, 34, 6, hexc("#8a5a3a"), 4)
    ctx.restore()
    if ring_T is not None and ring_T >= 0:
        for side in (-1, 1):
            for i in range(3):
                a = 0.5 + i * 0.4
                r = (140 + i * 26) * s
                ctx.new_sub_path()
                ctx.arc(x, y, r, -a if side > 0 else PI - 0.0, -a + 0.5 if side > 0 else PI + 0.5)
                ctx.set_source_rgba(*INK, 0.8)
                ctx.set_line_width(6 * s)
                ctx.stroke()


def juice_box(ctx, x, y, s=1.0, rot=0.0):
    """A juice box with a straw; (x, y) = centre."""
    ctx.save()
    ctx.translate(x, y)
    ctx.rotate(rot)
    ctx.scale(s, s)
    block(ctx, -40, -60, 80, 120, 8, hexc("#ff8a3d"), 5)
    block(ctx, -40, -60, 80, 26, 6, hexc("#ffd84a"), 4)
    ctx.new_sub_path()
    ctx.arc(0, 18, 22, 0, 2 * PI)
    shape_fill(ctx, hexc("#ff4f5a"), 3, -4, 40)
    bold_text(ctx, "JUICE", 0, -46, 14, (1, 1, 1), shadow=False, stroke=0.0)
    ctx.move_to(14, -60)
    ctx.line_to(26, -110)
    ctx.line_to(44, -114)
    ctx.set_source_rgb(*hexc("#ff5fb0"))
    ctx.set_line_width(9)
    ctx.stroke()
    ctx.restore()


def eraser(ctx, x, y, s=1.0, rot=0.0):
    ctx.save()
    ctx.translate(x, y)
    ctx.rotate(rot)
    ctx.scale(s, s)
    block(ctx, -70, -32, 140, 64, 14, hexc("#ff8fb0"), 5)
    block(ctx, 10, -32, 60, 64, 10, hexc("#4f8bff"), 4)
    bold_text(ctx, "ERASE", -26, 0, 18, (1, 1, 1), shadow=False, stroke=0.0)
    ctx.restore()


def pencil(ctx, x, y, s=1.0, rot=0.0):
    ctx.save()
    ctx.translate(x, y)
    ctx.rotate(rot)
    ctx.scale(s, s)
    block(ctx, -80, -16, 130, 32, 4, hexc("#ffd84a"), 4)
    block(ctx, -100, -16, 26, 32, 6, hexc("#ff8fb0"), 4)
    ctx.move_to(50, -16)
    ctx.line_to(92, 0)
    ctx.line_to(50, 16)
    ctx.close_path()
    shape_fill(ctx, hexc("#f2d2a0"), 4, -16, 16)
    ctx.move_to(80, -5)
    ctx.line_to(92, 0)
    ctx.line_to(80, 5)
    ctx.close_path()
    ctx.set_source_rgb(*INK)
    ctx.fill()
    ctx.restore()


ITEM_DRAW = {"pencil": lambda c, x, y, sz: pencil(c, x, y, sz / 120, -0.6),
             "eraser": lambda c, x, y, sz: eraser(c, x, y, sz / 150, -0.3),
             "juice": lambda c, x, y, sz: juice_box(c, x, y + sz * 0.08, sz / 140),
             "note": lambda c, x, y, sz: note_paper(c, x, y, sz / 170, lines=("...",)),
             "?": lambda c, x, y, sz: bold_text(c, "?", x, y, sz * 0.8, hexc("#ffd84a"))}


def inventory(ctx, cx, cy, s, items, k_items=None, sel=None, extra_k=None, T=0.0, title="INVENTORY"):
    """The Roblox backpack: a dark panel with numbered slots; items = names from ITEM_DRAW (or None).
    k_items[i] = seconds since item i popped in (None = shown). extra_k = seconds since a glowing extra slot
    appeared (slot n + 1, with a note in it)."""
    n = len(items) + (1 if extra_k is not None and extra_k >= 0 else 0)
    slot = 150
    w = n * (slot + 20) + 40
    ctx.save()
    ctx.translate(cx, cy)
    ctx.scale(s, s)
    block(ctx, -w / 2, -150, w, 300, 24, hexc("#1e2230"), 6, outline=hexc("#0f121c"))
    bold_text(ctx, title, -w / 2 + 30, -112, 30, (1, 1, 1), align="l", shadow=False, stroke=0.0)
    for i in range(n):
        x = -w / 2 + 40 + i * (slot + 20)
        is_extra = i == len(items)
        if is_extra:
            glow(ctx, x + slot / 2, 30, 160, (1, 0.85, 0.3), 0.6)
        rrect(ctx, x, -45, slot, slot, 16)
        ctx.set_source_rgba(0.2, 0.22, 0.3, 1)
        ctx.fill_preserve()
        ctx.set_source_rgb(*(hexc("#ffd84a") if (sel == i or is_extra) else (0.6, 0.62, 0.72)))
        ctx.set_line_width(7 if (sel == i or is_extra) else 3)
        ctx.stroke()
        bold_text(ctx, str(i + 1), x + 20, -26, 22, (1, 1, 1), shadow=False, stroke=0.0)
        name = "note" if is_extra else items[i]
        k = None if (is_extra or k_items is None) else k_items[i]
        if is_extra:
            k = extra_k - 0.3
        if name and (k is None or k >= 0):
            sc = 1.0 if k is None or k > 0.6 else pop(k)
            ctx.save()
            ctx.translate(x + slot / 2, 30)
            ctx.scale(sc, sc)
            ITEM_DRAW[name](ctx, 0, 0, 130)
            ctx.restore()
    ctx.restore()


def homework(ctx, x, y, s=1.0, rot=-0.05, text=None):
    """A homework sheet: title, empty lines, a big 0/20 (blank)."""
    ctx.save()
    ctx.translate(x, y)
    ctx.rotate(rot)
    ctx.scale(s, s)
    block(ctx, -170, -220, 340, 440, 10, (1, 1, 1), 5, gloss=False)
    bold_text(ctx, "HOMEWORK", 0, -175, 34, hexc("#2f6bd8"), outline=None, shadow=False, stroke=0.0)
    ctx.set_source_rgba(*hexc("#9ad0ff"), 1)
    ctx.set_line_width(3)
    for i in range(8):
        ctx.move_to(-140, -120 + i * 40)
        ctx.line_to(140, -120 + i * 40)
    ctx.stroke()
    if text:
        bold_text(ctx, text, 0, 140, 60, hexc("#e8323a"), shadow=False, stroke=0.05)
    ctx.restore()


def unicorn(ctx, x, y, s=1.0, T=0.0, look=1):
    """A blocky white unicorn with a rainbow mane and a gold horn; (x, y) = ground under it; look = +1 right."""
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s * look, s)
    trot = math.sin(T * 8) * 6
    for dx in (-90, -50, 40, 80):
        block(ctx, dx, -110 + (trot if dx < 0 else -trot) * 0.5, 30, 110, 6, hexc("#f4f0ff"), 4)
    block(ctx, -120, -230, 250, 130, 30, hexc("#f4f0ff"), 6)            # body
    block(ctx, 80, -330, 90, 150, 24, hexc("#f4f0ff"), 6)               # neck/head
    block(ctx, 130, -320, 90, 70, 20, hexc("#f4f0ff"), 6)
    ctx.new_sub_path()
    ctx.arc(170, -296, 8, 0, 2 * PI)
    ctx.set_source_rgb(*INK)
    ctx.fill()
    ctx.move_to(130, -330)                                             # horn
    ctx.line_to(150, -410)
    ctx.line_to(165, -330)
    ctx.close_path()
    shape_fill(ctx, hexc("#ffcc33"), 4, -410, -330)
    for i, c in enumerate(("#ff4f5a", "#ffd84a", "#4fd16a", "#4f8bff", "#9d5cff")):   # mane
        block(ctx, 60 - i * 6, -330 + i * 26, 40, 30, 12, hexc(c), 3, gloss=False)
    for i, c in enumerate(("#ff4f5a", "#ffd84a", "#4fd16a", "#4f8bff")):              # tail
        block(ctx, -160 - i * 8, -220 + i * 22 + math.sin(T * 6 + i) * 4, 50, 26, 12, hexc(c), 3, gloss=False)
    ctx.restore()


def exam_boss(ctx, x, y, s=1.0, T=0.0, jaw=0.0, erase_k=0.0, rage=0.0):
    """THE FINAL EXAM: a giant test paper monster (arms, angry eyes, a mouth full of teeth); (x, y) = its feet.
    jaw 0..1 opens the mouth (lip-sync on its lines); erase_k 0..1 rubs it out from the top."""
    if s <= 0.01 or erase_k >= 1:
        return
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s, s)
    sway = math.sin(T * 2.2) * 0.03
    ctx.rotate(sway)
    if erase_k > 0:
        ctx.rectangle(-600, -1100 + erase_k * 1150, 1200, 1300)
        ctx.clip()
    for side in (-1, 1):                                               # arms
        a = 0.5 + 0.25 * math.sin(T * 3 + side)
        ctx.save()
        ctx.translate(side * 230, -600)
        ctx.rotate(side * a)
        block(ctx, -40, 0, 80, 300, 30, hexc("#f4f0ff"), 6)
        block(ctx, -55, 270, 110, 90, 40, hexc("#f4f0ff"), 6)
        ctx.restore()
    for dx in (-110, 60):                                              # legs
        block(ctx, dx, -180, 60, 180, 20, hexc("#f4f0ff"), 6)
    ctx.move_to(-260, -1000)                                           # paper body with a folded corner
    ctx.line_to(170, -1000)
    ctx.line_to(260, -910)
    ctx.line_to(260, -160)
    ctx.line_to(-260, -160)
    ctx.close_path()
    shape_fill(ctx, (1, 1, 1), 7, -1000, -160)
    ctx.move_to(170, -1000)
    ctx.line_to(170, -910)
    ctx.line_to(260, -910)
    ctx.close_path()
    shape_fill(ctx, hexc("#d8dce8"), 5, -1000, -910)
    bold_text(ctx, "FINAL EXAM", 0, -940, 52, hexc("#e8323a"), shadow=False, stroke=0.05)
    ctx.set_source_rgba(*hexc("#9ad0ff"), 1)
    ctx.set_line_width(4)
    for i in range(6):
        ctx.move_to(-220, -580 + i * 60)
        ctx.line_to(220, -580 + i * 60)
    ctx.stroke()
    for i, q in enumerate(("1) 7 x 8 = ?", "2) 1776 = ?", "3) H2O = ?")):
        bold_text(ctx, q, -200, -560 + i * 120, 30, INK, outline=None, align="l", shadow=False, stroke=0.0)
    for dx in (-100, 100):                                             # angry eyes
        ellipse(ctx, dx, -820, 58, 48)
        shape_fill(ctx, (1, 1, 1), 6, -870, -770)
        ctx.new_sub_path()
        ctx.arc(dx + (8 if dx < 0 else -8), -812, 22, 0, 2 * PI)
        ctx.set_source_rgb(*(hexc("#e8323a") if rage > 0.5 else INK))
        ctx.fill()
        ctx.move_to(dx - 70, -890 + (30 if dx < 0 else -10))
        ctx.line_to(dx + 70, -890 + (-10 if dx < 0 else 30))
        ctx.set_source_rgb(*INK)
        ctx.set_line_width(14)
        ctx.stroke()
    mh = 50 + 110 * clamp(jaw)                                         # mouth with teeth
    block(ctx, -170, -720, 340, mh, 24, hexc("#5a1020"), 6, gloss=False)
    for i in range(7):
        tx = -150 + i * 50
        ctx.move_to(tx, -720)
        ctx.line_to(tx + 25, -720 + 34)
        ctx.line_to(tx + 50, -720)
        ctx.close_path()
        ctx.move_to(tx, -720 + mh)
        ctx.line_to(tx + 25, -720 + mh - 30)
        ctx.line_to(tx + 50, -720 + mh)
        ctx.close_path()
    ctx.set_source_rgb(1, 1, 1)
    ctx.fill()
    ctx.restore()


def fireball(ctx, x, y, s=1.0, T=0.0, txt="7 x 8"):
    """A math problem on fire, flying left."""
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s, s)
    for i in range(6):
        r = 80 - i * 10
        ctx.new_sub_path()
        ctx.arc(60 + i * 26 + math.sin(T * 30 + i) * 6, math.cos(T * 25 + i) * 8, r, 0, 2 * PI)
        ctx.set_source_rgba(*hexc(("#ff4f2a", "#ff8a3d", "#ffd84a")[i % 3]), 0.85 - i * 0.1)
        ctx.fill()
    ctx.new_sub_path()
    ctx.arc(0, 0, 90, 0, 2 * PI)
    shape_fill(ctx, hexc("#ff7a1a"), 6, -90, 90)
    bold_text(ctx, txt, 0, 0, 44, (1, 1, 1), shadow=False)
    ctx.restore()


def shop_buttons(ctx, x, y, s=1.0, sel=None, k=1.0):
    """The lunch lady's floating shop buttons: Pizza R$ 15 / Mystery meat FREE."""
    if k < 0:
        return
    sc = s * (pop(k) if k < 0.6 else 1.0)
    for i, (name, price, col) in enumerate((("PIZZA", "R$ 15", "#4f8bff"), ("MYSTERY MEAT", "FREE", "#4fd16a"))):
        ctx.save()
        ctx.translate(x, y + i * 100 * s)
        ctx.scale(sc, sc)
        if sel == i:
            glow(ctx, 0, 0, 200, (1, 0.9, 0.4), 0.6)
        block(ctx, -190, -40, 380, 80, 20, hexc(col), 5 if sel != i else 8,
              outline=hexc("#ffd84a") if sel == i else None)
        bold_text(ctx, name, -170, 0, 30, (1, 1, 1), align="l", shadow=False, stroke=0.1)
        bold_text(ctx, price, 170, 0, 30, hexc("#ffd84a"), align="r", shadow=False, stroke=0.1)
        ctx.restore()


def meat_tray(ctx, x, y, s=1.0, T=0.0):
    """A lunch tray with a green lump of mystery meat and buzzing flies."""
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s, s)
    block(ctx, -170, -30, 340, 60, 14, hexc("#c9cde0"), 5)
    ellipse(ctx, 0, -50, 110, 60)
    shape_fill(ctx, hexc("#7fa84a"), 6, -110, 10)
    for dx, dy in ((-40, -70), (30, -40), (50, -80)):
        ctx.new_sub_path()
        ctx.arc(dx, dy, 10, 0, 2 * PI)
        ctx.set_source_rgba(*hexc("#5a7a2a"), 1)
        ctx.fill()
    for i in range(3):
        a = T * 6 + i * 2.1
        fx, fy = math.cos(a) * 120, -150 + math.sin(a * 1.3) * 40
        ctx.new_sub_path()
        ctx.arc(fx, fy, 7, 0, 2 * PI)
        ctx.set_source_rgb(*INK)
        ctx.fill()
        ctx.move_to(fx - 14, fy - 8)
        ctx.line_to(fx, fy)
        ctx.line_to(fx + 14, fy - 8)
        ctx.set_line_width(3)
        ctx.stroke()
    ctx.restore()


def emote_wheel(ctx, cx, cy, s=1.0, sel=None, k=1.0):
    """The emote wheel: 6 slices (Wave, Dance, Point, Cheer, Laugh, KISS); sel = index lit."""
    if k < 0:
        return
    sc = s * (pop(k) if k < 0.6 else 1.0)
    names = ("WAVE", "DANCE", "POINT", "CHEER", "LAUGH", "KISS")
    ctx.save()
    ctx.translate(cx, cy)
    ctx.scale(sc, sc)
    for i, nm in enumerate(names):
        a0, a1 = -PI / 2 + i * PI / 3, -PI / 2 + (i + 1) * PI / 3
        ctx.move_to(0, 0)
        ctx.arc(0, 0, 230, a0, a1)
        ctx.close_path()
        ctx.set_source_rgba(*(hexc("#ff5fb0") if sel == i else hexc("#1e2230")), 0.92)
        ctx.fill_preserve()
        ctx.set_source_rgb(1, 1, 1)
        ctx.set_line_width(4)
        ctx.stroke()
        am = (a0 + a1) / 2
        bold_text(ctx, nm, math.cos(am) * 150, math.sin(am) * 150, 30, (1, 1, 1), shadow=False, stroke=0.1)
    ctx.new_sub_path()
    ctx.arc(0, 0, 60, 0, 2 * PI)
    ctx.set_source_rgb(*hexc("#2a2f45"))
    ctx.fill()
    bold_text(ctx, "EMOTES", 0, 0, 22, (1, 1, 1), shadow=False, stroke=0.0)
    ctx.restore()


def pa_speaker(ctx, x, y, s=1.0, T=0.0, crackle=0.0):
    """A wall loudspeaker; crackle 0..1 adds static zigzags."""
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s, s)
    block(ctx, -110, -90, 220, 180, 20, hexc("#8a90a8"), 6)
    ctx.new_sub_path()
    ctx.arc(0, 0, 66, 0, 2 * PI)
    shape_fill(ctx, hexc("#3a3f55"), 5, -66, 66)
    for r in (20, 40):
        ctx.new_sub_path()
        ctx.arc(0, 0, r, 0, 2 * PI)
        ctx.set_source_rgba(1, 1, 1, 0.3)
        ctx.set_line_width(3)
        ctx.stroke()
    if crackle > 0:
        rnd = random.Random(int(T * 12))
        for side in (-1, 1):
            for j in range(3):
                ctx.move_to(side * 130, -60 + j * 60)
                for q in range(5):
                    ctx.line_to(side * (150 + q * 26), -60 + j * 60 + rnd.uniform(-18, 18))
                ctx.set_source_rgba(*INK, crackle)
                ctx.set_line_width(6)
                ctx.stroke()
    ctx.restore()


def cage(ctx, x, y, s=1.0):
    """A small cage (bars + top); draw it AFTER the prisoner. (x, y) = bottom centre."""
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s, s)
    block(ctx, -170, -20, 340, 30, 6, hexc("#5a5f7a"), 4)
    block(ctx, -180, -420, 360, 40, 10, hexc("#5a5f7a"), 5)
    for i in range(8):
        block(ctx, -160 + i * 44, -390, 14, 380, 6, hexc("#8a90a8"), 3)
    ctx.restore()


def note_paper(ctx, x, y, s=1.0, lines=("LIBRARY.", "NOW."), sign=None, rot=0.06):
    ctx.save()
    ctx.translate(x, y)
    ctx.rotate(rot)
    ctx.scale(s, s)
    block(ctx, -180, -130, 360, 260, 8, hexc("#fff6c4"), 5, gloss=False)
    for i, ln in enumerate(lines):
        bold_text(ctx, ln, 0, -60 + i * 66, 50, hexc("#2b2f45"), outline=None, shadow=False, stroke=0.0)
    if sign:
        bold_text(ctx, sign, 60, 95, 26, hexc("#e8323a"), outline=None, shadow=False, stroke=0.0)
    ctx.restore()


def admin_screen(c, x, y, w, h, T, lines=None, red=None, blink=True):
    """An admin panel on a monitor: dark, a title bar, lines of settings; line `red` blinks red."""
    c.set_source_rgb(*hexc("#141a2e"))
    c.rectangle(x, y, w, h)
    c.fill()
    c.set_source_rgb(*hexc("#e8323a"))
    c.rectangle(x, y, w, h * 0.12)
    c.fill()
    bold_text(c, "ADMIN PANEL", x + w / 2, y + h * 0.06, h * 0.07, (1, 1, 1), shadow=False, stroke=0.0)
    lines = lines or ("Players: 412", "Gravity: ON", "Chat bubbles: ON", "UPDATE: FRI 3 PM", "Summer: DELETE")
    for i, ln in enumerate(lines):
        yy = y + h * (0.22 + i * 0.16)
        on = red == i and (not blink or int(T * 4) % 2 == 0)
        if on:
            c.set_source_rgba(0.9, 0.1, 0.15, 0.85)
            c.rectangle(x + w * 0.05, yy - h * 0.06, w * 0.9, h * 0.12)
            c.fill()
        bold_text(c, ln, x + w * 0.08, yy, h * 0.075, (1, 1, 1) if on else hexc("#9aa0b8"), align="l", shadow=False,
                  stroke=0.0)


def summer_card(ctx, x, y, s=1.0, T=0.0, deleted=0.0, restored=0.0):
    """'SUMMER VACATION': a sun over a beach; deleted 0..1 cracks it grey and stamps DELETED."""
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s, s)
    block(ctx, -260, -180, 520, 360, 26, hexc("#84d4fb"), 7)
    block(ctx, -260, 60, 520, 120, 26, hexc("#ffd27a"), 0, gloss=False)
    block(ctx, -260, 30, 520, 50, 0, hexc("#2f9be0"), 0, gloss=False)
    ctx.new_sub_path()
    ctx.arc(130, -80, 60, 0, 2 * PI)
    shape_fill(ctx, hexc("#ffd84a"), 5, -140, -20)
    for i in range(10):
        a = i * PI / 5 + T
        ctx.move_to(130 + math.cos(a) * 75, -80 + math.sin(a) * 75)
        ctx.line_to(130 + math.cos(a) * 100, -80 + math.sin(a) * 100)
    ctx.set_source_rgb(*hexc("#ffb020"))
    ctx.set_line_width(8)
    ctx.stroke()
    bold_text(ctx, "SUMMER", -90, -110, 50, (1, 1, 1))
    bold_text(ctx, "VACATION", -90, -50, 40, hexc("#ffd84a"))
    if deleted > 0:
        ctx.set_source_rgba(0.25, 0.25, 0.3, 0.7 * clamp(deleted))
        rrect(ctx, -260, -180, 520, 360, 26)
        ctx.fill()
        ctx.move_to(-200, -180)
        ctx.line_to(-40, -20)
        ctx.line_to(-110, 40)
        ctx.line_to(60, 180)
        ctx.set_source_rgb(*INK)
        ctx.set_line_width(8)
        ctx.stroke()
    ctx.restore()
    if deleted > 0:
        st.stamp(ctx, x, y, "DELETED", deleted * 0.7, size=90 * s)
    if restored > 0:
        st.sparkles(ctx, T, x, y, spread=300 * s, n=12, seed=2, c=hexc("#ffd84a"))


def hall_pass(ctx, x, y, s=1.0, T=0.0, rot=-0.08):
    """The golden HALL PASS ticket."""
    ctx.save()
    ctx.translate(x, y)
    ctx.rotate(rot + math.sin(T * 2) * 0.03)
    ctx.scale(s, s)
    glow(ctx, 0, 0, 340, (1, 0.85, 0.3), 0.5)
    block(ctx, -260, -120, 520, 240, 26, hexc("#ffcc33"), 7)
    block(ctx, -236, -96, 472, 192, 18, hexc("#ffe27a"), 3, gloss=False)
    bold_text(ctx, "GOLDEN", 0, -40, 44, hexc("#b07a10"), outline=(1, 1, 1), shadow=False, stroke=0.1)
    bold_text(ctx, "HALL PASS", 0, 30, 64, (1, 1, 1), outline=hexc("#b07a10"))
    ctx.restore()
    st.sparkles(ctx, T, x, y, spread=320 * s, n=10, seed=5, c=(1, 1, 1))


def report_card(ctx, x, y, s=1.0, T=0.0, k_lines=(0, 0)):
    """The report card: 'GRADE: LEVEL 1' and the 'ACHIEVEMENT: SAVED SUMMER' badge (k_lines = seconds since each)."""
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s, s)
    block(ctx, -230, -280, 460, 560, 14, (1, 1, 1), 6, gloss=False)
    block(ctx, -230, -280, 460, 90, 14, hexc("#2f6bd8"), 6)
    bold_text(ctx, "REPORT CARD", 0, -235, 40, (1, 1, 1), shadow=False)
    if k_lines[0] >= 0:
        bold_text(ctx, "GRADE:", -190, -110, 40, INK, outline=None, align="l", shadow=False, stroke=0.0)
        bold_text(ctx, "LEVEL 1", 190, -110, 54, hexc("#e8323a"), align="r", shadow=False,
                  scale=min(1.0, pop(k_lines[0]) + 0.05))
    if k_lines[1] >= 0:
        sc = min(1.0, pop(k_lines[1]) + 0.05)
        ctx.save()
        ctx.translate(0, 100)
        ctx.scale(sc, sc)
        glow(ctx, 0, 0, 200, (1, 0.85, 0.3), 0.6)
        block(ctx, -200, -70, 400, 140, 70, hexc("#ffcc33"), 6)
        bold_text(ctx, "ACHIEVEMENT", 0, -28, 30, hexc("#b07a10"), outline=(1, 1, 1), shadow=False, stroke=0.1)
        bold_text(ctx, "SAVED SUMMER", 0, 22, 40, (1, 1, 1))
        ctx.restore()
    ctx.restore()


def trade_window(ctx, x, y, s=1.0, k=1.0, offer="10 ROBUX", want="ZOMBIE KID"):
    if k < 0:
        return
    sc = s * (pop(k) if k < 0.6 else 1.0)
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(sc, sc)
    block(ctx, -300, -170, 600, 340, 22, hexc("#1e2230"), 6)
    bold_text(ctx, "TRADE REQUEST", 0, -130, 36, (1, 1, 1), shadow=False)
    for i, (t, v) in enumerate((("THEY OFFER", offer), ("THEY WANT", want))):
        xx = -150 + i * 300
        block(ctx, xx - 130, -90, 260, 160, 16, hexc("#2c3350"), 3, gloss=False)
        bold_text(ctx, t, xx, -60, 22, hexc("#9aa0b8"), shadow=False, stroke=0.0)
        bold_text(ctx, v, xx, 10, 30, hexc("#ffd84a"), shadow=False, stroke=0.0)
    block(ctx, -230, 100, 200, 54, 14, hexc("#4fd16a"), 4)
    bold_text(ctx, "ACCEPT", -130, 127, 26, (1, 1, 1), shadow=False)
    block(ctx, 30, 100, 200, 54, 14, hexc("#e8323a"), 4)
    bold_text(ctx, "DECLINE", 130, 127, 26, (1, 1, 1), shadow=False)
    ctx.restore()


def level_pill(ctx, x, y, n, s=1.0, col="#4fd16a", k=1.0, txt=None):
    """'LVL n' pill (a number badge over a head)."""
    if k < 0:
        return
    sc = s * (pop(k) if k < 0.6 else 1.0)
    t = txt or f"LVL {n}"
    w = text_width(ctx, t, 34) + 50
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(sc, sc)
    block(ctx, -w / 2, -30, w, 60, 30, hexc(col), 5)
    bold_text(ctx, t, 0, 0, 34, (1, 1, 1), shadow=False)
    ctx.restore()


def command_bar(ctx, x, y, w, txt, T=0.0, t0=0.0, cps=18):
    """The chat command bar: a dark field with a typed command and a blinking caret."""
    shown = txt[:max(0, int((T - t0) * cps))] if T >= t0 else ""
    block(ctx, x - w / 2, y - 40, w, 80, 20, hexc("#1e2230"), 5)
    bold_text(ctx, shown, x - w / 2 + 30, y, 40, (1, 1, 1), align="l", shadow=False, stroke=0.0)
    if int(T * 3) % 2 == 0:
        cx = x - w / 2 + 34 + text_width(ctx, shown, 40)
        block(ctx, cx, y - 24, 6, 48, 2, (1, 1, 1), 0, gloss=False)


def book(ctx, x, y, s=1.0, T=0.0, flip=0.0):
    """An open book; flip 0..1 turns a page."""
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s, s)
    block(ctx, -250, -20, 500, 40, 10, hexc("#2f6bd8"), 5)
    for side in (-1, 1):
        ctx.move_to(0, 0)
        ctx.curve_to(side * 80, -40, side * 180, -40, side * 240, -10)
        ctx.line_to(side * 240, -220)
        ctx.curve_to(side * 180, -250, side * 80, -250, 0, -210)
        ctx.close_path()
        shape_fill(ctx, (1, 1, 1), 5, -250, 0)
        for i in range(6):
            ctx.move_to(side * 40, -180 + i * 26)
            ctx.line_to(side * 200, -180 + i * 26)
        ctx.set_source_rgba(*hexc("#9aa0b8"), 1)
        ctx.set_line_width(3)
        ctx.stroke()
    if 0 < flip < 1:
        a = flip * PI
        ctx.move_to(0, 0)
        ctx.line_to(240 * math.cos(a), -10 - 60 * math.sin(a))
        ctx.line_to(240 * math.cos(a), -220 - 60 * math.sin(a))
        ctx.line_to(0, -210)
        ctx.close_path()
        shape_fill(ctx, hexc("#f4f0ff"), 4, -280, 0)
    ctx.restore()


def family_car(ctx, x, y, s=1.0, T=0.0, col="#4f8bff", driver=None):
    """A blocky family car, side view facing right; (x, y) = ground under its middle. driver(ctx, hx, hy) draws
    a head in the window."""
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s, s)
    c = hexc(col)
    block(ctx, -100, -230, 230, 110, 26, c, 6)
    block(ctx, -80, -215, 90, 80, 12, hexc("#bfe7ff"), 4, gloss=False)
    block(ctx, 22, -215, 90, 80, 12, hexc("#bfe7ff"), 4, gloss=False)
    ctx.restore()
    if driver:
        driver(ctx, x + 66 * s, y - 175 * s)
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s, s)
    block(ctx, -220, -140, 450, 100, 24, c, 6)
    block(ctx, 200, -110, 30, 30, 8, hexc("#ffe9a8"), 3, gloss=False)
    for wx in (-130, 130):
        ctx.new_sub_path()
        ctx.arc(wx, -40, 46, 0, 2 * PI)
        shape_fill(ctx, hexc("#2b2f45"), 5, -86, 6)
        ctx.new_sub_path()
        ctx.arc(wx, -40, 20, 0, 2 * PI)
        ctx.set_source_rgb(*hexc("#c9cde0"))
        ctx.fill()
    ctx.restore()


def crown(ctx, x, y, s=1.0, T=0.0):
    """A floating gold crown."""
    ctx.save()
    ctx.translate(x, y + math.sin(T * 3) * 6)
    ctx.scale(s, s)
    glow(ctx, 0, 0, 200, (1, 0.85, 0.3), 0.55)
    ctx.move_to(-110, 60)
    ctx.line_to(-120, -50)
    ctx.line_to(-60, 0)
    ctx.line_to(0, -80)
    ctx.line_to(60, 0)
    ctx.line_to(120, -50)
    ctx.line_to(110, 60)
    ctx.close_path()
    shape_fill(ctx, hexc("#ffcc33"), 7, -80, 60)
    for dx in (-60, 0, 60):
        ctx.new_sub_path()
        ctx.arc(dx, 30, 12, 0, 2 * PI)
        ctx.set_source_rgb(*hexc("#e8323a"))
        ctx.fill()
    ctx.restore()


def loading_ring(ctx, x, y, r, T, a=1.0):
    """A big loading spinner (a ring of fading dots)."""
    for i in range(12):
        ang = i * PI / 6 + T * 4
        ctx.new_sub_path()
        ctx.arc(x + math.cos(ang) * r, y + math.sin(ang) * r, r * 0.12, 0, 2 * PI)
        ctx.set_source_rgba(1, 1, 1, a * (0.15 + 0.85 * (i / 11)))
        ctx.fill()


def calendar(ctx, x, y, s=1.0, top="FRIDAY", big="?", col="#e8323a"):
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s, s)
    block(ctx, -150, -170, 300, 340, 20, (1, 1, 1), 6)
    block(ctx, -150, -170, 300, 90, 20, hexc(col), 6)
    bold_text(ctx, top, 0, -125, 40, (1, 1, 1), shadow=False)
    bold_text(ctx, big, 0, 40, 150, hexc(col), shadow=False)
    ctx.restore()

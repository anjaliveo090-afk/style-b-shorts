"""Style B sets, props, game UI and FX (style_bible.md sections 5-7).

Everything is flat vector with self-coloured outlines (style.line_of) and the soft
top-light gradient of style.block, in the measured palette. Coordinates are in the
720x1280 world; functions take (ctx, ...) and draw in place.

Groups:
  text      label (story captions/stickers; safezone wraps it), bold_text, day_text, counter
  rooms     night_bedroom, day_room, kitchen, doorway, gamer_desk, desk_close
  props     laptop, monitor, keyboard, alarm_clock, phone, cake, padlock, sticky_note, fridge, energy_can
  game      game_sky, block_clouds, baseplate, spawn_pad, brick_wall, lava, platform, obby, finish_flag,
            arena, throne_room, coin, coin_pile, egg, pet, chest
  UI        hud_timer, second_card, stage_pill, health_bar, damage_text, ko_sticker, toast, login_screen,
            leaderboard, shop_grid, gamepass_card, comments_sheet, subscribe_button, joystick_ui, cursor
  FX        burst, glow, tint, flash, vignette, speed_lines, shockwave, impact_star, sparkles, confetti,
            hearts, poof, rewind_bars, red_x, check_mark (+ style.sweat / anger_mark / shake_lines)"""
import math
import random

import cairo

from engine import H, PI, W, clamp, ease, ellipse, hexc, lerp, pop, rrect
from style import (FONT, INK, block, dark, light, line_of, mix, shape_fill, sparkle, star_path)

YELLOW, GREEN, RED, BLUE, PINK, PURPLE, GOLD = (hexc(c) for c in (
    "#ffd84a", "#4fd16a", "#ff4f5a", "#2f6bd8", "#ff5fb0", "#9d5cff", "#ffcc33"))
UI_DARK = hexc("#1e2230")


def c_(c):
    return hexc(c) if isinstance(c, str) else c


# ================================================================ text
def _font(ctx, size, font=FONT):
    ctx.select_font_face(font, cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
    ctx.set_font_size(size)


def bold_text(ctx, s, x, y, size, fill=(1, 1, 1), outline=INK, scale=1.0, tilt=0.0, shadow=True, stroke=0.22,
              font=FONT, align="c"):
    """Game-style caption text: heavy font, thick dark outline, drop shadow."""
    if scale <= 0.01 or not s:
        return
    ctx.save()
    ctx.translate(x, y)
    ctx.rotate(tilt)
    ctx.scale(scale, scale)
    _font(ctx, size, font)
    e = ctx.text_extents(s)
    ox = {"c": -e.width / 2, "l": 0, "r": -e.width}[align] - e.x_bearing
    oy = -e.height / 2 - e.y_bearing
    ctx.set_line_join(cairo.LINE_JOIN_ROUND)
    if shadow:
        ctx.move_to(ox + size * 0.04, oy + size * 0.09)
        ctx.text_path(s)
        ctx.set_source_rgba(0, 0, 0, 0.35)
        ctx.set_line_width(size * stroke)
        ctx.stroke_preserve()
        ctx.fill()
    ctx.move_to(ox, oy)
    ctx.text_path(s)
    ctx.set_source_rgb(*c_(outline))
    ctx.set_line_width(size * stroke)
    ctx.stroke_preserve()
    ctx.set_source_rgb(*c_(fill))
    ctx.fill()
    ctx.restore()


def text_width(ctx, s, size, font=FONT):
    ctx.save()
    _font(ctx, size, font)
    w = ctx.text_extents(s).width
    ctx.restore()
    return w


def label(ctx, s, x, y, size, bg=None, fg=(1, 1, 1), scale=1.0, tilt=-0.04):
    """Story caption / sticker. bg=None: big outlined game text in colour fg;
    bg given: a rounded sticker pill with white text. safezone.fit keeps these on screen."""
    if scale <= 0.01:
        return
    if bg is None:
        bold_text(ctx, s, x, y, size, c_(fg), scale=scale, tilt=tilt)
        return
    bg = c_(bg)
    ctx.save()
    ctx.translate(x, y)
    ctx.rotate(tilt)
    ctx.scale(scale, scale)
    w = text_width(ctx, s, size) + size * 0.9
    h = size * 1.45
    rrect(ctx, -w / 2 + size * 0.06, -h / 2 + size * 0.12, w, h, h * 0.32)
    ctx.set_source_rgba(0, 0, 0, 0.3)
    ctx.fill()
    block(ctx, -w / 2, -h / 2, w, h, h * 0.32, bg, size * 0.1, outline=INK)
    bold_text(ctx, s, 0, 0, size, c_(fg), shadow=False, stroke=0.16)
    ctx.restore()


def day_text(ctx, s, x, y, k, size=110, fill=YELLOW, T=0.0):
    """Hand-painted chapter text ('DAY 2') with an underline swoosh. k = time since the pop (s)."""
    if k < 0:
        return
    sc = pop(k)
    ctx.save()
    ctx.translate(x, y)
    ctx.rotate(-0.06 + 0.01 * math.sin(T * 3))
    ctx.scale(sc, sc)
    # underline swoosh draws on
    w = text_width(ctx, s, size) * 1.05
    p = ease(k / 0.35)
    ctx.move_to(-w / 2, size * 0.62)
    ctx.curve_to(-w / 6, size * 0.5, w / 6, size * 0.58, lerp(-w / 2, w / 2, p), size * 0.48)
    ctx.set_source_rgb(*INK)
    ctx.set_line_width(size * 0.14)
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    ctx.stroke_preserve()
    ctx.set_source_rgb(*c_(fill))
    ctx.set_line_width(size * 0.07)
    ctx.stroke()
    ctx.save()
    ctx.transform(cairo.Matrix(1, 0, -0.12, 1, 0, 0))   # slight italic brush feel
    bold_text(ctx, s, 0, 0, size, c_(fill), stroke=0.26)
    _font(ctx, size)
    e = ctx.text_extents(s)
    ctx.move_to(-e.width / 2 - e.x_bearing + size * 0.06, -size * 0.18)   # paint highlight streak
    ctx.line_to(-e.width / 2 - e.x_bearing + e.width * 0.5, -size * 0.24)
    ctx.set_source_rgba(1, 1, 1, 0.55)
    ctx.set_line_width(size * 0.05)
    ctx.stroke()
    ctx.restore()
    ctx.restore()


def counter(ctx, value, x, y, size, fill=(1, 1, 1), prefix="", suffix=""):
    bold_text(ctx, f"{prefix}{int(value):,}{suffix}", x, y, size, fill)


# ================================================================ FX
def tint(ctx, rgb, a):
    if a > 0:
        ctx.set_source_rgba(*c_(rgb), a)
        ctx.rectangle(-3000, -5000, 7000, 10000)
        ctx.fill()


def flash(ctx, a):
    tint(ctx, (1, 1, 1), clamp(a))


def glow(ctx, x, y, r, rgb, a):
    g = cairo.RadialGradient(x, y, 0, x, y, r)
    g.add_color_stop_rgba(0, *c_(rgb), a)
    g.add_color_stop_rgba(1, *c_(rgb), 0)
    ctx.set_source(g)
    ctx.arc(x, y, r, 0, 2 * PI)
    ctx.fill()


def vignette(ctx, rgb, a, cx=W / 2, cy=H / 2):
    g = cairo.RadialGradient(cx, cy, H * 0.25, cx, cy, H * 0.8)
    g.add_color_stop_rgba(0, *c_(rgb), 0)
    g.add_color_stop_rgba(1, *c_(rgb), a)
    ctx.set_source(g)
    ctx.rectangle(-3000, -5000, 7000, 10000)
    ctx.fill()


def burst(ctx, T, c1="#ffe27a", c2="#f29a2e", cx=W / 2, cy=H * 0.45, n=18, spin=0.15, glow_a=0.6):
    """Radial ray background (gold reward, red alarm, purple legendary, blue calm)."""
    c1, c2 = c_(c1), c_(c2)
    ctx.set_source_rgb(*c2)
    ctx.rectangle(-3000, -5000, 7000, 10000)
    ctx.fill()
    a0 = T * spin
    for i in range(n):
        a = a0 + i * 2 * PI / n
        ctx.move_to(cx, cy)
        ctx.line_to(cx + math.cos(a) * 3000, cy + math.sin(a) * 3000)
        ctx.line_to(cx + math.cos(a + PI / n) * 3000, cy + math.sin(a + PI / n) * 3000)
        ctx.close_path()
    ctx.set_source_rgba(*c1, 0.55)
    ctx.fill()
    glow(ctx, cx, cy, 520, light(c1, 0.5), glow_a)


def dark_glow_bg(ctx, T, glow_col="#ffcc33", base="#1b1426", cx=W / 2, cy=H * 0.45):
    """Dark scene with a golden glow and soft rays (secret item reveal)."""
    ctx.set_source_rgb(*c_(base))
    ctx.rectangle(-3000, -5000, 7000, 10000)
    ctx.fill()
    for i in range(12):
        a = T * 0.1 + i * PI / 6
        ctx.move_to(cx, cy)
        ctx.line_to(cx + math.cos(a) * 2000, cy + math.sin(a) * 2000)
        ctx.line_to(cx + math.cos(a + 0.12) * 2000, cy + math.sin(a + 0.12) * 2000)
        ctx.close_path()
    ctx.set_source_rgba(*c_(glow_col), 0.12)
    ctx.fill()
    glow(ctx, cx, cy, 560, c_(glow_col), 0.5)
    sparkles(ctx, T, cx, cy, spread=460, n=18, seed=11, c=c_(glow_col))


def speed_lines(ctx, T, cx=W / 2, cy=H / 2, n=34, r0=280, r1=1600, a=0.6, col=(1, 1, 1), seed=5):
    rnd = random.Random(seed + int(T * 24))
    for _ in range(n):
        ang = rnd.uniform(0, 2 * PI)
        w = rnd.uniform(0.008, 0.02)
        r = r0 + rnd.uniform(0, 120)
        ctx.move_to(cx + math.cos(ang) * r, cy + math.sin(ang) * r)
        ctx.line_to(cx + math.cos(ang - w) * r1, cy + math.sin(ang - w) * r1)
        ctx.line_to(cx + math.cos(ang + w) * r1, cy + math.sin(ang + w) * r1)
        ctx.close_path()
    ctx.set_source_rgba(*col, a)
    ctx.fill()


def shockwave(ctx, x, y, k, col=(1, 1, 1), r_max=420, ry=0.42):
    """Expanding flat ring (behind 'SECOND N' cards, on impacts). k: 0..1."""
    if not 0 < k < 1:
        return
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(1, ry)
    ctx.arc(0, 0, r_max * ease(k), 0, 2 * PI)
    ctx.set_source_rgba(*col, 0.9 * (1 - k))
    ctx.set_line_width(26 * (1 - k) + 4)
    ctx.stroke()
    ctx.restore()


def impact_star(ctx, x, y, r, k, txt=None, c1="#fff3a8", c2="#ffb02e", spikes=12):
    """Comic impact burst with optional 'BONK!' text; k = time since impact (s)."""
    if k < 0 or k > 0.7:
        return
    sc = pop(k) * (1 - clamp((k - 0.5) / 0.2))
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(sc, sc)
    star_path(ctx, 0, 0, r, inner=0.55, n=spikes, rot=k * 0.6)
    shape_fill(ctx, c_(c2), r * 0.06, -r, r, outline=INK)
    star_path(ctx, 0, 0, r * 0.62, inner=0.6, n=spikes, rot=k * 0.6 + 0.2)
    ctx.set_source_rgb(*c_(c1))
    ctx.fill()
    ctx.restore()
    if txt:
        bold_text(ctx, txt, x, y, r * 0.55, YELLOW, scale=sc, tilt=-0.15)


def sparkles(ctx, T, cx, cy, spread=300, n=12, seed=3, c=(1, 1, 1), size=18):
    rnd = random.Random(seed)
    for i in range(n):
        x = cx + rnd.uniform(-spread, spread)
        y = cy + rnd.uniform(-spread, spread) * 0.8
        ph = (T * rnd.uniform(0.8, 1.6) + rnd.random()) % 1
        a = math.sin(ph * PI)
        sparkle(ctx, x, y, size * (0.4 + a), a, c=c_(c))


def confetti(ctx, T, t0, n=40, seed=4, x0=0, x1=W, y0=-50):
    if T < t0:
        return
    rnd = random.Random(seed)
    cols = [YELLOW, GREEN, RED, BLUE, PINK, PURPLE]
    for i in range(n):
        x = rnd.uniform(x0, x1) + math.sin(T * 3 + i) * 20
        y = y0 + (T - t0) * rnd.uniform(300, 600) + rnd.uniform(-300, 0)
        ctx.save()
        ctx.translate(x, y)
        ctx.rotate(T * rnd.uniform(2, 6) + i)
        ctx.rectangle(-7, -4, 14, 8)
        ctx.set_source_rgb(*cols[i % len(cols)])
        ctx.fill()
        ctx.restore()


def hearts(ctx, T, t0, x, y, n=6, seed=8):
    if T < t0:
        return
    rnd = random.Random(seed)
    for i in range(n):
        ph = clamp((T - t0 - i * 0.08) / 1.2)
        if ph <= 0 or ph >= 1:
            continue
        hx = x + rnd.uniform(-120, 120)
        hy = y - ph * 260
        k = 14 * (1 + ph)
        ctx.move_to(hx, hy + k)
        ctx.curve_to(hx - 1.4 * k, hy - 0.2 * k, hx - 0.6 * k, hy - 1.3 * k, hx, hy - 0.45 * k)
        ctx.curve_to(hx + 0.6 * k, hy - 1.3 * k, hx + 1.4 * k, hy - 0.2 * k, hx, hy + k)
        ctx.close_path()
        ctx.set_source_rgba(*RED, 1 - ph)
        ctx.fill()


def poof(ctx, x, y, r, k):
    """White cartoon smoke cloud (transformations, landings). k: 0..1."""
    if not 0 <= k < 1:
        return
    for i in range(9):
        a = i * 2 * PI / 9
        ctx.new_sub_path()
        ctx.arc(x + math.cos(a) * r * (0.5 + k), y + math.sin(a) * r * 0.8 * (0.5 + k), r * 0.65 * (1 - 0.5 * k), 0,
                2 * PI)
    ctx.set_source_rgba(1, 1, 1, 0.95 * (1 - k))
    ctx.fill_preserve()
    ctx.set_source_rgba(*hexc("#c9cde0"), 0.8 * (1 - k))
    ctx.set_line_width(4)
    ctx.stroke()


def dust(ctx, x, y, k, n=5, spread=60, r=26):
    if not 0 <= k < 1:
        return
    for i in range(n):
        ctx.new_sub_path()
        ctx.arc(x + (i - (n - 1) / 2) * spread * (1 + k), y - k * 20, r * (1 + k), 0, 2 * PI)
    ctx.set_source_rgba(1, 1, 1, 0.75 * (1 - k))
    ctx.fill()


def red_x(ctx, x, y, r, k):
    """Big red X that draws on (k 0..1)."""
    if k <= 0:
        return
    k = clamp(k)
    for (ax, ay, bx, by), kk in (((-1, -1, 1, 1), clamp(k * 2)), ((1, -1, -1, 1), clamp(k * 2 - 1))):
        if kk <= 0:
            continue
        ctx.move_to(x + ax * r, y + ay * r)
        ctx.line_to(x + lerp(ax, bx, kk) * r, y + lerp(ay, by, kk) * r)
        ctx.set_line_cap(cairo.LINE_CAP_ROUND)
        ctx.set_source_rgb(*INK)
        ctx.set_line_width(r * 0.42)
        ctx.stroke_preserve()
        ctx.set_source_rgb(*hexc("#e8323a"))
        ctx.set_line_width(r * 0.28)
        ctx.stroke()


def check_mark(ctx, x, y, r, k, col=GREEN):
    if k <= 0:
        return
    sc = pop(k)
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(sc, sc)
    ctx.arc(0, 0, r, 0, 2 * PI)
    shape_fill(ctx, c_(col), r * 0.08, -r, r, outline=INK)
    ctx.move_to(-r * 0.45, 0)
    ctx.line_to(-r * 0.1, r * 0.35)
    ctx.line_to(r * 0.5, -r * 0.35)
    ctx.set_source_rgb(1, 1, 1)
    ctx.set_line_width(r * 0.22)
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    ctx.set_line_join(cairo.LINE_JOIN_ROUND)
    ctx.stroke()
    ctx.restore()


def rewind_bars(ctx, k):
    """Screen-space 'REWIND' smear for the loop ending (k 0..1)."""
    if k <= 0:
        return
    rnd = random.Random(int(k * 30))
    for i in range(14):
        y = rnd.uniform(0, H)
        ctx.rectangle(0, y, W, rnd.uniform(4, 30))
    ctx.set_source_rgba(1, 1, 1, 0.25 * math.sin(PI * clamp(k)))
    ctx.fill()
    bold_text(ctx, "<< REWIND", 140, 200, 34, (1, 1, 1), align="l", scale=1.0)


# ================================================================ rooms
def _wall_stars(ctx, x0, y0, x1, y1, seed=1, a=0.35):
    rnd = random.Random(seed)
    for _ in range(int((x1 - x0) * (y1 - y0) / 9000)):
        sparkle(ctx, rnd.uniform(x0, x1), rnd.uniform(y0, y1), rnd.uniform(4, 7), a)


def window(ctx, x, y, w, h, T, night=True, curtain="#2b9a9a"):
    """Window with sky (night: moon + skyline) and side curtains."""
    rrect(ctx, x - 10, y - 10, w + 20, h + 20, 6)
    shape_fill(ctx, hexc("#e9e4f5") if not night else hexc("#cfd2ee"), 4, y, y + h)
    ctx.save()
    ctx.rectangle(x, y, w, h)
    ctx.clip()
    g = cairo.LinearGradient(0, y, 0, y + h)
    if night:
        g.add_color_stop_rgb(0, *hexc("#0b1040"))
        g.add_color_stop_rgb(1, *hexc("#2a2f7a"))
    else:
        g.add_color_stop_rgb(0, *hexc("#6ec6ff"))
        g.add_color_stop_rgb(1, *hexc("#c4ecff"))
    ctx.set_source(g)
    ctx.paint()
    if night:
        ctx.new_sub_path()
        ctx.arc(x + w * 0.42, y + h * 0.3, w * 0.16, 0, 2 * PI)
        ctx.new_sub_path()
        ctx.arc_negative(x + w * 0.49, y + h * 0.26, w * 0.14, 2 * PI, 0)
        ctx.set_source_rgb(*hexc("#f6e7a8"))
        ctx.fill()
        _wall_stars(ctx, x, y, x + w, y + h * 0.6, seed=4, a=0.9)
        ctx.move_to(x, y + h)
        for i in range(8):   # skyline
            bx = x + i * w / 7
            ctx.line_to(bx, y + h * (0.72 + 0.1 * ((i * 37) % 3)))
            ctx.line_to(bx + w / 7, y + h * (0.72 + 0.1 * ((i * 37) % 3)))
        ctx.line_to(x + w, y + h)
        ctx.close_path()
        ctx.set_source_rgb(*hexc("#1a1d52"))
        ctx.fill()
        for i in range(6):
            ctx.rectangle(x + 15 + i * w / 6, y + h * 0.84, 6, 8)
        ctx.set_source_rgb(*hexc("#ffd27a"))
        ctx.fill()
    else:
        for cx_, cy_ in ((x + w * 0.3, y + h * 0.3), (x + w * 0.75, y + h * 0.5)):
            rrect(ctx, cx_ - 40, cy_ - 12, 80, 24, 12)
            ctx.set_source_rgb(1, 1, 1)
            ctx.fill()
    ctx.restore()
    ctx.move_to(x + w / 2, y)
    ctx.line_to(x + w / 2, y + h)
    ctx.move_to(x, y + h / 2)
    ctx.line_to(x + w, y + h / 2)
    ctx.set_source_rgb(*hexc("#e9e4f5") if not night else hexc("#b8bce0"))
    ctx.set_line_width(8)
    ctx.stroke()
    if curtain:
        cc = c_(curtain)
        for side in (-1, 1):
            cx_ = x - 30 if side < 0 else x + w - 20
            rrect(ctx, cx_, y - 30, 50, h + 80, 10)
            shape_fill(ctx, cc, 4, y, y + h)


def poster(ctx, x, y, s=1.0, col="#7ccf6a", tilt=0.04):
    """Simple framed poster with a little block-dino silhouette (generic, no logo)."""
    ctx.save()
    ctx.translate(x, y)
    ctx.rotate(tilt)
    ctx.scale(s, s)
    block(ctx, -55, -70, 110, 140, 6, c_(col), 4)
    ctx.move_to(-30, 40)
    ctx.line_to(-30, -5)
    ctx.curve_to(-30, -35, 20, -35, 20, -15)
    ctx.line_to(30, -15)
    ctx.line_to(30, 5)
    ctx.line_to(10, 5)
    ctx.line_to(10, 40)
    ctx.line_to(-5, 40)
    ctx.line_to(-5, 10)
    ctx.line_to(-15, 10)
    ctx.line_to(-15, 40)
    ctx.close_path()
    ctx.set_source_rgb(*dark(c_(col), 0.45))
    ctx.fill()
    ctx.restore()


def door(ctx, x, y, w, h, open_frac=0.0, col="#7a4f8f", light_col="#f2c46a"):
    """Door (bottom-left at x, y). An open door shows a warm lit hallway and spills light."""
    lc = c_(light_col)
    rrect(ctx, x - 12, y - h - 12, w + 24, h + 12, 6)
    shape_fill(ctx, hexc("#3a2f6a"), 4, y - h, y)
    if open_frac > 0:
        g = cairo.LinearGradient(0, y - h, 0, y)
        g.add_color_stop_rgb(0, *light(lc, 0.2))
        g.add_color_stop_rgb(1, *dark(lc, 0.15))
        ctx.rectangle(x, y - h, w, h)
        ctx.set_source(g)
        ctx.fill()
        rrect(ctx, x + w * 0.35, y - h + 20, w * 0.3, 14, 7)   # hallway ceiling lamp
        ctx.set_source_rgb(1, 0.97, 0.85)
        ctx.fill()
        glow(ctx, x + w / 2, y - h + 30, w * 0.7, (1, 0.95, 0.7), 0.6)
        ctx.move_to(x, y)
        ctx.line_to(x + w, y)
        ctx.line_to(x + w + 260 * open_frac, y + 420)
        ctx.line_to(x - 60 * open_frac, y + 420)
        ctx.close_path()
        ctx.set_source_rgba(*lc, 0.28 * open_frac)
        ctx.fill()
    dw = w * (1 - 0.85 * open_frac)
    if dw > 4:
        block(ctx, x + w - dw if open_frac > 0 else x, y - h, dw, h, 4, c_(col), 4, gloss=False)
        ctx.new_sub_path()
        ctx.arc(x + w - dw + 18 if open_frac > 0 else x + w - 22, y - h * 0.48, 8, 0, 2 * PI)
        shape_fill(ctx, GOLD, 3, y - h * 0.5, y - h * 0.46)


def lamp(ctx, x, y, s=1.0, on=1.0):
    block(ctx, x - 10 * s, y - 70 * s, 20 * s, 70 * s, 4, hexc("#8a6a4a"), 3, gloss=False)
    ctx.move_to(x - 45 * s, y - 70 * s)
    ctx.line_to(x - 28 * s, y - 130 * s)
    ctx.line_to(x + 28 * s, y - 130 * s)
    ctx.line_to(x + 45 * s, y - 70 * s)
    ctx.close_path()
    shape_fill(ctx, hexc("#f7e2a6"), 4, y - 130 * s, y - 70 * s)
    if on:
        glow(ctx, x, y - 100 * s, 220 * s, (1, 0.88, 0.55), 0.4 * on)
        ctx.move_to(x - 45 * s, y - 70 * s)
        ctx.line_to(x + 45 * s, y - 70 * s)
        ctx.line_to(x + 180 * s, y + 400 * s)
        ctx.line_to(x - 180 * s, y + 400 * s)
        ctx.close_path()
        ctx.set_source_rgba(1, 0.88, 0.55, 0.12 * on)
        ctx.fill()


def rug(ctx, x, y, rx, ry, col="#1d8381"):
    ellipse(ctx, x, y, rx, ry)
    shape_fill(ctx, c_(col), 5, y - ry, y + ry)
    ellipse(ctx, x, y, rx * 0.85, ry * 0.78)
    ctx.set_source_rgb(*light(c_(col), 0.18))
    ctx.set_line_width(5)
    ctx.stroke()


def checker(ctx, x, y, w, h, n=6, c1="#e58747", c2="#339891"):
    sz = w / n
    rows = int(h / sz) + 1
    ctx.save()
    rrect(ctx, x, y, w, h, 10)
    ctx.clip()
    for i in range(n):
        for j in range(rows):
            ctx.rectangle(x + i * sz, y + j * sz, sz + 0.5, sz + 0.5)
            ctx.set_source_rgb(*c_(c1 if (i + j) % 2 else c2))
            ctx.fill()
    g = cairo.LinearGradient(0, y, 0, y + h)
    g.add_color_stop_rgba(0, 1, 1, 1, 0.12)
    g.add_color_stop_rgba(1, 0, 0, 0, 0.2)
    ctx.rectangle(x, y, w, h)
    ctx.set_source(g)
    ctx.fill()
    ctx.restore()
    rrect(ctx, x, y, w, h, 10)
    ctx.set_source_rgb(*INK)
    ctx.set_line_width(4)
    ctx.stroke()


def bed(ctx, x, y, w=420, blanket=("#e58747", "#339891")):
    """Bed seen from the side-front; (x, y) = bottom-left on the floor."""
    block(ctx, x, y - 330, 50, 330, 8, hexc("#8a5a3a"), 4)                 # headboard
    block(ctx, x + 10, y - 150, w, 110, 10, hexc("#8a5a3a"), 4)            # frame
    rrect(ctx, x + 40, y - 230, 130, 60, 26)                               # pillow
    shape_fill(ctx, hexc("#f1eef8"), 4, y - 230, y - 170)
    checker(ctx, x + 60, y - 210, w - 50, 140, n=7, c1=blanket[0], c2=blanket[1])
    block(ctx, x + w - 10, y - 60, 30, 60, 4, hexc("#6b4430"), 4, gloss=False)


def nightstand(ctx, x, y, s=1.0):
    block(ctx, x - 70 * s, y - 120 * s, 140 * s, 120 * s, 8 * s, hexc("#8a5a3a"), 4)
    block(ctx, x - 55 * s, y - 95 * s, 110 * s, 40 * s, 5 * s, hexc("#a06e48"), 3, gloss=False)
    ctx.new_sub_path()
    ctx.arc(x, y - 75 * s, 6 * s, 0, 2 * PI)
    ctx.set_source_rgb(*GOLD)
    ctx.fill()


def floor(ctx, y, col="#3e2e3e", plank="#4a3848"):
    ctx.rectangle(-3000, y, 7000, 3000)
    ctx.set_source_rgb(*c_(col))
    ctx.fill()
    for i in range(-20, 30):
        ctx.move_to(i * 90, y)
        ctx.line_to(i * 90 + (i * 90 - 360) * 1.2, y + 1200)
    ctx.set_source_rgba(*c_(plank), 0.7)
    ctx.set_line_width(3)
    ctx.stroke()


def night_wall(ctx, y_floor=1050, wall="#272b6d"):
    g = cairo.LinearGradient(0, -400, 0, y_floor)
    g.add_color_stop_rgb(0, *dark(c_(wall), 0.12))
    g.add_color_stop_rgb(1, *light(c_(wall), 0.05))
    ctx.rectangle(-3000, -5000, 7000, 5000 + y_floor)
    ctx.set_source(g)
    ctx.fill()
    _wall_stars(ctx, -300, -300, 1100, y_floor - 50, seed=2, a=0.3)
    ctx.rectangle(-3000, y_floor - 20, 7000, 20)
    ctx.set_source_rgb(*hexc("#1c1f52"))
    ctx.fill()


def night_bedroom(ctx, T, door_open=1.0, lamp_on=True, y_floor=1050, door_x=520, stand_x=430):
    """The kid's room at night (home base): window + moon, poster, bed, nightstand, lamp, rug, door.
    door_x / stand_x move the door and the nightstand (e.g. door_x=360, stand_x=640 to put mom in the
    doorway right behind the bed)."""
    night_wall(ctx, y_floor)
    floor(ctx, y_floor)
    window(ctx, 40, 230, 230, 300, T, night=True)
    poster(ctx, 360 if door_x > 450 else 610, 330, 0.9)
    door(ctx, door_x, y_floor, 170, 400, open_frac=door_open)
    bed(ctx, -20, y_floor + 40, w=380)
    nightstand(ctx, stand_x, y_floor + 10, 0.9)
    if lamp_on:
        lamp(ctx, stand_x + 25, y_floor - 98, 0.75, on=1.0)
    rug(ctx, 330, y_floor + 190, 300, 70)


def day_room(ctx, T, y_floor=1050, wall="#f6e2b4"):
    g = cairo.LinearGradient(0, -400, 0, y_floor)
    g.add_color_stop_rgb(0, *light(c_(wall), 0.1))
    g.add_color_stop_rgb(1, *dark(c_(wall), 0.05))
    ctx.rectangle(-3000, -5000, 7000, 5000 + y_floor)
    ctx.set_source(g)
    ctx.fill()
    window(ctx, 220, 220, 280, 320, T, night=False)
    glow(ctx, 360, 380, 420, (1, 0.97, 0.8), 0.35)
    floor(ctx, y_floor, "#c99a6a", "#b8875a")
    rug(ctx, 360, y_floor + 180, 300, 70, "#ff8fa3")


def kitchen(ctx, T, night=True, y_floor=1080):
    """Kitchen: tiled wall, counter with cabinets, fridge on the right, window."""
    wall = hexc("#3b4a8a") if night else hexc("#bfe6e0")
    ctx.rectangle(-3000, -5000, 7000, 5000 + y_floor)
    ctx.set_source_rgb(*wall)
    ctx.fill()
    for i in range(-10, 20):     # tiles
        for j in range(4):
            ctx.rectangle(i * 70 + (j % 2) * 35, 620 + j * 70, 66, 66)
    ctx.set_source_rgba(1, 1, 1, 0.07)
    ctx.fill()
    window(ctx, 40, 230, 220, 260, T, night=night, curtain="#ffb84a")
    block(ctx, -100, 820, 520, 40, 6, hexc("#e9e4f5"), 4)                  # counter top
    block(ctx, -90, 860, 500, y_floor - 860, 6, hexc("#ff9f6a"), 4)          # cabinets
    for i in range(3):
        block(ctx, -70 + i * 160, 885, 140, y_floor - 905, 6, hexc("#ffb489"), 3, gloss=False)
    floor(ctx, y_floor, "#5a4a6a", "#6a5a7a")
    fridge(ctx, 560, y_floor, T)
    if night:
        tint(ctx, (0.05, 0.06, 0.25), 0.25)


def fridge(ctx, x, y, T, note=True, note_glow=0.0, w=260, h=640):
    """Fridge (bottom centre x, y) with magnets and optionally a yellow sticky note."""
    block(ctx, x - w / 2, y - h, w, h, 18, hexc("#e9f0ff"), 5)
    ctx.move_to(x - w / 2 + 6, y - h * 0.62)
    ctx.line_to(x + w / 2 - 6, y - h * 0.62)
    ctx.set_source_rgb(*line_of(hexc("#e9f0ff")))
    ctx.set_line_width(5)
    ctx.stroke()
    for hy in (y - h * 0.8, y - h * 0.45):
        block(ctx, x - w / 2 + 22, hy - 40, 16, 80, 8, hexc("#b8c2d8"), 3, gloss=False)
    for mx, my, c in ((x + 40, y - h * 0.9, RED), (x + 90, y - h * 0.75, BLUE), (x + 50, y - h * 0.35, GREEN)):
        ctx.new_sub_path()
        ctx.arc(mx, my, 12, 0, 2 * PI)
        shape_fill(ctx, c, 3, my - 12, my + 12)
    if note:
        if note_glow > 0:
            glow(ctx, x + 10, y - h * 0.72, 200, (1, 0.95, 0.5), 0.7 * note_glow)
        sticky_note(ctx, x + 10, y - h * 0.72, 0.5, [], tilt=0.08)


def sticky_note(ctx, x, y, s, lines, tilt=-0.04, col="#ffe45c", shown=None, size=56):
    """Yellow sticky note with handwritten-looking lines. shown = list of per-line pop times (s since)."""
    if s <= 0.01:
        return
    ctx.save()
    ctx.translate(x, y)
    ctx.rotate(tilt)
    ctx.scale(s, s)
    rrect(ctx, -170 + 10, -170 + 14, 340, 340, 8)
    ctx.set_source_rgba(0, 0, 0, 0.25)
    ctx.fill()
    block(ctx, -170, -170, 340, 340, 8, c_(col), 5)
    rrect(ctx, -60, -190, 120, 40, 4)                  # tape
    ctx.set_source_rgba(1, 1, 1, 0.55)
    ctx.fill()
    n = len(lines)
    for i, ln in enumerate(lines):
        k = 1.0 if shown is None else (shown[i] if i < len(shown) else -1)
        if k is None or k < 0:
            continue
        yy = -((n - 1) * size * 1.15) / 2 + i * size * 1.15
        bold_text(ctx, ln, 0, yy, size, hexc("#2a3a8a"), outline=c_(col), shadow=False, stroke=0.02,
                  scale=pop(k) if k < 1 else 1.0, tilt=0.02 * (i - 1))
    ctx.restore()


def gamer_desk(ctx, T, y_desk=900, night=True):
    """Front view of a desk against the night wall: monitor glow, energy cans, snack bag."""
    night_wall(ctx, 2000) if night else day_room(ctx, T)
    window(ctx, -40, 120, 200, 300, T, night=night)
    poster(ctx, 600, 260, 0.9, tilt=0.06)
    block(ctx, -100, y_desk, 920, 60, 8, hexc("#b9b4d8"), 5)
    block(ctx, -100, y_desk + 60, 920, 700, 0, hexc("#7a6aa8"), 5, gloss=False)
    for i, cx_ in enumerate((40, 80, 600)):
        energy_can(ctx, cx_, y_desk - 4, 0.8)


def energy_can(ctx, x, y, s=1.0, col="#39d26a"):
    block(ctx, x - 22 * s, y - 80 * s, 44 * s, 80 * s, 8 * s, c_(col), 3)
    rrect(ctx, x - 16 * s, y - 52 * s, 32 * s, 26 * s, 4 * s)
    ctx.set_source_rgb(*INK)
    ctx.fill()
    _bolt(ctx, x, y - 39 * s, 10 * s, YELLOW)


def _bolt(ctx, cx, cy, k, c):
    pts = [(0.15, -1.0), (-0.45, 0.12), (-0.02, 0.12), (-0.2, 1.0), (0.45, -0.18), (0.03, -0.18), (0.25, -1.0)]
    for i, (px, py) in enumerate(pts):
        (ctx.move_to if i == 0 else ctx.line_to)(cx + px * k, cy + py * k)
    ctx.close_path()
    ctx.set_source_rgb(*c_(c))
    ctx.fill()


# ================================================================ props
def screen_rect(ctx, x, y, w, h, fn, T, r=10):
    """Clip to a screen rectangle and call fn(ctx, x, y, w, h, T) to draw its content."""
    ctx.save()
    rrect(ctx, x, y, w, h, r)
    ctx.clip()
    ctx.set_source_rgb(*hexc("#141a2e"))
    ctx.paint()
    if fn:
        fn(ctx, x, y, w, h, T)
    g = cairo.LinearGradient(x, y, x + w, y + h)   # glass sheen
    g.add_color_stop_rgba(0, 1, 1, 1, 0.12)
    g.add_color_stop_rgba(0.4, 1, 1, 1, 0.0)
    ctx.rectangle(x, y, w, h)
    ctx.set_source(g)
    ctx.fill()
    ctx.restore()


def laptop(ctx, x, y, s, T, fn=None, back=False, col="#2b2f45"):
    """Laptop on a surface; (x, y) = bottom centre. back=True shows the lid back (seen from the front)."""
    w, h = 420 * s, 270 * s
    if back:
        block(ctx, x - w / 2, y - h, w, h, 16 * s, c_(col), 5)
        ctx.new_sub_path()
        ctx.arc(x, y - h / 2, 34 * s, 0, 2 * PI)
        shape_fill(ctx, YELLOW, 4, y - h / 2 - 34 * s, y - h / 2 + 34 * s)
        _bolt(ctx, x, y - h / 2, 24 * s, RED)
        glow(ctx, x, y - h - 40 * s, 260 * s, (0.6, 0.85, 1), 0.35)
        return
    block(ctx, x - w / 2, y - h, w, h, 14 * s, c_(col), 5)
    screen_rect(ctx, x - w / 2 + 16 * s, y - h + 16 * s, w - 32 * s, h - 30 * s, fn, T, 8 * s)
    block(ctx, x - w * 0.6, y - 4 * s, w * 1.2, 26 * s, 10 * s, hexc("#9aa0b8"), 5)


def monitor(ctx, x, y, s, T, fn=None):
    w, h = 560 * s, 340 * s
    block(ctx, x - 20 * s, y - 70 * s, 40 * s, 70 * s, 4, hexc("#3a3f55"), 4, gloss=False)
    block(ctx, x - 90 * s, y - 14 * s, 180 * s, 18 * s, 6, hexc("#3a3f55"), 4, gloss=False)
    block(ctx, x - w / 2, y - 70 * s - h, w, h, 16 * s, hexc("#2b2f45"), 5)
    screen_rect(ctx, x - w / 2 + 16 * s, y - 70 * s - h + 16 * s, w - 32 * s, h - 32 * s, fn, T, 8 * s)


def keyboard(ctx, x, y, s, T, pressed=None, mash=0.0):
    """Keyboard (centre x, y). pressed = index of a key to light up; mash jitters random keys."""
    w, h = 600 * s, 200 * s
    block(ctx, x - w / 2, y - h / 2, w, h, 16 * s, hexc("#3a3f55"), 5)
    rnd = random.Random(int(T * 14))
    k = 0
    for row in range(4):
        for col_ in range(11 - (row == 3) * 6):
            kw = (w - 40 * s) / 11
            kx = x - w / 2 + 20 * s + col_ * kw + (row == 3) * kw * 3
            ky = y - h / 2 + 18 * s + row * 44 * s
            ww = kw - 6 * s if row < 3 else kw * 5 - 6 * s
            hot = (pressed == k) or (mash > 0 and rnd.random() < 0.15 * mash)
            down = 4 * s if hot else 0
            block(ctx, kx, ky + down, ww, 36 * s, 6 * s, hexc("#5ad1ff") if hot else hexc("#e9ecf5"), 2.5,
                  gloss=False)
            k += 1


def alarm_clock(ctx, x, y, s, txt="0:10", T=0.0, ring=0.0, col="#e8323a"):
    """Red digital alarm clock with bells (centre x, y). ring > 0 shakes it."""
    j = math.sin(T * 60) * 6 * s * ring
    ctx.save()
    ctx.translate(x + j, y)
    ctx.rotate(math.sin(T * 50) * 0.06 * ring)
    for side in (-1, 1):
        ctx.new_sub_path()
        ctx.arc(side * 62 * s, -62 * s, 26 * s, 0, 2 * PI)
        shape_fill(ctx, GOLD, 4, -88 * s, -36 * s)
    block(ctx, -95 * s, -70 * s, 190 * s, 140 * s, 26 * s, c_(col), 5)
    rrect(ctx, -72 * s, -45 * s, 144 * s, 66 * s, 10 * s)
    shape_fill(ctx, hexc("#f2ece0"), 4, -45 * s, 21 * s)
    bold_text(ctx, txt, 0, -12 * s, 50 * s, INK, outline=hexc("#f2ece0"), shadow=False, stroke=0.02)
    for i in range(3):
        rrect(ctx, (-40 + i * 30) * s, 34 * s, 22 * s, 12 * s, 4 * s)
        ctx.set_source_rgb(1, 1, 1)
        ctx.fill()
    ctx.restore()


def phone(ctx, x, y, s, T, fn=None, tilt=0.0, col="#2b2f45"):
    """Phone / tablet held upright (centre x, y)."""
    if s <= 0.01:
        return
    ctx.save()
    ctx.translate(x, y)
    ctx.rotate(tilt)
    w, h = 200 * s, 380 * s
    block(ctx, -w / 2, -h / 2, w, h, 26 * s, c_(col), 5)
    screen_rect(ctx, -w / 2 + 12 * s, -h / 2 + 30 * s, w - 24 * s, h - 60 * s, fn, T, 10 * s)
    ctx.restore()


def cake(ctx, x, y, s, T, lit=True):
    """Birthday cake with candles (bottom centre x, y)."""
    block(ctx, x - 150 * s, y - 20 * s, 300 * s, 20 * s, 8 * s, hexc("#e9e4f5"), 4)
    block(ctx, x - 120 * s, y - 150 * s, 240 * s, 130 * s, 20 * s, hexc("#ff8fc8"), 5)
    ctx.move_to(x - 120 * s, y - 120 * s)
    for i in range(9):
        ctx.curve_to(x - 120 * s + (i + 0.3) * 26.6 * s, y - 80 * s, x - 120 * s + (i + 0.7) * 26.6 * s, y - 80 * s,
                     x - 120 * s + (i + 1) * 26.6 * s, y - 120 * s)
    ctx.line_to(x + 120 * s, y - 145 * s)
    ctx.line_to(x - 120 * s, y - 145 * s)
    ctx.close_path()
    shape_fill(ctx, hexc("#fff4f8"), 4, y - 150 * s, y - 90 * s)
    for i in range(3):
        cx_ = x + (i - 1) * 60 * s
        block(ctx, cx_ - 9 * s, y - 220 * s, 18 * s, 75 * s, 5 * s, (BLUE, GREEN, YELLOW)[i], 3, gloss=False)
        if lit:
            f = 1 + 0.15 * math.sin(T * 20 + i)
            ellipse(ctx, cx_, y - 240 * s, 10 * s * f, 18 * s * f)
            shape_fill(ctx, hexc("#ffb02e"), 3, y - 258 * s, y - 222 * s)
            glow(ctx, cx_, y - 240 * s, 50 * s, (1, 0.8, 0.4), 0.5)


def padlock(ctx, x, y, s, k=1.0, open_k=0.0, col="#ffcc33"):
    """Padlock (centre x, y); k = pop scale, open_k lifts the shackle."""
    if k <= 0:
        return
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(k, k)
    ctx.save()
    ctx.translate(0, -open_k * 50 * s)
    ctx.new_sub_path()
    ctx.arc(0, -60 * s, 70 * s, PI, 0)
    ctx.line_to(70 * s, -20 * s)
    ctx.set_source_rgb(*INK)
    ctx.set_line_width(46 * s)
    ctx.stroke_preserve()
    ctx.set_source_rgb(*hexc("#c9cde0"))
    ctx.set_line_width(30 * s)
    ctx.stroke()
    ctx.move_to(-70 * s, -60 * s)
    ctx.line_to(-70 * s, -20 * s)
    ctx.set_source_rgb(*INK)
    ctx.set_line_width(46 * s)
    ctx.stroke_preserve()
    ctx.set_source_rgb(*hexc("#c9cde0"))
    ctx.set_line_width(30 * s)
    ctx.stroke()
    ctx.restore()
    block(ctx, -120 * s, -40 * s, 240 * s, 190 * s, 30 * s, c_(col), 7 * s, outline=INK)
    ctx.new_sub_path()
    ctx.arc(0, 30 * s, 22 * s, 0, 2 * PI)
    ctx.move_to(-10 * s, 40 * s)
    ctx.line_to(10 * s, 40 * s)
    ctx.line_to(14 * s, 100 * s)
    ctx.line_to(-14 * s, 100 * s)
    ctx.close_path()
    ctx.set_source_rgb(*INK)
    ctx.fill()
    ctx.restore()


# ================================================================ game world
def game_sky(ctx, top="#84d4fb", bottom="#b8e8fb"):
    g = cairo.LinearGradient(0, -400, 0, 1100)
    g.add_color_stop_rgb(0, *c_(top))
    g.add_color_stop_rgb(1, *c_(bottom))
    ctx.rectangle(-3000, -5000, 7000, 10000)
    ctx.set_source(g)
    ctx.fill()


def block_clouds(ctx, T, seed=1, y0=60, y1=520, n=5, drift=12):
    rnd = random.Random(seed)
    for _ in range(n):
        x = (rnd.uniform(-200, 900) + T * drift) % 1300 - 300
        y = rnd.uniform(y0, y1)
        w = rnd.uniform(120, 240)
        for dx, dy, ww, hh in ((0, 0, w, 44), (w * 0.2, -30, w * 0.5, 36)):
            rrect(ctx, x + dx, y + dy, ww, hh, 8)
            ctx.set_source_rgb(1, 1, 1)
            ctx.fill_preserve()
            ctx.set_source_rgba(*hexc("#bfe3f5"), 1)
            ctx.set_line_width(3)
            ctx.stroke()


def baseplate(ctx, y, col="#51c844", horizon=None):
    """Studded green baseplate from y down (perspective rows of studs)."""
    c = c_(col)
    ctx.rectangle(-3000, y, 7000, 3000)
    g = cairo.LinearGradient(0, y, 0, y + 600)
    g.add_color_stop_rgb(0, *light(c, 0.08))
    g.add_color_stop_rgb(1, *dark(c, 0.06))
    ctx.set_source(g)
    ctx.fill()
    for row in range(14):
        yy = y + 14 + row * (16 + row * 6)
        sz = 10 + row * 2.4
        for i in range(-12, 24):
            ellipse(ctx, i * (sz * 3.8) + (row % 2) * sz * 1.9, yy, sz, sz * 0.36)
        ctx.set_source_rgba(*light(c, 0.3), 0.8)
        ctx.fill()


def spawn_pad(ctx, x, y, s=1.0, beam=0.0):
    ellipse(ctx, x, y, 110 * s, 30 * s)
    shape_fill(ctx, hexc("#c9cde0"), 4, y - 30 * s, y + 30 * s)
    ellipse(ctx, x, y - 6 * s, 80 * s, 20 * s)
    shape_fill(ctx, hexc("#9fd8ff"), 3, y - 26 * s, y + 14 * s)
    if beam > 0:
        g = cairo.LinearGradient(x - 90 * s, 0, x + 90 * s, 0)
        g.add_color_stop_rgba(0, 0.7, 0.95, 1, 0)
        g.add_color_stop_rgba(0.5, 0.85, 1, 1, 0.75 * beam)
        g.add_color_stop_rgba(1, 0.7, 0.95, 1, 0)
        ctx.rectangle(x - 90 * s, -2000, 180 * s, 2000 + y)
        ctx.set_source(g)
        ctx.fill()


def brick_wall(ctx, x, y, w, h, col="#aaafbc"):
    c = c_(col)
    block(ctx, x, y - h, w, h, 4, c, 5, gloss=False)
    ctx.save()
    ctx.rectangle(x, y - h, w, h)
    ctx.clip()
    for j in range(int(h / 34) + 1):
        for i in range(int(w / 70) + 2):
            ctx.rectangle(x + i * 70 - (j % 2) * 35 + 3, y - h + j * 34 + 3, 64, 28)
    ctx.set_source_rgba(*light(c, 0.12), 1)
    ctx.fill()
    ctx.restore()


def lava(ctx, y, T, c1="#fa801a", c2="#fcab17"):
    ctx.move_to(-3000, 3000)
    ctx.line_to(-3000, y)
    for i in range(-40, 60):
        x = i * 60
        ctx.line_to(x, y + math.sin(i * 0.9 + T * 3) * 10)
    ctx.line_to(4000, y)
    ctx.line_to(4000, 3000)
    ctx.close_path()
    g = cairo.LinearGradient(0, y, 0, y + 300)
    g.add_color_stop_rgb(0, *c_(c2))
    g.add_color_stop_rgb(1, *c_(c1))
    ctx.set_source(g)
    ctx.fill_preserve()
    ctx.set_source_rgb(*hexc("#c8401a"))
    ctx.set_line_width(5)
    ctx.stroke()
    for i in range(6):
        bx = (i * 173 + T * 40) % 900 - 100
        ctx.new_sub_path()
        ctx.arc(bx, y + 60 + (i % 3) * 50, 8 + (i % 2) * 6, 0, 2 * PI)
    ctx.set_source_rgba(1, 0.9, 0.4, 0.8)
    ctx.fill()


def platform(ctx, x, y, w, col="#2cd5fc", depth=26, num=None, h=60):
    """Floating 3D-ish block platform; (x, y) = top-left of the top face."""
    c = c_(col)
    ctx.move_to(x, y)
    ctx.line_to(x + depth, y - depth)
    ctx.line_to(x + w + depth, y - depth)
    ctx.line_to(x + w, y)
    ctx.close_path()
    shape_fill(ctx, light(c, 0.3), 4, y - depth, y)
    ctx.move_to(x + w, y)
    ctx.line_to(x + w + depth, y - depth)
    ctx.line_to(x + w + depth, y + h - depth)
    ctx.line_to(x + w, y + h)
    ctx.close_path()
    shape_fill(ctx, dark(c, 0.2), 4, y, y + h)
    block(ctx, x, y, w, h, 3, c, 4)
    if num is not None:
        bold_text(ctx, str(num), x + w / 2, y + h / 2, h * 0.5, (1, 1, 1), stroke=0.18, shadow=False)


def obby(ctx, T, y_lava=1080, cols=("#2cd5fc", "#fa3a9f", "#f7e04a", "#a694e1", "#4fd16a"), start=1, n=8,
         x0=-40, dx=200, y_top=880, rise=-40):
    """Sky + lava + a run of numbered platforms going right. Returns platform top centres."""
    game_sky(ctx)
    block_clouds(ctx, T)
    lava(ctx, y_lava, T)
    tops = []
    for i in range(n):
        x = x0 + i * dx
        y = y_top + i * rise + (i % 2) * 30
        platform(ctx, x, y, 130 if i else 220, cols[i % len(cols)], num=start + i)
        tops.append((x + (65 if i else 110), y))
    return tops


def finish_flag(ctx, x, y, s, T):
    block(ctx, x - 6 * s, y - 260 * s, 12 * s, 260 * s, 4, hexc("#e9e4f5"), 3, gloss=False)
    sq = 22 * s
    for i in range(6):
        for j in range(4):
            wv = math.sin(T * 6 + i * 0.6) * 6 * s
            ctx.rectangle(x + 6 * s + i * sq, y - 250 * s + j * sq + wv, sq, sq)
            ctx.set_source_rgb(*((1, 1, 1) if (i + j) % 2 else INK))
            ctx.fill()


def arena(ctx, T, y_floor=1000):
    """Boss arena: pink sky, purple castle wall with crenellations, torches, tiled floor + rune circle."""
    g = cairo.LinearGradient(0, -300, 0, y_floor)
    g.add_color_stop_rgb(0, *hexc("#4a1f7a"))
    g.add_color_stop_rgb(1, *hexc("#e0468f"))
    ctx.rectangle(-3000, -5000, 7000, 10000)
    ctx.set_source(g)
    ctx.fill()
    wall = hexc("#6b3fa0")
    block(ctx, -200, y_floor - 380, 1120, 380, 0, wall, 5, gloss=False)
    for i in range(-2, 10):
        block(ctx, i * 120, y_floor - 440, 70, 70, 4, wall, 5, gloss=False)
    for i in range(-2, 10):
        for j in range(5):
            ctx.rectangle(i * 120 + (j % 2) * 60 + 6, y_floor - 370 + j * 72, 108, 64)
    ctx.set_source_rgba(1, 1, 1, 0.06)
    ctx.fill()
    ctx.rectangle(-3000, y_floor, 7000, 3000)
    ctx.set_source_rgb(*hexc("#8d6bd6"))
    ctx.fill()
    for i in range(-20, 30):
        ctx.move_to(i * 80, y_floor)
        ctx.line_to(360 + (i * 80 - 360) * 3, y_floor + 900)
    for j in range(8):
        ctx.move_to(-3000, y_floor + j * j * 14)
        ctx.line_to(4000, y_floor + j * j * 14)
    ctx.set_source_rgba(*hexc("#6a4ab0"), 1)
    ctx.set_line_width(3)
    ctx.stroke()
    ellipse(ctx, 360, y_floor + 120, 230, 60)
    ctx.set_source_rgba(*GOLD, 0.8)
    ctx.set_line_width(8)
    ctx.stroke()
    for tx in (60, 660):
        block(ctx, tx - 12, y_floor - 150, 24, 150, 4, hexc("#5a3a2a"), 3, gloss=False)
        f = 1 + 0.15 * math.sin(T * 17 + tx)
        ellipse(ctx, tx, y_floor - 175, 22 * f, 36 * f)
        shape_fill(ctx, hexc("#ffb02e"), 3, y_floor - 210, y_floor - 140)
        glow(ctx, tx, y_floor - 175, 140, (1, 0.6, 0.2), 0.45)


def throne_room(ctx, T, y_floor=1080):
    burst(ctx, T, "#b07ae8", "#6a2fb0", cy=500, glow_a=0.3)
    for bx in (60, 660):
        block(ctx, bx - 60, -200, 120, 700, 6, hexc("#7a3fb8"), 5, gloss=False)
        star_path(ctx, bx, 300, 34)
        ctx.set_source_rgb(*GOLD)
        ctx.fill()
    ctx.move_to(220, y_floor)
    ctx.line_to(500, y_floor)
    ctx.line_to(620, 1600)
    ctx.line_to(100, 1600)
    ctx.close_path()
    shape_fill(ctx, hexc("#d8283a"), 5, y_floor, 1600)
    block(ctx, 180, 380, 360, 700, 60, GOLD, 6)
    block(ctx, 230, 450, 260, 560, 40, hexc("#b0203a"), 5)


def coin(ctx, x, y, s=1.0, spin=0.0, col="#ffcc33"):
    """Hexagonal game-currency coin (generic), spinning when spin varies."""
    sx = max(0.15, abs(math.cos(spin)))
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(sx, 1)
    for i in range(6):
        a = PI / 6 + i * PI / 3
        (ctx.move_to if i == 0 else ctx.line_to)(math.cos(a) * 34 * s, math.sin(a) * 34 * s)
    ctx.close_path()
    shape_fill(ctx, c_(col), 4 * s, -34 * s, 34 * s, outline=hexc("#a8741a"))
    for i in range(6):
        a = PI / 6 + i * PI / 3
        (ctx.move_to if i == 0 else ctx.line_to)(math.cos(a) * 20 * s, math.sin(a) * 20 * s)
    ctx.close_path()
    ctx.set_source_rgb(*hexc("#e6a92a"))
    ctx.set_line_width(4 * s)
    ctx.stroke()
    ctx.restore()


def coin_pile(ctx, x, y, w, h, T, seed=3):
    rnd = random.Random(seed)
    n = int(w * h / 1800)
    pts = []
    for _ in range(n):
        u = rnd.uniform(-1, 1)
        pts.append((x + u * w / 2, y - rnd.uniform(0, 1) * h * (1 - u * u)))
    for px, py in sorted(pts, key=lambda p: p[1]):
        coin(ctx, px, py, 0.8, spin=rnd.uniform(0, 1))


def egg(ctx, x, y, s, T, crack=0.0, col="#ffcc33", spots="#9d5cff"):
    ctx.save()
    ctx.translate(x, y)
    ctx.rotate(math.sin(T * 30) * 0.08 * crack)
    ctx.move_to(0, -130 * s)
    ctx.curve_to(90 * s, -130 * s, 110 * s, 60 * s, 0, 70 * s)
    ctx.curve_to(-110 * s, 60 * s, -90 * s, -130 * s, 0, -130 * s)
    ctx.close_path()
    shape_fill(ctx, c_(col), 5, -130 * s, 70 * s)
    for dx, dy, r in ((-30, -40, 18), (35, 0, 14), (-10, 30, 12)):
        ctx.new_sub_path()
        ctx.arc(dx * s, dy * s, r * s, 0, 2 * PI)
        ctx.set_source_rgb(*c_(spots))
        ctx.fill()
    if crack > 0:
        ctx.move_to(-70 * s, -30 * s)
        for i in range(6):
            ctx.line_to((-70 + (i + 1) * 23) * s, (-30 + (-18 if i % 2 else 14)) * s)
        ctx.set_source_rgb(*INK)
        ctx.set_line_width(5)
        ctx.stroke()
    ctx.restore()


def chest(ctx, x, y, s, T, open_k=0.0):
    block(ctx, x - 120 * s, y - 130 * s, 240 * s, 130 * s, 10 * s, hexc("#a0623a"), 5)
    ctx.save()
    ctx.translate(x, y - 130 * s)
    ctx.rotate(-open_k * 0.9)
    block(ctx, -120 * s, -80 * s, 240 * s, 80 * s, 26 * s, hexc("#b8743f"), 5)
    ctx.restore()
    block(ctx, x - 22 * s, y - 150 * s, 44 * s, 50 * s, 6 * s, GOLD, 4)
    if open_k > 0:
        glow(ctx, x, y - 170 * s, 260 * s, (1, 0.85, 0.3), 0.8 * open_k)


# ================================================================ UI
def hud_timer(ctx, txt, bump=0.0, urgent=False, y=180):
    """Screen-space timer pill at the top centre (dark; red when 4 or less). Widens for long text."""
    sc = 1 + 0.25 * bump
    ctx.save()
    ctx.translate(W / 2, y)
    ctx.scale(sc, sc)
    w, h = max(200, text_width(ctx, txt, 38) + 116), 62
    rrect(ctx, -w / 2, -h / 2 + 4, w, h, h / 2)
    ctx.set_source_rgba(0, 0, 0, 0.35)
    ctx.fill()
    rrect(ctx, -w / 2, -h / 2, w, h, h / 2)
    ctx.set_source_rgb(*(hexc("#e8323a") if urgent else UI_DARK))
    ctx.fill_preserve()
    ctx.set_source_rgba(1, 1, 1, 0.25)
    ctx.set_line_width(3)
    ctx.stroke()
    ix = -w / 2 + 42
    ctx.new_sub_path()
    ctx.arc(ix, 2, 17, 0, 2 * PI)
    ctx.move_to(ix, 2)
    ctx.line_to(ix, -9)
    ctx.move_to(ix, -19)
    ctx.line_to(ix, -24)
    ctx.set_source_rgb(1, 1, 1)
    ctx.set_line_width(4.5)
    ctx.stroke()
    bold_text(ctx, txt, 22, 0, 38, (1, 1, 1), shadow=False, stroke=0.0)
    ctx.restore()


def second_card(ctx, x, y, n, k, word="SECOND", col="#ffffff", accent="#4fd16a"):
    """'SECOND N' chapter card that flies in with a shockwave ring; k = time since the pop."""
    if k < 0:
        return
    shockwave(ctx, x, y, k / 0.6, r_max=360)
    sc = pop(k)
    ctx.save()
    ctx.translate(x, y)
    ctx.rotate(-0.05)
    ctx.scale(sc, sc)
    block(ctx, -170, -75, 340, 150, 34, c_(col), 7, outline=INK)
    rrect(ctx, -150, -58, 120, 116, 26)
    shape_fill(ctx, c_(accent), 6, -58, 58, outline=INK)
    ctx.new_sub_path()
    ctx.arc(-90, 4, 30, 0, 2 * PI)
    ctx.set_source_rgb(1, 1, 1)
    ctx.set_line_width(7)
    ctx.stroke()
    bold_text(ctx, word, 60, -36, 30, INK, outline=c_(col), shadow=False, stroke=0.02)
    bold_text(ctx, str(n), 60, 18, 92, c_(accent), stroke=0.14)
    ctx.restore()


def stage_pill(ctx, x, y, txt, s=1.0, col="#2f6bd8"):
    if s <= 0.01:
        return
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s, s)
    w = text_width(ctx, txt, 40) + 60
    block(ctx, -w / 2, -34, w, 68, 34, (1, 1, 1), 5, outline=INK)
    bold_text(ctx, txt, 0, 0, 40, c_(col), outline=(1, 1, 1), shadow=False, stroke=0.02)
    ctx.restore()


def health_bar(ctx, frac, name="BOSS", y=272, a=1.0, shake=0.0):
    if a <= 0:
        return
    ctx.save()
    ctx.translate(math.sin(shake * 80) * 8 * shake, 0)
    ctx.push_group()
    rrect(ctx, 110, y - 40, 500, 80, 16)
    ctx.set_source_rgba(*UI_DARK, 0.92)
    ctx.fill()
    bold_text(ctx, name, 130, y - 18, 26, (1, 1, 1), align="l", shadow=False, stroke=0.0)
    rrect(ctx, 130, y + 4, 460, 24, 12)
    ctx.set_source_rgb(*hexc("#3a1a24"))
    ctx.fill()
    if frac > 0:
        rrect(ctx, 130, y + 4, 460 * clamp(frac), 24, 12)
        ctx.set_source_rgb(*hexc("#ff3b4a"))
        ctx.fill()
    ctx.pop_group_to_source()
    ctx.paint_with_alpha(a)
    ctx.restore()


def damage_text(ctx, x, y, k, txt="-999,999", col="#ff4f5a"):
    if not 0 <= k < 1.2:
        return
    bold_text(ctx, txt, x, y - k * 120, 64, c_(col), scale=pop(k), tilt=-0.08)


def ko_sticker(ctx, x, y, k):
    if k < 0:
        return
    sc = pop(k)
    ctx.save()
    ctx.translate(x, y)
    ctx.rotate(-0.06)
    ctx.scale(sc, sc)
    block(ctx, -110, -50, 220, 100, 26, (1, 1, 1), 6, outline=INK)
    bold_text(ctx, "K.O.!", 0, 0, 64, hexc("#e8323a"), stroke=0.12, shadow=False)
    ctx.restore()


def toast(ctx, x, y, msg, k, col="#ffd84a", w=None):
    """Game notification toast ('X joined the game.') sliding in; k = time since."""
    if k < 0:
        return
    a = clamp(k / 0.15)
    w = w or text_width(ctx, msg, 26) + 50
    ctx.save()
    ctx.translate(x + (1 - ease(k / 0.2)) * 60, y)
    rrect(ctx, -w / 2, -26, w, 52, 12)
    ctx.set_source_rgba(*UI_DARK, 0.85 * a)
    ctx.fill()
    bold_text(ctx, msg, 0, 0, 26, c_(col), shadow=False, stroke=0.0)
    ctx.restore()


def joystick_ui(ctx, T, y=1000):
    for x, r in ((140, 74), (570, 60)):
        ctx.new_sub_path()
        ctx.arc(x, y, r, 0, 2 * PI)
        ctx.set_source_rgba(1, 1, 1, 0.2)
        ctx.fill_preserve()
        ctx.set_source_rgba(1, 1, 1, 0.7)
        ctx.set_line_width(4)
        ctx.stroke()
    ctx.new_sub_path()
    ctx.arc(140 + math.sin(T * 2) * 20, y, 32, 0, 2 * PI)
    ctx.set_source_rgba(1, 1, 1, 0.6)
    ctx.fill()
    bold_text(ctx, "JUMP", 570, y + 20, 22, (1, 1, 1), shadow=False, stroke=0.0)


def login_screen(ctx, x, y, w, h, T, typed="", wrong=0.0, granted=0.0, title="ENTER PASSWORD", lock=True):
    """Screen content: a game login box with a password field. wrong / granted 0..1 tint it red / green."""
    g = cairo.LinearGradient(0, y, 0, y + h)
    g.add_color_stop_rgb(0, *hexc("#3a5bd8"))
    g.add_color_stop_rgb(1, *hexc("#7a3fd8"))
    ctx.rectangle(x, y, w, h)
    ctx.set_source(g)
    ctx.fill()
    for i in range(6):   # floating blocks in the background
        bx = x + ((i * 97 + T * 30) % (w + 80)) - 40
        rrect(ctx, bx, y + h * (0.15 + 0.13 * (i % 4)), 30, 30, 6)
        ctx.set_source_rgba(1, 1, 1, 0.12)
        ctx.fill()
    cx_, cy_ = x + w / 2, y + h / 2
    if lock:
        padlock(ctx, cx_, y + h * 0.24, w / 1400, 1.0)
    bold_text(ctx, title, cx_, y + h * 0.43, w * 0.06, (1, 1, 1), stroke=0.12)
    fw, fh = w * 0.72, h * 0.16
    fill = (1, 1, 1)
    if wrong > 0:
        fill = mix(fill, hexc("#ff8a8a"), wrong)
    if granted > 0:
        fill = mix(fill, hexc("#8af0a0"), granted)
    j = math.sin(T * 70) * 10 * wrong * (1 - clamp(wrong - 0.6))
    block(ctx, cx_ - fw / 2 + j, cy_ + h * 0.08 - fh / 2, fw, fh, 12, fill, 4, outline=INK)
    if typed:
        bold_text(ctx, typed, cx_ + j, cy_ + h * 0.08, fh * 0.5, INK, outline=fill, shadow=False, stroke=0.02)
    if int(T * 3) % 2 == 0 and not wrong and not granted:
        tw = text_width(ctx, typed, fh * 0.5) if typed else 0
        ctx.rectangle(cx_ + tw / 2 + 6, cy_ + h * 0.08 - fh * 0.3, 4, fh * 0.6)
        ctx.set_source_rgb(*INK)
        ctx.fill()
    bw, bh = w * 0.34, h * 0.13
    block(ctx, cx_ - bw / 2, y + h * 0.78 - bh / 2, bw, bh, 12, GREEN, 4, outline=INK)
    bold_text(ctx, "LOG IN", cx_, y + h * 0.78, bh * 0.45, (1, 1, 1), stroke=0.12, shadow=False)


def leaderboard(ctx, x, y, s, rows, T, title="LEADERBOARD", hi=0, k_rows=None):
    """Leaderboard panel (top centre x, y). rows = [(name, value, avatar_fn or None), ...];
    the first row is gold. k_rows: per-row pop times (s since)."""
    if s <= 0.01:
        return
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s, s)
    w = 560
    h = 150 + len(rows) * 96
    block(ctx, -w / 2 - 14, -14, w + 28, h + 28, 34, GOLD, 6, outline=INK)
    block(ctx, -w / 2, 0, w, h, 26, hexc("#1f2a5a"), 4, outline=INK)
    block(ctx, -w / 2, 0, w, 100, 26, hexc("#2f6bd8"), 4, outline=INK)
    ctx.new_sub_path()
    ctx.arc(-w / 2 + 60, 50, 32, 0, 2 * PI)
    shape_fill(ctx, GOLD, 4, 18, 82, outline=INK)
    bold_text(ctx, title, 30, 50, 44, (1, 1, 1), stroke=0.12)
    for i, (name, val, av) in enumerate(rows):
        k = 1.0 if k_rows is None else k_rows[i]
        if k is None or k < 0:
            continue
        sc = pop(k) if k < 1 else 1.0
        ry = 130 + i * 96
        ctx.save()
        ctx.translate(0, ry + 40)
        ctx.scale(sc, sc)
        rc = GOLD if i == 0 else hexc("#2c3a78")
        block(ctx, -w / 2 + 20, -40, w - 40, 80, 18, rc, 4, outline=INK)
        ctx.new_sub_path()
        ctx.arc(-w / 2 + 70, 0, 26, 0, 2 * PI)
        shape_fill(ctx, (1, 1, 1) if i else hexc("#ffe27a"), 3, -26, 26, outline=INK)
        bold_text(ctx, str(i + 1), -w / 2 + 70, 0, 30, INK if i == 0 else hexc("#2c3a78"), outline=(1, 1, 1),
                  shadow=False, stroke=0.02)
        if av:
            av(ctx, -w / 2 + 145, 0, T)
        bold_text(ctx, name, -w / 2 + 190, 0, 34, INK if i == 0 else (1, 1, 1),
                  outline=rc if i == 0 else INK, shadow=False, stroke=0.04 if i == 0 else 0.1, align="l")
        bold_text(ctx, val, w / 2 - 44, 0, 28, INK if i == 0 else hexc("#cfd6ff"),
                  outline=rc if i == 0 else INK, shadow=False, stroke=0.04 if i == 0 else 0.1, align="r")
        ctx.restore()
    ctx.restore()


def face_icon(ctx, x, y, r, skin="#e6ddd6", hair="#4a2f22", crown=False, expr="smirk"):
    """Tiny avatar face for UI rows."""
    rrect(ctx, x - r, y - r * 0.9, 2 * r, 1.8 * r, r * 0.4)
    shape_fill(ctx, c_(skin), 2.5, y - r, y + r)
    ctx.move_to(x - r, y - r * 0.1)
    ctx.curve_to(x - r * 1.1, y - r * 1.5, x + r * 1.1, y - r * 1.5, x + r, y - r * 0.1)
    ctx.close_path()
    shape_fill(ctx, c_(hair), 2.5, y - r, y)
    for side in (-1, 1):
        ellipse(ctx, x + side * 0.38 * r, y + 0.15 * r, 0.1 * r, 0.14 * r)
        ctx.set_source_rgb(*INK)
        ctx.fill()
    ctx.move_to(x - 0.3 * r, y + 0.5 * r)
    ctx.curve_to(x - 0.1 * r, y + 0.65 * r, x + 0.2 * r, y + 0.6 * r, x + 0.4 * r, y + 0.4 * r)
    ctx.set_source_rgb(*INK)
    ctx.set_line_width(2.5)
    ctx.stroke()
    if crown:
        cw = 1.4 * r
        by = y - r * 1.0
        ctx.move_to(x - cw / 2, by)
        for px, py in ((-0.5, -0.8), (-0.25, -0.35), (0, -0.9), (0.25, -0.35), (0.5, -0.8)):
            ctx.line_to(x + px * cw, by + py * r)
        ctx.line_to(x + cw / 2, by)
        ctx.close_path()
        shape_fill(ctx, GOLD, 2.5, by - r, by, outline=INK)


def shop_grid(ctx, T, items, owned_t=None, y0=300):
    """Dark shop panel with a grid of item cards; owned_t[i] = time an OWNED stamp pops (or None)."""
    block(ctx, 30, y0, 660, 560, 26, hexc("#1f2236"), 5, outline=INK)
    bold_text(ctx, "SHOP", 110, y0 + 40, 36, (1, 1, 1), align="l", stroke=0.1)
    for i, (name, c) in enumerate(items):
        cx_ = 70 + (i % 3) * 205
        cy_ = y0 + 90 + (i // 3) * 220
        block(ctx, cx_, cy_, 180, 200, 18, c_(c), 4, outline=INK)
        bold_text(ctx, name, cx_ + 90, cy_ + 150, 22, (1, 1, 1), stroke=0.12, shadow=False)
        k = None if owned_t is None or owned_t[i] is None else T - owned_t[i]
        if k is not None and k >= 0:
            ctx.save()
            ctx.translate(cx_ + 90, cy_ + 70)
            ctx.rotate(-0.15)
            sc = pop(k)
            ctx.scale(sc, sc)
            block(ctx, -80, -26, 160, 52, 12, GREEN, 4, outline=INK)
            bold_text(ctx, "OWNED", 0, 0, 30, (1, 1, 1), stroke=0.12, shadow=False)
            ctx.restore()


def gamepass_card(ctx, x, y, s, T, title="+10 SECONDS", price="99", bought=0.0):
    if s <= 0.01:
        return
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s, s)
    block(ctx, -190, -200, 380, 400, 28, hexc("#1f2236"), 6, outline=GOLD)
    bold_text(ctx, "GAMEPASS", 0, -165, 26, hexc("#cfd6ff"), shadow=False, stroke=0.0)
    ctx.new_sub_path()
    ctx.arc(0, -70, 62, 0, 2 * PI)
    shape_fill(ctx, GOLD, 5, -132, -8, outline=INK)
    ctx.new_sub_path()
    ctx.arc(0, -70, 40, 0, 2 * PI)
    shape_fill(ctx, hexc("#fff4d0"), 4, -110, -30, outline=INK)
    bold_text(ctx, title, 0, 40, 40, (1, 1, 1), stroke=0.12)
    coin(ctx, -30, 95, 0.55)
    bold_text(ctx, price, 20, 95, 34, GOLD, stroke=0.12)
    bc = mix(BLUE, GREEN, clamp(bought))
    block(ctx, -150, 130, 300, 56, 16, bc, 4, outline=INK)
    bold_text(ctx, "BUY" if bought < 0.5 else "PURCHASED!", 0, 158, 30, (1, 1, 1), stroke=0.12, shadow=False)
    ctx.restore()


def subscribe_button(ctx, x, y, s, pressed=0.0):
    if s <= 0.01:
        return
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s * (1 - 0.08 * math.sin(PI * clamp(pressed * 3))), s)
    col = mix(hexc("#e8323a"), hexc("#f1f1f6"), clamp(pressed))
    block(ctx, -210, -50, 420, 100, 50, col, 6, outline=INK)
    bold_text(ctx, "SUBSCRIBED" if pressed > 0.5 else "SUBSCRIBE", 0, 0, 44,
              INK if pressed > 0.5 else (1, 1, 1), outline=col if pressed > 0.5 else INK, shadow=False,
              stroke=0.04 if pressed > 0.5 else 0.12)
    ctx.restore()


def cursor(ctx, x, y, s=1.0, click=0.0):
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s * (1 - 0.15 * click), s * (1 - 0.15 * click))
    ctx.move_to(0, 0)
    for px, py in ((0, 52), (13, 40), (24, 62), (34, 57), (23, 36), (40, 36)):
        ctx.line_to(px, py)
    ctx.close_path()
    shape_fill(ctx, (1, 1, 1), 4, 0, 60, outline=INK)
    ctx.restore()


def comments_sheet(ctx, T, comments, typed="", y0=480, likes_t=None, count="12,846"):
    """Phone comments sheet + keyboard filling the lower screen (comment-call ending).
    comments = [(name, text, colour), ...]; typed = text in the input box."""
    ctx.rectangle(-3000, y0, 7000, 3000)
    ctx.set_source_rgb(*hexc("#16181f"))
    ctx.fill()
    bold_text(ctx, f"Comments  {count}", 40, y0 + 40, 28, (1, 1, 1), align="l", shadow=False, stroke=0.0)
    for i, (name, txt, c) in enumerate(comments):
        yy = y0 + 110 + i * 92
        ctx.new_sub_path()
        ctx.arc(70, yy, 26, 0, 2 * PI)
        ctx.set_source_rgb(*c_(c))
        ctx.fill()
        bold_text(ctx, name, 112, yy - 16, 20, hexc("#9aa0b8"), align="l", shadow=False, stroke=0.0)
        bold_text(ctx, txt, 112, yy + 14, 28, (1, 1, 1), align="l", shadow=False, stroke=0.0)
    iy = y0 + 110 + len(comments) * 92
    rrect(ctx, 40, iy - 30, 560, 60, 30)
    ctx.set_source_rgb(*hexc("#2a2d38"))
    ctx.fill()
    bold_text(ctx, typed or "Add a comment...", 70, iy, 30 if typed else 24,
              (1, 1, 1) if typed else hexc("#7a7f90"), align="l", shadow=False, stroke=0.0)
    ky = iy + 60
    ctx.rectangle(-3000, ky, 7000, 3000)
    ctx.set_source_rgb(*hexc("#2a2d38"))
    ctx.fill()
    rows = ["QWERTYUIOP", "ASDFGHJKL", "ZXCVBNM"]
    for r, row in enumerate(rows):
        for i, ch in enumerate(row):
            kx = 14 + i * 69 + r * 34
            kyy = ky + 20 + r * 82
            rrect(ctx, kx, kyy, 60, 70, 10)
            hot = typed and ch == typed[-1:].upper() and int(T * 8) % 2 == 0
            ctx.set_source_rgb(*(hexc("#5a6080") if hot else hexc("#4a4e5e")))
            ctx.fill()
            bold_text(ctx, ch, kx + 30, kyy + 35, 28, (1, 1, 1), shadow=False, stroke=0.0)
    if likes_t is not None and T >= likes_t:
        for i in range(8):
            ph = clamp((T - likes_t - i * 0.07) / 1.0)
            if 0 < ph < 1:
                hx = 520 + math.sin(i * 1.7) * 60
                hy = iy - 40 - ph * 380
                bold_text(ctx, "♥", hx, hy, 40, RED if i % 2 else BLUE, scale=1 - ph * 0.3)


# ================================================================ more props / UI (added for report_noob.py)
def nametag(ctx, x, y, name, size=30, col=(1, 1, 1)):
    """Game name tag floating above a head (white text, dark outline)."""
    bold_text(ctx, name, x, y, size, c_(col), stroke=0.2, shadow=False)


def speech_bubble(ctx, x, y, txt, size=48, k=1.0, tail=(-1, 1), col=(1, 1, 1), fg=INK, tilt=-0.04):
    """Comic speech bubble centred at (x, y); tail points toward (dx, dy) sign. k = pop time (s since)."""
    if k < 0:
        return
    sc = pop(k) if k < 1 else 1.0
    ctx.save()
    ctx.translate(x, y)
    ctx.rotate(tilt)
    ctx.scale(sc, sc)
    w = text_width(ctx, txt, size) + size * 1.1
    h = size * 1.6
    ctx.move_to(tail[0] * w * 0.15, h / 2 - 4)
    ctx.line_to(tail[0] * w * 0.38, h / 2 + size * 0.7 * tail[1])
    ctx.line_to(tail[0] * w * 0.32, h / 2 - 4)
    ctx.close_path()
    shape_fill(ctx, c_(col), size * 0.09, 0, h, outline=INK)
    block(ctx, -w / 2, -h / 2, w, h, h * 0.45, c_(col), size * 0.09, outline=INK)
    bold_text(ctx, txt, 0, 0, size, c_(fg), outline=c_(col), shadow=False, stroke=0.02)
    ctx.restore()


def spotlight(ctx, x, y, r, a=0.75):
    """Darken everything except a soft circle (one character singled out of a crowd)."""
    g = cairo.RadialGradient(x, y, r * 0.75, x, y, r * 1.25)
    g.add_color_stop_rgba(0, 0, 0, 0, 0)
    g.add_color_stop_rgba(1, 0.02, 0.02, 0.08, a)
    ctx.set_source(g)
    ctx.rectangle(-3000, -5000, 7000, 10000)
    ctx.fill()
    ctx.move_to(x - r * 0.55, -400)
    ctx.line_to(x + r * 0.55, -400)
    ctx.line_to(x + r, y + r * 0.6)
    ctx.line_to(x - r, y + r * 0.6)
    ctx.close_path()
    ctx.set_source_rgba(1, 0.97, 0.8, 0.16)
    ctx.fill()


def calendar(ctx, x, y, s, top, big, col="#e8323a", flip=0.0):
    """Tear-off calendar page (centre x, y): coloured header `top`, big number/text `big`.
    flip > 0 shows the previous page peeling away."""
    if s <= 0.01:
        return
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s, s)
    block(ctx, -170, -190, 340, 380, 26, (1, 1, 1), 7, outline=INK)
    rrect(ctx, -170, -190, 340, 110, 26)
    ctx.rectangle(-170, -120, 340, 40)
    shape_fill(ctx, c_(col), 0.1, -190, -80)
    rrect(ctx, -170, -190, 340, 380, 26)
    ctx.set_source_rgb(*INK)
    ctx.set_line_width(7)
    ctx.stroke()
    for rx in (-90, 90):
        rrect(ctx, rx - 10, -215, 20, 50, 10)
        shape_fill(ctx, hexc("#c9cde0"), 4, -215, -165, outline=INK)
    bold_text(ctx, top, 0, -135, 48, (1, 1, 1), stroke=0.12, shadow=False)
    bold_text(ctx, big, 0, 55, 130 if len(big) <= 3 else 96, INK, outline=(1, 1, 1), shadow=False, stroke=0.02)
    if 0 < flip < 1:
        ctx.save()
        ctx.translate(0, -80)
        ctx.scale(1, 1 - flip)
        ctx.rotate(-0.3 * flip)
        block(ctx, -170, 0, 340, 270, 20, hexc("#f2ece0"), 6, outline=INK)
        ctx.restore()
    ctx.restore()


def rule_book(ctx, x, y, s, T, title="RULES"):
    """Open book with a heading and completely empty numbered lines."""
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s, s)
    block(ctx, -330, -220, 660, 440, 30, hexc("#8a3a2a"), 7, outline=INK)
    for side in (-1, 1):
        ctx.move_to(0, -190)
        ctx.curve_to(side * 100, -215, side * 220, -210, side * 310, -195)
        ctx.line_to(side * 310, 200)
        ctx.curve_to(side * 220, 185, side * 100, 190, 0, 210)
        ctx.close_path()
        shape_fill(ctx, hexc("#fbf3dc"), 5, -210, 210, outline=INK)
    bold_text(ctx, title, -160, -130, 50, hexc("#8a3a2a"), outline=hexc("#fbf3dc"), shadow=False, stroke=0.02)
    for i in range(5):
        yy = -60 + i * 52
        bold_text(ctx, f"{i + 1}.", -270, yy, 30, hexc("#9a8a70"), outline=hexc("#fbf3dc"), shadow=False,
                  stroke=0.02, align="l")
        ctx.move_to(-225, yy + 12)
        ctx.line_to(-40, yy + 12)
        ctx.move_to(40, yy - 50 + 12)
        ctx.line_to(270, yy - 50 + 12)
    ctx.set_source_rgba(*hexc("#c9b99a"), 1)
    ctx.set_line_width(3)
    ctx.stroke()
    ctx.restore()


def friends_panel(ctx, x, y, s, n, T, title="FRIENDS"):
    """Friend list panel with a count and empty slots."""
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s, s)
    block(ctx, -260, -200, 520, 400, 30, hexc("#1f2236"), 6, outline=INK)
    bold_text(ctx, f"{title} ({n})", 0, -150, 44, (1, 1, 1), stroke=0.12)
    for i in range(3):
        yy = -70 + i * 95
        rrect(ctx, -220, yy - 38, 440, 76, 18)
        ctx.set_source_rgba(1, 1, 1, 0.08)
        ctx.fill_preserve()
        ctx.set_source_rgba(1, 1, 1, 0.3)
        ctx.set_dash([12, 10])
        ctx.set_line_width(4)
        ctx.stroke()
        ctx.set_dash([])
        bold_text(ctx, "empty", 0, yy, 30, hexc("#7a7f90"), shadow=False, stroke=0.0)
    ctx.restore()


def server_list(ctx, T, join_t, x0=40, y0=280, rows=6):
    """Server browser: rows with player counts and JOIN buttons; join_t[i] = time row i is joined."""
    block(ctx, x0, y0, 640, 120 + rows * 96, 26, hexc("#1f2236"), 5, outline=INK)
    bold_text(ctx, "SERVERS", x0 + 40, y0 + 50, 40, (1, 1, 1), align="l", stroke=0.1)
    for i in range(rows):
        yy = y0 + 110 + i * 96
        block(ctx, x0 + 20, yy, 600, 80, 16, hexc("#2c3a78"), 4, outline=INK, gloss=False)
        bold_text(ctx, f"Server #{i + 1}", x0 + 50, yy + 40, 30, (1, 1, 1), align="l", shadow=False, stroke=0.0)
        bold_text(ctx, f"{8 + i % 4}/12", x0 + 330, yy + 40, 26, hexc("#9aa0b8"), shadow=False, stroke=0.0)
        k = None if i >= len(join_t) or join_t[i] is None else T - join_t[i]
        joined = k is not None and k >= 0
        bc = GREEN if not joined else hexc("#ffb02e")
        sc = 1 - 0.12 * math.exp(-12 * k) if joined else 1.0
        ctx.save()
        ctx.translate(x0 + 520, yy + 40)
        ctx.scale(sc, sc)
        block(ctx, -75, -28, 150, 56, 14, bc, 4, outline=INK)
        bold_text(ctx, "JOINED" if joined else "JOIN", 0, 0, 24, (1, 1, 1), shadow=False, stroke=0.12)
        ctx.restore()


def chat_box(ctx, x, y, w, h, lines, T, size=28, title="Chat"):
    """Game chat window; lines = [(name, text, colour), ...] (the newest at the bottom)."""
    rrect(ctx, x, y, w, h, 18)
    ctx.set_source_rgba(*UI_DARK, 0.88)
    ctx.fill()
    bold_text(ctx, title, x + 24, y + 30, 24, hexc("#9aa0b8"), align="l", shadow=False, stroke=0.0)
    ctx.save()
    ctx.rectangle(x, y + 50, w, h - 56)
    ctx.clip()
    n = int((h - 60) / (size * 1.45))
    for i, (name, txt, c) in enumerate(lines[-n:]):
        yy = y + 50 + (i + 0.6) * size * 1.45
        bold_text(ctx, name + ":", x + 24, yy, size, c_(c), align="l", shadow=False, stroke=0.0)
        bold_text(ctx, txt, x + 34 + text_width(ctx, name + ":", size), yy, size, (1, 1, 1), align="l",
                  shadow=False, stroke=0.0)
    ctx.restore()


def void_bg(ctx, top="#84d4fb", bottom="#1b1f4a", y0=600, y1=1400):
    """Sky that falls into a dark void (gaps under bridges)."""
    g = cairo.LinearGradient(0, y0 - 800, 0, y1)
    g.add_color_stop_rgb(0, *c_(top))
    g.add_color_stop_rgb(0.55, *light(c_(top), 0.3))
    g.add_color_stop_rgb(1, *c_(bottom))
    ctx.rectangle(-3000, -5000, 7000, 10000)
    ctx.set_source(g)
    ctx.fill()


def cliff(ctx, x, y, w, col="#51c844", side=1):
    """Grass-topped cliff block; (x, y) = top-left corner."""
    block(ctx, x, y + 40, w, 1200, 10, hexc("#9a6a3c"), 5, gloss=False)
    block(ctx, x, y, w, 60, 12, c_(col), 5)


def lava_bridge(ctx, x0, x1, y, T, built=1.0, lava=1.0, n=7):
    """Bridge of blocks between two cliffs. built 0..1 = how many blocks exist; lava 0..1 turns them to lava."""
    bw = (x1 - x0) / n
    for i in range(n):
        k = clamp(built * n - i)
        if k <= 0:
            continue
        yy = y - (1 - ease(k)) * 120
        c = mix(hexc("#b0b6c4"), hexc("#ff7a1a"), lava)
        block(ctx, x0 + i * bw + 2, yy, bw - 4, 50, 6, c, 4, outline=INK if lava < 0.5 else hexc("#8a2a0a"))
        if lava > 0.5:
            for j in range(2):
                bx = x0 + i * bw + bw * (0.3 + 0.4 * j)
                ph = (T * 1.7 + i * 0.37 + j * 0.5) % 1
                ctx.new_sub_path()
                ctx.arc(bx, yy - ph * 40, 6 * (1 - ph) + 2, 0, 2 * PI)
                ctx.set_source_rgba(1, 0.85, 0.3, 1 - ph)
                ctx.fill()
    if lava > 0.3:
        glow(ctx, (x0 + x1) / 2, y + 20, (x1 - x0) * 0.7, (1, 0.5, 0.1), 0.35 * lava)


def lemonade_stand(ctx, x, y, s, T, sign="LEMONADE"):
    """Wooden lemonade stand; (x, y) = bottom centre."""
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s, s)
    for px in (-150, 130):
        block(ctx, px, -330, 20, 330, 4, hexc("#8a5a3a"), 4, gloss=False)
    ctx.move_to(-190, -400)   # striped awning with a scalloped edge
    ctx.line_to(190, -400)
    ctx.line_to(200, -330)
    for i in range(6, -1, -1):
        ctx.curve_to(-190 + (i + 0.5) * 390 / 7, -300, -190 + (i + 0.5) * 390 / 7, -300, -190 + i * 390 / 7, -330)
    ctx.close_path()
    shape_fill(ctx, hexc("#ffe45c"), 5, -400, -300, outline=INK)
    for i in range(0, 7, 2):
        ctx.rectangle(-190 + i * 380 / 7 + 4, -398, 380 / 7, 66)
    ctx.set_source_rgba(1, 1, 1, 0.65)
    ctx.fill()
    block(ctx, -200, -170, 400, 170, 10, hexc("#d9a46a"), 5)
    for i in range(4):
        ctx.move_to(-195, -130 + i * 40)
        ctx.line_to(195, -130 + i * 40)
    ctx.set_source_rgba(*hexc("#a8743f"), 1)
    ctx.set_line_width(3)
    ctx.stroke()
    rrect(ctx, -150, -150, 300, 70, 12)
    shape_fill(ctx, (1, 1, 1), 4, -150, -80, outline=INK)
    bold_text(ctx, sign, 0, -115, 40, hexc("#e8b020"), outline=(1, 1, 1), shadow=False, stroke=0.02)
    block(ctx, -40, -260, 80, 90, 14, hexc("#ffe45c"), 4, outline=INK)    # jug
    for cx_ in (-140, 110):
        block(ctx, cx_, -215, 34, 45, 6, (1, 1, 1), 3, outline=INK, gloss=False)
    ctx.restore()


def big_clock(ctx, x, y, r, hours, T=0.0, col="#ffffff", rim="#e8323a"):
    """Analog wall clock showing `hours` (float, e.g. 2.5); spins fast in a time-lapse."""
    ctx.new_sub_path()
    ctx.arc(x, y, r, 0, 2 * PI)
    shape_fill(ctx, c_(rim), r * 0.06, y - r, y + r, outline=INK)
    ctx.new_sub_path()
    ctx.arc(x, y, r * 0.82, 0, 2 * PI)
    shape_fill(ctx, c_(col), r * 0.03, y - r, y + r, outline=INK)
    for i in range(12):
        a = i * PI / 6
        ctx.move_to(x + math.cos(a) * r * 0.66, y + math.sin(a) * r * 0.66)
        ctx.line_to(x + math.cos(a) * r * 0.74, y + math.sin(a) * r * 0.74)
    ctx.set_source_rgb(*INK)
    ctx.set_line_width(r * 0.04)
    ctx.stroke()
    for frac, ln, w in ((hours / 12, 0.42, 0.07), ((hours % 1), 0.62, 0.045)):
        a = -PI / 2 + frac * 2 * PI
        ctx.move_to(x, y)
        ctx.line_to(x + math.cos(a) * r * ln, y + math.sin(a) * r * ln)
        ctx.set_line_width(r * w)
        ctx.set_line_cap(cairo.LINE_CAP_ROUND)
        ctx.stroke()
    ctx.new_sub_path()
    ctx.arc(x, y, r * 0.06, 0, 2 * PI)
    ctx.fill()


def settings_menu(ctx, x, y, s, T, missing_k=1.0, rows=("Volume", "Graphics", "Camera", "Chat")):
    """Game settings panel; the last slot is an empty dashed box (no report button)."""
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s, s)
    block(ctx, -280, -330, 560, 660, 30, hexc("#1f2236"), 6, outline=INK)
    bold_text(ctx, "SETTINGS", 0, -270, 46, (1, 1, 1), stroke=0.12)
    for i, name in enumerate(rows):
        yy = -180 + i * 95
        block(ctx, -240, yy - 38, 480, 76, 16, hexc("#2c3a78"), 4, outline=INK, gloss=False)
        bold_text(ctx, name, -210, yy, 30, (1, 1, 1), align="l", shadow=False, stroke=0.0)
        rrect(ctx, 80, yy - 10, 130, 20, 10)
        ctx.set_source_rgb(*hexc("#4a4e6e"))
        ctx.fill()
        ctx.new_sub_path()
        ctx.arc(80 + 30 + i * 22, yy, 16, 0, 2 * PI)
        ctx.set_source_rgb(1, 1, 1)
        ctx.fill()
    yy = -180 + len(rows) * 95
    rrect(ctx, -240, yy - 38, 480, 76, 16)
    ctx.set_source_rgba(1, 1, 1, 0.06 * missing_k)
    ctx.fill_preserve()
    ctx.set_source_rgba(1, 1, 1, 0.55)
    ctx.set_dash([14, 10])
    ctx.set_line_width(5)
    ctx.stroke()
    ctx.set_dash([])
    bold_text(ctx, "?", 0, yy, 50, YELLOW, stroke=0.12, scale=missing_k)
    ctx.restore()


def report_button(ctx, x, y, s, T, pressed=0.0, glow_a=0.0):
    """Big red REPORT button with a flag icon (pressed 0..1 squashes it)."""
    if s <= 0.01:
        return
    if glow_a > 0:
        glow(ctx, x, y, 420 * s, (1, 0.3, 0.25), glow_a)
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s, s)
    block(ctx, -250, -40, 500, 150, 60, hexc("#8a1a24"), 7, outline=INK, gloss=False)   # base
    dy = 34 * clamp(pressed)
    block(ctx, -235, -110 + dy, 470, 170, 70, hexc("#ff3b4a"), 7, outline=INK)
    fx = -150
    fy = -25 + dy
    ctx.move_to(fx, fy + 40)
    ctx.line_to(fx, fy - 45)
    ctx.set_source_rgb(1, 1, 1)
    ctx.set_line_width(9)
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    ctx.stroke()
    ctx.move_to(fx, fy - 45)
    ctx.line_to(fx + 55, fy - 30)
    ctx.line_to(fx, fy - 12)
    ctx.close_path()
    ctx.fill()
    bold_text(ctx, "REPORT", 40, fy, 76, (1, 1, 1), stroke=0.14)
    ctx.restore()


def like_button(ctx, x, y, s, pressed=0.0, count=None):
    """Thumbs-up like button; pressed > 0.5 turns it blue."""
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s * (1 - 0.1 * math.sin(PI * clamp(pressed * 3))), s)
    on = pressed > 0.5
    block(ctx, -110, -90, 220, 180, 50, BLUE if on else hexc("#f1f1f6"), 6, outline=INK)
    c = (1, 1, 1) if on else INK
    rrect(ctx, -60, -10, 34, 70, 8)
    ctx.set_source_rgb(*c)
    ctx.fill()
    ctx.move_to(-20, 60)
    ctx.line_to(45, 60)
    ctx.curve_to(65, 60, 70, 0, 60, -5)
    ctx.line_to(15, -5)
    ctx.line_to(25, -50)
    ctx.curve_to(25, -70, 0, -70, -5, -50)
    ctx.line_to(-20, -10)
    ctx.close_path()
    ctx.fill()
    ctx.restore()
    if count is not None:
        bold_text(ctx, count, x, y + 130 * s, 40 * s, (1, 1, 1))


def coffee_cup(ctx, x, y, s=1.0, steam_T=None):
    block(ctx, x - 26 * s, y - 60 * s, 52 * s, 60 * s, 8 * s, (1, 1, 1), 3, outline=INK)
    ctx.new_sub_path()
    ctx.arc(x + 30 * s, y - 32 * s, 13 * s, -PI / 2, PI / 2)
    ctx.set_source_rgb(*INK)
    ctx.set_line_width(5 * s)
    ctx.stroke()
    rrect(ctx, x - 26 * s, y - 42 * s, 52 * s, 14 * s, 3)
    ctx.set_source_rgb(*hexc("#8a5a3a"))
    ctx.fill()
    if steam_T is not None:
        for k in range(2):
            ph = (steam_T * 0.8 + k * 0.5) % 1
            ctx.move_to(x - 8 * s + k * 16 * s, y - 70 * s - ph * 40 * s)
            ctx.curve_to(x + 4 * s, y - 80 * s - ph * 40 * s, x - 12 * s, y - 95 * s - ph * 40 * s,
                         x + k * 8 * s, y - 105 * s - ph * 40 * s)
            ctx.set_source_rgba(1, 1, 1, 0.6 * (1 - ph))
            ctx.set_line_width(4 * s)
            ctx.stroke()


def code_screen(ctx, x, y, w, h, T, typed=1.0, button_k=0.0):
    """Screen content: dark editor with lines of code typing in; a red button preview forms."""
    ctx.set_source_rgb(*hexc("#141a2e"))
    ctx.rectangle(x, y, w, h)
    ctx.fill()
    cols = [GREEN, BLUE, PINK, YELLOW, hexc("#9aa0b8")]
    n = int(typed * 14)
    rnd = random.Random(3)
    for i in range(n):
        indent = (i % 4) * 0.06 * w
        ww = rnd.uniform(0.2, 0.55) * w
        rrect(ctx, x + 0.06 * w + indent, y + 0.08 * h + i * 0.06 * h, ww, 0.03 * h, 4)
        ctx.set_source_rgb(*cols[i % len(cols)])
        ctx.fill()
    if button_k > 0:
        report_button(ctx, x + w * 0.72, y + h * 0.6, 0.28 * w / 560 * 2 * button_k, T)


def office(ctx, T, night=0.0, y_desk=980, sun=0.0):
    """Developer office: wall, big window (night or sunrise), desk; night 0..1, sun 0..1 (sunrise)."""
    wall = mix(hexc("#9fd0f0"), hexc("#2a2f6a"), night)
    ctx.rectangle(-3000, -5000, 7000, 10000)
    ctx.set_source_rgb(*wall)
    ctx.fill()
    wx, wy, ww, wh = 70, 170, 580, 420
    rrect(ctx, wx - 14, wy - 14, ww + 28, wh + 28, 10)
    shape_fill(ctx, hexc("#e9e4f5"), 5, wy, wy + wh, outline=INK)
    ctx.save()
    ctx.rectangle(wx, wy, ww, wh)
    ctx.clip()
    g = cairo.LinearGradient(0, wy, 0, wy + wh)
    top = mix(mix(hexc("#6ec6ff"), hexc("#0b1040"), night), hexc("#ff9a5a"), sun * 0.6)
    bot = mix(mix(hexc("#c4ecff"), hexc("#2a2f7a"), night), hexc("#ffd27a"), sun)
    g.add_color_stop_rgb(0, *top)
    g.add_color_stop_rgb(1, *bot)
    ctx.set_source(g)
    ctx.paint()
    if sun > 0:
        glow(ctx, wx + ww * 0.5, wy + wh * (1.05 - 0.4 * sun), 260, (1, 0.85, 0.4), 0.9 * sun)
        ctx.new_sub_path()
        ctx.arc(wx + ww * 0.5, wy + wh * (1.05 - 0.4 * sun), 70, 0, 2 * PI)
        ctx.set_source_rgb(*hexc("#ffe27a"))
        ctx.fill()
    if night > 0.5:
        _wall_stars(ctx, wx, wy, wx + ww, wy + wh * 0.6, seed=6, a=0.9 * night)
    for i in range(7):   # city skyline
        bx = wx + i * ww / 7
        bh = wh * (0.25 + 0.15 * ((i * 37) % 3))
        ctx.rectangle(bx, wy + wh - bh, ww / 7 - 6, bh)
    ctx.set_source_rgb(*mix(hexc("#7a8ab8"), hexc("#1a1d52"), night))
    ctx.fill()
    ctx.restore()
    ctx.move_to(wx + ww / 2, wy)
    ctx.line_to(wx + ww / 2, wy + wh)
    ctx.set_source_rgb(*hexc("#e9e4f5"))
    ctx.set_line_width(8)
    ctx.stroke()
    block(ctx, -100, y_desk, 920, 50, 8, hexc("#b9b4d8"), 5)
    block(ctx, -100, y_desk + 50, 920, 700, 0, hexc("#7a6aa8"), 5, gloss=False)
    if night > 0:
        tint(ctx, (0.04, 0.05, 0.2), 0.25 * night)


def report_card(ctx, x, y, s, face="?", tilt=0.0, name=None):
    """A report ticket: red header REPORT, a face slot ('?' or a face_icon-style fn), a name line."""
    if s <= 0.01:
        return
    ctx.save()
    ctx.translate(x, y)
    ctx.rotate(tilt)
    ctx.scale(s, s)
    block(ctx, -110, -140, 220, 280, 18, (1, 1, 1), 5, outline=INK)
    rrect(ctx, -110, -140, 220, 60, 18)
    ctx.rectangle(-110, -100, 220, 20)
    ctx.set_source_rgb(*hexc("#ff3b4a"))
    ctx.fill()
    bold_text(ctx, "REPORT", 0, -110, 32, (1, 1, 1), stroke=0.12, shadow=False)
    if face == "?":
        rrect(ctx, -55, -60, 110, 110, 20)
        shape_fill(ctx, hexc("#c9cde0"), 4, -60, 50, outline=INK)
        bold_text(ctx, "?", 0, -5, 80, (1, 1, 1), stroke=0.14, shadow=False)
    elif face:
        face(ctx, 0, -5, 48)
    for i in range(2):
        rrect(ctx, -80, 72 + i * 28, 160 - i * 50, 12, 6)
        ctx.set_source_rgb(*hexc("#c9cde0"))
        ctx.fill()
    if name:
        bold_text(ctx, name, 0, 78, 30, INK, outline=(1, 1, 1), shadow=False, stroke=0.02)
    ctx.restore()


def paper_pile(ctx, x, y, w, h, T, seed=5, face=None, n=None):
    """A mountain of report cards (bottom centre x, y)."""
    rnd = random.Random(seed)
    n = n or int(w * h / 9000)
    pts = []
    for _ in range(n):
        u = rnd.uniform(-1, 1)
        pts.append((x + u * w / 2, y - rnd.uniform(0.1, 1) * h * (1 - u * u), rnd.uniform(-0.5, 0.5)))
    for px, py, tl in sorted(pts, key=lambda p: p[1]):
        report_card(ctx, px, py, 0.42, face=face or "?", tilt=tl)


def stamp(ctx, x, y, txt, k, col="#e8323a", size=110, tilt=-0.18):
    """Rubber-stamp text slamming down (k = time since the slam)."""
    if k < 0:
        return
    sc = 1 + 1.4 * math.exp(-18 * k)
    ctx.save()
    ctx.translate(x, y)
    ctx.rotate(tilt)
    ctx.scale(sc, sc)
    ctx.push_group()
    w = text_width(ctx, txt, size) + size * 0.6
    rrect(ctx, -w / 2, -size * 0.75, w, size * 1.5, size * 0.18)
    ctx.set_source_rgb(*c_(col))
    ctx.set_line_width(size * 0.12)
    ctx.stroke()
    bold_text(ctx, txt, 0, 0, size, c_(col), outline=c_(col), shadow=False, stroke=0.0)
    ctx.pop_group_to_source()
    ctx.paint_with_alpha(min(1.0, k * 12) * 0.95)
    ctx.restore()


def ban_hammer(ctx, x, y, s, ang=0.0):
    ctx.save()
    ctx.translate(x, y)
    ctx.rotate(ang)
    ctx.scale(s, s)
    block(ctx, -16, -40, 32, 300, 10, hexc("#8a5a3a"), 5, outline=INK)
    block(ctx, -110, -130, 220, 110, 20, hexc("#ff3b4a"), 6, outline=INK)
    bold_text(ctx, "BAN", 0, -75, 54, (1, 1, 1), stroke=0.14, shadow=False)
    ctx.restore()


def profile_card(ctx, x, y, s, name, face=None, status=None):
    """Player profile card (avatar slot + name)."""
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s, s)
    block(ctx, -230, -250, 460, 500, 34, hexc("#1f2236"), 6, outline=INK)
    rrect(ctx, -150, -200, 300, 300, 30)
    shape_fill(ctx, hexc("#84d4fb"), 5, -200, 100, outline=INK)
    if face:
        face(ctx, 0, -50, 110)
    bold_text(ctx, name, 0, 160, 56, (1, 1, 1), stroke=0.12)
    if status:
        bold_text(ctx, status, 0, 215, 28, hexc("#9aa0b8"), shadow=False, stroke=0.0)
    ctx.restore()


def staff_badge(ctx, x, y, s, txt="STAFF"):
    """ID badge on a lanyard (hang it on a character's chest)."""
    ctx.move_to(x - 40 * s, y - 120 * s)
    ctx.line_to(x, y - 30 * s)
    ctx.line_to(x + 40 * s, y - 120 * s)
    ctx.set_source_rgb(*BLUE)
    ctx.set_line_width(8 * s)
    ctx.stroke()
    block(ctx, x - 50 * s, y - 35 * s, 100 * s, 70 * s, 10 * s, (1, 1, 1), 4 * s, outline=INK)
    bold_text(ctx, txt, x, y, 24 * s, BLUE, outline=(1, 1, 1), shadow=False, stroke=0.02)


def arrow(ctx, x0, y0, x1, y1, col="#ff3b4a", w=26, k=1.0):
    """Thick curved comic arrow from (x0, y0) to (x1, y1); k 0..1 draws it on."""
    if k <= 0:
        return
    k = clamp(k)
    mx, my = (x0 + x1) / 2 + (y1 - y0) * 0.25, (y0 + y1) / 2 - (x1 - x0) * 0.25
    ex, ey = lerp(x0, x1, k), lerp(y0, y1, k)
    ang = math.atan2(y1 - my, x1 - mx)
    for lw, c in ((w + 12, INK), (w, c_(col))):
        ctx.move_to(x0, y0)
        ctx.curve_to(mx, my, mx, my, ex - math.cos(ang) * w * 0.8, ey - math.sin(ang) * w * 0.8)
        ctx.set_source_rgb(*c)
        ctx.set_line_width(lw)
        ctx.set_line_cap(cairo.LINE_CAP_ROUND)
        ctx.stroke()
    hs = w * 1.9
    ctx.move_to(ex + math.cos(ang) * hs * 0.4, ey + math.sin(ang) * hs * 0.4)
    ctx.line_to(ex + math.cos(ang + 2.4) * hs, ey + math.sin(ang + 2.4) * hs)
    ctx.line_to(ex + math.cos(ang - 2.4) * hs, ey + math.sin(ang - 2.4) * hs)
    ctx.close_path()
    shape_fill(ctx, c_(col), 6, ey - hs, ey + hs, outline=INK)


def lightbulb(ctx, x, y, s, k=1.0, T=0.0):
    """Idea lightbulb (centre x, y), pops with k (s since), glowing rays."""
    if k < 0:
        return
    sc = pop(k) * s
    if sc <= 0.01:
        return
    glow(ctx, x, y, 200 * sc, (1, 0.95, 0.5), 0.8)
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(sc, sc)
    for i in range(8):
        a = i * PI / 4 + T * 0.5
        ctx.move_to(math.cos(a) * 95, math.sin(a) * 95)
        ctx.line_to(math.cos(a) * 130, math.sin(a) * 130)
    ctx.set_source_rgb(*YELLOW)
    ctx.set_line_width(12)
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    ctx.stroke()
    ctx.new_sub_path()
    ctx.arc(0, -10, 70, 0, 2 * PI)
    shape_fill(ctx, hexc("#fff3a8"), 6, -80, 60, outline=INK)
    block(ctx, -32, 50, 64, 50, 10, hexc("#b8bcc8"), 5, outline=INK)
    ctx.move_to(-20, 10)
    ctx.line_to(-8, -20)
    ctx.line_to(8, 10)
    ctx.line_to(20, -20)
    ctx.set_source_rgb(*hexc("#ffb02e"))
    ctx.set_line_width(6)
    ctx.stroke()
    ctx.restore()


# ================================================================ more props (added for no_break.py)
def stairs(ctx, T, x0=-60, y0=1180, n=9, dx=80, dy=-70, col="#a8743f", wall="#5a4a8a", light_col="#ffd27a"):
    """Staircase seen from the side, climbing to the upper right; a warm lit room at the bottom left."""
    ctx.rectangle(-3000, -5000, 7000, 10000)
    ctx.set_source_rgb(*c_(wall))
    ctx.fill()
    glow(ctx, x0 + 60, y0 - 120, 380, c_(light_col), 0.55)
    for i in range(n):
        x = x0 + i * dx
        y = y0 + i * dy
        block(ctx, x, y, dx + 4, (n - i) * 0 + 1400, 4, c_(col), 4, gloss=False)
        block(ctx, x, y, dx + 4, 18, 4, light(c_(col), 0.18), 3, gloss=False)
    # banister
    ctx.move_to(x0 + 20, y0 - 150)
    ctx.line_to(x0 + n * dx, y0 + n * dy - 150)
    ctx.set_source_rgb(*INK)
    ctx.set_line_width(20)
    ctx.stroke_preserve()
    ctx.set_source_rgb(*hexc("#8a5a3a"))
    ctx.set_line_width(12)
    ctx.stroke()
    for i in range(0, n, 2):
        ctx.move_to(x0 + 40 + i * dx, y0 + i * dy)
        ctx.line_to(x0 + 40 + i * dx, y0 + i * dy - 150)
    ctx.set_source_rgb(*hexc("#8a5a3a"))
    ctx.set_line_width(8)
    ctx.stroke()


def tablet(ctx, x, y, s, T, fn=None, tilt=0.0, smear=0.0, seed=2):
    """Landscape tablet (centre x, y); smear 0..1 covers it in peanut-butter blobs."""
    if s <= 0.01:
        return
    ctx.save()
    ctx.translate(x, y)
    ctx.rotate(tilt)
    w, h = 420 * s, 300 * s
    block(ctx, -w / 2, -h / 2, w, h, 30 * s, hexc("#2b2f45"), 5)
    screen_rect(ctx, -w / 2 + 22 * s, -h / 2 + 20 * s, w - 44 * s, h - 40 * s, fn, T, 10 * s)
    if smear > 0:
        rnd = random.Random(seed)
        for i in range(int(14 * smear)):
            bx = rnd.uniform(-w / 2, w / 2)
            by = rnd.uniform(-h / 2, h / 2)
            r = rnd.uniform(25, 60) * s
            peanut_smear(ctx, bx, by, r, seed + i)
    ctx.restore()


def peanut_smear(ctx, x, y, r, seed=0):
    rnd = random.Random(seed)
    n = 9
    for i in range(n + 1):
        a = i * 2 * PI / n
        rr = r * rnd.uniform(0.7, 1.15)
        (ctx.move_to if i == 0 else ctx.line_to)(x + math.cos(a) * rr, y + math.sin(a) * rr * 0.8)
    ctx.close_path()
    shape_fill(ctx, hexc("#c98a3e"), max(2, r * 0.06), y - r, y + r, outline=hexc("#8a5a2a"))
    ctx.new_sub_path()
    ctx.arc(x - r * 0.25, y - r * 0.25, r * 0.18, 0, 2 * PI)
    ctx.set_source_rgba(1, 1, 1, 0.45)
    ctx.fill()


def pb_jar(ctx, x, y, s):
    """Peanut butter jar (bottom centre x, y)."""
    block(ctx, x - 80 * s, y - 190 * s, 160 * s, 190 * s, 30 * s, hexc("#c98a3e"), 5)
    block(ctx, x - 70 * s, y - 230 * s, 140 * s, 50 * s, 12 * s, hexc("#e8323a"), 5)
    rrect(ctx, x - 70 * s, y - 140 * s, 140 * s, 80 * s, 10 * s)
    shape_fill(ctx, hexc("#fff4d0"), 4, y - 140 * s, y - 60 * s, outline=INK)
    bold_text(ctx, "PEANUT", x, y - 115 * s, 26 * s, hexc("#8a5a2a"), outline=hexc("#fff4d0"), shadow=False, stroke=0.02)
    bold_text(ctx, "BUTTER", x, y - 85 * s, 26 * s, hexc("#8a5a2a"), outline=hexc("#fff4d0"), shadow=False, stroke=0.02)


def cobweb(ctx, x, y, r, k=1.0, corner=(1, 1)):
    """Corner cobweb growing with k (0..1); corner = direction it spreads (sx, sy)."""
    if k <= 0:
        return
    r *= k
    sx, sy = corner
    ctx.set_source_rgba(1, 1, 1, 0.75)
    ctx.set_line_width(2.5)
    for i in range(6):
        a = i * (PI / 2) / 5
        ctx.move_to(x, y)
        ctx.line_to(x + sx * math.cos(a) * r, y + sy * math.sin(a) * r)
    ctx.stroke()
    for j in range(1, 5):
        rr = r * j / 5
        for i in range(6):
            a = i * (PI / 2) / 5
            px, py = x + sx * math.cos(a) * rr, y + sy * math.sin(a) * rr
            (ctx.move_to if i == 0 else ctx.line_to)(px, py)
        ctx.stroke()


def zzz(ctx, x, y, T, size=50):
    for k in range(3):
        ph = (T * 0.8 + k / 3) % 1
        bold_text(ctx, "Z", x + ph * 80 + k * 10, y - ph * 160, size * (0.6 + ph * 0.6), (1, 1, 1),
                  stroke=0.18, shadow=False)


def router(ctx, x, y, s, T, dead=0.0):
    """Wi-Fi router (bottom centre x, y) with a face; dead 0..1 makes it X-eyed and smoking."""
    for side in (-1, 1):
        ctx.save()
        ctx.translate(x + side * 110 * s, y - 120 * s)
        ctx.rotate(side * (0.15 + 0.5 * dead))
        block(ctx, -10 * s, -150 * s, 20 * s, 150 * s, 8 * s, hexc("#3b3f5a"), 4)
        ctx.restore()
    block(ctx, x - 170 * s, y - 140 * s, 340 * s, 140 * s, 26 * s, hexc("#f1f1f6"), 5)
    for i in range(4):
        ctx.new_sub_path()
        ctx.arc(x - 90 * s + i * 60 * s, y - 35 * s, 9 * s, 0, 2 * PI)
        on = dead < 0.5 and int(T * 6 + i) % 3
        ctx.set_source_rgb(*(GREEN if on else hexc("#e8323a")))
        ctx.fill()
    ey = y - 95 * s
    for side in (-1, 1):
        ex = x + side * 45 * s
        if dead > 0.5:
            for a, b in ((-1, 1), (1, -1)):
                ctx.move_to(ex - 14 * s, ey + a * 14 * s)
                ctx.line_to(ex + 14 * s, ey + b * 14 * s)
            ctx.set_source_rgb(*INK)
            ctx.set_line_width(6 * s)
            ctx.stroke()
        else:
            ellipse(ctx, ex, ey, 9 * s, 13 * s)
            ctx.set_source_rgb(*INK)
            ctx.fill()
    if dead > 0.5:
        for k in range(3):   # smoke
            ph = (T * 0.9 + k / 3) % 1
            ctx.new_sub_path()
            ctx.arc(x + (k - 1) * 60 * s, y - 180 * s - ph * 220 * s, (25 + ph * 30) * s, 0, 2 * PI)
            ctx.set_source_rgba(0.45, 0.45, 0.5, 0.7 * (1 - ph))
            ctx.fill()


def wifi_icon(ctx, x, y, r, col=(1, 1, 1), bars=3):
    for i in range(3):
        if i >= bars:
            continue
        rr = r * (0.35 + 0.32 * i)
        ctx.new_sub_path()
        ctx.arc(x, y, rr, -PI * 0.78, -PI * 0.22)
        ctx.set_source_rgb(*c_(col))
        ctx.set_line_width(r * 0.16)
        ctx.set_line_cap(cairo.LINE_CAP_ROUND)
        ctx.stroke()
    ctx.new_sub_path()
    ctx.arc(x, y, r * 0.1, 0, 2 * PI)
    ctx.fill()


def wifi_list(ctx, x, y, s, T, rows, connected_t=None):
    """Wi-Fi network list (top centre x, y); rows = names, the first one gets CONNECTED at connected_t."""
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s, s)
    h = 120 + len(rows) * 100
    block(ctx, -280, 0, 560, h, 30, hexc("#1f2236"), 6, outline=INK)
    bold_text(ctx, "Wi-Fi", -240, 55, 44, (1, 1, 1), align="l", stroke=0.1)
    for i, name in enumerate(rows):
        yy = 120 + i * 100
        on = connected_t is not None and i == 0 and T >= connected_t
        block(ctx, -250, yy, 500, 84, 18, GREEN if on else hexc("#2c3a78"), 4, outline=INK, gloss=False)
        wifi_icon(ctx, -205, yy + 58, 34)
        bold_text(ctx, name, -160, yy + 42, 30, (1, 1, 1), align="l", shadow=False, stroke=0.0)
        if on:
            bold_text(ctx, "CONNECTED", 150, yy + 42, 24, (1, 1, 1), shadow=False, stroke=0.0,
                      scale=pop(T - connected_t))
        else:
            rrect(ctx, 195, yy + 30, 26, 24, 4)   # padlock
            ctx.set_source_rgb(1, 1, 1)
            ctx.fill()
            ctx.new_sub_path()
            ctx.arc(208, yy + 30, 9, PI, 0)
            ctx.set_source_rgb(1, 1, 1)
            ctx.set_line_width(4)
            ctx.stroke()
    ctx.restore()


def pizza_box(ctx, x, y, w, h=34, tilt=0.0):
    """One closed pizza box; (x, y) = bottom centre."""
    ctx.save()
    ctx.translate(x, y)
    ctx.rotate(tilt)
    block(ctx, -w / 2, -h, w, h, 5, hexc("#e8c48a"), 4, gloss=False)
    ctx.move_to(-w / 2 + 6, -h + 9)
    ctx.line_to(w / 2 - 6, -h + 9)
    ctx.set_source_rgba(*hexc("#b8925a"), 1)
    ctx.set_line_width(3)
    ctx.stroke()
    ctx.new_sub_path()
    ctx.arc(0, -h / 2 + 2, h * 0.32, 0, 2 * PI)
    ctx.set_source_rgb(*hexc("#e8323a"))
    ctx.fill()
    ctx.restore()


def pizza_tower(ctx, x, y_base, n, w=260, T=0.0, h=34, seed=1):
    """A wobbly tower of n pizza boxes standing on y_base. Returns the top y."""
    rnd = random.Random(seed)
    y = y_base
    for i in range(int(n)):
        off = rnd.uniform(-14, 14) + math.sin(T * 2 + i * 0.3) * i * 0.4
        pizza_box(ctx, x + off, y, w * rnd.uniform(0.92, 1.0), h, tilt=rnd.uniform(-0.03, 0.03))
        y -= h
    return y


def height_ruler(ctx, x, y_base, h, step=100, label_fn=None):
    """Vertical measuring ruler standing on y_base, h px tall."""
    block(ctx, x - 30, y_base - h, 60, h, 6, hexc("#ffe45c"), 4)
    for i in range(int(h / step * 4) + 1):
        yy = y_base - i * step / 4
        ln = 30 if i % 4 == 0 else 14
        ctx.move_to(x - 30, yy)
        ctx.line_to(x - 30 + ln, yy)
    ctx.set_source_rgb(*INK)
    ctx.set_line_width(3)
    ctx.stroke()


def grad_cap(ctx, x, y, s, tilt=0.0, col="#1f2236"):
    """Graduation mortarboard; (x, y) = where it sits on the head."""
    ctx.save()
    ctx.translate(x, y)
    ctx.rotate(tilt)
    ctx.scale(s, s)
    block(ctx, -45, -30, 90, 40, 8, c_(col), 4)
    ctx.move_to(-95, -40)
    ctx.line_to(0, -75)
    ctx.line_to(95, -40)
    ctx.line_to(0, -5)
    ctx.close_path()
    shape_fill(ctx, light(c_(col), 0.1), 4, -75, -5, outline=INK)
    ctx.move_to(0, -40)
    ctx.line_to(70, -30)
    ctx.line_to(72, 10)
    ctx.set_source_rgb(*YELLOW)
    ctx.set_line_width(5)
    ctx.stroke()
    ctx.restore()


def diploma(ctx, x, y, s, tilt=0.0):
    ctx.save()
    ctx.translate(x, y)
    ctx.rotate(tilt)
    ctx.scale(s, s)
    block(ctx, -70, -18, 140, 36, 18, hexc("#fbf3dc"), 4, outline=INK)
    rrect(ctx, -10, -20, 20, 40, 4)
    ctx.set_source_rgb(*RED)
    ctx.fill()
    ctx.restore()


def delivery_box(ctx, x, y, s, open_k=0.0):
    """Cardboard box (bottom centre x, y); open_k 0..1 swings the flaps open."""
    w, h = 300 * s, 220 * s
    block(ctx, x - w / 2, y - h, w, h, 10 * s, hexc("#c99a5e"), 5)
    rrect(ctx, x - 20 * s, y - h, 40 * s, h, 4)
    ctx.set_source_rgba(*hexc("#e8d0a0"), 1)
    ctx.fill()
    for side in (-1, 1):
        ctx.save()
        ctx.translate(x + side * w / 2, y - h)
        ctx.rotate(-side * open_k * 2.2)
        block(ctx, -w / 2 if side > 0 else 0, -14 * s, w / 2, 28 * s, 6 * s, hexc("#b8874a"), 4, gloss=False)
        ctx.restore()


def trophy(ctx, x, y, s, T=0.0, plaque=None):
    """Golden trophy (bottom centre x, y) with an optional plaque text."""
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s, s)
    glow(ctx, 0, -230, 300, (1, 0.85, 0.3), 0.55)
    block(ctx, -110, -60, 220, 60, 10, hexc("#6b4430"), 5)
    if plaque:
        rrect(ctx, -90, -50, 180, 40, 6)
        shape_fill(ctx, GOLD, 3, -50, -10, outline=INK)
        bold_text(ctx, plaque, 0, -30, 18, INK, outline=GOLD, shadow=False, stroke=0.02)
    block(ctx, -30, -130, 60, 75, 10, GOLD, 5, outline=INK)
    for side in (-1, 1):   # handles
        ctx.new_sub_path()
        ctx.arc(side * 105, -270, 45, -PI / 2 if side > 0 else PI / 2, PI / 2 if side > 0 else 3 * PI / 2)
        ctx.set_source_rgb(*INK)
        ctx.set_line_width(26)
        ctx.stroke_preserve()
        ctx.set_source_rgb(*GOLD)
        ctx.set_line_width(14)
        ctx.stroke()
    ctx.move_to(-115, -340)
    ctx.line_to(115, -340)
    ctx.curve_to(115, -200, 60, -130, 0, -130)
    ctx.curve_to(-60, -130, -115, -200, -115, -340)
    ctx.close_path()
    shape_fill(ctx, GOLD, 6, -340, -130, outline=INK)
    star_path(ctx, 0, -250, 45)
    ctx.set_source_rgb(1, 1, 1)
    ctx.fill()
    ctx.move_to(-80, -320)
    ctx.curve_to(-80, -250, -60, -200, -40, -180)
    ctx.set_source_rgba(1, 1, 1, 0.5)
    ctx.set_line_width(10)
    ctx.stroke()
    ctx.restore()
    sparkles(ctx, T, x, y - 260 * s, spread=200 * s, n=6, seed=9, c=YELLOW, size=20 * s)


def bathtub(ctx, x, y, s, T, bubbles=1.0):
    """Bathtub (bottom centre x, y) overflowing with foam; draw the bather between bathtub_back and this."""
    w, h = 520 * s, 230 * s
    if bubbles > 0:
        rnd = random.Random(5)
        for i in range(int(22 * bubbles)):
            bx = x + rnd.uniform(-w / 2, w / 2)
            by = y - h - rnd.uniform(-10, 50) * s + math.sin(T * 2 + i) * 4 * s
            r = rnd.uniform(28, 55) * s
            ctx.new_sub_path()
            ctx.arc(bx, by, r, 0, 2 * PI)
            shape_fill(ctx, (1, 1, 1), 3, by - r, by + r, outline=hexc("#9fd0f0"))
    block(ctx, x - w / 2, y - h, w, h, 70 * s, (1, 1, 1), 6, outline=INK)
    for side in (-1, 1):
        block(ctx, x + side * (w / 2 - 70 * s) - 22 * s, y - 20 * s, 44 * s, 50 * s, 10 * s, GOLD, 4, gloss=False)
    rnd = random.Random(int(T * 3))
    for i in range(6):   # floating bubbles
        ph = (T * 0.6 + i / 6) % 1
        bx = x - w / 2 + (i + 0.5) * w / 6 + math.sin(T * 3 + i) * 10
        by = y - h - 60 * s - ph * 360 * s
        ctx.new_sub_path()
        ctx.arc(bx, by, (10 + 8 * (i % 3)) * s, 0, 2 * PI)
        ctx.set_source_rgba(0.75, 0.9, 1, 0.8 * (1 - ph))
        ctx.set_line_width(3)
        ctx.stroke()


def rubber_duck(ctx, x, y, s, T=0.0):
    ctx.save()
    ctx.translate(x, y + math.sin(T * 3) * 4 * s)
    ctx.scale(s, s)
    ellipse(ctx, 0, 0, 60, 38)
    shape_fill(ctx, YELLOW, 4, -38, 38, outline=INK)
    ctx.new_sub_path()
    ctx.arc(-38, -40, 30, 0, 2 * PI)
    shape_fill(ctx, YELLOW, 4, -70, -10, outline=INK)
    ctx.move_to(-66, -40)
    ctx.line_to(-90, -34)
    ctx.line_to(-66, -28)
    ctx.close_path()
    ctx.set_source_rgb(*hexc("#ff8a3d"))
    ctx.fill()
    ctx.new_sub_path()
    ctx.arc(-44, -46, 5, 0, 2 * PI)
    ctx.set_source_rgb(*INK)
    ctx.fill()
    ctx.restore()


def stink_lines(ctx, x, y, r, T, k=1.0, col="#7ccf3a"):
    """Wavy green stink lines rising around (x, y)."""
    if k <= 0:
        return
    for i in range(5):
        ph = (T * 0.7 + i / 5) % 1
        bx = x + (i - 2) * r * 0.45
        by = y - ph * r * 1.3
        ctx.move_to(bx, by)
        for j in range(4):
            ctx.curve_to(bx + 18, by - 15 - j * 30, bx - 18, by - 30 - j * 30, bx, by - 30 - (j + 1) * 30 + 30)
        a = k * math.sin(ph * PI)
        ctx.set_source_rgba(*c_(col), 0.9 * a)
        ctx.set_line_width(9)
        ctx.set_line_cap(cairo.LINE_CAP_ROUND)
        ctx.stroke()


def flies(ctx, x, y, r, T, n=4):
    for i in range(n):
        a = T * (4 + i) + i * 1.7
        fx, fy = x + math.cos(a) * r * (0.6 + 0.1 * i), y + math.sin(a * 1.3) * r * 0.5
        ctx.new_sub_path()
        ctx.arc(fx, fy, 7, 0, 2 * PI)
        ctx.set_source_rgb(*INK)
        ctx.fill()
        for side in (-1, 1):
            ellipse(ctx, fx + side * 8, fy - 8, 7, 5)
            ctx.set_source_rgba(1, 1, 1, 0.8)
            ctx.fill()


def scroll(ctx, x, y, s, T, open_k=1.0, title="LEGEND"):
    """Old parchment scroll unrolling vertically (centre x, y)."""
    if s <= 0.01:
        return
    h = 560 * s * max(0.08, open_k)
    w = 440 * s
    rrect(ctx, x - w / 2, y - h / 2, w, h, 10)
    shape_fill(ctx, hexc("#f2dca0"), 5, y - h / 2, y + h / 2, outline=hexc("#8a5a2a"))
    for side in (-1, 1):
        block(ctx, x - w / 2 - 20 * s, y + side * h / 2 - 22 * s, w + 40 * s, 44 * s, 22 * s, hexc("#c99a5e"), 5)
    if open_k > 0.6:
        bold_text(ctx, title, x, y - h / 2 + 70 * s, 50 * s, hexc("#8a5a2a"), outline=hexc("#f2dca0"),
                  shadow=False, stroke=0.02)


def screen_obby(ctx, x, y, w, h, T, avatar=None, stage="STAGE 1", fail=None):
    """Monitor content: a small obby over lava with an avatar callback avatar(ctx, ax, ay, s, T)."""
    g = cairo.LinearGradient(0, y, 0, y + h)
    g.add_color_stop_rgb(0, *hexc("#84d4fb"))
    g.add_color_stop_rgb(1, *hexc("#b8e8fb"))
    ctx.rectangle(x, y, w, h)
    ctx.set_source(g)
    ctx.fill()
    lava(ctx, y + h * 0.8, T)
    for i in range(4):
        px = x + w * (0.05 + i * 0.25)
        platform(ctx, px, y + h * (0.62 - 0.04 * i), w * 0.14, ("#2cd5fc", "#fa3a9f", "#f7e04a", "#a694e1")[i],
                 depth=w * 0.03, h=h * 0.08)
    if avatar:
        avatar(ctx, x + w * 0.15, y + h * 0.62, w / 900, T)
    stage_pill(ctx, x + w / 2, y + h * 0.13, stage, s=w / 1100)
    if fail:
        bold_text(ctx, fail, x + w / 2, y + h * 0.35, h * 0.12, RED, stroke=0.14)


# ================================================================ more props (added for robux10.py)
def mystery_box(ctx, x, y, s, T, open_k=0.0, glow_a=0.0):
    """Purple gift box with a gold '?' (bottom centre x, y); open_k 0..1 lifts the lid off."""
    if glow_a > 0:
        glow(ctx, x, y - 160 * s, 360 * s, (1, 0.85, 0.3), glow_a)
    w, h = 300 * s, 230 * s
    block(ctx, x - w / 2, y - h, w, h, 18 * s, hexc("#7a3fd8"), 6)
    rrect(ctx, x - 26 * s, y - h, 52 * s, h, 4)
    ctx.set_source_rgb(*GOLD)
    ctx.fill()
    bold_text(ctx, "?", x + 85 * s, y - h / 2, 110 * s, GOLD, stroke=0.14)
    ctx.save()
    ctx.translate(x - open_k * 160 * s, y - h - open_k * 260 * s)
    ctx.rotate(-open_k * 1.1)
    block(ctx, -w / 2 - 18 * s, -60 * s, w + 36 * s, 66 * s, 16 * s, hexc("#9d5cff"), 6)
    rrect(ctx, -26 * s, -60 * s, 52 * s, 66 * s, 4)
    ctx.set_source_rgb(*GOLD)
    ctx.fill()
    for side in (-1, 1):   # bow
        ellipse(ctx, side * 55 * s, -85 * s, 55 * s, 30 * s)
        shape_fill(ctx, GOLD, 5, -115 * s, -55 * s, outline=INK)
    ctx.restore()
    if open_k > 0.3:
        for i in range(5):   # light beams from the open box
            a = -PI / 2 + (i - 2) * 0.28
            ctx.move_to(x - 40 * s, y - h)
            ctx.line_to(x + math.cos(a - 0.08) * 900, y - h + math.sin(a - 0.08) * 900)
            ctx.line_to(x + math.cos(a + 0.08) * 900, y - h + math.sin(a + 0.08) * 900)
            ctx.line_to(x + 40 * s, y - h)
            ctx.close_path()
        ctx.set_source_rgba(1, 0.92, 0.5, 0.22 * open_k)
        ctx.fill()


def golden_ticket(ctx, x, y, s, rot=0.0, flip=1.0):
    """Golden ticket (centre x, y); flip -1..1 squashes it horizontally (spinning)."""
    ctx.save()
    ctx.translate(x, y)
    ctx.rotate(rot)
    ctx.scale(s * max(0.08, abs(flip)), s)
    w, h = 340, 170
    ctx.move_to(-w / 2, -h / 2)
    ctx.line_to(w / 2, -h / 2)
    ctx.arc_negative(w / 2, 0, 26, -PI / 2, PI / 2)
    ctx.line_to(-w / 2, h / 2)
    ctx.arc_negative(-w / 2, 0, 26, PI / 2, -PI / 2)
    ctx.close_path()
    shape_fill(ctx, GOLD, 7, -h / 2, h / 2, outline=INK)
    rrect(ctx, -w / 2 + 34, -h / 2 + 18, w - 68, h - 36, 10)
    ctx.set_source_rgb(*hexc("#e6a92a"))
    ctx.set_line_width(4)
    ctx.set_dash([10, 8])
    ctx.stroke()
    ctx.set_dash([])
    if flip > 0:
        bold_text(ctx, "GOLDEN", 0, -22, 40, (1, 1, 1), stroke=0.16, shadow=False)
        bold_text(ctx, "TICKET", 0, 26, 40, (1, 1, 1), stroke=0.16, shadow=False)
    ctx.restore()


def number_counter(ctx, x, y, s, value, T, spinning=False, col="#ffd84a", prefix="R$ "):
    """Big slot-style counter panel (centre x, y). spinning blurs the digits."""
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s, s)
    block(ctx, -300, -95, 600, 190, 40, hexc("#1f2236"), 7, outline=GOLD)
    txt = prefix + (f"{int(value):,}" if not spinning else f"{int(value):,}")
    if spinning:
        for k in (-1, 1):   # motion smear of rolling digits
            bold_text(ctx, txt, 0, k * 26, 74, c_(col), outline=INK, shadow=False, stroke=0.1, scale=0.95)
        ctx.set_source_rgba(0.12, 0.13, 0.21, 0.55)
        ctx.rectangle(-290, -90, 580, 180)
        ctx.fill()
    bold_text(ctx, txt, 0, 0, 74, c_(col), stroke=0.14, shadow=False)
    ctx.restore()


def glitch(ctx, T, k=1.0, seed=0):
    """RGB glitch bars + static over the whole frame (k = strength)."""
    if k <= 0:
        return
    rnd = random.Random(int(T * 24) + seed)
    for _ in range(int(10 * k)):
        y = rnd.uniform(-200, 1500)
        h = rnd.uniform(6, 60)
        c = rnd.choice([(1, 0.1, 0.3), (0.1, 1, 0.9), (1, 1, 1), (0.3, 0.3, 1)])
        ctx.rectangle(-3000 + rnd.uniform(-60, 60), y, 7000, h)
        ctx.set_source_rgba(*c, 0.35 * k)
        ctx.fill()


def prize_wheel(ctx, x, y, r, T, angle=0.0):
    """Prize wheel with coloured wedges and a pointer at the top."""
    cols = [RED, YELLOW, GREEN, BLUE, PINK, PURPLE, hexc("#ff8a3d"), hexc("#2fbf8f")]
    n = len(cols)
    for i in range(n):
        a0 = angle + i * 2 * PI / n
        ctx.move_to(x, y)
        ctx.arc(x, y, r, a0, a0 + 2 * PI / n)
        ctx.close_path()
        ctx.set_source_rgb(*cols[i])
        ctx.fill_preserve()
        ctx.set_source_rgb(*INK)
        ctx.set_line_width(5)
        ctx.stroke()
        am = a0 + PI / n
        star_path(ctx, x + math.cos(am) * r * 0.66, y + math.sin(am) * r * 0.66, r * 0.09)
        ctx.set_source_rgb(1, 1, 1)
        ctx.fill()
    ctx.new_sub_path()
    ctx.arc(x, y, r, 0, 2 * PI)
    ctx.set_source_rgb(*INK)
    ctx.set_line_width(12)
    ctx.stroke()
    ctx.new_sub_path()
    ctx.arc(x, y, r * 0.14, 0, 2 * PI)
    shape_fill(ctx, GOLD, 5, y - r * 0.14, y + r * 0.14, outline=INK)
    ctx.move_to(x - r * 0.12, y - r - 30)
    ctx.line_to(x + r * 0.12, y - r - 30)
    ctx.line_to(x, y - r + 40)
    ctx.close_path()
    shape_fill(ctx, RED, 5, y - r - 30, y - r + 40, outline=INK)


def credit_card(ctx, x, y, s, rot=0.0, col="#2f6bd8"):
    if s <= 0.01:
        return
    ctx.save()
    ctx.translate(x, y)
    ctx.rotate(rot)
    ctx.scale(s, s)
    block(ctx, -170, -105, 340, 210, 22, c_(col), 6, outline=INK)
    block(ctx, -130, -50, 70, 52, 8, GOLD, 4, outline=INK, gloss=False)
    bold_text(ctx, "**** 4021", 20, 50, 34, (1, 1, 1), shadow=False, stroke=0.0)
    bold_text(ctx, "MOM", 110, -60, 30, (1, 1, 1), shadow=False, stroke=0.0)
    ctx.restore()


def pet_puppy(ctx, x, y, s, T, col="#ffcc33"):
    """Legendary golden blocky puppy (bottom centre x, y)."""
    if s <= 0.01:
        return
    ctx.save()
    ctx.translate(x, y + math.sin(T * 6) * -6 * s)
    ctx.scale(s, s)
    c = c_(col)
    for lx in (-60, 40):
        block(ctx, lx, -70, 34, 70, 8, c, 5)
    block(ctx, -100, -170, 200, 110, 30, c, 6)
    ctx.move_to(100, -150)
    ctx.curve_to(150, -200, 150, -230, 130, -250)
    ctx.set_source_rgb(*INK)
    ctx.set_line_width(26)
    ctx.stroke_preserve()
    ctx.set_source_rgb(*c)
    ctx.set_line_width(14)
    ctx.stroke()
    block(ctx, -150, -290, 170, 150, 40, c, 6)
    for ex in (-150, 0):   # ears
        ctx.save()
        ctx.translate(ex + 10, -270)
        ctx.rotate(-0.5 if ex < 0 else 0.5)
        block(ctx, -22, -10, 44, 90, 20, dark(c, 0.15), 5, gloss=False)
        ctx.restore()
    for ex in (-110, -30):
        ellipse(ctx, ex, -220, 13, 18)
        ctx.set_source_rgb(*INK)
        ctx.fill()
        ctx.new_sub_path()
        ctx.arc(ex + 5, -227, 5, 0, 2 * PI)
        ctx.set_source_rgb(1, 1, 1)
        ctx.fill()
    ellipse(ctx, -70, -185, 16, 11)
    ctx.set_source_rgb(*INK)
    ctx.fill()
    ctx.move_to(-95, -168)
    ctx.curve_to(-80, -150, -60, -150, -45, -168)
    ctx.set_source_rgb(*INK)
    ctx.set_line_width(5)
    ctx.stroke()
    ctx.restore()
    sparkles(ctx, T, x, y - 200 * s, spread=180 * s, n=6, seed=12, c=YELLOW, size=18 * s)


def tap_ripple(ctx, x, y, k):
    if not 0 < k < 1:
        return
    for j in range(2):
        kk = clamp(k - j * 0.2)
        ctx.new_sub_path()
        ctx.arc(x, y, 20 + kk * 120, 0, 2 * PI)
        ctx.set_source_rgba(1, 1, 1, 0.9 * (1 - kk))
        ctx.set_line_width(8)
        ctx.stroke()


# ================================================================ ending: REWIND montage (script_guide.md section 6)
def rewind_shot(shots, picks):
    """The references' loop ending: after the last word, earlier shots flash BACKWARDS
    (~0.15-0.25 s each) under a '<< REWIND' label and scanlines, landing exactly on the first frame.

    shots : the story's SHOTS list (read at draw time, so safezone.fit's camera keys are used)
    picks : absolute story times to flash, in playing order, e.g. [41.0, 33.4, 24.5, 12.6, 0.0];
            end with 0.0 so the last frame equals the first frame.
    Returns (draw, overlay) for a shot with keys [(start, 1.0, (W / 2, H / 2))]:
      shot(t_end, draw, [(t_end, 1.0, (360, 640))], overlay=overlay, blur=False, closeup=True, keep=[])"""
    import engine

    def source(T):
        i = max(k for k, s in enumerate(shots) if s["start"] <= T or k == 0)
        return shots[i]

    def pick(t, d):
        k = min(len(picks) - 1, int(t / max(d, 1e-6) * len(picks)))
        seg = d / len(picks)
        back = (t - k * seg) * 2.0                   # play each flash backwards at double speed
        return max(0.0, picks[k] - back) if k < len(picks) - 1 else picks[-1], k

    def draw(ctx, t, d):
        T, _ = pick(t, d)
        src = source(T)
        z, (cx, cy) = engine.key_camera(src["keys"], T)
        ctx.save()
        ctx.translate(W / 2, H / 2)
        ctx.scale(z, z)
        ctx.translate(-cx, -cy)
        src["draw"](ctx, T - src["start"], src["end"] - src["start"])
        ctx.restore()

    def overlay(ctx, t, d):
        T, k = pick(t, d)
        src = source(T)
        if src.get("overlay"):
            src["overlay"](ctx, T - src["start"], src["end"] - src["start"])
        if k < len(picks) - 1:                       # the last flash is the clean first frame
            ctx.rectangle(0, 0, W, H)
            ctx.set_source_rgba(0.1, 0.12, 0.3, 0.18)
            ctx.fill()
            rewind_bars(ctx, 0.3 + 0.4 * ((t * 7) % 1))   # flickering scanlines + the '<< REWIND' label
    return draw, overlay


# ================================================================ more props (added for grandma_pro.py)
def walking_stick(ctx, x, y, s, ang=0.0, col="#8a5a3a"):
    """Wooden walking cane; (x, y) = the handle top, ang rotates it about the handle."""
    ctx.save()
    ctx.translate(x, y)
    ctx.rotate(ang)
    ctx.scale(s, s)
    ctx.new_sub_path()
    ctx.arc(-30, 0, 30, PI, 2 * PI)
    ctx.line_to(0, 300)
    for lw, c in ((26, INK), (16, c_(col))):
        ctx.set_source_rgb(*c)
        ctx.set_line_width(lw)
        ctx.set_line_cap(cairo.LINE_CAP_ROUND)
        ctx.stroke_preserve()
    ctx.new_path()
    block(ctx, -12, 290, 24, 24, 8, hexc("#3b3550"), 3, gloss=False)
    ctx.restore()


def yarn_ball(ctx, x, y, r, col="#e8323a", needles=True, T=0.0):
    ctx.new_sub_path()
    ctx.arc(x, y, r, 0, 2 * PI)
    shape_fill(ctx, c_(col), max(2, r * 0.08), y - r, y + r)
    ctx.save()
    ctx.new_sub_path()
    ctx.arc(x, y, r * 0.95, 0, 2 * PI)
    ctx.clip()
    for k in range(5):
        ctx.new_sub_path()
        ctx.arc(x - r * 0.6 + k * r * 0.3, y, r * 0.9, -1.2, 1.2)
    ctx.set_source_rgba(*dark(c_(col), 0.3), 1)
    ctx.set_line_width(max(2, r * 0.06))
    ctx.stroke()
    ctx.restore()
    if needles:
        for a in (-0.5 + 0.08 * math.sin(T * 12), 0.4 - 0.08 * math.sin(T * 12)):
            ctx.move_to(x, y)
            ctx.line_to(x + math.sin(a) * r * 2.2, y - math.cos(a) * r * 2.2)
            ctx.set_source_rgb(*hexc("#c9cde0"))
            ctx.set_line_width(max(3, r * 0.1))
            ctx.set_line_cap(cairo.LINE_CAP_ROUND)
            ctx.stroke()


def cookie(ctx, x, y, r, rot=0.0):
    """Chocolate-chip cookie."""
    ctx.save()
    ctx.translate(x, y)
    ctx.rotate(rot)
    ctx.new_sub_path()
    ctx.arc(0, 0, r, 0, 2 * PI)
    shape_fill(ctx, hexc("#e0a85a"), max(2, r * 0.08), -r, r, outline=hexc("#8a5a2a"))
    for dx, dy in ((-0.4, -0.3), (0.35, -0.4), (0.1, 0.15), (-0.3, 0.45), (0.5, 0.3)):
        ctx.new_sub_path()
        ctx.arc(dx * r, dy * r, r * 0.13, 0, 2 * PI)
        ctx.set_source_rgb(*hexc("#5a3020"))
        ctx.fill()
    ctx.restore()


def veggie_plate(ctx, x, y, s):
    """A plate piled with broccoli (bottom centre x, y)."""
    ellipse(ctx, x, y, 170 * s, 40 * s)
    shape_fill(ctx, (1, 1, 1), 5, y - 40 * s, y + 40 * s, outline=INK)
    for dx in (-80, 0, 80):
        bx = x + dx * s
        block(ctx, bx - 14 * s, y - 70 * s, 28 * s, 60 * s, 8 * s, hexc("#9bd36a"), 4, gloss=False)
        for ox, oy in ((-30, -90), (0, -110), (30, -90), (-15, -125), (18, -125)):
            ctx.new_sub_path()
            ctx.arc(bx + ox * s, y + oy * s, 26 * s, 0, 2 * PI)
        shape_fill(ctx, hexc("#3fa84a"), 4, y - 150 * s, y - 60 * s, outline=hexc("#1f5a28"))


def vs_banner(ctx, x, y, k, left="YOU", right="GRANDMA"):
    """'YOU VS GRANDMA' fight banner that slams in (k = time since)."""
    if k < 0:
        return
    sc = pop(k)
    ctx.save()
    ctx.translate(x, y)
    ctx.rotate(-0.05)
    ctx.scale(sc, sc)
    for side, txt, col in ((-1, left, BLUE), (1, right, PINK)):
        ctx.move_to(side * 20, -60)
        ctx.line_to(side * 320, -60)
        ctx.line_to(side * 290, 60)
        ctx.line_to(side * -10, 60)
        ctx.close_path()
        shape_fill(ctx, col, 6, -60, 60, outline=INK)
        bold_text(ctx, txt, side * 165, 0, 44, (1, 1, 1), stroke=0.14, shadow=False)
    star_path(ctx, 0, 0, 95, inner=0.55, n=10)
    shape_fill(ctx, YELLOW, 6, -95, 95, outline=INK)
    bold_text(ctx, "VS", 0, 0, 70, RED, stroke=0.14, shadow=False)
    ctx.restore()

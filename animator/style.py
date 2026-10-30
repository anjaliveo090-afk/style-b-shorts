"""Style B characters: flat-vector blocky game avatars (style_bible.md sections 3-4).

Measured in head-widths (hw): head 1.0 x 0.9, torso 1.1 x 1.05, arms 0.55 x 1.15,
legs 0.55 x 1.0 each, total ~3.25 hw with hair. Outlines are a dark shade of each
part's own colour, light comes from the top-left with a glossy streak inside each
block. Block.draw() has the same signature as style2.Char2.draw(), so story templates
work unchanged. hw = 1.45 r (r = 64 * s px): a character at s=1 is ~300 px tall."""
import math

import cairo

import engine
from engine import PI, draw_item, ellipse, hexc, rrect, src

INK = hexc("#2a1e2e")
EYE = hexc("#1a1020")
MOUTH = hexc("#5a1626")
TONGUE = hexc("#ff6a8d")
TEETH = hexc("#ffffff")
BLUSH = hexc("#ff8fa3")
TEAR = hexc("#6fc3ff")
PALE = hexc("#b9d6ff")
RAGE = hexc("#ff5a4a")
WHITE = (1.0, 1.0, 1.0)
FONT = "Inter Display Black"   # apt package fonts-inter (setup.sh); cairo falls back to a sans if missing

HAPPY = ("happy", "laugh", "grin", "stars", "wink", "crazy")
HALF_LID = ("smirk", "smug", "cold", "tired")


# ---------------------------------------------------------------- colour + block helpers
def mix(a, b, k):
    return tuple(x + (y - x) * k for x, y in zip(a, b))


def light(c, k=0.15):
    return mix(c, WHITE, k)


def dark(c, k=0.15):
    return tuple(v * (1 - k) for v in c)


def line_of(c):
    """Outline colour: the fill pushed ~70% toward the deep brown-purple ink."""
    return mix(c, INK, 0.72)


def col(c):
    return hexc(c) if isinstance(c, str) else c


def block(ctx, x, y, w, h, r, c, lw, gloss=True, grad=0.13, outline=None):
    """Rounded block (top-left x, y) with a vertical light->dark gradient, an inner
    glossy highlight on the top-left edge and a self-coloured outline."""
    rrect(ctx, x, y, w, h, r)
    g = cairo.LinearGradient(0, y, 0, y + h)
    g.add_color_stop_rgb(0, *light(c, grad))
    g.add_color_stop_rgb(0.45, *c)
    g.add_color_stop_rgb(1, *dark(c, grad))
    ctx.set_source(g)
    ctx.fill_preserve()
    ctx.set_source_rgb(*(outline or line_of(c)))
    ctx.set_line_width(lw)
    ctx.stroke()
    if gloss and w > 6 * lw and h > 6 * lw:
        i = lw * 1.9
        ctx.move_to(x + i, y + min(h * 0.42, h - r))
        ctx.line_to(x + i, y + min(r, h / 3))
        ctx.curve_to(x + i, y + i, x + i, y + i, x + min(r, w / 3), y + i)
        ctx.line_to(x + w * 0.42, y + i)
        ctx.set_source_rgba(1, 1, 1, 0.38)
        ctx.set_line_width(lw * 0.9)
        ctx.set_line_cap(cairo.LINE_CAP_ROUND)
        ctx.stroke()


def shape_fill(ctx, c, lw, y0, y1, grad=0.13, outline=None):
    """Fill the current path with the block gradient and stroke it with the self-coloured line."""
    g = cairo.LinearGradient(0, y0, 0, y1)
    g.add_color_stop_rgb(0, *light(c, grad))
    g.add_color_stop_rgb(1, *dark(c, grad))
    ctx.set_source(g)
    ctx.fill_preserve()
    ctx.set_source_rgb(*(outline or line_of(c)))
    ctx.set_line_width(lw)
    ctx.stroke()


def star_path(ctx, x, y, r, inner=0.45, n=5, rot=-PI / 2):
    for i in range(2 * n):
        rr = r if i % 2 == 0 else r * inner
        a = rot + i * PI / n
        (ctx.move_to if i == 0 else ctx.line_to)(x + math.cos(a) * rr, y + math.sin(a) * rr)
    ctx.close_path()


# ---------------------------------------------------------------- reaction FX (also used by sets.py)
def sweat(ctx, x, y, d, t=0.0):
    """Blue sweat drop (d = drop height)."""
    y += ((t * 1.5) % 1) * d * 0.3
    ctx.move_to(x, y - d)
    ctx.curve_to(x + d * 0.55, y - d * 0.2, x + d * 0.5, y + d * 0.45, x, y + d * 0.45)
    ctx.curve_to(x - d * 0.5, y + d * 0.45, x - d * 0.55, y - d * 0.2, x, y - d)
    shape_fill(ctx, hexc("#8fd6ff"), max(1.5, d * 0.09), y - d, y + d * 0.45)


def anger_mark(ctx, x, y, d, t=0.0):
    """Red cross-shaped anger vein (d = size), pulsing."""
    k = 1 + 0.12 * math.sin(t * 18)
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(k, k)
    for q in range(4):
        ctx.save()
        ctx.rotate(q * PI / 2)
        ctx.move_to(d * 0.12, -d * 0.5)
        ctx.curve_to(d * 0.12, -d * 0.18, d * 0.18, -d * 0.12, d * 0.5, -d * 0.12)
        ctx.restore()
    ctx.set_source_rgb(*hexc("#e8323a"))
    ctx.set_line_width(d * 0.16)
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    ctx.stroke()
    ctx.restore()


def shake_lines(ctx, x, y, rx, ry, t, n=3, lw=4.0, c=(1, 1, 1)):
    """Short radiating lines around a head (shock / panic)."""
    j = math.sin(t * 40) * lw * 0.6
    for side in (-1, 1):
        for i in range(n):
            a = (-0.55 + i * 0.45) * side + (0 if side > 0 else PI)
            cx, cy = x + math.cos(a) * rx, y + math.sin(a) * ry
            ctx.move_to(cx + math.cos(a) * j, cy + math.sin(a) * j)
            ctx.line_to(cx + math.cos(a) * (rx * 0.28 + j), cy + math.sin(a) * (ry * 0.28 + j))
    ctx.set_source_rgba(*c, 0.9)
    ctx.set_line_width(lw)
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    ctx.stroke()


def sparkle(ctx, x, y, r, a=1.0, c=(1, 1, 1)):
    """Four-point twinkle star."""
    ctx.move_to(x, y - r)
    ctx.curve_to(x + r * 0.12, y - r * 0.12, x + r * 0.12, y - r * 0.12, x + r, y)
    ctx.curve_to(x + r * 0.12, y + r * 0.12, x + r * 0.12, y + r * 0.12, x, y + r)
    ctx.curve_to(x - r * 0.12, y + r * 0.12, x - r * 0.12, y + r * 0.12, x - r, y)
    ctx.curve_to(x - r * 0.12, y - r * 0.12, x - r * 0.12, y - r * 0.12, x, y - r)
    ctx.close_path()
    ctx.set_source_rgba(*c, a)
    ctx.fill()


# ---------------------------------------------------------------- the character
class Block:
    """Blocky game avatar. All options are looks; motion comes from draw()."""
    HW = 1.45          # head width in units of r
    BBOX = (5.0, 1.7)  # (top, half width) in r, for safezone.fit

    def __init__(self, shirt, pants=None, skin="#e6ddd6", hair="bowl", hair_col="#8d5e3b", outfit="shirt",
                 emblem=None, emblem_col="#ffffff", sleeves=None, shoes="white", headband=None, headset=None,
                 glasses=False, crown=False, cap=None, cap_text=None, lashes=False, curlers=None, shades=False,
                 brow_col=None, accent=None):
        self.shirt = col(shirt)
        self.pants = col(pants) if pants else dark(self.shirt, 0.08)
        self.skin = col(skin)
        self.hair = hair
        self.hair_col = col(hair_col)
        self.outfit = outfit
        self.emblem = emblem
        self.emblem_col = col(emblem_col)
        self.sleeves = sleeves or ("short" if outfit in ("tshirt", "robe", "cardigan") else "long")
        self.shoes = shoes
        self.headband = col(headband) if headband else None
        self.headset = headset
        self.glasses = glasses
        self.crown = crown
        self.cap = col(cap) if cap else None
        self.cap_text = cap_text
        self.lashes = lashes
        self.curlers = col(curlers) if curlers else None
        self.shades = shades
        self.brow = col(brow_col) if brow_col else mix(self.hair_col, INK, 0.75)
        self.accent = col(accent) if accent else hexc("#ffffff")

    # ------------------------------------------------------------------
    def draw(self, ctx, x, y, s=1.0, expr="neutral", t=0.0, talk=False,
             arms=("down", "down"), pose="stand", look=0.0, bob=1.0,
             item=None, item_hand=1, walk_phase=0.0, lean=0.0, head_nod=0.0, shadow=True):
        r = 64 * s
        u = self.HW * r                      # head width
        e = engine.ENERGY * bob
        lw = max(2.4, 0.019 * u + 1.6)
        ctx.save()
        ctx.translate(x, y)
        ctx.set_line_join(cairo.LINE_JOIN_ROUND)
        ctx.set_line_cap(cairo.LINE_CAP_ROUND)

        if shadow:
            ctx.save()
            ctx.scale(1, 0.18)
            g = cairo.RadialGradient(0, 0, 0, 0, 0, u * 0.95)
            g.add_color_stop_rgba(0, 0, 0, 0, 0.32)
            g.add_color_stop_rgba(1, 0, 0, 0, 0)
            ctx.set_source(g)
            ctx.arc(0, 0, u * 0.95, 0, 2 * PI)
            ctx.fill()
            ctx.restore()

        bounce = -abs(math.sin(t * 2 * PI * 1.6)) * 0.035 * u * e
        leg_h = 1.0 * u
        if pose == "sit":
            leg_h = 0.5 * u
        hip = -leg_h + bounce
        top = hip - 1.05 * u                 # torso top

        self._legs(ctx, u, lw, hip, leg_h, pose, walk_phase, t)

        ctx.save()                          # upper body sways / leans around the hip
        ctx.translate(0, hip)
        ctx.rotate(lean + math.sin(t * 2.6) * 0.02 * e)
        ctx.translate(0, -hip)

        front = []
        for i, side in enumerate((-1, 1)):
            a = arms[i] if i < len(arms) else "down"
            ang, length, infront = self._arm_angle(a, side, t, e)
            if infront:
                front.append((i, side, a, ang, length))
            else:
                self._arm(ctx, u, lw, top, side, ang, length, item if i == item_hand else None, t)
        self._torso(ctx, u, lw, top, hip)
        hcx = 0.0
        hcy = top - 0.45 * u + 0.02 * u + head_nod + math.sin(t * 4.1) * 0.012 * u * e
        for i, side, a, ang, length in front:
            if a not in ("cover",):
                self._arm(ctx, u, lw, top, side, ang, length, item if i == item_hand else None, t)
        self._head(ctx, hcx, hcy, u, lw, expr, t, talk, look)
        for i, side, a, ang, length in front:
            if a == "cover":
                self._arm(ctx, u, lw, top, side, ang, length, None, t)
        ctx.restore()
        ctx.restore()

    # ------------------------------------------------------------------ limbs
    def _arm_angle(self, a, side, t, e):
        """(angle from hanging straight down, positive = outward), length factor, drawn in front."""
        wob = math.sin(t * 3.4 + side) * 0.05 * e
        tbl = {
            "down": (0.03 + wob * 0.5, 1.0, False),
            "up": (2.85 + wob, 1.0, False),
            "point": (1.55 + wob * 0.5, 1.0, False),
            "punch": (1.6, 1.15, False),
            "show": (2.25 + wob, 1.0, False),
            "hip": (0.38 + wob, 1.0, False),
            "shrug": (1.05 + wob, 1.0, False),
            "wave": (2.55 + math.sin(t * 11) * 0.35, 1.0, False),
            "wag": (2.35 + math.sin(t * 14) * 0.2, 1.0, False),
            "salute": (2.95, 0.95, False),
            "hold": (-0.42 + wob * 0.5, 0.78, True),
            "write": (-0.5 + math.sin(t * 22) * 0.06, 0.78, True),
            "cross": (-1.25, 0.82, True),
            "cover": (-2.55 + wob * 0.3, 0.95, True),     # hands over the face / mouth
            "phone": (-2.2, 0.85, True),                  # holds something up to the face
        }
        ang, ln, front = tbl.get(a, tbl["down"])
        return -side * ang, ln, front

    def _arm(self, ctx, u, lw, top, side, ang, length, item, t):
        aw, al = 0.55 * u, 1.15 * u * length
        px, py = side * 0.8 * u, top + 0.22 * u
        ctx.save()
        ctx.translate(px, py)
        ctx.rotate(ang)
        x0, y0 = -aw / 2, -0.22 * u
        if self.sleeves == "short":
            cut = y0 + al * 0.62
            block(ctx, x0, cut - 0.1 * u, aw, al - (cut - y0) + 0.1 * u, 0.1 * u, self.skin, lw)
            sl = self.shirt if self.outfit != "robe" else self.shirt
            block(ctx, x0, y0, aw, cut - y0, 0.1 * u, sl, lw)
            if self.outfit == "robe":   # puffy cuff
                rrect(ctx, x0 - 0.03 * u, cut - 0.12 * u, aw + 0.06 * u, 0.14 * u, 0.06 * u)
                shape_fill(ctx, light(self.shirt, 0.12), lw, cut - 0.12 * u, cut)
        elif self.sleeves == "skin":
            block(ctx, x0, y0, aw, al, 0.1 * u, self.skin, lw)
        else:
            block(ctx, x0, y0, aw, al, 0.1 * u, self.shirt, lw)
        if item:
            ctx.save()
            ctx.translate(0, y0 + al * 0.92)
            ctx.rotate(-ang)
            ctx.scale(u / 93, u / 93)
            draw_item(ctx, item, 0, 0, t)
            ctx.restore()
        ctx.restore()

    def _legs(self, ctx, u, lw, hip, leg_h, pose, walk_phase, t):
        lw_ = 0.55 * u
        for side in (-1, 1):
            ang = 0.0
            if pose in ("walk", "run"):
                amp = 0.32 if pose == "walk" else 0.6
                ang = math.sin(walk_phase * 2 * PI + (0 if side < 0 else PI)) * amp
            elif pose == "jump":
                ang = side * 0.28
            elif pose == "feetup":
                ang = -1.35
            ctx.save()
            ctx.translate(side * 0.275 * u, hip - 0.04 * u)
            ctx.rotate(ang)
            x0 = -lw_ / 2
            h = leg_h + 0.04 * u
            block(ctx, x0, 0, lw_, h, 0.06 * u, self.pants, lw, gloss=pose != "sit")
            if self.shoes == "white":
                block(ctx, x0, h - 0.13 * u, lw_, 0.13 * u, 0.05 * u, hexc("#f4f4f8"), lw, gloss=False)
            elif self.shoes == "dark":
                block(ctx, x0, h - 0.13 * u, lw_, 0.13 * u, 0.05 * u, hexc("#3b3550"), lw, gloss=False)
            elif self.shoes == "slippers":
                self._slipper(ctx, 0, h, u, lw)
            ctx.restore()

    def _slipper(self, ctx, x, y, u, lw):
        pink = hexc("#ff8fc8")
        for ex in (-0.13, 0.13):        # bunny ears
            ctx.save()
            ctx.translate(x + ex * u, y - 0.2 * u)
            ctx.rotate(ex * 1.2)
            ellipse(ctx, 0, -0.1 * u, 0.06 * u, 0.13 * u)
            shape_fill(ctx, pink, lw * 0.8, -0.23 * u, 0.03 * u)
            ellipse(ctx, 0, -0.1 * u, 0.025 * u, 0.08 * u)
            ctx.set_source_rgb(*hexc("#ffd0e6"))
            ctx.fill()
            ctx.restore()
        rrect(ctx, x - 0.32 * u, y - 0.2 * u, 0.64 * u, 0.24 * u, 0.1 * u)
        shape_fill(ctx, pink, lw, y - 0.2 * u, y + 0.04 * u)
        for ex in (-0.09, 0.09):
            ctx.new_sub_path()
            ctx.arc(x + ex * u, y - 0.09 * u, 0.022 * u, 0, 2 * PI)
            ctx.set_source_rgb(*INK)
            ctx.fill()

    # ------------------------------------------------------------------ torso / outfits
    def _torso(self, ctx, u, lw, top, hip):
        tw = 1.1 * u
        x0 = -tw / 2
        h = hip - top
        block(ctx, x0, top, tw, h, 0.08 * u, self.shirt, lw)
        # soft shadow of the head on the torso top
        g = cairo.LinearGradient(0, top, 0, top + 0.22 * u)
        g.add_color_stop_rgba(0, 0, 0, 0, 0.22)
        g.add_color_stop_rgba(1, 0, 0, 0, 0)
        rrect(ctx, x0 + lw / 2, top + lw / 2, tw - lw, 0.22 * u, 0.06 * u)
        ctx.set_source(g)
        ctx.fill()
        o = self.outfit
        if o == "robe":
            under = hexc("#f2eefa")
            ctx.move_to(-0.24 * u, top + lw)
            ctx.line_to(0.24 * u, top + lw)
            ctx.line_to(0.0, top + 0.62 * u)
            ctx.close_path()
            shape_fill(ctx, under, lw * 0.8, top, top + 0.6 * u)
            for side in (-1, 1):   # lapels
                ctx.move_to(side * 0.24 * u, top + lw)
                ctx.line_to(side * 0.34 * u, top + lw)
                ctx.line_to(side * 0.04 * u, top + 0.72 * u)
                ctx.line_to(0, top + 0.62 * u)
                ctx.close_path()
                shape_fill(ctx, light(self.shirt, 0.1), lw * 0.8, top, top + 0.7 * u)
            for k in range(11):    # pearl necklace
                a = PI * (0.12 + 0.76 * k / 10)
                ctx.new_sub_path()
                ctx.arc(math.cos(a) * 0.2 * u, top + 0.05 * u + math.sin(a) * 0.32 * u, 0.035 * u, 0, 2 * PI)
                shape_fill(ctx, hexc("#ece6f5"), lw * 0.5, top, top + 0.4 * u)
            block(ctx, x0 + lw, top + 0.7 * u, tw - 2 * lw, 0.13 * u, 0.04 * u, dark(self.shirt, 0.06), lw * 0.8,
                  gloss=False)
            ctx.new_sub_path()   # belt knot + tails
            ctx.arc(0.1 * u, top + 0.765 * u, 0.06 * u, 0, 2 * PI)
            shape_fill(ctx, light(self.shirt, 0.08), lw * 0.7, top + 0.7 * u, top + 0.83 * u)
            ctx.move_to(0.08 * u, top + 0.82 * u)
            ctx.curve_to(0.06 * u, top + 0.95 * u, 0.1 * u, top + 1.0 * u, 0.06 * u, top + 1.05 * u)
            ctx.move_to(0.14 * u, top + 0.82 * u)
            ctx.curve_to(0.18 * u, top + 0.92 * u, 0.2 * u, top + 0.98 * u, 0.2 * u, top + 1.04 * u)
            ctx.set_source_rgb(*line_of(self.shirt))
            ctx.set_line_width(lw * 1.6)
            ctx.stroke()
        elif o == "hoodie":
            ctx.move_to(-0.38 * u, top + lw)
            ctx.curve_to(-0.3 * u, top + 0.28 * u, 0.3 * u, top + 0.28 * u, 0.38 * u, top + lw)
            ctx.set_source_rgb(*line_of(self.shirt))
            ctx.set_line_width(lw)
            ctx.stroke()
            for side in (-1, 1):
                ctx.move_to(side * 0.12 * u, top + 0.2 * u)
                ctx.line_to(side * 0.13 * u, top + 0.5 * u)
            ctx.set_source_rgb(*WHITE)
            ctx.set_line_width(lw)
            ctx.stroke()
            rrect(ctx, -0.32 * u, top + 0.62 * u, 0.64 * u, 0.3 * u, 0.06 * u)
            ctx.set_source_rgb(*line_of(self.shirt))
            ctx.set_line_width(lw * 0.8)
            ctx.stroke()
        elif o == "cardigan":
            block(ctx, -0.2 * u, top + lw, 0.4 * u, h - 2 * lw, 0.04 * u, hexc("#f2eefa"), lw * 0.8, gloss=False)
            for k in range(3):
                ctx.new_sub_path()
                ctx.arc(0.27 * u, top + 0.25 * u + k * 0.25 * u, 0.035 * u, 0, 2 * PI)
                shape_fill(ctx, light(self.shirt, 0.3), lw * 0.5, top, top + 0.9 * u)
        elif o == "suit":
            ctx.move_to(-0.2 * u, top + lw)
            ctx.line_to(0, top + 0.5 * u)
            ctx.line_to(0.2 * u, top + lw)
            ctx.close_path()
            shape_fill(ctx, WHITE, lw * 0.8, top, top + 0.5 * u)
            ctx.move_to(0, top + 0.1 * u)
            ctx.line_to(0.06 * u, top + 0.2 * u)
            ctx.line_to(0, top + 0.5 * u)
            ctx.line_to(-0.06 * u, top + 0.2 * u)
            ctx.close_path()
            shape_fill(ctx, self.accent, lw * 0.6, top, top + 0.5 * u)
        if self.emblem == "bolt":
            cx, cy, k = 0.0, top + 0.55 * u, 0.33 * u
            pts = [(0.15, -1.0), (-0.45, 0.12), (-0.02, 0.12), (-0.2, 1.0), (0.45, -0.18), (0.03, -0.18), (0.25, -1.0)]
            for i, (px, py) in enumerate(pts):
                (ctx.move_to if i == 0 else ctx.line_to)(cx + px * k, cy + py * k)
            ctx.close_path()
            shape_fill(ctx, self.emblem_col, lw * 0.8, cy - k, cy + k, grad=0.08)
        elif self.emblem == "star":
            star_path(ctx, 0, top + 0.5 * u, 0.25 * u)
            shape_fill(ctx, self.emblem_col, lw * 0.8, top + 0.25 * u, top + 0.75 * u)
        elif self.emblem == "heart":
            cx, cy, k = 0, top + 0.5 * u, 0.2 * u
            ctx.move_to(cx, cy + k)
            ctx.curve_to(cx - 1.4 * k, cy - 0.2 * k, cx - 0.6 * k, cy - 1.3 * k, cx, cy - 0.45 * k)
            ctx.curve_to(cx + 0.6 * k, cy - 1.3 * k, cx + 1.4 * k, cy - 0.2 * k, cx, cy + k)
            ctx.close_path()
            shape_fill(ctx, self.emblem_col, lw * 0.8, cy - k, cy + k)

    # ------------------------------------------------------------------ head
    def _head(self, ctx, cx, cy, u, lw, expr, t, talk, look):
        hw, hh = 1.0 * u, 0.9 * u
        x0, y0 = cx - hw / 2, cy - hh / 2
        self._hair_back(ctx, cx, y0, u, lw)
        skin = self.skin
        if expr in ("shock", "scared"):
            skin = mix(skin, PALE, 0.5)
        rrect(ctx, x0, y0, hw, hh, 0.2 * u)
        g = cairo.LinearGradient(0, y0, 0, y0 + hh)
        if expr == "angry":
            g.add_color_stop_rgb(0, *mix(skin, RAGE, 0.55))
            g.add_color_stop_rgb(0.55, *mix(skin, RAGE, 0.2))
            g.add_color_stop_rgb(1, *dark(skin, 0.1))
        else:
            g.add_color_stop_rgb(0, *light(skin, 0.1))
            g.add_color_stop_rgb(0.5, *skin)
            g.add_color_stop_rgb(1, *dark(skin, 0.12))
        ctx.set_source(g)
        ctx.fill_preserve()
        ctx.set_source_rgb(*line_of(self.skin))
        ctx.set_line_width(lw)
        ctx.stroke()
        # glossy streak on the left cheek edge
        ctx.move_to(x0 + lw * 2, y0 + hh * 0.75)
        ctx.line_to(x0 + lw * 2, y0 + hh * 0.5)
        ctx.set_source_rgba(1, 1, 1, 0.3)
        ctx.set_line_width(lw)
        ctx.stroke()
        self._hair_front(ctx, cx, y0, u, lw, hh)
        _face(ctx, cx, y0, u, hh, lw, expr, t, talk, look, self)
        self._accessories(ctx, cx, y0, u, lw, hh, t)
        # reaction FX around the head
        if expr in ("shock", "scared"):
            shake_lines(ctx, cx, y0 + hh * 0.45, hw * 0.72, hh * 0.75, t, lw=max(2, lw * 1.1))
            sweat(ctx, cx + hw * 0.47, y0 + hh * 0.2, 0.13 * u, t)
        elif expr == "angry":
            anger_mark(ctx, cx + hw * 0.42, y0 + hh * 0.05, 0.24 * u, t)
        elif expr in ("worried", "forced"):
            sweat(ctx, cx + hw * 0.47, y0 + hh * 0.25, 0.11 * u, t)
        elif expr == "stars":
            for k, (dx, dy) in enumerate(((-0.62, -0.1), (0.64, 0.05), (0.5, -0.45))):
                sparkle(ctx, cx + dx * hw, y0 + hh * (0.4 + dy), 0.07 * u * (1 + 0.3 * math.sin(t * 9 + k)))

    def _hair_back(self, ctx, cx, y0, u, lw):
        h = self.hair
        hc = self.hair_col
        if h == "long":
            rrect(ctx, cx - 0.62 * u, y0 - 0.2 * u, 1.24 * u, 1.55 * u, 0.3 * u)
            shape_fill(ctx, dark(hc, 0.08), lw, y0, y0 + 1.4 * u)
        elif h in ("bun", "greybun"):
            ctx.new_sub_path()
            ctx.arc(cx, y0 - 0.36 * u, 0.19 * u, 0, 2 * PI)
            shape_fill(ctx, hc, lw, y0 - 0.52 * u, y0 - 0.14 * u)
            ctx.move_to(cx - 0.12 * u, y0 - 0.36 * u)
            ctx.curve_to(cx - 0.04 * u, y0 - 0.44 * u, cx + 0.06 * u, y0 - 0.44 * u, cx + 0.12 * u, y0 - 0.38 * u)
            ctx.set_source_rgba(1, 1, 1, 0.25)
            ctx.set_line_width(lw)
            ctx.stroke()
        elif h == "pony":
            ellipse(ctx, cx + 0.5 * u, y0 + 0.25 * u, 0.16 * u, 0.32 * u)
            shape_fill(ctx, hc, lw, y0, y0 + 0.55 * u)

    def _hair_front(self, ctx, cx, y0, u, lw, hh):
        h, hc = self.hair, self.hair_col
        if h == "cap" or self.cap is not None:
            self._cap(ctx, cx, y0, u, lw)
            return
        if h in (None, "none", "bald"):
            return
        if h == "bowl":
            # helmet-like cap with a jagged fringe; wavy light streaks on top
            fy = y0 + 0.3 * hh
            ctx.move_to(cx - 0.58 * u, y0 + 0.58 * hh)
            ctx.curve_to(cx - 0.64 * u, y0 - 0.56 * u, cx + 0.64 * u, y0 - 0.56 * u, cx + 0.58 * u, y0 + 0.58 * hh)
            ctx.line_to(cx + 0.58 * u, y0 + 0.7 * hh)
            ctx.curve_to(cx + 0.52 * u, y0 + 0.72 * hh, cx + 0.47 * u, y0 + 0.6 * hh, cx + 0.46 * u, fy)
            n = 5
            for i in range(n):
                xa = cx + 0.46 * u - (i + 0.55) * 0.92 * u / n
                xb = cx + 0.46 * u - (i + 1) * 0.92 * u / n
                xm = cx + 0.46 * u - i * 0.92 * u / n
                ctx.curve_to(xm - 0.02 * u, fy + 0.04 * u, xa + 0.03 * u, fy + 0.08 * u, xa, fy + 0.11 * u)
                ctx.curve_to(xa - 0.01 * u, fy + 0.05 * u, xb + 0.03 * u, fy, xb, fy - 0.01 * u)
            ctx.curve_to(cx - 0.47 * u, y0 + 0.6 * hh, cx - 0.52 * u, y0 + 0.72 * hh, cx - 0.58 * u, y0 + 0.7 * hh)
            ctx.close_path()
            shape_fill(ctx, hc, lw, y0 - 0.25 * u, fy)
            for k in range(2):
                yy = y0 - 0.17 * u + k * 0.12 * u
                ctx.move_to(cx - 0.36 * u, yy)
                for i in range(6):
                    ctx.curve_to(cx - 0.36 * u + (i + 0.25) * 0.12 * u, yy - 0.03 * u,
                                 cx - 0.36 * u + (i + 0.75) * 0.12 * u, yy + 0.03 * u,
                                 cx - 0.36 * u + (i + 1) * 0.12 * u, yy)
            ctx.set_source_rgba(*light(hc, 0.28), 0.95)
            ctx.set_line_width(0.045 * u)
            ctx.stroke()
        elif h in ("bun", "greybun", "pony", "long", "smooth"):
            # smooth cap with a centre parting
            ctx.move_to(cx - 0.56 * u, y0 + 0.5 * hh)
            ctx.curve_to(cx - 0.62 * u, y0 - 0.42 * u, cx + 0.62 * u, y0 - 0.42 * u, cx + 0.56 * u, y0 + 0.5 * hh)
            ctx.curve_to(cx + 0.5 * u, y0 + 0.22 * hh, cx + 0.2 * u, y0 + 0.12 * hh, cx, y0 + 0.16 * hh)
            ctx.curve_to(cx - 0.2 * u, y0 + 0.12 * hh, cx - 0.5 * u, y0 + 0.22 * hh, cx - 0.56 * u, y0 + 0.5 * hh)
            ctx.close_path()
            shape_fill(ctx, hc, lw, y0 - 0.2 * u, y0 + 0.4 * hh)
            ctx.move_to(cx - 0.32 * u, y0 - 0.08 * u)
            ctx.curve_to(cx - 0.17 * u, y0 - 0.17 * u, cx + 0.03 * u, y0 - 0.19 * u, cx + 0.15 * u, y0 - 0.17 * u)
            ctx.set_source_rgba(1, 1, 1, 0.22)
            ctx.set_line_width(lw * 1.4)
            ctx.stroke()
            if h in ("bun", "greybun"):
                for side in (-1, 1):   # side curls
                    for k in range(2):
                        ctx.new_sub_path()
                        ctx.arc(cx + side * 0.56 * u, y0 + (0.5 + k * 0.2) * hh, 0.1 * u, 0, 2 * PI)
                        shape_fill(ctx, hc, lw, y0 + 0.4 * hh, y0 + 0.9 * hh)
            if self.curlers is not None:
                for dx, dy, a in ((-0.3, 0.02, -0.5), (0.0, -0.1, 0.0), (0.3, 0.02, 0.5)):
                    ctx.save()
                    ctx.translate(cx + dx * u, y0 + dy * u)
                    ctx.rotate(a)
                    block(ctx, -0.13 * u, -0.06 * u, 0.26 * u, 0.12 * u, 0.05 * u, self.curlers, lw * 0.8, gloss=False)
                    for k in range(3):
                        ctx.move_to((-0.06 + k * 0.06) * u, -0.04 * u)
                        ctx.line_to((-0.06 + k * 0.06) * u, 0.04 * u)
                    ctx.set_source_rgb(*line_of(self.curlers))
                    ctx.set_line_width(lw * 0.6)
                    ctx.stroke()
                    ctx.restore()
        elif h == "afro":
            for i in range(9):
                a = PI + i * PI / 8
                ctx.new_sub_path()
                ctx.arc(cx + math.cos(a) * 0.45 * u, y0 + 0.12 * u + math.sin(a) * 0.3 * u, 0.14 * u, 0, 2 * PI)
            shape_fill(ctx, hc, lw, y0 - 0.3 * u, y0 + 0.2 * u)
        elif h == "spiky":
            ctx.move_to(cx - 0.55 * u, y0 + 0.4 * hh)
            for i in range(7):
                xa = cx - 0.55 * u + (i + 0.5) * 1.1 * u / 7
                xb = cx - 0.55 * u + (i + 1) * 1.1 * u / 7
                ctx.line_to(xa, y0 - 0.25 * u - (0.06 * u if i % 2 else 0))
                ctx.line_to(xb, y0 + 0.02 * u)
            ctx.line_to(cx + 0.55 * u, y0 + 0.4 * hh)
            ctx.line_to(cx + 0.45 * u, y0 + 0.2 * hh)
            ctx.line_to(cx - 0.45 * u, y0 + 0.2 * hh)
            ctx.close_path()
            shape_fill(ctx, hc, lw, y0 - 0.3 * u, y0 + 0.2 * u)

    def _cap(self, ctx, cx, y0, u, lw):
        c = self.cap if self.cap is not None else self.hair_col
        ctx.move_to(cx - 0.55 * u, y0 + 0.22 * u)
        ctx.curve_to(cx - 0.58 * u, y0 - 0.32 * u, cx + 0.58 * u, y0 - 0.32 * u, cx + 0.55 * u, y0 + 0.22 * u)
        ctx.close_path()
        shape_fill(ctx, c, lw, y0 - 0.3 * u, y0 + 0.2 * u)
        rrect(ctx, cx - 0.6 * u, y0 + 0.13 * u, 1.2 * u, 0.12 * u, 0.06 * u)
        shape_fill(ctx, dark(c, 0.12), lw, y0 + 0.13 * u, y0 + 0.25 * u)
        if self.cap_text:
            ctx.save()
            ctx.select_font_face(FONT, cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
            ctx.set_font_size(0.17 * u)
            ex = ctx.text_extents(self.cap_text)
            ctx.move_to(cx - ex.width / 2 - ex.x_bearing, y0 - 0.0 * u)
            ctx.set_source_rgb(1, 1, 1)
            ctx.show_text(self.cap_text)
            ctx.restore()

    def _accessories(self, ctx, cx, y0, u, lw, hh, t):
        if self.headband is not None:
            rrect(ctx, cx - 0.56 * u, y0 + 0.02 * u, 1.12 * u, 0.12 * u, 0.05 * u)
            shape_fill(ctx, self.headband, lw, y0, y0 + 0.14 * u)
            ctx.move_to(cx - 0.5 * u, y0 + 0.08 * u)
            ctx.line_to(cx + 0.5 * u, y0 + 0.08 * u)
            ctx.set_source_rgb(1, 1, 1)
            ctx.set_line_width(0.025 * u)
            ctx.stroke()
        if self.glasses:
            for side in (-1, 1):
                ctx.new_sub_path()
                ctx.arc(cx + side * 0.22 * u, y0 + 0.52 * hh, 0.13 * u, 0, 2 * PI)
            ctx.set_source_rgba(1, 1, 1, 0.25)
            ctx.fill_preserve()
            ctx.set_source_rgb(*INK)
            ctx.set_line_width(lw * 1.1)
            ctx.stroke()
            ctx.move_to(cx - 0.09 * u, y0 + 0.5 * hh)
            ctx.line_to(cx + 0.09 * u, y0 + 0.5 * hh)
            ctx.stroke()
        if self.shades:
            for side in (-1, 1):
                rrect(ctx, cx + side * 0.22 * u - 0.15 * u, y0 + 0.43 * hh, 0.3 * u, 0.17 * u, 0.05 * u)
            ctx.set_source_rgb(*hexc("#141420"))
            ctx.fill()
            ctx.rectangle(cx - 0.1 * u, y0 + 0.45 * hh, 0.2 * u, 0.035 * u)
            ctx.fill()
            for side in (-1, 1):
                ctx.move_to(cx + side * 0.22 * u - 0.08 * u, y0 + 0.47 * hh)
                ctx.line_to(cx + side * 0.22 * u - 0.02 * u, y0 + 0.47 * hh)
            ctx.set_source_rgba(1, 1, 1, 0.7)
            ctx.set_line_width(lw)
            ctx.stroke()
        if self.headset:
            band = self.headset
            ctx.new_sub_path()
            ctx.arc(cx, y0 + 0.35 * hh, 0.66 * u, PI * 1.02, PI * 1.98)
            if band == "rgb":
                g = cairo.LinearGradient(cx - 0.6 * u, 0, cx + 0.6 * u, 0)
                for k, c in enumerate(("#ff4f5a", "#ffd84a", "#4fd16a", "#4f8bff", "#ff4f5a")):
                    g.add_color_stop_rgb(k / 4, *hexc(c))
                ctx.set_source_rgb(*INK)
                ctx.set_line_width(0.14 * u)
                ctx.stroke_preserve()
                ctx.set_source(g)
                ctx.set_line_width(0.07 * u)
                ctx.stroke()
                cup = hexc("#39e29a")
            else:
                ctx.set_source_rgb(*INK)
                ctx.set_line_width(0.12 * u)
                ctx.stroke()
                cup = col(band)
            for side in (-1, 1):
                block(ctx, cx + side * 0.6 * u - 0.1 * u, y0 + 0.32 * hh, 0.2 * u, 0.36 * u, 0.09 * u, cup, lw)
            ctx.move_to(cx - 0.58 * u, y0 + 0.62 * hh + 0.15 * u)
            ctx.curve_to(cx - 0.55 * u, y0 + 0.95 * hh, cx - 0.3 * u, y0 + 0.92 * hh, cx - 0.16 * u, y0 + 0.88 * hh)
            ctx.set_source_rgb(*INK)
            ctx.set_line_width(0.035 * u)
            ctx.stroke()
            ctx.new_sub_path()
            ctx.arc(cx - 0.15 * u, y0 + 0.88 * hh, 0.04 * u, 0, 2 * PI)
            shape_fill(ctx, cup, lw * 0.7, y0 + 0.8 * hh, y0 + 0.95 * hh)
        if self.crown:
            cw, ch = 0.75 * u, 0.32 * u
            by = y0 - 0.08 * u
            ctx.move_to(cx - cw / 2, by)
            for i, (px, py) in enumerate(((-0.5, -1.0), (-0.25, -0.45), (0, -1.15), (0.25, -0.45), (0.5, -1.0))):
                ctx.line_to(cx + px * cw, by + py * ch)
            ctx.line_to(cx + cw / 2, by)
            ctx.close_path()
            shape_fill(ctx, hexc("#ffcc33"), lw, by - ch, by)
            for px, c in ((-0.25, "#4fd16a"), (0, "#e8323a"), (0.25, "#4f8bff")):
                ctx.new_sub_path()
                ctx.arc(cx + px * cw, by - 0.12 * ch * 2, 0.045 * u, 0, 2 * PI)
                shape_fill(ctx, hexc(c), lw * 0.5, by - 0.3 * ch, by)


# ---------------------------------------------------------------- face
def _face(ctx, cx, y0, u, hh, lw, expr, t, talk, look, ch):
    ey = y0 + 0.53 * hh
    my = y0 + 0.78 * hh
    by = y0 + 0.36 * hh
    lx = look * 0.05 * u
    sw = max(2.0, 0.032 * u)
    S = 1.3   # feature scale (measured: reference eyes ~0.09 x 0.13 hw)

    def stroke(c=EYE, w=sw):
        ctx.set_source_rgb(*c)
        ctx.set_line_width(w)
        ctx.set_line_cap(cairo.LINE_CAP_ROUND)
        ctx.stroke()

    # ---- blush
    if expr in HAPPY or ch.lashes or expr in ("smirk", "smug"):
        for side in (-1, 1):
            ellipse(ctx, cx + side * 0.33 * u, ey + 0.11 * u, 0.075 * u, 0.035 * u)
            ctx.set_source_rgba(*BLUSH, 0.45 if expr in HAPPY else 0.28)
            ctx.fill()

    # ---- brows
    def brow(side, lift=0.0, tilt=0.0, arch=False):
        bx = cx + side * 0.21 * u
        y = by - lift * u
        x1, x2 = bx - 0.12 * u, bx + 0.12 * u
        # tilt > 0 lowers the inner end (angry V)
        inner_dy, outer_dy = tilt * u, -tilt * u * 0.3
        y1 = y + (inner_dy if side > 0 else outer_dy)
        y2 = y + (outer_dy if side > 0 else inner_dy)
        ctx.move_to(x1, y1)
        if arch:
            ctx.curve_to(x1 + 0.05 * u, y1 - 0.045 * u, x2 - 0.05 * u, y2 - 0.045 * u, x2, y2)
        else:
            ctx.line_to(x2, y2)
        stroke(ch.brow, 0.062 * u)

    if expr == "angry" or expr == "determined":
        for s_ in (-1, 1):
            brow(s_, 0.0, 0.07)
    elif expr in ("sad", "worried", "cry", "scared", "forced"):
        for s_ in (-1, 1):
            brow(s_, 0.02, -0.05)
    elif expr in ("shock", "crazy"):
        for s_ in (-1, 1):
            brow(s_, 0.07, 0.0, arch=True)
    elif expr in ("smirk", "smug"):
        brow(-1, 0.05, 0.0, arch=True)
        brow(1, 0.0, 0.04)
    elif expr in ("cold", "tired", "sleepy"):
        for s_ in (-1, 1):
            brow(s_, -0.02, 0.0)
    elif expr in HAPPY:
        for s_ in (-1, 1):
            brow(s_, 0.04, 0.0, arch=True)
    else:
        for s_ in (-1, 1):
            brow(s_, 0.01, 0.0, arch=True)

    # ---- eyes
    def oval(x, y, rx, ry, c=EYE):
        ellipse(ctx, x, y, rx, ry)
        ctx.set_source_rgb(*c)
        ctx.fill()

    def hi(x, y, rr):
        ctx.new_sub_path()
        ctx.arc(x, y, rr, 0, 2 * PI)
        ctx.set_source_rgb(1, 1, 1)
        ctx.fill()

    def lashes(x, side):
        if not ch.lashes:
            return
        for k in range(3):
            a = -0.9 - k * 0.35
            ox = x + side * 0.06 * u
            ctx.move_to(ox, ey - 0.05 * u + k * 0.012 * u)
            ctx.line_to(ox + side * math.cos(a) * -0.06 * u, ey - 0.05 * u + math.sin(a) * 0.06 * u)
        stroke(EYE, 0.018 * u)

    for side in (-1, 1):
        ex = cx + side * 0.2 * u + lx
        if expr in ("happy", "laugh") or (expr == "wink" and side < 0):
            ctx.move_to(ex - 0.07 * u, ey + 0.02 * u)
            ctx.curve_to(ex - 0.04 * u, ey - 0.06 * u, ex + 0.04 * u, ey - 0.06 * u, ex + 0.07 * u, ey + 0.02 * u)
            stroke(EYE, 0.035 * u)
        elif expr in ("shock", "scared", "crazy"):
            rr = 0.15 * u if expr == "crazy" else 0.14 * u
            ctx.new_sub_path()
            ctx.arc(ex - lx, ey, rr, 0, 2 * PI)
            ctx.set_source_rgb(1, 1, 1)
            ctx.fill_preserve()
            stroke(EYE, 0.02 * u)
            if expr == "crazy":
                for k in range(4):
                    a = k * PI / 2 + 0.6
                    ctx.move_to(ex - lx + math.cos(a) * rr * 0.92, ey + math.sin(a) * rr * 0.92)
                    ctx.line_to(ex - lx + math.cos(a) * rr * 0.55, ey + math.sin(a) * rr * 0.55)
                stroke(hexc("#e8323a"), 0.012 * u)
                oval(ex - lx * 0.3, ey, 0.04 * u, 0.04 * u, hexc("#e8323a"))
            pj = math.sin(t * 37 + side) * 0.006 * u
            oval(ex + lx * 0.4 + pj, ey + pj, 0.032 * u, 0.032 * u)
        elif expr == "stars":
            star_path(ctx, ex, ey, 0.12 * u, inner=0.48, rot=-PI / 2 + math.sin(t * 6) * 0.15)
            shape_fill(ctx, hexc("#ffd84a"), 0.02 * u, ey - 0.1 * u, ey + 0.1 * u)
        elif expr in ("sleepy",):
            ctx.move_to(ex - 0.07 * u, ey)
            ctx.curve_to(ex - 0.03 * u, ey + 0.035 * u, ex + 0.03 * u, ey + 0.035 * u, ex + 0.07 * u, ey)
            stroke(EYE, 0.03 * u)
        else:
            rx, ry = 0.055 * S * u, 0.075 * S * u
            if expr in ("sad", "worried"):
                ry *= 0.85
            if expr == "angry":
                oval(ex, ey, rx * 1.35, ry * 1.2, hexc("#e8323a"))
                oval(ex, ey, rx * 0.8, ry * 0.75)
                hi(ex + 0.015 * u, ey - 0.03 * u, 0.02 * u)
            elif expr in HALF_LID:
                ctx.save()
                lid = ey - 0.005 * u
                ctx.rectangle(ex - rx * 2, lid, rx * 4, ry * 2)
                ctx.clip()
                if expr == "smug":
                    oval(ex, ey, rx, ry, hexc("#3fa9f5"))
                    oval(ex + side * 0.0, ey + 0.01 * u, rx * 0.6, ry * 0.6)
                else:
                    oval(ex, ey, rx, ry)
                hi(ex + 0.018 * u, ey + 0.012 * u, 0.017 * u)
                ctx.restore()
                ctx.move_to(ex - rx * 1.5, lid - (0.01 * u if side < 0 else 0))
                ctx.line_to(ex + rx * 1.5, lid - (0.01 * u if side > 0 else 0))
                stroke(EYE, 0.032 * u)
            else:
                oval(ex, ey, rx, ry)
                hi(ex + 0.025 * u, ey - 0.04 * u, 0.028 * u)
                hi(ex - 0.022 * u, ey + 0.045 * u, 0.011 * u)
            if expr == "cry":
                ctx.move_to(ex - 0.05 * u, ey + 0.06 * u)
                ctx.line_to(ex - 0.05 * u, my + 0.03 * u)
                ctx.line_to(ex + 0.05 * u, my + 0.03 * u)
                ctx.line_to(ex + 0.05 * u, ey + 0.06 * u)
                ctx.close_path()
                ctx.set_source_rgba(*TEAR, 0.88)
                ctx.fill()
                fl = (t * 3) % 1
                oval(ex, ey + 0.08 * u + fl * (my - ey), 0.03 * u, 0.02 * u, light(TEAR, 0.5))
        lashes(ex, side)

    # ---- mouth
    mouth = expr
    if talk and engine.LIPSYNC:
        lvl = engine.voice_level()
        if lvl > 0.15 and expr not in ("laugh", "shock", "scream"):
            mouth = "open"

    def dmouth(w, d, teeth=False, tongue=True, bottom_teeth=False, x=cx):
        ctx.move_to(x - w, my - 0.02 * u)
        ctx.line_to(x + w, my - 0.02 * u)
        ctx.curve_to(x + w, my + d * 0.8, x + w * 0.5, my + d, x, my + d)
        ctx.curve_to(x - w * 0.5, my + d, x - w, my + d * 0.8, x - w, my - 0.02 * u)
        ctx.close_path()
        ctx.set_source_rgb(*MOUTH)
        ctx.fill_preserve()
        ctx.save()
        ctx.clip_preserve()
        if tongue:
            ellipse(ctx, x, my + d * 0.95, w * 0.6, d * 0.42)
            ctx.set_source_rgb(*TONGUE)
            ctx.fill()
        if teeth:
            ctx.rectangle(x - w, my - 0.03 * u, 2 * w, d * 0.28)
            ctx.set_source_rgb(*TEETH)
            ctx.fill()
        if bottom_teeth:
            ctx.rectangle(x - w, my + d * 0.78, 2 * w, d * 0.3)
            ctx.set_source_rgb(*TEETH)
            ctx.fill()
        ctx.restore()
        ctx.new_path()
        ctx.move_to(x - w, my - 0.02 * u)
        ctx.line_to(x + w, my - 0.02 * u)
        ctx.curve_to(x + w, my + d * 0.8, x + w * 0.5, my + d, x, my + d)
        ctx.curve_to(x - w * 0.5, my + d, x - w, my + d * 0.8, x - w, my - 0.02 * u)
        ctx.close_path()
        stroke(EYE, 0.022 * u)

    if mouth in ("happy", "stars", "wink"):
        dmouth(0.15 * u, 0.13 * u)
    elif mouth == "laugh":
        dmouth(0.18 * u, 0.19 * u + math.sin(t * 22) * 0.01 * u)
    elif mouth == "grin":
        dmouth(0.2 * u, 0.13 * u, teeth=True, tongue=False, bottom_teeth=True)
    elif mouth == "crazy":
        dmouth(0.25 * u, 0.19 * u, teeth=True, tongue=True)
    elif mouth == "forced":
        dmouth(0.17 * u, 0.08 * u, teeth=True, tongue=False, bottom_teeth=True)
    elif mouth in ("shock",):
        ellipse(ctx, cx, my + 0.03 * u, 0.07 * u, 0.095 * u)
        ctx.set_source_rgb(*MOUTH)
        ctx.fill_preserve()
        stroke(EYE, 0.02 * u)
        ellipse(ctx, cx, my + 0.085 * u, 0.045 * u, 0.026 * u)
        ctx.set_source_rgb(*TONGUE)
        ctx.fill()
    elif mouth in ("open", "talk"):
        dmouth(0.1 * u, 0.1 * u)
    elif mouth == "scared":
        ctx.move_to(cx - 0.13 * u, my)
        for i in range(1, 7):
            ctx.line_to(cx - 0.13 * u + i * 0.26 * u / 6, my + (-0.025 if i % 2 else 0.025) * u)
        stroke(EYE, 0.025 * u)
    elif mouth == "angry":
        ctx.move_to(cx - 0.18 * u, my - 0.04 * u)
        ctx.line_to(cx + 0.18 * u, my - 0.04 * u)
        ctx.line_to(cx + 0.13 * u, my + 0.12 * u)
        ctx.line_to(cx - 0.13 * u, my + 0.12 * u)
        ctx.close_path()
        ctx.set_source_rgb(*MOUTH)
        ctx.fill_preserve()
        ctx.save()
        ctx.clip_preserve()
        ctx.rectangle(cx - 0.2 * u, my - 0.05 * u, 0.4 * u, 0.045 * u)
        ctx.set_source_rgb(*TEETH)
        ctx.fill()
        ellipse(ctx, cx, my + 0.13 * u, 0.09 * u, 0.04 * u)
        ctx.set_source_rgb(*TONGUE)
        ctx.fill()
        ctx.restore()
        ctx.new_path()
        ctx.move_to(cx - 0.18 * u, my - 0.04 * u)
        ctx.line_to(cx + 0.18 * u, my - 0.04 * u)
        ctx.line_to(cx + 0.13 * u, my + 0.12 * u)
        ctx.line_to(cx - 0.13 * u, my + 0.12 * u)
        ctx.close_path()
        stroke(EYE, 0.022 * u)
    elif mouth == "cry":
        ctx.move_to(cx - 0.12 * u, my + 0.07 * u)
        ctx.curve_to(cx - 0.1 * u, my - 0.05 * u, cx + 0.1 * u, my - 0.05 * u, cx + 0.12 * u, my + 0.07 * u)
        ctx.close_path()
        ctx.set_source_rgb(*MOUTH)
        ctx.fill_preserve()
        stroke(EYE, 0.022 * u)
    elif mouth in ("sad", "worried"):
        ctx.move_to(cx - 0.08 * u, my + 0.03 * u)
        ctx.curve_to(cx - 0.04 * u, my - 0.02 * u, cx + 0.04 * u, my - 0.02 * u, cx + 0.08 * u, my + 0.03 * u)
        stroke()
    elif mouth in ("cold", "determined", "tired"):
        ctx.move_to(cx - 0.07 * u, my + 0.01 * u)
        ctx.line_to(cx + 0.07 * u, my + 0.01 * u)
        stroke()
    elif mouth == "smirk":
        ctx.move_to(cx - 0.1 * u, my + 0.02 * u)
        ctx.curve_to(cx - 0.02 * u, my + 0.05 * u, cx + 0.08 * u, my + 0.03 * u, cx + 0.13 * u, my - 0.03 * u)
        stroke()
    elif mouth == "smug":
        ctx.move_to(cx - 0.12 * u, my - 0.01 * u)
        ctx.curve_to(cx - 0.04 * u, my + 0.05 * u, cx + 0.06 * u, my + 0.05 * u, cx + 0.13 * u, my - 0.02 * u)
        stroke()
        tx = cx + 0.05 * u
        ctx.move_to(tx - 0.04 * u, my + 0.035 * u)
        ctx.curve_to(tx - 0.04 * u, my + 0.11 * u, tx + 0.045 * u, my + 0.11 * u, tx + 0.045 * u, my + 0.03 * u)
        ctx.close_path()
        ctx.set_source_rgb(*TONGUE)
        ctx.fill_preserve()
        stroke(EYE, 0.018 * u)
    elif mouth == "sleepy":
        ellipse(ctx, cx, my + 0.02 * u, 0.025 * u, 0.03 * u)
        ctx.set_source_rgb(*MOUTH)
        ctx.fill()
    else:   # neutral
        ctx.move_to(cx - 0.08 * u, my)
        ctx.curve_to(cx - 0.03 * u, my + 0.04 * u, cx + 0.03 * u, my + 0.04 * u, cx + 0.08 * u, my)
        stroke()


# ---------------------------------------------------------------- over-the-shoulder figure
def back_figure(ctx, x, y, s, hair_col="#8d5e3b", shirt="#e8573a", hair="bowl"):
    """A character seen from behind (foreground of an over-the-shoulder shot).
    (x, y) = bottom centre of the shoulders."""
    r = 64 * s
    u = Block.HW * r
    lw = max(2.0, 0.026 * u)
    sc = col(shirt)
    block(ctx, x - 1.1 * u, y - 0.75 * u, 2.2 * u, 0.9 * u, 0.12 * u, sc, lw)
    hc = col(hair_col)
    hy = y - 0.75 * u - 0.8 * u
    rrect(ctx, x - 0.52 * u, hy, 1.04 * u, 0.92 * u, 0.25 * u)
    shape_fill(ctx, hc, lw, hy, hy + 0.9 * u)
    if hair == "bowl":
        for k in range(3):
            yy = hy + 0.15 * u + k * 0.13 * u
            ctx.move_to(x - 0.36 * u, yy)
            for i in range(6):
                ctx.curve_to(x - 0.36 * u + (i + 0.25) * 0.12 * u, yy - 0.03 * u,
                             x - 0.36 * u + (i + 0.75) * 0.12 * u, yy + 0.03 * u,
                             x - 0.36 * u + (i + 1) * 0.12 * u, yy)
        ctx.set_source_rgba(*light(hc, 0.3), 0.9)
        ctx.set_line_width(lw * 1.2)
        ctx.stroke()


# ---------------------------------------------------------------- our own cast (style only, not the reference's people)
EXPRESSIONS = ["neutral", "happy", "grin", "laugh", "smirk", "smug", "cold", "shock", "scared", "angry", "cry",
               "sad", "worried", "crazy", "wink", "stars", "sleepy", "determined", "forced"]
ARMS = ["down", "up", "point", "show", "hip", "hold", "cross", "wave", "shrug", "punch", "cover", "phone"]
POSES = ["stand", "walk", "run", "jump", "sit", "feetup"]

KID = Block("#2fbf8f", pants="#2b3f8f", skin="#e6ddd6", hair="bowl", hair_col="#4a2f22", emblem="star",
            emblem_col="#ffd84a", shoes="white")
KID_GAME = Block("#2fbf8f", pants="#2b3f8f", skin="#e6ddd6", hair="bowl", hair_col="#4a2f22", emblem="star",
                 emblem_col="#ffd84a", shoes="white", headband="#ff5f5f")
MOM = Block("#ff7a8a", pants="#5a4fb0", skin="#c89f82", hair="pony", hair_col="#a0442a", outfit="cardigan",
            lashes=True, shoes="dark")
MOM_ROBE = Block("#7fb8ff", pants="#7fb8ff", skin="#c89f82", hair="bun", hair_col="#a0442a", outfit="robe",
                 lashes=True, curlers="#ffd84a", shoes="slippers")
DAD = Block("#4f8bff", pants="#3b3550", skin="#d9a77f", hair="smooth", hair_col="#3a2a2a", outfit="suit",
            accent="#e8323a", shoes="dark")
GRANDMA = Block("#b48cff", pants="#5a4fb0", skin="#e8c3a8", hair="greybun", hair_col="#d8d8e4", outfit="cardigan",
                lashes=True, glasses=True, shoes="dark")
NOOB = Block("#1a68cf", pants="#9bbc36", skin="#e9c22c", hair=None, sleeves="skin", shoes=None)
BOSS = Block("#1a68cf", pants="#9bbc36", skin="#e9c22c", hair=None, sleeves="skin", shoes=None, crown=True)


def crowd_member(i):
    """A varied bystander for crowd shots (deterministic by index)."""
    shirts = ["#ff5fa2", "#9d5cff", "#ffd84a", "#4f8bff", "#ff8a3d", "#2fbf8f", "#e8323a"]
    skins = ["#e6ddd6", "#c89f82", "#7a4a2e", "#e9c22c", "#f0c9a8"]
    hairs = [("bowl", "#4a2f22"), ("long", "#f2c14e"), ("cap", "#e8323a"), ("afro", "#2a1a14"), (None, "#000000"),
             ("long", "#5a3020"), ("spiky", "#f2c14e")]
    h, hc = hairs[i % len(hairs)]
    return Block(shirts[i % len(shirts)], pants=["#2b45a6", "#3b3550", "#9bbc36"][i % 3], skin=skins[(i * 3) % 5],
                 hair=h, hair_col=hc, cap=hc if h == "cap" else None, outfit=["shirt", "hoodie", "tshirt"][i % 3],
                 lashes=h == "long", shoes="white" if i % 2 else "dark")

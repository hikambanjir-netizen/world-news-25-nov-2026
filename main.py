#!/usr/bin/env python3
"""The World Today - Wednesday 25 November 2026.

A one-page newspaper front page summing up the day's world news,
drawn from scratch with the Python standard library only: a hand-made
5x7 bitmap font, a small raster canvas with simple pictograms, and a
from-scratch PNG encoder built on zlib.

No network, no clock reads, no unseeded randomness: two runs write
byte-identical output.

Writes $MAKEFUN_OUTPUT_DIR/entry.png (default /output/entry.png).
Image: 1024x1024 PNG, well under the 1 MiB cap.

Stories (all reported on 25 November 2026):
  1. Houthis hit Riyadh's tallest tower, the PIF Tower, a second
     time in five days; 11 people wounded.
  2. Ukraine confirms a drone strike on a Russian cargo ship in the
     Gulf of Finland; Putin warns retaliation is inevitable.
  3. A US jury convicts Huawei on 10 of 12 counts, including bank
     fraud, sanctions violations and stealing trade secrets.
  4. NATO sends early-warning aircraft to Poland and vows to defend
     space, amid reports of a Russian nuclear-armed satellite.
  5. On the eve of Thanksgiving, Trump pardons turkeys Freedom and
     Feathers at the White House.
"""

import math
import os
import struct
import zlib

W, H = 1024, 1024
PAPER = (247, 242, 228)
INK = (24, 20, 15)
RED = (166, 30, 34)
BLUE = (28, 56, 94)
TEAL = (18, 92, 86)
GREY = (110, 104, 90)
LIGHT = (233, 227, 209)
GOLD = (176, 128, 32)
SKY = (178, 205, 224)


# ------------------------------------------------------------------ font
# 5x7 bitmap glyphs, '#' = ink. All page text is upper-case.
FONT = {
    "A": (" ### ", "#   #", "#   #", "#####", "#   #", "#   #", "#   #"),
    "B": ("#### ", "#   #", "#   #", "#### ", "#   #", "#   #", "#### "),
    "C": (" ####", "#    ", "#    ", "#    ", "#    ", "#    ", " ####"),
    "D": ("#### ", "#   #", "#   #", "#   #", "#   #", "#   #", "#### "),
    "E": ("#####", "#    ", "#    ", "#### ", "#    ", "#    ", "#####"),
    "F": ("#####", "#    ", "#    ", "#### ", "#    ", "#    ", "#    "),
    "G": (" ####", "#    ", "#    ", "# ###", "#   #", "#   #", " ### "),
    "H": ("#   #", "#   #", "#   #", "#####", "#   #", "#   #", "#   #"),
    "I": ("#####", "  #  ", "  #  ", "  #  ", "  #  ", "  #  ", "#####"),
    "J": ("  ###", "   # ", "   # ", "   # ", "   # ", "#  # ", " ##  "),
    "K": ("#   #", "#  # ", "# #  ", "##   ", "# #  ", "#  # ", "#   #"),
    "L": ("#    ", "#    ", "#    ", "#    ", "#    ", "#    ", "#####"),
    "M": ("#   #", "## ##", "# # #", "# # #", "#   #", "#   #", "#   #"),
    "N": ("#   #", "##  #", "##  #", "# # #", "#  ##", "#  ##", "#   #"),
    "O": (" ### ", "#   #", "#   #", "#   #", "#   #", "#   #", " ### "),
    "P": ("#### ", "#   #", "#   #", "#### ", "#    ", "#    ", "#    "),
    "Q": (" ### ", "#   #", "#   #", "#   #", "# # #", "#  # ", " ## #"),
    "R": ("#### ", "#   #", "#   #", "#### ", "# #  ", "#  # ", "#   #"),
    "S": (" ####", "#    ", "#    ", " ### ", "    #", "    #", "#### "),
    "T": ("#####", "  #  ", "  #  ", "  #  ", "  #  ", "  #  ", "  #  "),
    "U": ("#   #", "#   #", "#   #", "#   #", "#   #", "#   #", " ### "),
    "V": ("#   #", "#   #", "#   #", "#   #", "#   #", " # # ", "  #  "),
    "W": ("#   #", "#   #", "#   #", "# # #", "# # #", "## ##", "#   #"),
    "X": ("#   #", "#   #", " # # ", "  #  ", " # # ", "#   #", "#   #"),
    "Y": ("#   #", "#   #", " # # ", "  #  ", "  #  ", "  #  ", "  #  "),
    "Z": ("#####", "    #", "   # ", "  #  ", " #   ", "#    ", "#####"),
    "0": (" ### ", "#  ##", "# # #", "##  #", "#   #", "#   #", " ### "),
    "1": ("  #  ", " ##  ", "  #  ", "  #  ", "  #  ", "  #  ", " ### "),
    "2": (" ### ", "#   #", "    #", "   # ", "  #  ", " #   ", "#####"),
    "3": ("#### ", "    #", "    #", " ### ", "    #", "    #", "#### "),
    "4": ("   # ", "  ## ", " # # ", "#  # ", "#####", "   # ", "   # "),
    "5": ("#####", "#    ", "#### ", "    #", "    #", "#   #", " ### "),
    "6": (" ### ", "#    ", "#    ", "#### ", "#   #", "#   #", " ### "),
    "7": ("#####", "    #", "   # ", "   # ", "  #  ", "  #  ", "  #  "),
    "8": (" ### ", "#   #", "#   #", " ### ", "#   #", "#   #", " ### "),
    "9": (" ### ", "#   #", "#   #", " ####", "    #", "    #", " ### "),
    " ": ("     ", "     ", "     ", "     ", "     ", "     ", "     "),
    ".": ("     ", "     ", "     ", "     ", "     ", " ##  ", " ##  "),
    ",": ("     ", "     ", "     ", "     ", " ##  ", " ##  ", " #   "),
    ":": ("     ", " ##  ", " ##  ", "     ", " ##  ", " ##  ", "     "),
    ";": ("     ", " ##  ", " ##  ", "     ", " ##  ", " ##  ", " #   "),
    "'": ("  #  ", "  #  ", "  #  ", "     ", "     ", "     ", "     "),
    "-": ("     ", "     ", "     ", "#####", "     ", "     ", "     "),
    "!": ("  #  ", "  #  ", "  #  ", "  #  ", "  #  ", "     ", "  #  "),
    "?": (" ### ", "#   #", "    #", "   # ", "  #  ", "     ", "  #  "),
    "(": ("   # ", "  #  ", " #   ", " #   ", " #   ", "  #  ", "   # "),
    ")": (" #   ", "  #  ", "   # ", "   # ", "   # ", "  #  ", " #   "),
    "/": ("    #", "    #", "   # ", "  #  ", " #   ", "#    ", "#    "),
    "&": (" ### ", "#   #", "#   #", " #   ", "# # #", "#  # ", " ## #"),
    "%": ("#  ##", "# # #", "   # ", "  #  ", " #   ", "# # #", "##  #"),
    "+": ("     ", "  #  ", "  #  ", "#####", "  #  ", "  #  ", "     "),
    "=": ("     ", "     ", "#####", "     ", "#####", "     ", "     "),
    '"': (" # # ", " # # ", " # # ", "     ", "     ", "     ", "     "),
    "*": ("     ", " # # ", "  #  ", "#####", "  #  ", " # # ", "     "),
}


def glyph(ch):
    """Bitmap for one character; fancy punctuation folds to plain ASCII."""
    if ch in ("\u2014", "\u2013"):
        return FONT["-"]
    if ch in ("\u2019", "\u2018"):
        return FONT["'"]
    if ch == "\u201c" or ch == "\u201d":
        return FONT['"']
    if ch == "\u00b7":
        return ("     ", "     ", " ### ", " ### ", "     ", "     ",
                "     ")
    return FONT.get(ch.upper(), FONT[" "])


# ------------------------------------------------------------------ canvas
class Canvas:
    """A flat RGB canvas with rectangle, disc, triangle and text drawing."""

    def __init__(self, w, h, bg):
        self.w, self.h = w, h
        self.px = bytearray([bg[0]] * (w * h * 3))
        self.px[1::3] = bytearray([bg[1]] * (w * h))
        self.px[2::3] = bytearray([bg[2]] * (w * h))

    def fill(self, x, y, w, h, c):
        x0, y0 = max(0, x), max(0, y)
        x1, y1 = min(self.w, x + w), min(self.h, y + h)
        for yy in range(y0, y1):
            base = (yy * self.w + x0) * 3
            for xx in range(x0, x1):
                o = base + (xx - x0) * 3
                self.px[o], self.px[o + 1], self.px[o + 2] = c

    def hline(self, x, y, w, c, t=1):
        self.fill(x, y, w, t, c)

    def vline(self, x, y, h, c, t=1):
        self.fill(x, y, t, h, c)

    def box(self, x, y, w, h, c, t=1):
        self.hline(x, y, w, c, t)
        self.hline(x, y + h - t, w, c, t)
        self.vline(x, y, h, c, t)
        self.vline(x + w - t, y, h, c, t)

    def disc(self, cx, cy, r, c):
        """Filled disc by horizontal spans; deterministic, no floats."""
        for dy in range(-r, r + 1):
            half = int(math.sqrt(r * r - dy * dy))
            self.fill(cx - half, cy + dy, 2 * half + 1, 1, c)

    def tri(self, ax, ay, bx, by, cx, cy, c):
        """Filled triangle, scanline by scanline."""
        ys = sorted([(ay, ax), (by, bx), (cy, cx)])
        (y0, x0), (y1, x1), (y2, x2) = ys
        if y0 == y2:
            return
        for y in range(y0, y2 + 1):
            if y < y1:
                t1 = 0 if y1 == y0 else (y - y0) / (y1 - y0)
                xa = x0 + (x1 - x0) * t1
                t2 = (y - y0) / (y2 - y0)
                xb = x0 + (x2 - x0) * t2
            else:
                t1 = 0 if y2 == y1 else (y - y1) / (y2 - y1)
                xa = x1 + (x2 - x1) * t1
                t2 = (y - y0) / (y2 - y0)
                xb = x0 + (x2 - x0) * t2
            lo, hi = int(min(xa, xb)), int(max(xa, xb))
            self.fill(lo, y, hi - lo + 1, 1, c)

    def text(self, x, y, s, scale, c):
        cx = x
        for ch in s:
            g = glyph(ch)
            for row in range(7):
                line = g[row]
                for col in range(5):
                    if line[col] == "#":
                        self.fill(cx + col * scale, y + row * scale,
                                  scale, scale, c)
            cx += 6 * scale
        return cx

    def text_w(self, s, scale):
        return len(s) * 6 * scale - scale

    def centre(self, y, s, scale, c):
        self.text((self.w - self.text_w(s, scale)) // 2, y, s, scale, c)

    def centre_in(self, x, w, y, s, scale, c):
        self.text(x + (w - self.text_w(s, scale)) // 2, y, s, scale, c)

    def wrap(self, s, scale, max_w):
        """Greedy word wrap; returns the lines that fit inside max_w."""
        words, lines, cur = s.split(" "), [], ""
        for wd in words:
            trial = wd if not cur else cur + " " + wd
            if self.text_w(trial, scale) <= max_w:
                cur = trial
            else:
                if cur:
                    lines.append(cur)
                cur = wd
        if cur:
            lines.append(cur)
        return lines

    def para(self, x, y, s, scale, c, max_w, leading=None):
        lh = leading if leading is not None else 10 * scale
        lines = self.wrap(s, scale, max_w)
        for i, line in enumerate(lines):
            self.text(x, y + i * lh, line, scale, c)
        return y + len(lines) * lh


# ------------------------------------------------------------------ png
def _chunk(tag, data):
    out = struct.pack(">I", len(data)) + tag + data
    return out + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)


def encode_png(cv):
    raw = bytearray()
    for yy in range(cv.h):
        raw.append(0)
        raw += cv.px[yy * cv.w * 3:(yy + 1) * cv.w * 3]
    png = b"\x89PNG\r\n\x1a\n"
    png += _chunk(b"IHDR", struct.pack(">IIBBBBB", cv.w, cv.h, 8, 2, 0, 0, 0))
    png += _chunk(b"IDAT", zlib.compress(bytes(raw), 9))
    png += _chunk(b"IEND", b"")
    return png



# ------------------------------------------------------------------ pictures
# Small flat pictograms, one per story, drawn from rectangles, discs
# and triangles so each story is recognisable from its picture alone.

def pic_tower(cv, x, y, w, h):
    """The PIF Tower: a tall slab with lit windows, smoke at its top."""
    cv.fill(x, y + h, w, 6, INK)                    # ground
    bw = w * 3 // 5
    bx = x + (w - bw) // 2
    cv.fill(bx, y + 22, bw, h - 22, BLUE)          # the slab
    cv.tri(bx, y + 22, bx + bw, y + 22, bx + bw // 2, y + 2, BLUE)
    for fy in range(y + 34, y + h - 8, 12):        # floor lines
        cv.hline(bx, fy, bw, LIGHT, 1)
    for wy in range(y + 40, y + h - 12, 24):       # lit windows
        cv.fill(bx + 6, wy, 5, 7, GOLD)
        cv.fill(bx + bw - 11, wy, 5, 7, GOLD)
    cv.disc(bx + bw // 2 - 14, y + 6, 7, GREY)     # smoke puffs
    cv.disc(bx + bw // 2 + 10, y - 2, 9, GREY)
    cv.disc(bx + bw // 2 + 2, y - 10, 6, GREY)
    cv.fill(bx + bw // 2 - 2, y + 22, 4, 10, RED)  # impact flash


def pic_ship(cv, x, y, w, h):
    """A cargo ship on the sea, struck amidships."""
    cv.fill(x, y + h - 18, w, 3, BLUE)             # sea lines
    cv.fill(x + 8, y + h - 10, w - 16, 2, BLUE)
    hx, hy = x + 6, y + h - 46
    cv.tri(hx, hy, hx + w - 12, hy, hx + 8, hy + 22, INK)  # hull
    cv.fill(hx + 8, hy, w - 20, 22, INK)
    cv.fill(hx + w // 2 - 3, hy - 26, 6, 26, INK)  # mast
    cv.fill(hx + w // 2 - 3, hy - 26, 26, 5, INK)  # bridge
    cv.fill(hx + 16, hy - 12, 10, 12, RED)         # containers
    cv.fill(hx + 30, hy - 12, 10, 12, GOLD)
    cv.disc(hx + w // 2, hy - 34, 7, GREY)         # blast smoke
    cv.disc(hx + w // 2 + 12, hy - 42, 5, GREY)
    cv.tri(hx + w // 2 - 10, hy - 46, hx + w // 2 + 10, hy - 46,
           hx + w // 2, hy - 28, RED)              # blast flash


def pic_scales(cv, x, y, w, h):
    """Scales of justice: a courthouse verdict."""
    cx = x + w // 2
    cv.fill(cx - 3, y + 12, 6, h - 24, INK)        # post
    cv.fill(x + 8, y + h - 12, w - 16, 6, INK)     # base
    cv.fill(cx - w // 2 + 6, y + 12, w - 12, 4, INK)  # beam
    for sgn in (-1, 1):
        px = cx + sgn * (w // 2 - 12)
        cv.vline(px, y + 16, 26, INK, 2)
        cv.tri(px - 18, y + 44, px + 18, y + 44, px, y + 62, BLUE)
    cv.disc(cx, y + 8, 6, GOLD)                    # finial


def pic_jet(cv, x, y, w, h):
    """An early-warning jet in flight, radar arcs above it."""
    cx, cy = x + w // 2, y + h // 2 + 6
    cv.tri(cx - 34, cy + 6, cx + 38, cy, cx - 34, cy - 6, INK)
    cv.tri(cx - 8, cy, cx - 26, cy - 22, cx - 2, cy - 2, INK)
    cv.tri(cx - 8, cy, cx - 26, cy + 22, cx - 2, cy + 2, INK)
    cv.tri(cx - 34, cy + 4, cx - 44, cy - 8, cx - 40, cy + 6, INK)
    cv.disc(cx + 34, cy, 5, RED)                   # radar dome
    cv.hline(x + 6, cy + 16, 26, GREY, 2)          # motion lines
    cv.hline(x + 12, cy + 24, 18, GREY, 2)


def pic_turkey(cv, x, y, w, h):
    """A Thanksgiving turkey: fanned tail, round body, small head."""
    cx, cy = x + w // 2, y + h - 30
    for i, ang in enumerate((-60, -30, 0, 30, 60)):
        rad = math.radians(ang)
        fx = cx + int(30 * math.sin(rad))
        fy = cy - 18 - int(30 * math.cos(rad))
        cv.disc(fx, fy, 12, GOLD if i % 2 else RED)
    cv.disc(cx, cy, 24, (122, 74, 30))             # body
    cv.disc(cx + 14, cy - 26, 11, (122, 74, 30))   # head
    cv.tri(cx + 24, cy - 28, cx + 32, cy - 24, cx + 24, cy - 20, GOLD)
    cv.disc(cx + 17, cy - 29, 2, PAPER)            # eye


# ------------------------------------------------------------------ page
def draw_masthead(cv):
    cv.hline(36, 30, W - 72, INK, 2)
    cv.centre(44, "ONE PAGE - THE WORLD'S NEWS", 2, GREY)
    cv.centre(68, "THE WORLD TODAY", 8, INK)
    cv.hline(36, 134, W - 72, INK, 3)
    cv.centre(146, "WEDNESDAY 25 NOVEMBER 2026", 3, INK)
    cv.hline(36, 176, W - 72, INK, 1)


def draw_lead(cv):
    y = 192
    cv.text(36, y, "SAUDI ARABIA - RIYADH", 2, RED)
    cv.text(36, y + 24, "HOUTHIS HIT RIYADH'S", 6, INK)
    cv.text(36, y + 72, "TALLEST TOWER AGAIN", 6, INK)
    deck = ("A Houthi strike hits the PIF Tower, the capital's tallest "
            "building, for the second time in five days. Eleven people "
            "are wounded, and the Saudi-led coalition calls the attack "
            "a terrorist act.")
    cv.para(36, y + 132, deck, 2, INK, 600, leading=18)
    pic_tower(cv, 780, y + 30, 160, 190)
    fy = y + 222
    boxes = [("11 WOUNDED", "INCL. TWO INDIANS"),
             ("SECOND HIT", "IN FIVE DAYS"),
             ("PIF TOWER", "TALLEST IN RIYADH")]
    bw = (W - 72 - 2 * 16) // 3
    for i, (a, b) in enumerate(boxes):
        bx = 36 + i * (bw + 16)
        cv.box(bx, fy, bw, 56, BLUE, 2)
        cv.centre_in(bx, bw, fy + 10, a, 2, BLUE)
        cv.centre_in(bx, bw, fy + 32, b, 2, INK)
    cv.hline(36, fy + 72, W - 72, INK, 2)
    return fy + 72


def draw_story(cv, x, y, w, pic, kicker, headline, body, accent=RED):
    pic(cv, x, y + 6, 96, 84)
    tx = x + 112
    tw = w - 112
    cv.text(tx, y, kicker, 2, accent)
    y2 = cv.para(tx, y + 22, headline, 3, INK, tw, leading=28)
    y2 = cv.para(tx, y2 + 4, body, 2, INK, tw, leading=18)
    return max(y2, y + 96)


def draw_middle(cv, top):
    y = top + 16
    col_w = 452
    lx, rx = 36, 536
    ly = draw_story(cv, lx, y, col_w, pic_ship,
                    "UKRAINE - GULF OF FINLAND",
                    "KYIV CONFIRMS SHIP STRIKE",
                    "Zelenskiy says Ukraine hit a Russian cargo ship "
                    "carrying weapons. Kyiv also sank a Russian warship "
                    "off Libya, and Putin warns retaliation is inevitable.")
    ly = draw_story(cv, lx, ly + 18, col_w, pic_scales,
                    "UNITED STATES - CHINA",
                    "HUAWEI CONVICTED IN US TRIAL",
                    "A jury convicts Huawei on 10 of 12 counts: bank "
                    "fraud, sanctions violations and stealing trade "
                    "secrets over its Iran business.", accent=BLUE)
    ry = draw_story(cv, rx, y, col_w, pic_jet,
                    "NATO - POLAND",
                    "NATO SENDS EARLY-WARNING JETS",
                    "The alliance deploys surveillance aircraft to "
                    "Poland after missiles landed there, and vows to "
                    "defend space amid reports of a Russian nuclear "
                    "satellite.", accent=BLUE)
    ry = draw_story(cv, rx, ry + 18, col_w, pic_turkey,
                    "UNITED STATES - THANKSGIVING",
                    "TRUMP PARDONS TWO TURKEYS",
                    "On the eve of Thanksgiving, the president spares "
                    "Freedom and Feathers at the White House ceremony.",
                    accent=TEAL)
    cv.vline(512, y, max(ly, ry) - y, GREY, 1)
    return max(ly, ry)


def draw_ticker(cv, top):
    y = top + 14
    cv.text(36, y, "ALSO:", 2, RED)
    cv.para(110, y,
            "NEPAL QUAKE 5.6 HITS KOSHI PROVINCE - SOUTH KOREA MINISTER "
            "QUITS OVER EXAM SCANDAL - ANTHROPIC SHARES SLIDE BELOW $83 "
            "- IRAQ ORDERS FEDERAL CONTROL OF KURDISH OILFIELDS - INTL "
            "DAY AGAINST VIOLENCE AGAINST WOMEN",
            2, INK, W - 146, leading=18)
    y += 56
    cv.hline(36, y, W - 72, INK, 3)
    cv.centre(y + 12, "SOURCES: REUTERS - AP - ARAB NEWS - BBC - 25 NOVEMBER 2026",
              2, GREY)


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    cv = Canvas(W, H, PAPER)
    draw_masthead(cv)
    y = draw_lead(cv)
    y = draw_middle(cv, y)
    draw_ticker(cv, y)
    png = encode_png(cv)
    path = os.path.join(out_dir, "entry.png")
    with open(path, "wb") as f:
        f.write(png)
    print("wrote %s (%d bytes)" % (path, len(png)))


if __name__ == "__main__":
    main()

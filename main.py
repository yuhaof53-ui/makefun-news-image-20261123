#!/usr/bin/env python3
"""News-image entry for make.fun: sum up 23 November 2026 in one image.

Draws a newspaper front page for Monday, 23 November 2026 with a pure
standard-library rasterizer: a 15x17 bitmap font rendered in this session
from DejaVu Sans Bold and embedded below, rectangles, circles and lines,
and a hand-written PNG encoder. No network, no files read, no randomness:
two runs write identical bytes.

The page: masthead + date banner, lead story (Nvidia reinstates Jensen
Huang, shares +31%), then five more stories (COP31 collapse, Ukrainian
drones sink a Russian warship off Libya, US sanctions on Iran's banks,
NATO sends an AWACS to Poland, Democrats' record House majority) plus a
ticker of smaller items (Indonesia factory fire, India aid to Nepal,
South Korea minister quits, Houthi refinery claim).

Sources (all reported 23 Nov 2026): Motley Fool / Reuters / Finnhub /
Nvidia 8-K (Huang reinstated 22 Nov, NVDA +31.48% to $165.05);
Just Security Early Edition + BusinessWorld (COP31 ends with no deal);
Daily Mirror + Daily News Egypt (Ukraine strikes Russian ships off
Libya); Daily News Egypt (US Treasury sanctions on Iran banks, NATO
AWACS to Poland); Al Jazeera / AP / CNN (Democrats 258 House seats,
largest since 1992); Reuters / CNA / Al Jazeera (Indonesia fire, 24
dead, confirmed Monday).
"""

import base64
import math
import os
import struct
import zlib

W, H = 1024, 1024

# ---------------------------------------------------------------- font data
# Bitmap font rendered in this session from DejaVu Sans Bold: 89 glyphs,
# each a 15x17 cell, 1 bit per pixel, bit-packed and base64-encoded.
CHARSET = (
    "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    "abcdefghijklmnopqrstuvwxyz"
    "0123456789"
    " .,;:!?%()+-/&=$#@*_'\"="
    "\u2022\u2014\u2019\u2013"
)
CELL_W, CELL_H = 15, 17
FONT_B64 = (
    "AAAAAB4APgD8AfgDuA5wHOA44P/B/8ODjgcAAAAAAAAAAAAB/gP+B54PPB5wP+B/wPHB44PHB/4P"
    "+AAAAAAAAAAAAAB+Af4HjB4AOABwAOABwAPAA8YD/APwAAAAAAAAAAAAB/gP/B58PDh4cPDx4ePD"
    "h4cPPh/4P8AAAAAAAAAAAAAH/A/4HgA8AHgA/wH+A8AHgA8AH/A/4AAAAAAAAAAAAA/4H/A8AHgA"
    "8AH+A/wHgA8AHgA8AHgAAAAAAAAAAAAAB/Af8Hhh4AOABwAOPhx8PDg8cD/gP4AAAAAAAAAAAAB4"
    "cPDh4cPDh4cP/h/8PDh4cPDh4cPDgAAAAAAAAAAAAB4APAB4APAB4APAB4APAB4APAB4APAAAAAA"
    "AAAAAA8AHgA8AHgA8AHgA8AHgA8AHgA8AHgA4AfADwAAAAAAAAPHh54PeB/gP4B+AP4B/gPeB54P"
    "Hh4eAAAAAAAAAAAAA8AHgA8AHgA8AHgA8AHgA8AHgA/4H/AAAAAAAAAAAAA+H3w++H35+/P3fu75"
    "3PO553GO4B3AOAAAAAAAAAAAAB4cPjh8cPzh+cO7hzcOfhx8OPhw8OHgAAAAAAAAAAAAD8B/wOPD"
    "w4cHjgccDjg8eHBx4P+AfgAAAAAAAAAAAAB/gP+B54PHB44PPB/wP8B4APAB4APAAAAAAAAAAAAf"
    "gP+Bx4eHDg8cDjgccHjw4OPB/wD8ADwAPAAAAAAAAAAB/gP+B54PPB5wP8B/gPeB54PHB44PHgAA"
    "AAAAAAAAAAD8A/wOGBwAPAA/gD+AHwAOBhwP+A/gAAAAAAAAAAAAB/8P/gHAA4AHAA4AHAA4AHAA"
    "4AHAA4AAAAAAAAAAAAAPHh48PHh48PHh48PHh48PHg44H/APgAAAAAAAAAAAADgcODhw8OHA44HO"
    "A5wDuAfgD8APgB4AAAAAAAAAAAAAxw+PHx4+fO753bu7N35+/Pjx8ePjw8AAAAAAAAAAAABw8PHA"
    "5wD+AfgB4APAD8AfwHOB44OHgAAAAAAAAAAAAPDw48HnAd4B+APgA8AHAA4AHAA4AHAAAAAAAAAA"
    "AAAB/4P/ADwAeAHgB4AeADgA8APAB/4P/AAAAAAAAAAAAAAAAAAH8A/wAPAf4H/A44HPA/4D/AAA"
    "AAAAAAAAAAAAA4AHAA4AH+A/4HnA4cHDg4cHnA/4H+AAAAAAAAAAAAAAAAAAA+AP4DwAcADgAcAD"
    "wAP4A+AAAAAAAAAAAAAAAAA4AHAA4B/A/4HPA44HHA44HPA/4D/AAAAAAAAAAAAAAAAAAB8AfwHH"
    "A/4H/A4AHjAf4B+AAAAAAAAAAAAAAAAHgB8AOAH8A/gBwAOABwAOABwAOABwAAAAAAAAAAAAAB/A"
    "f4HPA44HHA44HPAf4B/AQ4D+APgAAAAAAAAAAAAA4AHAA4AHeA/4HnA44HHA44HHA44HHAAAAAAA"
    "AAAAAAA4AHAAAAHAA4AHAA4AHAA4AHAA4AHAAAAAAAAAAAA4AHAAAAHAA4AHAA4AHAA4AHAA4AHA"
    "A4AfADwAAAAAAAAHAA4AHAA44HOA7gH4A/AH8A7wHPA48AAAAAAAAAAAAAHAA4AHAA4AHAA4AHAA"
    "4AHAA4AHAA4AAAAAAAAAAAAAAAAAA73n/+893HO45/HP45/HP454AAAAAAAAAAAAAAAAAAAA7wH/"
    "A84HHA44HHA44HHA44AAAAAAAAAAAAAAAAAAAAB8AfwHHA44HHA44HHAfwB8AAAAAAAAAAAAAAAA"
    "/wH/A84HDg4cHDg84H/A/wHAA4AHAAAAAAAAAAAAAAD/A/4HPA44HHA44HPA/4D/AA4AHAA4AAAA"
    "AAAAAAAAAAAAAAdwD+AeADgAcADgAcADgAcAAAAAAAAAAAAAAAAAAAAAD4A/gHEA4AD8ADwEOA/w"
    "D8AAAAAAAAAAAAAAAAAABwAOAH8A/gBwAOABwAOABwAPgA8AAAAAAAAAAAAAAAAAAHHA44HHA44H"
    "HA44HvAf4D/AAAAAAAAAAAAAAAAAAAABw4HHA5wHOAdwD8APgB4APAAAAAAAAAAAAAAAAAAAAAc5"
    "znOc5zvsNvh98Pvh54HHAAAAAAAAAAAAAAAAAAAAA44HOAfgB8APAB8AfgHOA44AAAAAAAAAAAAA"
    "AAOHA44HOAZwDsAfgB8APAA4AGADwAcAAAAAAAAAAAAAAAAAAAf4D/ABwAcAHABwAeAD/Af4AAAA"
    "AAAAAAAAAAAB8AfwHvA44HHA44HHA44HHA94D+APgAAAAAAAAAAAAAPAD4AXAA4AHAA4AHAA4AHA"
    "A4Af4D/AAAAAAAAAAAAAD8A/wGPAB4APABwAcAHABwAcAH/A/4AAAAAAAAAAAAAPgH+AR4AOAPgB"
    "+AB4AHAA4EPA/wD8AAAAAAAAAAAAAAeAHwA+APwDuAZwHOAxwH/g/8AOABwAAAAAAAAAAAAAfwD+"
    "AYADAAfgD+AR4AHAA4GPA/wD8AAAAAAAAAAAAAA+AP4DjA4AH+A/4HnA44HHAc4D+APgAAAAAAAA"
    "AAAAA/4H/AB4AOABwAcADgA4AHAB4AOADwAAAAAAAAAAAAAB+A/4HHA44D+AfwHnA44HHA84D/AP"
    "gAAAAAAAAAAAAAPgD+A54HHA44HPA/4B/AA4COAfwD4AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA"
    "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA4AHAA4AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA"
    "4AHABwAOABgAAAAAAAAAAAAAAAAAAAAAAAA4AHAA4AAAAAAAAA4AHAA4AOABgAAAAAAAAAAAAAAA"
    "AAAA4AHAA4AAAAAAAAA4AHAA4AAAAAAAAAAAAAAAAHAA4AHAA4AHAA4AHAA4AAAA4AHAA4AAAAAA"
    "AAAAAAAB8AfwCOABwAOADgA4AHAAAAHAA4AHAAAAAAAAAAAAADww2GGZgzMGzAewAG8BmwJnDM4w"
    "2GHgAAAAAAAAAADgAYAHAA4AGABwAOABwAOAAwAHAA4ADAAcAAAAAAAABwAHAA4ADAAcADgAcADg"
    "AcADgAYAHAA4AOAAAAAAAAAAAAAADAAYADAAYA/8H/gDAAYADAAYAAAAAAAAAAAAAAAAAAAAAAAB"
    "8APgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAMABAAYADAAYAGAAwAGABgAMABgAYADAAAAAAAAAAA"
    "AfAH8A5AHAA8APjj+cc/Dj4eeB/4H3gAAAAAAAAAAAAAAAAAH/g/8AAAAAH/g/8AAAAAAAAAAAAA"
    "AAAAAAAAQACAB8AfwHSA6AD8AP4AXAy4H/AfwAQACAAAAAAAAAAAAzAGYA2A/8H/gMwBsB/8P/gZ"
    "gDMATAAAAAAAAAAAD8Aw4MBjPszM2ZmzM2ZmzM2Z8Z/BgAGGAfgAAAAAAAAAAAwAWwD+APAD+AWw"
    "AwAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAH+AAAAAAAAAAAAAAAAAAAAAAAAwAGAA"
    "wAGAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAZgDMAZgDMAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA"
    "AAAAAAAAH/g/8AAAAAH/g/8AAAAAAAAAAAAAAAAAAAAAAAAAAAAHAB8AfgD8APgB4AAAAAAAAAAA"
    "AAAAAAAAAAAAAAAAAAAH/+//wAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAHAA4AGABwAMAAAAAAAAAA"
    "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAfgD8AAAAAAAAAAAAAAAAAAAAAAAAAA="
)


def decode_font():
    """Decode FONT_B64 into one list of CELL_H row ints per charset char."""
    raw = base64.b64decode(FONT_B64)
    glyphs = []
    per = CELL_W * CELL_H
    total = len(CHARSET) * per
    for gi in range(len(CHARSET)):
        rows = []
        base = gi * per
        for y in range(CELL_H):
            v = 0
            for x in range(CELL_W):
                bitpos = base + y * CELL_W + x
                byte = raw[bitpos // 8]
                bit = (byte >> (7 - bitpos % 8)) & 1
                v = (v << 1) | bit
            rows.append(v)
        glyphs.append(rows)
    assert total <= len(raw) * 8, "font blob too short"
    return glyphs


GLYPHS = decode_font()
GLYPH_INDEX = {ch: i for i, ch in enumerate(CHARSET)}

# ------------------------------------------------------------------- colors
PAPER = (250, 246, 235)
INK = (20, 20, 20)
RED = (165, 20, 20)
BLUE = (30, 80, 140)
GREEN = (26, 110, 56)
ORANGE = (216, 106, 18)
GRAY = (112, 106, 94)
PANEL = (234, 228, 208)
WHITE = (255, 255, 255)
DARKBLUE = (22, 50, 96)

# ------------------------------------------------------------------- canvas


class Canvas:
    """An RGB framebuffer with filled shapes and bitmap text."""

    def __init__(self, w, h, bg):
        self.w = w
        self.h = h
        self.buf = bytearray(bg * (w * h))

    def px(self, x, y, color):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.buf[i:i + 3] = bytes(color)

    def rect(self, x, y, w, h, color):
        x0 = max(0, x)
        y0 = max(0, y)
        x1 = min(self.w, x + w)
        y1 = min(self.h, y + h)
        if x1 <= x0 or y1 <= y0:
            return
        row = bytes(color) * (x1 - x0)
        for yy in range(y0, y1):
            i = (yy * self.w + x0) * 3
            self.buf[i:i + len(row)] = row

    def hline(self, x, y, w, color, thick=1):
        self.rect(x, y, w, thick, color)

    def vline(self, x, y, h, color, thick=1):
        self.rect(x, y, thick, h, color)

    def line(self, x0, y0, x1, y1, color, thick=1):
        dx = abs(x1 - x0)
        dy = -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        x, y = x0, y0
        half = thick // 2
        while True:
            self.rect(x - half, y - half, thick, thick, color)
            if x == x1 and y == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x += sx
            if e2 <= dx:
                err += dx
                y += sy

    def disc(self, cx, cy, r, color):
        for dy in range(-r, r + 1):
            dx = math.isqrt(max(0, r * r - dy * dy))
            self.rect(cx - dx, cy + dy, 2 * dx + 1, 1, color)

    def ring(self, cx, cy, r, color, thick=2):
        self.disc(cx, cy, r, color)
        self.disc(cx, cy, max(0, r - thick), PAPER)

    def text_width(self, s, scale):
        return len(s) * CELL_W * scale

    def text(self, x, y, s, scale, color, align="left"):
        if align == "center":
            x -= self.text_width(s, scale) // 2
        elif align == "right":
            x -= self.text_width(s, scale)
        cx = x
        for ch in s:
            gi = GLYPH_INDEX.get(ch)
            if gi is None:
                cx += CELL_W * scale
                continue
            for gy in range(CELL_H):
                bits = GLYPHS[gi][gy]
                if not bits:
                    continue
                for gx in range(CELL_W):
                    if bits & (1 << (CELL_W - 1 - gx)):
                        self.rect(cx + gx * scale, y + gy * scale,
                                  scale, scale, color)
            cx += CELL_W * scale
        return cx

    def wrap(self, s, scale, max_w):
        """Word-wrap s to lines no wider than max_w at the given scale."""
        lines = []
        for para in s.split("\n"):
            words = para.split(" ")
            cur = ""
            for word in words:
                trial = word if not cur else cur + " " + word
                if self.text_width(trial, scale) <= max_w or not cur:
                    cur = trial
                else:
                    lines.append(cur)
                    cur = word
            if cur:
                lines.append(cur)
        return lines


# --------------------------------------------------------------- PNG output


def encode_png(rgb, w, h):
    def chunk(typ, data):
        out = struct.pack(">I", len(data)) + typ + data
        return out + struct.pack(">I", zlib.crc32(typ + data) & 0xFFFFFFFF)

    ihdr = struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0)
    raw = bytearray()
    stride = w * 3
    for y in range(h):
        raw.append(0)
        raw += rgb[y * stride:(y + 1) * stride]
    return (
        b"\x89PNG\r\n\x1a\n"
        + chunk(b"IHDR", ihdr)
        + chunk(b"IDAT", zlib.compress(bytes(raw), 6))
        + chunk(b"IEND", b"")
    )

# -------------------------------------------------------------------- layout

MARGIN = 30
RIGHT = W - MARGIN


def draw_globe(cv, x, y):
    """Earth in trouble: blue disc, green land, a red crack."""
    cx, cy = x + 46, y + 46
    cv.disc(cx, cy, 34, BLUE)
    cv.disc(cx - 15, cy - 12, 9, GREEN)
    cv.disc(cx + 12, cy + 8, 11, GREEN)
    cv.disc(cx + 4, cy - 18, 7, GREEN)
    cv.disc(cx - 8, cy + 18, 6, GREEN)
    cv.disc(cx - 20, cy - 20, 5, WHITE)
    crack = [(cx - 30, cy - 10), (cx - 14, cy + 4), (cx - 4, cy - 8),
             (cx + 10, cy + 10), (cx + 20, cy - 2), (cx + 30, cy + 8)]
    for (x0, y0), (x1, y1) in zip(crack, crack[1:]):
        cv.line(x0, y0, x1, y1, RED, 4)


def draw_ship(cv, x, y):
    """A warship under a starburst explosion."""
    cv.rect(x + 10, y + 56, 72, 12, DARKBLUE)
    cv.rect(x + 22, y + 68, 48, 7, DARKBLUE)
    cv.rect(x + 44, y + 38, 5, 18, DARKBLUE)
    cv.rect(x + 30, y + 44, 32, 5, DARKBLUE)
    cx, cy = x + 46, y + 20
    for ang in range(0, 360, 30):
        rad = math.radians(ang)
        cv.line(cx, cy, cx + int(15 * math.cos(rad)),
                cy + int(15 * math.sin(rad)), ORANGE, 3)
    cv.disc(cx, cy, 6, ORANGE)


def draw_bank(cv, x, y):
    """A bank under sanctions: columns, pediment, red slash."""
    cv.line(x + 18, y + 14, x + 46, y + 4, DARKBLUE, 3)
    cv.line(x + 74, y + 14, x + 46, y + 4, DARKBLUE, 3)
    cv.rect(x + 16, y + 16, 60, 4, DARKBLUE)
    for i in range(3):
        cv.rect(x + 22 + i * 20, y + 24, 7, 40, DARKBLUE)
    cv.rect(x + 14, y + 66, 64, 5, DARKBLUE)
    cv.rect(x + 10, y + 73, 72, 5, DARKBLUE)
    cv.line(x + 12, y + 12, x + 80, y + 80, RED, 5)


def draw_plane(cv, x, y):
    """An AWACS: fuselage, wings, tail, radar dome on top."""
    cv.rect(x + 12, y + 44, 68, 11, DARKBLUE)
    cv.rect(x + 72, y + 46, 12, 7, DARKBLUE)
    cv.rect(x + 34, y + 30, 9, 15, DARKBLUE)
    cv.rect(x + 52, y + 32, 6, 13, DARKBLUE)
    cv.rect(x + 24, y + 55, 4, 9, INK)
    cv.rect(x + 62, y + 55, 4, 9, INK)
    cv.disc(x + 46, y + 26, 9, BLUE)
    cv.line(x + 16, y + 42, x + 30, y + 48, ORANGE, 3)
    cv.line(x + 16, y + 52, x + 30, y + 48, ORANGE, 3)


def draw_capitol(cv, x, y):
    """A capitol dome on columns: the US House."""
    cv.disc(x + 46, y + 26, 13, DARKBLUE)
    cv.rect(x + 33, y + 26, 26, 6, DARKBLUE)
    cv.rect(x + 44, y + 8, 4, 8, DARKBLUE)
    for i in range(4):
        cv.rect(x + 20 + i * 15, y + 36, 6, 32, DARKBLUE)
    cv.rect(x + 14, y + 70, 64, 5, DARKBLUE)
    cv.rect(x + 10, y + 77, 72, 5, DARKBLUE)


def draw_chart(cv, x0, y_base):
    """Five rising green bars with a red arrow: the market rally."""
    heights = [40, 75, 110, 150, 185]
    for i, h in enumerate(heights):
        bx = x0 + i * 56
        cv.rect(bx, y_base - h, 44, h, GREEN)
    cv.line(x0 - 6, y_base - 30, x0 + 268, y_base - 196, RED, 5)
    cv.line(x0 + 268, y_base - 196, x0 + 240, y_base - 192, RED, 5)
    cv.line(x0 + 268, y_base - 196, x0 + 262, y_base - 168, RED, 5)


BANDS = [
    ("CLIMATE", "CLIMATE TALKS COLLAPSE",
     "COP31 ends in Turkey with no deal on fossil fuels. "
     "Longest climate summit in history.", draw_globe),
    ("UKRAINE WAR", "WARSHIP SUNK OFF LIBYA",
     "Zelensky says Ukrainian drones hit two Russian ships at Benghazi. "
     "Kyiv hails an \u2019exemplary\u2019 mission.", draw_ship),
    ("IRAN", "US SANCTIONS IRAN BANKS",
     "Treasury hits 20+ exchange houses in Iran\u2019s shadow banking. "
     "Tehran claims $290bn damages from US.", draw_bank),
    ("NATO", "NATO SENDS AWACS TO POLAND",
     "Early-warning jet to watch the border after Russian missiles "
     "fell in Poland on Friday.", draw_plane),
    ("US POLITICS", "DEMOCRATS\u2019 RECORD HOUSE WIN",
     "258 seats after Hubbard flips a North Carolina seat from Foxx. "
     "Both chambers now Democratic.", draw_capitol),
]


def draw_page():
    cv = Canvas(W, H, PAPER)
    cv.rect(0, 0, W, 8, INK)

    # Masthead.
    cv.text(W // 2, 24, "THE WORLD TODAY", 4, INK, align="center")
    cv.hline(MARGIN, 104, RIGHT - MARGIN, INK, 2)

    # Date banner.
    cv.rect(MARGIN, 116, RIGHT - MARGIN, 54, RED)
    cv.text(W // 2, 128, "MONDAY, 23 NOVEMBER 2026", 2, WHITE,
            align="center")
    cv.hline(MARGIN, 182, RIGHT - MARGIN, INK, 2)

    # Lead story: Nvidia brings Huang back.
    cv.text(MARGIN, 196, "MARKETS", 1, RED)
    cv.text(MARGIN, 218, "NVIDIA SOARS 31%", 3, INK)
    cv.text(MARGIN, 272, "HUANG IS BACK", 3, INK)
    deck = ("Board reinstates Jensen Huang as CEO, 11 days after he quit. "
            "Shares close at $165.05; Nasdaq jumps 6.5%.")
    y = 336
    for line in cv.wrap(deck, 1, 640):
        cv.text(MARGIN, y, line, 1, INK)
        y += 22
    draw_chart(cv, 700, 390)
    cv.hline(MARGIN, 408, RIGHT - MARGIN, INK, 2)

    # Five story bands.
    y = 420
    for kicker, headline, deck, icon in BANDS:
        cv.rect(MARGIN, y, 92, 92, PANEL)
        cv.rect(MARGIN, y, 92, 2, INK)
        cv.rect(MARGIN, y + 90, 92, 2, INK)
        cv.rect(MARGIN, y, 2, 92, INK)
        cv.rect(MARGIN + 90, y, 2, 92, INK)
        icon(cv, MARGIN, y)
        cv.text(140, y + 4, kicker, 1, RED)
        cv.text(140, y + 24, headline, 2, INK)
        dy = y + 58
        for line in cv.wrap(deck, 1, RIGHT - 140)[:2]:
            cv.text(140, dy, line, 1, INK)
            dy += 18
        y += 96
        if (kicker, headline) != BANDS[-1][:2]:
            cv.hline(MARGIN, y, RIGHT - MARGIN, GRAY, 1)
            y += 8

    # Ticker of smaller items.
    cv.rect(MARGIN, 940, RIGHT - MARGIN, 56, INK)
    cv.text(W // 2, 946,
            "INDONESIA FIRE TOLL 24  \u2022  INDIA GIVES NEPAL $1.62BN",
            1, WHITE, align="center")
    cv.text(W // 2, 966,
            "S. KOREA MINISTER QUITS  \u2022  HOUTHIS CLAIM REFINERY HIT",
            1, WHITE, align="center")
    cv.rect(0, H - 10, W, 10, INK)
    return cv.buf


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    data = encode_png(draw_page(), W, H)
    path = os.path.join(out_dir, "entry.png")
    with open(path, "wb") as f:
        f.write(data)
    print(f"wrote {path} ({len(data)} bytes)")


if __name__ == "__main__":
    main()

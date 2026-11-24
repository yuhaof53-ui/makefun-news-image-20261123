#!/usr/bin/env python3
"""THE WORLD TODAY -- front page for Monday 23 November 2026.

Draws the day's world news as a newspaper front page and writes a
1024x1024 PNG. Pure standard library: a 15x17 bitmap font (base64
below), a pixel canvas with small drawing helpers, and a tiny PNG
encoder. No network, no files read, no randomness, so every run
writes identical bytes. Run with no argument to write
/output/entry.png, or pass an output path.
"""

import base64
import struct
import sys
import zlib

W, H = 1024, 1024

PAPER = (247, 242, 226)
INK = (24, 24, 24)
RED = (179, 32, 32)
GREEN = (34, 120, 62)
BLUE = (32, 84, 160)
GOLD = (233, 128, 28)
BOX = (243, 237, 218)
GREY = (130, 126, 114)
WHITE = (255, 255, 255)

CHARSET = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789 .,;:!?%()+-/&=$#@*_'\"=•—’–"
CELL_W, CELL_H = 15, 17
FONT_B64 = "AAAAAB4APgD8AfgDuA5wHOA44P/B/8ODjgcAAAAAAAAAAAAB/gP+B54PPB5wP+B/wPHB44PHB/4P+AAAAAAAAAAAAAB+Af4HjB4AOABwAOABwAPAA8YD/APwAAAAAAAAAAAAB/gP/B58PDh4cPDx4ePDh4cPPh/4P8AAAAAAAAAAAAAH/A/4HgA8AHgA/wH+A8AHgA8AH/A/4AAAAAAAAAAAAA/4H/A8AHgA8AH+A/wHgA8AHgA8AHgAAAAAAAAAAAAAB/Af8Hhh4AOABwAOPhx8PDg8cD/gP4AAAAAAAAAAAAB4cPDh4cPDh4cP/h/8PDh4cPDh4cPDgAAAAAAAAAAAAB4APAB4APAB4APAB4APAB4APAB4APAAAAAAAAAAAA8AHgA8AHgA8AHgA8AHgA8AHgA8AHgA4AfADwAAAAAAAAPHh54PeB/gP4B+AP4B/gPeB54PHh4eAAAAAAAAAAAAA8AHgA8AHgA8AHgA8AHgA8AHgA/4H/AAAAAAAAAAAAA+H3w++H35+/P3fu753PO553GO4B3AOAAAAAAAAAAAAB4cPjh8cPzh+cO7hzcOfhx8OPhw8OHgAAAAAAAAAAAAD8B/wOPDw4cHjgccDjg8eHBx4P+AfgAAAAAAAAAAAAB/gP+B54PHB44PPB/wP8B4APAB4APAAAAAAAAAAAAfgP+Bx4eHDg8cDjgccHjw4OPB/wD8ADwAPAAAAAAAAAAB/gP+B54PPB5wP8B/gPeB54PHB44PHgAAAAAAAAAAAAD8A/wOGBwAPAA/gD+AHwAOBhwP+A/gAAAAAAAAAAAAB/8P/gHAA4AHAA4AHAA4AHAA4AHAA4AAAAAAAAAAAAAPHh48PHh48PHh48PHh48PHg44H/APgAAAAAAAAAAAADgcODhw8OHA44HOA5wDuAfgD8APgB4AAAAAAAAAAAAAxw+PHx4+fO753bu7N35+/Pjx8ePjw8AAAAAAAAAAAABw8PHA5wD+AfgB4APAD8AfwHOB44OHgAAAAAAAAAAAAPDw48HnAd4B+APgA8AHAA4AHAA4AHAAAAAAAAAAAAAB/4P/ADwAeAHgB4AeADgA8APAB/4P/AAAAAAAAAAAAAAAAAAH8A/wAPAf4H/A44HPA/4D/AAAAAAAAAAAAAAAA4AHAA4AH+A/4HnA4cHDg4cHnA/4H+AAAAAAAAAAAAAAAAAAA+AP4DwAcADgAcADwAP4A+AAAAAAAAAAAAAAAAA4AHAA4B/A/4HPA44HHA44HPA/4D/AAAAAAAAAAAAAAAAAAB8AfwHHA/4H/A4AHjAf4B+AAAAAAAAAAAAAAAAHgB8AOAH8A/gBwAOABwAOABwAOABwAAAAAAAAAAAAAB/Af4HPA44HHA44HPAf4B/AQ4D+APgAAAAAAAAAAAAA4AHAA4AHeA/4HnA44HHA44HHA44HHAAAAAAAAAAAAAA4AHAAAAHAA4AHAA4AHAA4AHAA4AHAAAAAAAAAAAA4AHAAAAHAA4AHAA4AHAA4AHAA4AHAA4AfADwAAAAAAAAHAA4AHAA44HOA7gH4A/AH8A7wHPA48AAAAAAAAAAAAAHAA4AHAA4AHAA4AHAA4AHAA4AHAA4AAAAAAAAAAAAAAAAAA73n/+893HO45/HP45/HP454AAAAAAAAAAAAAAAAAAAA7wH/A84HHA44HHA44HHA44AAAAAAAAAAAAAAAAAAAAB8AfwHHA44HHA44HHAfwB8AAAAAAAAAAAAAAAA/wH/A84HDg4cHDg84H/A/wHAA4AHAAAAAAAAAAAAAAD/A/4HPA44HHA44HPA/4D/AA4AHAA4AAAAAAAAAAAAAAAAAAdwD+AeADgAcADgAcADgAcAAAAAAAAAAAAAAAAAAAAAD4A/gHEA4AD8ADwEOA/wD8AAAAAAAAAAAAAAAAAABwAOAH8A/gBwAOABwAOABwAPgA8AAAAAAAAAAAAAAAAAAHHA44HHA44HHA44HvAf4D/AAAAAAAAAAAAAAAAAAAABw4HHA5wHOAdwD8APgB4APAAAAAAAAAAAAAAAAAAAAAc5znOc5zvsNvh98Pvh54HHAAAAAAAAAAAAAAAAAAAAA44HOAfgB8APAB8AfgHOA44AAAAAAAAAAAAAAAOHA44HOAZwDsAfgB8APAA4AGADwAcAAAAAAAAAAAAAAAAAAAf4D/ABwAcAHABwAeAD/Af4AAAAAAAAAAAAAAAB8AfwHvA44HHA44HHA44HHA94D+APgAAAAAAAAAAAAAPAD4AXAA4AHAA4AHAA4AHAA4Af4D/AAAAAAAAAAAAAD8A/wGPAB4APABwAcAHABwAcAH/A/4AAAAAAAAAAAAAPgH+AR4AOAPgB+AB4AHAA4EPA/wD8AAAAAAAAAAAAAAeAHwA+APwDuAZwHOAxwH/g/8AOABwAAAAAAAAAAAAAfwD+AYADAAfgD+AR4AHAA4GPA/wD8AAAAAAAAAAAAAA+AP4DjA4AH+A/4HnA44HHAc4D+APgAAAAAAAAAAAAA/4H/AB4AOABwAcADgA4AHAB4AOADwAAAAAAAAAAAAAB+A/4HHA44D+AfwHnA44HHA84D/APgAAAAAAAAAAAAAPgD+A54HHA44HPA/4B/AA4COAfwD4AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA4AHAA4AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA4AHABwAOABgAAAAAAAAAAAAAAAAAAAAAAAA4AHAA4AAAAAAAAA4AHAA4AOABgAAAAAAAAAAAAAAAAAAA4AHAA4AAAAAAAAA4AHAA4AAAAAAAAAAAAAAAAHAA4AHAA4AHAA4AHAA4AAAA4AHAA4AAAAAAAAAAAAAB8AfwCOABwAOADgA4AHAAAAHAA4AHAAAAAAAAAAAAADww2GGZgzMGzAewAG8BmwJnDM4w2GHgAAAAAAAAAADgAYAHAA4AGABwAOABwAOAAwAHAA4ADAAcAAAAAAAABwAHAA4ADAAcADgAcADgAcADgAYAHAA4AOAAAAAAAAAAAAAADAAYADAAYA/8H/gDAAYADAAYAAAAAAAAAAAAAAAAAAAAAAAB8APgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAMABAAYADAAYAGAAwAGABgAMABgAYADAAAAAAAAAAAAfAH8A5AHAA8APjj+cc/Dj4eeB/4H3gAAAAAAAAAAAAAAAAAH/g/8AAAAAH/g/8AAAAAAAAAAAAAAAAAAAAAQACAB8AfwHSA6AD8AP4AXAy4H/AfwAQACAAAAAAAAAAAAzAGYA2A/8H/gMwBsB/8P/gZgDMATAAAAAAAAAAAD8Aw4MBjPszM2ZmzM2ZmzM2Z8Z/BgAGGAfgAAAAAAAAAAAwAWwD+APAD+AWwAwAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAH+AAAAAAAAAAAAAAAAAAAAAAAAwAGAAwAGAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAZgDMAZgDMAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAH/g/8AAAAAH/g/8AAAAAAAAAAAAAAAAAAAAAAAAAAAAHAB8AfgD8APgB4AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAH/+//wAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAHAA4AGABwAMAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAfgD8AAAAAAAAAAAAAAAAAAAAAAAAAA="


def load_font():
    """Unpack the base64 blob into {char: [17 row bitmasks]}.

    The blob holds every charset glyph in order, row-major, one bit
    per pixel, packed most-significant-bit first.
    """
    raw = base64.b64decode(FONT_B64)
    bits = []
    for byte in raw:
        for shift in (7, 6, 5, 4, 3, 2, 1, 0):
            bits.append((byte >> shift) & 1)
    table = {}
    per_glyph = CELL_W * CELL_H
    for pos, ch in enumerate(CHARSET):
        if ch in table:
            continue
        start = pos * per_glyph
        rows = []
        for r in range(CELL_H):
            value = 0
            for c in range(CELL_W):
                value = (value << 1) | bits[start + r * CELL_W + c]
            rows.append(value)
        table[ch] = rows
    return table


GLYPHS = load_font()

canvas = bytearray(W * H * 3)


def fill(color):
    r, g, b = color
    canvas[:] = bytes((r, g, b)) * (W * H)


def rect(x, y, w, h, color):
    r, g, b = color
    row = bytes((r, g, b)) * w
    for yy in range(y, y + h):
        base = (yy * W + x) * 3
        canvas[base:base + w * 3] = row


def set_px(x, y, color):
    if 0 <= x < W and 0 <= y < H:
        i = (y * W + x) * 3
        canvas[i], canvas[i + 1], canvas[i + 2] = color


def block(x, y, s, color):
    r, g, b = color
    row = bytes((r, g, b)) * s
    for yy in range(y, y + s):
        base = (yy * W + x) * 3
        canvas[base:base + s * 3] = row


def line(x0, y0, x1, y1, color, thick=1):
    """Bresenham line, thick by stamping squares along it."""
    dx = abs(x1 - x0)
    dy = -abs(y1 - y0)
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    err = dx + dy
    half = thick // 2
    while True:
        for ox in range(-half, half + 1):
            for oy in range(-half, half + 1):
                set_px(x0 + ox, y0 + oy, color)
        if x0 == x1 and y0 == y1:
            break
        e2 = 2 * err
        if e2 >= dy:
            err += dy
            x0 += sx
        if e2 <= dx:
            err += dx
            y0 += sy


def disc(cx, cy, r, color):
    for dy in range(-r, r + 1):
        dx = int((r * r - dy * dy) ** 0.5)
        rect(cx - dx, cy + dy, 2 * dx + 1, 1, color)


def poly(points, color):
    """Scanline fill of a polygon given as [(x, y), ...]."""
    ys = [p[1] for p in points]
    for y in range(min(ys), max(ys) + 1):
        xs = []
        n = len(points)
        for i in range(n):
            x0, y0 = points[i]
            x1, y1 = points[(i + 1) % n]
            if (y0 <= y < y1) or (y1 <= y < y0):
                xs.append(x0 + (y - y0) * (x1 - x0) / (y1 - y0))
        xs.sort()
        for i in range(0, len(xs) - 1, 2):
            x0 = int(xs[i] + 0.5)
            x1 = int(xs[i + 1] + 0.5)
            if x1 > x0:
                rect(x0, y, x1 - x0, 1, color)


def text_width(s, scale, tracking=0):
    if not s:
        return 0
    return len(s) * (CELL_W * scale + tracking) - tracking


def draw_text(s, x, y, scale, color, tracking=0):
    cx = x
    for ch in s:
        rows = GLYPHS.get(ch)
        if rows is not None:
            for r in range(CELL_H):
                bits = rows[r]
                for c in range(CELL_W):
                    if (bits >> (CELL_W - 1 - c)) & 1:
                        block(cx + c * scale, y + r * scale, scale, color)
        cx += CELL_W * scale + tracking
    return cx - x


def draw_centered(s, cx, y, scale, color, tracking=0):
    x = cx - text_width(s, scale, tracking) // 2
    draw_text(s, x, y, scale, color, tracking)


def arrow(x0, y0, x1, y1, color):
    line(x0, y0, x1, y1, color, 5)
    dx, dy = x1 - x0, y1 - y0
    ln = (dx * dx + dy * dy) ** 0.5
    ux, uy = dx / ln, dy / ln
    bx, by = x1 - ux * 26, y1 - uy * 26
    px, py = -uy, ux
    line(x1, y1, int(bx + px * 11), int(by + py * 11), color, 5)
    line(x1, y1, int(bx - px * 11), int(by - py * 11), color, 5)


# ---------------- icons: each drawn inside an 88x88 box at (ox, oy) ----

def icon_globe(ox, oy):
    disc(ox + 44, oy + 44, 30, BLUE)
    rect(ox + 28, oy + 30, 12, 8, GREEN)
    rect(ox + 48, oy + 52, 16, 10, GREEN)
    rect(ox + 30, oy + 56, 10, 8, GREEN)
    rect(ox + 52, oy + 26, 9, 7, GREEN)
    line(ox + 16, oy + 50, ox + 30, oy + 38, RED, 3)
    line(ox + 30, oy + 38, ox + 44, oy + 52, RED, 3)
    line(ox + 44, oy + 52, ox + 58, oy + 36, RED, 3)
    line(ox + 58, oy + 36, ox + 72, oy + 48, RED, 3)


def icon_ship(ox, oy):
    cx, cy = ox + 44, oy + 24
    disc(cx, cy, 8, GOLD)
    # eight sun rays as fixed offsets: cardinal rays reach 12..18 px,
    # diagonal rays 9..13 px, so every ray stays inside the icon box
    for dx, dy in [(12, 0), (9, 9), (0, 12), (-9, 9),
                   (-12, 0), (-9, -9), (0, -12), (9, -9)]:
        line(cx + dx, cy + dy, cx + dx * 3 // 2, cy + dy * 3 // 2, GOLD, 2)
    rect(ox + 43, oy + 34, 2, 28, INK)
    poly([(ox + 18, oy + 62), (ox + 70, oy + 62),
          (ox + 64, oy + 74), (ox + 24, oy + 74)], BLUE)
    rect(ox + 30, oy + 54, 28, 8, BLUE)


def icon_bank(ox, oy):
    poly([(ox + 16, oy + 34), (ox + 44, oy + 16), (ox + 72, oy + 34)], BLUE)
    for cx in (24, 41, 58):
        rect(ox + cx, oy + 38, 6, 26, BLUE)
    rect(ox + 16, oy + 66, 56, 6, BLUE)
    line(ox + 14, oy + 14, ox + 74, oy + 74, RED, 5)


def icon_awacs(ox, oy):
    disc(ox + 44, oy + 40, 9, BLUE)
    rect(ox + 14, oy + 48, 60, 12, BLUE)
    disc(ox + 14, oy + 54, 6, BLUE)
    disc(ox + 74, oy + 54, 6, BLUE)
    poly([(ox + 66, oy + 48), (ox + 76, oy + 32), (ox + 76, oy + 48)], BLUE)
    poly([(ox + 36, oy + 60), (ox + 28, oy + 72), (ox + 46, oy + 60)], BLUE)
    rect(ox + 8, oy + 50, 6, 8, GOLD)


def icon_capitol(ox, oy):
    disc(ox + 44, oy + 34, 12, BLUE)
    rect(ox + 32, oy + 34, 24, 6, BLUE)
    for cx in (22, 34, 46, 58):
        rect(ox + cx, oy + 44, 5, 22, BLUE)
    rect(ox + 16, oy + 68, 56, 6, BLUE)
    line(ox + 44, oy + 14, ox + 44, oy + 22, INK, 2)


def icon_box(ox, oy, draw):
    rect(ox, oy, 88, 88, INK)
    rect(ox + 2, oy + 2, 84, 84, BOX)
    draw(ox + 2, oy + 2)


# ---------------- the page ----------------

BANDS = [
    ("CLIMATE", "CLIMATE TALKS COLLAPSE", icon_globe,
     "COP31 ends in Turkey with no deal on fossil fuels.",
     "Longest climate summit in history."),
    ("UKRAINE WAR", "WARSHIP SUNK OFF LIBYA", icon_ship,
     "Zelensky says Ukrainian drones hit two Russian ships at",
     "Benghazi. Kyiv hails an 'exemplary' mission."),
    ("IRAN", "US SANCTIONS IRAN BANKS", icon_bank,
     "Treasury hits 20+ exchange houses in Iran's shadow",
     "banking. Tehran claims $290bn damages from US."),
    ("NATO", "NATO SENDS AWACS TO POLAND", icon_awacs,
     "Early-warning jet to watch the border after Russian",
     "missiles fell in Poland on Friday."),
    ("US POLITICS", "DEMOCRATS' RECORD HOUSE WIN", icon_capitol,
     "258 seats after Hubbard flips a North Carolina seat from",
     "Foxx. Both chambers now Democratic."),
]


def draw_page():
    fill(PAPER)
    # masthead
    draw_text("THE WORLD TODAY", 62, 24, 4, INK)
    rect(28, 104, 968, 3, INK)
    # red date band
    rect(28, 116, 968, 52, RED)
    draw_centered("MONDAY, 23 NOVEMBER 2026", 512, 125, 2, WHITE, tracking=2)
    rect(28, 178, 968, 2, INK)
    # markets lead
    draw_text("MARKETS", 28, 192, 1, RED)
    draw_text("NVIDIA SOARS 31%", 28, 214, 3, INK)
    draw_text("HUANG IS BACK", 28, 270, 3, INK)
    draw_text("Board reinstates Jensen Huang as CEO, 11", 28, 336, 1, INK)
    draw_text("days after he quit. Shares close at", 28, 359, 1, INK)
    draw_text("$165.05; Nasdaq jumps 6.5%.", 28, 382, 1, INK)
    # rising bar chart with a red arrow
    tops = [336, 302, 266, 228, 192]
    for i, top in enumerate(tops):
        x = 706 + i * 58
        rect(x, top, 46, 374 - top, GREEN)
    arrow(700, 370, 978, 196, RED)
    rect(28, 398, 968, 2, INK)
    # five story bands
    for i, (kicker, head, icon, sub1, sub2) in enumerate(BANDS):
        top = 408 + i * 98
        if i:
            rect(28, top - 3, 968, 1, GREY)
        icon_box(28, top + 4, icon)
        draw_text(kicker, 136, top + 6, 1, RED)
        draw_text(head, 136, top + 26, 2, INK)
        draw_text(sub1, 136, top + 64, 1, INK)
        draw_text(sub2, 136, top + 83, 1, INK)
    # black ticker
    rect(28, 912, 968, 74, INK)
    draw_centered("INDONESIA FIRE TOLL 24  •  INDIA GIVES NEPAL $1.62BN",
                  512, 926, 1, WHITE)
    draw_centered("S. KOREA MINISTER QUITS  •  HOUTHIS CLAIM REFINERY HIT",
                  512, 951, 1, WHITE)


def chunk(kind, data):
    return (struct.pack(">I", len(data)) + kind + data +
            struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF))


def png_bytes():
    raw = bytearray()
    for y in range(H):
        raw.append(0)
        raw += canvas[y * W * 3:(y + 1) * W * 3]
    ihdr = struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0)
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr) +
            chunk(b"IDAT", zlib.compress(bytes(raw), 6)) +
            chunk(b"IEND", b""))


def main():
    out = sys.argv[1] if len(sys.argv) > 1 else "/output/entry.png"
    draw_page()
    with open(out, "wb") as f:
        f.write(png_bytes())


if __name__ == "__main__":
    main()

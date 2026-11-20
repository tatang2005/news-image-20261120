"""Front-page renderer for the news-image-20261120 make.fun entry.

Draws a 1024x1024 newspaper front page summarising Friday 20 November 2026
using nothing but the Python standard library: a hand-rolled PNG writer
(zlib + struct), a small software rasteriser (rects, lines, circles), and
a 5x7 bitmap font defined below as literal bit patterns.

No third-party packages, no image files, no randomness: the same code
always produces the same bytes.
"""

import struct
import zlib

# ---------------------------------------------------------------------------
# Palette
# ---------------------------------------------------------------------------

PAPER = (246, 241, 229)   # warm off-white newsprint
INK = (22, 20, 17)        # near-black ink
RED = (176, 32, 26)       # single accent red
WHITE = (250, 248, 243)   # ticker text
FAINT = (120, 112, 98)    # muted grey-brown for hairlines

# ---------------------------------------------------------------------------
# 5x7 bitmap font. Each glyph is seven rows of five bits, written out by
# hand as strings of '0'/'1'. Only the characters the page needs are here.
# ---------------------------------------------------------------------------

FONT = {
    "A": ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    "B": ("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
    "C": ("01110", "10001", "10000", "10000", "10000", "10001", "01110"),
    "D": ("11100", "10010", "10001", "10001", "10001", "10010", "11100"),
    "E": ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
    "F": ("11111", "10000", "10000", "11110", "10000", "10000", "10000"),
    "G": ("01110", "10001", "10000", "10111", "10001", "10001", "01111"),
    "H": ("10001", "10001", "10001", "11111", "10001", "10001", "10001"),
    "I": ("01110", "00100", "00100", "00100", "00100", "00100", "01110"),
    "J": ("00111", "00010", "00010", "00010", "00010", "10010", "01100"),
    "K": ("10001", "10010", "10100", "11000", "10100", "10010", "10001"),
    "L": ("10000", "10000", "10000", "10000", "10000", "10000", "11111"),
    "M": ("10001", "11011", "10101", "10101", "10001", "10001", "10001"),
    "N": ("10001", "11001", "10101", "10011", "10001", "10001", "10001"),
    "O": ("01110", "10001", "10001", "10001", "10001", "10001", "01110"),
    "P": ("11110", "10001", "10001", "11110", "10000", "10000", "10000"),
    "Q": ("01110", "10001", "10001", "10001", "10101", "10010", "01101"),
    "R": ("11110", "10001", "10001", "11110", "10100", "10010", "10001"),
    "S": ("01111", "10000", "10000", "01110", "00001", "00001", "11110"),
    "T": ("11111", "00100", "00100", "00100", "00100", "00100", "00100"),
    "U": ("10001", "10001", "10001", "10001", "10001", "10001", "01110"),
    "V": ("10001", "10001", "10001", "10001", "10001", "01010", "00100"),
    "W": ("10001", "10001", "10001", "10101", "10101", "10101", "01010"),
    "X": ("10001", "01010", "00100", "00100", "00100", "01010", "10001"),
    "Y": ("10001", "01010", "00100", "00100", "00100", "00100", "00100"),
    "Z": ("11111", "00001", "00010", "00100", "01000", "10000", "11111"),
    "0": ("01110", "10001", "10011", "10101", "11001", "10001", "01110"),
    "1": ("00100", "01100", "00100", "00100", "00100", "00100", "01110"),
    "2": ("01110", "10001", "00001", "00110", "01000", "10000", "11111"),
    "3": ("11111", "00010", "00100", "00010", "00001", "10001", "01110"),
    "4": ("00010", "00110", "01010", "10010", "11111", "00010", "00010"),
    "5": ("11111", "10000", "11110", "00001", "00001", "10001", "01110"),
    "6": ("00110", "01000", "10000", "11110", "10001", "10001", "01110"),
    "7": ("11111", "00001", "00010", "00100", "01000", "01000", "01000"),
    "8": ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    "9": ("01110", "10001", "10001", "01111", "00001", "00010", "01100"),
    " ": ("00000", "00000", "00000", "00000", "00000", "00000", "00000"),
    ".": ("00000", "00000", "00000", "00000", "00000", "01100", "01100"),
    ",": ("00000", "00000", "00000", "00000", "01100", "00100", "01000"),
    "'": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
    "-": ("00000", "00000", "00000", "01110", "00000", "00000", "00000"),
    ":": ("00000", "01100", "01100", "00000", "01100", "01100", "00000"),
    ";": ("00000", "01100", "01100", "00000", "01100", "00100", "01000"),
    "!": ("00100", "00100", "00100", "00100", "00100", "00000", "00100"),
    "?": ("01110", "10001", "00001", "00010", "00100", "00000", "00100"),
    "%": ("11001", "11010", "00010", "00100", "01000", "01011", "10011"),
    "$": ("00100", "01111", "10100", "01110", "00101", "11110", "00100"),
    "(": ("00010", "00100", "01000", "01000", "01000", "00100", "00010"),
    ")": ("01000", "00100", "00010", "00010", "00010", "00100", "01000"),
    "/": ("00001", "00010", "00010", "00100", "01000", "01000", "10000"),
    "&": ("01100", "10010", "10100", "01000", "10101", "10010", "01101"),
    "+": ("00000", "00100", "00100", "01110", "00100", "00100", "00000"),
    "*": ("00000", "10101", "01110", "11111", "01110", "10101", "00000"),
    '"': ("01010", "01010", "01010", "00000", "00000", "00000", "00000"),
    "=": ("00000", "00000", "11111", "00000", "11111", "00000", "00000"),
}

GLYPH_W = 5
GLYPH_H = 7
ADVANCE = 6  # glyph width plus one column of tracking, in font units


# ---------------------------------------------------------------------------
# Canvas: a flat RGB pixel buffer plus the drawing primitives.
# ---------------------------------------------------------------------------


class Canvas:
    def __init__(self, width, height, bg):
        self.w = width
        self.h = height
        self.px = bytearray(bg) * (width * height)

    def set(self, x, y, color):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i:i + 3] = bytes(color)

    def fill_rect(self, x, y, w, h, color):
        x0 = max(0, x)
        y0 = max(0, y)
        x1 = min(self.w, x + w)
        y1 = min(self.h, y + h)
        if x1 <= x0 or y1 <= y0:
            return
        row = bytes(color) * (x1 - x0)
        for yy in range(y0, y1):
            i = (yy * self.w + x0) * 3
            self.px[i:i + len(row)] = row

    def rect_outline(self, x, y, w, h, color, t=1):
        self.fill_rect(x, y, w, t, color)
        self.fill_rect(x, y + h - t, w, t, color)
        self.fill_rect(x, y, t, h, color)
        self.fill_rect(x + w - t, y, t, h, color)

    def line(self, x0, y0, x1, y1, color, t=1):
        # Bresenham, stamping a t-by-t square at each step for weight.
        dx = abs(x1 - x0)
        dy = -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        off = t // 2
        while True:
            self.fill_rect(x0 - off, y0 - off, t, t, color)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x0 += sx
            if e2 <= dx:
                err += dx
                y0 += sy

    def circle_outline(self, cx, cy, r, color, t=1):
        # Midpoint circle.
        x = r
        y = 0
        err = 1 - r
        off = t // 2
        while x >= y:
            for px, py in ((cx + x, cy + y), (cx - x, cy + y),
                           (cx + x, cy - y), (cx - x, cy - y),
                           (cx + y, cy + x), (cx - y, cy + x),
                           (cx + y, cy - x), (cx - y, cy - x)):
                self.fill_rect(px - off, py - off, t, t, color)
            y += 1
            if err < 0:
                err += 2 * y + 1
            else:
                x -= 1
                err += 2 * (y - x) + 1

    def fill_circle(self, cx, cy, r, color):
        r2 = r * r
        for yy in range(cy - r, cy + r + 1):
            dy = yy - cy
            span = int((r2 - dy * dy) ** 0.5)
            self.fill_rect(cx - span, yy, 2 * span + 1, 1, color)

    # -- PNG serialisation -------------------------------------------------

    def to_bytes(self):
        stride = self.w * 3
        raw = bytearray()
        for y in range(self.h):
            raw.append(0)  # filter type 0 (None) for every scanline
            raw += self.px[y * stride:(y + 1) * stride]

        def chunk(kind, data):
            out = struct.pack(">I", len(data)) + kind + data
            out += struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)
            return out

        header = struct.pack(">IIBBBBB", self.w, self.h, 8, 2, 0, 0, 0)
        return (b"\x89PNG\r\n\x1a\n"
                + chunk(b"IHDR", header)
                + chunk(b"IDAT", zlib.compress(bytes(raw), 9))
                + chunk(b"IEND", b""))

    def save(self, path):
        with open(path, "wb") as fh:
            fh.write(self.to_bytes())


# ---------------------------------------------------------------------------
# Text: measuring, drawing, wrapping with the bitmap font.
# ---------------------------------------------------------------------------


def text_width(text, scale):
    if not text:
        return 0
    return (len(text) * ADVANCE - 1) * scale


def draw_text(c, x, y, text, scale, color, bold=False):
    text = text.upper()
    cx = x
    for ch in text:
        glyph = FONT.get(ch, FONT[" "])
        for row in range(GLYPH_H):
            bits = glyph[row]
            for col in range(GLYPH_W):
                if bits[col] == "1":
                    c.fill_rect(cx + col * scale, y + row * scale,
                                scale, scale, color)
                    if bold:
                        c.fill_rect(cx + col * scale + 1, y + row * scale,
                                    scale, scale, color)
        cx += ADVANCE * scale
    return cx - x


def draw_text_centered(c, cx, y, text, scale, color, bold=False):
    w = text_width(text, scale)
    if bold:
        w += 1
    return draw_text(c, cx - w // 2, y, text, scale, color, bold)


def draw_text_right(c, xr, y, text, scale, color, bold=False):
    w = text_width(text, scale)
    if bold:
        w += 1
    return draw_text(c, xr - w, y, text, scale, color, bold)


def wrap_text(text, scale, max_width):
    """Greedy word wrap; returns a list of lines that fit max_width."""
    lines = []
    current = ""
    for word in text.upper().split():
        trial = word if not current else current + " " + word
        if text_width(trial, scale) <= max_width:
            current = trial
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


# ---------------------------------------------------------------------------
# Panel icons. Each draws inside a box with top-left corner (x, y) and
# roughly 54x54 pixels. Simple shapes only: poles, decks, tubes, axes.
# ---------------------------------------------------------------------------


def icon_flags(c, x, y):
    # Three summit flags on poles above a shared base line.
    for i, col in enumerate((RED, INK, RED)):
        px = x + 6 + i * 19
        c.fill_rect(px, y + 4, 2, 40, INK)
        c.fill_rect(px + 2, y + 4, 13, 9, col)
    c.fill_rect(x + 2, y + 46, 50, 3, INK)


def icon_bridge(c, x, y):
    # Suspension bridge: two towers, a deck, sagging cables, water below.
    deck_y = y + 34
    c.fill_rect(x + 2, deck_y, 50, 3, INK)
    for tx in (x + 13, x + 39):
        c.fill_rect(tx, y + 10, 3, deck_y - y - 10 + 8, INK)
    # Main cables: straight segments approximating the sag.
    c.line(x + 2, y + 16, x + 14, y + 10, INK, 2)
    c.line(x + 14, y + 10, x + 27, y + 20, INK, 2)
    c.line(x + 27, y + 20, x + 40, y + 10, INK, 2)
    c.line(x + 40, y + 10, x + 52, y + 16, INK, 2)
    # Hangers.
    for hx in (x + 20, x + 27, x + 34):
        c.fill_rect(hx, y + 17, 1, deck_y - y - 17, INK)
    # Water: two short wavy strokes in red.
    for wy in (y + 44, y + 50):
        for wx in range(x + 4, x + 48, 11):
            c.line(wx, wy + 2, wx + 5, wy - 2, RED, 2)
            c.line(wx + 5, wy - 2, wx + 10, wy + 2, RED, 2)


def icon_thermometer(c, x, y):
    # Thermometer with a red column and bulb.
    cx = x + 27
    c.rect_outline(cx - 5, y + 2, 10, 34, INK, 2)
    c.fill_rect(cx - 2, y + 18, 4, 15, RED)
    c.circle_outline(cx, y + 43, 9, INK, 2)
    c.fill_circle(cx, y + 43, 5, RED)
    for i in range(3):
        c.fill_rect(cx + 9, y + 8 + i * 9, 7, 2, INK)


def icon_chart(c, x, y):
    # Axes and a rising red line with an arrowhead. Drawn squashed into
    # the top ~32px of the box so it stays clear of the headline below.
    c.fill_rect(x + 6, y + 2, 2, 30, INK)
    c.fill_rect(x + 6, y + 30, 46, 2, INK)
    pts = [(x + 10, y + 25), (x + 20, y + 20), (x + 29, y + 22),
           (x + 39, y + 13), (x + 49, y + 7)]
    for (ax, ay), (bx, by) in zip(pts, pts[1:]):
        c.line(ax, ay, bx, by, RED, 3)
    c.line(x + 49, y + 7, x + 41, y + 8, RED, 3)
    c.line(x + 49, y + 7, x + 48, y + 14, RED, 3)
    # Small down tick for the falling index.
    c.line(x + 12, y + 5, x + 20, y + 8, INK, 2)
    c.line(x + 20, y + 8, x + 13, y + 8, INK, 2)
    c.line(x + 20, y + 8, x + 19, y + 4, INK, 2)


def icon_gavel(c, x, y):
    # Gavel: a banded head, a diagonal handle, a sounding block. Drawn
    # squashed into the top ~32px of the box so it stays clear of the
    # headline below.
    c.fill_rect(x + 6, y + 4, 26, 9, INK)
    c.fill_rect(x + 10, y + 2, 4, 13, RED)
    c.fill_rect(x + 24, y + 2, 4, 13, RED)
    c.line(x + 26, y + 12, x + 42, y + 25, INK, 4)
    c.fill_rect(x + 4, y + 29, 34, 3, INK)
    c.fill_rect(x + 12, y + 26, 18, 3, INK)


def icon_river(c, x, y):
    # A rooftop poking out of wavy flood water, red high-water mark.
    c.line(x + 8, y + 22, x + 24, y + 8, INK, 3)
    c.line(x + 24, y + 8, x + 40, y + 22, INK, 3)
    c.fill_rect(x + 13, y + 22, 22, 10, PAPER)
    c.rect_outline(x + 13, y + 22, 22, 10, INK, 2)
    c.fill_rect(x + 21, y + 26, 6, 6, RED)
    for wy in (y + 38, y + 46):
        for wx in range(x + 2, x + 48, 11):
            c.line(wx, wy + 2, wx + 5, wy - 2, INK, 2)
            c.line(wx + 5, wy - 2, wx + 10, wy + 2, INK, 2)
    c.line(x + 47, y + 30, x + 47, y + 12, RED, 2)
    c.line(x + 47, y + 12, x + 43, y + 17, RED, 2)
    c.line(x + 47, y + 12, x + 51, y + 17, RED, 2)


# ---------------------------------------------------------------------------
# Page content: the six stories of Friday 20 November 2026.
# ---------------------------------------------------------------------------

STORIES = [
    {
        "label": "POLITICS - SHENZHEN",
        "headline": "SHENZHEN SUMMIT",
        "body": ("Presidents Trump, Xi and Putin held their first "
                 "three-way meeting and issued a joint four-point "
                 "peace declaration."),
        "icon": icon_flags,
    },
    {
        "label": "CONFLICT - KYIV",
        "headline": "KYIV BRIDGES STRUCK",
        "body": ("Russian overnight strikes targeted Kyiv's bridges, "
                 "killing eight people; 28 more were hurt across "
                 "nine regions."),
        "icon": icon_bridge,
    },
    {
        "label": "CLIMATE - ANTALYA",
        "headline": "COP31 INTO OVERTIME",
        "body": ("The UN climate talks reached their final day with "
                 "no deal in sight; the latest draft dropped fossil "
                 "fuels and the summit looked set to spill into "
                 "the weekend."),
        "icon": icon_thermometer,
    },
    {
        "label": "TECH + BUSINESS",
        "headline": "ANTHROPIC SOARS ON DEBUT",
        "body": ("The Claude maker closed near $97, up 17% on its "
                 "$83 IPO price, as the S&P 500 fell a fifth day "
                 "and the Nikkei dropped 4.8%."),
        "icon": icon_chart,
    },
    {
        "label": "COURTS - THE HAGUE",
        "headline": "MYANMAR GENOCIDE RULING",
        "body": ("The World Court ruled Myanmar committed genocide "
                 "against the Rohingya - the first such finding "
                 "against a state - by a nine-to-six vote."),
        "icon": icon_gavel,
    },
    {
        "label": "DISASTER - FLORIDA",
        "headline": "FLORIDA RIVER TOPS RECORD",
        "body": ("The St. Johns River hit 18.66 feet, a foot above "
                 "its 1953 record, flooding the Space Coast; over "
                 "100 people were rescued."),
        "icon": icon_river,
    },
]

TICKER = [
    "US SENATE BLOCKS IRAN WAR-POWERS MEASURE, 51-48",
    "HOUTHI MISSILE DAMAGES RIYADH'S TALLEST TOWER",
    "KENYA DISCHARGES LAST EBOLA PATIENT, DAY 37",
]

PAGE = 1024
MARGIN = 40


def draw_panel(c, x, y, w, h, story):
    pad = 14
    inner_w = w - 2 * pad
    c.rect_outline(x, y, w, h, INK, 2)
    # Category label in red, icon in the top-right corner.
    draw_text(c, x + pad, y + 12, story["label"], 2, RED, bold=True)
    story["icon"](c, x + w - pad - 54, y + 8)
    # Headline, wrapped at display size.
    hy = y + 42
    for line in wrap_text(story["headline"], 3, inner_w):
        draw_text(c, x + pad, hy, line, 3, INK, bold=True)
        hy += 27
    # Red rule under the headline.
    c.fill_rect(x + pad, hy + 2, inner_w, 2, RED)
    # Summary body.
    by = hy + 14
    for line in wrap_text(story["body"], 2, inner_w):
        if by + GLYPH_H * 2 > y + h - 8:
            break
        draw_text(c, x + pad, by, line, 2, INK)
        by += 19


def build_front_page():
    c = Canvas(PAGE, PAGE, PAPER)

    # --- Masthead -------------------------------------------------------
    c.fill_rect(MARGIN, 30, PAGE - 2 * MARGIN, 3, INK)
    draw_text(c, MARGIN, 42, "FRIDAY", 2, INK, bold=True)
    draw_text_right(c, PAGE - MARGIN, 42, "20 NOVEMBER 2026", 2, INK,
                    bold=True)
    draw_text_centered(c, PAGE // 2, 44, "EST. 2026 * NO. 20", 1, FAINT)
    draw_text_centered(c, PAGE // 2, 68, "THE DAILY WIRE", 9, INK,
                       bold=True)
    # Double rule: one heavy stroke, one hairline.
    c.fill_rect(MARGIN, 140, PAGE - 2 * MARGIN, 4, INK)
    c.fill_rect(MARGIN, 148, PAGE - 2 * MARGIN, 1, INK)
    draw_text_centered(c, PAGE // 2, 158, "THE WORLD IN ONE PAGE", 2,
                       RED, bold=True)

    # --- Story grid: two columns, three rows ----------------------------
    grid_top = 190
    grid_bottom = 936
    gap_x = 16
    gap_y = 14
    col_w = (PAGE - 2 * MARGIN - gap_x) // 2
    row_h = (grid_bottom - grid_top - 2 * gap_y) // 3
    for i, story in enumerate(STORIES):
        col = i % 2
        row = i // 2
        px = MARGIN + col * (col_w + gap_x)
        py = grid_top + row * (row_h + gap_y)
        draw_panel(c, px, py, col_w, row_h, story)

    # --- Ticker: black band, white text, red bullets --------------------
    band_y = 946
    c.fill_rect(MARGIN, band_y, PAGE - 2 * MARGIN, 68, INK)
    ty = band_y + 8
    for item in TICKER:
        c.fill_rect(MARGIN + 16, ty + 3, 8, 8, RED)
        draw_text(c, MARGIN + 36, ty, item, 2, WHITE)
        ty += 19

    return c


if __name__ == "__main__":
    build_front_page().save("entry.png")

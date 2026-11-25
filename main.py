#!/usr/bin/env python3
"""THE WORLD TODAY - a dense one-image newspaper for Wednesday 25 November 2026.

Entry for make.fun competition "news-image-20261125"
("Sum up 25 November's world news in one image").

The program draws a complete newspaper front page - masthead, one hero
story, twelve news panels, a sports band and a wire ticker - onto a
1024 x 1024 canvas and writes it as a palette PNG named entry.png.

It uses only the Python standard library: the grader sandbox is a stock
python:3.13-slim image with nothing installed, so the page is rendered
with a small hand-drawn 5x7 bitmap font and the PNG is encoded directly
with zlib. There is no network access, no randomness and no clock use,
so two runs always write byte-identical output.
"""

import os
import struct
import zlib

# ---------------------------------------------------------------------------
# 5x7 bitmap font. Each glyph is seven rows of five bits; the most
# significant bit is the leftmost pixel. Text is rendered in upper case,
# which keeps the small sizes legible.
# ---------------------------------------------------------------------------

FONT = {
    "A": (0b01110, 0b10001, 0b10001, 0b11111, 0b10001, 0b10001, 0b10001),
    "B": (0b11110, 0b10001, 0b10001, 0b11110, 0b10001, 0b10001, 0b11110),
    "C": (0b01110, 0b10001, 0b10000, 0b10000, 0b10000, 0b10001, 0b01110),
    "D": (0b11100, 0b10010, 0b10001, 0b10001, 0b10001, 0b10010, 0b11100),
    "E": (0b11111, 0b10000, 0b10000, 0b11110, 0b10000, 0b10000, 0b11111),
    "F": (0b11111, 0b10000, 0b10000, 0b11110, 0b10000, 0b10000, 0b10000),
    "G": (0b01110, 0b10001, 0b10000, 0b10111, 0b10001, 0b10001, 0b01111),
    "H": (0b10001, 0b10001, 0b10001, 0b11111, 0b10001, 0b10001, 0b10001),
    "I": (0b01110, 0b00100, 0b00100, 0b00100, 0b00100, 0b00100, 0b01110),
    "J": (0b00111, 0b00010, 0b00010, 0b00010, 0b00010, 0b10010, 0b01100),
    "K": (0b10001, 0b10010, 0b10100, 0b11000, 0b10100, 0b10010, 0b10001),
    "L": (0b10000, 0b10000, 0b10000, 0b10000, 0b10000, 0b10000, 0b11111),
    "M": (0b10001, 0b11011, 0b10101, 0b10101, 0b10001, 0b10001, 0b10001),
    "N": (0b10001, 0b11001, 0b10101, 0b10011, 0b10001, 0b10001, 0b10001),
    "O": (0b01110, 0b10001, 0b10001, 0b10001, 0b10001, 0b10001, 0b01110),
    "P": (0b11110, 0b10001, 0b10001, 0b11110, 0b10000, 0b10000, 0b10000),
    "Q": (0b01110, 0b10001, 0b10001, 0b10001, 0b10101, 0b10010, 0b01101),
    "R": (0b11110, 0b10001, 0b10001, 0b11110, 0b10100, 0b10010, 0b10001),
    "S": (0b01111, 0b10000, 0b10000, 0b01110, 0b00001, 0b00001, 0b11110),
    "T": (0b11111, 0b00100, 0b00100, 0b00100, 0b00100, 0b00100, 0b00100),
    "U": (0b10001, 0b10001, 0b10001, 0b10001, 0b10001, 0b10001, 0b01110),
    "V": (0b10001, 0b10001, 0b10001, 0b10001, 0b10001, 0b01010, 0b00100),
    "W": (0b10001, 0b10001, 0b10001, 0b10101, 0b10101, 0b10101, 0b01010),
    "X": (0b10001, 0b01010, 0b00100, 0b00100, 0b01010, 0b10001, 0b10001),
    "Y": (0b10001, 0b10001, 0b01010, 0b00100, 0b00100, 0b00100, 0b00100),
    "Z": (0b11111, 0b00001, 0b00010, 0b00100, 0b01000, 0b10000, 0b11111),
    "0": (0b01110, 0b10001, 0b10011, 0b10101, 0b11001, 0b10001, 0b01110),
    "1": (0b00100, 0b01100, 0b00100, 0b00100, 0b00100, 0b00100, 0b01110),
    "2": (0b01110, 0b10001, 0b00001, 0b00010, 0b00100, 0b01000, 0b11111),
    "3": (0b11111, 0b00010, 0b00100, 0b00010, 0b00001, 0b10001, 0b01110),
    "4": (0b00010, 0b00110, 0b01010, 0b10010, 0b11111, 0b00010, 0b00010),
    "5": (0b11111, 0b10000, 0b11110, 0b00001, 0b00001, 0b10001, 0b01110),
    "6": (0b00110, 0b01000, 0b10000, 0b11110, 0b10001, 0b10001, 0b01110),
    "7": (0b11111, 0b00001, 0b00010, 0b00100, 0b01000, 0b01000, 0b01000),
    "8": (0b01110, 0b10001, 0b10001, 0b01110, 0b10001, 0b10001, 0b01110),
    "9": (0b01110, 0b10001, 0b10001, 0b01111, 0b00001, 0b00010, 0b01100),
    " ": (0, 0, 0, 0, 0, 0, 0),
    ".": (0, 0, 0, 0, 0, 0b01100, 0b01100),
    ",": (0, 0, 0, 0, 0b01100, 0b00100, 0b01000),
    "'": (0b00100, 0b00100, 0b01000, 0, 0, 0, 0),
    '"': (0b01010, 0b01010, 0, 0, 0, 0, 0),
    "-": (0, 0, 0, 0b01110, 0, 0, 0),
    ":": (0, 0b01100, 0b01100, 0, 0b01100, 0b01100, 0),
    ";": (0, 0b01100, 0b01100, 0, 0b01100, 0b00100, 0b01000),
    "!": (0b00100, 0b00100, 0b00100, 0b00100, 0b00100, 0, 0b00100),
    "?": (0b01110, 0b10001, 0b00001, 0b00110, 0b00100, 0, 0b00100),
    "%": (0b11001, 0b11010, 0b00010, 0b00100, 0b01000, 0b01011, 0b10011),
    "(": (0b00010, 0b00100, 0b01000, 0b01000, 0b01000, 0b00100, 0b00010),
    ")": (0b01000, 0b00100, 0b00010, 0b00010, 0b00010, 0b00100, 0b01000),
    "/": (0b00001, 0b00010, 0b00010, 0b00100, 0b01000, 0b01000, 0b10000),
    "&": (0b01100, 0b10010, 0b10100, 0b01000, 0b10101, 0b10010, 0b01101),
    "+": (0, 0b00100, 0b00100, 0b01110, 0b00100, 0b00100, 0),
    "*": (0, 0b00100, 0b10101, 0b01110, 0b10101, 0b00100, 0),
    "|": (0b00100, 0b00100, 0b00100, 0b00100, 0b00100, 0b00100, 0b00100),
    "=": (0, 0, 0b01110, 0, 0b01110, 0, 0),
    "$": (0b00100, 0b01111, 0b10100, 0b01110, 0b00101, 0b11110, 0b00100),
    "#": (0b01010, 0b01010, 0b11111, 0b01010, 0b11111, 0b01010, 0b01010),
}

GLYPH_W = 5
GLYPH_H = 7
ADVANCE = 6  # glyph width plus one column of tracking, in font units

# ---------------------------------------------------------------------------
# Palette. Indices are assigned in the fixed order the colours are listed,
# so the encoded PNG is identical on every run.
# ---------------------------------------------------------------------------

PAPER = 0
INK = 1
WHITE = 2
CREAM = 3
RED = 4
NAVY = 5
BORDER = 6
SOFT = 7
CAT_WORLD = 8
CAT_INDIA = 9
CAT_BUSINESS = 10
CAT_TECH = 11
GOLD = 12

PALETTE = [
    (248, 245, 236),  # PAPER - page background
    (20, 22, 26),     # INK - main text
    (255, 255, 255),  # WHITE - panel background / chip text
    (253, 240, 208),  # CREAM - hero band background
    (179, 32, 44),    # RED - accents, tags, sport
    (18, 49, 94),     # NAVY - sports band background
    (198, 190, 168),  # BORDER - panel outlines
    (56, 58, 64),     # SOFT - summary text
    (32, 80, 158),    # WORLD chip
    (216, 110, 24),   # INDIA chip
    (28, 122, 61),    # BUSINESS chip
    (106, 63, 160),   # TECH chip
    (212, 160, 32),   # GOLD - sports band accents
]

CATEGORY_COLORS = {
    "WORLD": CAT_WORLD,
    "INDIA": CAT_INDIA,
    "BUSINESS": CAT_BUSINESS,
    "TECH": CAT_TECH,
    "SPORT": RED,
}

PAGE_W = 1024
PAGE_H = 1024
MARGIN = 14
CONTENT_W = PAGE_W - 2 * MARGIN


# ---------------------------------------------------------------------------
# Canvas: a palette-index framebuffer with rectangle and text drawing.
# ---------------------------------------------------------------------------


class Canvas:
    def __init__(self, width, height, background):
        self.width = width
        self.height = height
        self.pixels = bytearray([background]) * (width * height)

    def fill_rect(self, x, y, w, h, color):
        if w <= 0 or h <= 0:
            return
        x0 = max(x, 0)
        y0 = max(y, 0)
        x1 = min(x + w, self.width)
        y1 = min(y + h, self.height)
        if x1 <= x0 or y1 <= y0:
            return
        row = bytes([color]) * (x1 - x0)
        for yy in range(y0, y1):
            start = yy * self.width + x0
            self.pixels[start:start + (x1 - x0)] = row

    def frame_rect(self, x, y, w, h, color, thickness=1):
        self.fill_rect(x, y, w, thickness, color)
        self.fill_rect(x, y + h - thickness, w, thickness, color)
        self.fill_rect(x, y, thickness, h, color)
        self.fill_rect(x + w - thickness, y, thickness, h, color)

    def draw_char(self, x, y, ch, scale, color, bold=False):
        glyph = FONT.get(ch)
        if glyph is None:
            glyph = FONT[" "]
        offsets = (0, max(1, scale // 2)) if bold else (0,)
        for row_idx, bits in enumerate(glyph):
            if bits == 0:
                continue
            for col_idx in range(GLYPH_W):
                if bits & (1 << (GLYPH_W - 1 - col_idx)):
                    for off in offsets:
                        self.fill_rect(
                            x + col_idx * scale + off,
                            y + row_idx * scale,
                            scale,
                            scale,
                            color,
                        )

    def draw_text(self, x, y, text, scale, color, bold=False):
        cx = x
        for ch in text:
            self.draw_char(cx, y, ch, scale, color, bold)
            cx += ADVANCE * scale
        return cx - x

    def text_width(self, text, scale):
        if not text:
            return 0
        return len(text) * ADVANCE * scale - scale


def wrap_text(text, max_chars):
    """Greedy word wrap for the monospace font; returns a list of lines."""
    lines = []
    current = ""
    for word in text.split(" "):
        if not word:
            continue
        if len(word) > max_chars:
            if current:
                lines.append(current)
                current = ""
            while len(word) > max_chars:
                lines.append(word[:max_chars])
                word = word[max_chars:]
            current = word
            continue
        trial = word if not current else current + " " + word
        if len(trial) <= max_chars:
            current = trial
        else:
            lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def draw_block(canvas, x, y, width, text, scale, color, line_h, max_lines,
               bold=False):
    """Draw wrapped text inside a box; returns the number of lines drawn."""
    max_chars = max(1, width // (ADVANCE * scale))
    lines = wrap_text(text, max_chars)
    drawn = 0
    for line in lines[:max_lines]:
        canvas.draw_text(x, y + drawn * line_h, line, scale, color, bold)
        drawn += 1
    return drawn


def draw_flow(canvas, x, y, line_widths, text, scale, color, line_h,
              bold=False):
    """Draw text flowing over lines whose widths may differ (first line can
    be shorter, e.g. when a label chip sits at its start)."""
    words = [w for w in text.split(" ") if w]
    line_idx = 0
    cx = x
    cy = y
    max_chars = max(1, line_widths[0] // (ADVANCE * scale))
    line_len = 0
    for word in words:
        need = len(word) if line_len == 0 else line_len + 1 + len(word)
        if need > max_chars and line_len > 0:
            line_idx += 1
            if line_idx >= len(line_widths):
                return
            cy = y + line_idx * line_h
            cx = x
            max_chars = max(1, line_widths[line_idx] // (ADVANCE * scale))
            line_len = 0
            need = len(word)
        if line_len > 0:
            cx += ADVANCE * scale
            line_len += 1
        canvas.draw_text(cx, cy, word, scale, color, bold)
        cx += len(word) * ADVANCE * scale
        line_len += len(word)


# ---------------------------------------------------------------------------
# PNG writer: colour type 3 (palette), filter 0 rows, zlib level 9.
# ---------------------------------------------------------------------------


def _chunk(tag, data):
    return (
        struct.pack(">I", len(data))
        + tag
        + data
        + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)
    )


def encode_png(canvas):
    raw = bytearray()
    width = canvas.width
    for yy in range(canvas.height):
        raw.append(0)
        start = yy * width
        raw += canvas.pixels[start:start + width]
    ihdr = struct.pack(">IIBBBBB", canvas.width, canvas.height, 8, 3, 0, 0, 0)
    plte = bytearray()
    for rgb in PALETTE:
        plte += bytes(rgb)
    png = bytearray()
    png += b"\x89PNG\r\n\x1a\n"
    png += _chunk(b"IHDR", ihdr)
    png += _chunk(b"PLTE", bytes(plte))
    png += _chunk(b"IDAT", zlib.compress(bytes(raw), 9))
    png += _chunk(b"IEND", b"")
    return bytes(png)


# ---------------------------------------------------------------------------
# The day's news: Wednesday 25 November 2026.
# ---------------------------------------------------------------------------

HERO_HEADLINE = (
    "US PROPOSES TARIFFS OF UP TO 25% ON INDIA AND 13 OTHER TRADING PARTNERS"
)
HERO_SUMMARY = (
    "THE TRUMP ADMINISTRATION PROPOSED NEW DUTIES ON 14 MAJOR TRADING "
    "PARTNERS OVER 'STRUCTURAL EXCESS CAPACITY'. CHINA FACES 20% STACKED "
    "ON FIRST-TERM DUTIES; RATES WILL NOT EXCEED TRADE-DEAL CAPS FOR "
    "CHINA, THE EU, JAPAN AND SOUTH KOREA. IMPLEMENTATION IS NOT "
    "EXPECTED BEFORE JANUARY, AFTER A PUBLIC HEARING."
)

PANELS = [
    ("WORLD",
     "CIA'S UNCLASSIFIED SYSTEMS BREACHED IN CYBERATTACK",
     "EXPOSED SOME UNCLASSIFIED DATA; NO CLASSIFIED DATA HIT."),
    ("TECH",
     "HUAWEI GUILTY OF CONSPIRACY TO STEAL TRADE SECRETS, US JURY FINDS",
     "A US JURY CONVICTED HUAWEI OF STEALING TRADE SECRETS AND BANK "
     "FRAUD."),
    ("WORLD",
     "CHINA LAUNCHES SHENZHOU-24 WITH FIRST PAKISTANI ASTRONAUT",
     "CARRIES THE FIRST FOREIGN VISITOR TO TIANGONG: A PAKISTANI "
     "SPECIALIST."),
    ("WORLD",
     "RIYADH'S TALLEST SKYSCRAPER HIT AGAIN IN 'TERRORIST ATTACK'",
     "11 INJURED IN A SECOND HOUTHI HIT ON THE LANDMARK IN UNDER A "
     "WEEK."),
    ("WORLD",
     "ISRAEL'S EISENKOT CLINCHES FIRST COALITION PACT",
     "YASHAR SIGNED A FIRST PACT WITH A RIGHT-WING OPPOSITION PARTY."),
    ("TECH",
     "NVIDIA REINSTATES CEO JENSEN HUANG AFTER TRUMP ASSURANCE",
     "TRUMP AND VANCE ASSURED THE BOARD HUANG POSED NO SECURITY RISK."),
    ("BUSINESS",
     "SENSEX SURGES 1,502 POINTS AS IT STOCKS RALLY UP TO 5%",
     "NIFTY BACK ABOVE 25,800; TCS, INFOSYS, WIPRO LED, FMCG AND BANKS "
     "FIRM."),
    ("BUSINESS",
     "TATA STEEL PROPOSES RS 32,266 CRORE APL APOLLO DEAL",
     "TO BUY A 52.38% STAKE IN APL APOLLO TUBES IN A TOP STEEL-SECTOR "
     "DEAL."),
    ("INDIA",
     "INDIA-NEPAL: RS 15,000 CRORE PACKAGE, FIRST AYODHYA-JANAKPUR TRAIN",
     "MODI AND PM SHAH FLAG OFF FIRST AYODHYA-JANAKPUR TRAIN."),
    ("INDIA",
     "CABINET CLEARS NEW SILCHAR AIRPORT, RS 11,000 CRORE EQUIPMENT SCHEME",
     "GREENFIELD AIRPORT AT DOLOO, SILCHAR; BOOST FOR EQUIPMENT "
     "MAKERS."),
    ("WORLD",
     "SHEIKH HASINA SETS DECEMBER 16 RETURN DATE TO DHAKA",
     "SHE ASKED DHAKA TO ARRANGE HER RETURN; INDIA KEEPS EXTRADITION "
     "SEPARATE."),
    ("WORLD",
     "BANGLADESH GARMENT WORKERS WIN 36% PAY HIKE",
     "36% RISE FROM JANUARY AFTER WEEKS OF PROTESTS; UNIONS MAY STRIKE "
     "ON."),
]

SPORTS = [
    "SOORYAVANSHI 204 OFF 53 - FASTEST LIST A TON, 28 BALLS, INDIA A V UAE",
    "GUKESH HOLDS SINDAROV TO A DRAW IN WORLD CHESS TITLE GAME 1 IN GENEVA",
    "SENEGAL RESTORED AS AFCON CHAMPIONS AS CAS OVERTURNS MOROCCO RULING",
    "REAL MADRID THRASH PSV 5-1; ARSENAL 1-1 DORTMUND; MAN CITY 2-2 NAPOLI",
    "ENGLAND BEAT AUSTRALIA BY 8 WICKETS IN 2ND T20I TO LEVEL SERIES 1-1",
    "INDIA WOMEN ROUT CHINA 6-2 IN HOCKEY - DEEPIKA HAT-TRICK, NOW WORLD NO. 5",
    "EAST BENGAL SEAL FIRST AFC CHAMPIONS LEAGUE TWO WIN, 1-0 V AL HUSSEIN",
    "BEN STOKES ENTERS THE IPL 2027 AUCTION, SET FOR DECEMBER 16 IN GOA",
]

TICKER = [
    "US CONSUMER CONFIDENCE JUMPS TO 103.3",
    "IRAN RULES OUT US TALKS UNTIL 7 CONDITIONS MET",
    "TRUMP GIVES GIULIANI THE MEDAL OF FREEDOM",
    "AUSTRALIA FINES PLATFORMS UP TO 5% OF REVENUE",
    "UN: HIV INFECTIONS MAY RISE FROM 2027",
    "LANDMINE CASUALTIES HIT 5-YEAR HIGH OF 7,000",
    "HONG KONG FIRE SURVIVORS RETURN AFTER A YEAR",
    "COLOMBIA BOMB ATTACK INJURES 23",
    "DENMARK BANS HEADSCARVES FOR PROSECUTORS",
    "NTPC CANCELS RECRUITMENT EXAM RESULTS",
    "IITS TO ADD 6,000 SEATS IN AI, SPACE TECH",
    "DALAI LAMA OFFICE GETS A LUTYENS' DELHI BUNGALOW",
    "INDIA WINS VISITORS' LION AT VENICE BIENNALE",
    "'RAMAYANA' IN OSCARS VFX TOP-20 RACE",
    "JIO SCRAPS DAILY DATA CAP ON SELECT PLANS",
    "PT USHA STEPS OUT OF IOA PRESIDENT RACE",
    "PRIYANSH ARYA'S 181 - HIGHEST INDIAN T20 SCORE",
    "DELHI AIR 'VERY POOR' IN POCKETS; AQI 224",
    "MAGNITUDE 6.0 QUAKE STRIKES SOUTH PACIFIC",
]

# ---------------------------------------------------------------------------
# Page layout.
# ---------------------------------------------------------------------------


def build_page():
    page = Canvas(PAGE_W, PAGE_H, PAPER)

    # Masthead ------------------------------------------------------------
    title = "THE WORLD TODAY"
    title_w = page.text_width(title, 6)
    page.draw_text((PAGE_W - title_w) // 2, 10, title, 6, INK, bold=True)
    dateline = "WEDNESDAY, 25 NOVEMBER 2026"
    dateline_w = page.text_width(dateline, 2)
    page.draw_text((PAGE_W - dateline_w) // 2, 58, dateline, 2, INK, bold=True)
    page.draw_text(MARGIN, 58, "VOL. 1 - NO. 330", 2, SOFT)
    right_note = "ONE IMAGE - ALL THE NEWS"
    right_w = page.text_width(right_note, 2)
    page.draw_text(PAGE_W - MARGIN - right_w, 58, right_note, 2, SOFT)
    page.fill_rect(MARGIN, 80, CONTENT_W, 1, INK)
    page.fill_rect(MARGIN, 84, CONTENT_W, 4, INK)

    # Hero story ----------------------------------------------------------
    hero_y = 92
    page.fill_rect(MARGIN, hero_y, CONTENT_W, 156, CREAM)
    page.frame_rect(MARGIN, hero_y, CONTENT_W, 156, INK, 1)
    page.fill_rect(MARGIN + 10, hero_y + 10, 120, 20, RED)
    page.draw_text(MARGIN + 16, hero_y + 13, "TOP STORY", 2, WHITE, bold=True)
    page.draw_text(MARGIN + 142, hero_y + 13, "WASHINGTON - TRADE WAR", 2, RED,
                   bold=True)
    draw_block(page, MARGIN + 14, hero_y + 38, CONTENT_W - 28,
               HERO_HEADLINE, 3, INK, 26, 2, bold=True)
    draw_block(page, MARGIN + 14, hero_y + 92, CONTENT_W - 28,
               HERO_SUMMARY, 2, SOFT, 15, 4)

    # News panels: 3 columns x 4 rows --------------------------------------
    grid_y = 254
    panel_w = 330
    panel_h = 124
    pitch_x = 338
    pitch_y = 132
    for idx, (category, headline, summary) in enumerate(PANELS):
        col = idx % 3
        row = idx // 3
        px = MARGIN + col * pitch_x
        py = grid_y + row * pitch_y
        page.fill_rect(px, py, panel_w, panel_h, WHITE)
        page.frame_rect(px, py, panel_w, panel_h, BORDER, 1)
        chip_color = CATEGORY_COLORS[category]
        chip_w = page.text_width(category, 2) + 12
        page.fill_rect(px + 8, py + 6, chip_w, 18, chip_color)
        page.draw_text(px + 14, py + 8, category, 2, WHITE, bold=True)
        draw_block(page, px + 8, py + 28, panel_w - 16, headline, 2, INK,
                   16, 3, bold=True)
        draw_block(page, px + 8, py + 77, panel_w - 16, summary, 2, SOFT,
                   15, 3)

    # Sports band -----------------------------------------------------------
    sports_y = 782
    page.fill_rect(MARGIN, sports_y, CONTENT_W, 166, NAVY)
    page.draw_text(MARGIN + 12, sports_y + 8, "SPORT", 2, WHITE, bold=True)
    sport_note = "RESULTS - RECORDS - FIXTURES"
    note_w = page.text_width(sport_note, 2)
    page.draw_text(PAGE_W - MARGIN - 12 - note_w, sports_y + 8, sport_note,
                   2, GOLD)
    page.fill_rect(MARGIN + 12, sports_y + 28, CONTENT_W - 24, 2, GOLD)
    item_y = sports_y + 38
    for idx, item in enumerate(SPORTS):
        col = idx % 2
        row = idx // 2
        ix = MARGIN + 12 + col * 506
        iy = item_y + row * 31
        page.fill_rect(ix, iy + 3, 8, 8, RED)
        draw_block(page, ix + 16, iy, 474, item, 2, WHITE, 15, 2)

    # Wire ticker -----------------------------------------------------------
    ticker_y = 956
    page.fill_rect(MARGIN, ticker_y, CONTENT_W, 64, INK)
    page.fill_rect(MARGIN + 4, ticker_y + 2, 74, 11, RED)
    flow_text = "LATEST WIRE /// " + " /// ".join(TICKER)
    draw_flow(page, MARGIN + 8, ticker_y + 4, [CONTENT_W - 16] * 6,
              flow_text, 1, PAPER, 10, bold=True)

    return page


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output"
    os.makedirs(out_dir, exist_ok=True)
    page = build_page()
    data = encode_png(page)
    out_path = os.path.join(out_dir, "entry.png")
    with open(out_path, "wb") as handle:
        handle.write(data)


if __name__ == "__main__":
    main()

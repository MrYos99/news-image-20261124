#!/usr/bin/env python3
"""Render the 24 November 2026 world-news front page, 1024x1024.

Fresh code written for the news-image-20261124 bounty. Layout follows the
locked rank-1 pattern: giant serif masthead, UTC strip, numbers strip, 3 big
lead cards with red fact banners, 10 small icon cards, numbered world map,
two-column ALSO list, DATE CHECK with exclusions, badge legend footer.
All drawings are code-drawn with Pillow; no photos, no third-party art.
"""
import math
import os
from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
MARGIN = 38
CONTENT_W = W - 2 * MARGIN  # 948

PAPER = (247, 242, 229)
INK = (26, 25, 23)
INK_SOFT = (74, 70, 64)
RED = (179, 38, 30)
RED_DARK = (140, 28, 22)
RULE = (26, 25, 23)
SEA = (205, 223, 222)
LAND = (233, 224, 192)
LAND_LINE = (168, 156, 120)
GRID = (255, 255, 255)
CARD_BG = (252, 249, 240)
ART_SKY = (186, 214, 226)

# Region colours, used identically in cards, list and map legend.
REGION_COLORS = {
    "Europe": (29, 78, 216),
    "Asia": (124, 58, 237),
    "Middle East": (190, 24, 93),
    "Africa": (146, 64, 14),
    "N. America": (220, 38, 38),
    "S. America": (234, 88, 12),
    "Oceania": (14, 116, 144),
    "World": (51, 65, 85),
    "Space": (51, 65, 85),
}
BADGE_STYLE = {
    "CONFIRMED": ((22, 101, 52), (220, 240, 224)),
    "OFFICIAL": ((146, 64, 14), (250, 235, 210)),
    "REPORTED": ((100, 100, 100), (238, 238, 238)),
}

FONT_DIR = "/usr/share/fonts/truetype/liberation"


def font(name, size):
    return ImageFont.truetype(os.path.join(FONT_DIR, name), size)


SERIF_B = lambda s: font("LiberationSerif-Bold.ttf", s)
SERIF = lambda s: font("LiberationSerif-Regular.ttf", s)
SERIF_I = lambda s: font("LiberationSerif-Italic.ttf", s)
SANS = lambda s: font("LiberationSans-Regular.ttf", s)
SANS_B = lambda s: font("LiberationSans-Bold.ttf", s)


def wrap(draw, text, fnt, max_w):
    """Greedy word wrap; returns a list of lines that fit max_w."""
    words = text.split()
    lines, cur = [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if draw.textlength(trial, font=fnt) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def text(draw, xy, s, fnt, fill=INK, anchor="la"):
    draw.text(xy, s, font=fnt, fill=fill, anchor=anchor)


def draw_badge(draw, x, y, label):
    """Small verification badge; returns its width."""
    fnt = SANS_B(9)
    w = int(draw.textlength(label, font=fnt)) + 10
    h = 13
    fg, bg = BADGE_STYLE[label]
    draw.rounded_rectangle([x, y, x + w, y + h], radius=3, fill=bg, outline=fg, width=1)
    draw.text((x + 5, y + 2), label, font=fnt, fill=fg)
    return w


# ---------------------------------------------------------------- stories
# (num, region, place, headline, detail, source, badge, lat, lon, art)
LEADS = [
    (1, "Middle East", "Strait of Hormuz",
     "Three tankers hit by mines off Hormuz",
     "Iran's Revolutionary Guard Navy says two tankers struck naval mines and "
     "fires broke out aboard all three vessels.",
     "Anadolu", "REPORTED", 26.5, 56.5, "tankers"),
    (2, "N. America", "New York",
     "AI rally fizzles as Nvidia slides 6%",
     "A day after Huang's return sent Nvidia up 31%, the chipmaker fell 6% and "
     "Anthropic dropped below its $83 IPO price.",
     "AP, Investopedia", "CONFIRMED", 40.7, -74.0, "chart"),
    (3, "Europe", "Zaporizhzhia, Ukraine",
     "Russian strike hits apartment block in Zaporizhzhia",
     "A guided aerial bomb hit a five-storey building near a Dnipro bridge: "
     "2 killed, 44 wounded, among them four children.",
     "AP, Reuters", "CONFIRMED", 47.8, 35.2, "building"),
]

SMALL = [
    (4, "Middle East", "Gaza",
     "Israel kills Hamas security chief Naeem Abu Nahel",
     "A drone missile hit his tent west of Gaza City; at least six other "
     "Palestinians were killed the same day.",
     "Reuters", "CONFIRMED", 31.5, 34.5, "target"),
    (5, "Europe", "Estonia",
     "Russia threatens “open war” with Estonia",
     "Moscow accuses Tallinn of letting Ukraine launch attacks from its soil, "
     "days after Estonia closed its land border with Russia.",
     "Democracy Now", "REPORTED", 59.4, 24.7, "flag"),
    (6, "Africa", "Khartoum, Sudan",
     "RSF drones hit Khartoum as power grid nears collapse",
     "The army says it intercepted drones over the capital; the airport and a "
     "UN facility were hit, at least 4 killed.",
     "Democracy Now", "REPORTED", 15.6, 32.5, "drone"),
    (7, "Asia", "Bangladesh",
     "Garment workers clash with police as pay protests shut factories",
     "Police fire tear gas and stun grenades in Gazipur, Savar and Ashulia; "
     "production halts at 481 factories in a wage dispute.",
     "Reuters", "CONFIRMED", 24.0, 90.4, "factory"),
    (8, "World", "Zurich",
     "2031 Women's World Cup goes to the US, Mexico, Costa Rica and Jamaica",
     "FIFA confirms at a virtual congress; the 2031 edition is the first with "
     "48 teams and 104 matches. The UK gets 2035.",
     "Anadolu", "OFFICIAL", 47.4, 8.5, "trophy"),
    (9, "Oceania", "Solomon Islands",
     "Solomons scraps China security pact in “massive win” for Australia",
     "Honiara moves to end the contentious security agreement with Beijing.",
     "ABC News", "CONFIRMED", -9.4, 160.0, "island"),
    (10, "Space", "Mercury",
     "BepiColombo reaches Mercury after eight years",
     "The joint ESA–JAXA spacecraft arrives despite a propulsion glitch.",
     "CBC", "OFFICIAL", None, None, "planet"),
    (11, "Europe", "United Kingdom",
     "UK records its deadliest heat year: 5,258 deaths",
     "The UK Health Security Agency says 2026 heat deaths beat the 2022 "
     "record — the highest since records began in 2016.",
     "Reuters", "OFFICIAL", 51.5, -0.1, "sun"),
    (12, "Africa", "Senegal",
     "CAS restores Senegal as Africa Cup champions",
     "The court reverses CAF's decision to overturn Senegal's 1–0 final win "
     "over Morocco in the 2025 Africa Cup of Nations final.",
     "AP", "OFFICIAL", 14.7, -17.4, "cup"),
    (13, "Asia", "East Sea",
     "South Korea scrambles jets as Russian planes enter defence zone",
     "Fighter jets launched early Tuesday after several Russian military "
     "aircraft entered the air defence identification zone over the East Sea.",
     "Yonhap", "REPORTED", 38.5, 129.5, "jet"),
]

ALSO = [
    (14, "Middle East", "Yemen", "Houthis say Saudi strikes killed 41 civilians in a day", "Democracy Now"),
    (15, "Middle East", "Gaza", "Oxfam: assault turned Gaza into a “toxic wasteland”", "Democracy Now"),
    (16, "Middle East", "Gaza", "Drone strike kills three at a police post in al-Mawasi", "Anadolu"),
    (17, "Europe", "Ukraine", "UNICEF: about three children a day killed or hurt", "Democracy Now"),
    (18, "Europe", "Ukraine", "Kyiv: Libya ship attack was self-defence", "Reuters"),
    (19, "Europe", "Norway", "Norway and Ukraine expand DESNA defences", "Reuters"),
    (20, "Europe", "Germany", "53% oppose military aid to Ukraine", "Reuters"),
    (21, "Europe", "France", "Nahel Merzouk shooter faces murder trial", "Reuters"),
    (22, "Europe", "EU", "New Russia sanctions hit banks and crypto", "Anadolu"),
    (23, "N. America", "US", "Envoy doubts Israel military aid ends this year", "Reuters"),
    (24, "Middle East", "Iraq", "PM al-Zaidi takes on militias and Kurds", "Reuters"),
    (25, "Asia", "Armenia", "Pashinyan starts TRIPP corridor work", "Anadolu"),
    (26, "Asia", "India", "BJP and Akali Dal reunite for Punjab polls", "The Hindu"),
    (27, "Asia", "India", "Thirupparankundram lamp row: BJP chief arrested en route", "The Hindu"),
    (28, "Asia", "China", "Export controls on 40 Japanese entities as tensions rise", "TaxTMI"),
    (29, "Asia", "Japan", "Japan and Australia agree stronger defence ties", "Yeni Şafak"),
    (30, "Asia", "North Korea", "Kim Yo Jong warns over Swiss office closure", "KCNA"),
    (31, "Middle East", "UAE", "Bus crash kills 13 and injures 14 in Ras Al Khaimah", "Gulf News"),
    (32, "Asia", "Vietnam", "Hanoi hot-pot blast kills 7, injures 9", "VnExpress"),
    (33, "Europe", "Türkiye", "Helicopter crash kills five crew in Eskişehir", "AP"),
    (34, "S. America", "Colombia", "Gunmen take 25 hostage in a Cartagena supermarket", "Al Jazeera"),
    (35, "Europe", "Football", "Real Madrid 5–1 PSV, City 2–2 Napoli", "UEFA"),
]

UTC_STRIP = [
    ("09:10", "Hormuz: 3 tankers hit by mines"),
    ("11:10", "EU to overhaul climate summits"),
    ("12:56", "Huang back at Nvidia"),
    ("15:44", "Dragonfly gets its eyes"),
    ("17:27", "Nasdaq falls 1.5%"),
    ("18:23", "BepiColombo reaches Mercury"),
    ("21:19", "S&P closes down 0.5%"),
]

NUMBERS = [
    ("3", "tankers hit by mines"),
    ("700,000+", "Russian soldiers dead since 2022"),
    ("5,258", "UK heat deaths, a record"),
    ("−6%", "Nvidia on Tuesday"),
    ("$4.71B", "Bitcoin ETF outflows in Nov"),
    ("48", "teams at the 2031 World Cup"),
]

REGION_COUNTS = [
    ("Europe", 11), ("Asia", 9), ("Middle East", 7), ("Africa", 2),
    ("N. America", 2), ("S. America", 1), ("Oceania", 1), ("World + space", 2),
]


# ---------------------------------------------------------------- map data
# Simplified continent outlines, hand-written lon/lat pairs for a small
# equirectangular map (top latitude 83, bottom -58, Antarctica skipped).
NORTH_AMERICA = [(-168, 66), (-155, 58), (-140, 60), (-130, 55), (-125, 49),
                 (-124, 40), (-120, 34), (-114, 28), (-110, 23), (-105, 20),
                 (-97, 16), (-92, 15), (-86, 13), (-83, 9), (-79, 9),
                 (-82, 11), (-88, 14), (-94, 17), (-97, 19), (-96, 21),
                 (-90, 21), (-86, 25), (-83, 28), (-81, 31), (-76, 35),
                 (-74, 39), (-70, 42), (-66, 45), (-60, 47), (-55, 52),
                 (-60, 55), (-65, 60), (-70, 62), (-78, 62), (-85, 66),
                 (-92, 66), (-95, 69), (-105, 68), (-115, 69), (-125, 70),
                 (-140, 70), (-155, 71), (-165, 68), (-168, 66)]
GREENLAND = [(-58, 64), (-45, 60), (-40, 65), (-32, 68), (-22, 70),
             (-25, 76), (-35, 80), (-50, 79), (-58, 76), (-60, 72), (-58, 64)]
SOUTH_AMERICA = [(-80, 9), (-75, 11), (-68, 12), (-62, 10), (-55, 6),
                 (-52, 4), (-50, 0), (-44, -3), (-35, -8), (-38, -15),
                 (-40, -22), (-48, -28), (-55, -35), (-62, -41), (-66, -47),
                 (-69, -52), (-71, -54), (-73, -50), (-73, -40), (-72, -30),
                 (-70, -20), (-75, -15), (-80, -6), (-81, 0), (-80, 9)]
AFRICA = [(-6, 35), (0, 36), (10, 37), (20, 32), (30, 31), (35, 28),
          (37, 22), (39, 18), (43, 12), (48, 11), (51, 10), (46, 5),
          (42, 0), (40, -5), (40, -12), (36, -18), (33, -26), (28, -33),
          (20, -35), (16, -28), (12, -18), (9, -2), (9, 4), (4, 6),
          (-8, 5), (-13, 8), (-17, 12), (-17, 16), (-16, 21), (-15, 25),
          (-10, 30), (-6, 35)]
EURASIA = [(-10, 36), (-9, 43), (-2, 48), (0, 50), (5, 53), (8, 57),
           (10, 59), (18, 56), (21, 55), (24, 59), (28, 60), (32, 63),
           (38, 66), (45, 68), (52, 69), (60, 69), (68, 71), (75, 73),
           (85, 74), (95, 76), (105, 77), (115, 74), (125, 73), (135, 72),
           (145, 72), (155, 70), (165, 68), (173, 66), (178, 65),
           (178, 62), (170, 60), (162, 56), (158, 52), (150, 59),
           (142, 55), (140, 50), (136, 44), (130, 42), (127, 40),
           (122, 38), (120, 32), (118, 25), (110, 20), (108, 18),
           (105, 10), (103, 7), (100, 7), (98, 10), (95, 15), (92, 21),
           (89, 22), (86, 20), (82, 17), (80, 13), (77, 8), (75, 11),
           (72, 20), (68, 23), (65, 25), (60, 25), (57, 26), (54, 27),
           (52, 28), (50, 29), (48, 30), (44, 29), (40, 28), (38, 25),
           (36, 22), (35, 20), (39, 21), (43, 17), (45, 14), (48, 14),
           (52, 14), (55, 17), (58, 20), (59, 22), (57, 25), (54, 26),
           (51, 27), (48, 29), (45, 29), (42, 28), (39, 24), (36, 21),
           (34, 27), (33, 31), (30, 36), (26, 38), (23, 36), (20, 39),
           (18, 40), (15, 44), (12, 44), (8, 44), (3, 43), (0, 40),
           (-2, 37), (-6, 36), (-9, 37), (-10, 36)]
AUSTRALIA = [(113, -22), (114, -30), (115, -35), (120, -34), (125, -33),
             (130, -32), (132, -32), (135, -35), (138, -35), (140, -38),
             (145, -38), (150, -37), (153, -32), (153, -27), (150, -23),
             (146, -19), (142, -15), (142, -11), (137, -12), (135, -15),
             (132, -12), (130, -13), (126, -14), (122, -17), (118, -20),
             (113, -22)]
UK = [(-5, 50), (-3, 53), (-5, 56), (-3, 58), (-1, 57), (0, 53),
      (-1, 51), (-5, 50)]
JAPAN = [(130, 31), (132, 33), (135, 34), (137, 35), (139, 37), (140, 39),
         (141, 41), (142, 44), (144, 44), (143, 42), (141, 39), (139, 36),
         (136, 34), (133, 34), (131, 33), (130, 31)]
NEW_ZEALAND = [(167, -45), (170, -43), (173, -41), (175, -38), (177, -38),
               (175, -40), (172, -42), (168, -44), (167, -45)]
CONTINENTS = [NORTH_AMERICA, GREENLAND, SOUTH_AMERICA, AFRICA, EURASIA,
              AUSTRALIA, UK, JAPAN, NEW_ZEALAND]

MAP_LAT_TOP, MAP_LAT_BOT = 83.0, -58.0


def lonlat_to_xy(lon, lat, x0, y0, w, h):
    x = x0 + (lon + 180.0) / 360.0 * w
    y = y0 + (MAP_LAT_TOP - lat) / (MAP_LAT_TOP - MAP_LAT_BOT) * h
    return x, y


def segments_cross(p1, p2, p3, p4):
    def orient(a, b, c):
        v = (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])
        return 0 if abs(v) < 1e-9 else (1 if v > 0 else -1)
    o1, o2, o3, o4 = (orient(p1, p2, p3), orient(p1, p2, p4),
                      orient(p3, p4, p1), orient(p3, p4, p2))
    return o1 != o2 and o3 != o4


def place_badges(points, x0, y0, w, h, r=7):
    """Search badge slots around each point: growing radii x 12 angles.
    Points and slots are in absolute page coordinates; slots are kept
    inside the map panel (x0, y0, w, h). A slot is refused if it overlaps
    a placed badge or its leader crosses another leader.
    Returns {num: (bx, by)} badge centres."""
    placed = {}
    leaders = []
    for num, (px, py) in points:
        chosen = None
        for radius in (11, 17, 24, 31, 38):
            for k in range(12):
                ang = math.radians(k * 30 + 15)
                bx = px + radius * math.cos(ang)
                by = py + radius * math.sin(ang)
                if bx < x0 + r + 2 or bx > x0 + w - r - 2:
                    continue
                if by < y0 + r + 2 or by > y0 + h - r - 2:
                    continue
                if any((bx - ox) ** 2 + (by - oy) ** 2 < (2 * r + 4) ** 2
                       for ox, oy in placed.values()):
                    continue
                if any(segments_cross((px, py), (bx, by), a, b)
                       for a, b in leaders):
                    continue
                chosen = (bx, by)
                break
            if chosen:
                break
        if chosen is None:
            chosen = (min(max(px + 11, x0 + r + 2), x0 + w - r - 2),
                      min(max(py - 11, y0 + r + 2), y0 + h - r - 2))
        placed[num] = chosen
        leaders.append(((px, py), chosen))
    return placed, leaders


def draw_map(draw, x0, y0, w, h, stories):
    """World map panel with numbered pins and a region-count legend."""
    draw.rectangle([x0, y0, x0 + w, y0 + h], fill=SEA, outline=INK, width=1)
    for gx in range(-150, 181, 30):
        gx_px = x0 + (gx + 180) / 360.0 * w
        draw.line([(gx_px, y0), (gx_px, y0 + h)], fill=(255, 255, 255), width=1)
    for gy in range(-30, 61, 30):
        gy_px = y0 + (MAP_LAT_TOP - gy) / (MAP_LAT_TOP - MAP_LAT_BOT) * h
        draw.line([(x0, gy_px), (x0 + w, gy_px)], fill=(255, 255, 255), width=1)
    for poly in CONTINENTS:
        pts = [lonlat_to_xy(lon, lat, x0, y0, w, h) for lon, lat in poly]
        draw.polygon(pts, fill=LAND, outline=LAND_LINE)
    pts = []
    for num, region, place, _h, _d, _s, _b, lat, lon, _a in stories:
        if lat is None:
            continue
        px, py = lonlat_to_xy(lon, lat, x0, y0, w, h)
        pts.append((num, (px, py)))
    placed, leaders = place_badges(pts, x0, y0, w, h)
    for (px, py), (bx, by) in leaders:
        draw.line([(px, py), (bx, by)], fill=INK_SOFT, width=1)
    for num, (px, py) in pts:
        draw.ellipse([px - 2.5, py - 2.5, px + 2.5, py + 2.5],
                     fill=INK, outline=(255, 255, 255), width=1)
    fnt = SANS_B(9)
    for num, (bx, by) in placed.items():
        region = next(s[1] for s in stories if s[0] == num)
        col = REGION_COLORS[region]
        draw.ellipse([bx - 7, by - 7, bx + 7, by + 7], fill=col,
                     outline=(255, 255, 255), width=1)
        tw = draw.textlength(str(num), font=fnt)
        draw.text((bx - tw / 2, by - 5), str(num), font=fnt, fill=(255, 255, 255))
    return placed


# ---------------------------------------------------------------- art
def art_banner(draw, x, y, w, label):
    """Red fact banner across the top of an illustration."""
    fnt = SANS_B(13)
    tw = draw.textlength(label, font=fnt)
    bw = tw + 18
    draw.polygon([(x, y), (x + bw, y), (x + bw - 8, y + 20), (x, y + 20)],
                 fill=RED)
    draw.text((x + 9, y + 3), label, font=fnt, fill=(255, 255, 255))


def art_place(draw, x, y, label):
    """Place label inside the art, bottom left, white on dark strip."""
    fnt = SANS_B(11)
    tw = draw.textlength(label, font=fnt)
    draw.rectangle([x, y, x + tw + 12, y + 17], fill=INK)
    draw.text((x + 6, y + 2), label, font=fnt, fill=(255, 255, 255))


def draw_tanker(draw, x, y, w, h, color):
    """Tanker silhouette: hull, deck, funnel, containers."""
    draw.polygon([(x, y + h * 0.55), (x + w, y + h * 0.55), (x + w - 8, y + h),
                  (x + 8, y + h)], fill=color)
    draw.rectangle([x + w * 0.30, y + h * 0.30, x + w * 0.42, y + h * 0.55],
                   fill=color)
    draw.rectangle([x + w * 0.50, y + h * 0.42, x + w * 0.56, y + h * 0.55],
                   fill=color)
    draw.rectangle([x + w * 0.62, y + h * 0.18, x + w * 0.68, y + h * 0.55],
                   fill=color)


def draw_mine(draw, cx, cy, r):
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=INK)
    for k in range(8):
        ang = math.radians(k * 45)
        x2 = cx + (r + 5) * math.cos(ang)
        y2 = cy + (r + 5) * math.sin(ang)
        draw.line([(cx, cy), (x2, y2)], fill=INK, width=2)


def draw_smoke(draw, x, y, s):
    for dx, dy, r in [(0, 0, 9), (10, -8, 12), (22, -14, 10), (32, -22, 8)]:
        draw.ellipse([x + dx - r, y + dy - r, x + dx + r, y + dy + r],
                     fill=(120, 120, 118))


def draw_lead_art(draw, x, y, w, h, kind):
    """Code-drawn illustration for a lead card."""
    draw.rectangle([x, y, x + w, y + h], fill=ART_SKY)
    if kind == "tankers":
        draw.rectangle([x, y + h * 0.62, x + w, y + h], fill=(58, 96, 122))
        for i in range(4):
            wy = y + h * 0.66 + i * 9
            draw.line([(x, wy), (x + w, wy)], fill=(140, 175, 195), width=1)
        draw_tanker(draw, x + 18, y + h * 0.42, 110, 34, (52, 52, 50))
        draw_tanker(draw, x + 165, y + h * 0.50, 105, 30, (70, 62, 55))
        draw_smoke(draw, x + 40, y + 34, 1)
        draw_smoke(draw, x + 190, y + 42, 1)
        draw.polygon([(x + 52, y + 22), (x + 58, y + 34), (x + 62, y + 22),
                      (x + 68, y + 34), (x + 60, y + 40), (x + 52, y + 40)],
                     fill=(230, 120, 30))
        draw_mine(draw, x + 140, y + h * 0.78, 7)
        draw_mine(draw, x + 250, y + h * 0.85, 6)
        draw_mine(draw, x + 285, y + h * 0.72, 5)
    elif kind == "chart":
        draw.rectangle([x, y, x + w, y + h], fill=(238, 240, 236))
        for gy in range(5):
            gy_y = y + 14 + gy * (h - 28) // 4
            draw.line([(x + 8, gy_y), (x + w - 8, gy_y)], fill=(210, 212, 208),
                      width=1)
        pts = [(x + 12, y + 30), (x + 55, y + 22), (x + 95, y + 34),
               (x + 135, y + 26), (x + 175, y + 48), (x + 215, y + 62),
               (x + 255, y + 88), (x + w - 12, y + 104)]
        draw.line(pts, fill=RED, width=4, joint="curve")
        for px, py in pts:
            draw.ellipse([px - 3, py - 3, px + 3, py + 3], fill=RED)
        draw.rectangle([x + w - 78, y + 12, x + w - 18, y + 44],
                       fill=(30, 30, 32), outline=(255, 255, 255), width=1)
        for i in range(3):
            draw.line([(x + w - 70, y + 20 + i * 8), (x + w - 26, y + 20 + i * 8)],
                      fill=(120, 200, 120), width=2)
    elif kind == "building":
        draw.rectangle([x, y, x + w, y + h], fill=(196, 200, 205))
        draw.rectangle([x + 30, y + 18, x + 150, y + h], fill=(150, 140, 128))
        draw.rectangle([x + 170, y + 45, x + 260, y + h], fill=(128, 120, 110))
        for r in range(5):
            for c in range(4):
                wx = x + 44 + c * 28
                wy = y + 30 + r * 22
                if (r, c) in ((1, 1), (2, 2), (3, 0)):
                    draw.rectangle([wx, wy, wx + 16, wy + 13], fill=(40, 38, 34))
                else:
                    draw.rectangle([wx, wy, wx + 16, wy + 13],
                                   fill=(250, 240, 200))
        draw.polygon([(x + 150, y + 18), (x + 190, y + 45), (x + 150, y + 45)],
                     fill=(90, 84, 76))
        draw_smoke(draw, x + 120, y + 8, 1)
        draw.line([(x + 200, y + h - 4), (x + 260, y + h - 4)], fill=INK, width=2)
        draw.line([(x + 215, y + h - 18), (x + 245, y + h - 4)], fill=INK, width=2)


def draw_icon(draw, x, y, w, h, kind):
    """Small pictogram for a small card (icon area w x h)."""
    cx, cy = x + w // 2, y + h // 2
    if kind == "target":
        draw.ellipse([cx - 20, cy - 20, cx + 20, cy + 20], outline=RED, width=3)
        draw.ellipse([cx - 10, cy - 10, cx + 10, cy + 10], outline=RED, width=2)
        draw.ellipse([cx - 3, cy - 3, cx + 3, cy + 3], fill=RED)
    elif kind == "flag":
        draw.line([(cx - 14, cy - 22), (cx - 14, cy + 22)], fill=INK, width=3)
        draw.polygon([(cx - 14, cy - 22), (cx + 16, cy - 14), (cx - 14, cy - 6)],
                     fill=RED)
    elif kind == "drone":
        draw.line([(cx - 20, cy), (cx + 20, cy)], fill=INK, width=2)
        draw.ellipse([cx - 26, cy - 4, cx - 14, cy + 4], outline=INK, width=2)
        draw.ellipse([cx + 14, cy - 4, cx + 26, cy + 4], outline=INK, width=2)
        draw.rectangle([cx - 8, cy - 6, cx + 8, cy + 6], fill=INK)
    elif kind == "factory":
        draw.polygon([(cx - 22, cy + 16), (cx - 22, cy - 6), (cx - 12, cy - 6),
                      (cx - 12, cy - 14), (cx - 2, cy - 14), (cx - 2, cy - 6),
                      (cx + 8, cy - 6), (cx + 8, cy - 14), (cx + 18, cy - 14),
                      (cx + 18, cy + 16)], fill=INK_SOFT)
        draw.rectangle([cx + 20, cy - 22, cx + 24, cy + 16], fill=INK_SOFT)
    elif kind == "trophy":
        draw.polygon([(cx - 12, cy - 18), (cx + 12, cy - 18), (cx + 8, cy + 2),
                      (cx - 8, cy + 2)], fill=(212, 160, 40))
        draw.arc([cx - 20, cy - 18, cx - 8, cy + 0], 90, 270, fill=(212, 160, 40),
                 width=3)
        draw.arc([cx + 8, cy - 18, cx + 20, cy + 0], -90, 90,
                 fill=(212, 160, 40), width=3)
        draw.rectangle([cx - 3, cy + 2, cx + 3, cy + 12], fill=(212, 160, 40))
        draw.rectangle([cx - 10, cy + 12, cx + 10, cy + 18], fill=(212, 160, 40))
    elif kind == "island":
        draw.ellipse([cx - 24, cy + 2, cx + 24, cy + 18], fill=(90, 140, 90))
        draw.polygon([(cx - 6, cy + 2), (cx, cy - 18), (cx + 6, cy + 2)],
                     fill=(40, 90, 50))
        draw.line([(cx - 26, cy + 20), (cx + 26, cy + 20)], fill=(58, 96, 122),
                  width=2)
    elif kind == "planet":
        draw.ellipse([cx - 16, cy - 16, cx + 16, cy + 16], fill=(150, 90, 60))
        draw.ellipse([cx - 24, cy - 4, cx + 24, cy + 6], outline=(90, 90, 90),
                     width=2)
        draw.ellipse([cx - 4, cy - 22, cx + 4, cy - 14], fill=(200, 200, 200))
    elif kind == "sun":
        draw.ellipse([cx - 12, cy - 12, cx + 12, cy + 12], fill=(230, 160, 40))
        for k in range(8):
            ang = math.radians(k * 45)
            draw.line([(cx + 16 * math.cos(ang), cy + 16 * math.sin(ang)),
                       (cx + 23 * math.cos(ang), cy + 23 * math.sin(ang))],
                      fill=(230, 160, 40), width=3)
    elif kind == "cup":
        draw.polygon([(cx - 12, cy - 18), (cx + 12, cy - 18), (cx + 9, cy + 4),
                      (cx - 9, cy + 4)], fill=(200, 170, 60))
        draw.rectangle([cx - 2, cy + 4, cx + 2, cy + 12], fill=(200, 170, 60))
        draw.rectangle([cx - 10, cy + 12, cx + 10, cy + 16], fill=(200, 170, 60))
        draw.ellipse([cx - 3, cy - 12, cx + 3, cy - 6], fill=(255, 255, 255))
    elif kind == "jet":
        draw.polygon([(cx - 22, cy), (cx + 10, cy - 6), (cx + 24, cy),
                      (cx + 10, cy + 6)], fill=INK)
        draw.polygon([(cx - 2, cy - 4), (cx + 6, cy - 16), (cx + 10, cy - 4)],
                     fill=INK)
        draw.polygon([(cx - 2, cy + 4), (cx + 6, cy + 16), (cx + 10, cy + 4)],
                     fill=INK)


# ---------------------------------------------------------------- page
def fit_line(draw, s, fnt, max_w):
    """Shorten a one-line list item until it fits, ending with … if cut."""
    if draw.textlength(s, font=fnt) <= max_w:
        return s
    words = s.split()
    while len(words) > 3 and draw.textlength(" ".join(words) + " …",
                                            font=fnt) > max_w:
        words.pop()
    return " ".join(words) + " …"


def draw_lead_card(draw, x, y, w, story):
    num, region, place, headline, detail, source, badge, _lat, _lon, art = story
    art_h = 120
    draw_lead_art(draw, x, y, w, art_h, art)
    banner = {"tankers": "3 TANKERS HIT", "chart": "NVIDIA −6%",
              "building": "2 DEAD, 44 HURT"}[art]
    art_banner(draw, x + 8, y + 8, w, banner)
    art_place(draw, x + 8, y + art_h - 25, place.upper())
    ty = y + art_h + 8
    col = REGION_COLORS[region]
    draw.ellipse([x, ty, x + 18, ty + 18], fill=col)
    fnt_n = SANS_B(11)
    tw = draw.textlength(str(num), font=fnt_n)
    draw.text((x + 9 - tw / 2, ty + 3), str(num), font=fnt_n,
              fill=(255, 255, 255))
    text(draw, (x + 24, ty + 2), f"{region} · {place}", SANS_B(10), col)
    bw = draw_badge(draw, x + w - 74, ty + 2, badge)
    ty += 22
    for line in wrap(draw, headline, SERIF_B(18), w)[:2]:
        text(draw, (x, ty), line, SERIF_B(18))
        ty += 21
    ty += 2
    for line in wrap(draw, detail, SANS(11), w)[:2]:
        text(draw, (x, ty), line, SANS(11), INK_SOFT)
        ty += 14
    text(draw, (x, ty + 3), source, SERIF_I(10), INK_SOFT)
    return ty + 16


def draw_small_card(draw, x, y, w, story):
    num, region, place, headline, detail, source, badge, _lat, _lon, art = story
    icon_h = 44
    draw.rectangle([x, y, x + w, y + icon_h], fill=(238, 240, 236),
                   outline=(200, 200, 195), width=1)
    draw_icon(draw, x - 34, y, w, icon_h, art)
    draw_badge(draw, x + w - 68, y + 4, badge)
    ty = y + icon_h + 6
    col = REGION_COLORS[region]
    draw.ellipse([x, ty, x + 15, ty + 15], fill=col)
    fnt_n = SANS_B(10)
    tw = draw.textlength(str(num), font=fnt_n)
    draw.text((x + 7.5 - tw / 2, ty + 2), str(num), font=fnt_n,
              fill=(255, 255, 255))
    text(draw, (x + 20, ty + 2), region.upper(), SANS_B(9), col)
    ty += 18
    for line in wrap(draw, headline, SERIF_B(15), w)[:2]:
        text(draw, (x, ty), line, SERIF_B(15))
        ty += 18
    for line in wrap(draw, detail, SANS(10), w)[:1]:
        text(draw, (x, ty), line, SANS(10), INK_SOFT)
        ty += 13
    text(draw, (x, ty + 1), source, SERIF_I(9), INK_SOFT)
    return ty + 12


def build():
    img = Image.new("RGB", (W, H), PAPER)
    draw = ImageDraw.Draw(img)
    # kicker + masthead
    text(draw, (MARGIN, 8), "ONE DAY OF WORLD NEWS, ONE PICTURE",
         SANS_B(13), RED)
    text(draw, (MARGIN, 22), "Tuesday 24 November 2026", SERIF_B(54))
    text(draw, (MARGIN, 84),
         "35 STORIES · 7 REGIONS + SPACE · 14 FIELDS · ALL FROM THIS TUESDAY",
         SANS_B(12), INK)
    draw.line([(MARGIN, 102), (W - MARGIN, 102)], fill=RULE, width=2)
    # UTC strip
    y = 108
    draw.rectangle([MARGIN, y, MARGIN + 108, y + 40], fill=RED)
    text(draw, (MARGIN + 8, y + 5), "THE DAY", SANS_B(13), (255, 255, 255))
    text(draw, (MARGIN + 8, y + 20), "IN UTC", SANS_B(13), (255, 255, 255))
    col_w = (CONTENT_W - 108) / 7
    for i, (t, ev) in enumerate(UTC_STRIP):
        cx = MARGIN + 108 + i * col_w
        text(draw, (cx + 8, y + 2), t, SANS_B(13), RED)
        for j, line in enumerate(wrap(draw, ev, SANS(10), col_w - 12)):
            text(draw, (cx + 8, y + 18 + j * 11), line, SANS(10), INK_SOFT)
        if i:
            draw.line([(cx, y + 4), (cx, y + 32)], fill=(210, 205, 190), width=1)
    # numbers strip
    y = 154
    draw.line([(MARGIN, y), (W - MARGIN, y)], fill=RULE, width=1)
    cell_w = CONTENT_W / 6
    for i, (num, label) in enumerate(NUMBERS):
        cx = MARGIN + i * cell_w
        text(draw, (cx + 6, y + 4), num, SANS_B(26), RED)
        for j, line in enumerate(wrap(draw, label, SANS(10), cell_w - 12)):
            text(draw, (cx + 6, y + 34 + j * 11), line, SANS(10), INK_SOFT)
        if i:
            draw.line([(cx, y + 6), (cx, y + 52)], fill=(210, 205, 190), width=1)
    draw.line([(MARGIN, y + 58), (W - MARGIN, y + 58)], fill=RULE, width=1)
    # lead cards
    y = 218
    card_w = (CONTENT_W - 2 * 15) // 3
    for i, story in enumerate(LEADS):
        draw_lead_card(draw, MARGIN + i * (card_w + 15), y, card_w, story)
    # small cards, two rows of five
    y = 452
    small_w = (CONTENT_W - 4 * 12) // 5
    row_h = 128
    for i, story in enumerate(SMALL):
        row, col = divmod(i, 5)
        draw_small_card(draw, MARGIN + col * (small_w + 12),
                        y + row * (row_h + 8), small_w, story)
    # bottom: map + ALSO
    y = 722
    text(draw, (MARGIN, y), "WHERE IT HAPPENED", SANS_B(13), RED)
    text(draw, (MARGIN + 316, y), "ALSO ON TUESDAY 24 NOVEMBER", SANS_B(13), RED)
    map_y = y + 20
    map_w, map_h = 300, 128
    draw_map(draw, MARGIN, map_y, map_w, map_h, LEADS + SMALL)
    ly = map_y + map_h + 8
    lx = MARGIN
    for region, count in REGION_COUNTS:
        col = REGION_COLORS.get(region, (51, 65, 85))
        draw.ellipse([lx, ly + 2, lx + 8, ly + 10], fill=col)
        label = f"{region} {count}"
        text(draw, (lx + 12, ly), label, SANS(10))
        lx += int(draw.textlength(label, font=SANS(10))) + 26
        if lx > MARGIN + map_w - 60:
            lx = MARGIN
            ly += 14
    # ALSO list, two columns of 11
    ax = MARGIN + 316
    col_w = (CONTENT_W - 316) // 2
    fnt_a = SANS(10)
    for i, (num, region, place, headline, source) in enumerate(ALSO):
        col_i, row_i = divmod(i, 11)
        ix = ax + col_i * col_w
        iy = map_y + row_i * 15
        col = REGION_COLORS[region]
        text(draw, (ix, iy), str(num), SANS_B(10), col)
        line = fit_line(draw, f"{place}: {headline}", fnt_a,
                        col_w - 26)
        text(draw, (ix + 24, iy), line, fnt_a)
    # DATE CHECK
    y = 910
    draw.rectangle([MARGIN, y, W - MARGIN, y + 56], fill=(250, 238, 232),
                   outline=RED, width=1)
    draw.rectangle([MARGIN, y, MARGIN + 92, y + 56], fill=RED)
    text(draw, (MARGIN + 8, y + 12), "DATE", SANS_B(13), (255, 255, 255))
    text(draw, (MARGIN + 8, y + 28), "CHECK", SANS_B(13), (255, 255, 255))
    dc = ("Left out on purpose, first reported before Tuesday: the COP31 collapse "
          "(21–22 Nov); Huang's resignation (~12 Nov) and his reinstatement "
          "(Mon 23 Nov) — Tuesday is the sell-off; the Colombia Meta HQ bombing "
          "(Mon 23 Nov); US Treasury Iran sanctions (Mon 23 Nov); Senegal's AFCON "
          "final win (months ago — the CAS ruling is today's news). Not yet: "
          "Taiwan votes Sat 28 Nov; US Thanksgiving Thu 26 Nov; Huang testifies "
          "on Capitol Hill next week.")
    ty = y + 5
    for line in wrap(draw, dc, SANS(10), CONTENT_W - 108):
        text(draw, (MARGIN + 100, ty), line, SANS(10), INK_SOFT)
        ty += 12
    # footer
    y = 974
    text(draw, (MARGIN, y),
         "Every story happened or was first reported on Tue 24 Nov 2026; claims attributed.",
         SANS(9), INK_SOFT)
    fx = MARGIN
    fy = y + 14
    for label in ("CONFIRMED", "OFFICIAL", "REPORTED"):
        bw = draw_badge(draw, fx, fy, label)
        fx += bw + 6
        meaning = {"CONFIRMED": "2+ outlets", "OFFICIAL": "on the record",
                   "REPORTED": "one outlet"}[label]
        text(draw, (fx, fy + 1), meaning, SANS(9), INK_SOFT)
        fx += int(draw.textlength(meaning, font=SANS(9))) + 16
    text(draw, (MARGIN, fy + 15),
         "Sources: AP, Reuters, AFP, BBC, Anadolu, Democracy Now, The Hindu, "
         "Investopedia, UEFA, Xinhua, ABC, CBC, NASA, ESA, UKHSA, FIFA, CAS · "
         "Original drawings",
         SANS(9), INK_SOFT)
    return img


def main():
    img = build()
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "entry.png")
    img.save(out, "PNG", optimize=True)
    print("wrote", out, os.path.getsize(out), "bytes")


if __name__ == "__main__":
    main()

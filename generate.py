#!/usr/bin/env python3
"""
Generates the pixel-art SVGs for a farm-style GitHub profile README.
All art is drawn from scratch with code (original, not taken from any game).

Edit the CONFIG block, then run:   python3 generate.py
"""
import math
import os
import random

# ======================= PERSONAL CONFIG =======================
# Adda's pixel-farm GitHub profile. Change these whenever your skills grow.
NAME = "Hi, I'm Adda! 👋"
TAGLINE = "PLANTING CODE, GROWING DREAMS"
FOOTER_TEXT = "THANKS FOR VISITING!"

# Skill inventory. These labels describe your current project tech and
# areas you are actively exploring; adjust if any entry isn't accurate.
# Each icon is 1-2 letters and labels should be six letters or fewer.
BACKPACK = [
    ("LANGUAGES", [
        ("KOTLIN", "KT", "#7f52ff"),
        ("JAVA", "JV", "#d1492e"),
        ("PYTHON", "PY", "#3776ab"),
        ("SQL", "SQ", "#2f8f83"),
    ]),
    ("TOOLS", [
        ("GIT", "GT", "#f05032"),
        ("STUDIO", "AS", "#3a9d5d"),
        ("ROOM", "RM", "#4c75a3"),
        ("GITHUB", "GH", "#555555"),
    ]),
    ("EXPLORING", [
        ("AI", "AI", "#8a4fc7"),
        ("WEB", "WB", "#3a9d5d"),
        ("MOBILE", "MB", "#d17f30"),
        ("DATA", "DT", "#2f8f83"),
    ]),
]
OUT_DIR = "assets"
# ================================================================

# ---------- 5x7 bitmap font (uppercase, digits, a little punctuation) ----------
FONT = {
    'A': ".###./#...#/#...#/#####/#...#/#...#/#...#",
    'B': "####./#...#/#...#/####./#...#/#...#/####.",
    'C': ".###./#...#/#..../#..../#..../#...#/.###.",
    'D': "####./#...#/#...#/#...#/#...#/#...#/####.",
    'E': "#####/#..../#..../####./#..../#..../#####",
    'F': "#####/#..../#..../####./#..../#..../#....",
    'G': ".###./#...#/#..../#.###/#...#/#...#/.###.",
    'H': "#...#/#...#/#...#/#####/#...#/#...#/#...#",
    'I': ".###./..#../..#../..#../..#../..#../.###.",
    'J': "..###/...#./...#./...#./...#./#..#./.##..",
    'K': "#...#/#..#./#.#../##.../#.#../#..#./#...#",
    'L': "#..../#..../#..../#..../#..../#..../#####",
    'M': "#...#/##.##/#.#.#/#.#.#/#...#/#...#/#...#",
    'N': "#...#/##..#/#.#.#/#..##/#...#/#...#/#...#",
    'O': ".###./#...#/#...#/#...#/#...#/#...#/.###.",
    'P': "####./#...#/#...#/####./#..../#..../#....",
    'Q': ".###./#...#/#...#/#...#/#.#.#/#..#./.##.#",
    'R': "####./#...#/#...#/####./#.#../#..#./#...#",
    'S': ".####/#..../#..../.###./....#/....#/####.",
    'T': "#####/..#../..#../..#../..#../..#../..#..",
    'U': "#...#/#...#/#...#/#...#/#...#/#...#/.###.",
    'V': "#...#/#...#/#...#/#...#/#...#/.#.#./..#..",
    'W': "#...#/#...#/#...#/#.#.#/#.#.#/##.##/#...#",
    'X': "#...#/#...#/.#.#./..#../.#.#./#...#/#...#",
    'Y': "#...#/#...#/.#.#./..#../..#../..#../..#..",
    'Z': "#####/....#/...#./..#../.#.../#..../#####",
    '0': ".###./#...#/#..##/#.#.#/##..#/#...#/.###.",
    '1': "..#../.##../..#../..#../..#../..#../.###.",
    '2': ".###./#...#/....#/...#./..#../.#.../#####",
    '3': "####./....#/....#/.###./....#/....#/####.",
    '4': "...#./..##./.#.#./#..#./#####/...#./...#.",
    '5': "#####/#..../####./....#/....#/#...#/.###.",
    '6': ".###./#..../#..../####./#...#/#...#/.###.",
    '7': "#####/....#/...#./..#../.#.../.#.../.#...",
    '8': ".###./#...#/#...#/.###./#...#/#...#/.###.",
    '9': ".###./#...#/#...#/.####/....#/....#/.###.",
    '.': "...../...../...../...../...../.##../.##..",
    ',': "...../...../...../...../.##../..#../.#...",
    "'": "..#../..#../.#.../...../...../...../.....",
    '-': "...../...../...../#####/...../...../.....",
    ':': "...../.##../.##../...../.##../.##../.....",
    '!': "..#../..#../..#../..#../..#../...../..#..",
    '&': ".##../#..#./.##../#.#.#/#..#./#..#./.##.#",
    '/': "....#/....#/...#./..#../.#.../#..../#....",
    '+': "...../..#../..#../#####/..#../..#../.....",
    '>': "#..../.#.../..#../...#./..#../.#.../#....",
    '@': ".###./#...#/#.###/#.#.#/#.###/#..../.###.",
    '?': ".###./#...#/....#/...#./..#../...../..#..",
}


def text_width(s, scale=1):
    return (sum((3 if ch == ' ' else 5) + 1 for ch in s) - 1) * scale


class Canvas:
    def __init__(self, w, h):
        self.w, self.h = w, h
        self.p = [[None] * w for _ in range(h)]

    def px(self, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.h:
            self.p[y][x] = c

    def rect(self, x, y, w, h, c):
        for yy in range(y, y + h):
            for xx in range(x, x + w):
                self.px(xx, yy, c)

    def disc(self, cx, cy, r, c):
        for yy in range(cy - r, cy + r + 1):
            for xx in range(cx - r, cx + r + 1):
                if (xx - cx) ** 2 + (yy - cy) ** 2 <= r * r + r * 0.4:
                    self.px(xx, yy, c)

    def pattern(self, x, y, rows, cmap):
        for ry, row in enumerate(rows):
            for rx, ch in enumerate(row):
                if ch in cmap:
                    self.px(x + rx, y + ry, cmap[ch])

    def text(self, x, y, s, color, scale=1, shadow=None):
        def put(ox, oy, col):
            cx = x + ox
            for ch in s:
                if ch == ' ':
                    cx += 4 * scale
                    continue
                glyph = FONT.get(ch.upper(), FONT['?']).split('/')
                for ry, row in enumerate(glyph):
                    for rx, v in enumerate(row):
                        if v == '#':
                            self.rect(cx + rx * scale, y + oy + ry * scale, scale, scale, col)
                cx += 6 * scale
        if shadow:
            off = max(1, scale // 2)
            put(off, off, shadow)
        put(0, 0, color)

    def paths(self):
        by, active = {}, {}

        def flush(key, y_end):
            x0, x1, c = key
            y0 = active.pop(key)
            by.setdefault(c, []).append(f"M{x0} {y0}h{x1 - x0}v{y_end - y0}h-{x1 - x0}z")

        for y in range(self.h):
            row, runs, x = self.p[y], set(), 0
            while x < self.w:
                c = row[x]
                if c is None:
                    x += 1
                    continue
                x0 = x
                while x < self.w and row[x] == c:
                    x += 1
                runs.add((x0, x, c))
            for key in list(active):
                if key not in runs:
                    flush(key, y)
            for key in runs:
                if key not in active:
                    active[key] = y
        for key in list(active):
            flush(key, self.h)
        return "".join(f'<path fill="{c}" d="{"".join(ds)}"/>' for c, ds in by.items())


def shade(c, f):
    c = c.lstrip('#')
    r, g, b = [int(c[i:i + 2], 16) for i in (0, 2, 4)]
    if f < 0:
        r, g, b = [int(v * (1 + f)) for v in (r, g, b)]
    else:
        r, g, b = [int(v + (255 - v) * f) for v in (r, g, b)]
    return f"#{r:02x}{g:02x}{b:02x}"


def layer(cv, cls="", style=""):
    a = f' class="{cls}"' if cls else ""
    s = f' style="{style}"' if style else ""
    return f"<g{a}{s}>{cv.paths()}</g>"


CSS = """
.c1{animation:d1 60s steps(24) infinite alternate}
.c2{animation:d2 75s steps(20) infinite alternate}
.c3{animation:d1 90s steps(24) infinite alternate-reverse}
@keyframes d1{from{transform:translateX(-8px)}to{transform:translateX(16px)}}
@keyframes d2{from{transform:translateX(6px)}to{transform:translateX(-14px)}}
.t1{animation:tw 3s steps(1) infinite}
.t2{animation:tw 3s steps(1) infinite;animation-delay:-1.5s}
@keyframes tw{0%,50%{opacity:1}51%,100%{opacity:.15}}
.sm{animation:sm 4s steps(8) infinite}
@keyframes sm{from{transform:translateY(0);opacity:.9}to{transform:translateY(-8px);opacity:0}}
.pk{animation:pk 1.8s steps(1) infinite}
@keyframes pk{0%,60%{transform:translateY(0)}65%,80%{transform:translateY(1px)}85%,100%{transform:translateY(0)}}
.ff{animation:ff 4s steps(1) infinite}
@keyframes ff{0%,40%{opacity:0}41%,75%{opacity:1}76%,100%{opacity:0}}
.zz{animation:zz 3s steps(6) infinite}
@keyframes zz{from{transform:translateY(0);opacity:1}to{transform:translateY(-6px);opacity:0}}
@media (prefers-reduced-motion:reduce){*{animation:none!important}}
"""


def svg_doc(w, h, body, scale=4):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" '
            f'width="{w * scale}" height="{h * scale}" shape-rendering="crispEdges">'
            f'<style>{CSS}</style>{body}</svg>')


# ---------------- palettes ----------------
DK, MID, LT, EDGE, PARCH = "#4a2511", "#8a4b1e", "#b8742f", "#e0b25f", "#f8d98f"

DAY = dict(
    night=False,
    sky=["#5bb8ee", "#6cc3f2", "#80cdf5", "#96d7f8", "#addffa", "#c4e8fb"],
    mount="#8db3d8", mount_hi="#b3d0ea", hill="#58a64a", hill_hi="#70bd5c",
    grass="#74bd3f", grass_dk="#5fa332", grass_lt="#8ed653",
    soil="#a0703c", soil_dk="#7d5229", soil_lt="#b78450",
    wood="#c68642", wood_dk="#9a622a", wood_lt="#dea15a",
    roof="#c0413a", roof_dk="#8f2c27", roof_lt="#dd6a60",
    glass="#a8e2f7", stone="#9a9a9a", stone_dk="#6f6f6f",
    tree_dk="#2f7a34", tree_md="#43953e", tree_lt="#63b852", trunk="#7a4a22", trunk_dk="#5a3416",
    cloud="#ffffff", cloud_sh="#d6e8f5", smoke="#ececec",
    flowers=["#ff7fa8", "#ffe066", "#ffffff", "#b58cff"], stem="#3f8f2f",
)
NIGHT = dict(
    night=True,
    sky=["#0a0e2e", "#101648", "#17205a", "#1f2b6a", "#2a387a", "#37478a"],
    mount="#3b4a82", mount_hi="#566699", hill="#2c6144", hill_hi="#3d7a56",
    grass="#3a7a3c", grass_dk="#2e6a31", grass_lt="#4a8f48",
    soil="#6b4a30", soil_dk="#4f3420", soil_lt="#805c3c",
    wood="#8f5f35", wood_dk="#6e4524", wood_lt="#aa7342",
    roof="#8f3a3a", roof_dk="#652727", roof_lt="#aa5050",
    glass="#ffd36a", stone="#6d7388", stone_dk="#4d5266",
    tree_dk="#1f4f2d", tree_md="#2c6a3a", tree_lt="#3d8449", trunk="#5c3a1c", trunk_dk="#40270f",
    cloud="#2f3d80", cloud_sh="#26336c", smoke="#a8aec8",
    flowers=["#d97aa0", "#e8cf6a", "#cfd6f0", "#9f84d9"], stem="#2a6a2c",
)


# ---------------- shared pieces ----------------
def boxc(cv, x, y, w, h, c):
    cv.rect(x + 1, y, w - 2, 1, c)
    cv.rect(x, y + 1, w, h - 2, c)
    cv.rect(x + 1, y + h - 1, w - 2, 1, c)


def frame(cv, x, y, w, h):
    boxc(cv, x, y, w, h, DK)
    boxc(cv, x + 1, y + 1, w - 2, h - 2, MID)
    boxc(cv, x + 2, y + 2, w - 4, h - 4, LT)
    cv.rect(x + 3, y + 3, w - 6, h - 6, EDGE)
    cv.rect(x + 4, y + 4, w - 8, h - 8, PARCH)


def sky_bands(cv, P, bands, thickness, y0=0, fill_to=None):
    for i, c in enumerate(bands):
        cv.rect(0, y0 + i * thickness, cv.w, thickness, c)
    for i in range(1, len(bands)):
        by = y0 + i * thickness
        for x in range(cv.w):
            if (x + i) % 2 == 0:
                cv.px(x, by, bands[i - 1])
            else:
                cv.px(x, by - 1, bands[i])
    if fill_to:
        cv.rect(0, y0 + len(bands) * thickness, cv.w, fill_to - (y0 + len(bands) * thickness), bands[-1])


def sun_or_moon(cv, P, cx, cy):
    if not P['night']:
        cv.disc(cx, cy, 6, "#ffd84a")
        cv.disc(cx, cy, 4, "#ffe98a")
        for (rx, ry, rw, rh) in [(-1, -10, 2, 3), (-1, 8, 2, 3), (-10, -1, 3, 2), (8, -1, 3, 2)]:
            cv.rect(cx + rx, cy + ry, rw, rh, "#fff3b0")
    else:
        for yy in range(cy - 7, cy + 8):
            for xx in range(cx - 7, cx + 8):
                in_a = (xx - cx) ** 2 + (yy - cy) ** 2 <= 38
                in_b = (xx - cx - 3) ** 2 + (yy - cy + 2) ** 2 <= 30
                if in_a and not in_b:
                    cv.px(xx, yy, "#f4eec4")


def draw_fence(cv, P, y, x_from, x_to, gap=None, spacing=12):
    wood, dk, lt = P['wood'], P['wood_dk'], P['wood_lt']
    for rail_y in (y + 3, y + 6):
        segs = [(x_from, x_to)] if not gap else [(x_from, gap[0]), (gap[1], x_to)]
        for a, b in segs:
            cv.rect(a, rail_y, b - a, 2, wood)
            cv.rect(a, rail_y + 1, b - a, 1, dk)
    for x in range(x_from, x_to, spacing):
        if gap and gap[0] - 2 <= x <= gap[1] - 3:
            continue
        cv.rect(x, y, 3, 10, wood)
        cv.rect(x + 2, y, 1, 10, dk)
        cv.px(x, y, lt)
        cv.px(x + 1, y, lt)


def scatter_flowers(cv, P, rng, n, x0, x1, y0, y1):
    for _ in range(n):
        x, y = rng.randint(x0, x1), rng.randint(y0, y1)
        col = rng.choice(P['flowers'])
        if rng.random() < 0.35:
            for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1)):
                cv.px(x + dx, y + dy, col)
            cv.px(x, y, "#ffd84a" if col != "#ffe066" else "#ffffff")
        else:
            cv.px(x, y, col)
        cv.px(x, y + 1, P['stem'])


def tufts(cv, P, rng, n, y0, y1):
    for _ in range(n):
        x, y = rng.randint(0, cv.w - 3), rng.randint(y0, y1)
        if rng.random() < 0.6:
            cv.px(x, y, P['grass_dk'])
            cv.px(x + 2, y, P['grass_dk'])
            cv.px(x + 1, y - 1, P['grass_dk'])
        else:
            cv.px(x, y, P['grass_lt'])
            cv.px(x + 1, y, P['grass_lt'])


CLOUD_A = ["....####......", "..########.##.", ".#############", "##############", ".ssssssssssss."]
CLOUD_B = ["...####..", ".#######.", "#########", ".sssssss."]


# ---------------- banner ----------------
def banner(P):
    W, H = 225, 96
    tw = max(text_width(NAME, 2), text_width(TAGLINE, 1))
    pw = max(tw + 18, 120)
    ph = 44
    pxl, pyt = (W - pw) // 2, 4
    rng = random.Random(42)

    sky = Canvas(W, H)
    sky_bands(sky, P, P['sky'], 8, 0, fill_to=70)
    sun_or_moon(sky, P, 213, 12)

    parts = [layer(sky)]

    if P['night']:
        s1, s2 = Canvas(W, H), Canvas(W, H)
        for i in range(34):
            x, y = rng.randint(2, W - 3), rng.randint(2, 50)
            if pxl - 2 <= x <= pxl + pw + 2 and pyt - 2 <= y <= pyt + ph + 2:
                continue
            tgt = s1 if i % 2 == 0 else s2
            col = "#ffffff" if i % 3 else "#ffe9a8"
            tgt.px(x, y, col)
            if i % 5 == 0:
                for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1)):
                    tgt.px(x + dx, y + dy, col)
        parts += [layer(s1, "t1"), layer(s2, "t2")]

    cm = {'#': P['cloud'], 's': P['cloud_sh']}
    for (rows, x, y, cls) in [(CLOUD_A, 3, 12, "c1"), (CLOUD_B, 196, 28, "c2"), (CLOUD_A, 100, 34, "c3")]:
        c = Canvas(W, H)
        c.pattern(x, y, rows, cm)
        parts.append(layer(c, cls))

    f = Canvas(W, H)
    # mountains + hills
    for x in range(W):
        h = 60 - int(9 + 5 * math.sin(x / 16.0) + 3 * math.sin(x / 6.5 + 1.3) + 4 * math.sin(x / 38.0 + 0.5))
        f.rect(x, h, 1, 70 - h, P['mount'])
        f.px(x, h, P['mount_hi'])
        if x % 2 == 0:
            f.px(x, h + 1, P['mount_hi'])
    for x in range(W):
        h = 64 - int(4 + 3 * math.sin(x / 21.0 + 2) + 2 * math.sin(x / 9.0))
        f.rect(x, h, 1, 72 - h, P['hill'])
        f.px(x, h, P['hill_hi'])
    # ground
    f.rect(0, 64, W, H - 64, P['grass'])
    tufts(f, P, rng, 170, 66, H - 2)
    scatter_flowers(f, P, rng, 60, 0, W - 2, 68, H - 3)

    # dirt path from the door
    for y in range(85, H):
        f.rect(12, y, 11, 1, P['soil_lt'])
        f.px(12, y, P['soil'])
        f.px(22, y, P['soil'])
    for (x, y) in [(15, 88), (19, 91), (14, 93), (20, 86)]:
        f.px(x, y, P['soil_dk'])

    # sign posts (behind the field)
    for x in (72, 150):
        f.rect(x, 40, 4, 30, P['wood_dk'])
        f.rect(x, 40, 1, 30, P['wood'])

    # crop field
    fx, fy, fw, fh = 68, 70, 98, 17
    f.rect(fx, fy, fw, fh, P['soil'])
    f.rect(fx, fy, fw, 1, P['soil_dk'])
    f.rect(fx, fy + fh - 1, fw, 1, P['soil_dk'])
    f.rect(fx, fy, 1, fh, P['soil_dk'])
    f.rect(fx + fw - 1, fy, 1, fh, P['soil_dk'])
    for ry in (71, 76, 81, 86):
        f.rect(fx + 1, ry, fw - 2, 1, P['soil_dk'])
    for yy in (73, 78, 83):
        for xx in range(fx + 2, fx + fw - 2, 3):
            f.px(xx, yy, P['soil_lt'])
    leaf = "#4fb043" if not P['night'] else "#2f7a3a"
    leaf_dk = "#2f7a34" if not P['night'] else "#1f5a2d"
    for row, base in enumerate((75, 80, 85)):
        for i in range(10):
            cx = 74 + i * 9 + (row % 2) * 4
            kind = (i + row) % 3
            if kind == 0:   # sprout
                f.px(cx, base, leaf_dk); f.px(cx, base - 1, leaf)
                f.px(cx - 1, base - 2, leaf); f.px(cx + 1, base - 2, leaf)
            elif kind == 1:  # cabbage
                f.rect(cx - 1, base - 3, 3, 1, "#8fdc6f" if not P['night'] else "#4f9a50")
                f.rect(cx - 2, base - 2, 5, 2, "#6fcf5a" if not P['night'] else "#3f8a47")
                f.rect(cx - 2, base, 5, 1, leaf_dk)
            else:           # pumpkin
                org = "#f08a24" if not P['night'] else "#b8651f"
                f.px(cx, base - 4, leaf_dk)
                f.rect(cx - 2, base - 3, 5, 3, org)
                f.px(cx - 1, base - 3, shade(org, 0.35)); f.px(cx - 1, base - 2, shade(org, 0.2))
                f.px(cx + 2, base - 1, shade(org, -0.3)); f.px(cx, base - 1, shade(org, -0.2))

    # house
    x0, cx = 6, 29
    f.rect(cx + 4, 49, 5, 12, P['stone'])          # chimney
    f.rect(cx + 3, 49, 7, 2, P['stone_dk'])
    for r in range(15):
        hw = 5 + (r * 8) // 5
        col = P['roof_dk'] if r == 14 else (P['roof_dk'] if r % 4 == 3 else P['roof'])
        f.rect(cx - hw, 55 + r, 2 * hw + 1, 1, col)
        f.px(cx - hw, 55 + r, P['roof_lt'])
        if r % 4 != 3 and r != 14:
            for sx in range(cx - hw + 3, cx + hw, 6):
                f.px(sx, 55 + r, P['roof_dk'])
    f.rect(x0, 70, 46, 15, P['wood'])
    for xx in range(x0 + 4, x0 + 44, 5):
        f.rect(xx, 70, 1, 13, P['wood_dk'])
    f.rect(x0, 70, 2, 15, P['wood_dk'])
    f.rect(x0 + 44, 70, 2, 15, P['wood_dk'])
    f.rect(x0, 83, 46, 2, P['stone'])
    for xx in range(x0, x0 + 46, 4):
        f.px(xx, 83, P['stone_dk'])
    f.rect(x0 + 7, 73, 9, 12, "#4a2a12")
    f.rect(x0 + 8, 74, 7, 11, "#7a4a22")
    f.px(x0 + 8, 74, "#4a2a12"); f.px(x0 + 14, 74, "#4a2a12")
    f.rect(x0 + 11, 74, 1, 11, "#6a3d1c")
    f.px(x0 + 13, 80, "#f2c14e")
    f.rect(x0 + 26, 73, 12, 9, "#4a2a12")
    f.rect(x0 + 27, 74, 10, 7, P['glass'])
    f.rect(x0 + 32, 74, 1, 7, "#4a2a12")
    f.rect(x0 + 27, 77, 10, 1, "#4a2a12")
    if P['night']:
        f.rect(x0 + 27, 74, 5, 3, "#ffe9a8")
    else:
        f.px(x0 + 28, 75, shade(P['glass'], 0.7)); f.px(x0 + 29, 75, shade(P['glass'], 0.7))

    # tree
    f.rect(186, 84, 20, 2, P['grass_dk'])
    f.rect(193, 70, 6, 15, P['trunk'])
    f.rect(197, 70, 2, 15, P['trunk_dk'])
    f.px(192, 84, P['trunk']); f.px(199, 84, P['trunk_dk'])
    f.disc(196, 60, 14, P['tree_dk'])
    f.disc(194, 58, 12, P['tree_md'])
    f.disc(191, 54, 7, P['tree_lt'])
    for _ in range(26):
        sx, sy = rng.randint(184, 208), rng.randint(48, 72)
        if (sx - 195) ** 2 + (sy - 60) ** 2 <= 150:
            f.px(sx, sy, P['tree_lt'] if rng.random() < 0.5 else P['tree_dk'])

    # front fence
    draw_fence(f, P, 87, 0, W, gap=(11, 24))
    parts.append(layer(f))

    # smoke
    for dy, delay in ((0, "0s"), (0, "-2s")):
        sm = Canvas(W, H)
        sm.rect(cx + 5, 44, 3, 2, P['smoke'])
        sm.rect(cx + 6, 43, 2, 1, P['smoke'])
        parts.append(layer(sm, "sm", f"animation-delay:{delay}"))

    # chicken
    ch = Canvas(W, H)
    chk = ["....rr..", "...wkwo.", ".gwwwww.", "gwwwwwg.", ".gwwwgg.", "..o..o.."]
    ch.pattern(170, 79, chk, {'r': "#d63a3a", 'w': "#ffffff" if not P['night'] else "#d8dcee",
                              'k': "#222222", 'o': "#f0a030", 'g': "#d4d4d4" if not P['night'] else "#aab0c8"})
    parts.append(layer(ch, "pk"))

    if P['night']:
        for i, (fx_, fy_) in enumerate([(60, 66), (120, 90), (176, 70), (40, 92), (140, 66), (100, 68)]):
            fl = Canvas(W, H)
            fl.px(fx_, fy_, "#fff59a")
            fl.px(fx_ + 1, fy_, "#ffe066")
            parts.append(layer(fl, "ff", f"animation-delay:-{i * 0.7:.1f}s"))

    # wooden sign (top layer)
    top = Canvas(W, H)
    frame(top, pxl, pyt, pw, ph)
    for (nx, ny) in ((pxl + 6, pyt + 6), (pxl + pw - 7, pyt + 6), (pxl + 6, pyt + ph - 7), (pxl + pw - 7, pyt + ph - 7)):
        top.px(nx, ny, MID)
    top.text(pxl + (pw - text_width(NAME, 2)) // 2, pyt + 9, NAME, DK, 2, "#d9a652")
    top.text(pxl + (pw - text_width(TAGLINE, 1)) // 2, pyt + 29, TAGLINE, MID, 1, "#ecc88a")
    parts.append(layer(top))
    return svg_doc(W, H, "".join(parts))


# ---------------- backpack (inventory panel) ----------------
def backpack():
    W = 225
    n = len(BACKPACK)
    H = 32 + 38 * n + 4
    cv = Canvas(W, H)
    frame(cv, 0, 0, W, H)
    title = "BACKPACK"
    cv.text((W - text_width(title, 2)) // 2, 9, title, DK, 2, "#d9a652")
    cv.rect(10, 26, W - 20, 1, "#d9a652")
    for nx, ny in ((6, 6), (W - 7, 6), (6, H - 7), (W - 7, H - 7)):
        cv.px(nx, ny, MID)

    x0 = 14
    for ri, (title_, items) in enumerate(BACKPACK):
        y = 32 + ri * 38
        cv.text(x0, y, title_, MID, 1)
        lw = text_width(title_, 1)
        cv.rect(x0 + lw + 4, y + 3, W - 2 * x0 - lw - 4, 1, "#d9a652")
        for i in range(5):
            sx = x0 + i * 38 + 11
            sy = y + 9
            boxc(cv, sx, sy, 16, 16, "#a56a2f")
            cv.rect(sx + 1, sy + 1, 14, 14, "#e8b96a")
            cv.rect(sx + 1, sy + 1, 14, 1, "#c98d45")
            cv.rect(sx + 1, sy + 1, 1, 14, "#c98d45")
            if i < len(items):
                label, icon, col = items[i]
                assert len(icon) <= 2, "icon text must be 1-2 letters"
                boxc(cv, sx + 2, sy + 2, 12, 12, col)
                cv.rect(sx + 3, sy + 3, 10, 1, shade(col, 0.35))
                cv.rect(sx + 3, sy + 12, 10, 1, shade(col, -0.35))
                iw = text_width(icon, 1)
                cv.text(sx + 2 + (12 - iw) // 2, sy + 4, icon, "#ffffff", 1, shade(col, -0.5))
                lw2 = text_width(label, 1)
                cv.text(sx + 8 - lw2 // 2, sy + 19, label, DK, 1)
    return svg_doc(W, H, layer(cv))


# ---------------- footer ----------------
def footer(P):
    W, H = 225, 52
    rng = random.Random(5)
    sky = Canvas(W, H)
    sky_bands(sky, P, P['sky'][1:6], 5, 0, fill_to=30)
    sun_or_moon(sky, P, 14, 11)
    parts = [layer(sky)]
    if P['night']:
        s1, s2 = Canvas(W, H), Canvas(W, H)
        for i in range(22):
            x, y = rng.randint(30, W - 3), rng.randint(1, 20)
            tgt = s1 if i % 2 == 0 else s2
            tgt.px(x, y, "#ffffff")
            if i % 5 == 0:
                for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1)):
                    tgt.px(x + dx, y + dy, "#ffffff")
        parts += [layer(s1, "t1"), layer(s2, "t2")]

    f = Canvas(W, H)
    for x in range(W):
        h = 29 - int(3 + 2 * math.sin(x / 14.0 + 1) + 1.5 * math.sin(x / 5.0))
        f.rect(x, h, 1, 32 - h, P['hill'])
        f.px(x, h, P['hill_hi'])
    f.rect(0, 29, W, H - 29, P['grass'])
    tufts(f, P, rng, 80, 31, H - 2)
    scatter_flowers(f, P, rng, 36, 0, W - 2, 34, H - 3)

    tw = text_width(FOOTER_TEXT, 1)
    pw, ph = tw + 18, 22
    pxl, pyt = (W - pw) // 2, 3
    for x in (pxl + 14, pxl + pw - 17):
        f.rect(x, 20, 3, 18, P['wood_dk'])
        f.rect(x, 20, 1, 18, P['wood'])
    draw_fence(f, P, 40, 0, W)

    # hay bale + sleeping cat
    f.rect(194, 35, 18, 11, "#e7c05a" if not P['night'] else "#a98d3f")
    f.rect(194, 35, 18, 1, "#f4d97f" if not P['night'] else "#c2a655")
    for yy in (38, 42):
        f.rect(194, yy, 18, 1, "#b8923a" if not P['night'] else "#7e6a2c")
    for xx in (198, 204, 209):
        f.px(xx, 36, "#b8923a" if not P['night'] else "#7e6a2c")
    cat = ["o..o.........", "oooooooooo...", "okoooodoodoo.", "ooooooooooood",
           "llooooooooood", ".llllllllll.."]
    f.pattern(197, 29, cat, {'o': "#e08a3c" if not P['night'] else "#b86a2c",
                             'd': "#b8652a" if not P['night'] else "#8f4a1f",
                             'l': "#f6d6a0" if not P['night'] else "#cfae80", 'k': "#3a2410"})
    parts.append(layer(f))

    zc = Canvas(W, H)
    zc.text(192, 20, "Z", "#ffffff" if P['night'] else "#6a7ab0", 1)
    parts.append(layer(zc, "zz"))
    zc2 = Canvas(W, H)
    zc2.text(199, 14, "Z", "#ffffff" if P['night'] else "#6a7ab0", 1)
    parts.append(layer(zc2, "zz", "animation-delay:-1.5s"))

    if P['night']:
        for i, (fx_, fy_) in enumerate([(30, 36), (80, 44), (130, 34), (160, 46), (60, 32)]):
            fl = Canvas(W, H)
            fl.px(fx_, fy_, "#fff59a")
            fl.px(fx_ + 1, fy_, "#ffe066")
            parts.append(layer(fl, "ff", f"animation-delay:-{i * 0.8:.1f}s"))

    top = Canvas(W, H)
    frame(top, pxl, pyt, pw, ph)
    top.text(pxl + (pw - tw) // 2, pyt + 8, FOOTER_TEXT, DK, 1, "#d9a652")
    parts.append(layer(top))
    return svg_doc(W, H, "".join(parts))


# ---------------- divider ----------------
def divider():
    W, H = 225, 10
    P = DAY
    rng = random.Random(3)
    cv = Canvas(W, H)
    for x in range(W):
        cv.px(x, 8, P['grass_dk'])
        cv.px(x, 9, P['grass'])
    for x in range(0, W, 3):
        if rng.random() < 0.8:
            cv.px(x, 7, P['grass_lt'])
    for x in range(6, W - 4, 17):
        col = rng.choice(P['flowers'])
        cv.px(x, 3, col); cv.px(x - 1, 4, col); cv.px(x + 1, 4, col); cv.px(x, 5, col)
        cv.px(x, 4, "#ffd84a")
        cv.px(x, 6, P['stem']); cv.px(x, 7, P['stem'])
    return svg_doc(W, H, layer(cv))


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    files = {
        "banner-day.svg": banner(DAY),
        "banner-night.svg": banner(NIGHT),
        "backpack.svg": backpack(),
        "footer-day.svg": footer(DAY),
        "footer-night.svg": footer(NIGHT),
        "divider.svg": divider(),
    }
    for name, content in files.items():
        with open(os.path.join(OUT_DIR, name), "w", encoding="utf-8") as fh:
            fh.write(content)
        print(f"{name}: {len(content) / 1024:.1f} KB")


if __name__ == "__main__":
    main()

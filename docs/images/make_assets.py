#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generates the README images (SVG), stdlib only:  python docs/images/make_assets.py

Palette (crimson brand, no orange/olive). Base contrast >= 4.5:1, light >= 7:1 on #131016
(checked at the end of this script).
  brand            #C0392B  (light #E5614F on dark cards)
  zone 1 demo      #E5483B / #FF9D93   crimson
  zone 2 how       #E8608F / #FFA9C6   rose
  zone 3 get       #C26AE0 / #E3A9F5   orchid
  zone 4 use       #5B93F0 / #A3C4FA   blue
  zone 5 ai        #8E86F0 / #C3BEFA   lavender
  demo modules     KAF #6d4fd6/#a995f5  RAD #2563c9/#7fb0f5  GAR #1b9a5f/#5fd49a  (dark/light UI colour)
  real modules     see MOD8 (one colour per module, used by its study-doc and trainer pill)
Outputs: docs/images/*.svg (README) and docs/images/mine/*.svg (docs/MY-EXAM-PERIOD.md).
"""
import os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
SRC = os.path.join(ROOT, "examples", "source", "docs", "readme")
MINE = os.path.join(HERE, "mine")
os.makedirs(MINE, exist_ok=True)
FONT = "Segoe UI, -apple-system, Helvetica, Arial, sans-serif"
CARD = "#131016"
CRIMSON, CRIMSON_L = "#C0392B", "#E5614F"


def w(path, s):
    with open(path, "w", encoding="utf-8") as f:
        f.write(s)


def esc(t):
    return t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


# ───────────────────────── zones ─────────────────────────
ZONES = [  # key, number, title, subtitle, base, light, icon
    ("demo", "01", "Try the demo", "three fictional modules, same structure as the real thing", "#E5483B", "#FF9D93",
     '<rect x="-12" y="-9" width="24" height="18" rx="3"/><path d="M-3 -4 L5 0 L-3 4 Z"/>'),
    ("how", "02", "How it works", "material → analysis → build → plan → cockpit", "#E8608F", "#FFA9C6",
     '<circle cx="-9" cy="0" r="3"/><circle cx="9" cy="0" r="3"/><path d="M-5 0 H5"/><path d="M2 -3 L5 0 L2 3"/>'),
    ("get", "03", "What you get", "screens from the demo, dark mode", "#C26AE0", "#E3A9F5",
     '<rect x="-11" y="-11" width="9" height="9" rx="2"/><rect x="2" y="-11" width="9" height="9" rx="2"/>'
     '<rect x="-11" y="2" width="9" height="9" rx="2"/><rect x="2" y="2" width="9" height="9" rx="2"/>'),
    ("use", "04", "Use it yourself", "three steps, then your own modules", "#5B93F0", "#A3C4FA",
     '<rect x="-12" y="-10" width="24" height="20" rx="3"/><path d="M-7 -3 L-3 0 L-7 3"/><path d="M0 4 H6"/>'),
    ("ai", "05", "How I built it and what the AI did", "my decisions, Claude as coding assistant", "#8E86F0", "#C3BEFA",
     '<path d="M-11 -9 H11 V5 H2 L-4 11 V5 H-11 Z"/><path d="M-5 -2 H5"/>'),
]


MINE_ZONES = [  # the three zones of docs/MY-EXAM-PERIOD.md, same strip design
    ("modules", "01", "The eight modules", "one colour per module · study document and trainer", "#E5483B", "#FF9D93",
     '<rect x="-11" y="-11" width="9" height="9" rx="2"/><rect x="2" y="-11" width="9" height="9" rx="2"/>'
     '<rect x="-11" y="2" width="9" height="9" rx="2"/><rect x="2" y="2" width="9" height="9" rx="2"/>'),
    ("plan", "02", "A day in the real plan", "typed blocks, checkable steps", "#E8608F", "#FFA9C6",
     '<rect x="-11" y="-9" width="22" height="20" rx="3"/><path d="M-11 -3 H11"/><path d="M-6 -12 V-7"/><path d="M6 -12 V-7"/>'),
    ("numbers", "03", "In numbers", "the September 2026 exam period", "#C26AE0", "#E3A9F5",
     '<path d="M-10 10 V2"/><path d="M-3 10 V-4"/><path d="M4 10 V-9"/><path d="M11 10 V-1"/>'),
]


def strip(z):
    k, nn, title, sub, base, light, icon = z
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="84" viewBox="0 0 1200 84" font-family="{FONT}">
<defs><linearGradient id="g" x1="0" x2="1" y1="0" y2="0"><stop offset="0" stop-color="{base}" stop-opacity=".28"/><stop offset=".55" stop-color="{base}" stop-opacity="0"/></linearGradient></defs>
<rect x="0.5" y="0.5" width="1199" height="83" rx="14" fill="{CARD}" stroke="{base}" stroke-opacity=".45"/>
<rect x="1" y="1" width="1198" height="82" rx="14" fill="url(#g)"/>
<rect x="0" y="16" width="6" height="52" rx="3" fill="{base}"/>
<circle cx="62" cy="42" r="24" fill="{base}" fill-opacity=".16" stroke="{base}" stroke-width="1.5"/>
<g transform="translate(62 42)" fill="none" stroke="{light}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">{icon}</g>
<text x="106" y="33" fill="{base}" font-size="12" font-weight="700" letter-spacing="3">{nn}</text>
<text x="104" y="60" fill="{light}" font-size="27" font-weight="700" letter-spacing="-0.3">{esc(title)}</text>
<text x="1172" y="49" fill="#b8aeb4" font-size="15" text-anchor="end">{esc(sub)}</text>
</svg>
'''


def nav_pill(label, base):
    wd = round(len(label) * 7.3 + 42)
    tx = 26 + (len(label) * 7.3 + 2) / 2
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{wd}" height="26" viewBox="0 0 {wd} 26" font-family="Verdana, DejaVu Sans, sans-serif" font-size="12">
<rect x=".5" y=".5" width="{wd-1}" height="25" rx="13" fill="#1c1418" stroke="{base}"/>
<circle cx="15" cy="13" r="4" fill="{base}"/><text x="{tx:.1f}" y="17.5" fill="#f3e9e0" text-anchor="middle">{esc(label)}</text></svg>
'''


def badge(left, right, wl, wr, fill=CRIMSON):
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{wl+wr}" height="24" viewBox="0 0 {wl+wr} 24" font-family="Verdana, DejaVu Sans, sans-serif" font-size="11.5">
<rect width="{wl+wr}" height="24" rx="5" fill="#25252c"/><rect x="{wl}" width="{wr}" height="24" rx="5" fill="{fill}"/><rect x="{wl}" width="6" height="24" fill="{fill}"/>
<text x="{wl/2:.1f}" y="16" fill="#b8b6ae" text-anchor="middle">{esc(left)}</text><text x="{wl+wr/2:.1f}" y="16" fill="#fff" font-weight="bold" text-anchor="middle">{esc(right)}</text></svg>
'''


# ───────────────────────── banner ─────────────────────────
def banner():
    ticked = 11  # of 14
    cells = []
    x0, y0, s, g = 800, 108, 38, 10
    for i in range(14):
        r, c = divmod(i, 7)
        x, y = x0 + c * (s + g), y0 + r * (s + g)
        if i < ticked:
            cells.append(f'<rect x="{x}" y="{y}" width="{s}" height="{s}" rx="8" fill="{CRIMSON}"/>'
                         f'<path d="M{x+11} {y+20} L{x+17} {y+26} L{x+28} {y+13}" fill="none" stroke="#fff" stroke-width="3.2" stroke-linecap="round" stroke-linejoin="round"/>')
        else:
            cells.append(f'<rect x="{x}" y="{y}" width="{s}" height="{s}" rx="8" fill="#2a262c"/>')
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="300" viewBox="0 0 1200 300" font-family="{FONT}">
<rect x="0.5" y="0.5" width="1199" height="299" rx="22" fill="{CARD}" stroke="#2c2630"/>
<rect x="0" y="60" width="6" height="180" rx="3" fill="{CRIMSON}"/>
<text x="70" y="156" font-size="96" font-weight="700" letter-spacing="-2"><tspan fill="#f3e9e0">disci</tspan><tspan fill="{CRIMSON}">plan</tspan></text>
<text x="74" y="212" font-size="30" fill="#d9d0d6">Every day knows what to study.</text>
<text x="{x0}" y="84" font-size="14" font-weight="700" letter-spacing="3" fill="#b8aeb4">WEEK 1 · WEEK 2</text>
{chr(10).join(cells)}
</svg>
'''


def banner_mine():
    cells = []
    x0, y0, s, g = 56, 92, 22, 6
    for i in range(51):
        r, c = divmod(i, 17)
        cells.append(f'<rect x="{x0 + c*(s+g)}" y="{y0 + r*(s+g)}" width="{s}" height="{s}" rx="5" fill="{CRIMSON}"/>')
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="300" viewBox="0 0 1200 300" font-family="{FONT}">
<rect x="0.5" y="0.5" width="1199" height="299" rx="22" fill="{CARD}" stroke="#2c2630"/>
<text x="56" y="66" font-size="14" font-weight="700" letter-spacing="3" fill="#b8aeb4">51 PLANNED DAYS</text>
{chr(10).join(cells)}
<text x="56" y="214" font-size="15" fill="#b8aeb4">one square = one day of the plan</text>
<text x="650" y="120" font-family="Georgia, 'Times New Roman', Times, serif" font-size="52" fill="#f3e9e0">Motivation fades.</text>
<text x="650" y="182" font-family="Georgia, 'Times New Roman', Times, serif" font-size="52" fill="{CRIMSON_L}">Discipline stays.</text>
<text x="650" y="240" font-size="21" fill="#d9d0d6">51 days planned · 8 exams · 1–25 Sept</text>
</svg>
'''


# ───────────────────────── demo module cards and buttons ─────────────────────────
DEMO = {  # k: (colour, light, name, lines, trainer)
    "KAF": ("#6d4fd6", "#a995f5", "Coffee machine technology", ["study page with a state machine", "trainer, 1st generation: terms,", "two chapters, mock exam, cheat sheet"], True),
    "RAD": ("#2563c9", "#7fb0f5", "Bike workshop", ["study page with a practical part", "trainer, 2nd generation: dashboard,", "simulations, cheat sheet"], True),
    "GAR": ("#1b9a5f", "#5fd49a", "Garden planning", ["study page only", "no trainer, mode not analysed yet", "shows a module at the very start"], False),
}


def demo_card(k):
    col, light, name, lines, tr = DEMO[k]
    body = "".join(f'<text x="30" y="{112 + i*23}" font-size="15" fill="#d9d0d6">{esc(t)}</text>' for i, t in enumerate(lines))
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="380" height="196" viewBox="0 0 380 196" font-family="{FONT}">
<defs><linearGradient id="g" x1="0" x2="1"><stop offset="0" stop-color="{light}" stop-opacity=".22"/><stop offset=".6" stop-color="{light}" stop-opacity="0"/></linearGradient></defs>
<rect x="0.5" y="0.5" width="379" height="195" rx="14" fill="{CARD}" stroke="{light}" stroke-opacity=".55"/>
<rect x="1" y="1" width="378" height="194" rx="14" fill="url(#g)"/>
<rect x="0" y="18" width="6" height="160" rx="3" fill="{light}"/>
<rect x="28" y="24" width="64" height="30" rx="15" fill="{light}"/>
<text x="60" y="45" font-size="16" font-weight="800" fill="#131016" text-anchor="middle" letter-spacing="1">{k}</text>
<text x="106" y="46" font-size="11" font-weight="700" letter-spacing="2.5" fill="{light}">DEMO MODULE</text>
<text x="30" y="84" font-size="22" font-weight="700" fill="#f3e9e0">{esc(name)}</text>
{body}
</svg>
'''


def btn(label, light, filled):
    wd = round(len(label) * 7.6 + 40)
    if filled:
        return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{wd}" height="34" viewBox="0 0 {wd} 34" font-family="{FONT}" font-size="14">
<rect x=".5" y=".5" width="{wd-1}" height="33" rx="17" fill="{light}"/><text x="{wd/2}" y="22" fill="#131016" font-weight="700" text-anchor="middle">{esc(label)}</text></svg>
'''
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{wd}" height="34" viewBox="0 0 {wd} 34" font-family="{FONT}" font-size="14">
<rect x="1" y="1" width="{wd-2}" height="32" rx="16" fill="{CARD}" stroke="{light}" stroke-width="2"/><text x="{wd/2}" y="22" fill="{light}" font-weight="700" text-anchor="middle">{esc(label)}</text></svg>
'''


def btn_none(label):
    wd = round(len(label) * 7.6 + 40)
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{wd}" height="34" viewBox="0 0 {wd} 34" font-family="{FONT}" font-size="14">
<rect x="1" y="1" width="{wd-2}" height="32" rx="16" fill="{CARD}" stroke="#6b6470" stroke-width="1.5" stroke-dasharray="4 4"/><text x="{wd/2}" y="22" fill="#b8aeb4" text-anchor="middle">{esc(label)}</text></svg>
'''


def mine_card():
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="120" viewBox="0 0 1200 120" font-family="{FONT}">
<defs><linearGradient id="g" x1="0" x2="1"><stop offset="0" stop-color="{CRIMSON_L}" stop-opacity=".24"/><stop offset=".6" stop-color="{CRIMSON_L}" stop-opacity="0"/></linearGradient></defs>
<rect x="0.5" y="0.5" width="1199" height="119" rx="16" fill="{CARD}" stroke="{CRIMSON_L}" stroke-opacity=".55"/>
<rect x="1" y="1" width="1198" height="118" rx="16" fill="url(#g)"/>
<rect x="0" y="22" width="6" height="76" rx="3" fill="{CRIMSON_L}"/>
<text x="40" y="50" font-size="12" font-weight="700" letter-spacing="3" fill="{CRIMSON_L}">THE REAL THING</text>
<text x="40" y="88" font-size="30" font-weight="700" fill="#f3e9e0">Built for my own exam period</text>
<text x="1160" y="74" font-size="20" fill="#d9d0d6" text-anchor="end">8 exams in 25 days</text>
</svg>
'''


# ───────────────────────── real modules (my exam period) ─────────────────────────
MOD8 = {"NSA": "#5fcf7a", "DB2": "#d678d6", "SIG": "#4fb3f0", "PI2": "#8888f0",
        "ITS": "#58c8b8", "BWR": "#a67cf0", "GSP": "#e8c93a", "BVS2": "#e0606a"}
NEUTRAL = {"#1e1e24", "#16161a", "#e9e8e3", "#25252c", "#2c2c33", "#9a9a92", "#fff"}


def recolor_pill(src_name, key):
    s = open(os.path.join(SRC, src_name), encoding="utf-8").read()
    col = MOD8[key]
    return re.sub(r"#[0-9a-fA-F]{6}\b", lambda m: m.group(0) if m.group(0).lower() in NEUTRAL else col, s)


REMAP = {"#e08858": CRIMSON_L, "#e89058": CRIMSON_L, "#b0522c": CRIMSON}


def recolor_copy(name, dest):
    s = open(os.path.join(SRC, name), encoding="utf-8").read()
    for a, b in REMAP.items():
        s = s.replace(a, b)
    w(os.path.join(dest, name), s)


def contrast(h1, h2):
    def lum(h):
        c = [int(h[i:i + 2], 16) / 255 for i in (1, 3, 5)]
        c = [x / 12.92 if x <= 0.03928 else ((x + .055) / 1.055) ** 2.4 for x in c]
        return .2126 * c[0] + .7152 * c[1] + .0722 * c[2]
    a, b = sorted((lum(h1), lum(h2)), reverse=True)
    return (a + .05) / (b + .05)


def main():
    bad = []
    for z in ZONES:
        w(os.path.join(HERE, f"strip-{z[0]}.svg"), strip(z))
        if contrast(z[4], CARD) < 4.5 or contrast(z[5], CARD) < 7:
            bad.append(z[0])
    navs = [("Try the demo", "demo"), ("How it works", "how"), ("What you get", "get"), ("Use it yourself", "use")]
    for label, k in navs:
        base = [z for z in ZONES if z[0] == k][0][4]
        w(os.path.join(HERE, f"nav-{k}.svg"), nav_pill(label, base))
    w(os.path.join(HERE, "nav-mine.svg"), nav_pill("My exam period", CRIMSON_L))
    w(os.path.join(HERE, "banner.svg"), banner())
    w(os.path.join(HERE, "badge-stdlib.svg"), badge("Python", "stdlib only", 58, 88))
    w(os.path.join(HERE, "badge-server.svg"), badge("server", "none", 50, 50))
    w(os.path.join(HERE, "badge-demo.svg"), badge("demo modules", "3", 100, 28))
    for k, v in DEMO.items():
        w(os.path.join(HERE, f"card-{k.lower()}.svg"), demo_card(k))
        w(os.path.join(HERE, f"btn-study-{k.lower()}.svg"), btn("Study page", v[1], True))
        if v[4]:
            w(os.path.join(HERE, f"btn-trainer-{k.lower()}.svg"), btn("Trainer", v[1], False))
        else:
            w(os.path.join(HERE, f"btn-notrainer-{k.lower()}.svg"), btn_none("no trainer"))
        if contrast(v[1], CARD) < 7:
            bad.append(k)
    w(os.path.join(HERE, "card-mine.svg"), mine_card())
    w(os.path.join(HERE, "btn-story.svg"), btn("Read the story", CRIMSON_L, True))
    # how it works: the existing 5-step diagram, recoloured
    recolor_copy("how-it-works.svg", HERE)
    # my exam period
    w(os.path.join(MINE, "banner.svg"), banner_mine())
    for n in ("hook.svg", "story-button.svg"):
        recolor_copy(n, MINE)
    for z in MINE_ZONES:
        w(os.path.join(MINE, f"strip-{z[0]}.svg"), strip(z))
        if contrast(z[4], CARD) < 4.5 or contrast(z[5], CARD) < 7:
            bad.append(z[0])
    for f in sorted(os.listdir(SRC)):
        m = re.match(r"pill-(doc|trainer)-([a-z0-9]+)\.svg$", f)
        if m:
            w(os.path.join(MINE, f), recolor_pill(f, m.group(2).upper()))
    for k, c in MOD8.items():
        if contrast(c, "#1e1e24") < 4.5:
            bad.append(k)
    if bad:
        sys.exit("contrast too low: " + ", ".join(bad))
    print("ok")


if __name__ == "__main__":
    main()

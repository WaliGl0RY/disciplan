#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""make_readme_assets.py: draws every SVG used by README.md and docs/MY-EXAM-PERIOD.md into docs/images/.

    python scripts/make_readme_assets.py           SVGs, plus a copy of the real screenshots
    python scripts/make_readme_assets.py --shots   also re-shoot the six demo screenshots
                                                   (needs: pip install playwright, and a Chromium)

Palette (see docs/readme-standard/README-STANDARD.md, colours are per repo):
    brand red   #C8102E   bars, borders, fills         (true red, not orange)
    accent text #F0566A   titles, numbers, icons
    dark card   #14111a   every image draws its own card
    borders     #3a1420 / #5a1525
Module colours: one per module, used in the study-document pill AND the trainer pill.

Only the standard library is needed for the SVGs. If Pillow is installed, text widths are
measured with real fonts (wider of Liberation Sans / DejaVu Sans, x 1.06); otherwise estimated.
"""
import datetime
import os
import shutil
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMG = os.path.join(ROOT, "docs", "images")

RED, LIGHT, CARD = "#C8102E", "#F0566A", "#14111a"
B1, B2 = "#3a1420", "#5a1525"
TEXT, MUTED, GREY = "#f3ecee", "#b8aeb4", "#2a2228"
SANS = "Segoe UI, -apple-system, Helvetica, Arial, sans-serif"
SERIF = "Georgia, 'Times New Roman', Times, serif"
VERD = "Verdana, DejaVu Sans, sans-serif"
MONO = "Consolas, 'Cascadia Mono', Menlo, monospace"

# real modules (exam-period page): one colour per module
REAL = {"NSA": "#378ADD", "DB2": "#D4537E", "SIG": "#2E9E5B", "PI2": "#7F77DD",
        "ITS": "#1D9E75", "BWR": "#B04FC9", "GSP": "#D9B100", "BVS2": "#2BB8E0"}
REAL_NAME = {"NSA": "Netzsicherheit und Automation", "DB2": "Datenbanken II", "SIG": "Signalverarbeitung",
             "PI2": "Praktische Informatik 2", "ITS": "IT-Sicherheit", "BWR": "Betriebswirtschaft und Recht",
             "GSP": "Grundlagen der Systemprogrammierung", "BVS2": "Betriebssysteme & Verteilte Systeme 2"}
TRAINERS = ["BWR", "ITS", "PI2", "GSP", "BVS2"]
# demo modules: same colours as klausuren_data.MODULES[..]["col"], the trainer palettes and the cockpit chips
DEMO = {"KAF": "#7C5CD6", "RAD": "#0E8F86", "GAR": "#4C9A2A"}

# ─────────────────────────── text measuring ───────────────────────────
try:
    from PIL import ImageFont
    _F = {}

    def _font(paths, size):
        k = (tuple(paths), size)
        if k not in _F:
            for p in paths:
                if os.path.exists(p):
                    _F[k] = ImageFont.truetype(p, size)
                    break
            else:
                _F[k] = None
        return _F[k]
except ImportError:
    ImageFont = None

_LIB = "/usr/share/fonts/truetype/liberation/LiberationSans-%s.ttf"
_DJV = "/usr/share/fonts/truetype/dejavu/DejaVuSans%s.ttf"


def w(text, size, bold=False, verdana=False):
    """Width in px. Wider of two fonts, x 1.06 (README-STANDARD section 4)."""
    if ImageFont is None:
        return len(text) * size * (0.62 if verdana else 0.56) * (1.06 if not verdana else 1.0) * (1.08 if bold else 1)
    a = _font([_LIB % ("Bold" if bold else "Regular")], size)
    d = _font([_DJV % ("-Bold" if bold else "")], size)
    ws = [f.getlength(text) for f in (a, d) if f]
    if not ws:
        return len(text) * size * 0.58
    return max(ws) * (1.0 if verdana else 1.06)


def esc(t):
    return t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def lum(h):
    c = [int(h[i:i + 2], 16) / 255 for i in (1, 3, 5)]
    c = [x / 12.92 if x <= 0.03928 else ((x + 0.055) / 1.055) ** 2.4 for x in c]
    return 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2]


def on(h):
    """Text colour with the better contrast on fill h."""
    lh = lum(h)
    cw = 1.05 / (lh + 0.05)
    cd = (lh + 0.05) / (lum("#0b0a0f") + 0.05)
    return "#ffffff" if cw >= cd else "#0b0a0f"


def save(name, svg):
    p = os.path.join(IMG, name)
    with open(p, "w", encoding="utf-8", newline="\n") as f:
        f.write(svg.strip() + "\n")


def head(wd, ht, font=SANS):
    return '<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" viewBox="0 0 %d %d" font-family="%s">' % (wd, ht, wd, ht, font)


def card(wd, ht, rx=14, stroke=B2):
    return '<rect x="0.5" y="0.5" width="%d" height="%d" rx="%d" fill="%s" stroke="%s"/>' % (wd - 1, ht - 1, rx, CARD, stroke)


# ─────────────────────────── components ───────────────────────────
ICONS = {
    "play": '<path d="M-5 -9 L10 0 L-5 9 Z"/>',
    "flow": '<circle cx="-9" cy="-6" r="3.5"/><circle cx="9" cy="0" r="3.5"/><circle cx="-9" cy="8" r="3.5"/><path d="M-6 -5 L6 -1"/><path d="M-6 7 L6 1"/>',
    "grid": '<rect x="-11" y="-11" width="9" height="9" rx="2"/><rect x="2" y="-11" width="9" height="9" rx="2"/><rect x="-11" y="2" width="9" height="9" rx="2"/><rect x="2" y="2" width="9" height="9" rx="2"/>',
    "term": '<rect x="-12" y="-10" width="24" height="20" rx="3"/><path d="M-7 -3 L-3 0 L-7 3"/><path d="M0 4 H6"/>',
    "tree": '<path d="M-10 -9 H-2 L1 -6 H10 V9 H-10 Z"/><path d="M-4 1 H4"/>',
    "cal": '<rect x="-11" y="-9" width="22" height="20" rx="3"/><path d="M-11 -2 H11"/><path d="M-6 -12 V-7"/><path d="M6 -12 V-7"/>',
    "book": '<path d="M-12 -8 C-7 -10 -3 -9 0 -6 C3 -9 7 -10 12 -8 V9 C7 7 3 8 0 10 C-3 8 -7 7 -12 9 Z"/><path d="M0 -6 V10"/>',
    "check": '<circle cx="0" cy="0" r="10"/><path d="M-5 0 L-1.5 4 L5.5 -4"/>',
    "flag": '<path d="M-8 11 V-10"/><path d="M-8 -9 H9 L5 -3 L9 3 H-8"/>',
    "bars": '<path d="M-10 10 V2"/><path d="M-3 10 V-4"/><path d="M4 10 V-9"/><path d="M11 10 V-1"/>',
}


def zone_strip(nn, title, sub, icon):
    """README-STANDARD 'Zone header strip', 1200 x 84, in brand red."""
    return head(1200, 84) + '''
<defs><linearGradient id="g" x1="0" x2="1" y1="0" y2="0"><stop offset="0" stop-color="%(R)s" stop-opacity=".28"/><stop offset=".55" stop-color="%(R)s" stop-opacity="0"/></linearGradient></defs>
<rect x="0.5" y="0.5" width="1199" height="83" rx="14" fill="%(C)s" stroke="%(B)s"/>
<rect x="1" y="1" width="1198" height="82" rx="14" fill="url(#g)"/>
<rect x="0" y="16" width="6" height="52" rx="3" fill="%(R)s"/>
<circle cx="62" cy="42" r="24" fill="%(R)s" fill-opacity=".16" stroke="%(R)s" stroke-width="1.5"/>
<g transform="translate(62 42)" fill="none" stroke="%(L)s" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">%(I)s</g>
<text x="106" y="33" fill="%(L)s" font-size="12" font-weight="700" letter-spacing="3">%(N)s</text>
<text x="104" y="60" fill="%(L)s" font-size="27" font-weight="700" letter-spacing="-0.3">%(T)s</text>
<text x="1172" y="49" fill="%(M)s" font-size="15" text-anchor="end">%(S)s</text>
</svg>''' % dict(R=RED, C=CARD, B=B2, L=LIGHT, I=ICONS[icon], N=nn, T=esc(title), S=esc(sub), M=MUTED)


def nav_pill(label):
    wd = round(len(label) * 7.3 + 42)
    tx = 26 + (len(label) * 7.3 + 2) / 2
    return head(wd, 26, VERD) + '''
<rect x=".5" y=".5" width="%d" height="25" rx="13" fill="#1c1418" stroke="%s"/>
<circle cx="15" cy="13" r="4" fill="%s"/><text x="%.1f" y="17.5" fill="#f3e9e0" font-size="12" text-anchor="middle">%s</text></svg>''' % (wd - 1, RED, RED, tx, esc(label))


def badge(left, right):
    lw, rw = round(w(left, 11.5, verdana=True) + 18), round(w(right, 11.5, True, verdana=True) + 18)
    return head(lw + rw, 24, VERD) + '''
<rect width="%d" height="24" rx="5" fill="#2a2228"/><rect x="%d" width="%d" height="24" rx="5" fill="%s"/><rect x="%d" width="6" height="24" fill="%s"/>
<text x="%.1f" y="16" fill="%s" font-size="11.5" text-anchor="middle">%s</text><text x="%.1f" y="16" fill="#fff" font-size="11.5" font-weight="bold" text-anchor="middle">%s</text></svg>''' % (
        lw + rw, lw, rw, RED, lw, RED, lw / 2, MUTED, esc(left), lw + rw / 2, esc(right))


def button(label, colour, outline=False):
    wd = round(w(label, 13, True, verdana=True) + 44)
    if outline:
        return head(wd, 36, VERD) + '''
<rect x="1" y="1" width="%d" height="34" rx="17" fill="%s" stroke="#4a4148" stroke-width="1.5" stroke-dasharray="4 3"/>
<text x="%.1f" y="23" fill="%s" font-size="13" text-anchor="middle">%s</text></svg>''' % (wd - 2, CARD, wd / 2, MUTED, esc(label))
    return head(wd, 36, VERD) + '''
<rect x="0" y="0" width="%d" height="36" rx="18" fill="%s"/>
<text x="%.1f" y="23" fill="%s" font-size="13" font-weight="bold" text-anchor="middle">%s</text></svg>''' % (wd, colour, wd / 2, on(colour), esc(label))


def pill(key, colour, label):
    kw = max(48, round(w(key, 12, True, verdana=True) + 26))
    wd = kw + round(w(label, 12, verdana=True) + 30)
    return head(wd, 28, VERD) + '''
<rect x=".5" y=".5" width="%d" height="27" rx="14" fill="#1c1418" stroke="%s"/>
<rect x=".5" y=".5" width="%d" height="27" rx="14" fill="%s"/><rect x="%d" y=".5" width="14" height="27" fill="%s"/>
<text x="%.1f" y="18.5" fill="%s" font-size="12" font-weight="bold" text-anchor="middle">%s</text>
<text x="%.1f" y="18.5" fill="#f3e9e0" font-size="12" text-anchor="middle">%s</text></svg>''' % (
        wd - 1, colour, kw, colour, kw - 14, colour, kw / 2, on(colour), esc(key), kw + (wd - kw) / 2, esc(label))


# ─────────────────────────── README images ───────────────────────────
def banner():
    sq, gap = 52, 10
    x0, y0 = 1200 - 72 - (7 * sq + 6 * gap), 94
    o = [head(1200, 300), card(1200, 300)]
    o.append('<text x="68" y="158" font-size="104" font-weight="700" letter-spacing="-3"><tspan fill="%s">disci</tspan><tspan fill="%s">plan</tspan></text>' % (TEXT, RED))
    o.append('<text x="72" y="212" fill="#d9ced2" font-size="30">Every day knows what to study.</text>')
    for i in range(14):
        r, c = divmod(i, 7)
        x, y = x0 + c * (sq + gap), y0 + r * (sq + gap)
        if i < 9:
            o.append('<rect x="%d" y="%d" width="%d" height="%d" rx="9" fill="%s"/>' % (x, y, sq, sq, RED))
            o.append('<path d="M%d %d l8 9 l15 -17" fill="none" stroke="#fff" stroke-opacity=".9" stroke-width="3.5" stroke-linecap="round" stroke-linejoin="round"/>' % (x + 14, y + 27))
        else:
            o.append('<rect x="%d" y="%d" width="%d" height="%d" rx="9" fill="%s"/>' % (x, y, sq, sq, GREY))
    o.append("</svg>")
    return "\n".join(o)


def demo_card(k, name, line1, line2, colour):
    wd, ht = 380, 150
    kw = round(w(k, 17, True) + 28)
    o = [head(wd, ht), card(wd, ht, 14, B2)]
    o.append('<rect x="0" y="14" width="6" height="%d" rx="3" fill="%s"/>' % (ht - 28, colour))
    o.append('<rect x="24" y="22" width="%d" height="30" rx="15" fill="%s"/>' % (kw, colour))
    o.append('<text x="%.1f" y="43" fill="%s" font-size="17" font-weight="700" text-anchor="middle">%s</text>' % (24 + kw / 2, on(colour), k))
    o.append('<text x="%d" y="43" fill="%s" font-size="16" font-weight="700">%s</text>' % (24 + kw + 12, TEXT, esc(name)))
    o.append('<text x="24" y="82" fill="%s" font-size="14">%s</text>' % (MUTED, esc(line1)))
    o.append('<text x="24" y="108" fill="%s" font-size="14">%s</text>' % (MUTED, esc(line2)))
    o.append('<text x="24" y="132" fill="%s" font-size="12" letter-spacing="1.5" font-weight="700">DEMO · INVENTED CONTENT</text>' % colour_text(colour))
    o.append("</svg>")
    need = 24 + kw + 12 + w(name, 16, True)
    assert need < wd - 14, (k, need)
    for t in (line1, line2):
        assert 24 + w(t, 14) < wd - 14, t
    return "\n".join(o)


def colour_text(c):
    """Module colour made readable as text on the dark card (lift lightness if needed)."""
    if lum(c) >= 0.18:
        return c
    r, g, b = [int(c[i:i + 2], 16) for i in (1, 3, 5)]
    f = 0.45
    r, g, b = [round(x + (255 - x) * f) for x in (r, g, b)]
    return "#%02x%02x%02x" % (r, g, b)


def how_it_works():
    steps = [
        ("1", "Material", ["quellen/", "altklausuren/"], "slides, scripts, old exams"),
        ("2", "Analysis", ["mode per module"], "what the exam rewards"),
        ("3", "Build", ["<K>.html", "trainer/", "fehler-log.md"], "doc · self-test · error log"),
        ("4", "Plan", ["klausuren_data.py"], "days with checkable steps"),
        ("5", "Cockpit", ["klausuren.html"], "one offline page"),
    ]
    bw, gap, x0 = 208, 24, 32
    o = [head(1200, 290), card(1200, 290, 18),
         '<defs><marker id="ar" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="%s"/></marker></defs>' % RED]
    for i, (n, t, chips, cap) in enumerate(steps):
        x = x0 + i * (bw + gap)
        last = i == len(steps) - 1
        o.append('<rect x="%d" y="40" width="%d" height="204" rx="14" fill="#1c1418" stroke="%s" stroke-width="%s"/>' % (x, bw, RED if last else B1, 2 if last else 1))
        o.append('<circle cx="%d" cy="72" r="15" fill="%s"/><text x="%d" y="77.5" fill="#fff" font-size="15" font-weight="700" text-anchor="middle">%s</text>' % (x + 30, RED, x + 30, n))
        o.append('<text x="%d" y="78" fill="%s" font-size="19" font-weight="700">%s</text>' % (x + 56, TEXT, t))
        for j, c in enumerate(chips):
            cw = round(len(c) * 8.4 + 18)
            o.append('<rect x="%d" y="%d" width="%d" height="24" rx="6" fill="#2a2228"/><text x="%d" y="%d" fill="%s" font-size="14" font-family="%s">%s</text>' % (
                x + 16, 106 + j * 30, cw, x + 25, 122.5 + j * 30, LIGHT, MONO, esc(c)))
            assert cw < bw - 20, c
        o.append('<text x="%d" y="226" fill="%s" font-size="13">%s</text>' % (x + 16, MUTED, esc(cap)))
        assert w(cap, 13) < bw - 24, cap
        if not last:
            o.append('<line x1="%d" y1="142" x2="%d" y2="142" stroke="%s" stroke-width="2.5" marker-end="url(#ar)"/>' % (x + bw + 3, x + bw + gap - 3, RED))
    o.append("</svg>")
    return "\n".join(o)


def exam_card():
    return head(1200, 170) + '''
<defs><linearGradient id="g" x1="0" x2="1" y1="0" y2="0"><stop offset="0" stop-color="%(R)s" stop-opacity=".28"/><stop offset=".6" stop-color="%(R)s" stop-opacity="0"/></linearGradient></defs>
<rect x="0.5" y="0.5" width="1199" height="169" rx="16" fill="%(C)s" stroke="%(R)s" stroke-opacity=".6"/>
<rect x="1" y="1" width="1198" height="168" rx="16" fill="url(#g)"/>
<rect x="0" y="20" width="7" height="130" rx="3.5" fill="%(R)s"/>
<text x="48" y="64" fill="%(L)s" font-size="13" font-weight="700" letter-spacing="3">MY OWN EXAM PERIOD</text>
<text x="48" y="110" fill="%(T)s" font-size="38" font-family="%(SE)s">Built for my own exam period: <tspan fill="%(L)s">8 exams in 25 days</tspan></text>
<text x="48" y="144" fill="%(M)s" font-size="17">The real plan, the real study documents and the real trainers, from the September 2026 run.</text>
</svg>''' % dict(R=RED, C=CARD, L=LIGHT, T=TEXT, M=MUTED, SE=SERIF)


# ─────────────────────────── exam-period page ───────────────────────────
def exam_banner():
    sq, gap, cols = 30, 8, 9
    x0, y0 = 72, 66
    o = [head(1200, 340), card(1200, 340)]
    o.append('<text x="%d" y="44" fill="%s" font-size="13" font-weight="700" letter-spacing="3">51 PLANNED DAYS</text>' % (x0, LIGHT))
    for i in range(51):
        r, c = divmod(i, cols)
        o.append('<rect x="%d" y="%d" width="%d" height="%d" rx="6" fill="%s"/>' % (x0 + c * (sq + gap), y0 + r * (sq + gap), sq, sq, RED))
    yb = y0 + 6 * (sq + gap) - gap + 30
    o.append('<text x="%d" y="%d" fill="%s" font-size="15">one square = one day of the plan</text>' % (x0, yb, MUTED))
    o.append('<text x="520" y="140" fill="%s" font-size="60" font-family="%s">Motivation fades.</text>' % (TEXT, SERIF))
    o.append('<text x="520" y="214" fill="%s" font-size="60" font-family="%s">Discipline stays.</text>' % (LIGHT, SERIF))
    o.append('<line x1="522" y1="246" x2="602" y2="246" stroke="%s" stroke-width="3" stroke-linecap="round"/>' % RED)
    o.append('<text x="520" y="286" fill="#d9ced2" font-size="23">51 days planned · 8 exams · 1–25 Sept</text>')
    o.append("</svg>")
    return "\n".join(o)


def quote_card():
    return head(1000, 290) + '''
<rect x="0.5" y="0.5" width="999" height="289" rx="18" fill="%(C)s" stroke="%(B)s"/>
<rect x="0" y="32" width="8" height="226" rx="4" fill="%(R)s"/>
<text x="48" y="124" fill="%(T)s" font-size="50" font-family="%(SE)s">Eight exams. Twenty-five days.</text>
<text x="48" y="190" fill="%(L)s" font-size="50" font-family="%(SE)s">Too much for one head.</text>
<text x="48" y="256" fill="%(T)s" font-size="50" font-family="%(SE)s">So I planned it first.</text>
</svg>''' % dict(C=CARD, B=B2, R=RED, T=TEXT, L=LIGHT, SE=SERIF)


def numbers():
    items = [("51", "days planned"), ("269", "blocks"), ("5", "trainers"), ("8", "exams")]
    tw, gap = 266, 24
    o = [head(1200, 150), card(1200, 150, 16)]
    for i, (n, t) in enumerate(items):
        x = 32 + i * (tw + gap)
        o.append('<rect x="%d" y="26" width="%d" height="98" rx="12" fill="#1c1418" stroke="%s"/>' % (x, tw, B1))
        o.append('<rect x="%d" y="40" width="5" height="70" rx="2.5" fill="%s"/>' % (x, RED))
        o.append('<text x="%d" y="86" fill="%s" font-size="52" font-weight="700" letter-spacing="-1">%s</text>' % (x + 26, LIGHT, n))
        o.append('<text x="%d" y="112" fill="%s" font-size="17">%s</text>' % (x + 28, MUTED, t))
    o.append("</svg>")
    return "\n".join(o)


# ─────────────────────────── demo screenshots ───────────────────────────
def shoot():
    """Six 800 x 500 demo screenshots (dark mode). Fixed clocks, because the demo plan runs 26 Aug - 7 Sep 2026."""
    from playwright.sync_api import sync_playwright
    exe = os.environ.get("CHROME", "/opt/pw-browsers/chromium-1194/chrome-linux/chrome")
    kw = {"executable_path": exe} if os.path.exists(exe) else {}
    uri = lambda p: "file://" + os.path.join(ROOT, p)
    out = lambda n: os.path.join(IMG, n)
    with sync_playwright() as p:
        b = p.chromium.launch(**kw)

        def page(day, vw=1120, crop=None):
            vh = round(vw / 1.6)
            ctx = b.new_context(viewport={"width": vw, "height": vh}, color_scheme="dark",
                                device_scale_factor=800 / (crop or vw))
            pg = ctx.new_page()
            pg.clock.set_fixed_time(day)
            return pg

        aug28, aug31, sep30 = (datetime.datetime(2026, 8, 28, 9), datetime.datetime(2026, 8, 31, 9),
                               datetime.datetime(2026, 9, 30, 9))
        # 1 cockpit: the three module cards
        pg = page(aug31, 1280, crop=1040)
        pg.goto(uri("klausuren.html")); pg.wait_for_timeout(400)
        pg.screenshot(path=out("shot-cockpit-modules.png"), clip={"x": 232, "y": 16, "width": 1040, "height": 650})
        # 2 cockpit: the week and the day
        pg = page(aug28)
        pg.goto(uri("klausuren.html")); pg.wait_for_timeout(300)
        pg.click('.tab:has-text("Tagesplan")'); pg.wait_for_timeout(300)
        pg.evaluate("window.scrollTo(0, document.querySelector('.lauf').getBoundingClientRect().top + window.scrollY - 12)")
        pg.wait_for_timeout(300)
        pg.screenshot(path=out("shot-cockpit-plan.png"))
        # 3 cockpit: one block opened, with its steps
        pg.evaluate("document.querySelector('.lt .chev').click()"); pg.wait_for_timeout(500)
        pg.screenshot(path=out("shot-cockpit-steps.png"))
        # 4 study document: the state diagram
        pg = page(aug31)
        pg.goto(uri("klausuren.html")); pg.wait_for_timeout(300)
        pg.click("#side .nl[data-go=KAF]"); pg.wait_for_timeout(300)
        pg.evaluate("[...document.querySelectorAll('#m-KAF a')].find(a => /zustand/.test(a.getAttribute('href') || '')).click()")
        pg.wait_for_timeout(700)
        pg.screenshot(path=out("shot-study-doc.png"))
        # 5, 6 trainers (the RAD countdown is relative to its build day, so they get their own clock)
        pg = page(sep30, 1280)
        pg.goto(uri("module/KAF/KAF-Trainer.html")); pg.wait_for_timeout(500)
        pg.screenshot(path=out("shot-trainer-kaf.png"))
        pg.goto(uri("module/RAD/RAD-Trainer.html")); pg.wait_for_timeout(500)
        pg.screenshot(path=out("shot-trainer-rad.png"))
        b.close()


# ─────────────────────────── main ───────────────────────────
def main():
    os.makedirs(IMG, exist_ok=True)
    # README
    save("banner.svg", banner())
    save("badge-stdlib.svg", badge("Python", "stdlib only"))
    save("badge-server.svg", badge("runs from", "file, no server"))
    save("badge-modules.svg", badge("demo", "3 modules"))
    for slug, label in [("demo", "Try the demo"), ("how", "How it works"), ("get", "What you get"),
                        ("use", "Use it yourself"), ("where", "Where things are"), ("exam", "My exam period")]:
        save("nav-%s.svg" % slug, nav_pill(label))
    save("zone-demo.svg", zone_strip("01", "Try the demo", "three invented modules, open them in your browser", "play"))
    save("zone-how.svg", zone_strip("02", "How it works", "from material to one offline page", "flow"))
    save("zone-get.svg", zone_strip("03", "What you get", "screenshots of the demo, dark mode", "grid"))
    save("zone-use.svg", zone_strip("04", "Use it yourself", "three steps", "term"))
    save("zone-where.svg", zone_strip("05", "Where things are", "what is in each folder, and when to open it", "tree"))
    save("zone-built.svg", zone_strip("06", "How I built it and what the AI did", "I decided and tested, Claude coded", "check"))
    cards = [("KAF", "Kaffeemaschinen-Technik", "Exam 2 Sept · 10:00 · first attempt", "study document + first-generation trainer"),
             ("RAD", "Fahrrad-Werkstatt", "Exam 4 Sept · 14:00 · second attempt", "practical module, trainer with simulations"),
             ("GAR", "Gartenplanung", "Exam 7 Sept · elective", "study document only, mode still open")]
    for k, n, a, b2 in cards:
        save("card-%s.svg" % k.lower(), demo_card(k, n, a, b2, DEMO[k]))
        save("btn-study-%s.svg" % k.lower(), button("Study page", DEMO[k]))
    save("btn-trainer-kaf.svg", button("Trainer", DEMO["KAF"]))
    save("btn-trainer-rad.svg", button("Trainer", DEMO["RAD"]))
    save("btn-trainer-gar.svg", button("no trainer", DEMO["GAR"], outline=True))
    save("how-it-works.svg", how_it_works())
    save("exam-card.svg", exam_card())
    save("btn-read-story.svg", button("Read the story  →", RED))
    # exam-period page
    save("exam-banner.svg", exam_banner())
    save("ep-quote.svg", quote_card())
    save("ep-numbers.svg", numbers())
    save("ep-zone-stopped.svg", zone_strip("01", "How I stopped owing exams", "eight exams, one plan", "flag"))
    save("ep-zone-docs.svg", zone_strip("02", "Study documents", "one per module, pick one", "book"))
    save("ep-zone-trainers.svg", zone_strip("03", "Trainers", "five self-test apps, pick one", "check"))
    save("ep-zone-plan.svg", zone_strip("04", "A day in the real plan", "blocks, steps, the end-of-day line", "cal"))
    save("ep-zone-numbers.svg", zone_strip("05", "In numbers", "the September 2026 run", "bars"))
    for k, c in REAL.items():
        save("pill-doc-%s.svg" % k.lower(), pill(k, c, REAL_NAME[k]))
    for k in TRAINERS:
        save("pill-trainer-%s.svg" % k.lower(), pill(k, REAL[k], "Trainer"))
    # real screenshots: copied from examples/source (that folder stays untouched)
    src = os.path.join(ROOT, "examples", "source", "docs", "readme")
    for f in sorted(os.listdir(src)):
        if f.startswith(("doc-", "trainer-", "plan-")):
            shutil.copyfile(os.path.join(src, f), os.path.join(IMG, f))
    if "--shots" in sys.argv:
        shoot()
    print("OK ->", IMG)


if __name__ == "__main__":
    main()

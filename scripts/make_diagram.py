#!/usr/bin/env python3
"""make_diagram.py: draws the demo state diagram (a coffee machine, invented example).

Output: docs/images/kaffeemaschine-zustaende.svg, plus the same drawing inline in
module/KAF/KAF.html (between <!--SVG--> and <!--/SVG-->).

Arrowheads are drawn as polygons instead of SVG markers: build.py namespaces
element ids when it merges module documents into the cockpit, but it does not
rewrite url(#...) references, so markers would disappear there.
"""
import html, math, os

BG, BOX, EDGE, HOT, TXT, OUT, LBL = "#241f35", "#110f16", "#54525b", "#a48bf0", "#e9e6f2", "#a48bf0", "#8fa6c9"
W, H = 165, 62

STATES = {  # name: (x, y, output line 1, output line 2, initial?)
    "AUS":       (30, 179, "Heizung aus", "Pumpe aus", True),
    "AUFHEIZEN": (290, 40, "Heizung an", "LED blinkt", False),
    "BEREIT":    (610, 40, "Heizung regelt", "LED an", False),
    "BRÜHEN":    (610, 318, "Pumpe an", "Zähler + 1", False),
    "ENTKALKEN": (290, 318, "Pumpe im Intervall", "LED rot", False),
}
# (path d, label x, label y, label, highlighted?)
EDGES = [
    ("M195,192 C232,152 252,92 286,74", 236, 118, "Ein-Taste", False),
    ("M455,62 L606,62", 530, 52, "T ≥ 93 °C", False),
    ("M606,84 L459,84", 530, 103, "T < 90 °C", False),
    ("M676,102 L676,314", 632, 214, "Bezug-Taste", True),
    ("M716,314 L716,106", 772, 214, "Menge erreicht", False),
    ("M606,349 L459,349", 532, 339, "Zähler ≥ 200", False),
    ("M372,316 L372,106", 322, 214, "Programm fertig", False),
    ("M290,370 C232,370 150,330 120,245", 178, 372, "Aus-Taste", False),
]


def arrowhead(d):
    """Triangle at the end of a path, pointing along its last segment."""
    nums = [float(v) for v in d.replace("M", " ").replace("L", " ").replace("C", " ").replace(",", " ").split()]
    (x0, y0), (x1, y1) = (nums[-4], nums[-3]), (nums[-2], nums[-1])
    a = math.atan2(y1 - y0, x1 - x0)
    pts = [(x1, y1),
           (x1 - 10 * math.cos(a) + 5 * math.sin(a), y1 - 10 * math.sin(a) - 5 * math.cos(a)),
           (x1 - 10 * math.cos(a) - 5 * math.sin(a), y1 - 10 * math.sin(a) + 5 * math.cos(a))]
    return " ".join("%.1f,%.1f" % p for p in pts)


def svg():
    o = ['<svg xmlns="http://www.w3.org/2000/svg" viewBox="-20 -70 980 520" font-family="sans-serif" role="img" '
         'aria-label="Zustandsdiagramm einer Kaffeemaschine (Demo)">',
         '<rect x="-20" y="-70" width="980" height="520" fill="%s"/>' % BG,
         '<text x="10" y="-38" fill="%s" font-size="17" font-weight="bold">Kaffeemaschine — Zustandsdiagramm (Demo)</text>' % TXT,
         '<text x="10" y="-16" fill="%s" font-size="12">Moore-Automat: die Ausgaben (violett) hängen am Zustand, '
         'die Übergänge (blau) an Ereignissen.</text>' % LBL]
    o.append('<circle cx="12" cy="210" r="5" fill="#7C5CD6"/><path d="M18,210 L26,210" stroke="#918e9a" stroke-width="2"/>'
             '<polygon points="%s" fill="#918e9a"/>' % arrowhead("M18,210 L28,210"))
    for d, lx, ly, lab, hot in EDGES:
        col = HOT if hot else "#918e9a"
        o.append('<path d="%s" stroke="%s" stroke-width="2" fill="none"/><polygon points="%s" fill="%s"/>'
                 % (d, col, arrowhead(d), col))
        o.append('<text x="%d" y="%d" fill="%s" font-size="13" text-anchor="middle">%s</text>' % (lx, ly, LBL, html.escape(lab)))
    for name, (x, y, a, b, init) in STATES.items():
        o.append('<rect x="%d" y="%d" width="%d" height="%d" rx="8" fill="%s" stroke="%s" stroke-width="%s"/>'
                 % (x, y, W, H, BOX, HOT if init else EDGE, "2.5" if init else "2"))
        cx = x + W // 2
        o.append('<text x="%d" y="%d" fill="%s" font-size="15" font-weight="bold" text-anchor="middle">%s</text>' % (cx, y + 24, TXT, name))
        o.append('<text x="%d" y="%d" fill="%s" font-size="11.5" text-anchor="middle">%s</text>' % (cx, y + 40, OUT, a))
        o.append('<text x="%d" y="%d" fill="%s" font-size="11.5" text-anchor="middle">%s</text>' % (cx, y + 55, OUT, b))
    o.append('<text x="10" y="435" fill="#918e9a" font-size="11">Erfundenes Beispiel. Der hervorgehobene Pfeil ist der '
             'Normalbetrieb; „Aus-Taste" gilt sinngemäß aus jedem Zustand (nur einmal gezeichnet).</text>')
    o.append("</svg>")
    return "\n".join(o)


if __name__ == "__main__":
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))   # Repo-Wurzel
    out = os.path.join(root, "docs", "images", "kaffeemaschine-zustaende.svg")
    open(out, "w", encoding="utf-8", newline="\n").write(svg() + "\n")
    print("OK ->", out)
    # the same drawing, inline in the demo study document (between the markers)
    doc = os.path.join(root, "module", "KAF", "KAF.html")
    if os.path.exists(doc):
        t = open(doc, encoding="utf-8").read()
        a, b = t.index("<!--SVG-->") + len("<!--SVG-->"), t.index("<!--/SVG-->")
        open(doc, "w", encoding="utf-8", newline="\n").write(t[:a] + svg() + t[b:])
        print("OK ->", os.path.normpath(doc), "(inline)")

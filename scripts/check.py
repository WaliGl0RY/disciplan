#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""check.py — eine Textpruefung statt zehn Screenshots.

    python3 scripts/check.py         alles, fuer alle Module
    python3 scripts/check.py KAF     nur ein Modul
    python3 scripts/check.py KAF --plan zusaetzlich die Planpruefungen

Prueft, ohne Browser:
  1 tote Anker im Modul-HTML
  2 Codebloecke, die nicht als Python parsen
  3 <pre>-Zeilen breiter als das Layout (Standard 92 Zeichen)
  4 Klassennamen, die mit dem unscoped CSS der Shell kollidieren
  5 Dunkelmodus-Regeln, die background setzen aber color vergessen
  6 (--plan) tote Plan-Anker, Tagesminuten, Block-Minuten gegen Schrittsumme
Rueckgabe 0 = sauber, 1 = Befunde.
"""
import sys, os, re, io, ast, html, json, glob

MAXCOL = 118   # gemessen: 123 Zeichen passen in die Spalte, 118 ist der sichere Rand
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))   # Repo-Wurzel (Skripte liegen in scripts/)
findings = []


def note(kind, msg):
    findings.append((kind, msg))
    print("  [%s] %s" % (kind, msg))


def read(p):
    return io.open(p, encoding="utf-8").read()


# ── 1-3 · pro Modul-HTML ─────────────────────────────────────────────────────
def check_html(path):
    s = read(path)
    name = os.path.basename(path)
    print("\n== %s  (%d KB)" % (name, len(s) // 1024))

    ids = set(re.findall(r'id="([^"]+)"', s))
    dead = sorted({h for h in re.findall(r'href="#([^"]+)"', s) if h not in ids})
    if dead:
        note("ANKER", "tot: " + ", ".join(dead[:12]) + (" …" if len(dead) > 12 else ""))

    # unescapte spitze Klammern in <pre>: der Browser frisst sie als unbekanntes Tag,
    # und <filename> ist dann unsichtbar. Genau das ist am 19.09. passiert.
    # echte Inline-Tags sind erlaubt; alles andere ist vermutlich ein Platzhalter
    OK = ("span", "b", "a", "code", "i", "u", "sup", "sub", "br", "em", "strong",
          "mark", "small", "kbd", "samp", "var", "abbr", "s", "del", "ins")
    for m in re.finditer(r'<pre[^>]*>(.*?)</pre>', s, re.S):
        for _slash, tag, _rest in re.findall(r'<(/?)([a-zA-Z][\w-]*)([^>]*)>', m.group(1)):
            if tag.lower() not in OK:
                note("ESCAPE", "<%s> in einem <pre> ist nicht escapt -> der Browser "
                               "verschluckt es. Schreib &lt;%s&gt;" % (tag, tag))

    n_code = n_bad = 0
    for m in re.finditer(r'<pre[^>]*>(.*?)</pre>', s, re.S):
        raw = m.group(1)
        raw = re.sub(r'<span class="op">\[(.*?)\]</span>', r'\1', raw, flags=re.S)  # [OPTIONAL]-Markierung auf dem Blatt
        t = html.unescape(re.sub('<[^>]+>', '', raw))
        if "\\n" in t:          # als JS-String hinterlegte Daten, keine Anzeige
            continue
        # Breite
        for i, line in enumerate(t.strip("\n").split("\n")):
            if len(line) > MAXCOL:
                note("BREIT", "%d Zeichen (max %d): %s" % (len(line), MAXCOL, line[:60].strip()))
                break
        # Python?
        head = t.lstrip()[:40]
        if head.startswith("import java") or "public class" in t or ");" in t[:200]:
            continue          # Java o.ae., nicht als Python pruefen
        if head.startswith(("from flask", "import ", "# api_server", "# server", "async def", "def ")):
            n_code += 1
            try:
                ast.parse(t)
            except SyntaxError as e:
                n_bad += 1
                note("PYTHON", "%s Zeile %s: %s" % (head.split("\n")[0][:30], e.lineno, e.msg))
    print("  %d Codebloecke geprueft, %d fehlerhaft" % (n_code, n_bad))
    return s


# ── 4-5 · Kollisionen und Dunkelmodus ────────────────────────────────────────
SHELLSET = {}   # Klasse -> Eigenschaften, die die Shell unscoped setzt


def defines(css_text, cls):
    """Definiert das Modul-CSS diese Klasse in IRGENDEINER Selektorform?
       .mini,.fine{...} und .st .sn{...} zaehlen mit."""
    return re.search(r'(?:^|\n|,)[^{}\n]*\.' + re.escape(cls) + r'\b[^{}]*\{', css_text) is not None


def check_shell(modul_html, built="klausuren.html"):
    p = os.path.join(ROOT, built)
    if not os.path.exists(p):
        return
    k = read(p)
    head = k[:k.index("#m-")] if "#m-" in k else k
    shell = {}
    for m in re.finditer(r'\.([a-zA-Z][\w-]*)\s*\{([^{}]*)\}', re.sub(r'/\*.*?\*/', '', head, flags=re.S)):
        shell.setdefault(m.group(1), m.group(2))
    used = set()
    for u in re.findall(r'class="([^"]+)"', modul_html):
        used.update(u.split())
    hit = sorted(used & set(shell))
    if hit:
        print("  Klassen, die auch unscoped in der Shell stehen: " + ", ".join(hit))
        for h in hit:
            props = {x.split(":")[0].strip() for x in shell[h].split(";") if ":" in x}
            SHELLSET[h] = props
            if not defines(modul_html, h):
                note("SHELL", ".%s wird von der Shell gesetzt (%s) und im Modul gar nicht "
                              "definiert -> die Shell gewinnt"
                     % (h, ", ".join(sorted(props))))


def check_dark(s):
    i = s.find("prefers-color-scheme: dark")
    if i < 0:
        return
    dark = s[i:]
    end = dark.find("\n</style>")
    dark = dark[:end if end > 0 else len(dark)]
    for m in re.finditer(r'(?:^|\n)(\.[a-zA-Z][\w-]*)\s*\{([^}]*)\}', dark):
        body = m.group(2)
        cls = m.group(1).lstrip(".")
        hat_bg = "background" in body
        hat_col = "color:" in body.replace("background-color", "").replace("border-color", "")
        # nur riskant, wenn die Shell fuer dieselbe Klasse eine Farbe erzwingt
        if hat_bg and not hat_col and "color" in SHELLSET.get(cls, ()):
            note("DUNKEL", ".%s setzt im Dunkelmodus background, aber keine color — und die Shell "
                           "setzt unscoped color. Genau so entsteht dunkel auf dunkel." % cls)


# ── 6 · Plan ─────────────────────────────────────────────────────────────────
def check_plan(modul):
    b = os.path.join(ROOT, "klausuren_data.py")  # Tagesplan, seit 28.09.2026 aus build.py ausgelagert
    k = os.path.join(ROOT, "klausuren.html")
    if not (os.path.exists(b) and os.path.exists(k)):
        return
    print("\n== Plan (build.py gegen klausuren.html)")
    s, kk = read(b), read(k)
    ids = set(re.findall(r'id="([^"]+)"', kk))
    bad = set()
    pat = r'\("' + modul + r'",(\d+),"([A-Z])","[^"]*","([a-z0-9-]*)",(\[\{.*?\}\]),\['
    for mn, ty, anc, steps in re.findall(pat, s, re.S):
        if anc and modul + "-" + anc not in ids:
            bad.add(anc)
        try:
            st = json.loads(steps)
        except Exception:
            continue
        tot = sum(x.get("min", 0) for x in st)
        if ty != "T" and abs(tot - int(mn)) > 3:
            note("MINUTEN", "Block %s min, Schritte summieren %s min (Anker %s)" % (mn, tot, anc or "-"))
        for x in st:
            if x.get("to") and modul + "-" + x["to"] not in ids:
                bad.add(x["to"])
    if bad:
        note("PLANANKER", "tot: " + ", ".join(sorted(bad)))
    for d, seg in re.findall(r'\("(2026-\d\d-\d\d)", \[(.*?)\], "', s, re.S):
        mins = [int(x) for x in re.findall(r'\("' + modul + r'",(\d+),', seg)]
        if not mins:
            continue
        kur = [int(x) for x in re.findall(r'\("' + modul + r'",(\d+),"V"', seg)]
        pflicht = sum(mins) - sum(kur)
        flag = "  <-- ueber 3 h" if pflicht > 180 else ""
        print("  %s  gesamt %3d  Kuer %3d  Pflicht %3d min (%.1f h)%s"
              % (d, sum(mins), sum(kur), pflicht, pflicht / 60, flag))


def main(argv):
    modul = None
    plan = "--plan" in argv
    rest = [a for a in argv if not a.startswith("--")]
    if rest:
        modul = rest[0]
    files = ([os.path.join(ROOT, "module", modul, modul + ".html")] if modul
             else sorted(glob.glob(os.path.join(ROOT, "module", "*", "*.html"))))
    for f in files:
        if not os.path.exists(f):
            print("nicht gefunden:", f)
            continue
        s = check_html(f)
        check_shell(s)
        check_dark(s)
    if plan and modul:
        check_plan(modul)
    print("\n%s  %d Befund(e)" % ("SAUBER" if not findings else "BEFUNDE", len(findings)))
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

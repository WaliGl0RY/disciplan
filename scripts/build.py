#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
build.py — baut alle Modul-HTMLs zu EINER Datei klausuren.html zusammen.

Aufruf:  python scripts/build.py
Ergebnis: klausuren-2026-09/klausuren.html

Jedes Modul behaelt sein eigenes CSS — es wird beim Bauen auf #m-<KUERZEL>
gescoped, damit sich die Regeln nicht gegenseitig ueberschreiben.
Neue Module fallen automatisch rein: einfach module/<K>/<K>.html anlegen.
"""
import os, re, json, datetime, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))   # Repo-Wurzel (scripts/ liegt eine Ebene tiefer)
OUT  = os.path.join(ROOT, "klausuren.html")

# ─────────────────────────── Kursdaten ───────────────────────────
# MODULES (Moduldaten), DAYS (Tagesplan) und TEXT (Titel, Strategietexte) liegen seit 28.09.2026 in
# klausuren_data.py im Repo-Wurzelordner (in diesem Repo: Demo-Daten fuer KAF, GAR, RAD).
sys.path.insert(0, ROOT)
from klausuren_data import MODULES, DAYS, TEXT, PLAN_START, PREP_END  # noqa: E402

# ─────────────────────── CSS-Scoping ───────────────────────
def scope_css(css, sel):
    """Praefixt jede Regel mit `sel`. Behandelt @media/@supports rekursiv,
       laesst @page/@keyframes/@font-face unangetastet."""
    out, i, n = [], 0, len(css)
    while i < n:
        # Leerraum — muss vor Kommentar/At-Rule weg, sonst wird "\n@media" nicht
        # als At-Rule erkannt und landet als "#sel @media{...}" im Output (ungueltig).
        if css[i].isspace():
            i += 1
            continue
        # Kommentar
        if css.startswith("/*", i):
            j = css.find("*/", i + 2)
            i = n if j < 0 else j + 2
            continue
        # At-Rule
        if css[i] == "@":
            j = i
            while j < n and css[j] not in "{;":
                j += 1
            head = css[i:j].strip()
            if j < n and css[j] == ";":
                out.append(head + ";")
                i = j + 1
                continue
            depth, k = 1, j + 1
            while k < n and depth:
                if css[k] == "{": depth += 1
                elif css[k] == "}": depth -= 1
                k += 1
            body = css[j + 1:k - 1]
            low = head.lower()
            if low.startswith("@media") and "prefers-color-scheme" in low and "dark" in low:
                # Die Moduldokumente bringen ihren Dunkelmodus als Media Query mit.
                # Hier gilt aber der Umschalter oben rechts, nicht die Systemeinstellung —
                # also wird der Block auf html[data-t=dark] umgeschrieben statt verschachtelt.
                out.append(scope_css(body, "html[data-t=dark] " + sel))
            elif low.startswith(("@media", "@supports", "@layer")):
                out.append(head + "{" + scope_css(body, sel) + "}")
            else:                       # @keyframes, @page, @font-face
                out.append(head + "{" + body + "}")
            i = k
            continue
        # normale Regel
        j = css.find("{", i)
        if j < 0:
            break
        depth, k = 1, j + 1
        while k < n and depth:
            if css[k] == "{": depth += 1
            elif css[k] == "}": depth -= 1
            k += 1
        sels = css[i:j].strip()
        body = css[j + 1:k - 1]
        if sels:
            parts = []
            for s in sels.split(","):
                s = s.strip()
                if not s:
                    continue
                if s in ("html", "body", ":root"):
                    parts.append(sel)
                elif s == "*":
                    parts.append(sel + ",%s *" % sel)
                elif s.startswith(("html ", "body ", "html>", "body>")):
                    parts.append(sel + " " + s.split(" ", 1)[-1].lstrip(">"))
                else:
                    parts.append(sel + " " + s)
            out.append(",".join(parts) + "{" + body + "}")
        i = k
    return "".join(out)

# ─────────────────────── Modul einlesen ───────────────────────
RE_STYLE  = re.compile(r"<style[^>]*>(.*?)</style>", re.S | re.I)
RE_SCRIPT = re.compile(r"<script[^>]*>(.*?)</script>", re.S | re.I)

def load(k):
    p = os.path.join(ROOT, "module", k, k + ".html")
    if not os.path.exists(p):
        return None
    h = open(p, encoding="utf-8").read()
    css = "\n".join(RE_STYLE.findall(h))
    js  = "\n".join(RE_SCRIPT.findall(h))
    body = RE_STYLE.sub("", h)
    body = RE_SCRIPT.sub("", body)
    # Kopf und Rumpf wegschneiden
    body = re.sub(r"(?is)^.*?<(?:!doctype|html|meta|title)[^>]*>", "", body)
    for tag in ("meta", "title"):
        body = re.sub(r"(?is)<%s[^>]*>.*?(</%s>)?" % (tag, tag), "", body, count=3)
    body = re.sub(r"(?is)</?(html|head|body)[^>]*>", "", body)
    # interne Verweise auf andere Module in Routen umbiegen
    body = re.sub(r'href="(?:\.\./)*module/([A-Z0-9]+)/\1\.html"', r'href="#\1"', body)
    # Links auf die Trainer-Apps zeigen im Modulordner relativ ("KAF-Trainer.html").
    # In der zusammengebauten Datei liegt die Wurzel eine Ebene hoeher.
    body = re.sub(r'href="([A-Z0-9]+)-Trainer\.html"',
                  r'href="module/\1/\1-Trainer.html"', body)
    # IDs und In-Page-Anker pro Modul namespacen — sonst kollidieren z.B.
    # id="orient" aus mehreren Modulen miteinander.
    pre = k + "-"
    ids = set(re.findall(r'\bid="([^"]+)"', body))
    body = re.sub(r'\bid="([^"]+)"', lambda m: 'id="%s%s"' % (pre, m.group(1)), body)
    def fixhref(m):
        t = m.group(1)
        return 'href="#%s%s"' % (pre, t) if t in ids else m.group(0)
    body = re.sub(r'href="#([^"]+)"', fixhref, body)
    # ID-Selektoren im Modul-CSS mitziehen, sonst greift z.B. #KAFTR ins Leere
    css = re.sub(r'#([A-Za-z_][\w-]*)',
                 lambda m: '#' + pre + m.group(1) if m.group(1) in ids else m.group(0), css)
    # JS: NICHT die Aufrufstellen textuell umschreiben — das trifft nur Literale und
    # bricht bei dynamischen IDs (getElementById(id) / `e${i}` / 'r'+i). Stattdessen
    # wird der Zugriff zur Laufzeit umgebogen: eine Modul-Helferfunktion praefixt jede
    # ID, egal wie sie zustande kommt.
    if js.strip():
        helper = "$g" + re.sub(r"\W", "", k)
        js = js.replace("document.getElementById(", helper + "(")
        js = ('function %s(i){i=String(i);'
              'return document.getElementById(i.indexOf("%s")===0?i:"%s"+i);}\n'
              % (helper, pre, pre)) + js
    return dict(css=scope_css(css, "#m-" + k), js=js, body=body.strip())

# ─────────────────────── Shell ───────────────────────
SHELL_CSS = r"""

/* ---- Der laufende Plan (Ansicht ab 28.08.) ---- */
.lauf{background:var(--card);border:1px solid var(--line);border-left:3px solid var(--acc);
 border-radius:10px;padding:16px 18px 18px;margin:0 0 20px}
.lauf .lh{display:flex;align-items:flex-start;gap:14px;margin-bottom:11px}
.lauf .lh h3{margin:0 0 2px;font:700 17px sans-serif;letter-spacing:-.01em}
.lauf .ls{font-size:12.5px;color:var(--mut)}
.lauf .sp{flex:1}
.lauf .lring{font:700 22px sans-serif;color:var(--acc);white-space:nowrap;line-height:1.15;text-align:right}
.lauf .lring small{display:block;font:500 11px sans-serif;color:var(--mut);letter-spacing:.03em}
.lprog{height:5px;background:var(--soft);border-radius:3px;overflow:hidden;margin-bottom:15px}
.lprog i{display:block;height:100%;background:var(--acc);border-radius:3px;transition:width .25s}
.lhd{font:600 10.5px/1 sans-serif;letter-spacing:.13em;text-transform:uppercase;color:var(--mut);
 margin:0 0 8px}
.ltoday{border:1px solid var(--line);border-radius:9px;padding:12px 13px;background:var(--soft);margin-bottom:16px}
.ltoday .th{display:flex;align-items:baseline;gap:9px;margin-bottom:9px}
.ltoday .th b{font:700 15px sans-serif}
.ltoday .th span{font-size:12px;color:var(--mut)}
.lt{display:flex;align-items:flex-start;gap:9px;padding:8px 0;border-top:1px solid var(--line);font-size:14px}
.lt:first-of-type{border-top:0}
.lt input{margin:4px 0 0;width:16px;height:16px;flex:0 0 auto;accent-color:var(--acc);cursor:pointer}
.lt .mk4{font:700 10.5px sans-serif;background:var(--card);border:1px solid var(--line);
 border-radius:4px;padding:2px 5px;flex:0 0 auto;margin-top:2px}
.lt .m4{font-size:11px;color:var(--mut);flex:0 0 auto;margin-top:3px}
.lt label{flex:1;cursor:pointer;line-height:1.5}
.lt .ltx{flex:1;cursor:pointer;line-height:1.45;min-width:0}
.lt .ltx b{font-weight:650}
.lt .ltx:hover b{text-decoration:underline;text-underline-offset:2px}
.lt .lsub{display:block;font-size:11.5px;color:var(--mut);margin-top:2px}
.lt .chev{flex:0 0 auto;border:0;background:none;color:var(--mut);cursor:pointer;font-size:15px;padding:0 2px}
.lt .chev:hover{color:var(--acc)}
#pov{position:fixed;inset:0;background:rgba(0,0,0,.45);display:none;z-index:120;overflow:auto;padding:5vh 14px 40px}
#pov.on{display:block}
#pbox{max-width:640px;margin:0 auto;background:var(--card);border:1px solid var(--line);
 border-radius:13px;overflow:hidden;box-shadow:0 18px 50px rgba(0,0,0,.3)}
.ph{padding:16px 20px 14px;border-bottom:1px solid var(--line);background:var(--soft)}
.ph .pmeta{display:flex;align-items:center;gap:8px;flex-wrap:wrap;margin-bottom:7px}
.ph h3{margin:0;font:700 19px sans-serif;letter-spacing:-.01em;line-height:1.28}
.ph .pcl{margin-left:auto;border:0;background:none;font-size:21px;color:var(--mut);cursor:pointer;line-height:1}
.pmk{font:700 10.5px sans-serif;background:var(--card);border:1px solid var(--line);border-radius:4px;padding:2px 6px}
.pty{font-size:11.5px;color:var(--mut)}
.pb{padding:6px 20px 18px}
.plab{font:600 10.5px/1 sans-serif;letter-spacing:.13em;text-transform:uppercase;color:var(--mut);margin:16px 0 9px}
.stp{display:flex;gap:11px;padding:11px 0;border-top:1px solid var(--line)}
.stp:first-of-type{border-top:0}
.stp input{margin:3px 0 0;width:17px;height:17px;flex:0 0 auto;accent-color:var(--acc);cursor:pointer}
.stp .sn{flex:0 0 auto;width:21px;height:21px;border-radius:50%;background:var(--soft);border:1px solid var(--line);
 font:700 11px/20px sans-serif;text-align:center;color:var(--mut)}
.stp.sdone .sn{background:var(--acc);border-color:var(--acc);color:#fff}
.stp .sc{flex:1;min-width:0}
.stp.sdone .st1{opacity:.45;text-decoration:line-through}
.st1{font:600 14.5px sans-serif;line-height:1.4}
.st2{font-size:12.5px;color:var(--mut);margin-top:3px;line-height:1.5}
.sgo{margin-top:7px;display:flex;gap:6px;flex-wrap:wrap;align-items:center}
.sgo button{font:600 12.5px sans-serif;border:1px solid var(--line);background:var(--card);color:var(--fg);
 border-radius:6px;padding:3px 10px;cursor:pointer}
.sgo button:hover{background:var(--acc);border-color:var(--acc);color:#fff}
.sgo .qlab{font-size:12px;color:var(--mut);margin-right:1px}
.sgo button.qb{padding:3px 8px;min-width:30px}
.pmk2{margin:8px 0 4px;padding:0;list-style:none}
.pmk2 li{position:relative;margin:7px 0;padding:9px 13px 9px 34px;font-size:13.6px;line-height:1.6;
 background:var(--soft);border:1px solid var(--line);border-left:3px solid var(--acc);
 border-radius:0 9px 9px 0;color:var(--fg)}
.pmk2 li:before{content:"\2691";position:absolute;left:12px;top:9px;color:var(--acc);font-size:13px}
.pprog{margin-top:14px;padding:9px 12px;border-radius:8px;background:var(--soft);border:1px solid var(--line);
 font-size:12.5px;color:var(--mut)}
.pprog b{color:var(--fg)}
.pprog.ok{background:#1b7a4b14;border-color:#1b7a4b66;color:#1b7a4b}
.pprog.ok b{color:#1b7a4b}
.ptxt{font-size:13.5px;line-height:1.62;color:var(--mut);margin-top:9px}
.ptxt b{color:var(--fg)}
.lt.done label{opacity:.4;text-decoration:line-through}
.lt.kur{opacity:.72}
.lt.kur .mk4{border-style:dashed}
.feier{display:flex;align-items:center;gap:8px;flex-wrap:wrap;margin:13px 0 4px;padding:8px 11px;
 border-radius:7px;background:var(--soft);border:1px dashed var(--line);font-size:12.5px;color:var(--mut)}
.feier b{color:var(--fg);font-weight:700}
.feier.ok{background:#1b7a4b14;border-color:#1b7a4b66;color:#1b7a4b}
.feier.ok b{color:#1b7a4b}
.lt .jp2{flex:0 0 auto;border:0;background:none;color:var(--acc);cursor:pointer;font-size:15px;padding:0 2px}
.lnx{display:flex;align-items:center;gap:10px;padding:8px 10px;border:1px solid var(--line);
 border-radius:7px;margin-bottom:6px;cursor:pointer;background:var(--card);font-size:13.5px}
.lnx:hover{border-color:var(--acc)}
.lnx.kl{border-left:3px solid #C8102E}
.lnx .d1{font:700 13px sans-serif;min-width:62px}
.lnx .c1{font-size:11.5px;color:var(--mut);min-width:74px}
.lnx .m1{display:flex;gap:4px;flex-wrap:wrap;flex:1}
.lnx .m1 span{font:600 10px sans-serif;background:var(--soft);border-radius:4px;padding:2px 5px}
.lnx .a1{color:var(--acc);font-size:14px}
.lnx .kb{font:700 9.5px sans-serif;background:#C8102E;color:#fff;border-radius:3px;padding:2px 5px;letter-spacing:.04em}
.lnx.gestern{opacity:.72;border-style:dashed}
.lmore{width:100%;margin-top:4px;padding:7px;border:1px dashed var(--line);border-radius:7px;
 background:none;color:var(--mut);font:600 12px sans-serif;cursor:pointer;font-family:inherit}
.lmore:hover{border-color:var(--acc);color:var(--acc)}
.lcal{margin:0 0 16px;border-radius:12px}
.lfil{display:flex;flex-wrap:wrap;gap:6px;margin:0 0 15px}
.lchip{display:inline-flex;align-items:center;gap:6px;padding:5px 11px;border:1px solid var(--line);
 border-radius:20px;background:var(--card);font:600 12.5px sans-serif;color:var(--fg);cursor:pointer;
 font-family:inherit}
.lchip:hover{border-color:var(--acc);color:var(--acc)}
.lchip.on{background:var(--acc);border-color:var(--acc);color:#fff}
.lchip i{font-style:normal;font-size:11px;opacity:.7}
.lchip.on i{opacity:.85}
.lchip.fertig{opacity:.45}
.kd{display:inline-block;width:9px;height:9px;border-radius:3px;margin-right:7px;flex:0 0 auto;vertical-align:baseline}
.mk{display:inline-block;padding:2px 10px;border-radius:999px;color:#fff;font-weight:700;letter-spacing:.02em}
.ldh{display:flex;align-items:baseline;gap:9px;margin:15px 0 4px;padding-top:11px;border-top:1px solid var(--line)}
.ldh:first-child{border-top:0;padding-top:0;margin-top:0}
.ldh b{font:700 13.5px sans-serif}
.ldh span{font-size:11.5px;color:var(--mut)}
.ldh .kl{font:700 9.5px sans-serif;background:#C8102E;color:#fff;border-radius:3px;padding:2px 5px;letter-spacing:.04em}
.ldh a{margin-left:auto;font-size:11.5px;color:var(--acc);text-decoration:none}
.lauf .fin{font-size:12.5px;color:var(--mut);margin-top:10px;line-height:1.6}
*{box-sizing:border-box}
:root{--bg:#f4f4f1;--fg:#1b1b19;--mut:#6d6d66;--line:#e3e3dc;--card:#fff;--acc:#C8102E;--soft:#efeee8}
html[data-t=dark]{--bg:#16161a;--fg:#e9e8e3;--mut:#9a9a92;--line:#2c2c33;--card:#1e1e24;--acc:#F0566A;--soft:#25252c}
html{scroll-behavior:smooth}
body{margin:0;background:var(--bg);color:var(--fg);
 font:15.5px/1.65 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif;
 transition:background .18s,color .18s}
#app{display:flex;align-items:flex-start;min-height:100vh}
#side{position:sticky;top:0;flex:0 0 218px;height:100vh;overflow-y:auto;
 padding:16px 11px 30px 16px;border-right:1px solid var(--line);background:var(--card)}
#side .brand{font:700 15px sans-serif;letter-spacing:-.01em;margin:2px 0 3px}
#side .bsub{font-size:11.5px;color:var(--mut);margin-bottom:13px}
#side h5{font:600 10px/1 sans-serif;letter-spacing:.14em;text-transform:uppercase;
 color:var(--mut);margin:17px 0 6px;opacity:.8}
.nl{display:flex;align-items:center;gap:7px;padding:6px 9px;margin:1px 0;border-radius:6px;
 font-size:13.3px;color:var(--fg);text-decoration:none;cursor:pointer;border:0;background:none;
 width:100%;text-align:left;font-family:inherit}
.nl:hover{background:var(--soft)}
.nl.on{background:var(--acc);color:#fff}
.nl .kk{font:700 11px sans-serif;min-width:34px}
.nl .dd{margin-left:auto;font-size:11px;opacity:.65}
.nl.dis{opacity:.4;cursor:default}
#side .tt{margin-top:20px;display:flex;gap:6px}
.mini{flex:1;padding:6px;border:1px solid var(--line);border-radius:6px;background:var(--card);
 color:var(--mut);cursor:pointer;font:600 11.5px sans-serif}
.mini:hover{border-color:var(--acc);color:var(--acc)}
#wrap{flex:1 1 auto;min-width:0}
.view{display:none}.view.on{display:block}
#hub{max-width:1120px;margin:0 auto;padding:26px 26px 80px}
.mv{padding:0}
.topbar{position:sticky;top:0;z-index:9;background:var(--card);border-bottom:1px solid var(--line);
 padding:9px 20px;display:flex;align-items:center;gap:12px;flex-wrap:wrap}
.topbar b{font-size:15px}
.topbar .cd2{font:600 12.5px sans-serif;color:var(--acc)}
.topbar .sp{flex:1}
h1{font-size:28px;margin:0 0 2px;letter-spacing:-.024em}
.sub{color:var(--mut);margin:0 0 6px;font-size:14.3px}
h2{font-size:20px;margin:28px 0 4px}
h3{font-size:16.5px;margin:20px 0 6px}
.fine{font-size:13px;color:var(--mut)}
a{color:var(--acc)}
code{background:var(--soft);padding:1.5px 5px;border-radius:4px;font:12.6px ui-monospace,Menlo,Consolas,monospace}
.cd{display:flex;gap:11px;flex-wrap:wrap;margin:14px 0 6px}
.cdb{background:var(--fg);color:var(--bg);border-radius:10px;padding:10px 15px;min-width:126px}
.cdb .n{font:700 24px sans-serif;line-height:1.1}
.cdb .l{font-size:11.5px;opacity:.72;margin-top:2px}
.cdb.warn{background:#C8102E;color:#fff}
.tabs{display:flex;gap:5px;margin:20px 0 0;border-bottom:2px solid var(--fg);flex-wrap:wrap}
.tab{padding:8px 15px;border-radius:8px 8px 0 0;border:0;font:600 14px sans-serif;
 cursor:pointer;color:var(--mut);background:none}
.tab:hover{background:var(--soft);color:var(--fg)}
.tab.on{background:var(--fg);color:var(--bg)}
/* .cdb und .tab.on sind im Hellen bewusst invertiert (dunkle Kachel auf hellem Grund).
   Im Dunkeln waere die Umkehrung ein greller weisser Block — dort stattdessen eine
   angehobene dunkle Flaeche, die dieselbe Rolle spielt, ohne zu blenden. */
html[data-t=dark] .cdb:not(.warn){background:#2b2b33;color:var(--fg)}
html[data-t=dark] .tabs{border-bottom-color:#3a3a44}
html[data-t=dark] .tab.on{background:#2b2b33;color:var(--fg)}
html[data-t=dark] .tab:hover{background:#23232a;color:var(--fg)}
.pane{display:none;padding-top:20px}.pane.on{display:block}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(320px,1fr));gap:13px}
.card{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:14px 17px 15px;
 display:flex;flex-direction:column;position:relative;overflow:hidden;transition:.14s}
.card:hover{transform:translateY(-1px);box-shadow:0 3px 12px rgba(0,0,0,.07)}
.card .bar{position:absolute;left:0;top:0;bottom:0;width:4px}
.card h3{margin:0;font-size:18.5px}
.card .mn{font-size:12.4px;color:var(--mut);margin:1px 0 8px}
.row{display:flex;align-items:center;gap:7px;flex-wrap:wrap;margin-bottom:8px}
.tg{font:600 11.2px sans-serif;padding:3px 9px;border-radius:20px;white-space:nowrap}
.tg.ok{background:#e7f3e1;color:#2c5220}.tg.todo{background:#fbe4e8;color:#9c0c24}
.tg.pf{background:#e6edf5;color:#2c5580}.tg.wp{background:var(--soft);color:var(--mut)}
.tg.v3{background:#C8102E;color:#fff}.tg.v2{background:#dde7f5;color:#2c4a75}
.dt{font:600 13.8px sans-serif}
.md{font-size:13.2px;color:var(--mut);margin:2px 0 10px;flex:1 1 auto}
.btn{display:inline-block;padding:6px 13px;border-radius:7px;font:600 13px sans-serif;
 text-decoration:none;border:1px solid var(--acc);color:var(--acc);background:none;cursor:pointer}
.btn.pri{background:var(--acc);color:#fff}
.btn:hover{opacity:.87}
.key{background:var(--card);border:1px solid var(--line);border-radius:9px;padding:11px 15px;margin:12px 0;font-size:14.3px}
.warn{background:#eef3fa;border:1px solid #c9d7ec;color:#243a5c;border-radius:9px;padding:11px 15px;margin:12px 0;font-size:14.3px}
.crit{background:#fdecef;border:1px solid #efbcc4;color:#5a1420;border-radius:9px;padding:12px 16px;margin:12px 0;font-size:14.6px}
table{border-collapse:collapse;width:100%;margin:12px 0;font-size:13.6px;background:var(--card);display:block;overflow-x:auto}
/* Im hellen Modus haben Modulinhalte helle Kartenflaechen und dunkle Schrift; die
   table-Regel darueber wuerde sie dunkel einfaerben -> unlesbar. Deshalb hier hell halten.
   Im Dunkelmodus bringen die Moduldokumente ihre eigenen Farben mit (auf html[data-t=dark]
   umgeschrieben), also darf diese Notbremse dort nicht greifen. */
html:not([data-t=dark]) [id^="m-"] table{background:#fff;color:#1b1b19}
html:not([data-t=dark]) [id^="m-"] th{background:#efeee8;color:#1b1b19}
html:not([data-t=dark]) [id^="m-"] td{background:#fff;color:#1b1b19}
html:not([data-t=dark]) [id^="m-"] code{color:#1b1b19}
th{background:var(--soft);text-align:left;padding:7px 10px;border:1px solid var(--line);font-size:12.6px;white-space:nowrap}
td{padding:7px 10px;border:1px solid var(--line);vertical-align:top}
/* ── Wochenkalender ── */
.cal{background:var(--card);border:1px solid var(--line);border-radius:16px;padding:16px 18px 18px;
 margin:16px 0 26px;box-shadow:0 1px 3px rgba(0,0,0,.04);overflow:hidden}
.calh{display:flex;align-items:center;gap:12px;margin-bottom:14px;flex-wrap:wrap}
.calh .kw{font:700 17px sans-serif;letter-spacing:-.01em}
.calh .rg{font-size:13px;color:var(--mut)}
.calh .sp{flex:1}
.nav{display:flex;gap:5px;align-items:center}
.nb{width:32px;height:32px;border-radius:9px;border:1px solid var(--line);background:var(--card);
 color:var(--fg);cursor:pointer;font:600 15px sans-serif;display:flex;align-items:center;
 justify-content:center;transition:.14s}
.nb:hover:not(:disabled){border-color:var(--acc);color:var(--acc);transform:translateY(-1px)}
.nb:disabled{opacity:.3;cursor:default}
.nb.tdy{width:auto;padding:0 13px;font-size:12.5px}
.wgrid{display:grid;grid-template-columns:repeat(7,minmax(0,1fr));gap:8px}
.wgrid.slideL{animation:sl .26s cubic-bezier(.22,.9,.3,1)}
.wgrid.slideR{animation:sr .26s cubic-bezier(.22,.9,.3,1)}
@keyframes sl{from{opacity:0;transform:translateX(26px)}to{opacity:1;transform:none}}
@keyframes sr{from{opacity:0;transform:translateX(-26px)}to{opacity:1;transform:none}}
.dc{border:1px solid var(--line);border-radius:12px;padding:8px 8px 9px;min-height:132px;min-width:0;
 display:flex;flex-direction:column;gap:5px;background:var(--bg);transition:.16s;position:relative;
 overflow:hidden}
.dc:hover{border-color:#c9c9be;transform:translateY(-2px);box-shadow:0 4px 14px rgba(0,0,0,.07)}
.dc.void{opacity:.32;background:none;border-style:dashed;min-height:132px}
.dc.past{opacity:.5}
.dc.today{border-color:var(--acc);border-width:2px;padding:7px 7px 8px;
 box-shadow:0 0 0 4px rgba(176,82,44,.11)}
.dc.klausur{background:linear-gradient(160deg,#fdecef,#f8d9df);border-color:#e89aa6}
html[data-t=dark] .crit{background:#2a1319;border-color:#5a1525;color:#f3d6db}
html[data-t=dark] .warn{background:#182230;border-color:#34476a;color:#c9dbf5}
html[data-t=dark] .dc.klausur{background:linear-gradient(160deg,#2a1219,#200e14);border-color:#5a1525}
.dc.deadline{background:linear-gradient(160deg,#eef3fa,#e2ebf7);border-color:#b9cbe6}
html[data-t=dark] .dc.deadline{background:linear-gradient(160deg,#182230,#141c28);border-color:#34476a}
.dch{display:flex;align-items:baseline;gap:6px;padding:1px 3px 5px;border-bottom:1px solid var(--line);margin-bottom:2px}
.dch .wd{font:700 10.5px sans-serif;letter-spacing:.09em;text-transform:uppercase;color:var(--mut)}
.dch .dn{font:700 17px sans-serif;line-height:1;letter-spacing:-.02em}
.dch .mo{font-size:10.5px;color:var(--mut)}
.dch .dot{margin-left:auto;width:7px;height:7px;border-radius:50%;background:var(--line)}
.dch .dot.part{background:linear-gradient(90deg,var(--acc) 50%,var(--line) 50%)}
.dch .dot.full{background:#2E9E5B}
.tk{display:flex;gap:5px;align-items:flex-start;padding:4px 5px;border-radius:7px;min-width:0;
 background:var(--card);border:1px solid var(--line);cursor:pointer;transition:.13s}
.tk code{font-size:10px;padding:0 3px;word-break:break-all}
.tk:hover{border-color:var(--acc)}
.tk input{margin:1px 0 0;width:13px;height:13px;accent-color:var(--acc);flex:0 0 auto;cursor:pointer}
.tk .mk2{font:700 9.5px sans-serif;padding:1px 5px;border-radius:20px;background:var(--soft);
 color:var(--mut);flex:0 0 auto;letter-spacing:.03em}
.tk .tx{font-size:11.4px;line-height:1.34;flex:1;min-width:0;
 display:-webkit-box;-webkit-line-clamp:4;-webkit-box-orient:vertical;overflow:hidden}
.tk.done{opacity:.4}.tk.done .tx{text-decoration:line-through}
.jp{flex:0 0 auto;border:0;background:none;color:var(--mut);cursor:pointer;padding:0 1px;
 font:600 13px sans-serif;line-height:1;border-radius:5px;align-self:center;opacity:.55;transition:.13s}
.jp:hover{color:var(--acc);opacity:1;transform:translateX(1px)}
.obj .jp{font-size:15px;margin-top:1px}
.tk .tx b{font-weight:700}
.badge{position:absolute;top:0;right:0;font:700 8.5px sans-serif;letter-spacing:.07em;
 text-transform:uppercase;padding:2px 7px 3px;border-radius:0 11px 0 10px;color:#fff;z-index:2}
.badge.k{background:#C8102E}.badge.d{background:#5b7fb5}
/* einklappbare Tagesliste */
.tglr{display:flex;align-items:center;gap:9px;margin:26px 0 0;cursor:pointer;
 background:none;border:0;color:var(--fg);font:inherit;padding:0}
.tglr h3{margin:0}
.tglr .ar{width:26px;height:26px;border-radius:8px;border:1px solid var(--line);
 display:flex;align-items:center;justify-content:center;font-size:12px;transition:.18s;color:var(--mut)}
.tglr:hover .ar{border-color:var(--acc);color:var(--acc)}
.tglr.open .ar{transform:rotate(90deg)}
.tglr .hint{font-size:12.5px;color:var(--mut)}
#dayswrap{display:none;animation:fadeIn .22s ease}
#arcwrap{display:none;animation:fadeIn .22s ease;margin-top:12px}
#arcwrap.open{display:block}
.expo{border-top:1px solid var(--line);margin-top:18px;padding-top:14px}
.expo .exph{font-size:12.8px;color:var(--mut);margin:0 0 10px;max-width:70ch}
.expo .exbtns{display:flex;gap:8px;align-items:center;flex-wrap:wrap;margin-bottom:9px}
.expo .hint{font-size:12px;color:var(--mut)}
#expout{display:none;width:100%;min-height:230px;padding:11px 13px;border:1px solid var(--line);
 border-radius:9px;background:var(--soft);color:var(--fg);resize:vertical;
 font:12.4px/1.55 ui-monospace,SFMono-Regular,Menlo,monospace}
#expout.on{display:block}
#dayswrap.open{display:block}
@keyframes fadeIn{from{opacity:0;transform:translateY(-4px)}to{opacity:1;transform:none}}
.calf{display:flex;gap:14px;align-items:center;margin-top:13px;flex-wrap:wrap;font-size:12px;color:var(--mut)}
.lg{display:flex;align-items:center;gap:5px}
.lg i{width:11px;height:11px;border-radius:3px;display:inline-block}
@media(max-width:900px){.wgrid{grid-template-columns:repeat(7,minmax(122px,1fr));
 overflow-x:auto;padding-bottom:6px}}

/* Tageskarte kompakt */
.dc{cursor:pointer}
.dsum{display:flex;align-items:baseline;gap:6px;margin:2px 0 4px;flex-wrap:wrap}
.dsum .cnt{font:700 15px sans-serif}
.dsum .mins{font-size:11px;color:var(--mut)}
.mods{display:flex;flex-wrap:wrap;gap:3px;margin-top:2px}
.mods span{font:700 9.5px sans-serif;padding:2px 6px;border-radius:20px;background:var(--soft);color:var(--mut)}
.mods span.on{background:var(--acc);color:#fff}
.dbar{height:4px;background:var(--soft);border-radius:3px;overflow:hidden;margin-top:auto}
.dbar i{display:block;height:100%;background:#2E9E5B;width:0;transition:.3s}
.more{font-size:10.5px;color:var(--mut);margin-top:3px;text-align:center;opacity:.75}
/* Modal */
#dov{position:fixed;inset:0;background:rgba(0,0,0,.45);display:none;z-index:120;
 overflow-y:auto;padding:5vh 16px 40px}
#dov.on{display:block}
#dbox{max-width:720px;margin:0 auto;background:var(--card);border-radius:14px;overflow:hidden;
 box-shadow:0 20px 60px rgba(0,0,0,.32);animation:dpop .2s cubic-bezier(.22,.9,.3,1)}
@keyframes dpop{from{opacity:0;transform:translateY(14px) scale(.98)}to{opacity:1;transform:none}}
#dhead{padding:16px 22px 14px;border-bottom:1px solid var(--line);position:sticky;top:0;background:var(--card);z-index:2}
#dhead .r1{display:flex;align-items:baseline;gap:11px;flex-wrap:wrap}
#dhead h3{margin:0;font-size:21px;letter-spacing:-.015em}
#dhead .wd2{font-size:13.5px;color:var(--mut)}
#dhead .bud{margin-left:auto;font:600 13px sans-serif;color:var(--acc)}
#dhead .x{background:none;border:0;font-size:22px;line-height:1;color:var(--mut);cursor:pointer;padding:0 4px}
#dhead .x:hover{color:var(--acc)}
#dhead .pr{height:5px;background:var(--soft);border-radius:3px;overflow:hidden;margin-top:10px}
#dhead .pr i{display:block;height:100%;background:#2E9E5B;width:0;transition:.3s}
#dbody{padding:8px 22px 20px}
.tsk{display:flex;gap:11px;align-items:flex-start;padding:11px 0;border-bottom:1px solid var(--line)}
.tsk:last-child{border:0}
.tsk input{margin-top:3px;width:18px;height:18px;accent-color:var(--acc);flex:0 0 auto;cursor:pointer}
.tsk .meta{flex:0 0 auto;display:flex;flex-direction:column;gap:3px;align-items:flex-start;min-width:78px}
.tsk .mk3{font:700 10px sans-serif;padding:2px 7px;border-radius:20px;background:var(--soft);color:var(--mut)}
.tsk .ty{font:700 9.5px sans-serif;padding:2px 6px;border-radius:4px;letter-spacing:.04em}
.ty.L{background:#e6edf5;color:#2c5580}.ty.U{background:#eef4ea;color:#2E9E5B}
.ty.D{background:#fbe4e8;color:#9c0c24}.ty.T{background:#fbe4e8;color:#9c0c24}
.ty.W{background:#f0efe9;color:#6d6d66}.ty.O{background:#e8eef8;color:#2c4a75}
.tsk .mn2{font:600 10.5px ui-monospace,monospace;color:var(--mut)}
.tsk .tt{flex:1;font-size:14.4px;line-height:1.55}
.tsk.done .tt{opacity:.42;text-decoration:line-through}
.tsk .go{flex:0 0 auto;border:0;background:none;color:var(--mut);cursor:pointer;font-size:16px;
 opacity:.5;align-self:center;padding:0 2px}
.tsk .go:hover{color:var(--acc);opacity:1}
.dlg{display:flex;gap:12px;flex-wrap:wrap;font-size:11.5px;color:var(--mut);
 padding:11px 0 0;margin-top:6px;border-top:1px solid var(--line)}

/* Tagesplan */
.wk{margin:22px 0 6px;font:700 12px sans-serif;letter-spacing:.1em;text-transform:uppercase;color:var(--mut)}
.day{display:flex;gap:12px;background:var(--card);border:1px solid var(--line);border-radius:10px;
 padding:10px 14px;margin:6px 0;align-items:flex-start}
.day.today{border-color:var(--acc);border-width:2px;box-shadow:0 0 0 3px rgba(176,82,44,.1)}
.day.past{opacity:.42}
.day.klausur{background:#fdecef;border-color:#efbcc4}
html[data-t=dark] .day.klausur{background:#2a1319;border-color:#5a1525}
.day.deadline{background:#eef3fa;border-color:#c9d7ec}
html[data-t=dark] .day.deadline{background:#182230;border-color:#34476a}
.day.puffer{opacity:.72}
.day .dt2{flex:0 0 92px}
.day .dnum{font:700 15px sans-serif;line-height:1.15}
.day .dwd{font-size:11.4px;color:var(--mut)}
.day .obs{flex:1;min-width:0}
.obj{display:flex;gap:9px;align-items:flex-start;padding:3px 0}
.obj input{margin-top:3px;width:16px;height:16px;accent-color:var(--acc);flex:0 0 auto;cursor:pointer}
.obj .mk{font:700 10.5px sans-serif;padding:2px 7px;border-radius:20px;background:var(--soft);
 color:var(--mut);flex:0 0 auto;margin-top:1px;min-width:40px;text-align:center}
.obj label{font-size:14px;cursor:pointer;flex:1}
.obj.done label{opacity:.42;text-decoration:line-through}
.prog{height:6px;background:var(--soft);border-radius:4px;overflow:hidden;margin:10px 0 4px}
.prog i{display:block;height:100%;background:var(--acc);width:0;transition:.3s}
/* Suche */
#ov{position:fixed;inset:0;background:rgba(0,0,0,.4);display:none;z-index:99;padding-top:9vh}
#ov.on{display:block}
#sbox{max-width:620px;margin:0 auto;background:var(--card);border-radius:12px;overflow:hidden;
 box-shadow:0 18px 50px rgba(0,0,0,.3)}
#sin{width:100%;border:0;padding:15px 18px;font:16px inherit;background:var(--card);color:var(--fg);outline:none;
 border-bottom:1px solid var(--line)}
#sres{max-height:56vh;overflow-y:auto}
.sr{padding:9px 18px;cursor:pointer;border-bottom:1px solid var(--line);font-size:13.8px}
.sr:hover,.sr.sel{background:var(--soft)}
.sr b{color:var(--acc)}
.sr .sk{font:700 10.5px sans-serif;padding:2px 7px;border-radius:20px;background:var(--soft);margin-right:7px}
mark{background:#d6e4ff;color:inherit;padding:0 1px}
html[data-t=dark] mark{background:#2a3f6a;color:#fff}
@media(max-width:820px){#side{position:fixed;left:-230px;z-index:50;transition:.2s}
 #side.open{left:0}#hub{padding:18px 14px 70px}.grid{grid-template-columns:1fr}}
"""

def build():
    mods, missing = {}, []
    for m in MODULES:
        r = load(m["k"])
        if r: mods[m["k"]] = r
        else: missing.append(m["k"])

    css = SHELL_CSS + "\n" + "\n".join(v["css"] for v in mods.values())
    panes = "".join(
        '<div class="view mv" id="v-%s"><div id="m-%s">%s</div></div>' % (k, k, v["body"])
        for k, v in mods.items())
    js_mod = "\n".join("/* ==== %s ==== */\n%s" % (k, v["js"]) for k, v in mods.items())

    data = json.dumps(dict(
        start=PLAN_START, prepEnd=PREP_END,
        mods=[dict(m, has=(m["k"] in mods)) for m in MODULES],
        days=[dict(d=d, o=[dict(m=x[0], min=x[1], ty=x[2], x=x[3], to=(x[4] if len(x) > 4 else None),
                               st=(x[5] if len(x) > 5 else None),
                               mk=(x[6] if len(x) > 6 else None)) for x in o], t=t) for d, o, t in DAYS],
    ), ensure_ascii=False)

    # Kampagnen- und Strategietexte kommen aus klausuren_data.TEXT (privat)
    tpl = TPL
    for key, val in TEXT.items():
        tpl = tpl.replace("<!--TXT:%s-->" % key, val)
    html = tpl.replace("/*CSS*/", css) \
              .replace("<!--PANES-->", panes) \
              .replace("/*DATA*/", data) \
              .replace("/*MODJS*/", js_mod) \
              .replace("/*BUILT*/", datetime.datetime.now().strftime("%d.%m.%Y %H:%M"))
    open(OUT, "w", encoding="utf-8").write(html)
    kb = os.path.getsize(OUT) // 1024
    print("OK  ->", OUT, "(%d KB)" % kb)
    print("    Module drin :", ", ".join(mods))
    if missing:
        print("    Noch ohne HTML:", ", ".join(missing))

TPL = r"""<!doctype html><html lang="de" data-t="light"><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title><!--TXT:title--></title>
<style>/*CSS*/</style>
<div id="app">
<aside id="side">
  <div class="brand"><!--TXT:brand--></div>
  <div class="bsub"><!--TXT:bsub--></div>
  <button class="nl" data-go="hub"><span class="kk">&#9632;</span>Übersicht</button>
  <h5>Module</h5>
  <div id="navmod"></div>
  <h5>Trainer</h5>
  <div id="navtr"></div>
  <h5>Werkzeuge</h5>
  <button class="nl" data-go="hub" data-tab="plan"><span class="kk">&#9634;</span>Tagesplan</button>
  <button class="nl" id="osearch"><span class="kk">&#9906;</span>Suche <span class="dd">Ctrl K</span></button>
  <div class="tt">
    <button class="mini" id="theme">Dark</button>
    <button class="mini" onclick="window.print()">Drucken</button>
  </div>
  <div class="bsub" style="margin-top:14px">gebaut /*BUILT*/</div>
</aside>

<div id="wrap">
<div class="view on" id="v-hub"><div id="hub">
  <h1><!--TXT:h1--></h1>
  <p class="sub"><!--TXT:hubsub--> &middot; <span id="today"></span></p>
  <div class="cd" id="cd"></div>
  <div class="tabs">
    <button class="tab on" data-p="mod">Module</button>
    <button class="tab" data-p="plan">Tagesplan</button>
    <button class="tab" data-p="tl">Zeitachse</button>
    <button class="tab" data-p="reg">Strategie</button>
  </div>
  <div class="pane on" id="p-mod"><div class="grid" id="grid"></div></div>
  <div class="pane" id="p-plan">
    <!--TXT:crit-->
    <!--TXT:planintro-->
    <div class="lauf" id="laufbox">
      <div class="lh"><div><h3>Der laufende Plan</h3><div class="ls" id="laufs"></div></div>
        <div class="sp"></div><div class="lring" id="laufring"></div></div>
      <div class="lprog"><i id="laufbar"></i></div>
      <div class="cal lcal">
        <div class="calh">
          <div><div class="kw" id="lkwlab"></div><div class="rg" id="lkwrg"></div></div>
          <div class="sp"></div>
          <div class="nav">
            <button class="nb" id="lwprev" title="Woche zurück">&#8249;</button>
            <button class="nb tdy" id="lwtoday">Heute</button>
            <button class="nb" id="lwnext" title="Woche vor">&#8250;</button>
          </div>
        </div>
        <div class="wgrid" id="lwgrid"></div>
        <div class="calf">
          <span class="lg"><i style="background:#e89aa6"></i>Klausur</span>
          <span class="lg"><i style="background:var(--acc)"></i>heute</span>
          <span class="lg"><i style="background:#2E9E5B;border-radius:50%"></i>Tag komplett</span>
          <span class="sp"></span><span id="lwsum"></span>
        </div>
      </div>
      <div class="lhd">Was möchtest du sehen?</div>
      <div class="lfil" id="lauffil"></div>
      <div class="lhd" id="laufheuteh">Heute im Detail</div>
      <div id="laufheute"></div>
      <div class="fin">Alles vor dem 28.08. steht unten im vollständigen Kalender &mdash; als Archiv, nicht als offene Rechnung.</div>
    </div>
    <button class="tglr" id="tgla"><span class="ar">&#9656;</span>
      <h3>Der alte Plan bis 27.08. &mdash; zum Abhaken</h3>
      <span class="hint" id="tglah"></span></button>
    <div id="arcwrap"><div class="lauf" id="arcbox">
      <div class="lh"><div><h3>Was vor dem Neuschnitt lief</h3><div class="ls" id="arcs"></div></div>
        <div class="sp"></div><div class="lring" id="arcring"></div></div>
      <div class="lprog"><i id="arcbar"></i></div>
      <div class="cal lcal">
        <div class="calh">
          <div><div class="kw" id="akwlab"></div><div class="rg" id="akwrg"></div></div>
          <div class="sp"></div>
          <div class="nav">
            <button class="nb" id="awprev" title="Woche zurück">&#8249;</button>
            <button class="nb tdy" id="awlast">Letzte Woche</button>
            <button class="nb" id="awnext" title="Woche vor">&#8250;</button>
          </div>
        </div>
        <div class="wgrid" id="awgrid"></div>
        <div class="calf">
          <span class="lg"><i style="background:#e89aa6"></i>Klausur</span>
          <span class="lg"><i style="background:#2E9E5B;border-radius:50%"></i>Tag komplett</span>
          <span class="sp"></span><span id="awsum"></span>
        </div>
      </div>
      <div class="lhd">Was möchtest du sehen?</div>
      <div class="lfil" id="arcfil"></div>
      <div class="lhd" id="archeuteh">Tag im Detail</div>
      <div id="archeute"></div>
      <div class="expo">
        <div class="lhd" style="margin-top:0">Stand weitergeben</div>
        <p class="exph">Erzeugt eine kurze Textfassung deines Stands &mdash; Archiv und laufender
        Plan, je Modul erledigt/offen. Kopieren und mir in den Chat kleben; dann plane ich mit
        Zahlen statt mit Vermutungen.</p>
        <div class="exbtns"><button class="nb" id="expbtn">Stand erzeugen</button>
          <button class="nb" id="expcopy">In die Zwischenablage</button>
          <span class="hint" id="expmsg"></span></div>
        <textarea id="expout" readonly spellcheck="false" placeholder="&hellip;"></textarea>
      </div>
      <div class="fin">Häkchen hier ändern nichts am laufenden Plan &mdash; sie sind nur die
      Bestandsaufnahme dessen, was vorher schon lief.</div>
    </div></div>
    <div class="lhd">Vollständiger Kalender &middot; Archiv</div>
    <div class="cal">
      <div class="calh">
        <div><div class="kw" id="kwlab"></div><div class="rg" id="kwrg"></div></div>
        <div class="sp"></div>
        <div class="nav">
          <button class="nb" id="wprev" title="Woche zurück">&#8249;</button>
          <button class="nb tdy" id="wtoday">Heute</button>
          <button class="nb" id="wnext" title="Woche vor">&#8250;</button>
        </div>
      </div>
      <div class="wgrid" id="wgrid"></div>
      <div class="calf">
        <span class="lg"><i style="background:#e89aa6"></i>Klausur</span>
        <span class="lg"><i style="background:#b9cbe6"></i>Deadline</span>
        <span class="lg"><i style="background:var(--acc)"></i>heute</span>
        <span class="lg"><i style="background:#2E9E5B;border-radius:50%"></i>Tag komplett</span>
        <span class="sp"></span>
        <span id="wsum"></span>
      </div>
    </div>
    <div class="prog"><i id="pall"></i></div>
    <div class="fine" id="pinfo"></div>
    <button class="tglr" id="tglr"><span class="ar">&#9656;</span>
      <h3>Alle Tage als Liste</h3><span class="hint" id="tglrh"></span></button>
    <div id="dayswrap"><div id="days"></div></div>
  </div>
  <div class="pane" id="p-tl"><div id="tlbox"></div></div>
  <div class="pane" id="p-reg">
    <!--TXT:strategie-->
  </div>
</div></div>
<!--PANES-->
</div></div>

<div id="dov"><div id="dbox">
  <div id="dhead">
    <div class="r1"><h3 id="dtitle"></h3><span class="wd2" id="dwd"></span>
      <span class="bud" id="dbud"></span>
      <button class="x" onclick="dClose()">&times;</button></div>
    <div class="pr"><i id="dpr"></i></div>
  </div>
  <div id="dbody"></div>
</div></div>

<div id="pov"><div id="pbox"></div></div>

<div id="ov"><div id="sbox">
  <input id="sin" placeholder="Suchen in allen Modulen …" autocomplete="off">
  <div id="sres"></div>
</div></div>

<script>
const D=/*DATA*/;
const T=new Date();T.setHours(0,0,0,0);
const dt=s=>new Date(s+"T00:00:00");
const dd=s=>Math.round((dt(s)-T)/864e5);
const WD=["So","Mo","Di","Mi","Do","Fr","Sa"];
const fm=s=>{const d=dt(s);return WD[d.getDay()]+" "+String(d.getDate()).padStart(2,"0")+"."+String(d.getMonth()+1).padStart(2,"0")+"."};
let ST={};try{ST=JSON.parse(localStorage.getItem("kl2609")||"{}")}catch(e){}
const save=()=>{try{localStorage.setItem("kl2609",JSON.stringify(ST))}catch(e){}};
/* Einmalige Bereinigung: der Plan ab 29.08.2026 (Tagindex 25) wurde am 29.08. neu
   geschnitten. Haken haengen an Tag- und Positionsindex, alte Haken ab dort zeigen
   also auf voellig andere Ziele. Tage 0-24 bleiben unangetastet. */
/* 18.09.2026: der Leseblock am 18.09. (Tagindex 44) wurde aus einem Block
   herausgeloest, dadurch verschieben sich dort alle Positionen ab 1 um eins.
   Nur dieser eine Tag wird zurueckgesetzt, alles andere bleibt. Schritt-Haken
   dieses Tages ebenso. */
try{if(localStorage.getItem("kl-recut2209")!=="1"){
  for(const k of Object.keys(ST)){const d=parseInt(k.split("_")[0],10);if(d>=47)delete ST[k];}
  ST["47_0"]=ST["47_1"]=ST["48_0"]=ST["48_1"]=true;save();
  try{const raw=JSON.parse(localStorage.getItem("kl-step")||"{}");for(const k of Object.keys(raw)){if(parseInt(k.split("_")[0],10)>=47)delete raw[k];}localStorage.setItem("kl-step",JSON.stringify(raw));}catch(e2){}
  localStorage.setItem("kl-recut2209","1");
}}catch(e){}
try{if(localStorage.getItem("kl-split1809")!=="1"){
  for(const k of Object.keys(ST)){if(parseInt(k.split("_")[0],10)===44)delete ST[k];}
  save();
  /* Schritt-Haken desselben Tages direkt im Speicher, SP gibt es hier noch nicht */
  try{const raw=JSON.parse(localStorage.getItem("kl-step")||"{}");
      for(const k of Object.keys(raw)){if(parseInt(k.split("_")[0],10)===44)delete raw[k];}
      localStorage.setItem("kl-step",JSON.stringify(raw));}catch(e2){}
  localStorage.setItem("kl-split1809","1");
}}catch(e){}
try{if(localStorage.getItem("kl-recut2")!=="2026-08-30"){
  for(const k of Object.keys(ST)){const d=parseInt(k.split("_")[0],10);if(d>=29)delete ST[k];}
  save();localStorage.setItem("kl-recut2","2026-08-30");
}}catch(e){}
try{if(localStorage.getItem("kl-recut")!=="2026-08-29b"){
  for(const k of Object.keys(ST)){const d=parseInt(k.split("_")[0],10);if(d>=24)delete ST[k];}
  save();localStorage.setItem("kl-recut","2026-08-29b");
}}catch(e){}

/* ---------- Navigation ---------- */
function go(k,tab){
 const t=document.getElementById("v-"+k);
 // Unbekannter Hash = In-Page-Anker eines Moduls. Nicht routen, Browser scrollen lassen.
 if(!t&&k!=="hub")return;
 document.querySelectorAll(".view").forEach(v=>v.classList.remove("on"));
 (t||document.getElementById("v-hub")).classList.add("on");
 document.querySelectorAll("#side .nl").forEach(n=>n.classList.toggle("on",n.dataset.go===k&&!n.dataset.tab));
 if(tab)swtab(tab);
 location.hash=k==="hub"?"":k;
 window.scrollTo(0,0);
 document.getElementById("side").classList.remove("open");
}
function swtab(p){
 document.querySelectorAll(".tab").forEach(x=>x.classList.toggle("on",x.dataset.p===p));
 document.querySelectorAll(".pane").forEach(x=>x.classList.toggle("on",x.id==="p-"+p));
}
document.querySelectorAll(".tab").forEach(t=>t.onclick=()=>swtab(t.dataset.p));

/* Modulfarbe (klausuren_data.MODULES[..]['col']); ohne Angabe die Akzentfarbe */
const mcol=k=>(D.mods.find(x=>x.k===k)||{}).col||'var(--acc)';
/* ---------- Sidebar ---------- */
document.getElementById("navmod").innerHTML=D.mods.map(m=>{
 const n=dd(m.d);
 return `<button class="nl${m.has?"":" dis"}" ${m.has?`data-go="${m.k}"`:""}>
  <span class="kk"><i class="kd" style="background:${m.col||'var(--acc)'}"></i>${m.k}</span>${m.has?"":"<span style='font-size:11.5px'>kein Dok</span>"}
  <span class="dd">${n<0?"&#10003;":n+"T"}</span></button>`}).join("");
document.querySelectorAll("#side .nl[data-go]").forEach(b=>b.onclick=()=>go(b.dataset.go,b.dataset.tab));
/* Die Trainer sind eigene Apps und oeffnen in einem neuen Tab. */
document.getElementById("navtr").innerHTML=D.mods.filter(m=>m.trainer).map(m=>
 `<a class="nl" href="${m.trainer.file}" target="_blank" title="${m.trainer.was}">
  <span class="kk"><i class="kd" style="background:${m.col||'var(--acc)'}"></i>${m.k}</span>Trainer<span class="dd">&#8599;</span></a>`).join("");

/* ---------- Countdown ---------- */
function kpi(){
 const nx=D.mods.filter(m=>dd(m.d)>=0).sort((a,b)=>dd(a.d)-dd(b.d));
 const p=[];
 if(nx.length)p.push(`<div class="cdb${dd(nx[0].d)<7?" warn":""}"><div class="n">${dd(nx[0].d)}</div><div class="l">Tage bis ${nx[0].k}</div></div>`);
 p.push(`<div class="cdb"><div class="n">${Math.max(0,dd(D.prepEnd))}</div><div class="l">Tage Vorbereitung übrig</div></div>`);
 const w=D.days.map((d,i)=>({...d,i})).filter(d=>d.d>=D.start);
 const done=w.reduce((a,d)=>a+d.o.filter((_,j)=>ST[d.i+"_"+j]).length,0);
 const tot=w.reduce((a,d)=>a+d.o.length,0);
 p.push(`<div class="cdb"><div class="n">${done}/${tot}</div><div class="l">Ziele ab 28.08.</div></div>`);
 p.push(`<div class="cdb"><div class="n">${D.mods.filter(m=>m.has).length}/${D.mods.length}</div><div class="l">Module dokumentiert</div></div>`);
 document.getElementById("cd").innerHTML=p.join("");
 document.getElementById("today").textContent="Heute: "+fm(iso(T));
}
kpi();

/* ---------- Modulkarten ---------- */
document.getElementById("grid").innerHTML=D.mods.map(m=>{
 const n=dd(m.d),col=n<0?"#c9c9be":n<7?"#C8102E":n<21?"#5b7fb5":"#2E9E5B";
 const vt=m.v===3?'<span class="tg v3">3. Versuch</span>':m.v===2?'<span class="tg v2">2. Versuch</span>':'';
 return `<div class="card"><div class="bar" style="background:${m.col||col}"></div>
  <h3><span class="mk" style="background:${m.col||'var(--acc)'}">${m.k}</span></h3><div class="mn">${m.name} &middot; ${m.prof}</div>
  <div class="row"><span class="dt">${fm(m.d)} ${m.t}</span>
   <span class="fine">${n<0?"vorbei":n===0?"HEUTE":"noch "+n+" Tage"}</span></div>
  <div class="row"><span class="tg ${m.typ==="PF"?"pf":"wp"}">${m.typ==="PF"?"Pflicht":"Wahlpflicht"}</span>
   ${vt}<span class="tg ${m.has?"ok":"todo"}">${m.has?"dokumentiert":"offen"}</span></div>
  ${m.mode?`<div class="row"><span class="fine"><b>${m.mode}</b></span></div>`:""}
  <div class="md">${m.desc}</div>
  <div><button class="btn ${m.has?"pri":""}" ${m.has?`onclick="go('${m.k}')"`:"disabled"}${m.col&&m.has?` style="background:${m.col};border-color:${m.col}"`:""}>
   ${m.has?"Lerndokument öffnen":"noch kein Dokument"}</button>${m.trainer?
   `<a class="btn" href="${m.trainer.file}" target="_blank" style="margin-left:7px${m.col?`;border-color:${m.col};color:${m.col}`:""}"
      title="${m.trainer.was}">Trainer &#8599;</a>`:""}</div></div>`}).join("");

/* ---------- Tagesplan ---------- */
function days(){
 let out="",lastW=null;
 D.days.forEach((d,i)=>{
  const dte=dt(d.d),n=dd(d.d);
  const wk=new Date(dte);wk.setDate(wk.getDate()-((wk.getDay()+6)%7));
  const wkey=iso(wk);
  if(wkey!==lastW){lastW=wkey;
   const we=new Date(wk);we.setDate(we.getDate()+6);
   out+=`<div class="wk">${fm(wkey)} &ndash; ${fm(iso(we))}</div>`}
  const cls=[d.t,n<0?"past":"",n===0?"today":""].filter(Boolean).join(" ");
  out+=`<div class="day ${cls}"><div class="dt2">
    <div class="dnum">${String(dte.getDate()).padStart(2,"0")}.${String(dte.getMonth()+1).padStart(2,"0")}.</div>
    <div class="dwd">${WD[dte.getDay()]}${n===0?" &middot; heute":""}</div></div><div class="obs">`;
  d.o.forEach((o,j)=>{const id=i+"_"+j,c=!!ST[id];
   const jb=o.to?`<button class="jp" title="Zum Lernstoff: ${o.m}" onclick="jump('${o.m}','${o.m}-${o.to}')">&#8599;</button>`:"";
   out+=`<div class="obj${c?" done":""}"><input type="checkbox" id="k${id}" ${c?"checked":""} onchange="tog('${id}')">
     <span class="mk">${o.m}</span><span class="ty ${o.ty}">${o.ty}</span>
     <label for="k${id}">${o.x} <span style="color:var(--mut);font-size:12px">· ${o.min} Min</span></label>${jb}</div>`});
  out+="</div></div>"});
 document.getElementById("days").innerHTML=out;
 const done=D.days.reduce((a,d,i)=>a+d.o.filter((_,j)=>ST[i+"_"+j]).length,0);
 const tot=D.days.reduce((a,d)=>a+d.o.length,0);
 document.getElementById("pall").style.width=(done/tot*100)+"%";
 document.getElementById("pinfo").textContent=done+" von "+tot+" Zielen erledigt";
}
function tog(id){ST[id]=!ST[id];save();days();cal();lauf();arc();kpi()}

/* Tagesliste ein-/ausklappen (Standard: zu) */
(function(){
 const b=document.getElementById("tglr"),w=document.getElementById("dayswrap"),h=document.getElementById("tglrh");
 let open=false;try{open=localStorage.getItem("kl-list")==="1"}catch(e){}
 const set=()=>{w.classList.toggle("open",open);b.classList.toggle("open",open);
  h.textContent=open?"zuklappen":"alle "+D.days.length+" Tage aufklappen";
  try{localStorage.setItem("kl-list",open?"1":"0")}catch(e){}};
 b.onclick=()=>{open=!open;set()};set();
})();

/* ---------- Wochenkalender ---------- */
const MO=["Jan","Feb","Mär","Apr","Mai","Jun","Jul","Aug","Sep","Okt","Nov","Dez"];
const byDate={};D.days.forEach((d,i)=>byDate[d.d]={...d,i});
function monday(d){const x=new Date(d);x.setHours(0,0,0,0);x.setDate(x.getDate()-((x.getDay()+6)%7));return x}
function iso(d){return d.getFullYear()+"-"+String(d.getMonth()+1).padStart(2,"0")+"-"+String(d.getDate()).padStart(2,"0")}
function kwnum(d){const x=new Date(d);x.setDate(x.getDate()+3-((x.getDay()+6)%7));
 const y=new Date(x.getFullYear(),0,4);return 1+Math.round(((x-y)/864e5-3+((y.getDay()+6)%7))/7)}
const W0=monday(dt(D.days[0].d)), WN=monday(dt(D.days[D.days.length-1].d));
const NW=Math.round((WN-W0)/6048e5)+1;
let wi=Math.min(NW-1,Math.max(0,Math.round((monday(T)-W0)/6048e5)));
function cal(dir){
 const mon=new Date(W0);mon.setDate(mon.getDate()+wi*7);
 const sun=new Date(mon);sun.setDate(sun.getDate()+6);
 document.getElementById("kwlab").textContent="KW "+kwnum(mon);
 document.getElementById("kwrg").innerHTML=mon.getDate()+". "+MO[mon.getMonth()]+
   " &ndash; "+sun.getDate()+". "+MO[sun.getMonth()]+" "+sun.getFullYear();
 let cells="",tot=0,don=0;
 for(let j=0;j<7;j++){
  const cur=new Date(mon);cur.setDate(cur.getDate()+j);
  const key=iso(cur),d=byDate[key],n=dd(key);
  if(!d){cells+=`<div class="dc void"><div class="dch"><span class="wd">${WD[cur.getDay()]}</span>
    <span class="dn">${cur.getDate()}</span><span class="mo">${MO[cur.getMonth()]}</span></div></div>`;continue}
  const done=d.o.filter((_,q)=>ST[d.i+"_"+q]).length;
  tot+=d.o.length;don+=done;
  const mins=d.o.reduce((a,o)=>a+(o.min||0),0);
  const st=done===0?"":done===d.o.length?"full":"part";
  const cls=["dc",d.t,n<0?"past":"",n===0?"today":""].filter(Boolean).join(" ");
  const bdg=d.t==="klausur"?'<span class="badge k">Klausur</span>':
            d.t==="deadline"?'<span class="badge d">Deadline</span>':"";
  const mods=[...new Set(d.o.map(o=>o.m))];
  const chips=mods.map(m=>{
    const alle=d.o.filter(o=>o.m===m);
    const fertig=alle.every((o,q)=>ST[d.i+"_"+d.o.indexOf(o)]);
    return `<span class="${fertig?"on":""}">${m}</span>`}).join("");
  cells+=`<div class="${cls}" onclick="dOpen('${key}')">${bdg}<div class="dch">
    <span class="wd">${WD[cur.getDay()]}</span><span class="dn">${cur.getDate()}</span>
    <span class="mo">${MO[cur.getMonth()]}</span><span class="dot ${st}"></span></div>
    <div class="dsum"><span class="cnt">${done}/${d.o.length}</span>
      <span class="mins">${Math.round(mins/60*10)/10} h</span></div>
    <div class="mods">${chips}</div>
    <div class="more">öffnen &#8599;</div>
    <div class="dbar"><i style="width:${done/d.o.length*100}%"></i></div>
  </div>`;
 }
 const g=document.getElementById("wgrid");
 g.className="wgrid";void g.offsetWidth;
 g.innerHTML=cells;
 if(dir)g.classList.add(dir>0?"slideL":"slideR");
 document.getElementById("wsum").textContent=tot?don+" von "+tot+" Zielen diese Woche":"keine Ziele";
 document.getElementById("wprev").disabled=wi<=0;
 document.getElementById("wnext").disabled=wi>=NW-1;
}
document.getElementById("wprev").onclick=()=>{if(wi>0){wi--;cal(-1)}};
document.getElementById("wnext").onclick=()=>{if(wi<NW-1){wi++;cal(1)}};
document.getElementById("wtoday").onclick=()=>{
 const t=Math.min(NW-1,Math.max(0,Math.round((monday(T)-W0)/6048e5)));
 const dir=t>wi?1:t<wi?-1:0;wi=t;cal(dir)};
document.addEventListener("keydown",e=>{
 if(document.getElementById("ov").classList.contains("on"))return;
 if(!document.getElementById("p-plan").classList.contains("on"))return;
 if(e.key==="ArrowLeft"&&wi>0){wi--;cal(-1)}
 if(e.key==="ArrowRight"&&wi<NW-1){wi++;cal(1)}});
cal();


/* ---------- Tagesdetail ---------- */
const TY={L:"lesen",U:"üben",D:"aus dem Kopf",T:"Test",W:"Wiederholung",O:"Orga"};
let dKey=null;
function dOpen(key){
 const d=byDate[key]; if(!d)return;
 dKey=key;
 const dte=dt(key), n=dd(key);
 document.getElementById("dtitle").textContent=
  String(dte.getDate()).padStart(2,"0")+"."+String(dte.getMonth()+1).padStart(2,"0")+"."+dte.getFullYear();
 document.getElementById("dwd").textContent=
  WD[dte.getDay()]+(n===0?" · heute":n>0?" · in "+n+" Tagen":" · vorbei");
 dRender();
 document.getElementById("dov").classList.add("on");
 document.body.style.overflow="hidden";
}
function dRender(){
 const d=byDate[dKey]; if(!d)return;
 const mins=d.o.reduce((a,o)=>a+(o.min||0),0);
 const done=d.o.filter((_,q)=>ST[d.i+"_"+q]).length;
 const offen=d.o.reduce((a,o,q)=>a+(ST[d.i+"_"+q]?0:(o.min||0)),0);
 document.getElementById("dbud").textContent=
  done+"/"+d.o.length+" · "+Math.round(mins/60*10)/10+" h geplant"+(offen?" · "+Math.round(offen/60*10)/10+" h offen":" · fertig");
 document.getElementById("dpr").style.width=(done/d.o.length*100)+"%";
 document.getElementById("dbody").innerHTML=d.o.map((o,q)=>{
  const id=d.i+"_"+q,c=!!ST[id];
  const jb=o.to?`<button class="go" title="Zum Lernstoff: ${o.m}" onclick="dJump('${o.m}','${o.m}-${o.to}')">&#8599;</button>`:"";
  return `<div class="tsk${c?" done":""}">
    <input type="checkbox" ${c?"checked":""} onchange="dTog('${id}')">
    <span class="meta"><span class="mk3">${o.m}</span>
      <span class="ty ${o.ty}">${TY[o.ty]||o.ty}</span>
      <span class="mn2">${o.min} Min</span></span>
    <span class="tt">${o.x}</span>${jb}</div>`}).join("")
  +'<div class="dlg"><b>lesen</b> = Stoff durchgehen &middot; <b>üben</b> = mit Vorlage rechnen '
  +'&middot; <b>aus dem Kopf</b> = ohne Vorlage &middot; <b>Test</b> = kalt, Zeit stoppen und Punktzahl notieren</div>';
}
function dTog(id){ST[id]=!ST[id];save();dRender();days();cal();lauf();arc();kpi();}
function dJump(m,id){dClose();jump(m,id);}
function dClose(){document.getElementById("dov").classList.remove("on");document.body.style.overflow="";}
document.getElementById("dov").onclick=e=>{if(e.target.id==="dov")dClose()};
document.addEventListener("keydown",e=>{if(e.key==="Escape")dClose()});

/* ---------- Zeitachse ---------- */
(function(){
 const mx=Math.max(...D.mods.map(m=>dd(m.d)));
 document.getElementById("tlbox").innerHTML=
 '<p class="fine">Balkenlänge = verbleibende Tage.</p>'+D.mods.map(m=>{
  const n=dd(m.d),w=Math.max(2,n/mx*100),col=n<7?"#C8102E":n<21?"#5b7fb5":"#2E9E5B";
  return `<div style="display:flex;align-items:center;gap:12px;padding:7px 0;border-bottom:1px solid var(--line)">
   <span style="font:600 13px ui-monospace,monospace;color:var(--mut);min-width:76px">${fm(m.d)}</span>
   <span style="height:12px;border-radius:3px;flex:1;background:var(--soft);position:relative">
     <i style="position:absolute;inset:0 auto 0 0;width:${w}%;border-radius:3px;background:${col}"></i></span>
   <span style="font:600 13px sans-serif;min-width:50px">${m.k}</span>
   <span class="fine">${n} T</span></div>`}).join("")
 +`<!--TXT:fenster-->`;
})();

/* ---------- Suche ---------- */
let IDX=null;
function idx(){
 if(IDX)return IDX;IDX=[];
 D.mods.filter(m=>m.has).forEach(m=>{
  const root=document.getElementById("m-"+m.k);if(!root)return;
  root.querySelectorAll("h2,h3,h4,p,li,td,pre").forEach(el=>{
   const t=(el.textContent||"").trim().replace(/\s+/g," ");
   if(t.length>18&&t.length<400){
    if(!el.id)el.id="x"+Math.random().toString(36).slice(2,9);
    IDX.push({k:m.k,id:el.id,t:t})}})});
 return IDX;
}
function search(q){
 const r=document.getElementById("sres");
 if(!q||q.length<2){r.innerHTML='<div class="sr fine">Mindestens zwei Zeichen …</div>';return}
 const ql=q.toLowerCase();
 const hits=idx().filter(x=>x.t.toLowerCase().includes(ql)).slice(0,40);
 if(!hits.length){r.innerHTML='<div class="sr fine">Nichts gefunden.</div>';return}
 r.innerHTML=hits.map((h,i)=>{
  const p=h.t.toLowerCase().indexOf(ql),s=Math.max(0,p-55);
  const frag=(s?"…":"")+h.t.slice(s,p)+"<mark>"+h.t.slice(p,p+q.length)+"</mark>"+h.t.slice(p+q.length,p+q.length+90)+"…";
  return `<div class="sr${i?"":" sel"}" data-k="${h.k}" data-id="${h.id}"><span class="sk">${h.k}</span>${frag}</div>`}).join("");
 r.querySelectorAll(".sr[data-k]").forEach(el=>el.onclick=()=>jump(el.dataset.k,el.dataset.id));
}
function jump(k,id){
 closeS();
 if(!document.getElementById("v-"+k))return;
 go(k);
 setTimeout(()=>{const e=document.getElementById(id);
  if(e){
   const pane=e.closest&&e.closest(".unit");
   if(pane&&!pane.classList.contains("on")){
    const u=pane.id.replace(/^[A-Z0-9]+-/,"");
    const pill=document.querySelector('.pill[data-u="'+u+'"]');
    if(pill)pill.click();
   }
   e.scrollIntoView({block:"center"});
   const o=e.style.background;e.style.background="#d6e4ff";
   setTimeout(()=>e.style.background=o,1600)}},60);
}
function openS(){document.getElementById("ov").classList.add("on");
 const i=document.getElementById("sin");i.value="";i.focus();search("")}
function closeS(){document.getElementById("ov").classList.remove("on")}
document.getElementById("osearch").onclick=openS;
document.getElementById("sin").oninput=e=>search(e.target.value);
document.getElementById("ov").onclick=e=>{if(e.target.id==="ov")closeS()};
document.getElementById("pov").onclick=e=>{if(e.target.id==="pov")pClose()};
document.addEventListener("keydown",e=>{
 if((e.ctrlKey||e.metaKey)&&e.key.toLowerCase()==="k"){e.preventDefault();openS()}
 if(e.key==="Escape"){closeS();pClose();}
 if(document.getElementById("ov").classList.contains("on")&&(e.key==="Enter")){
  const s=document.querySelector(".sr.sel[data-k]");if(s)jump(s.dataset.k,s.dataset.id)}
 if(document.getElementById("ov").classList.contains("on")&&(e.key==="ArrowDown"||e.key==="ArrowUp")){
  e.preventDefault();const all=[...document.querySelectorAll(".sr[data-k]")];
  let i=all.findIndex(x=>x.classList.contains("sel"));
  all.forEach(x=>x.classList.remove("sel"));
  i=Math.max(0,Math.min(all.length-1,i+(e.key==="ArrowDown"?1:-1)));
  if(all[i]){all[i].classList.add("sel");all[i].scrollIntoView({block:"nearest"})}}
});

/* ---------- Theme ---------- */
const th=document.getElementById("theme");

/* ---------- Der laufende Plan (Wochenraster ab START; davor = Archiv) ---------- */
const START=D.start;
function lhrs(d){return d.o.reduce((a,o)=>a+((d.t==="klausur"&&o.ty==="T"&&o.min>=90)?0:(o.min||0)),0)}
const LW0=monday(dt(START)), LWN=monday(dt(D.days[D.days.length-1].d));
const LNW=Math.round((LWN-LW0)/6048e5)+1;
let lwi=Math.min(LNW-1,Math.max(0,Math.round((monday(T)-LW0)/6048e5)));

function laufcal(dir){
 const mon=new Date(LW0);mon.setDate(mon.getDate()+lwi*7);
 const sun=new Date(mon);sun.setDate(sun.getDate()+6);
 document.getElementById("lkwlab").textContent="KW "+kwnum(mon);
 document.getElementById("lkwrg").innerHTML=mon.getDate()+". "+MO[mon.getMonth()]+
   " &ndash; "+sun.getDate()+". "+MO[sun.getMonth()]+" "+sun.getFullYear();
 let cells="",tot=0,don=0;
 for(let j=0;j<7;j++){
  const cur=new Date(mon);cur.setDate(cur.getDate()+j);
  const key=iso(cur),d=byDate[key],n=dd(key);
  if(!d||key<START){cells+='<div class="dc void"><div class="dch"><span class="wd">'+WD[cur.getDay()]+
    '</span><span class="dn">'+cur.getDate()+'</span><span class="mo">'+MO[cur.getMonth()]+
    '</span></div></div>';continue}
  const done=d.o.filter((_,q)=>ST[d.i+"_"+q]).length;
  tot+=d.o.length;don+=done;
  const st=done===0?"":done===d.o.length?"full":"part";
  const cls=["dc",d.t,n<0?"past":"",n===0?"today":""].filter(Boolean).join(" ");
  const bdg=d.t==="klausur"?'<span class="badge k">Klausur</span>':"";
  const chips=[...new Set(d.o.map(o=>o.m))].map(m=>{
    const fertig=d.o.every((o,q)=>o.m!==m||ST[d.i+"_"+q]);
    return '<span class="'+(fertig?"on":"")+'">'+m+'</span>'}).join("");
  cells+='<div class="'+cls+'" onclick="lOpen(\''+key+'\')">'+bdg+'<div class="dch">'+
    '<span class="wd">'+WD[cur.getDay()]+'</span><span class="dn">'+cur.getDate()+'</span>'+
    '<span class="mo">'+MO[cur.getMonth()]+'</span><span class="dot '+st+'"></span></div>'+
    '<div class="dsum"><span class="cnt">'+done+'/'+d.o.length+'</span>'+
    '<span class="mins">'+Math.round(lhrs(d)/60*10)/10+' h</span></div>'+
    '<div class="mods">'+chips+'</div><div class="more">öffnen &#8599;</div>'+
    '<div class="dbar"><i style="width:'+(done/d.o.length*100)+'%"></i></div></div>';
 }
 const g=document.getElementById("lwgrid");
 g.className="wgrid";void g.offsetWidth;
 g.innerHTML=cells;
 if(dir)g.classList.add(dir>0?"slideL":"slideR");
 document.getElementById("lwsum").textContent=tot?don+" von "+tot+" Zielen diese Woche":"keine Ziele";
 document.getElementById("lwprev").disabled=lwi<=0;
 document.getElementById("lwnext").disabled=lwi>=LNW-1;
}
/* Klick auf eine Karte: Tag unten im Detail aufklappen statt Overlay */
let lKey=null, lMod=null;
function lOpen(key){lKey=key;lMod=null;lauf();
 document.getElementById("laufheute").scrollIntoView({block:"nearest",behavior:"smooth"})}

function lauf(){
 const win=D.days.map((d,i)=>({...d,i})).filter(d=>d.d>=START);
 if(!win.length)return;
 const tot=win.reduce((a,d)=>a+d.o.length,0);
 const don=win.reduce((a,d)=>a+d.o.filter((_,j)=>ST[d.i+"_"+j]).length,0);
 const offen=win.reduce((a,d)=>a+d.o.reduce((b,o,j)=>b+(ST[d.i+"_"+j]?0:
   ((d.t==="klausur"&&o.ty==="T"&&o.min>=90)?0:(o.min||0))),0),0);
 document.getElementById("laufring").innerHTML=don+"/"+tot+"<small>Ziele</small>";
 document.getElementById("laufbar").style.width=(tot?don/tot*100:0)+"%";
 document.getElementById("laufs").innerHTML="ab "+fm(START)+" &middot; "+win.length+
   " Tage &middot; noch "+Math.round(offen/60)+" h Lernzeit";
 laufcal();

 /* Filterleiste: Tagesansicht plus je Modul ein Chip mit offenen Zielen */
 const mods={};
 win.forEach(d=>d.o.forEach((o,j)=>{
   if(o.m==="ORGA")return;
   if(!mods[o.m])mods[o.m]={tot:0,don:0};
   mods[o.m].tot++; if(ST[d.i+"_"+j])mods[o.m].don++;}));
 const order=D.mods.map(m=>m.k).filter(k=>mods[k]);
 let fh='<button class="lchip'+(lMod?"":" on")+'" onclick="lMod=null;lauf()">Tagesansicht</button>';
 order.forEach(k=>{const m=mods[k],offen=m.tot-m.don;
   fh+='<button class="lchip'+(lMod===k?" on":"")+(offen?"":" fertig")+'" onclick="lMod=\''+k+'\';lKey=null;lauf()">'+
       '<i class="kd" style="background:'+mcol(k)+';margin-right:0"></i>'+k+' <i>'+offen+' offen</i></button>';});
 document.getElementById("lauffil").innerHTML=fh;

 if(lMod){laufmod(win);return;}

 const cur=win.find(d=>d.d===lKey)||win.find(d=>d.d===iso(T))||win.find(d=>dd(d.d)>=0)||win[win.length-1];
 const n=dd(cur.d);
 document.getElementById("laufheuteh").textContent=
   n===0?"Heute im Detail":fm(cur.d)+" im Detail";
 let h='<div class="ltoday"><div class="th"><b>'+fm(cur.d)+'</b><span>'+
   (n===0?"heute":n===1?"morgen":n>0?"in "+n+" Tagen":Math.abs(n)+" Tage her")+
   " &middot; "+cur.o.length+" Ziele &middot; "+Math.round(lhrs(cur)/60*10)/10+" h"+
   (n!==0?' &middot; <a href="#" onclick="lKey=null;lauf();return false">zurück zu heute</a>':"")+
   "</span></div>";
 h+=lbody(cur);
 document.getElementById("laufheute").innerHTML=h+"</div>";
}
/* ---------- Archiv: derselbe Aufbau, aber alles VOR START ---------- */
const AEND="2026-08-27";
const AW0=monday(dt(D.days[0].d)), AWN=monday(dt(AEND));
const ANW=Math.max(1,Math.round((AWN-AW0)/6048e5)+1);
let awi=ANW-1, aKey=null, aMod=null;

function arccal(dir){
 const mon=new Date(AW0);mon.setDate(mon.getDate()+awi*7);
 const sun=new Date(mon);sun.setDate(sun.getDate()+6);
 document.getElementById("akwlab").textContent="KW "+kwnum(mon);
 document.getElementById("akwrg").innerHTML=mon.getDate()+". "+MO[mon.getMonth()]+
   " &ndash; "+sun.getDate()+". "+MO[sun.getMonth()]+" "+sun.getFullYear();
 let cells="",tot=0,don=0;
 for(let j=0;j<7;j++){
  const cur=new Date(mon);cur.setDate(cur.getDate()+j);
  const key=iso(cur),d=byDate[key];
  if(!d||key>=START){cells+='<div class="dc void"><div class="dch"><span class="wd">'+WD[cur.getDay()]+
    '</span><span class="dn">'+cur.getDate()+'</span><span class="mo">'+MO[cur.getMonth()]+
    '</span></div></div>';continue}
  const done=d.o.filter((_,q)=>ST[d.i+"_"+q]).length;
  tot+=d.o.length;don+=done;
  const st=done===0?"":done===d.o.length?"full":"part";
  const cls=["dc",d.t,"past"].filter(Boolean).join(" ");
  const bdg=d.t==="klausur"?'<span class="badge k">Klausur</span>':"";
  const chips=[...new Set(d.o.map(o=>o.m))].map(m=>{
    const fertig=d.o.every((o,q)=>o.m!==m||ST[d.i+"_"+q]);
    return '<span class="'+(fertig?"on":"")+'">'+m+'</span>'}).join("");
  cells+='<div class="'+cls+'" onclick="aOpen(\''+key+'\')">'+bdg+'<div class="dch">'+
    '<span class="wd">'+WD[cur.getDay()]+'</span><span class="dn">'+cur.getDate()+'</span>'+
    '<span class="mo">'+MO[cur.getMonth()]+'</span><span class="dot '+st+'"></span></div>'+
    '<div class="dsum"><span class="cnt">'+done+'/'+d.o.length+'</span>'+
    '<span class="mins">'+Math.round(lhrs(d)/60*10)/10+' h</span></div>'+
    '<div class="mods">'+chips+'</div><div class="more">öffnen &#8599;</div>'+
    '<div class="dbar"><i style="width:'+(done/d.o.length*100)+'%"></i></div></div>';
 }
 const g=document.getElementById("awgrid");
 g.className="wgrid";void g.offsetWidth;
 g.innerHTML=cells;
 if(dir)g.classList.add(dir>0?"slideL":"slideR");
 document.getElementById("awsum").textContent=tot?don+" von "+tot+" Zielen diese Woche":"keine Ziele";
 document.getElementById("awprev").disabled=awi<=0;
 document.getElementById("awnext").disabled=awi>=ANW-1;
}
function aOpen(key){aKey=key;aMod=null;arc();
 document.getElementById("archeute").scrollIntoView({block:"nearest",behavior:"smooth"})}

function arc(){
 const win=D.days.map((d,i)=>({...d,i})).filter(d=>d.d<START);
 if(!win.length)return;
 const tot=win.reduce((a,d)=>a+d.o.length,0);
 const don=win.reduce((a,d)=>a+d.o.filter((_,j)=>ST[d.i+"_"+j]).length,0);
 document.getElementById("arcring").innerHTML=don+"/"+tot+"<small>Ziele</small>";
 document.getElementById("arcbar").style.width=(tot?don/tot*100:0)+"%";
 document.getElementById("arcs").innerHTML=fm(win[0].d)+" &ndash; "+fm(AEND)+" &middot; "+
   win.length+" Tage &middot; hake ab, was du davon wirklich gemacht hast";
 arccal();
 const mods={};
 win.forEach(d=>d.o.forEach((o,j)=>{
   if(o.m==="ORGA")return;
   if(!mods[o.m])mods[o.m]={tot:0,don:0};
   mods[o.m].tot++; if(ST[d.i+"_"+j])mods[o.m].don++;}));
 const order=D.mods.map(m=>m.k).filter(k=>mods[k]);
 let fh='<button class="lchip'+(aMod?"":" on")+'" onclick="aMod=null;arc()">Tagesansicht</button>';
 order.forEach(k=>{const m=mods[k];
   fh+='<button class="lchip'+(aMod===k?" on":"")+(m.don===m.tot?" fertig":"")+
       '" onclick="aMod=\''+k+'\';aKey=null;arc()">'+'<i class="kd" style="background:'+mcol(k)+';margin-right:0"></i>'+k+' <i>'+m.don+'/'+m.tot+'</i></button>';});
 document.getElementById("arcfil").innerHTML=fh;
 if(aMod){arcmod(win);return;}
 const cur=win.find(d=>d.d===aKey)||win[win.length-1];
 let h='<div class="ltoday"><div class="th"><b>'+fm(cur.d)+'</b><span>'+
   Math.abs(dd(cur.d))+" Tage her &middot; "+cur.o.length+" Ziele &middot; "+
   Math.round(lhrs(cur)/60*10)/10+" h</span></div>";
 document.getElementById("archeuteh").textContent=fm(cur.d)+" im Detail";
 cur.o.forEach((o,j)=>{h+=lrow2(cur,o,j)});
 document.getElementById("archeute").innerHTML=h+"</div>";
}
function arcmod(win){
 const days=win.filter(d=>d.o.some(o=>o.m===aMod));
 const tot=days.reduce((a,d)=>a+d.o.filter(o=>o.m===aMod).length,0);
 const don=days.reduce((a,d)=>a+d.o.filter((o,j)=>o.m===aMod&&ST[d.i+"_"+j]).length,0);
 document.getElementById("archeuteh").innerHTML=
   "Alle "+aMod+"-Aufgaben bis "+fm(AEND)+" &middot; "+don+"/"+tot+" abgehakt";
 let h='<div class="ltoday">';
 days.forEach(d=>{
  h+='<div class="ldh"><b>'+fm(d.d)+'</b><span>'+Math.abs(dd(d.d))+' Tage her</span>'+
     (d.t==="klausur"?'<span class="kl">Klausur</span>':'')+
     '<a href="#" onclick="aMod=null;aKey=\''+d.d+'\';arc();return false">nur diesen Tag</a></div>';
  d.o.forEach((o,j)=>{if(o.m===aMod)h+=lrow2(d,o,j)});
 });
 document.getElementById("archeute").innerHTML=h+"</div>";
}

/* ---------- Stand als Text ---------- */
function stand(){
 const L=[], strip=t=>t.replace(/<[^>]+>/g,"").replace(/\s+/g," ").trim();
 L.push("STAND "+fm(iso(T))+"  (aus klausuren.html)");
 [["ARCHIV  bis "+fm(AEND), d=>d.d<START],
  ["LAUFENDER PLAN  ab "+fm(START), d=>d.d>=START]].forEach(function(p){
  const win=D.days.map((d,i)=>({...d,i})).filter(p[1]);
  L.push(""); L.push("=== "+p[0]+" ===");
  const mods={};
  win.forEach(d=>d.o.forEach((o,j)=>{
   if(o.m==="ORGA")return;
   const M=mods[o.m]||(mods[o.m]={tot:0,don:0,min:0,offen:[]});
   M.tot++;
   if(ST[d.i+"_"+j]){M.don++;M.min+=(o.min||0);}
   else M.offen.push(d.d.slice(8,10)+"."+d.d.slice(5,7)+"  "+(o.min||0)+"'  "+strip(o.x).slice(0,58));
  }));
  const order=D.mods.map(m=>m.k).filter(k=>mods[k]);
  if(!order.length){L.push("(nichts)");return}
  order.forEach(k=>{const M=mods[k];
   L.push(k.padEnd(5)+" "+String(M.don+"/"+M.tot).padEnd(8)+" abgehakt   "+
          Math.round(M.min/60*10)/10+" h gemacht");});
  const rest=order.filter(k=>mods[k].offen.length);
  if(rest.length){
   L.push(""); L.push("offen geblieben:");
   rest.forEach(k=>{const M=mods[k];
    M.offen.slice(0,8).forEach(t=>L.push("  "+k.padEnd(5)+t));
    if(M.offen.length>8)L.push("  "+k.padEnd(5)+"… und "+(M.offen.length-8)+" weitere");
   });
  }
 });
 return L.join("\n");
}

function lmin(a){return a.reduce((s,e)=>s+e[0].min,0)}

/* ---------- Blockdetail: Ueberschrift in der Zeile, Schritte im Panel ---------- */
const TYN={L:"lesen",U:"\u00fcben",D:"aus dem Kopf",T:"Test",W:"Wiederholung",O:"Orga",V:"K\u00fcr"};
let SP={};try{SP=JSON.parse(localStorage.getItem("kl-step")||"{}")}catch(e){}
function spSave(){try{localStorage.setItem("kl-step",JSON.stringify(SP))}catch(e){}}
/* Modul-Aufgabensprung: Module tragen sich in window.QJUMP ein. */
function lhead(x){
 const m=String(x).match(/^\s*<b>([\s\S]*?)<\/b>/);
 let h=m?m[1]:String(x);
 h=h.replace(/<[^>]+>/g,"").trim().replace(/[.:\u2014\u2013]\s*$/,"");
 if(!m&&h.length>84)h=h.slice(0,84).replace(/\s\S*$/,"")+"\u2026";
 return h;
}
let pCur=null;
function pOpen(di,j){
 const d=D.days[di],o=d.o[j];pCur=[di,j];
 const st=o.st||[];
 let h='<div class="ph"><div class="pmeta"><span class="pmk">'+o.m+'</span>'+
   '<span class="pty">'+fm(d.d)+' &middot; '+o.min+' Min &middot; '+(TYN[o.ty]||o.ty)+
   (o.ty==="V"?' <b>(K\u00fcr \u2014 optional)</b>':'')+'</span>'+
   '<button class="pcl" onclick="pClose()" title="Schlie\u00dfen">&times;</button></div>'+
   '<h3>'+lhead(o.x)+'</h3></div><div class="pb">';
 if(st.length){
  h+='<div class="plab">Der Weg \u2014 '+st.length+' Schritte</div>';
  st.forEach((sx,k)=>{
   const id=di+"_"+j+"_"+k,c=!!SP[id];
   h+='<div class="stp'+(c?" sdone":"")+'"><input type="checkbox" '+(c?"checked":"")+
     ' onchange="pStep(\''+id+'\')"><div class="sn">'+(k+1)+'</div><div class="sc">'+
     '<div class="st1">'+sx.t+'</div>'+
     (sx.d?'<div class="st2">'+sx.d+'</div>':'')+
     '<div class="sgo">'+
     (sx.to?'<button onclick="pGo(\''+o.m+'\',\''+o.m+'-'+sx.to+'\')">&#8599; Abschnitt</button>':'')+
     (sx.q&&sx.q.length?'<span class="qlab">Aufgaben</span>'+
        sx.q.map(n=>'<button class="qb" onclick="pQ(\''+o.m+'\','+n+')">'+n+'</button>').join(""):'')+
     (sx.min?'<span class="qlab" style="margin-left:4px">'+sx.min+' Min</span>':'')+
     '</div></div></div>';
  });
  const dn=st.filter((_,k)=>!!SP[di+"_"+j+"_"+k]).length;
  h+='<div class="pprog'+(dn===st.length?" ok":"")+'">'+(dn===st.length
    ?"&#10003; <b>Block fertig</b> \u2014 in der Tagesliste automatisch abgehakt."
    :"<b>"+dn+" von "+st.length+"</b> Schritten erledigt")+'</div>';
 }else if(o.to){
  h+='<div class="sgo" style="margin-top:14px"><button onclick="pGo(\''+o.m+'\',\''+o.m+'-'+o.to+'\')">&#8599; Zum Lernstoff</button></div>';
 }
 if(o.mk&&o.mk.length){
  h+='<div class="plab">Danach im Kopf \u2014 das nimmst du mit</div><ul class="pmk2">'+
     o.mk.map(x=>'<li>'+x+'</li>').join("")+'</ul>';
 }
 const rest=String(o.x).replace(/^\s*<b>[\s\S]*?<\/b>\s*/,"").trim();
 if(rest)h+='<div class="plab">Worum es geht</div><div class="ptxt">'+rest+'</div>';
 h+='</div>';
 const b=document.getElementById("pbox");b.innerHTML=h;b.scrollTop=0;
 document.getElementById("pov").classList.add("on");
}
function pClose(){document.getElementById("pov").classList.remove("on")}
/* Schritt umschalten. Sind danach ALLE Schritte des Blocks gehakt, haekt sich der
   Block in der Tagesliste selbst ab. Nimmst du einen Schritt wieder raus, waehrend
   der Block komplett war, geht der Blockhaken wieder weg. Ein von Hand gesetzter
   Haken bei unvollstaendigen Schritten bleibt unangetastet. */
function pStep(id){
 const p=id.split("_"),di=+p[0],j=+p[1],bid=di+"_"+j;
 const dd=D.days[di],o=dd&&dd.o?dd.o[j]:null,st=(o&&o.st)||[];
 const was=st.length>0&&st.every((_,k)=>!!SP[bid+"_"+k]);
 SP[id]=!SP[id];spSave();
 if(st.length){
  const now=st.every((_,k)=>!!SP[bid+"_"+k]);
  if(now&&!ST[bid]){ST[bid]=true;save();days();cal();arc();kpi()}
  else if(was&&!now&&ST[bid]){ST[bid]=false;save();days();cal();arc();kpi()}
 }
 if(pCur)pOpen(pCur[0],pCur[1]);lauf()
}
function pGo(k,id){pClose();jump(k,id)}
function pQ(k,n){pClose();jump(k,k+"-uebung");
 setTimeout(()=>{try{if(window.QJUMP&&QJUMP[k])QJUMP[k](n)}catch(e){}},420)}
function pDone(di,j){const st=(D.days[di].o[j].st)||[];
 if(!st.length)return null;
 return [st.filter((_,k)=>!!SP[di+"_"+j+"_"+k]).length,st.length];}

/* Die Klausur selbst ist keine Lernzeit — sie zaehlt nicht ins Tagespensum. */
function lexam(o){return /KLAUSUR/.test(o.x)}
function llern(a){return a.reduce((s,e)=>s+(lexam(e[0])?0:e[0].min),0)}
/* Pflicht ueber der Linie, Kuer darunter. Die Linie sagt, wann der Tag erledigt ist. */
function lbody(d){
 let h="",pf=[],ku=[];
 d.o.forEach((o,j)=>{(o.ty==="V"?ku:pf).push([o,j])});
 pf.forEach(e=>{h+=lrow2(d,e[0],e[1])});
 if(!pf.length)return h+ku.map(e=>lrow2(d,e[0],e[1])).join("");
 const done=pf.every(e=>!!ST[d.i+"_"+e[1]]);
 const lern=llern(pf), nk=pf.filter(e=>!lexam(e[0])).length, hrs=Math.round(lern/60*10)/10;
 const kl=pf.length-nk;
 h+='<div class="feier'+(done?" ok":"")+'">'+(done
   ?"&#10003; <b>Tagesziel erreicht.</b> Der Tag z\u00e4hlt als erledigt"+
    (ku.length?" \u2014 was darunter steht, ist freiwillig.":".")
   :"&#9209; <b>Bis hierhin, dann ist genug.</b> "+nk+" Pflichtbl\u00f6cke &middot; "+hrs+" h Lernzeit"+
    (kl?" (die Klausur nicht gerechnet)":"")+
    (ku.length?" &middot; darunter "+ku.length+" K\u00fcr-Block"+(ku.length>1?"e":"")+", nur wenn noch Luft ist":""))
   +"</div>";
 ku.forEach(e=>{h+=lrow2(d,e[0],e[1])});
 return h;
}
function lrow2(d,o,j){
 const id=d.i+"_"+j, c=!!ST[id];
 const jb=o.to?'<button class="jp2" title="Zum Lernstoff: '+o.m+'" onclick="jump(\''+o.m+'\',\''+o.m+"-"+o.to+'\')">&#8599;</button>':"";
 const pr=pDone(d.i,j);
 const nq=o.st?o.st.reduce((a,x)=>a+((x.q||[]).length),0):0;
 const sub=pr?(pr[0]+" von "+pr[1]+" Schritten"+(nq?" \u00b7 "+nq+" Aufgaben":"")):
   (o.st?o.st.length+" Schritte":"");
 return '<div class="lt'+(c?" done":"")+(o.ty==="V"?" kur":"")+'"><input type="checkbox" id="L'+id+'" '+(c?"checked":"")+
   ' onchange="tog(\''+id+'\')"><span class="mk4">'+o.m+'</span><span class="m4">'+o.min+
   ' Min</span><div class="ltx" onclick="pOpen('+d.i+','+j+')" title="Details und Schritte"><b>'+
   lhead(o.x)+'</b>'+(sub?'<span class="lsub">'+sub+'</span>':'')+'</div>'+
   '<button class="chev" onclick="pOpen('+d.i+','+j+')" title="Details und Schritte">&#9656;</button>'+jb+'</div>';
}
/* Modulansicht: alle Aufgaben eines Moduls ab START, nach Tagen gruppiert */
function laufmod(win){
 const days=win.filter(d=>d.o.some(o=>o.m===lMod));
 const off=days.reduce((a,d)=>a+d.o.reduce((b,o,j)=>b+((o.m===lMod&&!ST[d.i+"_"+j])?(o.min||0):0),0),0);
 const tot=days.reduce((a,d)=>a+d.o.filter(o=>o.m===lMod).length,0);
 const don=days.reduce((a,d)=>a+d.o.filter((o,j)=>o.m===lMod&&ST[d.i+"_"+j]).length,0);
 document.getElementById("laufheuteh").innerHTML=
   "Alle "+lMod+"-Aufgaben ab "+fm(START)+" &middot; "+don+"/"+tot+" erledigt &middot; noch "+
   Math.round(off/60*10)/10+" h";
 let h='<div class="ltoday">';
 days.forEach(d=>{
  const n=dd(d.d);
  h+='<div class="ldh"><b>'+fm(d.d)+'</b><span>'+
     (n===0?"heute":n===1?"morgen":n>0?"in "+n+" Tagen":Math.abs(n)+" Tage her")+'</span>'+
     (d.t==="klausur"?'<span class="kl">Klausur</span>':'')+
     '<a href="#" onclick="lMod=null;lKey=\''+d.d+'\';lauf();return false">nur diesen Tag</a></div>';
  d.o.forEach((o,j)=>{if(o.m===lMod)h+=lrow2(d,o,j)});
 });
 document.getElementById("laufheute").innerHTML=h+"</div>";
}
document.getElementById("lwprev").onclick=()=>{if(lwi>0){lwi--;laufcal(-1)}};
document.getElementById("lwnext").onclick=()=>{if(lwi<LNW-1){lwi++;laufcal(1)}};
document.getElementById("lwtoday").onclick=()=>{
 const t=Math.min(LNW-1,Math.max(0,Math.round((monday(T)-LW0)/6048e5)));
 const dir=t>lwi?1:t<lwi?-1:0;lwi=t;lKey=null;lMod=null;lauf();if(dir)laufcal(dir)};
lauf();

/* ---------- Archiv: Bedienung ---------- */
document.getElementById("awprev").onclick=()=>{if(awi>0){awi--;arccal(-1)}};
document.getElementById("awnext").onclick=()=>{if(awi<ANW-1){awi++;arccal(1)}};
document.getElementById("awlast").onclick=()=>{
 const dir=(ANW-1)>awi?1:-1;awi=ANW-1;aKey=null;aMod=null;arc();arccal(dir)};
(function(){
 const b=document.getElementById("tgla"),w=document.getElementById("arcwrap"),h=document.getElementById("tglah");
 let open=false;try{open=localStorage.getItem("kl-arc")==="1"}catch(e){}
 const set=()=>{w.classList.toggle("open",open);b.classList.toggle("open",open);
  h.textContent=open?"zuklappen":"aufklappen und abhaken";
  try{localStorage.setItem("kl-arc",open?"1":"0")}catch(e){}
  if(open)arc();};
 b.onclick=()=>{open=!open;set()};set();
})();
(function(){
 const out=document.getElementById("expout"), msg=document.getElementById("expmsg");
 document.getElementById("expbtn").onclick=()=>{
  out.value=stand();out.classList.add("on");out.focus();out.select();
  msg.textContent="markiert \u2014 Strg+C, dann in den Chat kleben";};
 document.getElementById("expcopy").onclick=async()=>{
  if(!out.value)out.value=stand();
  out.classList.add("on");
  try{await navigator.clipboard.writeText(out.value);msg.textContent="kopiert \u2713";}
  catch(e){out.focus();out.select();msg.textContent="Zwischenablage gesperrt \u2014 mit Strg+C kopieren";}
 };
})();
arc();

try{
  const w=localStorage.getItem("kl-theme");
  if(w==="dark"||w==="light") document.documentElement.dataset.t=w;
  else if(matchMedia("(prefers-color-scheme: dark)").matches) document.documentElement.dataset.t="dark";
}catch(e){}
th.textContent=document.documentElement.dataset.t==="dark"?"Light":"Dark";
th.onclick=()=>{const d=document.documentElement.dataset.t==="dark";
 document.documentElement.dataset.t=d?"light":"dark";
 th.textContent=d?"Dark":"Light";
 try{localStorage.setItem("kl-theme",d?"light":"dark")}catch(e){}};

/* ---------- Start ---------- */
window.addEventListener("hashchange",()=>go(location.hash.slice(1)||"hub"));
go(location.hash.slice(1)||"hub");
</script>
<script>/*MODJS*/</script>
</html>
"""

if __name__ == "__main__":
    build()

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""patch.py — Textstellen in einer HTML-Datei ersetzen, tolerant und nachvollziehbar.

    python3 patch.py module/KAF/KAF.html ops.json           ausfuehren
    python3 patch.py module/KAF/KAF.html ops.json --dry      nur pruefen

ops.json ist eine Liste von Operationen:

  {"id":"kurzname", "op":"replace",  "anchor":"...", "text":"..."}
  {"id":"...",      "op":"before",   "anchor":"...", "text":"..."}
  {"id":"...",      "op":"after",    "anchor":"...", "text":"..."}
  {"id":"...",      "op":"between",  "anchor":"...", "end":"...", "text":"..."}
  {"id":"...",      "op":"css",      "text":"..."}        haengt CSS an den Hellmodus
  {"id":"...",      "op":"cssdark",  "text":"..."}        haengt CSS an den Dunkelmodus

Warum tolerant: die Datei mischt literale Zeichen und Entities. Ein Anker mit
"&#183;" findet ein literales "·" nicht und umgekehrt — das war die haeufigste
Fehlerquelle. patch.py vergleicht deshalb auf einer normalisierten Fassung und
rechnet die Position zurueck.

Es wird NUR geschrieben, wenn ALLE Operationen genau einmal treffen. Sonst
bleibt die Datei unberuehrt und der Bericht sagt, welche Operation warum nicht
gegriffen hat — dann muss nur diese eine nachgebessert werden, nicht alles.
Vor dem Schreiben entsteht <datei>.bak-patch.
"""
import sys, os, re, io, json, html

# Zeichen, die in beiden Schreibweisen vorkommen
PAIRS = [("&#183;", "·"), ("&#8212;", "—"), ("&#8211;", "–"),
         ("&#8594;", "→"), ("&#8599;", "↗"), ("&#8722;", "−"),
         ("&#252;", "ü"), ("&#228;", "ä"), ("&#246;", "ö"),
         ("&#223;", "ß"), ("&#196;", "Ä"), ("&#214;", "Ö"),
         ("&#220;", "Ü"), ("&#8222;", "„"), ("&#8220;", "“"),
         ("&nbsp;", " ")]


def norm(t):
    """Beide Schreibweisen auf dieselbe Form bringen, Laenge bleibt egal:
       wir suchen danach nur noch ueber die normalisierte Fassung."""
    for ent, lit in PAIRS:
        t = t.replace(ent, lit)
    return t


def build_map(s):
    """normalisierter Text + Abbildung norm-Index -> Original-Index."""
    out, idx, i = [], [], 0
    while i < len(s):
        hit = None
        if s[i] == "&":
            for ent, lit in PAIRS:
                if s.startswith(ent, i):
                    hit = (ent, lit)
                    break
        if hit:
            out.append(hit[1])
            idx.append(i)
            i += len(hit[0])
        else:
            out.append(s[i])
            idx.append(i)
            i += 1
    idx.append(len(s))
    return "".join(out), idx


def find(s, nrm, idx, needle):
    """gibt (start, ende) im ORIGINAL zurueck, oder die Trefferzahl bei != 1."""
    n = norm(needle)
    c = nrm.count(n)
    if c != 1:
        return None, c
    a = nrm.index(n)
    return (idx[a], idx[a + len(n)]), 1


CSS_ANCHOR = ".pic b:first-child{color:#b0522c}\n"
DARK_ANCHOR = "@media (prefers-color-scheme: dark){\n:root{color-scheme:dark}\n"


def main(argv):
    if len(argv) < 2:
        print(__doc__)
        return 2
    path, opsfile = argv[0], argv[1]
    dry = "--dry" in argv
    s = io.open(path, encoding="utf-8").read()
    ops = json.loads(io.open(opsfile, encoding="utf-8").read())
    if isinstance(ops, dict):
        ops = [ops]

    plan, fail = [], 0
    for o in ops:
        oid = o.get("id", "?")
        op = o.get("op", "replace")
        if op in ("css", "cssdark"):
            anc = CSS_ANCHOR if op == "css" else DARK_ANCHOR
            o = dict(o, op="after", anchor=anc)
            op = "after"
        nrm, idx = build_map(s)
        span, cnt = find(s, nrm, idx, o["anchor"])
        if span is None:
            print("  FEHLT  %-16s Anker %s mal gefunden: %s"
                  % (oid, cnt, o["anchor"][:64].replace("\n", " ")))
            fail += 1
            continue
        a, b = span
        if op == "between":
            span2, cnt2 = find(s, nrm, idx, o["end"])
            if span2 is None:
                print("  FEHLT  %-16s end %s mal gefunden" % (oid, cnt2))
                fail += 1
                continue
            b = span2[1]
        if op == "replace":
            neu = s[:a] + o["text"] + s[b:]
        elif op == "between":
            neu = s[:a] + o["text"] + s[b:]
        elif op == "before":
            neu = s[:a] + o["text"] + s[a:]
        elif op == "after":
            neu = s[:b] + o["text"] + s[b:]
        else:
            print("  FEHLT  %-16s unbekannte op: %s" % (oid, op))
            fail += 1
            continue
        plan.append((oid, op, len(neu) - len(s)))
        s = neu
        print("  ok     %-16s %-8s %+d Zeichen" % (oid, op, plan[-1][2]))

    if fail:
        print("\n%d von %d Operationen ohne Treffer — NICHTS geschrieben." % (fail, len(ops)))
        print("Nur die fehlenden nachbessern und erneut laufen lassen.")
        return 1
    if dry:
        print("\n--dry: alles wuerde treffen, nichts geschrieben.")
        return 0
    io.open(path + ".bak-patch", "w", encoding="utf-8").write(
        io.open(path, encoding="utf-8").read())
    io.open(path, "w", encoding="utf-8").write(s)
    print("\n%d Operationen geschrieben. Backup: %s.bak-patch" % (len(ops), os.path.basename(path)))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

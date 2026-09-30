#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
build.py — baut aus shell.html, gen2.js und data/*.js die eine Datei KAF-Trainer.html.

Aufruf:  python build.py
Ergebnis: ../KAF-Trainer.html  (liegt dann neben KAF.html)

Neues Kapitel ergaenzen: data/kapN.js anlegen und unten in QUIZZES eintragen.
Alle Inhalte in data/ und gen2.js sind erfundene Demo-Daten.
"""
import io, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
OUT  = os.path.join(HERE, "..", "KAF-Trainer.html")

KLAUSUREN = ["probeklausur.js"]
QUIZZES   = ["kap1.js", "kap2.js"]                   # Aufgaben je Kapitel
BEGRIFFE  = ["begriffe1.js"]                        # Karteikarten
SPICK     = "spick.js"


def lies(name):
    p = os.path.join(HERE, "data", name)
    if not os.path.exists(p):
        sys.exit("fehlt: " + p)
    return io.open(p, encoding="utf-8").read().strip().rstrip(",")


def main():
    shell = io.open(os.path.join(HERE, "shell.html"), encoding="utf-8").read()
    if "/*__DATA__*/" not in shell:
        sys.exit("Marker /*__DATA__*/ fehlt in shell.html")

    spick = lies(SPICK) if os.path.exists(os.path.join(HERE, "data", SPICK)) else "[]"
    daten = "{\nklausuren:[\n%s\n],\nquizzes:[\n%s\n],\nbegriffe:[\n%s\n],\nspick:%s\n}" % (
        ",\n".join(lies(f) for f in KLAUSUREN),
        ",\n".join(lies(f) for f in QUIZZES),
        ",\n".join(lies(f) for f in BEGRIFFE),
        spick,
    )
    gen2 = io.open(os.path.join(HERE, "gen2.js"), encoding="utf-8").read()
    gen2 = gen2[gen2.index("{"):].strip()          # Kommentarkopf abschneiden
    out = shell.replace("/*__DATA__*/{}", daten).replace("/*__GEN2__*/{}", gen2)
    io.open(OUT, "w", encoding="utf-8").write(out)

    kb = len(out.encode("utf-8")) / 1024.0
    print("OK  -> %s  (%.0f KB)" % (os.path.normpath(OUT), kb))
    print("    Klausuren: %s" % (", ".join(KLAUSUREN) or "-"))
    print("    Aufgaben : %s" % (", ".join(QUIZZES) or "-"))
    print("    Begriffe : %s" % (", ".join(BEGRIFFE) or "-"))


if __name__ == "__main__":
    main()

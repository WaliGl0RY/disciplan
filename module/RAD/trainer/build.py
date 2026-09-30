#!/usr/bin/env python3
"""build.py — baut RAD-Trainer.html aus shell.html + data/lectures.json + data/sims.json
+ data/spick.json + data/summary.json (Demo-Daten, erfunden).

Der Klausurtermin fuer den Countdown kommt aus data/meta.json ("exam_in_days"),
relativ zum Bautag, damit die Demo immer eine laufende Vorbereitung zeigt."""
import datetime, io, os, json
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "RAD-Trainer.html")
def j(n): return json.load(io.open(os.path.join(HERE, "data", n), encoding="utf-8"))
shell = io.open(os.path.join(HERE, "shell.html"), encoding="utf-8").read()
meta = j("meta.json")
exam = datetime.datetime.combine(datetime.date.today() + datetime.timedelta(days=meta["exam_in_days"]),
                                 datetime.time(10, 0))
data = {"lectures": j("lectures.json"), "sims": j("sims.json"), "spick": j("spick.json"),
        "summary": j("summary.json"), "exam": exam.isoformat()}
blob = json.dumps(data, ensure_ascii=False).replace("</", "<\\/")
io.open(OUT, "w", encoding="utf-8", newline="\n").write(shell.replace("/*__DATA__*/{}", blob))
print("OK ->", os.path.normpath(OUT), "|", sum(len(l["fragen"]) for l in data["lectures"]), "Fragen,",
      len(data["sims"]), "Simulationen")

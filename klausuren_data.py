# -*- coding: utf-8 -*-
"""
klausuren_data.py — Daten fuer build.py: MODULES (Moduldaten), DAYS (Tagesplan) und
TEXT (Titel und Strategietexte der Uebersicht).

In diesem Repo stehen hier nur DEMO-Daten fuer drei erfundene Module (KAF, GAR, RAD).
Die Struktur ist dieselbe wie im echten Einsatz: eigene Module eintragen, dann
`python build.py`.

check.py --plan liest diese Datei als Text (Tagesplan-Pruefung). Deshalb:
Texte in doppelten Anfuehrungszeichen ohne innere doppelte Anfuehrungszeichen,
Schrittlisten als JSON-kompatible Dicts.
"""

# ─────────────────────────── Moduldaten ───────────────────────────
# k      Kuerzel = Ordnername unter module/ und Dateiname <k>.html
# name   voller Modulname
# d, t   Klausurdatum (YYYY-MM-DD) und Uhrzeit ("?" wenn unbekannt)
# v      Versuch (1, 2, 3)
# typ    "PF" Pflicht · "WP" Wahlpflicht
# prof   Pruefer
# mode   Modus aus der Analyse (siehe CLAUDE.md) oder None
# desc   ein, zwei Saetze Begruendung (HTML erlaubt)
# trainer  optional: dict(file=..., was=...) — nur wenn es eine Trainer-App gibt
MODULES = [
 dict(k="KAF", name="Kaffeemaschinen-Technik (Demo)", d="2026-09-02", t="10:00", v=1, typ="PF", prof="Demo",
      trainer=dict(file="module/KAF/KAF-Trainer.html", was="Demo-Trainer: Begriffe, zwei Kapitel, Probeklausur, Spickzettel"),
      mode="DEMO · ALTKLAUSUR-DRIVEN", desc="<b>Erfundenes Beispielmodul.</b> Zeigt ein Lerndokument mit Zustandsautomat und einen Trainer der ersten Generation."),
 dict(k="RAD", name="Fahrrad-Werkstatt (Demo)",       d="2026-09-04", t="14:00", v=2, typ="PF", prof="Demo",
      trainer=dict(file="module/RAD/RAD-Trainer.html", was="Demo-Trainer der zweiten Generation: Dashboard, Simulationen, Spickzettel"),
      mode="DEMO · MIXED", desc="Erfundenes Beispielmodul mit Praxisteil. Zeigt den Trainer der zweiten Generation."),
 dict(k="GAR", name="Gartenplanung (Demo)",           d="2026-09-07", t="?",     v=1, typ="WP", prof="Demo",
      mode=None, desc="Erfundenes Beispielmodul ohne Trainer und noch ohne Modus."),
]

# ─────────────────────────── Plan-Konfiguration ───────────────────────────
# Alles, was build.py an Daten braucht und was nicht aus MODULES/DAYS folgt.
# start       erster Tag der laufenden Planansicht (YYYY-MM-DD); alles davor ist Archiv
# countdown   Ende der Vorbereitung, worauf "Tage Vorbereitung uebrig" zaehlt
# store       localStorage-Schluessel fuer die Haken. Anderer Wert = Fortschritt startet leer
# migrations  Liste; leer lassen, solange der Plan nicht neu geschnitten wird. Jeder Eintrag:
#             dict(key="kl-recut-1", value="1", days=[24, None], steps=False, tick=[])
#             loescht einmalig pro Browser alle Haken der Tagindizes von..bis (None = offen)
#             und setzt optional "Tagindex_Position"-Haken (tick). Siehe GUIDE.md.
PLAN = dict(
  start="2026-08-28",
  countdown="2026-09-01",
  store="kl-demo",
  migrations=[],
)

# ───────────────────────────── Tagesplan ─────────────────────────────
# (Datum, [ (Modul, Minuten, Typ, Text, Anker?, Schritte?, Merksaetze?), ... ], Tagestyp)
# Aufgabentyp: L lesen · U ueben · D aus dem Kopf · T Test/kalt · W Wiederholung · O Orga
#              V Kuer — ausdruecklich optional, faellt als erstes weg (steht unter der Feierabend-Linie)
# Tagestyp:    "" normal · "deadline" · "klausur"
# Schritte:    [{"t": Titel, "d": Beschreibung, "to": Anker, "min": Minuten}, ...]
# Hinweis:     die laufende Planansicht beginnt an PLAN['start'] (siehe oben).
DAYS = [
 ("2026-08-26", [("KAF",50,"L","<b>KAF.html Orientierung und G1–G2</b> lesen.","orient"),("GAR",25,"L","<b>GAR Orientierung</b> überfliegen.","orient")], ""),
 ("2026-08-27", [("KAF",50,"L","<b>G3–G5</b> lesen, zu jedem Begriff zwei Sätze notieren.","g3"),("RAD",50,"L","<b>Antrieb</b> lesen.","antrieb")], ""),
 ("2026-08-28", [("KAF",50,"U","<b>Zustandsautomat aus dem Kopf</b> zeichnen, dann vergleichen.","zustand",
   [{"t": "Automat aus dem Kopf", "d": "Zustände, Übergänge, Bedingungen — ohne Vorlage.", "to": "zustand", "min": 25},
    {"t": "Vergleichen", "d": "Mit dem Dokument abgleichen, Abweichungen ins Fehler-Log.", "to": "zustand", "min": 15},
    {"t": "Verfahren V1 nachlesen", "d": "Nur die Stelle, an der es gehakt hat.", "to": "v1", "min": 10}],
   ["<b>Jeder Übergang braucht eine Bedingung.</b> Ein Pfeil ohne Beschriftung ist null Punkte.",
    "<b>Startzustand markieren</b>, bevor der erste Pfeil gezogen wird."]),
  ("RAD",50,"L","<b>Bremsen</b> lesen.","bremsen"),("GAR",25,"V","<b>Licht</b> — Kür.","licht")], ""),
 ("2026-08-29", [("KAF",50,"U","<b>Übungen U1–U2</b> mit verdeckter Lösung.","u1"),("RAD",50,"U","<b>Trainer</b>: eine Runde Antrieb.","trainer"),("ORGA",25,"O","<b>DEADLINE:</b> fehlendes Material anfragen.")], "deadline"),
 ("2026-08-30", [("KAF",50,"U","<b>Übungen U3–U4</b>.","u3"),("KAF",50,"U","<b>Trainer</b>: Kapitel 1 und 2.","trainer"),("RAD",50,"U","<b>Reifen</b> lesen und üben.","reifen")], ""),
 ("2026-08-31", [("KAF",60,"T","<b>Probeklausur im Trainer, kalt.</b> Punktzahl notieren.","trainer"),("RAD",50,"U","<b>Praxis</b> einmal komplett.","praxis")], ""),
 ("2026-09-01", [("KAF",40,"W","<b>Nichts Neues.</b> Taktik und Fehler-Log durchgehen.","taktik"),("RAD",50,"U","<b>Trainer-Simulation</b> 1.","trainer")], ""),
 ("2026-09-02", [("KAF",40,"W","<b>Vormittag:</b> Automat einmal aus dem Kopf.","zustand"),("KAF",90,"T","<b>KLAUSUR KAF 10:00.</b>","taktik")], "klausur"),
 ("2026-09-03", [("RAD",50,"U","<b>Trainer-Simulation</b> 2.","trainer"),("GAR",50,"L","<b>Planung</b> lesen.","plan")], ""),
 ("2026-09-04", [("RAD",40,"W","<b>Nichts Neues.</b> Praxis-Checkliste.","praxis"),("RAD",90,"T","<b>KLAUSUR RAD 14:00.</b>","praxis")], "klausur"),
 ("2026-09-05", [("GAR",50,"U","<b>Übung</b> komplett.","uebung"),("GAR",25,"L","<b>Taktik</b>.","taktik")], ""),
 ("2026-09-06", [("GAR",50,"T","<b>Übung kalt, mit Uhr.</b>","uebung"),("GAR",25,"W","<b>Quellen</b> durchsehen.","quellen")], ""),
 ("2026-09-07", [("GAR",90,"T","<b>KLAUSUR GAR.</b>","taktik")], "klausur"),
]

# ───────────── Texte der Uebersicht (Titel, Plan-Einleitung, Strategie, Zeitfenster) ─────────────
# build.py setzt sie an den Platzhaltern <!--TXT:key--> ein.
TEXT = {
  'crit': r'''<div class="crit"><b>Demo.</b> Drei erfundene Module, drei Klausuren in sechs Tagen.
    Die Daten zeigen nur, wie das Cockpit aussieht, wenn es gefüllt ist.</div>''',
  'planintro': r'''<div class="key"><b>Objektive statt Stunden.</b> Jeder Punkt ist ein <b>überprüfbarer
    Zustand</b>, kein Zeitbudget.<br><br>
    Der Pfeil <b>&#8599;</b> an einer Aufgabe springt direkt an die Stelle im Lerndokument.</div>''',
  'strategie': r'''<h3>Warum diese Reihenfolge</h3>
    <table>
    <tr><th>Entscheidung</th><th>Begründung</th></tr>
    <tr><td><b>KAF zuerst</b></td><td>Früheste Klausur, altklausur-getrieben, also planbar.</td></tr>
    <tr><td><b>RAD parallel</b></td><td>Praxisteil — Fertigkeit verfällt langsamer als Faktenwissen.</td></tr>
    <tr><td><b>GAR zuletzt</b></td><td>Wahlpflicht und die meiste Zeit nach den anderen Klausuren.</td></tr>
    </table>
    <h3>Arbeitsregeln</h3>
    <div class="key"><b>Modus vor Material.</b> Kein Modul wird gelernt, bevor sein Modus feststeht.</div>
    <div class="key"><b>Der Fehler-Log ist das eigentliche Lernmittel.</b></div>''',
  'fenster': r'''<h3>Die kritischen Fenster</h3><table>
   <tr><th>Fenster</th><th>Tage</th><th>Was passiert</th></tr>
   <tr><td><b>26.08. &ndash; 01.09.</b></td><td>7</td><td>Vorbereitung</td></tr>
   <tr><td><b>02. &ndash; 07.09.</b></td><td>6</td><td>KAF, RAD, GAR</td></tr></table>''',
  'title': r'''disciplan — Demo''',
  'h1': r'''disciplan — Demo''',
  'brand': r'''disciplan''',
  'bsub': r'''Demo &middot; 3 Module''',
  'hubsub': r'''3 Demo-Klausuren in 6 Tagen''',
}

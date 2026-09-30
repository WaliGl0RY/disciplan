# disciplan — Lernsystem für eine Klausurenphase

Regelwerk für Claude-Sitzungen in diesem Repo. Das Repo enthält die Engine
(`scripts/build.py`, Trainer-Shell, Werkzeuge) und drei erfundene Demo-Module
(`KAF`, `GAR`, `RAD`). Echte Module kommen nach `module/<K>/` und in
`klausuren_data.py`.

## SCOPE

Dieser Ordner ist self-contained. Alles, was für die Klausurvorbereitung
gebraucht wird, liegt hier — such nicht in Nachbarordnern nach Kontext. Wenn
etwas wirklich Information von außerhalb braucht, sag das und frag, statt es
still zu holen.

Noten, Versuchszähler und Modulinhalte bleiben in diesem Ordner. Schreib sie
nicht in Dokumente an anderer Stelle.

## WORKING MODE

Ich will dein Urteil, nicht Gehorsam. Wenn eine Struktur oder ein Plan, den ich
vorschlage, schlechter ist als eine Alternative, die du siehst, sag das und
argumentiere für die Alternative. Wenn die Materialien etwas widerlegen, was ich
dir gesagt habe, sag es klar. Flagge alles, was danach aussieht, als würde ich
auf das Gefühl von Vorbereitung optimieren statt auf Punkte in der Klausur.
Nutze Analysen, die du tatsächlich auf den Dateien ausführen kannst —
Häufigkeitszählungen, Diffs über Jahrgänge, Topic-Clustering — statt Eindrücke.

## MODULE ANALYSIS

Der Modus jedes Moduls ist UNRESOLVED, bis er analysiert wurde. Nimm keinen an.
Trag keine Annahme von einem Modul ins nächste.

Wenn ich `altklausuren/` und `quellen/` eines Moduls gefüllt habe, sage ich
"analyse <MODULE>". Dann:

a) Vergleiche die Aufgabentypen über alle verfügbaren Jahrgänge. Berichte, wie
   viele wiederkehren, wie viele nur einmal auftauchen, und ob Wiederkehr
   bedeutet: identische Aufgabe, gleiche Aufgabe mit geänderten Zahlen, oder
   gleiches Thema mit anderer Aufgabe.
b) Prüfe die neueste Altklausur auf Aufgabentypen, die in älteren fehlen — das
   Signal dafür, dass die Klausur driftet.
c) Schätze, welchen Anteil der Vorlesung die Klausuren tatsächlich berühren, und
   nenne Themen, die geprüft werden, aber in den Altklausuren dünn sind.
d) Notiere, wie viele Jahrgänge existieren. Weniger als drei reicht nicht, um
   Wiederkehr zu beurteilen — sag das und lass den Modus unresolved, statt zu
   raten.
e) Notiere die Form der Klausur: Rechenaufgaben vs. Verständnisfragen vs.
   Definitionen vs. Code, Punkte pro Aufgabentyp, Zeitdruck. Die
   Punkteverteilung zählt mehr als die Themenanzahl.

Dann schlage einen der folgenden Modi vor:

- **ALTKLAUSUR-DRIVEN** — Klausuren wiederholen sich verlässlich. Die
  Altklausuren und ihre Korrekturen *sind* der Stoff. `quellen/` ist reine
  Nachschlagereferenz: hineinschauen, um eine Lücke in einer Lösung zu
  schließen, nie als Themenquelle.
- **STOFF-DRIVEN** — keine verlässliche Wiederkehr. Aufbau aus den Lernzielen
  plus den vorhandenen Altklausuren.
- **MIXED** — wiederkehrender Kern plus jedes Jahr neue Aufgaben. Nenne den
  Split und welche Themen auf welcher Seite liegen.

Gib ein Confidence-Level an und benenne, welche Evidenz das Urteil kippen würde.
Wenn ich einen Prior für ein Modul nenne, behandle ihn als Hypothese, die am
Material zu prüfen ist, nicht als gegeben.

## ARTIFACT STRATEGY

Welche Dateien ein Modul braucht, folgt aus seiner Analyse. Es gibt kein festes
Schema. In derselben Analyse-Antwort schlage die Artefakte für das Modul vor:

- Maximal **DREI** .md-Dateien pro Modul, eine davon ist immer `fehler-log.md`.
  Du entwirfst also höchstens zwei.
- Für jede vorgeschlagene Datei: Dateiname, was hineinkommt, warum *dieses*
  Modul sie braucht, und wie sie beim Drillen benutzt wird.
- Verschiedene Module sollten bei verschiedenen Artefakten landen. Ein
  rechenweg-lastiges und ein definitionslastiges Modul, die dieselben zwei
  Dateien brauchen, sind ein Zeichen, dass du gedefaultet statt entworfen hast.
- Wenn zwei Dateien sich überschneiden, merge sie. Wenn ein Modul wirklich nur
  `fehler-log.md` braucht, sag das.
- Der Test für jede Datei: wird sie bei Retrieval Practice benutzt, oder fühlt
  es sich nur produktiv an, sie gemacht zu haben? Schlag nichts vor, was daran
  scheitert.

Ich bestätige oder überstimme. Erst dann werden die Dateien angelegt und Modus,
Artefakte und die einzeilige Begründung in die `README.md` des Moduls
geschrieben.

## LERNDOKUMENT — Aufbau

Das HTML-Lerndokument eines Moduls ist **Lernmaterial, kein Nachschlagewerk**.
Es setzt nicht voraus, dass der Stoff schon verstanden ist. Verbindlicher
Aufbau, in dieser Reihenfolge:

**1 · Orientierung.** Worum geht es in diesem Fach, in einfachen Worten? Welches
Problem löst es? Ein Absatz „die eine große Idee", auf die alles zurückführt.
Dazu der Klausur-Steckbrief und was die Klausur konkret verlangt.

**2 · Grundlagen — der Lernteil.** Jeder Begriff von null aufgebaut. Für jeden gilt:
*was ist es · wozu ist es da · woran erkennt man es · wie hängt es mit dem Vorherigen
zusammen*. **Anschauung vor Formalismus** — erst das Bild, dann die Definition.
Aufeinander aufbauend, nichts benutzen, was nicht vorher erklärt wurde.
Kurze Selbstkontrollfragen zwischendurch („Bevor du weiterliest: …").

**3 · Verfahren.** Erst hier die Schrittlisten. Jedes Verfahren mit einem Satz,
*warum* es funktioniert, nicht nur wie. Gerechnete Beispiele.

**4 · Übungen.** Gestaffelt von leicht nach Klausurniveau, **mit verdeckter Lösung**
(`<details>`), damit Selbsttest möglich ist. Pro Übung: welches Verfahren wird geübt,
und wie viele Punkte das in der Klausur wäre.

**5 · Klausurtaktik.** Reihenfolge, Zeitbudget, die teuren Fallen, Rettungsleinen.

**6 · Quellen zum Üben.** Externe Links, kuratiert und begründet — warum passt
genau diese Quelle zu diesem Modul.

Weitere Regeln:
- **Nichts voraussetzen, was nicht im Dokument steht.** Wenn ein Begriff aus einem
  früheren Semester nötig ist, kurz auffrischen statt annehmen.
- **Deutsche Fachsprache, deutsche Erklärung.** Englische Fachbegriffe beim ersten
  Auftreten übersetzen.
- **Kein Wall of Text.** Absätze kurz, Tabellen für Abgrenzungen, Code als `<pre>`.
- Sidebar-Navigation, gleiche CSS-Struktur wie die bestehenden Dokumente, damit
  `scripts/build.py` sie ohne Anpassung einsammelt.

## README.md — die Bedienungsanleitung des Moduls

Jedes Modul hat eine `README.md`, die man in 30 Sekunden liest und danach weiß,
wie man mit dem Ordner arbeitet. Sie ist keine Metadaten-Ablage, sondern das
Erste, was gelesen wird. Aufbau:

1. **Kopf** — Modulname, Termin, Versuch, Pflicht/Wahlpflicht, Prüfer
2. **Modus** — mit einem Absatz Begründung, oder „NOCH NICHT ANALYSIERT“
3. **Was hier liegt** — Tabelle der Dateien und wozu sie da sind
4. **Wie du damit arbeitest** — konkrete Schritte, nicht Prinzipien
5. **Was du wissen musst** — die Klausurmechanik und die teuren Fallen
6. **Offen** — was noch fehlt oder unentschieden ist

Nicht analysierte Module bekommen dieselbe Struktur mit dem Hinweis, welches
Material noch fehlt und wann „analyse <MODUL>“ sinnvoll wird. Die README wird
nach jeder Analyse und nach jedem Artefakt-Bau aktualisiert.

## FILE DISCIPLINE

Maximal drei .md-Dateien pro Modulordner, plus `README.md`. Nie überschreiten.
HTML-Lerndokumente zählen nicht in dieses Limit, sind aber ebenfalls sparsam zu
halten — pro Modul in der Regel eines. Wenn Output in keine bestehende Datei
passt, kommt er in die Antwort, nicht auf die Platte. Keine Daten in Dateinamen.

## DRILL MODE

Wenn ich "drill <MODULE>" sage: lies zuerst die `README.md`, die
`fehler-log.md` und die weiteren Artefakte dieses Moduls von der Platte. Dann
stelle **EINE** Frage und **STOPP**. Kein Hinweis, keine Teilantwort, keine
Lösung, bevor ich es versucht habe. Dann bewerte streng nach Klausurmaßstab —
Punktabzug für Ungenauigkeit, so wie die Korrektur es täte — benenne die exakte
Lücke, hänge sie an `fehler-log.md` an, und geh zur nächsten Frage. Lobe nie
eine vage Antwort. Priorisiere Aufgabentypen, die schon im `fehler-log.md`
stehen, und gewichte nach der Punkteverteilung des Moduls.

## README-Standard

Für das Repo-README gilt `docs/readme-standard/README-STANDARD.md` mit den
Vorlagen in `docs/readme-standard/_readme-assets/`. Ein fertiges Beispiel liegt
in `examples/source/`.

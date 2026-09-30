#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
restyle.py — gibt allen Trainer-Apps dieselbe Oberflaeche.

Zwei Dinge passieren je Datei:
  1. Der Inhalt des <style>-Blocks wird durch assets/trainer/trainer-style.css ersetzt
     (Gestaltung aus dem Bewerbungs-Cockpit: Indigo, weiche Karten, Schatten).
  2. Die Aktionsleiste #nav wird aus der fest am Fensterboden klebenden Leiste
     in die Fragekarte geholt — solange die Frage offen ist direkt unter die
     Antworten, nach dem Aufloesen direkt hinter das Urteil.

Aufruf:  python3 scripts/restyle.py module/KAF/trainer/shell.html [weitere ...]
         python3 scripts/restyle.py --alle      (alle module/*/trainer/shell.html)

Danach das jeweilige trainer/build.py laufen lassen, sonst aendert sich an der
fertigen <K>-Trainer.html nichts. Mehrfaches Aufrufen ist ungefaehrlich.
"""
import io, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))   # Repo-Wurzel
ASSETS = os.path.join(ROOT, "assets", "trainer")
CSS = os.path.join(ASSETS, "trainer-style.css")
JS  = os.path.join(ASSETS, "trainer-kopf.js")
JS_BLATT = os.path.join(ASSETS, "trainer-blatt.js")
JS_RAIL  = os.path.join(ASSETS, "trainer-rail.js")
KOPFFUNKTION = io.open(JS, encoding="utf-8").read()
ADDON = ("/*__ADDON_START__*/\n" + io.open(JS_BLATT, encoding="utf-8").read()
         + io.open(JS_RAIL, encoding="utf-8").read() + "/*__ADDON_END__*/\n")

# Je Modul eine eigene Akzentfarbe, damit sich die Trainer unterscheiden.
# Nicht eingetragene Kuerzel behalten die Grundfassung (Indigo).
PALETTEN = {
  "rad": dict(acc="#0e8f86", acc2="#0a6f68", accw="#e0f3f1",
              dacc="#5cc9bd", daccw="#12332f",
              g1="linear-gradient(135deg,#0f9b8e,#46bfa6)",
              g2="linear-gradient(135deg,#2aa39a,#6fd0c0)"),
  "kaf": dict(acc="#7C5CD6", acc2="#5a3fb8", accw="#efe9fb",
              dacc="#a48bf0", daccw="#231c40",
              g1="linear-gradient(135deg,#6d4cc9,#9d83ea)",
              g2="linear-gradient(135deg,#7c5cd6,#b19af0)"),
}

def palette(kuerzel):
    p = PALETTEN.get(kuerzel)
    if not p:
        return ""
    return ("""

/* ---- Akzentfarbe dieses Moduls ---- */
:root{--acc:%(acc)s;--acc2:%(acc2)s;--acc-w:%(accw)s;
  --g-violet:%(g1)s;--g-blue:%(g2)s}
@media (prefers-color-scheme:dark){:root:not([data-t="light"]){
  --acc:%(dacc)s;--acc2:%(dacc)s;--acc-w:%(daccw)s}}
""" % p)

RETTEN = (
    "  /* Die Aktionsleiste haengt in der alten Karte — vor dem Leeren retten. */\n"
    "  const NAVEL=$('#nav'); if(NAVEL&&NAVEL.parentNode!==document.body) document.body.appendChild(NAVEL);\n"
)
EINHAENGEN = (
    "  /* Aktionsleiste sitzt IN der Karte: solange offen direkt unter den Antworten,\n"
    "     nach dem Aufloesen direkt hinter dem Urteil. Nie am Seitenende. */\n"
    "  if(offen && NAVEL) card.appendChild(NAVEL);\n\n"
)


G_RE = re.compile(r"  const g=setId=>\{const s=setById\(setId\);.*?\};", re.S)

G_NEU = """  /* Fortschrittsbalken statt drei Zahlen-Pillen — man sieht die Kachel volllaufen. */
  const g=setId=>{const s=setById(setId), t=stat(s), n=s.fragen.length,
    pct=n?Math.round(100*t.ok/n):0;
    return `<span class="mtr"><i style="width:${pct}%"></i></span>`+
           `<span class="mtl"><b>${t.ok}</b> von ${n} sicher`+
           (t.no?` \u00b7 <span class="mo">${t.no} offen</span>`:'')+
           `<span class="mpc${pct===100?' voll':''}">${pct}\u2009%</span></span>`};"""

KOPF_ANKER = "  const h=$('#home'); h.innerHTML='';"
KOPF_RUF   = "\n  h.appendChild(cockpitKopf());"
TAG_ANKER  = "  S.vers=S.vers||{}; S.vers[S.i]=(S.vers[S.i]||0)+1;"
TAG_ZAEHL  = ("\n  /* Tageszaehler fuer den Kopf der Startseite. */\n"
              "  ST.tage=ST.tage||{}; const hk=heuteKey(); ST.tage[hk]=(ST.tage[hk]||0)+1;")


def klassen(css):
    """Alle Klassennamen, die im Stylesheet eine Regel bekommen."""
    css = re.sub(r"/\*.*?\*/", "", css, flags=re.S)
    return set(re.findall(r"\.([A-Za-z][\w-]*)", css))


def eine(pfad, css):
    h = io.open(pfad, encoding="utf-8").read()
    warn = []
    m = re.search(r"const KEY='([a-z0-9]+)-trainer", h)
    kuerzel = m.group(1) if m else ""
    css = css + palette(kuerzel)

    # ── 1. Stylesheet austauschen ──────────────────────────────
    a, b = h.index("<style>") + len("<style>"), h.index("</style>")
    fehlt = sorted(klassen(h[a:b]) - klassen(css))
    if fehlt:
        warn.append("Klassen ohne neue Regel: " + ", ".join("." + k for k in fehlt))
    h = h[:a] + "\n" + css.strip() + "\n" + h[b:]

    # ── 2. Aktionsleiste in die Karte ──────────────────────────
    if "NAVEL" not in h:
        anker = "  const r=$('#run'); r.innerHTML='';"
        if h.count(anker) == 1:
            h = h.replace(anker, RETTEN + anker, 1)
        else:
            warn.append("Ankerstelle fuer das Retten der Leiste nicht gefunden")

        for anker in ("  /* --- Auflösung --- */\n  if(!offen){",
                      "  /* --- Aufloesung --- */\n  if(!offen){"):
            if h.count(anker) == 1:
                h = h.replace(anker, EINHAENGEN + anker, 1)
                break
        else:
            warn.append("Ankerstelle fuer die Aufloesung nicht gefunden")

        anker = "    res.appendChild(v);\n"
        if h.count(anker) == 1:
            h = h.replace(anker, anker + "    if(NAVEL) res.appendChild(NAVEL);\n", 1)
        else:
            warn.append("Ankerstelle hinter dem Urteil nicht gefunden")

    # ── 3. Kachel-Fortschritt statt Zahlenpillen ───────────────
    if "Fortschrittsbalken statt drei" not in h:
        treffer = G_RE.findall(h)
        if len(treffer) == 1:
            h = h.replace(treffer[0], G_NEU, 1)
        else:
            warn.append("Kachel-Auszeichnung g() nicht eindeutig (%d Treffer)" % len(treffer))

    # ── 4. Cockpit-Kopf auf der Startseite ─────────────────────
    if "cockpitKopf" not in h:
        h = h.replace("function home(){", KOPFFUNKTION + "function home(){", 1)
        if h.count(KOPF_ANKER) == 1:
            h = h.replace(KOPF_ANKER, KOPF_ANKER + KOPF_RUF, 1)
        else:
            warn.append("Startseiten-Anker nicht gefunden")
        if h.count(TAG_ANKER) == 1:
            h = h.replace(TAG_ANKER, TAG_ANKER + TAG_ZAEHL, 1)
        else:
            warn.append("Anker fuer den Tageszaehler nicht gefunden")

    # ── 5. Blattmodus und Seitenleiste ─────────────────────────
    j = h.find("\nfunction home(){")
    if j < 0:
        warn.append("home() nicht gefunden — Blatt und Leiste nicht gesetzt")
    else:
        a = h.find("/*__ADDON_START__*/")
        if a < 0:
            a = h.find("\n/* ══════════ Blattmodus ══════════")   # alte, unmarkierte Fassung
            a = a if 0 <= a < j else j
        b = h.find("/*__ADDON_END__*/")
        b = (b + len("/*__ADDON_END__*/\n")) if b >= 0 else j
        h = h[:a] + "\n" + ADDON + h[b:]

    # alte, direkt in der Shell stehende Leisten-Logik entfernen —
    # sie steht jetzt in trainer-rail.js und wuerde sonst doppelt deklariert
    h = h.replace("""/* Leiste: breit = ein-/ausklappen und merken, schmal = \u00fcber den Inhalt legen */
const breit=()=>matchMedia('(min-width:1100px)').matches;
try{ if(localStorage.getItem(KEY+'-railzu')==='1') document.body.classList.add('railzu') }catch(e){}
function railUm(){
  if(breit()){ const zu=document.body.classList.toggle('railzu');
    try{ localStorage.setItem(KEY+'-railzu', zu?'1':'0') }catch(e){} }
  else document.body.classList.toggle('railauf');
}
""", "try{ if(localStorage.getItem(KEY+'-railzu')==='1') document.body.classList.add('railzu') }catch(e){}\n")

    # ── 6. Markup der Seitenleiste ─────────────────────────────
    if 'id="rail"' not in h:
        h = h.replace("<body>\n<header>",
            '<body>\n<aside id="rail"><div id="railin"></div></aside>\n'
            '<div id="railbg"></div>\n<header>', 1)
        h = re.sub(r'(  <h1>)', '  <button class="btn sm" id="railtog" title="Menü">\u2630</button>\n\\1', h, count=1)
        h = h.replace("$('#spickbtn').onclick=spickAuf;",
            "document.querySelector('#railtog').onclick=railUm;\n"
            "document.querySelector('#railbg').onclick=()=>document.body.classList.remove('railauf');\n"
            "try{ if(localStorage.getItem(KEY+'-railzu')==='1') document.body.classList.add('railzu') }catch(e){}\n"
            "$('#spickbtn').onclick=spickAuf;", 1)
    if "railBauen();" not in h.split("function home(){")[1][:400]:
        h = h.replace(KOPF_ANKER, KOPF_ANKER + " railBauen();", 1)
    # ── 7. Antworten auch im Einzelmodus mischen ───────────────
    anker = "if(!S.cur[S.i]) S.cur[S.i]=build(q0);"
    if anker in h:
        h = h.replace(anker, "if(!S.cur[S.i]) S.cur[S.i]=mische(build(q0));", 1)
    elif "mische(build(q0))" not in h:
        warn.append("Ankerstelle fuers Mischen im Einzelmodus nicht gefunden")

    # Kapitelklick oeffnet als Blatt
    h = h.replace("b.onclick=()=>start(s.id,false); gq.appendChild(b)});",
                  "b.onclick=()=>blattSet(s.id); gq.appendChild(b)});")
    h = h.replace("b.onclick=()=>start(s.id,false); gk.appendChild(b)});",
                  "b.onclick=()=>blattSet(s.id); gk.appendChild(b)});")

    io.open(pfad, "w", encoding="utf-8").write(h)
    print(("  neu gestaltet: " if not warn else "  TEILWEISE: ") + pfad)
    for w in warn:
        print("      ! " + w)
    return not warn


def main():
    args = sys.argv[1:]
    if not args:
        sys.exit(__doc__)
    if args[0] == "--alle":
        mod = os.path.join(ROOT, "module")
        args = [os.path.join(mod, k, "trainer", "shell.html") for k in sorted(os.listdir(mod))
                if os.path.exists(os.path.join(mod, k, "trainer", "shell.html"))]
    css = io.open(CSS, encoding="utf-8").read()
    ok = all([eine(p, css) for p in args])
    print("fertig — jetzt die betroffenen trainer/build.py laufen lassen")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
theme.py — haengt jeder HTML-Datei einen Umschalter fuer die Darstellung an.

Der Dunkelmodus dieser Dateien steckt in einer Media Query
(prefers-color-scheme: dark) und folgt damit dem Betriebssystem. Dieser
Schalter macht daraus drei Zustaende: Auto, Hell, Dunkel.

Umgesetzt wird das NICHT durch Umschreiben des CSS, sondern zur Laufzeit:
das Skript sucht die Dark-Media-Regeln im CSSOM und setzt ihre Bedingung auf
"all" (immer dunkel) bzw. "not all" (nie dunkel) — Auto stellt das Original
wieder her. Damit bleibt das CSS unveraendert, und build.py, das die
Media Query beim Bauen von klausuren.html auf html[data-t=dark] umschreibt,
sieht weiterhin genau das, was es erwartet.

Die Wahl liegt unter dem Schluessel "kl-theme" im localStorage — demselben,
den klausuren.html schon benutzt. Alle Seiten des Ordners teilen sich diesen
Speicher, die Einstellung gilt also ueberall.

Aufruf:  python3 theme.py datei.html [datei.html ...]
         python3 theme.py --alle        (module/*/*.html; index.html ist seit 27.09.2026 archiviert)

Mehrfaches Aufrufen ist ungefaehrlich: ein vorhandener Block wird ersetzt.
klausuren.html wird uebersprungen — die Datei wird von build.py erzeugt und
hat oben rechts bereits einen eigenen Umschalter.
"""
import io, os, re, sys

MARKE_A = "<!-- ══ Darstellung: Auto / Hell / Dunkel ══ -->"
MARKE_E = "<!-- ══ Ende Darstellung ══ -->"

BLOCK = MARKE_A + """
<script>
/* Umschalter fuer die Darstellung. Setzt html[data-t] und biegt die
   Dark-Media-Regeln um. Laeuft nicht in klausuren.html — die Datei bringt
   ihren eigenen Schalter mit und traegt data-t schon im html-Tag. */
(function(){
  if(window.__klTheme) return;
  if(document.documentElement.hasAttribute("data-t")) return;
  window.__klTheme = 1;

  var KEY = "kl-theme", stand = "auto";
  try{ var v = localStorage.getItem(KEY); if(v === "dark" || v === "light") stand = v; }catch(e){}
  var mq = window.matchMedia("(prefers-color-scheme: dark)");
  var regeln = null, orig = [];

  function sammeln(){
    regeln = []; orig = [];
    for(var i = 0; i < document.styleSheets.length; i++){
      var rs;
      try{ rs = document.styleSheets[i].cssRules; }catch(e){ continue }
      if(!rs) continue;
      for(var j = 0; j < rs.length; j++){
        var r = rs[j];
        if(!r || !r.media) continue;
        var t = r.media.mediaText || "";
        if(/prefers-color-scheme/i.test(t) && /dark/i.test(t)){ regeln.push(r); orig.push(t); }
      }
    }
  }

  function anwenden(){
    if(regeln === null) sammeln();
    var wirkt = stand === "auto" ? (mq.matches ? "dark" : "light") : stand;
    document.documentElement.setAttribute("data-t", wirkt);
    for(var i = 0; i < regeln.length; i++){
      try{
        regeln[i].media.mediaText =
          stand === "dark" ? "all" : stand === "light" ? "not all" : orig[i];
      }catch(e){}
    }
    var b = document.querySelector("#klTheme");
    if(b){
      b.textContent = stand === "auto" ? "Auto" : stand === "light" ? "Hell" : "Dunkel";
      b.title = "Darstellung: " + b.textContent + " (klicken wechselt Auto, Hell, Dunkel)";
    }
  }

  function weiter(){
    stand = stand === "auto" ? "light" : stand === "light" ? "dark" : "auto";
    try{ stand === "auto" ? localStorage.removeItem(KEY) : localStorage.setItem(KEY, stand); }catch(e){}
    anwenden();
  }

  function knopf(){
    var b = document.createElement("button");
    b.id = "klTheme"; b.type = "button";
    var kopf = document.querySelector("header .hd");
    if(kopf){
      /* Trainer-App: in die Kopfzeile, im Stil der übrigen Knöpfe */
      b.className = "btn sm";
      var vor = kopf.querySelector("#enbtn") || kopf.querySelector("#quit");
      vor ? kopf.insertBefore(b, vor) : kopf.appendChild(b);
    } else {
      /* Lerndokumente und Übersicht: klein oben rechts, druckt nicht mit */
      b.setAttribute("style",
        "position:fixed;top:10px;right:14px;z-index:9999;" +
        "font:600 11.5px/1 system-ui,sans-serif;letter-spacing:.03em;" +
        "padding:6px 11px;border-radius:999px;cursor:pointer;" +
        "border:1px solid rgba(128,128,128,.45);background:rgba(128,128,128,.14);" +
        "color:inherit;opacity:.5;transition:opacity .15s");
      b.onmouseenter = function(){ b.style.opacity = "1" };
      b.onmouseleave = function(){ b.style.opacity = ".5" };
      var s = document.createElement("style");
      s.textContent = "@media print{#klTheme{display:none}}";
      (document.head || document.documentElement).appendChild(s);
      (document.body || document.documentElement).appendChild(b);
    }
    b.onclick = weiter;
    anwenden();
  }

  anwenden();
  if(document.readyState === "loading") document.addEventListener("DOMContentLoaded", knopf);
  else knopf();
  if(mq.addEventListener) mq.addEventListener("change", function(){ if(stand === "auto") anwenden() });
})();
</script>
""" + MARKE_E


def eine(pfad):
    name = os.path.basename(pfad)
    if name == "klausuren.html":
        print("  uebersprungen (eigener Schalter): " + pfad)
        return False
    h = io.open(pfad, encoding="utf-8").read()
    # vorhandenen Block entfernen, damit mehrfaches Aufrufen nichts stapelt
    h = re.sub(re.escape(MARKE_A) + r".*?" + re.escape(MARKE_E), "", h, flags=re.S).rstrip()
    if "prefers-color-scheme" not in h:
        print("  kein Dunkelmodus, nichts zu tun: " + pfad)
        return False
    if "</body>" in h:
        h = h.replace("</body>", BLOCK + "\n</body>", 1)
    else:
        h = h + "\n" + BLOCK + "\n"
    io.open(pfad, "w", encoding="utf-8").write(h)
    print("  Schalter gesetzt: " + pfad)
    return True


def main():
    args = sys.argv[1:]
    if not args:
        sys.exit(__doc__)
    if args[0] == "--alle":
        root = os.path.dirname(os.path.abspath(__file__))
        args = []
        mod = os.path.join(root, "module")
        for k in sorted(os.listdir(mod)):
            d = os.path.join(mod, k)
            if not os.path.isdir(d):
                continue
            for f in sorted(os.listdir(d)):
                if f.endswith(".html"):
                    args.append(os.path.join(d, f))
    n = 0
    for p in args:
        if eine(p):
            n += 1
    print("fertig — %d Datei(en) geaendert" % n)


if __name__ == "__main__":
    main()

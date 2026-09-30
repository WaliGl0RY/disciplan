/* gen2.js — Demo-Generatoren (erfunden, neutrales Thema). build.py haengt sie an GEN an.
   Jeder Generator liefert frische Zahlen, eine gerechnete Loesung und unter "variiert"
   die typischen Fehlerquellen. Bewusst kleine, runde Zahlen. */
{

/* ── Brührezept: Kaffeemenge aus Wassermenge und Verhältnis ── */
bruehrezept(){
  const r = pick([14, 15, 16, 17]);
  const tassen = pick([2, 3, 4, 5, 6]);
  const g = pick([8, 10, 12]);                 /* Gramm Kaffee pro Tasse */
  const wasser = g * r * tassen;
  const kaffee = g * tassen;
  return {
    frage: `Du brühst <b>${tassen} Tassen</b> mit insgesamt <b>${wasser} ml</b> Wasser im Verhältnis <b>1 : ${r}</b>. `+
           `Wie viel Kaffee brauchst du insgesamt, und wie viel ist das pro Tasse?`,
    hinweis: 'Ganze Gramm genügen.',
    felder: [{k:'k', label:'Kaffee gesamt (g) ='}, {k:'t', label:'pro Tasse (g) ='}],
    loesung: {k: String(kaffee), t: String(g)},
    pruef: {k:'numround', t:'numround'},
    erklaerung: `<code>${wasser} / ${r} = ${kaffee} g</code> Kaffee; auf ${tassen} Tassen verteilt: <code>${kaffee} / ${tassen} = ${g} g</code>.`,
    variiert: `<b>Die zwei Fehlerquellen:</b> <b>1 ·</b> das Verhältnis falsch herum lesen (mit ${r} multiplizieren statt teilen). `+
              `<b>2 ·</b> pro Tasse vor dem Teilen rechnen und dabei runden — erst gesamt, dann verteilen.`
  };
},

/* ── Temperatur: °C in °F und Kelvin ── */
temperatur(){
  const c = pick([88, 90, 92, 93, 94, 95, 96]);
  const f = c * 9 / 5 + 32;
  const k = c + 273;
  return {
    frage: `Das Rezept verlangt Brühwasser mit <b>${c} °C</b>. Deine Kanne zeigt nur °F an, das Thermometer im Labor nur Kelvin. `+
           `Rechne um (Kelvin gerundet mit +273).`,
    felder: [{k:'f', label:'°F ='}, {k:'k', label:'K ='}],
    loesung: {f: String(Math.round(f * 10) / 10), k: String(k)},
    pruef: {f:'numround', k:'num'},
    erklaerung: `<code>${c} · 9/5 + 32 = ${Math.round(f * 10) / 10} °F</code> und <code>${c} + 273 = ${k} K</code>.`,
    variiert: `<b>Die Falle:</b> erst +32 und dann · 9/5 rechnen ergibt einen ganz anderen Wert. Die Reihenfolge ist: erst skalieren, dann verschieben.`
  };
}

}

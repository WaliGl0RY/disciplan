/* Demo-Daten (erfunden) — Kapitel 2: Brühen und Rezepte */
{
id:'k2', nr:2, name:'Brühen und Rezepte', fragen:[

{id:'k2-1',nr:1,typ:'num',titel:'Rezept für eine Kanne',
 frage:'Du brühst <b>750 ml</b> Filterkaffee im Verhältnis <b>1 : 15</b>. Wie viel Kaffee brauchst du, und wie viel ist das pro Tasse (5 Tassen)?',
 hinweis:'Ganze Gramm genügen.',
 felder:[{k:'g',label:'Kaffee gesamt (g) ='},{k:'t',label:'pro Tasse (g) ='}],
 loesung:{g:'50',t:'10'},
 pruef:{g:'numround',t:'numround'},
 erklaerung:'<code>750 / 15 = 50 g</code>, verteilt auf 5 Tassen: <code>50 / 5 = 10 g</code>.',
 variiert:'<b>Die zwei Fehlerquellen:</b> mit 16 statt 15 teilen (dann 47 g) und das Verhältnis falsch herum lesen (Wasser : Kaffee).',
 quelle:'kap2', anker:'g4'},

{id:'k2-2',nr:2,typ:'gen',gen:'bruehrezept',titel:'Rezept mit neuen Zahlen',
 quelle:'kap2', anker:'v1'},

{id:'k2-3',nr:3,typ:'gen',gen:'temperatur',titel:'Brühtemperatur umrechnen',
 quelle:'kap2', anker:'g5'},

{id:'k2-4',nr:4,typ:'text',titel:'Fehlersuche erklären',
 frage:'Dein Espresso läuft in <b>12 Sekunden</b> durch. Beschreibe in zwei bis drei Sätzen, was passiert ist und was du änderst.',
 hinweis:'Freitext — danach selbst bewerten.',
 muster:'Der Bezug ist <b>zu schnell</b>: das Wasser findet zu wenig Widerstand, der Espresso ist unterextrahiert und sauer. Ich mahle <b>feiner</b> (oder erhöhe die Dosis leicht) und prüfe, ob der Bezug danach bei etwa 25–30 Sekunden liegt.',
 erklaerung:'Es kommt auf drei Dinge an: <b>Diagnose</b> (zu schnell), <b>Folge</b> (unterextrahiert) und <b>eine</b> konkrete Stellschraube.',
 variiert:'Wer drei Stellschrauben gleichzeitig dreht, weiß danach nicht, welche geholfen hat — immer nur eine ändern.',
 quelle:'kap2', anker:'v2'},

{id:'k2-5',nr:5,typ:'single',titel:'Wasserhärte',
 frage:'Warum wird für Espressomaschinen oft <b>gefiltertes Wasser</b> empfohlen?',
 hinweis:'Wählen Sie eine Antwort.',
 optionen:['Weil Kalk die Maschine zusetzt','Weil weiches Wasser mehr Koffein löst','Weil Filterwasser heißer wird','Weil es die Crema dunkler macht'],
 richtig:[0],
 erklaerung:'Hartes Wasser lagert <b>Kalk</b> in Kessel und Leitungen ab. Deshalb gibt es auch das Entkalkungsprogramm (siehe Zustandsdiagramm).',
 variiert:'<b>Zu weiches Wasser</b> ist aber auch nicht ideal: ganz ohne Mineralien schmeckt der Kaffee flach.',
 quelle:'kap2', anker:'zustand'}
]}

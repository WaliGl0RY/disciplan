/* Demo-Daten (erfunden) — Probeklausur des Demo-Moduls */
{
id:'pk', nr:1, klausur:true, name:'Probeklausur · Demo', datum:'8 Aufgaben · alle Formate', fragen:[

{id:'pk-1',nr:1,typ:'single',titel:'Verhältnis lesen',
 frage:'Was bedeutet das Brühverhältnis <b>1 : 16</b>?',
 hinweis:'Wählen Sie eine Antwort.',
 optionen:['1 g Kaffee auf 16 g Wasser','16 g Kaffee auf 1 l Wasser','1 Löffel auf 16 Tassen','16 Sekunden pro Gramm'],
 richtig:[0],
 erklaerung:'Das Verhältnis ist immer <b>Kaffee : Wasser</b> in Gramm (1 ml Wasser ≈ 1 g).',
 variiert:'Bei Espresso wird meist umgekehrt vom Ergebnis her gedacht: 18 g rein, 36 g raus = 1 : 2.',
 quelle:'klausur', anker:'g4'},

{id:'pk-2',nr:2,typ:'multi',titel:'Überextraktion erkennen',
 frage:'Woran erkennst du einen <b>überextrahierten</b> Kaffee?',
 hinweis:'Wählen Sie alle zutreffenden Antworten (2).',
 optionen:['Bitter und trocken im Abgang','Sehr lange Durchlaufzeit','Wässrig und sauer','Sehr helle Crema, die sofort zerfällt'],
 richtig:[0,1],
 erklaerung:'<b>Bitter + langsam</b> = zu viel gelöst. Sauer, wässrig und helle, dünne Crema sprechen für das Gegenteil.',
 variiert:'Paare lernen: <b>sauer ↔ zu wenig</b>, <b>bitter ↔ zu viel</b>.',
 quelle:'klausur', anker:'g5'},

{id:'pk-3',nr:3,typ:'match',titel:'Stellschraube und Wirkung',
 frage:'Ordnen Sie jeder Änderung ihre Hauptwirkung zu.',
 hinweis:'Tragen Sie die Nummer aus der Liste ein.',
 zuordnung:['mehr Extraktion','weniger Extraktion','stärker, aber nicht mehr extrahiert'],
 items:['Feiner mahlen','Gröber mahlen','Mehr Kaffee, gleiches Wasser'],
 richtig:[1,2,3],
 erklaerung:'Mahlgrad steuert die <b>Extraktion</b>; die Dosis steuert vor allem die <b>Stärke</b>.',
 variiert:'Stärke und Extraktion sind zwei verschiedene Achsen — genau das trennt ein gutes Rezept von Raten.',
 quelle:'klausur', anker:'g5'},

{id:'pk-4',nr:4,typ:'gap',titel:'Espresso-Parameter',
 frage:'Füllen Sie die Lücken.',
 text:'Ein klassischer Espresso nutzt etwa [0] Kaffee, läuft etwa [1] und wird mit rund [2] Druck gebrüht.',
 luecken:[{o:['18 g','5 g','40 g'],a:0},{o:['25–30 s','5 s','3 min'],a:0},{o:['9 bar','1 bar','30 bar'],a:0}],
 erklaerung:'Richtwerte: <b>18 g</b>, <b>25–30 s</b>, <b>9 bar</b>.',
 variiert:'Richtwerte sind ein Startpunkt. Geschmack entscheidet, die Zahlen helfen beim Wiederholen.',
 quelle:'klausur', anker:'g4'},

{id:'pk-5',nr:5,typ:'num',titel:'Espresso-Verhältnis',
 frage:'Du nimmst <b>18 g</b> Kaffee und willst ein Verhältnis von <b>1 : 2,5</b>. Wie viel Espresso (g) soll in der Tasse landen?',
 felder:[{k:'e',label:'Espresso (g) ='}],
 loesung:{e:'45'},
 pruef:{e:'numround'},
 erklaerung:'<code>18 · 2,5 = 45 g</code>.',
 variiert:'Beim Espresso wird das Getränk gewogen, nicht das Wasser — der Kaffee hält einen Teil zurück.',
 quelle:'klausur', anker:'v1'},

{id:'pk-6',nr:6,typ:'order',titel:'Handfilter in Schritten',
 frage:'Bringen Sie die Schritte in die richtige Reihenfolge.',
 hinweis:'Tragen Sie 1 bis 4 ein.',
 items:['In Etappen aufgießen','Filter ausspülen','Kaffee vorbrühen (Bloom)','Kaffee einfüllen'],
 richtig:[4,1,3,2],
 erklaerung:'Filter spülen → Kaffee einfüllen → vorbrühen → in Etappen aufgießen.',
 variiert:'Das Vorbrühen lässt CO₂ entweichen. Ohne diesen Schritt fließt das Wasser ungleichmäßig.',
 quelle:'klausur', anker:'v1'},

{id:'pk-7',nr:7,typ:'gen',gen:'bruehrezept',titel:'Rezept rechnen (neue Zahlen)',
 quelle:'klausur', anker:'v1'},

{id:'pk-8',nr:8,typ:'text',titel:'Kurz begründen',
 frage:'Warum sollte man Kaffee erst direkt vor dem Brühen mahlen?',
 muster:'Beim Mahlen wächst die Oberfläche stark. Aromastoffe verfliegen und oxidieren dann innerhalb von Minuten, ganze Bohnen halten dagegen wochenlang.',
 erklaerung:'Das Stichwort ist die <b>Oberfläche</b>: Mahlen vervielfacht sie.',
 variiert:'Dasselbe Argument erklärt, warum gemahlener Kaffee luftdicht gelagert werden sollte.',
 quelle:'klausur', anker:'g3'}
]}

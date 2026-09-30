/* Demo-Daten (erfunden) — Kapitel 1: Bohne, Röstung, Mahlgrad */
{
id:'k1', nr:1, name:'Bohne, Röstung, Mahlgrad', fragen:[

{id:'k1-1',nr:1,typ:'single',titel:'Mahlgrad und Brühzeit',
 frage:'Ein Filterkaffee läuft in <b>90 Sekunden</b> durch und schmeckt dünn und sauer. Was änderst du zuerst?',
 hinweis:'Wählen Sie eine Antwort.',
 optionen:['Feiner mahlen','Gröber mahlen','Mehr Wasser nehmen','Kälteres Wasser nehmen'],
 richtig:[0],
 optionNotiz:{1:'Gröber mahlen beschleunigt den Durchlauf noch weiter.',2:'Mehr Wasser verdünnt, es verlängert die Kontaktzeit kaum.',3:'Kälteres Wasser löst noch weniger.'},
 erklaerung:'<b>Zu schnell + sauer = unterextrahiert.</b> Feiner mahlen vergrößert die Oberfläche und bremst den Durchlauf, beides erhöht die Extraktion.',
 variiert:'<b>Umgedreht:</b> läuft er nach 6 Minuten noch und schmeckt bitter, ist er überextrahiert → gröber mahlen.<br><b>Die Prüffrage:</b> erst die Zeit ansehen, dann den Geschmack.',
 quelle:'kap1', anker:'g3'},

{id:'k1-2',nr:2,typ:'multi',titel:'Was die Röstung verändert',
 frage:'Welche Aussagen über eine <b>dunklere Röstung</b> stimmen?',
 hinweis:'Wählen Sie alle zutreffenden Antworten (3).',
 optionen:['Mehr Röstaromen und Bitterstoffe','Weniger wahrnehmbare Säure','Die Bohne wird poröser und löst sich schneller','Deutlich mehr Koffein pro Bohne'],
 richtig:[0,1,2],
 optionNotiz:{3:'Der Koffeingehalt ändert sich durch die Röstung nur wenig.'},
 erklaerung:'Dunkle Röstungen bringen <b>Röstaromen</b>, verdecken <b>Säure</b> und sind <b>poröser</b> — sie extrahieren also schneller.',
 variiert:'<b>Merksatz:</b> hell = Frucht und Säure, dunkel = Körper und Bitterkeit. Beim Koffein ist die Sorte wichtiger als die Röstung.',
 quelle:'kap1', anker:'g2'},

{id:'k1-3',nr:3,typ:'match',titel:'Zubereitung und Mahlgrad',
 frage:'Ordnen Sie jeder Zubereitung den passenden Mahlgrad zu.',
 hinweis:'Tragen Sie die Nummer aus der Liste ein.',
 zuordnung:['fein wie Mehl','fein wie Salz','mittel wie Sand','grob wie Meersalz'],
 items:['Espresso','Mokkakanne','Handfilter','French Press'],
 richtig:[1,2,3,4],
 erklaerung:'Je <b>kürzer</b> der Kontakt zwischen Wasser und Kaffee, desto <b>feiner</b> das Mehl.',
 variiert:'<b>Die Regel dahinter:</b> Kontaktzeit und Mahlgrad gleichen sich aus. Die French Press zieht vier Minuten, also grob; Espresso nur 25 Sekunden, also fein.',
 quelle:'kap1', anker:'g3'},

{id:'k1-4',nr:4,typ:'gap',titel:'Lückentext Röstung',
 frage:'Füllen Sie die Lücken.',
 text:'Beim Rösten hört man zuerst den [0]. Eine helle Röstung endet kurz danach und schmeckt eher [1]; eine dunkle Röstung schmeckt eher [2].',
 luecken:[{o:['First Crack','Second Crack','Cooling'],a:0},{o:['fruchtig','rauchig','salzig'],a:0},{o:['bitter','sauer','süß'],a:0}],
 erklaerung:'Der <b>First Crack</b> ist das hörbare Aufplatzen der Bohne. Kurz danach endet eine helle Röstung (fruchtig), weit danach eine dunkle (bitter, röstig).',
 variiert:'<b>Achtung:</b> „Second Crack" gibt es auch — er markiert erst die sehr dunklen Röstungen.',
 quelle:'kap1', anker:'g2'},

{id:'k1-5',nr:5,typ:'order',titel:'Vom Strauch in die Tasse',
 frage:'Bringen Sie die Schritte in die richtige Reihenfolge (1 = zuerst).',
 hinweis:'Tragen Sie 1 bis 5 ein.',
 items:['Rösten','Ernten','Mahlen','Aufbereiten und Trocknen','Brühen'],
 richtig:[3,1,4,2,5],
 erklaerung:'Ernten → Aufbereiten/Trocknen → Rösten → Mahlen → Brühen.',
 variiert:'<b>Die Falle:</b> Mahlen gehört direkt vor das Brühen, nicht vor das Rösten — gemahlener Kaffee verliert sein Aroma in Minuten.',
 quelle:'kap1', anker:'g1'}
]}

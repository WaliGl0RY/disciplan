
/* ══════════ Blattmodus ══════════
   Alle Fragen eines Kapitels untereinander auf einer Seite, zum Scrollen.
   Jede Frage lässt sich einzeln auflösen, oder am Stück über „Alles auswerten“.
   Derselbe Bau trägt den Klausurbogen: gezogene Fragen aus allen Kapiteln,
   im Zuschnitt einer typischen Klausuraufgabe 1 (4 Ankreuz- + 4 Wahr/Falsch-Fragen). */
let BLATT = true;           /* Kapitel öffnen standardmäßig als Blatt */
let BL = null;              /* laufendes Blatt */
let PROSEITE = 10;          /* 0 = alle auf einmal, sonst 5 oder 10 je Seite */
try{ const v = localStorage.getItem(KEY+'-pro'); if(v !== null) PROSEITE = +v }catch(e){}

/* Blatt über eine gefilterte Auswahl, z. B. nur wahr/falsch */
function blattFilter(fn, titel){
  const l = alleFragen().filter(q => BLTYP(q) && fn(q));
  if(!l.length){ meldung('Nichts gefunden.'); return }
  blattStart(titel, shuf(l), null);
}

const alleFragen = () => sets().reduce((a, s) => a.concat(s.fragen), []);
/* Ankreuzformate trägt das Blatt; Rechnen, Zuordnen, Lücken und Karteikarten
   bleiben dem Einzelmodus vorbehalten. */
const BLTYP = q => !q.typ || q.typ === 'single' || q.typ === 'multi';
const pktVon = q => q.kopf ? 0 : (q.frei ? q.pkt : (q.wf ? 1.5 : 1));

/* ══ Antworten mischen ══
   Sonst steht die richtige Antwort immer an derselben Stelle und man lernt
   die Position statt die Sache. Wahr/falsch bleibt in seiner festen Ordnung,
   ebenso alles, was ein Generator gerade frisch gewürfelt hat. */
function mische(q){
  if(!q || !q.optionen || q.optionen.length < 2) return q;
  if(q.wf || q.gen || q.istGen || q.nichtMischen) return q;
  if(!(!q.typ || q.typ === 'single' || q.typ === 'multi')) return q;
  const idx = shuf(q.optionen.map((_, i) => i));
  const neu = {optionen: idx.map(i => q.optionen[i]),
               richtig: (q.richtig || []).map(i => idx.indexOf(i)).sort((a, b) => a - b)};
  if(q.optionNotiz){
    const n = {};
    Object.keys(q.optionNotiz).forEach(k => { n[idx.indexOf(+k)] = q.optionNotiz[k] });
    neu.optionNotiz = n;
  }
  return Object.assign({}, q, neu);
}

/* ══ Ganze Klausur: Aufgabe 1 gezogen, Aufgaben 2-4 aus data/boegen.js ══ */
function blattVollklausur(bogenId){
  const bg = (DATA.boegen||[]).find(b => b.id === bogenId) || pick(DATA.boegen||[]);
  if(!bg){ meldung('Kein Bogen hinterlegt.'); return }
  const alle = alleFragen();
  const items = [{kopf:true, text:'Aufgabe 1 · Verständnisfragen', pkt:10,
                  intro:'Vier zum Ankreuzen (je 1 Punkt), vier wahr oder falsch mit kurzer Begründung (je 1,5 Punkte). Die Begründung gehört aufs Papier — hier wird nur das Kreuz gezählt.'}]
    .concat(ziehen(alle.filter(q=>!q.wf),4), ziehen(alle.filter(q=>q.wf),4));
  bg.teile.forEach(t => {
    items.push({kopf:true, text:'Aufgabe ' + t.nr + ' · ' + t.titel, pkt:t.pkt, intro:t.intro});
    t.teil.forEach(x => items.push(Object.assign({frei:true}, x)));
  });
  blattStart(bg.name, items, {voll:true, bogen:bg.id, mc:4, wf:4});
}

function blattSet(id){
  const s = setById(id);
  const l = s.fragen.filter(BLTYP), weg = s.fragen.length - l.length;
  if(!l.length){ start(id, false); return }
  blattStart((s.klausur ? s.name : (s.begriffe ? 'Begriffe ' : '') + (s.nr ? 'Kap. ' + s.nr + ' · ' : '') + s.name),
             l, null, weg ? {set:id, weg:weg} : null);
}

/* zieht n Fragen, bevorzugt die, die noch nicht sicher sind */
function ziehen(pool, n){
  const offen = shuf(pool.filter(q => ST.status[q.id] !== 'ok'));
  const rest  = shuf(pool.filter(q => ST.status[q.id] === 'ok'));
  return offen.concat(rest).slice(0, n);
}

function blattKlausur(mc, wf, titel){
  const alle = alleFragen();
  const a = ziehen(alle.filter(q => !q.wf), mc);
  const b = ziehen(alle.filter(q =>  q.wf), wf);
  if(a.length + b.length === 0){ meldung('Keine Fragen gefunden.'); return }
  blattStart(titel, a.concat(b), {mc:a.length, wf:b.length});
}

function blattStart(titel, fragen, klausur, rest){
  if(BL && BL.uhr) clearInterval(BL.uhr);
  fragen = fragen.map(mische);
  BL = {titel, fragen, klausur, sel:{}, res:{}, txt:{}, self:{}, zeig:{},
        pro: (klausur ? 0 : PROSEITE), seite: 0,
        rest: rest||null,
        start: (klausur && klausur.voll) ? Date.now() : null, uhr:null};
  /* Nicht jede Trainer-Fassung hat alle Kopfknöpfe — deshalb geduldig zugreifen. */
  const zu = (s,k,an) => { const e = $(s); if(e) e.classList[an?'add':'remove'](k) };
  zu('#home','hide',1); zu('#end','hide',1); zu('#run','hide',0);
  zu('#nav','hide',1); zu('#quit','hide',0); zu('#lernbtn','hide',1); zu('#cnt','hide',1);
  zu('#modepill','hide',0);
  const mp = $('#modepill'); if(mp) mp.textContent = titel;
  blattZeichnen(); window.scrollTo({top:0});
}

function blattZeichnen(){
  const r = $('#run'); r.innerHTML = '';
  const wrap = el('div','blatt');

  const kopf = el('div','blkopf');
  kopf.innerHTML =
    '<div class="blk-l"><span class="kick">' +
      (BL.klausur ? 'Übungsklausur · Aufgabe 1' : 'Blattmodus') + '</span>' +
    '<h2>' + BL.titel + '</h2><p class="sub" id="blstand"></p></div>' +
    '<div class="blk-r">' +
      (BL.pro ? '<button class="btn p" id="blSeite">Diese Seite auswerten</button>' : '') +
      '<button class="btn' + (BL.pro?'':' p') + '" id="blAlle">' +
        (BL.klausur ? 'Alles auswerten' : 'Ganzes Kapitel auswerten') + '</button>' +
      '<button class="btn" id="blReset">Zurücksetzen</button>' +
      (BL.klausur ? '<button class="btn" id="blNeu">Neuer Bogen</button>' : '') +
      (BL.start ? '<span class="bluhr" id="bluhr">75:00</span>' : '') +
    '</div>';
  wrap.appendChild(kopf);

  if(!BL.klausur){
    const seg = el('div','seg blseg');
    [['Alle',0],['10 je Seite',10],['5 je Seite',5]].forEach(pa => {
      const sb = el('button',null,pa[0]);
      sb.setAttribute('aria-selected', BL.pro === pa[1]);
      sb.onclick = () => { BL.pro = pa[1]; BL.seite = 0; PROSEITE = pa[1];
        try{ localStorage.setItem(KEY+'-pro', pa[1]) }catch(e){}
        blattZeichnen(); window.scrollTo({top:0}) };
      seg.appendChild(sb) });
    kopf.querySelector('.blk-l').appendChild(seg);
  }

  const von = BL.pro ? BL.seite*BL.pro : 0;
  const bis = BL.pro ? Math.min(BL.fragen.length, von+BL.pro) : BL.fragen.length;
  for(let i = von; i < bis; i++) wrap.appendChild(blattFrage(BL.fragen[i], i));

  if(BL.pro && BL.fragen.length > BL.pro){
    const seiten = Math.ceil(BL.fragen.length/BL.pro);
    const nav = el('div','blseiten');
    const zu = (s) => { BL.seite = s; blattZeichnen(); window.scrollTo({top:0}) };
    const zb = el('button','btn','‹ zurück'); zb.disabled = BL.seite === 0;
    zb.onclick = () => zu(BL.seite-1); nav.appendChild(zb);
    for(let s = 0; s < seiten; s++){
      const b = el('button','btn sm' + (s===BL.seite?' on':''), String(s+1));
      b.onclick = () => zu(s); nav.appendChild(b);
    }
    const vb = el('button','btn','weiter ›'); vb.disabled = BL.seite === seiten-1;
    vb.onclick = () => zu(BL.seite+1); nav.appendChild(vb);
    wrap.appendChild(nav);
  }

  const fuss = el('div','blfuss');
  fuss.innerHTML = '<button class="btn p" id="blAlle2">Alles auswerten</button>' +
                   '<button class="btn" id="blHome">Zur Übersicht</button>';
  wrap.appendChild(fuss);
  r.appendChild(wrap);

  const A = (a,b) => { for(let i=(a||0); i<(b===undefined?BL.fragen.length:b); i++)
      if(!BL.res[i]) blattLoesen(i,true);
    blattZeichnen(); window.scrollTo({top:0,behavior:'smooth'}) };
  $('#blAlle').onclick = () => A(); $('#blAlle2').onclick = () => A();
  if(BL.pro) $('#blSeite').onclick = () => A(von, bis);
  $('#blReset').onclick = () => { BL.sel={}; BL.res={}; blattZeichnen(); window.scrollTo({top:0}) };
  $('#blHome').onclick = () => home();
  if(BL.klausur) $('#blNeu').onclick = () => BL.klausur.voll
    ? blattVollklausur(null) : blattKlausur(BL.klausur.mc, BL.klausur.wf, BL.titel);
  if(BL.start){
    const tick = () => { const u = document.getElementById('bluhr'); if(!u) return;
      let s = 75*60 - Math.floor((Date.now()-BL.start)/1000);
      const neg = s < 0; if(neg) s = -s;
      u.textContent = (neg?'+':'') + Math.floor(s/60) + ':' + String(s%60).padStart(2,'0');
      u.classList.toggle('aus', neg) };
    tick(); BL.uhr = setInterval(tick, 1000);
  }
  blattStandSchreiben();
  const rb = document.getElementById('blrest');
  if(rb) rb.onclick = e => { e.preventDefault(); start(BL.rest.set, false) };
  if(typeof railBauen==='function') railBauen();
}

function blattFrage(q,i){
  if(q.kopf) return blattKopfKarte(q,i);
  if(q.frei) return blattFrei(q,i);
  const offen = !BL.res[i], sel = BL.sel[i]||[], multi = q.typ==='multi';
  const card = el('div','qcard blq' + (offen?'':' done'));
  card.id = 'blq' + i;
  const pkt = BL.klausur ? '<span class="tag">' + String(pktVon(q)).replace('.',',') + ' Pkt</span>' : '';
  card.innerHTML = '<div class="qmeta"><span class="blnr">' + (i+1) + '</span>' +
    '<span class="qtitle">' + (q.titel||'') + '</span>' +
    (q.wf ? '<span class="tag">wahr/falsch · mit Begründung</span>' : '') +
    (q.kap ? '<span>Kap. ' + q.kap + '</span>' : '') + pkt + '</div>' +
    '<div class="qtext">' + q.frage + '</div>' +
    (q.hinweis && offen ? '<div class="qhint">' + q.hinweis + '</div>' : '');

  const box = el('div','opts');
  q.optionen.forEach((o,j) => {
    const b = el('button','opt' + (multi?'':' rad'));
    const richtig = q.richtig.includes(j), gewaehlt = sel.indexOf(j) >= 0;
    b.setAttribute('aria-pressed', gewaehlt);
    b.innerHTML = '<span class="bx">' + (offen ? (multi?'✓':'●') : (richtig?'✓':'✕')) + '</span><span>' + o + '</span>';
    if(offen){ b.onclick = () => { BL.sel[i] = multi
        ? (gewaehlt ? sel.filter(x=>x!==j) : sel.concat(j)) : [j];
      blattErsetzen(i) }; }
    else{
      b.classList.add(richtig ? 'ok' : 'no');
      const txt = b.querySelector('span:last-child');
      if(gewaehlt){ b.classList.add('mine');
        txt.appendChild(el('span','wahl', richtig ? 'deine Wahl · richtig' : 'deine Wahl · falsch')); }
      const n = (q.optionNotiz||{})[j];
      if(n) txt.appendChild(el('span','on', n));
    }
    box.appendChild(b);
  });
  card.appendChild(box);

  const leiste = el('div','nav bln');
  const inner = el('div','navin');
  if(offen){
    const b1 = el('button','btn p','Diese Frage auflösen');
    b1.onclick = () => { blattLoesen(i); blattErsetzen(i) };
    inner.appendChild(b1);
    const b2 = el('button','btn','Lösung zeigen');
    b2.onclick = () => { ST.stuck[q.id] = (ST.stuck[q.id]||0)+1; save(); blattLoesen(i,true); blattErsetzen(i) };
    inner.appendChild(b2);
  } else {
    const b3 = el('button','btn','Nochmal antworten');
    b3.onclick = () => { delete BL.res[i]; delete BL.sel[i]; blattErsetzen(i) };
    inner.appendChild(b3);
  }
  leiste.appendChild(inner);
  if(offen) card.appendChild(leiste);   /* nach dem Auflösen steht sie unter der Erklärung */

  if(!offen){
    const res = el('div','res');
    const ok = BL.res[i] === 'ok';
    const v = el('div','verd ' + (ok?'ok':'no'));
    v.textContent = ok ? 'Richtig' : (!sel.length ? 'Nicht beantwortet' : 'Nicht richtig');
    res.appendChild(v);
    if(q.erklaerung){ const e = el('div','box ex');
      e.innerHTML = '<h4>Erklärung</h4>' + q.erklaerung; res.appendChild(e) }
    if(q.variiert){ const w = el('div','box va');
      w.innerHTML = '<h4>Was sich in anderen Fällen ändert</h4>' + q.variiert; res.appendChild(w) }
    const src = el('div','src');
    src.innerHTML = (q.quelle ? 'Quelle: <code>' + q.quelle + '</code>' : '') +
      (q.anker ? ' · <a href="' + location.pathname.split('/').pop().replace(/-Trainer\.html$/, '.html') + '#' + q.anker + '" target="_blank">↗ im Lerndokument nachlesen</a>' : '');
    if(q.quelle||q.anker) res.appendChild(src);
    card.appendChild(res);
    card.appendChild(leiste);
  }
  return card;
}

/* Zwischenüberschrift für Aufgabe 1 / 2 / 3 / 4 */
function blattKopfKarte(q,i){
  const d = el('div','blteil'); d.id = 'blq' + i;
  d.innerHTML = '<h3>' + q.text + '</h3><span class="tag">' +
    String(q.pkt).replace('.',',') + ' Punkte</span>' +
    (q.intro ? '<p>' + q.intro + '</p>' : '');
  return d;
}

/* Schriftliche Aufgabe: selbst lösen, Musterlösung aufklappen, Punkte selbst setzen */
function blattFrei(q,i){
  const card = el('div','qcard blq blfrei'); card.id = 'blq' + i;
  const p = BL.self[i];
  card.innerHTML = '<div class="qmeta"><span class="blnr">' + (q.label||'') + '</span>' +
    '<span class="qtitle">schriftlich</span>' +
    '<span class="tag">' + String(q.pkt).replace('.',',') + ' Punkte</span>' +
    (p !== undefined ? '<span class="tag g">' + String(p).replace('.',',') + ' erreicht</span>' : '') +
    '</div><div class="qtext">' + q.frage + '</div>';

  const ta = el('textarea');
  ta.rows = 8; ta.spellcheck = false;
  ta.placeholder = 'Erst auf Papier lösen — hier nur abtippen, wenn du vergleichen willst.';
  ta.value = BL.txt[i] || '';
  ta.oninput = e => BL.txt[i] = e.target.value;
  card.appendChild(ta);

  const leiste = el('div','nav bln'); const inner = el('div','navin');
  const b1 = el('button','btn p', BL.zeig[i] ? 'Lösung ausblenden' : 'Musterlösung zeigen');
  b1.onclick = () => { BL.zeig[i] = !BL.zeig[i]; blattErsetzen(i) };
  inner.appendChild(b1);
  inner.appendChild(el('span','selflb','Deine Punkte:'));
  [['0',0],['die Hälfte',q.pkt/2],['voll',q.pkt]].forEach(pa => {
    const b = el('button','btn sm' + (p===pa[1]?' on':''), pa[0]);
    b.onclick = () => { BL.self[i] = pa[1]; BL.res[i] = pa[1]===q.pkt ? 'ok' : 'no';
      blattErsetzen(i) };
    inner.appendChild(b);
  });
  leiste.appendChild(inner); card.appendChild(leiste);

  if(BL.zeig[i]){
    const m = el('div','box mu'); m.innerHTML = '<h4>Musterlösung</h4>' + q.loesung;
    card.appendChild(m);
  }
  return card;
}

function blattLoesen(i, auchOhneWahl){
  if(BL.fragen[i].kopf || BL.fragen[i].frei) return;
  const q = BL.fragen[i], sel = BL.sel[i]||[];
  if(!sel.length && !auchOhneWahl) return;
  const a = sel.slice().sort().join(','), b = (q.richtig||[]).slice().sort().join(',');
  BL.res[i] = (sel.length && a === b) ? 'ok' : 'no';
  ST.status[q.id] = BL.res[i] === 'ok' ? 'ok' : 'no';
  ST.tage = ST.tage||{}; const hk = heuteKey(); ST.tage[hk] = (ST.tage[hk]||0)+1;
  save();
}

function blattErsetzen(i){
  const alt = document.getElementById('blq' + i);
  if(!alt) return blattZeichnen();
  alt.replaceWith(blattFrage(BL.fragen[i], i));
  blattStandSchreiben();
}

function blattStandSchreiben(){
  const n = BL.fragen.length;
  let fertig = 0, ok = 0, pMax = 0, pIst = 0;
  let p2 = 0;
  BL.fragen.forEach((q,i) => { if(q.kopf) return; pMax += pktVon(q);
    const istA2 = q.frei && String(q.id||'').indexOf('-2') > 0;
    if(q.frei){ if(BL.self[i] !== undefined){ fertig++; pIst += BL.self[i];
        if(istA2) p2 += BL.self[i]; if(BL.self[i]===q.pkt) ok++ } }
    else if(BL.res[i]){ fertig++; if(BL.res[i]==='ok'){ ok++; pIst += pktVon(q) } } });
  const el2 = document.getElementById('blstand'); if(!el2) return;
  const kom = x => String(x).replace('.', ',');
  const kom2 = x => String(Math.round(x*10)/10).replace('.', ',');
  if(BL.klausur && BL.klausur.voll){
    const best = pIst >= 30 && p2 >= 15;
    el2.innerHTML = '<b>60 Punkte</b> · 75 Minuten · bestanden ab <b>30</b> gesamt und <b>15</b> in Aufgabe 2' +
      (fertig ? ' — erreicht: <b>' + kom2(pIst) + ' von 60</b>, davon <b>' + kom2(p2) +
        '</b> in Aufgabe 2 · <span class="' + (best?'bstd':'nbstd') + '">' +
        (best ? 'bestanden' : 'noch nicht bestanden') + '</span>' : '');
    return;
  }
  el2.innerHTML = BL.klausur
    ? '<b>' + n + '</b> Aufgaben · ' + BL.klausur.mc + ' zum Ankreuzen, ' + BL.klausur.wf +
      ' wahr/falsch · <b>' + kom(pMax) + ' Punkte</b>' +
      (fertig ? ' — ausgewertet: <b>' + kom(pIst) + ' von ' + kom(pMax) + '</b> Punkten (' +
        Math.round(100*pIst/pMax) + ' %)' : '')
    : '<b>' + n + '</b> Fragen auf einem Blatt' +
      (BL.rest ? ' · <a href="#" id="blrest">' + BL.rest.weg +
        ' weitere brauchen den Einzelmodus</a>' : '') +
      (BL.pro ? ' · Seite <b>' + (BL.seite+1) + ' von ' +
        Math.ceil(n/BL.pro) + '</b>' : '') +
      (fertig ? ' — ' + fertig + ' ausgewertet, <b>' + ok + '</b> richtig' : '') +
      '. Jede Frage einzeln auflösen oder oben alles auf einmal.';
}

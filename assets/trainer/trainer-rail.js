
/* ══════════ Seitenleiste ══════════
   Ein fester Wegweiser links, aus DATA gebaut: Übersicht, die Übungsarten,
   alle Sets mit Stand, die Klausurbögen und die Werkzeuge. Ein Klick, kein
   Suchen. Über ✕ klappt sie weg, über ☰ kommt sie zurück; die Entscheidung
   wird gemerkt. Auf schmalen Fenstern legt sie sich über den Inhalt. */
const breit = () => matchMedia('(min-width:1100px)').matches;
function railUm(){
  if(breit()){
    const zu = document.body.classList.toggle('railzu');
    try{ localStorage.setItem(KEY + '-railzu', zu ? '1' : '0') }catch(e){}
  } else document.body.classList.toggle('railauf');
}

function railBauen(){
  const r = document.querySelector('#railin'); if(!r) return;
  r.innerHTML = '';
  const h5 = t => r.appendChild(el('h5', null, t));
  const add = (kk, t, dd, fn) => {
    const b = el('button','rl');
    b.innerHTML = '<span class="kk">' + kk + '</span><span class="rt">' + t + '</span>' +
                  (dd ? '<span class="dd">' + dd + '</span>' : '');
    b.onclick = () => { document.body.classList.remove('railauf'); fn() };
    r.appendChild(b);
  };
  const st = s => { let ok = 0; s.fragen.forEach(q => { if(ST.status[q.id]==='ok') ok++ }); return ok };
  const kurz = n => n.replace(/^(OOP|Ein-\/Ausgabe|Dynamische Datenstrukturen)\s*[—–-]\s*/,'');
  const alle = alleFragen();
  const offen = alle.filter(q => ST.status[q.id] !== 'ok').length;
  const hatWF = alle.some(q => q.wf);
  const kopf = document.querySelector('.hd h1');
  const name = ((kopf && kopf.textContent) || 'Trainer').split('·')[0].trim();
  const modul = name.replace('-Trainer','').trim();

  const br = el('div','brand'); br.innerHTML = '<span>' + name + '</span>';
  const zu = el('button', null, '✕'); zu.id = 'railzu'; zu.title = 'Menü ausblenden';
  zu.onclick = railUm; br.appendChild(zu); r.appendChild(br);
  const sub = ((kopf && kopf.textContent) || '').split('·')[1];
  if(sub) r.appendChild(el('div','bsub', sub.trim()));
  add('▦','Übersicht','', () => home());

  h5('Üben');
  add('▸','Weitermachen', offen ? String(offen) : '',
      () => startFilter('off', q => ST.status[q.id] !== 'ok', 'Offen und noch nicht sicher'));
  add('≡','Alles gemischt','', () => blattFilter(() => true, 'Alles gemischt'));
  if(hatWF) add('✓','Nur wahr/falsch','', () => blattFilter(q => q.wf, 'Wahr oder falsch'));
  add('↺','Festgehangen','', () => blattFilter(q => (ST.stuck||{})[q.id], 'Wo ich festgehangen habe'));

  if((DATA.begriffe||[]).length){
    h5('Begriffe');
    DATA.begriffe.forEach(s => add(String(s.nr), kurz(s.name),
      st(s) + '/' + s.fragen.length, () => start(s.id, true)));
  }

  if((DATA.quizzes||[]).length){
    h5(DATA.begriffe && DATA.begriffe.length ? 'Aufgaben' : 'Kapitel');
    DATA.quizzes.forEach(s => add(String(s.nr), kurz(s.name),
      st(s) + '/' + s.fragen.length, () => blattSet(s.id)));
  }

  if((DATA.klausuren||[]).length){
    h5('Klausuren');
    DATA.klausuren.forEach(s => add('★', s.name.split('·')[0].trim(),
      st(s) + '/' + s.fragen.length, () => blattSet(s.id)));
  }

  if(hatWF || (DATA.boegen||[]).length){
    h5('Klausur üben');
    if(hatWF){
      add('A1','Aufgabe 1 ziehen','10 P', () => blattKlausur(4,4,'Übungsklausur · Aufgabe 1'));
      add('WF','Acht Aussagen','12 P', () => blattKlausur(0,8,'Acht Aussagen wahr oder falsch'));
    }
    (DATA.boegen||[]).forEach((bg,i) =>
      add('K'+(i+1), (bg.name.split('·')[1]||bg.name).trim(), '60 P', () => blattVollklausur(bg.id)));
    if((DATA.boegen||[]).length)
      add('⟳','Zufälliger Bogen','60 P', () => blattVollklausur(null));
  }

  h5('Werkzeuge');
  if((DATA.spick||[]).length) add('📋','Spickzettel','', () => spickAuf());
  add('↗','Lerndokument','', () => window.open(modul + '.html','_blank'));
}

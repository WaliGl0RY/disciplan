// check.js — prueft die Datendateien und die Generatoren.
// Aufruf: node check.js
const fs = require('fs'), path = require('path'), vm = require('vm');
const HERE = __dirname;
let fehler = 0;
const w = (id, m) => { console.log('  !! ' + id + ': ' + m); fehler++; };

// ── 1. Datendateien ──────────────────────────────────────────────
const files = fs.readdirSync(path.join(HERE, 'data')).filter(f => f.endsWith('.js')).sort();
let gesamt = 0, ids = new Set(), anker = new Set(), genRef = new Set();
for (const f of files) {
  let o;
  try { o = eval('(' + fs.readFileSync(path.join(HERE, 'data', f), 'utf8') + ')'); }
  catch (e) { console.log('SYNTAXFEHLER ' + f + ': ' + e.message); fehler++; continue; }
  if (!o || !o.fragen) { console.log('ok     ' + f + '  (kein Aufgabensatz)'); continue; }
  let bad = fehler;
  o.fragen.forEach(q => {
    if (!q.id || !q.typ) return w(f, 'id oder typ fehlt');
    if (ids.has(q.id)) w(q.id, 'doppelte id');
    ids.add(q.id);
    if (q.anker) anker.add(q.anker);
    if (q.gen) genRef.add(q.gen + '||' + q.id);
    if (q.typ === 'begriff') {
      if (!q.begriff) w(q.id, 'kein Begriff');
      if (!q.de) w(q.id, 'keine deutsche Erklaerung');
      if (!q.en) w(q.id, 'keine englische Erklaerung');
      if (q.de && q.de.length < 25) w(q.id, 'deutsche Erklaerung zu knapp');
      gesamt++; return;
    }
    if (q.typ === 'gen') { gesamt++; return; }   // Text kommt vom Generator, geprueft in Abschnitt 2
    if (!q.frage) w(q.id, 'keine Frage');
    if (!q.erklaerung) w(q.id, 'keine Erklaerung');
    if (!q.variiert) w(q.id, 'kein "was aendert sich"');
    if (q.typ === 'single' || q.typ === 'multi') {
      if (!q.optionen || !q.optionen.length) w(q.id, 'keine Optionen');
      if (!q.richtig || !q.richtig.length) w(q.id, 'keine Loesung');
      else q.richtig.forEach(i => { if (i < 0 || i >= q.optionen.length) w(q.id, 'Loesungsindex ' + i + ' ausserhalb'); });
      if (q.typ === 'single' && q.richtig && q.richtig.length !== 1) w(q.id, 'single mit ' + q.richtig.length + ' Loesungen');
      if (q.typ === 'multi' && !q.nurEins && q.richtig && q.richtig.length < 2) w(q.id, 'multi mit nur einer Loesung');
      if (q.optionNotiz) Object.keys(q.optionNotiz).forEach(k => {
        if (+k >= q.optionen.length) w(q.id, 'optionNotiz-Index ' + k + ' ausserhalb');
      });
      if (q.hinweis) {
        const m = q.hinweis.match(/(eine|zwei|drei|vier|fünf|\((\d)\))\s*Antwort|\((\d)\)/i);
        const z = { eine: 1, zwei: 2, drei: 3, vier: 4, 'fünf': 5 };
        let soll = null;
        const zahl = q.hinweis.match(/\((\d)\)/);
        if (zahl) soll = +zahl[1];
        else if (m && z[m[1].toLowerCase()]) soll = z[m[1].toLowerCase()];
        if (soll !== null && q.richtig && soll !== q.richtig.length)
          w(q.id, 'Hinweis nennt ' + soll + ', Loesung hat ' + q.richtig.length);
      }
    }
    if (q.typ === 'num') {
      if (!q.felder || !q.felder.length) w(q.id, 'keine Felder');
      else q.felder.forEach(fd => { if (!(q.loesung || {})[fd.k]) w(q.id, 'keine Loesung fuer Feld ' + fd.k); });
    }
    if (q.typ === 'match') { if (!q.zuordnung) w(q.id, 'keine Zuordnungsliste'); }
    if (q.typ === 'gap') {
      if (!q.text) w(q.id, 'kein Lueckentext');
      else {
        const ids = [...q.text.matchAll(/\[(\d+)\]/g)].map(m => +m[1]);
        if (!q.luecken) w(q.id, 'keine Luecken');
        else {
          if (ids.length !== q.luecken.length) w(q.id, ids.length + ' Marken, ' + q.luecken.length + ' Luecken');
          q.luecken.forEach((l, i) => { if (!l.o || l.a === undefined || l.a >= l.o.length) w(q.id, 'Luecke ' + i + ' fehlerhaft'); });
        }
      }
    }
    if (q.typ === 'order' || q.typ === 'match') {
      if (!q.items || !q.richtig) w(q.id, 'items/richtig fehlt');
      else {
        if (q.items.length !== q.richtig.length) w(q.id, 'items und richtig ungleich lang');
        if (q.mehrfach) {
          // Kategorien duerfen mehrfach vergeben werden
          const n = (q.zuordnung || []).length;
          q.richtig.forEach(r => { if (r < 1 || r > n) w(q.id, 'Zuordnung ' + r + ' ausserhalb 1..' + n); });
        } else {
        if (q.zuordnung && q.zuordnung.length !== q.items.length) w(q.id, 'zuordnung und items ungleich lang');
        const s = q.richtig.slice().sort((a, b) => a - b).join(',');
        const soll = q.items.map((_, i) => i + 1).join(',');
        if (s !== soll) w(q.id, 'Reihenfolge ist nicht 1..n, sondern ' + s);
        }
      }
    }
    if (q.typ === 'text' && !q.muster) w(q.id, 'keine Musterantwort');
    gesamt++;
  });
  console.log((fehler === bad ? 'ok     ' : 'FEHLER ') + f + '  ' + o.fragen.length + ' Aufgaben');
}
console.log('-> ' + gesamt + ' Aufgaben, ' + ids.size + ' eindeutige ids');
// Anker gegen KAF.html pruefen (ids direkt aus dem Lerndokument)
try {
  const doc = fs.readFileSync(path.join(HERE, '..', 'KAF.html'), 'utf8');
  const vorhanden = new Set([...doc.matchAll(/\bid="([^"]+)"/g)].map(m => m[1]));
  const tot = [...anker].filter(a => !vorhanden.has(a));
  if (tot.length) { tot.forEach(a => w('Anker', "'" + a + "' gibt es in KAF.html nicht")); }
  else console.log('   ' + anker.size + ' Sprungziele, alle in KAF.html vorhanden');
} catch (e) { console.log('   (KAF.html fehlt, Ankerpruefung uebersprungen)'); }
console.log('');

// ── 2. Generatoren ───────────────────────────────────────────────
const shell = fs.readFileSync(path.join(HERE, 'shell.html'), 'utf8');
const gen = 'const GEN={};';
const helfer = shell.slice(shell.indexOf('const $=s=>'), shell.indexOf('/* ══'), 0);
const pre = `
const eur=n=>n.toLocaleString('de-DE',{minimumFractionDigits:0,maximumFractionDigits:2})+' EUR';
const ri=(a,b)=>a+Math.floor(Math.random()*(b-a+1));
const pick=a=>a[Math.floor(Math.random()*a.length)];
const shuf=a=>{a=a.slice();for(let i=a.length-1;i>0;i--){const j=Math.floor(Math.random()*(i+1));[a[i],a[j]]=[a[j],a[i]]}return a};
const ggt=(a,b)=>b?ggt(b,a%b):a;
const fmt=n=>n.toLocaleString('de-DE');
const r2=n=>n.toFixed(2).replace('.',',');
`;
const ctx = {};
vm.createContext(ctx);
let gen2 = fs.readFileSync(path.join(HERE, 'gen2.js'), 'utf8');
gen2 = gen2.slice(gen2.indexOf('{'));
vm.runInContext(pre + gen + '\nObject.assign(GEN, ' + gen2 + ');\nthis.G=GEN;', ctx);
const G = ctx.G;

const namen = Object.keys(G);
for (const r of genRef) { const [n, id] = r.split('||'); if (!namen.includes(n)) w(id, "gen:'" + n + "' existiert nicht"); }
console.log('Generatoren: ' + namen.length);
for (const n of namen) {
  let ok = 0;
  for (let i = 0; i < 300; i++) {
    let r;
    try { r = G[n](); } catch (e) { w('GEN ' + n, 'Ausnahme: ' + e.message); break; }
    if (!r.frage) { w('GEN ' + n, 'keine Frage'); break; }
    if (!r.erklaerung) { w('GEN ' + n, 'keine Erklaerung'); break; }
    if (!r.variiert) { w('GEN ' + n, 'kein "was aendert sich"'); break; }
    if (r.optionen) {
      if (!r.richtig || !r.richtig.length) { w('GEN ' + n, 'keine Loesung'); break; }
      if (new Set(r.optionen).size !== r.optionen.length) { w('GEN ' + n, 'doppelte Option: ' + r.optionen.join(' | ')); break; }
      let bad = r.richtig.some(x => x < 0 || x >= r.optionen.length);
      if (bad) { w('GEN ' + n, 'Loesungsindex ausserhalb'); break; }
      if (r.hinweis) {
        const z = r.hinweis.match(/\((\d)\)/);
        if (z && +z[1] !== r.richtig.length) { w('GEN ' + n, 'Hinweis ' + z[1] + ' != ' + r.richtig.length); break; }
        if (/zwei Antworten/.test(r.hinweis) && r.richtig.length !== 2) { w('GEN ' + n, 'sagt zwei, hat ' + r.richtig.length); break; }
      }
    } else if (r.felder) {
      for (const fd of r.felder) {
        if (r.loesung[fd.k] === undefined || r.loesung[fd.k] === '') { w('GEN ' + n, 'keine Loesung fuer ' + fd.k); i = 999; break; }
      }
    } else { w('GEN ' + n, 'weder Optionen noch Felder'); break; }
    ok++;
  }
  console.log((ok === 300 ? '  ok     ' : '  FEHLER ') + n + '  ' + ok + '/300 Durchlaeufe');
}

// ── 3. Mathematische Stichproben ─────────────────────────────────

// ── 3. Rechenproben: die Loesung muss aus der Aufgabe folgen ─────
console.log('\nRechenproben:');
const probe=(name,fn)=>{let ok=true;
  for(let i=0;i<200;i++){ try{ if(!fn(G[name]())) {ok=false;break} }catch(e){ok=false;console.log('   '+e.message);break} }
  console.log((ok?'  ok     ':'  FEHLER ')+name); if(!ok) fehler++;};
const z=t=>parseFloat(String(t).replace(/[^0-9,.-]/g,'').replace(/\.(?=\d{3}\b)/g,'').replace(',','.'));
probe('bruehrezept', r=>{
  const k=z(r.loesung.k), t=z(r.loesung.t);
  const w_=z(r.frage.match(/<b>(\d+) ml<\/b>/)[1]), v=z(r.frage.match(/1 : (\d+)/)[1]);
  const n=z(r.frage.match(/<b>(\d+) Tassen<\/b>/)[1]);
  return Math.abs(w_/v-k)<0.5 && Math.abs(k/n-t)<0.5;});
probe('temperatur', r=>{
  const c=z(r.frage.match(/<b>(\d+) °C<\/b>/)[1]);
  return Math.abs(z(r.loesung.f)-(c*9/5+32))<0.11 && z(r.loesung.k)===c+273;});

console.log('\n' + (fehler ? 'FEHLER: ' + fehler : 'Alles in Ordnung.'));
process.exit(fehler ? 1 : 0);


/* ══════════ Cockpit-Kopf ══════════
   Zeigt oben auf der Startseite, wie weit du bist, und bringt einen Knopf
   mit, der ohne Umweg in die noch offenen Aufgaben springt. */
function heuteKey(){const d=new Date();
  return d.getFullYear()+'-'+String(d.getMonth()+1).padStart(2,'0')+'-'+String(d.getDate()).padStart(2,'0')}
function cockpitKopf(){
  let ok=0,no=0,tot=0,fertig=0,setsN=0;
  sets().forEach(s=>{let o=0;setsN++;
    s.fragen.forEach(q=>{tot++;const v=ST.status[q.id];
      if(v==='ok'){ok++;o++}else if(v){no++}});
    if(s.fragen.length&&o===s.fragen.length)fertig++});
  const pct=tot?Math.round(100*ok/tot):0;
  const heute=(ST.tage||{})[heuteKey()]||0;
  const kopf=document.querySelector('.hd h1');
  const name=((kopf&&kopf.textContent)||'Trainer').split('·')[0].trim();
  const gruss = (tot&&ok===tot) ? 'Alles sitzt.' : pct>=60 ? 'Das läuft.'
              : heute ? 'Weiter so.' : 'Fangen wir an.';
  const R=40,U=2*Math.PI*R;
  const box=el('div','hero');
  box.innerHTML=
   '<div class="hero-l">'+
     '<span class="kick">'+name+'</span>'+
     '<h1>'+gruss+'</h1>'+
     '<p><b>'+tot+'</b> Aufgaben in '+setsN+' Sets. '+
       (heute?'Heute schon <b>'+heute+'</b> beantwortet.':'Heute noch keine beantwortet.')+
       ' Der Stand bleibt im Browser gespeichert.</p>'+
     '<div class="hero-btns">'+
       '<button class="hb p" id="hbGo">'+(ok<tot?'Weitermachen':'Nochmal von vorn')+'</button>'+
       '<button class="hb" id="hbMix">Alles gemischt</button>'+
     '</div>'+
   '</div>'+
   '<div class="hero-r">'+
     '<div class="ring"><svg width="94" height="94" viewBox="0 0 94 94">'+
       '<circle class="bgc" cx="47" cy="47" r="'+R+'" fill="none" stroke-width="9"></circle>'+
       '<circle class="fgc" cx="47" cy="47" r="'+R+'" fill="none" stroke-width="9" '+
         'stroke-dasharray="'+U.toFixed(1)+'" stroke-dashoffset="'+U.toFixed(1)+'"></circle>'+
     '</svg><span class="v">'+pct+'%</span></div>'+
     '<div class="hnums">'+
       '<div><b>'+ok+'</b><span>sicher</span></div>'+
       '<div><b>'+no+'</b><span>offen oder falsch</span></div>'+
       '<div><b>'+(tot-ok-no)+'</b><span>noch nie dran</span></div>'+
       '<div><b>'+fertig+'</b><span>Sets fertig</span></div>'+
     '</div>'+
   '</div>';
  setTimeout(function(){const c=box.querySelector('.fgc');
    if(c)c.setAttribute('stroke-dashoffset',(U*(1-pct/100)).toFixed(1))},60);
  box.querySelector('#hbGo').onclick=()=>ok<tot
    ? startFilter('off',q=>ST.status[q.id]!=='ok','Offen und noch nicht sicher')
    : startFilter('alle',()=>true,'Alles gemischt',true);
  box.querySelector('#hbMix').onclick=()=>startFilter('alle',()=>true,'Alles gemischt',true);
  return box;
}

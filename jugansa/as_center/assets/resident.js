// 입주민 화면: ① 업체 연락처 → ② 주관사에 요청(4단계) → ③ 진행 확인(해결 확인 · 다시 요청)
(function(){
'use strict';
var P=new URLSearchParams(location.search),CODE=P.get('d')||'',KEY=P.get('k')||'';
var VEND=[],ITEMS=[],MANY=6,FORGOT='forgot',S,STEP=1,EXP={},RATE={},RNOTE={},FLASH={},CENTER=false;
window.ROWS={};
var BUILD_WORDS='아파트자체하자시공사벽창호배관타일결로누수곰팡이균열천장바닥';
function vendorsOf(it){return VEND.filter(function(v){return v.item===it;});}
function t4(v){return (v.tel||'').replace(/\D/g,'').slice(-4);}
// 업체 찾기: 칸마다 따로 맞춤. 숫자만 3자리 이상이면 전화 뒤 4자리도 봄. 이름이 똑같은 업체를 맨 위로
function vmatch(v,q){if(!q)return true;var n=v.co.replace(/\s/g,''),t=(v.tag||'').replace(/\s/g,'');
  if(/^\d+$/.test(q))return n.indexOf(q)>=0||(q.length>=3&&t4(v).indexOf(q)>=0);
  return n.indexOf(q)>=0||t.indexOf(q)>=0;}
function vsort(rows,q){return rows.slice().sort(function(a,b){return (b.co.replace(/\s/g,'')===q)-(a.co.replace(/\s/g,'')===q);});}

if(!CODE){$('noDanji').textContent='단지 안내문의 QR 코드나 문자로 받은 링크로 들어와 주세요.';$('noDanji').hidden=false;return;}
api('danji',null,{d:CODE}).then(function(j){
  if(!j.ok){$('noDanji').textContent=j.msg;$('noDanji').hidden=false;return;}
  $('djName').textContent=j.name+' 입주민 전용';$('djName').hidden=false;document.title=j.name+' · 엣지컴퍼니 A/S 도움 창구';
  if(j.keep)$('keepTxt').textContent=j.keep;
  // 주관사 한 창구 단지: 업체 연락처 탭 · '업체에 먼저 연락' 단계 없이 바로 접수(단계 번호도 01 ~ 03)
  CENTER=j.intake==='center';
  if(CENTER){$('t-vendors').hidden=true;document.querySelector('#fm .sec[data-step="3"] .h2 .k').textContent='02';document.querySelector('#fm .sec[data-step="4"] .h2 .k').textContent='03';}
  VEND=j.vendors;VEND.forEach(function(v){if(ITEMS.indexOf(v.item)<0)ITEMS.push(v.item);});
  $('item').innerHTML='<option value="">품목을 골라 주세요</option>'+ITEMS.map(function(x){return '<option value="'+esc(x)+'">'+esc(x)+' (업체 '+vendorsOf(x).length+'곳)</option>';}).join('')+'<option value="unknown">잘 모르겠어요</option><option value="free">목록에 없어요(직접 적기)</option>';
  $('app').hidden=false;resetForm();renderVgrid();
  if(KEY){show('check');lookup({k:KEY});}else show((location.hash||'').slice(1)||'vendors');
});

// 탭
var VIEWS=['vendors','req','check'];
function show(v){if(VIEWS.indexOf(v)<0||(CENTER&&v==='vendors'))v=CENTER?'req':'vendors';VIEWS.forEach(function(x){$('v-'+x).hidden=x!==v;$('t-'+x).setAttribute('aria-selected',x===v?'true':'false');});try{history.replaceState(null,'','?d='+encodeURIComponent(CODE)+'#'+v);}catch(e){}}
document.querySelector('nav.tabs').onclick=function(e){var b=e.target.closest('button');if(b)show(b.getAttribute('data-v'));};

// ① 업체 연락처
function renderVgrid(){
  var q=($('vq').value||'').replace(/\s/g,''),hit=function(s){return !q||s.replace(/\s/g,'').indexOf(q)>=0;};
  var html=ITEMS.map(function(it){
    var all=vendorsOf(it),rows=hit(it)?all:vsort(all.filter(function(v){return vmatch(v,q);}),q);
    if(!rows.length)return '';
    var cut=!q&&!EXP[it]&&rows.length>4,shown=cut?rows.slice(0,3):rows;
    return '<div class="vc"><div class="it">'+esc(it)+'</div><div class="n">선정 업체 '+all.length+'곳'+(rows.length<all.length?' · 찾은 업체 '+rows.length+'곳':'')+'</div>'
      +shown.map(function(v){return '<div class="vrow"><span class="co">'+esc(v.co)+' <small style="font-weight:500;color:var(--ink-2)">'+esc(v.tag)+'</small></span><a class="tel" href="tel:'+esc(v.tel.replace(/\D/g,''))+'" style="color:inherit;text-decoration:none">'+esc(v.tel)+'</a><button class="ghost sm" type="button" data-id="'+v.id+'">이 업체로 요청</button></div>';}).join('')
      +(cut?'<button class="link" type="button" data-exp="'+esc(it)+'" style="margin-top:4px;text-align:left">업체 '+all.length+'곳 모두 보기</button>':'')+'</div>';}).join('');
  if(!q||hit(BUILD_WORDS))html+='<div class="vc build"><div class="it">아파트 자체 하자</div><div class="co">벽 · 창호 · 배관 · 타일 등 분양 때 시공된 부분</div><div class="as" style="border-top-color:var(--hair)">판정과 보수는 시공사 하자 접수 창구에서 합니다. 주관사는 정리 · 전달 · 진행 확인을 돕습니다.</div><div class="acts"><button class="ghost sm" type="button" data-id="build">주관사에 전달 요청</button></div></div>';
  $('vgrid').innerHTML=html||'<div class="note warn">찾는 품목 · 업체가 없어요. \'주관사에 요청\'에서 \'목록에 없어요\'를 골라 직접 적어 주세요.</div>';
}
$('vq').oninput=renderVgrid;
// 업체 카드에서 요청: 쓰던 내용 · 사진 · 연락처는 그대로 두고 품목 · 업체만 바꿈(접수증이 떠 있으면 새로 시작)
$('vgrid').onclick=function(e){
  var x=e.target.closest('button[data-exp]');if(x){EXP[x.getAttribute('data-exp')]=1;renderVgrid();return;}
  var b=e.target.closest('button[data-id]');if(!b)return;var id=b.getAttribute('data-id');
  if(!$('done').hidden)resetForm();
  if(id==='build')setBuild(true);else{var v=VEND.filter(function(z){return String(z.id)===id;})[0];setBuild(false);$('item').value=v.item;drawVend();setVend(String(v.id));}
  STEP=1;drawSteps();show('req');if(!$('vendMany').hidden)drawVendList();};

// ② 요청(4단계)
function setBuild(on){S.build=on;pickChip($('build'),on?'yes':'no');$('buildNote').hidden=!on;$('itemBox').hidden=on;}
$('build').onclick=function(e){var b=e.target.closest('button');if(b){setBuild(b.getAttribute('data-v')==='yes');drawSteps();}};
// 품목을 고르면 그 품목의 업체만. 6곳 이하 = 버튼, 7곳 이상 = 찾기 + 목록. 1곳이면 바로 골라 둠
function drawVend(){
  var it=$('item').value,vs=vendorsOf(it),many=vs.length>MANY;S.vend='';
  $('itemFreeWrap').hidden=it!=='free';$('vendBox').hidden=!vs.length;$('vendHint').hidden=true;$('vend').hidden=many;$('vendMany').hidden=!many;
  if(!vs.length)return;
  if(many){$('vendQ').value='';$('vendCount').textContent='업체가 '+vs.length+'곳이에요. 계약서 · 영수증의 상호, 취급 품목, 업체 전화번호 뒤 4자리로 찾아보세요.';drawVendList();return;}
  $('vend').innerHTML=vs.map(function(v){return '<button type="button" aria-pressed="false" data-v="'+v.id+'">'+esc(v.co)+'</button>';}).join('')+'<button type="button" aria-pressed="false" data-v="'+FORGOT+'">기억이 안 나요</button>';
  $('vend').onclick=function(e){var b=e.target.closest('button');if(!b)return;S.vend=b.getAttribute('data-v');pickChip($('vend'),S.vend);$('vendHint').hidden=S.vend!==FORGOT;};
  if(vs.length===1){S.vend=String(vs[0].id);pickChip($('vend'),S.vend);}
}
function drawVendList(){
  var it=$('item').value,q=$('vendQ').value.replace(/\s/g,''),rows=vsort(vendorsOf(it).filter(function(v){return vmatch(v,q);}),q);
  $('vlist').innerHTML=rows.map(function(v){return '<button type="button" role="radio" aria-checked="'+(S.vend===String(v.id))+'" data-v="'+v.id+'"><b>'+esc(v.co)+'</b><span>'+esc(v.tag)+'</span><span class="t4">···'+esc(t4(v))+'</span></button>';}).join('')||'<div class="hint" style="padding:10px 12px;margin:0">맞는 업체가 없어요. 아래 \'기억이 안 나요\'를 눌러 주세요.</div>';
  $('vforgot').setAttribute('aria-pressed',S.vend===FORGOT);$('vendHint').hidden=S.vend!==FORGOT;
  var s=$('vlist').querySelector('[aria-checked="true"]');if(s)$('vlist').scrollTop=Math.max(s.offsetTop-8,0);
}
function setVend(id){S.vend=id;if(!$('vendMany').hidden)drawVendList();else pickChip($('vend'),id);}
$('vendQ').oninput=drawVendList;
$('vlist').onclick=function(e){var b=e.target.closest('button');if(!b)return;S.vend=b.getAttribute('data-v');drawVendList();};
$('vforgot').onclick=function(){S.vend=S.vend===FORGOT?'':FORGOT;drawVendList();};
$('item').onchange=drawVend;
$('vcGo').onclick=function(){show('vendors');};
$('body').oninput=function(){$('cnt').textContent=this.value.length+' / 1000';};
function drawPh(note){$('photos').innerHTML=thumbsEdit(S.photos);$('phSize').innerHTML=sizeLine(S.photos)+(note?'<div style="color:var(--warn)">'+esc(note)+'</div>':'');}
$('phIn').onchange=function(){addPhotos(this.files,S.photos,5,function(sk,fl){drawPh(phNote(sk,fl));});this.value='';};
$('phBtn').onkeydown=function(e){if(e.key==='Enter'||e.key===' '){e.preventDefault();$('phIn').click();}};
$('photos').onclick=function(e){var rm=e.target.closest('[data-rm]');if(rm){S.photos.splice(+rm.getAttribute('data-rm'),1);drawPh();return;}var b=e.target.closest('[data-src]');if(b)openLb(S.photos[+b.getAttribute('data-src')].src);};
$('tel').oninput=function(){var d=this.value.replace(/\D/g,'').slice(0,11),v;
  if(d.length<4)v=d;else if(d.length<8)v=d.slice(0,3)+'-'+d.slice(3);else if(d.length===10)v=d.slice(0,3)+'-'+d.slice(3,6)+'-'+d.slice(6);else v=d.slice(0,3)+'-'+d.slice(3,7)+'-'+d.slice(7);this.value=v;};
// 방문 시간: '언제든 가능'(전체)을 고르면 요일 · 시간대는 꺼지고, 요일 · 시간대를 고르면 '언제든 가능'이 꺼짐. '업체와 통화로 협의'는 따로
function drawSlots(){[].forEach.call($('slot').children,function(x){x.setAttribute('aria-pressed',S.slots.indexOf(x.getAttribute('data-v'))>=0);});}
function slotPick(v){var i=S.slots.indexOf(v);if(i>=0)S.slots.splice(i,1);else{if(v===ANY)S.slots=S.slots.filter(function(x){return x===NEGO;});else if(v!==NEGO)S.slots=S.slots.filter(function(x){return x!==ANY;});S.slots.push(v);}drawSlots();}

function drawSteps(focus){
  $('steps').innerHTML=['무엇이','업체 연락','내용 · 사진','연락처'].map(function(t,i){var n=i+1,skip=n===2&&S.build;if(CENTER&&n===2)return '';return '<div class="'+(skip?'skip':n===STEP?'on':n<STEP?'done':'')+'"><b>0'+(CENTER&&n>2?n-1:n)+'</b><span>'+esc(skip?'해당 없음':t)+'</span></div>';}).join('');
  [].forEach.call(document.querySelectorAll('#fm .sec'),function(s){s.hidden=+s.getAttribute('data-step')!==STEP;});
  $('prev').hidden=STEP===1;$('next').hidden=STEP===4;$('go').hidden=STEP!==4;$('err').textContent='';
  if(focus){var h=document.querySelector('#fm .sec[data-step="'+STEP+'"] .h2 b');if(h){h.tabIndex=-1;h.focus({preventScroll:true});}}
}
function stepOk(){
  var it=$('item').value;
  if(STEP===1&&!S.build&&!it)return '품목을 골라 주세요. 모르시면 \'잘 모르겠어요\'를 고르세요.';
  if(STEP===1&&!S.build&&it==='free'&&!$('itemFree').value.trim())return '품목 이름을 적어 주세요.';
  if(STEP===1&&!S.build&&vendorsOf(it).length&&!S.vend)return '계약한 업체를 골라 주세요. 모르시면 \'기억이 안 나요\'를 누르세요.';
  if(STEP===2&&!S.build&&!S.vc)return '업체에 연락해 보셨는지 골라 주세요.';
  if(STEP===3&&!$('body').value.trim())return '내용을 적어 주세요.';
  return '';
}
$('next').onclick=function(){var m=stepOk();if(m){$('err').textContent=m;return;}STEP++;if(STEP===2&&(S.build||CENTER))STEP=3;drawSteps(true);window.scrollTo({top:$('steps').getBoundingClientRect().top+scrollY-12,behavior:'smooth'});};
$('prev').onclick=function(){STEP--;if(STEP===2&&(S.build||CENTER))STEP=1;drawSteps(true);};
function resetForm(){
  S={cat:CATS[0],build:false,photos:[],slots:[NEGO],vc:'',vend:''};STEP=1;
  $('fm').reset();drawVend();
  chipGroup($('cat'),CATS,false,function(v){S.cat=v;});pickChip($('cat'),CATS[0]);
  chipGroup($('vc'),VC,false,function(v){S.vc=v;$('vcNote').hidden=v!==VC[3];});$('vcNote').hidden=true;
  chipGroup($('slot'),SLOTS,true,slotPick,['추천']);drawSlots();
  setBuild(false);drawPh();$('cnt').textContent='0 / 1000';
  $('done').hidden=true;$('fm').hidden=false;$('steps').hidden=false;drawSteps();
}

var SENDING=false;
$('fm').onsubmit=function(e){
  e.preventDefault();if(SENDING)return;
  var dong=$('dong').value.replace(/동|\s/g,''),ho=$('ho').value.replace(/호|\s/g,''),nm=$('nm').value.trim(),tel=$('tel').value.replace(/\D/g,'');
  var miss=[];if(!dong||!ho)miss.push('동 · 호수');if(!nm)miss.push('성함');if(!tel)miss.push('연락처');
  if(miss.length){$('err').textContent='아직 비어 있는 칸이 있어요: '+miss.join(', ');return;}
  if(!/^01[016789]\d{7,8}$/.test(tel)){$('err').textContent='휴대폰 번호를 다시 확인해 주세요. 010으로 시작하는 10 ~ 11자리여야 문자를 받을 수 있어요.';$('tel').focus();return;}
  if(!$('a1').checked||!$('a2').checked){$('err').textContent='필수 동의 2개에 체크해 주세요.';return;}
  var it=$('item').value,fd=new FormData();
  fd.append('d',CODE);fd.append('website',$('website').value);fd.append('build',S.build?'1':'0');fd.append('cat',S.cat);
  if(!S.build){
    if(it==='unknown')fd.append('item_mode','unknown');
    else if(it==='free'){fd.append('item_mode','free');fd.append('item_free',$('itemFree').value.trim());}
    else{fd.append('item_mode','list');fd.append('item',it);fd.append('vendor',S.vend);}
    fd.append('vc',S.vc);}
  fd.append('body',$('body').value.trim());S.slots.forEach(function(x){fd.append('slots[]',x);});
  fd.append('dong',dong);fd.append('ho',ho);fd.append('name',nm);fd.append('tel',tel);fd.append('a1','1');fd.append('a2','1');
  S.photos.forEach(function(p,i){fd.append('photos[]',toBlob(p.src),'photo'+i+'.jpg');});
  SENDING=true;$('go').disabled=true;$('go').textContent='보내는 중…';
  api('submit',fd).then(function(j){
    SENDING=false;$('go').disabled=false;$('go').textContent='주관사에 요청하기';
    if(!j.ok){$('err').textContent=j.msg;return;}
    if(!j.t)return;
    var r=j.t;window.ROWS[r.no]=r;LAST=r;
    $('doneNo').textContent=r.no;$('doneClock').setAttribute('data-no',r.no);$('doneClock').innerHTML=clock(r);
    $('donePh').innerHTML=phBox(r.photos.req,'올린 사진');$('doneTl').innerHTML=tl(r);
    $('fm').hidden=true;$('steps').hidden=true;$('done').hidden=false;window.scrollTo({top:$('v-req').getBoundingClientRect().top+scrollY-12,behavior:'smooth'});
  });
};
var LAST=null;
$('copyNo').onclick=function(){var t=$('doneNo').textContent,b=this;
  function sel(){var g=document.createRange();g.selectNodeContents($('doneNo'));var s=getSelection();s.removeAllRanges();s.addRange(g);b.textContent='선택했어요 · 복사해 주세요';}
  try{navigator.clipboard.writeText(t).then(function(){b.textContent='복사했어요';setTimeout(function(){b.textContent='접수번호 복사';},1500);},sel);}catch(e){sel();}};
$('toCheck').onclick=function(){if(!LAST)return;show('check');lookup({k:LAST.k});};
$('again').onclick=function(){resetForm();};

// ③ 진행 확인
var LASTQ=null;
function lookup(q){LASTQ=q;var d={d:CODE};for(var k in q)d[k]=q[k];
  api('lookup',d).then(function(j){if(!j.ok){$('ckList').innerHTML='<div class="note warn">'+esc(j.msg)+'</div>';return;}
    LIST=j.list;LIST.forEach(function(r){window.ROWS[r.no]=r;});drawCheck();});}
var LIST=[];
function drawCheck(){
  $('ckList').innerHTML=LIST.length?LIST.map(function(r){
    var c='';
    if(r.st===3&&r.confirm===null&&!r.hcAt){var rt=RATE[r.no]||0;
      c='<div class="confirm" data-no="'+esc(r.no)+'"><div style="font-weight:700">처리 완료로 표시됐어요. 해결되었나요?</div>'
       +(r.center?'<div class="hint" style="margin:4px 0 0">주관사가 해피콜로도 확인드립니다. 여기서 먼저 알려 주셔도 됩니다.</div>':'')
       +(known(r)?'<div class="rate"><div class="q">'+esc(r.vend)+' 응대는 어떠셨나요? (선택 · 주관사 업체 관리에만 씁니다)</div><div class="chips" role="group" aria-label="업체 응대 평가">'+[3,2,1].map(function(n){return '<button type="button" data-rate="'+n+'" aria-pressed="'+(n===rt)+'">'+RLB[n]+'</button>';}).join('')+'</div>'
       +(rt===1?'<div class="inl"><input data-rnote placeholder="아쉬웠던 점을 적어 주시면 업체 관리에 반영합니다(선택)" maxlength="200" value="'+esc(RNOTE[r.no]||'')+'"></div>':'')+'</div>':'')
       +'<div class="btnrow" style="margin-top:12px"><button class="btn" type="button" data-ok="1">해결됐어요</button><button class="ghost" type="button" data-ok="0">아직 해결 안 됐어요</button></div>'
       +'<div class="inl" data-why hidden><input placeholder="어떤 점이 아직 남았나요? (필수)" maxlength="200"><button class="ghost" type="button" data-reopen>다시 요청</button></div></div>';}
    else if(r.hcAt)c='<div class="note ok">주관사 해피콜로 해결을 확인해 마감됐습니다. 이용해 주셔서 감사합니다.</div>';
    else if(r.confirm===1)c='<div class="note ok">'+(r.center?'해결됐다고 알려 주셔서 감사합니다. 주관사가 해피콜로 한 번 더 확인드립니다.':'해결 확인으로 마감됐습니다. 이용해 주셔서 감사합니다.')+'</div>';
    return '<div class="item"><div class="top2"><span class="mono">'+esc(r.no)+'</span><span class="pill '+PC[r.st]+'">'+esc(r.stage)+'</span></div>'+(FLASH[r.no]?'<div class="flash">'+esc(FLASH[r.no])+'</div>':'')+'<div style="margin-top:6px;font-weight:700">'+esc(r.build?r.cat:iv(r))+'</div><div style="font-size:13px;color:var(--ink-2)">'+esc(r.body)+'</div>'+phBox(r.photos.req,'올린 사진')+phBox(r.photos.done,'업체 완료 사진')+clockBox(r)+'<ul class="tl">'+tl(r)+'</ul>'+c+'</div>';
  }).join(''):'<div class="note warn">일치하는 요청이 없어요. 동 · 호수는 103-1502처럼(또는 접수번호 EC-…), 연락처는 뒤 4자리만 넣어 주세요.</div>';
}
$('ck').onsubmit=function(e){e.preventDefault();FLASH={};lookup({dh:$('cDh').value,tel4:$('cTel').value.replace(/\D/g,'')});};
$('ckList').onclick=function(e){
  var box=e.target.closest('.confirm');if(!box)return;var no=box.getAttribute('data-no'),r=window.ROWS[no];if(!r)return;
  var b=e.target.closest('button');if(!b)return;
  var ni=box.querySelector('[data-rnote]');if(ni)RNOTE[no]=ni.value;
  if(b.hasAttribute('data-rate')){var n=+b.getAttribute('data-rate');RATE[no]=RATE[no]===n?0:n;drawCheck();return;}
  if(b.getAttribute('data-ok')==='0'){box.querySelector('[data-why]').hidden=false;box.querySelector('[data-why] input').focus();return;}
  var data={d:CODE,k:r.k};
  if(b.getAttribute('data-ok')==='1'){data.ok='1';data.rating=RATE[no]||'';data.note=RNOTE[no]||'';}
  else if(b.hasAttribute('data-reopen')){var inp=box.querySelector('[data-why] input'),why=inp.value.trim();if(!why){need(inp,'아직 남은 문제를 적어 주세요');return;}data.ok='0';data.why=why;}
  else return;
  b.disabled=true;
  api('confirm',data).then(function(j){b.disabled=false;if(!j.ok){alertBox(box,j.msg);return;}
    var t=j.t;window.ROWS[t.no]=t;LIST=LIST.map(function(x){return x.no===t.no?t:x;});
    FLASH[t.no]=data.ok==='1'?(t.center?'해결됐다고 알렸어요. 주관사가 해피콜로 확인드립니다.':'해결 확인으로 마감했어요.'):'다시 요청했어요. '+(known(t)?t.vend+' · 주관사':'주관사')+'에 알렸어요.';drawCheck();});
};
function alertBox(box,msg){var n=document.createElement('div');n.className='note warn';n.textContent=msg;box.appendChild(n);}
})();

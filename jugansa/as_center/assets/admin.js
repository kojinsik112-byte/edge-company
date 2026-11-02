// 주관사 관리: 로그인 → 요청 관리(목록 · 자세히 · 처리 · 되돌리기) / 단지 · 업체(링크 · QR · 안내문) / 문자 기록 / 설정
(function(){
'use strict';
window.ROWS={};
var LIST=[],VENDORS=[],DANJI=[],DJ=0,FST='open',ASEL=null,DET=null,TAB='req',SEEN=0;
var ST_F=[['open','처리 중'],['late','기한 지남'],['done','마감'],['all','전체']];
var WHO={res:'입주민',ven:'업체',adm:'주관사 담당',test:'시험'};

// ---------- 로그인 ----------
api('me').then(function(j){if(j.in){window.CSRF=j.csrf;start(j.name);}else $('login').hidden=false;});
$('login').onsubmit=function(e){e.preventDefault();$('lErr').textContent='';
  api('login',{login:$('lId').value.trim(),pw:$('lPw').value}).then(function(j){if(!j.ok){$('lErr').textContent=j.msg;return;}window.CSRF=j.csrf;$('lPw').value='';$('login').hidden=true;start(j.name);});};
$('logout').onclick=function(){api('logout',{}).then(function(){location.reload();});};
function guard(j){if(j.ok)return true;if(j.msg&&/로그인/.test(j.msg)){location.reload();return false;}return false;}

function start(name){
  $('app').hidden=false;$('who').textContent=name+' 님';$('who').hidden=false;
  $('fSt').innerHTML=ST_F.map(function(s){return '<button type="button" data-v="'+s[0]+'" aria-pressed="'+(s[0]===FST)+'">'+s[1]+'</button>';}).join('');
  $('fSt').onclick=function(e){var b=e.target.closest('button');if(!b)return;FST=b.getAttribute('data-v');pickChip($('fSt'),FST);renderList();};
  $('fQ').oninput=renderList;
  $('fDj').onchange=function(){DJ=+this.value;ASEL=null;$('adDetail').innerHTML='';loadList();};
  try{if(localStorage.getItem('as_noti')==='1'&&window.Notification&&Notification.permission==='granted')$('notiBtn').textContent='새 요청 알림 켜짐';}catch(e){}
  loadList(true);
}
document.querySelector('nav.tabs').onclick=function(e){var b=e.target.closest('button[data-v]');if(!b)return;show(b.getAttribute('data-v'));};
function show(v){TAB=v;['req','dj','sms','set'].forEach(function(x){$('v-'+x).hidden=x!==v;$('t-'+x).setAttribute('aria-selected',x===v?'true':'false');});
  if(v==='req')loadList();if(v==='dj')loadDanji();if(v==='sms')loadSms();if(v==='set')loadSet();}

// ---------- 요청 목록 ----------
function loadList(first){
  api('adm_list',null,{danji:DJ}).then(function(j){if(!guard(j))return;
    LIST=j.list;VENDORS=j.vendors;DANJI=j.danji;LIST.forEach(function(r){window.ROWS[r.no]=r;});
    $('fDj').innerHTML='<option value="0">전체 단지</option>'+DANJI.map(function(d){return '<option value="'+d.id+'"'+(+d.id===DJ?' selected':'')+'>'+esc(d.name)+(+d.active?'':' (멈춤)')+'</option>';}).join('');
    $('csv').href='api.php?a=adm_export&danji='+DJ;
    notifyNew(first);renderList();
    if(first&&location.hash.length>1){var r=LIST.filter(function(x){return x.no===decodeURIComponent(location.hash.slice(1));})[0];if(r)openDetail(r.id);}
  });
}
function djName(id){var d=DANJI.filter(function(x){return +x.id===+id;})[0];return d?d.name:'';}
function isLate(r){return r.nextDue&&r.nextDue<Date.now();}
function renderList(){
  var open=LIST.filter(function(x){return x.st<3;}),late=open.filter(isLate);
  var vend=LIST.filter(function(x){return known(x)&&x.rBy==='업체';}),inTime=vend.filter(function(x){return x.rAt<=x.replyDue;});
  var rated=LIST.filter(function(x){return x.rating;}),good=rated.filter(function(x){return x.rating===3;});
  $('kpi').innerHTML=[
    ['요청',LIST.length+'건',DJ?djName(DJ):'전체 단지'],
    ['처리 중',open.length+'건','마감 전 요청'],
    ['기한 안 1차 회신',vend.length?Math.round(inTime.length/vend.length*100)+'%':'—','업체 회신 '+vend.length+'건 · 주말 · 공휴일 규칙'],
    ['기한 지남',late.length+'건','주관사 개입 대상'],
    ['업체 응대 \'좋았어요\'',rated.length?Math.round(good.length/rated.length*100)+'%':'—','평가 '+rated.length+'건 · 내부용']
  ].map(function(k){return '<div><div class="l">'+esc(k[0])+'</div><div class="v">'+esc(k[1])+'</div><div class="l">'+esc(k[2])+'</div></div>';}).join('');
  var q=($('fQ').value||'').replace(/\s/g,'');
  var rows=LIST.filter(function(r){
    if(FST==='open'&&r.st>=3)return false;if(FST==='late'&&!isLate(r))return false;if(FST==='done'&&r.st<3)return false;
    return !q||(r.no+r.dh+(r.vend||'')+r.item).replace(/\s/g,'').indexOf(q)>=0;});
  rows.sort(function(a,b){return (a.st>=3)-(b.st>=3)||(a.nextDue||9e15)-(b.nextDue||9e15)||b.t-a.t;});
  $('admBody').innerHTML=rows.map(function(r){
    var d=r.nextDue,lt=isLate(r);
    var pill=lt?'<span class="pill pl">주관사 개입</span>':'<span class="pill '+PC[r.st]+'">'+esc(r.stage)+'</span>';
    return '<tr'+(r.id===ASEL?' class="sel"':'')+'><td class="mono">'+esc(r.no)+(r.reopen?'<span class="ex">다시 열림</span>':'')+'</td><td>'+esc(r.dj)+'</td><td>'+esc(r.dh)+'</td><td>'+(r.build||known(r)?esc(iv(r)):esc(r.item)+' · <span class="pill p1">업체 확인 필요</span>')+'</td><td>'+esc(r.build?'—':(VC_SHORT[VC.indexOf(r.vc)]||'—'))+'</td><td>'+pill+'</td><td class="sla'+(lt?' late':'')+'">'+(d?esc((r.st===0?'1차 연락 ':'방문 일정 ')+left(d)):'—')+'</td><td>'+(r.rating?esc(RLB[r.rating]):(r.st===3&&r.confirm===null?'확인 대기':(r.confirm?'평가 안 함':'—')))+'</td><td><button class="ghost sm" type="button" data-id="'+r.id+'">자세히</button></td></tr>';
  }).join('')||'<tr><td colspan="9">해당하는 요청이 없습니다.</td></tr>';
  // 업체별 성적
  $('vsBody').innerHTML=VENDORS.map(function(v){
    var rs=LIST.filter(function(x){return known(x)&&x.vendorId===+v.id;});if(!rs.length)return null;
    var rep=rs.filter(function(x){return x.rBy==='업체';}),ok=rep.filter(function(x){return x.rAt<=x.replyDue;}),op=rs.filter(function(x){return x.st<3;}),lt=op.filter(isLate),rt=rs.filter(function(x){return x.rating;}),gd=rt.filter(function(x){return x.rating===3;});
    var pct=rep.length?Math.round(ok.length/rep.length*100):null;
    return {c:rs.length,h:'<tr><td>'+esc(v.item)+'</td><td><b>'+esc(v.company)+'</b></td><td>'+rs.length+'건</td><td>'+(pct===null?'—':'<span class="bar" style="width:'+Math.max(pct*0.6,4)+'px"></span>'+pct+'%')+'</td><td>'+op.length+'건</td><td'+(lt.length?' style="color:var(--bad);font-weight:700"':'')+'>'+lt.length+'건</td><td>'+(rt.length?Math.round(gd.length/rt.length*100)+'% ('+rt.length+'건 중 '+gd.length+')':'—')+'</td></tr>'};
  }).filter(Boolean).sort(function(a,b){return b.c-a.c;}).map(function(x){return x.h;}).join('')||'<tr><td colspan="7">아직 업체에 연결된 요청이 없습니다.</td></tr>';
}
$('admBody').onclick=function(e){var b=e.target.closest('button[data-id]');if(b)openDetail(+b.getAttribute('data-id'));};

// ---------- 자세히 · 처리 ----------
function openDetail(id){ASEL=id;renderList();api('adm_get',null,{id:id}).then(function(j){if(!guard(j))return;DET=j.t;window.ROWS[DET.no]=DET;renderDetail();$('adDetail').scrollIntoView({behavior:'smooth',block:'nearest'});try{history.replaceState(null,'','#'+DET.no);}catch(e){}});}
function renderDetail(err){
  var r=DET;if(!r){$('adDetail').innerHTML='';return;}
  var acts='',h=r.last;
  if(!r.build&&r.st<3){var its=[];r.vendors.forEach(function(v){if(its.indexOf(v.item)<0)its.push(v.item);});its.sort(function(a,b){return (b===r.item)-(a===r.item);});
    acts+=(known(r)?'':'<div class="note warn" style="margin-top:0">입주민이 업체를 모릅니다. 같은 품목 업체들에 동 · 호로 계약 여부를 확인한 뒤 지정하세요.</div>')
    +'<div class="inl"><select id="aVend"><option value="">'+(known(r)?'바꿀 업체 고르기':'업체 고르기')+'</option>'+its.map(function(it){return '<optgroup label="'+esc(it)+'">'+r.vendors.filter(function(v){return v.item===it&&+v.id!==r.vendorId;}).map(function(v){return '<option value="'+v.id+'">'+esc(v.company)+'</option>';}).join('')+'</optgroup>';}).join('')+'</select><button class="ghost" type="button" data-a="vend">'+(known(r)?'업체 바꾸기 · 문자':'업체 지정 · 문자')+'</button></div>';
    if(known(r))acts+='<div class="inl"><button class="ghost" type="button" data-a="resend">업체에 링크 문자 다시 보내기</button></div>';}
  if(r.st===0)acts+='<div class="inl"><button class="ghost" type="button" data-a="reply">'+(r.build?'시공사에 전달함':'주관사가 직접 연락함')+'</button></div>';
  if(r.st<=1&&r.needVisit)acts+='<div class="inl"><input id="aWhen" placeholder="방문 날짜 · 시간" maxlength="60"><button class="ghost" type="button" data-a="visit">방문 일정 입력</button></div>';
  if(r.st===1&&r.build)acts+='<div class="inl"><button class="ghost" type="button" data-a="bcheck">시공사 처리 확인함</button></div>';
  if(r.st<=2)acts+='<div class="inl"><button class="ghost" type="button" data-a="done">처리 완료</button></div>';
  acts+='<div class="inl"><input id="aMemo" placeholder="메모(처리 이력에 남음)" maxlength="300"><button class="ghost" type="button" data-a="memo">메모 남기기</button></div>';
  if(h)acts+='<div class="undo" style="display:block"><div><b>한 단계 되돌리기</b> · 마지막 처리: \''+esc(h.label)+'\' ('+esc(h.by)+' · '+esc(fmt(h.at))+')</div>'
    +'<div class="inl"><input id="aWhy" placeholder="되돌리는 사유(필수) 예) 업체가 잘못 누름" maxlength="200"><button class="ghost" type="button" data-a="undo">되돌리기</button></div>'
    +(h.res?'<label style="display:flex;gap:6px;align-items:center;margin-top:8px;font-size:13px"><input type="checkbox" id="aFix" checked style="width:auto"> 입주민에게 정정 문자 보내기(이 단계에서 문자가 나갔음)</label>':'')+'</div>';
  $('adDetail').innerHTML='<div class="detail"><div><h3><span class="mono">'+esc(r.no)+'</span> · '+esc(r.dh)+' · '+esc(r.nm)+'</h3>'+(err?'<div class="note warn">'+esc(err)+'</div>':'')+clockBox(r)
    +'<dl class="kv"><dt>단지</dt><dd>'+esc(r.dj)+'</dd><dt>연락처</dt><dd class="mono"><a href="tel:'+esc(r.tel.replace(/\D/g,''))+'" style="color:inherit">'+esc(r.tel)+'</a></dd><dt>구분</dt><dd>'+esc(r.cat)+'</dd><dt>품목 · 업체</dt><dd>'+esc(iv(r))+'</dd><dt>업체 연락</dt><dd>'+esc(r.build?'아파트 자체 하자(업체 없음)':(r.vc||'—'))+'</dd><dt>내용</dt><dd>'+esc(r.body)+'</dd>'+(r.rw?'<dt>다시 연 사유</dt><dd>'+esc(r.rw)+'</dd>':'')+'<dt>방문 시간</dt><dd>'+esc(r.slot)+'</dd>'+(r.visit?'<dt>방문 일정</dt><dd>'+esc(r.visit)+'</dd>':'')+'</dl>'
    +phBox(r.photos.req,'입주민 사진')+phBox(r.photos.done,'업체 완료 사진')
    +'<div class="lbl">주관사 처리</div>'+acts+'</div>'
    +'<div><h3>처리 이력</h3><ul class="log">'+r.log.map(function(l){return '<li'+(l.rev?' class="rev"':'')+'><span class="at">'+esc(fmt(l.at))+'</span><span><b>'+esc(l.who)+'</b> · '+esc(l.what)+'</span></li>';}).join('')+'</ul>'
    +'<details class="smsbox" open style="margin-left:0"><summary>보낸 문자 '+r.sms.length+'건</summary><div class="sms">'+r.sms.map(function(s){return '<div><div class="who"><b>'+esc(WHO[s.kind.split('_')[0]]||s.kind)+'</b><span>'+esc(fmt(s.at))+'</span><span class="tag">'+esc(s.to)+'</span><span class="tag" style="'+(s.ok?'':'color:var(--warn)')+'">'+(s.ok?'보냄':'안 보냄')+'</span></div><div class="b">'+esc(s.msg)+'</div></div>';}).join('')+'</div></details></div></div>';
}
$('adDetail').onclick=function(e){
  var b=e.target.closest('button[data-a]');if(!b||!DET)return;var a=b.getAttribute('data-a'),d={id:DET.id,act:a};
  if(a==='vend'){var s=$('aVend');if(!s.value){s.classList.add('bad');s.focus();return;}d.vendor_id=s.value;}
  if(a==='visit'){var w=$('aWhen').value.trim();if(!w){need($('aWhen'),'방문 날짜 · 시간을 적어 주세요');return;}d.when=w;}
  if(a==='memo'){var m=$('aMemo').value.trim();if(!m){need($('aMemo'),'메모를 적어 주세요');return;}d.memo=m;}
  if(a==='undo'){var y=$('aWhy').value.trim();if(!y){need($('aWhy'),'되돌리는 사유를 적어 주세요(필수)');return;}d.why=y;d.fix=$('aFix')&&$('aFix').checked?'1':'0';}
  b.disabled=true;
  api('adm_act',d).then(function(j){b.disabled=false;if(!guard(j)){renderDetail(j.msg);return;}DET=j.t;window.ROWS[DET.no]=DET;renderDetail();loadList();});
};

// ---------- 새 요청 알림(이 화면을 열어 둔 PC) ----------
function maxId(){return LIST.reduce(function(m,r){return Math.max(m,r.id);},0);}
function notifyNew(first){var mx=maxId();if(!first&&mx>SEEN&&window.Notification&&Notification.permission==='granted'){
  LIST.filter(function(r){return r.id>SEEN;}).slice(0,3).forEach(function(r){try{new Notification('새 A/S 요청 · '+r.dj,{body:r.no+' · '+iv(r)});}catch(e){}});}
  SEEN=Math.max(SEEN,mx);}
$('notiBtn').onclick=function(){if(!window.Notification){this.textContent='이 브라우저는 알림을 지원하지 않아요';return;}var b=this;
  Notification.requestPermission().then(function(p){if(p==='granted'){try{localStorage.setItem('as_noti','1');}catch(e){}b.textContent='새 요청 알림 켜짐';}else b.textContent='알림이 막혀 있어요(브라우저 설정)';});};
// 1분마다 목록 새로 고침 · 자세히는 입력 중이면 건드리지 않음
function editing(box){if(!box)return false;if(box.contains(document.activeElement)&&/INPUT|SELECT|TEXTAREA/.test(document.activeElement.tagName))return true;
  return [].some.call(box.querySelectorAll('input:not([type=checkbox]),select'),function(x){return x.value;});}
setInterval(function(){if(!$('app').hidden&&TAB==='req'){loadList();if(ASEL&&!editing($('adDetail')))api('adm_get',null,{id:ASEL}).then(function(j){if(j.ok){DET=j.t;window.ROWS[DET.no]=DET;renderDetail();}});}},60000);

// ---------- 단지 · 업체 ----------
var DJS=[],VS=[],BASE='';
function loadDanji(){api('adm_danji').then(function(j){if(!guard(j))return;DJS=j.danji;VS=j.vendors;BASE=j.base;drawDanji();});}
function link(d){return BASE+'/?d='+d.code;}
function drawDanji(){
  $('djList').innerHTML=DJS.length?DJS.map(function(d){return '<div class="djcard"><div><div class="nm">'+esc(d.name)+(+d.active?'':' <span class="pill pl">멈춤</span>')+'</div><div class="meta">단지 코드 '+esc(d.code)+' · 업체 '+VS.filter(function(v){return +v.danji_id===+d.id&&+v.active;}).length+'곳 · 보유 기간 '+(d.purge_date?esc(d.purge_date)+'까지':'미정')+'</div><div class="lnk">'+esc(link(d))+'</div>'
    +'<div class="btnrow" style="margin-top:8px"><button class="ghost sm" type="button" data-dj="'+d.id+'" data-x="edit">고치기</button><button class="ghost sm" type="button" data-dj="'+d.id+'" data-x="copy">링크 복사</button><button class="ghost sm" type="button" data-dj="'+d.id+'" data-x="print">안내문(QR) 인쇄</button><button class="ghost sm" type="button" data-dj="'+d.id+'" data-x="vend">업체 보기</button></div></div><div class="qr" id="qr'+d.id+'"></div></div>';}).join(''):'<div class="note info">아직 단지가 없습니다. 아래에서 첫 단지를 만드세요.</div>';
  DJS.forEach(function(d){var el=$('qr'+d.id);if(el&&window.QRCode)new QRCode(el,{text:link(d),width:88,height:88,correctLevel:QRCode.CorrectLevel.M});});
  $('vDj').innerHTML=DJS.map(function(d){return '<option value="'+d.id+'">'+esc(d.name)+'</option>';}).join('');
  if(VDJ&&DJS.some(function(d){return +d.id===VDJ;}))$('vDj').value=String(VDJ);
  drawVendors();
}
$('djList').onclick=function(e){var b=e.target.closest('button[data-dj]');if(!b)return;var d=DJS.filter(function(x){return +x.id===+b.getAttribute('data-dj');})[0],x=b.getAttribute('data-x');
  if(x==='edit'){$('djId').value=d.id;$('djName').value=d.name;$('djPurge').value=d.purge_date||'';$('djKeep').value=d.keep_text||'';$('djActive').value=String(+d.active);$('djFormT').textContent=d.name+' 고치기';$('djForm').scrollIntoView({behavior:'smooth'});}
  if(x==='copy'){var t=link(d);try{navigator.clipboard.writeText(t).then(function(){b.textContent='복사했어요';});}catch(er){b.textContent=t;}}
  if(x==='vend'){VDJ=+d.id;$('vDj').value=String(d.id);drawVendors();$('vBody').scrollIntoView({behavior:'smooth'});}
  if(x==='print')printPoster(d);};
// 입주 안내문용 한 장: 단지 이름 · QR · 링크 · 이용 순서 · 약속
function printPoster(d){var tmp=document.createElement('div');new QRCode(tmp,{text:link(d),width:360,height:360,correctLevel:QRCode.CorrectLevel.M});
  setTimeout(function(){var c=tmp.querySelector('canvas'),src=c?c.toDataURL('image/png'):(tmp.querySelector('img')||{}).src;var w=window.open('','_blank');if(!w)return;
    w.document.write('<!doctype html><html lang="ko"><head><meta charset="utf-8"><title>'+esc(d.name)+' A/S 도움 창구 안내</title><style>body{font-family:"Malgun Gothic","Apple SD Gothic Neo",sans-serif;color:#2a2521;margin:0;padding:40px;text-align:center}h1{font-size:30px;margin:6px 0 4px}h2{font-size:20px;font-weight:600;margin:0 0 24px;color:#8c6a2f}.box{border:2px solid #c99a52;border-radius:14px;padding:28px;max-width:560px;margin:0 auto}ol{text-align:left;font-size:16px;line-height:1.8;max-width:460px;margin:20px auto}.u{font-family:monospace;font-size:14px;word-break:break-all}.p{font-size:14px;color:#6a5f52}</style></head><body><div class="box"><div class="p">엣지컴퍼니 · 공동구매 주관사</div><h1>'+esc(d.name)+'</h1><h2>공동구매 품목 A/S 도움 창구</h2><img src="'+src+'" width="300" height="300" alt="QR"><div class="u">'+esc(link(d))+'</div><ol><li>먼저 계약 업체에 연락해 주세요(업체 번호는 QR 안에 있어요).</li><li>업체가 24시간 안에 답이 없거나 해결이 안 되면 QR로 주관사에 요청하세요.</li><li>주관사가 업체를 챙기고, 업체가 답이 없으면 직접 연락합니다.</li></ol><div class="p">1차 연락 24시간(주말 · 공휴일은 다음 영업일 12시까지) · 방문 일정 확정 48시간</div></div><script>window.onload=function(){window.print();}<\/script></body></html>');w.document.close();},150);}
$('djForm').onsubmit=function(e){e.preventDefault();$('djErr').textContent='';
  api('adm_danji_save',{id:$('djId').value,name:$('djName').value.trim(),purge_date:$('djPurge').value.trim(),keep_text:$('djKeep').value.trim(),active:$('djActive').value}).then(function(j){if(!j.ok){$('djErr').textContent=j.msg;return;}$('djNew').click();loadDanji();});};
$('djNew').onclick=function(){$('djForm').reset();$('djId').value='';$('djFormT').textContent='새 단지';};
var VDJ=0;
$('vDj').onchange=function(){VDJ=+this.value;drawVendors();};
function drawVendors(){var dj=+$('vDj').value;VDJ=dj;var vs=VS.filter(function(v){return +v.danji_id===dj;});
  $('itemList').innerHTML=vs.map(function(v){return v.item;}).filter(function(x,i,a){return a.indexOf(x)===i;}).map(function(x){return '<option value="'+esc(x)+'">';}).join('');
  $('vBody').innerHTML=vs.map(function(v){return '<tr><td>'+esc(v.item)+'</td><td><b>'+esc(v.company)+'</b></td><td>'+esc(v.tag||'')+'</td><td>'+esc(v.person||'')+'</td><td class="mono">'+esc(v.phone)+'</td><td class="mono">'+esc(v.show_phone||'')+'</td><td>'+esc(v.sort)+'</td><td>'+(+v.active?'사용':'멈춤')+'</td><td><button class="ghost sm" type="button" data-v="'+v.id+'">고치기</button></td></tr>';}).join('')||'<tr><td colspan="9">이 단지에는 아직 업체가 없습니다.</td></tr>';}
$('vBody').onclick=function(e){var b=e.target.closest('button[data-v]');if(!b)return;var v=VS.filter(function(x){return +x.id===+b.getAttribute('data-v');})[0];
  $('vId').value=v.id;$('vItem').value=v.item;$('vCo').value=v.company;$('vTag').value=v.tag||'';$('vPerson').value=v.person||'';$('vPhone').value=v.phone;$('vShow').value=v.show_phone||'';$('vSort').value=v.sort;$('vActive').value=String(+v.active);$('vFormT').textContent=v.company+' 고치기';$('vForm').scrollIntoView({behavior:'smooth'});};
$('vForm').onsubmit=function(e){e.preventDefault();$('vErr').textContent='';
  api('adm_vendor_save',{id:$('vId').value,danji_id:$('vDj').value,item:$('vItem').value.trim(),company:$('vCo').value.trim(),tag:$('vTag').value.trim(),person:$('vPerson').value.trim(),phone:$('vPhone').value,show_phone:$('vShow').value,sort:$('vSort').value,active:$('vActive').value}).then(function(j){if(!j.ok){$('vErr').textContent=j.msg;return;}$('vNew').click();loadDanji();});};
$('vNew').onclick=function(){var keep=$('vItem').value;$('vForm').reset();$('vId').value='';$('vItem').value=keep;$('vFormT').textContent='새 업체';};

// ---------- 문자 기록 ----------
function loadSms(){api('adm_sms').then(function(j){if(!guard(j))return;
  $('smsMode').textContent=j.mode==='gabia'?'가비아 문자로 실제 발송 중입니다.':'지금은 실제로 보내지 않고 기록만 남깁니다(config.php의 sms.mode = off). 가비아 설정을 마치면 gabia로 바꾸세요.';
  $('smsBody').innerHTML=j.list.map(function(s){return '<tr><td class="mono">'+esc(fmt(s.at))+'</td><td class="mono">'+esc(s.no||'—')+'</td><td class="mono">'+esc(s.to)+'</td><td>'+esc(WHO[s.kind.split('_')[0]]||s.kind)+'</td><td><div class="smsmsg">'+esc(s.msg)+'</div></td><td'+(s.ok?'':' style="color:var(--warn)"')+'>'+(s.ok?'보냄':'안 보냄')+'<div class="hint" style="margin:0">'+esc(s.resp||'')+'</div></td></tr>';}).join('')||'<tr><td colspan="6">아직 문자 기록이 없습니다.</td></tr>';});}

// ---------- 설정 ----------
var ADMINS=[];
function loadSet(){api('adm_settings').then(function(j){if(!guard(j))return;var s=j.server,m=j.sms;ADMINS=j.admins;
  var yn=function(ok,y,n){return '<span class="'+(ok?'y':'n')+'">'+(ok?y:n)+'</span>';};
  $('srv').innerHTML='<div class="chk"><span>보안 연결(https)</span>'+yn(s.https,'켜짐','꺼짐 · 가비아에서 SSL 인증서를 켜 주세요')
    +'<span>문자 발송</span>'+yn(m.mode==='gabia','가비아로 발송','꺼짐(기록만)')+'<span>발신번호</span><span>'+esc(m.callback||'없음')+'</span><span>가비아 API 키</span>'+yn(m.keys,'있음','없음')
    +'<span>사진 줄이기(GD)</span>'+yn(s.gd,'됨','안 됨 · 휴대폰에서 줄인 사진을 그대로 저장')+'<span>바깥 연결(curl)</span>'+yn(s.curl,'됨','안 됨 · 문자를 보낼 수 없음')
    +'<span>data 폴더 쓰기</span>'+yn(s.writable,'됨','안 됨 · 폴더 권한 확인')+'<span>data 폴더 바깥 노출</span><span id="probe">확인 중…</span>'
    +'<span>DB</span><span>'+esc(s.db)+' · PHP '+esc(s.php)+'</span><span>서버 주소</span><span class="mono">'+esc(s.addr||'—')+' (가비아 문자 \'API 발송 IP\'에는 호스팅 관리 화면의 서버 IP를 넣으세요)</span></div>';
  fetch('data/probe.txt',{cache:'no-store'}).then(function(r){$('probe').innerHTML=r.ok?'<span class="n">열림 · 위험! .htaccess가 올라갔는지 확인하세요</span>':'<span class="y">막힘(정상)</span>';},function(){$('probe').innerHTML='<span class="y">막힘(정상)</span>';});
  $('hol').value=j.holidays;
  $('admins').innerHTML=ADMINS.map(function(a){return '<tr><td class="mono">'+esc(a.login)+'</td><td>'+esc(a.name)+(+a.id===j.me?' (나)':'')+'</td><td class="mono">'+esc(a.phone||'')+'</td><td>'+(+a.notify?'받음':'—')+'</td><td>'+(+a.active?'사용':'멈춤')+'</td><td><button class="ghost sm" type="button" data-ad="'+a.id+'">고치기</button></td></tr>';}).join('');});}
$('holSave').onclick=function(){$('holErr').textContent='';api('adm_holidays_save',{text:$('hol').value}).then(function(j){$('holErr').textContent=j.ok?'저장했습니다('+j.n+'일).':j.msg;});};
$('smsTest').onclick=function(){$('smsTestR').textContent='보내는 중…';api('adm_sms_test',{}).then(function(j){$('smsTestR').textContent=j.ok?(j.sent?'보냈습니다. 휴대폰을 확인하세요.':'보내지 못했습니다: '+j.resp):j.msg;});};
$('admins').onclick=function(e){var b=e.target.closest('button[data-ad]');if(!b)return;var a=ADMINS.filter(function(x){return +x.id===+b.getAttribute('data-ad');})[0];
  $('aId').value=a.id;$('aLogin').value=a.login;$('aLogin').disabled=true;$('aName').value=a.name;$('aPhone').value=a.phone||'';$('aPw').value='';$('aPw').disabled=true;$('aNoti').value=String(+a.notify);$('aAct').value=String(+a.active);};
$('aNew').onclick=function(){$('adForm').reset();$('aId').value='';$('aLogin').disabled=false;$('aPw').disabled=false;};
$('adForm').onsubmit=function(e){e.preventDefault();$('aErr').textContent='';
  api('adm_admin_save',{id:$('aId').value,login:$('aLogin').value.trim(),name:$('aName').value.trim(),phone:$('aPhone').value,pw:$('aPw').value,notify:$('aNoti').value,active:$('aAct').value}).then(function(j){if(!j.ok){$('aErr').textContent=j.msg;return;}$('aNew').click();loadSet();});};
$('pwForm').onsubmit=function(e){e.preventDefault();api('adm_pw',{cur:$('pCur').value,pw:$('pNew').value}).then(function(j){$('pErr').textContent=j.ok?'바꿨습니다.':j.msg;if(j.ok)$('pwForm').reset();});};
})();

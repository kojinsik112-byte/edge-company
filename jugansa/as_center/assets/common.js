// 입주민 · 업체 · 관리 화면이 함께 쓰는 도우미(시연판 as_demo.html과 같은 표시 규칙). 기한 계산은 서버가 해서 보내 줌(replyDue · visitDue · nextDue).
var $=function(id){return document.getElementById(id);};
var esc=function(s){return String(s==null?'':s).replace(/[&<>"']/g,function(c){return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c];});};
var pad=function(n){return String(n).padStart(2,'0');};
var CATS=['품목 하자 · A/S','방문 일정 변경','환불 · 취소','기타 문의 · 불편'];
var VC=['연락했는데 24시간 넘게 답이 없어요','연락했지만 해결이 안 됐어요','업체와 방문 일정이 안 맞아요','아직 연락 안 했어요'];
var VC_SHORT=['답 없음','해결 안 됨','일정 안 맞음','업체 연락 전'];
var NEGO='업체와 통화로 협의', ANY='언제든 가능';
var SLOTS=[NEGO,ANY,'평일 오전','평일 오후','평일 저녁(18시 이후)','토요일','일요일'];
var RLB=['','아쉬워요','보통이에요','좋았어요'];
var PC=['p0','p1','p2','p3'];

function fmt(t){var d=new Date(t);return (d.getMonth()+1)+'.'+pad(d.getDate())+'('+'일월화수목금토'[d.getDay()]+') '+pad(d.getHours())+':'+pad(d.getMinutes());}
function dur(ms){var m=Math.round(Math.abs(ms)/60000);return (m>=60?Math.floor(m/60)+'시간 ':'')+(m%60)+'분';}
function left(t){var ms=t-Date.now();return dur(ms)+(ms<0?' 지남':' 남음');}
function known(r){return !r.build&&!!r.vend;}
function iv(r){return r.build?'아파트 자체 하자':r.item+' · '+(r.vend||'업체 확인 필요');}
// 빈칸에서 눌렀을 때 말없이 끝나지 않게: 빨간 테두리 + 안내 문구 + 커서
function need(el,msg){el.classList.add('bad');el.placeholder=msg;el.focus();el.oninput=function(){el.classList.remove('bad');};}

// 서버 부르기: data가 있으면 POST(FormData). 관리 화면은 window.CSRF를 머리말로 보냄
function api(a,data,q){
  var url='api.php?a='+a+(q?'&'+new URLSearchParams(q).toString():''),init={credentials:'same-origin',headers:{}};
  if(data){init.method='POST';var fd=data instanceof FormData?data:new FormData();
    if(!(data instanceof FormData))Object.keys(data).forEach(function(k){var v=data[k];if(Array.isArray(v))v.forEach(function(x){fd.append(k+'[]',x);});else if(v!=null)fd.append(k,v);});
    init.body=fd;if(window.CSRF)init.headers['X-CSRF']=window.CSRF;}
  return fetch(url,init).then(function(r){return r.json().catch(function(){return {ok:false,msg:'서버 응답을 읽지 못했습니다. 잠시 뒤 다시 해 주세요.'};});},function(){return {ok:false,msg:'인터넷 연결을 확인해 주세요.'};});
}

// 사진: 휴대폰에서 긴 변 1600px · JPEG로 줄여서 올림(원본 3 ~ 8MB → 약 0.3 ~ 0.6MB)
function shrink(f,cb){var rd=new FileReader();rd.onload=function(){var im=new Image();im.onload=function(){var s=Math.min(1,1600/Math.max(im.width,im.height)),c=document.createElement('canvas');c.width=Math.round(im.width*s);c.height=Math.round(im.height*s);c.getContext('2d').drawImage(im,0,0,c.width,c.height);var u=c.toDataURL('image/jpeg',0.8);cb({src:u,orig:f.size,size:Math.round((u.length-23)*3/4)});};im.onerror=function(){cb(null);};im.src=rd.result;};rd.onerror=function(){cb(null);};rd.readAsDataURL(f);}
function toBlob(u){var b=atob(u.split(',')[1]),a=new Uint8Array(b.length);for(var i=0;i<b.length;i++)a[i]=b.charCodeAt(i);return new Blob([a],{type:'image/jpeg'});}
function mb(n){return n>=1048576?(n/1048576).toFixed(1)+'MB':Math.max(1,Math.round(n/1024))+'KB';}
// 다 읽은 뒤 한 번만 done(빠진 장 수, 못 읽은 장 수)
function addPhotos(files,list,max,done){var fs=[].slice.call(files),n=fs.length,skip=0,fail=0;if(!n)return;
  fs.forEach(function(f){shrink(f,function(p){if(!p)fail++;else if(list.length<max)list.push(p);else skip++;if(--n===0)done(skip,fail);});});}
function phNote(skip,fail){return (skip?'5장까지만 올릴 수 있어 '+skip+'장은 빠졌어요. ':'')+(fail?'읽지 못한 사진 '+fail+'장이 있어요(아이폰 HEIC 사진은 JPG로 바꿔 올려 주세요).':'');}
function sizeLine(list){if(!list.length)return '';var o=0,s=0;list.forEach(function(p){o+=p.orig;s+=p.size;});return '사진 '+list.length+'장 · 원본 '+mb(o)+' → 올리는 크기 <b>'+mb(s)+'</b>';}
// 미리보기(지울 수 있음)
function thumbsEdit(list){return list.map(function(p,i){return '<span style="position:relative"><button type="button" class="ph" style="background-image:url('+p.src+')" data-src="'+i+'" aria-label="사진 크게 보기"></button><button type="button" data-rm="'+i+'" aria-label="사진 빼기" style="position:absolute;top:-6px;right:-6px;width:20px;height:20px;border-radius:50%;border:0;background:var(--ink);color:var(--paper);font-size:12px;cursor:pointer;line-height:20px;padding:0">×</button></span>';}).join('');}
// 서버에 저장된 사진(주소 목록)
function phBox(urls,label){if(!urls||!urls.length)return '';return '<div class="phlbl">'+esc(label)+' '+urls.length+'장</div><div class="photos">'+urls.map(function(u){return '<button type="button" class="ph" style="background-image:url(\''+esc(u)+'\')" data-big="'+esc(u)+'" aria-label="사진 크게 보기"></button>';}).join('')+'</div>';}
function openLb(src){$('lbImg').src=src;$('lb').hidden=false;}
function closeLb(){$('lb').hidden=true;$('lbImg').removeAttribute('src');}
document.addEventListener('click',function(e){var b=e.target.closest('[data-big]');if(b)openLb(b.getAttribute('data-big'));});
document.addEventListener('keydown',function(e){if(e.key==='Escape'&&$('lb')&&!$('lb').hidden)closeLb();});
document.addEventListener('DOMContentLoaded',function(){if($('lb'))$('lb').onclick=closeLb;});

// 약속 시계: 다음 기한까지 남은 몫을 금색 호로
function clock(r){
  var d=r.nextDue;if(!d)return '';
  var start=r.st===0?(r.va||r.t):Math.max(r.ro||0,r.rAt||r.t),tot=Math.max(d-start,1),rem=Math.max(Math.min((d-Date.now())/tot,1),0),late=d<Date.now();
  var C=2*Math.PI*26,arc=(C*rem).toFixed(1);
  var what=r.st===0?(known(r)?'업체 1차 회신':'주관사 1차 연락'):'방문 일정 확정';
  return '<svg width="64" height="64" viewBox="0 0 64 64" aria-hidden="true"><circle cx="32" cy="32" r="26" fill="none" stroke="var(--line)" stroke-width="5"/><circle cx="32" cy="32" r="26" fill="none" stroke="'+(late?'var(--bad)':'var(--gold)')+'" stroke-width="5" stroke-linecap="round" stroke-dasharray="'+arc+' '+C.toFixed(1)+'" transform="rotate(-90 32 32)"/></svg>'
    +'<div><div class="sm">'+esc(what)+(late?' 기한 지남 · 주관사가 직접 연락합니다':'까지')+'</div><div class="big">'+esc(dur(d-Date.now()))+(late?' 지남':' 남음')+'</div><div class="sm">'+esc(fmt(d))+' 기한</div></div>';
}
function clockBox(r){return r.nextDue?'<div class="clock" data-no="'+esc(r.no)+'">'+clock(r)+'</div>':'';}
function tl(r){
  var nv=r.needVisit;
  var rows=[
    {lb:'요청 접수',ds:(known(r)?r.vend+' · 주관사 담당자':'주관사 담당자')+'에게 바로 문자 알림',when:fmt(r.t),on:1},
    {lb:r.build?'시공사 전달':'1차 연락',ds:r.build?'주관사가 내용을 정리해 시공사 하자 창구에 전달하고 연락드림':(known(r)?'업체가 연락드립니다. 기한 안에 연락이 없으면 주관사가 직접 연락':'주관사가 계약 업체를 확인해 연결하고 연락드림'),when:r.rAt?fmt(r.rAt):fmt(r.replyDue)+'까지',on:r.st>=1},
    {lb:r.build?'시공사 처리 확인':(nv?'방문 일정 확정':'처리 진행'),ds:r.build?'시공사 처리 상황을 주관사가 확인해 알려 드림':(nv?(r.visit?'방문 '+r.visit:'통화로 협의한 날로 방문 날짜 확정'):'요청하신 내용을 업체 · 주관사가 처리해 안내드림'),when:r.vAt?fmt(r.vAt):(nv&&r.st<2?fmt(r.visitDue)+'까지':''),on:r.st>=2},
    {lb:'처리 완료',ds:r.hcAt?'주관사 해피콜로 해결 확인 · 마감':(r.center?'처리 뒤 주관사가 해피콜로 해결 여부를 확인하고 마감':(r.confirm===1?'입주민 해결 확인':'처리 뒤 입주민이 \'해결됐어요\'를 눌러 마감')),when:r.dAt?fmt(r.dAt):'',on:r.st>=3}];
  var cur=Math.min(r.st+1,3);
  return rows.map(function(x,i){return '<li class="'+(x.on?'on':(i===cur?'now':''))+'"><span class="dot"></span><div><div class="lb">'+esc(x.lb)+'</div><div class="ds">'+esc(x.ds)+'</div></div><div class="when">'+esc(x.when)+'</div></li>';}).join('');
}
function chipGroup(el,vals,multi,onPick,labels){
  el.innerHTML=vals.map(function(c,i){return '<button type="button" aria-pressed="false" data-v="'+esc(c)+'">'+esc(c)+(labels&&labels[i]?'<span class="tip">'+esc(labels[i])+'</span>':'')+'</button>';}).join('');
  el.onclick=function(e){var b=e.target.closest('button');if(!b)return;
    if(multi)b.setAttribute('aria-pressed',b.getAttribute('aria-pressed')!=='true');
    else [].forEach.call(el.children,function(x){x.setAttribute('aria-pressed',x===b);});
    onPick(b.getAttribute('data-v'));};
}
function pickChip(el,v){[].forEach.call(el.children,function(x){x.setAttribute('aria-pressed',x.getAttribute('data-v')===String(v));});}
// 30초마다 시계 다시 그림(목록은 각 화면이 r을 window.ROWS에 둠)
setInterval(function(){[].forEach.call(document.querySelectorAll('.clock[data-no]'),function(c){var r=(window.ROWS||{})[c.getAttribute('data-no')];if(r)c.innerHTML=clock(r);});},30000);

// 업체 화면: 연락했어요 → 방문 일정 확정 → 처리 완료(완료 사진) · 10분 안 되돌리기
(function(){
'use strict';
var TOK=new URLSearchParams(location.search).get('t')||'',R=null,VDONE=[],UNDO_MIN=10;
window.ROWS={};
function load(){api('v_get',null,{t:TOK}).then(function(j){if(!j.ok){$('vCard').innerHTML='<div class="note warn" style="margin-top:12px">'+esc(j.msg)+'</div>';return;}R=j.t;window.ROWS[R.no]=R;render();});}
function editing(){var b=$('vCard');if(b.contains(document.activeElement)&&/INPUT|TEXTAREA/.test(document.activeElement.tagName))return true;return [].some.call(b.querySelectorAll('input:not([type=file])'),function(x){return x.value;})||VDONE.length>0;}
function render(note){
  var r=R,d=r.nextDue,late=d&&d<Date.now(),act='',h=r.last;
  if(r.rw&&r.st<3)act+='<div class="note warn">입주민이 다시 요청했어요: '+esc(r.rw)+'</div>';
  if(r.st===0)act+='<div class="btnrow"><button class="btn" type="button" data-v="reply">고객에게 연락했어요 (1차 회신)</button></div>';
  if(r.st<=1&&r.needVisit)act+='<div class="lbl">통화로 정한 방문 날짜 · 시간</div><div class="inl"><input id="vWhen" placeholder="예) 11.05(목) 14:00" maxlength="60"><button class="btn" type="button" data-v="visit">방문 일정 확정</button></div>';
  if(r.st<=2)act+='<div class="lbl">처리 내용 · 완료 사진(선택)</div><label class="addph sm" for="vDonePh" tabindex="0" role="button">＋ 완료 사진</label><input type="file" id="vDonePh" accept="image/*" multiple hidden><div id="vDonePrev" class="photos">'+thumbsEdit(VDONE)+'</div><div class="inl"><input id="vNote" placeholder="예) 경첩 조정 · 부품 교체" maxlength="200"><button class="ghost" type="button" data-v="done">처리 완료</button></div>';
  if(r.st===3)act+='<div class="note '+(r.confirm?'ok':'info')+'">'+(r.confirm?'마감됐습니다. 수고하셨습니다.':'처리 완료로 표시했습니다. 입주민 확인을 기다리는 중입니다.')+'</div>';
  if(h&&h.by==='업체'){var rest=UNDO_MIN*60e3-(Date.now()-h.at);
    act+=rest>0?'<div class="undo"><span>방금 누른 <b>\''+esc(h.label)+'\'</b> 버튼을 잘못 눌렀나요? '+esc(dur(rest))+' 안에 되돌릴 수 있어요.</span><button class="ghost sm" type="button" data-v="undo">되돌리기</button></div>'
      :'<div class="undo"><span>\''+esc(h.label)+'\' 버튼을 누른 지 '+UNDO_MIN+'분이 지났습니다. 잘못 눌렀다면 주관사에 알려 주세요. 주관사가 되돌립니다.</span></div>';}
  $('vCard').innerHTML='<div class="item" style="margin-top:12px"><div class="eyebrow ko" style="margin-bottom:4px">'+esc(r.vend)+' 전용 링크</div><div class="top2"><span class="mono">'+esc(r.no)+'</span><span class="pill '+(late?'pl':PC[r.st])+'">'+esc(late?'기한 지남':r.stage)+'</span></div>'
    +(note?'<div class="note warn">'+esc(note)+'</div>':'')+clockBox(r)
    +'<dl class="kv"><dt>단지</dt><dd>'+esc(r.dj)+'</dd><dt>동 · 호</dt><dd>'+esc(r.dh)+'</dd><dt>성함</dt><dd>'+esc(r.nm)+'</dd><dt>연락처</dt><dd class="mono"><a href="tel:'+esc(r.tel.replace(/\D/g,''))+'" style="color:inherit">'+esc(r.tel)+'</a></dd><dt>품목</dt><dd>'+esc(r.item)+' · '+esc(r.cat)+'</dd><dt>입주민 사유</dt><dd>'+esc(r.vc||'—')+'</dd><dt>내용</dt><dd>'+esc(r.body)+'</dd><dt>방문 시간</dt><dd>'+esc(r.slot)+'</dd></dl>'
    +(r.photos.req.length?phBox(r.photos.req,'입주민 사진'):'<div class="phlbl">입주민 사진 없음</div>')+phBox(r.photos.done,'완료 사진')
    +act+'<p class="legend">마감되고 30일이 지나면 이 링크는 닫힙니다.</p></div>';
}
$('vCard').onchange=function(e){if(e.target.id!=='vDonePh')return;addPhotos(e.target.files,VDONE,5,function(sk,fl){$('vDonePrev').innerHTML=thumbsEdit(VDONE)+(sk||fl?'<div class="phsize" style="color:var(--warn)">'+esc(phNote(sk,fl))+'</div>':'');});e.target.value='';};
$('vCard').onkeydown=function(e){if(e.target.getAttribute('for')==='vDonePh'&&(e.key==='Enter'||e.key===' ')){e.preventDefault();$('vDonePh').click();}};
$('vCard').onclick=function(e){
  var rm=e.target.closest('#vDonePrev [data-rm]');if(rm){VDONE.splice(+rm.getAttribute('data-rm'),1);$('vDonePrev').innerHTML=thumbsEdit(VDONE);return;}
  var sb=e.target.closest('#vDonePrev [data-src]');if(sb){openLb(VDONE[+sb.getAttribute('data-src')].src);return;}
  var b=e.target.closest('button[data-v]');if(!b||!R)return;var a=b.getAttribute('data-v'),fd=new FormData();fd.append('t',TOK);fd.append('act',a);
  if(a==='visit'){var w=$('vWhen').value.trim();if(!w){need($('vWhen'),'통화로 정한 날짜 · 시간을 적어 주세요');return;}fd.append('when',w);}
  if(a==='done'){fd.append('note',$('vNote').value.trim());VDONE.forEach(function(p,i){fd.append('photos[]',toBlob(p.src),'done'+i+'.jpg');});}
  b.disabled=true;
  api('v_act',fd).then(function(j){b.disabled=false;if(!j.ok){render(j.msg);return;}if(a==='done')VDONE=[];R=j.t;window.ROWS[R.no]=R;render();});
};
// 30초마다 다시 불러옴(입력 중이면 건너뜀) · 되돌리기 남은 시간도 이때 바뀜
setInterval(function(){if(R&&!editing())load();},30000);
load();
})();

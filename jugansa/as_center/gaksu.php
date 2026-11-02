<?php
// 특약이행각서(참여업체 하자보수 · 사후관리 이행) 인쇄 화면: 단지 · 상호 · 품목만 채움.
// 날인은 업체가 인쇄본에 직접 한다(시스템은 도장 이미지를 만들거나 찍지 않음). ?t=업체 전용 토큰 · 주관사는 로그인 뒤 ?id=
require __DIR__ . '/lib/boot.php';
require __DIR__ . '/lib/recruit.php';
if (!installed()) { http_response_code(404); exit; }
header('X-Frame-Options: SAMEORIGIN');
header('Referrer-Policy: no-referrer');
header('Cache-Control: private, no-store');
$a = null;
if (!empty($_GET['t']) && strlen((string)$_GET['t']) >= 16) $a = rc_app('a.token=?', [(string)$_GET['t']]);
elseif (!empty($_GET['id'])) { require __DIR__ . '/lib/admin_api.php'; adm_session(); if (!empty($_SESSION['adm'])) $a = rc_app('a.id=?', [(int)$_GET['id']]); }
if (!$a || (int)$a['stage'] === 9) { http_response_code(404); header('Content-Type: text/plain; charset=utf-8'); exit('링크가 맞지 않습니다.'); }
$dj = $a['dname']; $b = digits($a['biz_no']); $bz = strlen($b) === 10 ? substr($b, 0, 3) . '-' . substr($b, 3, 2) . '-' . substr($b, 5) : $b;
$ARTS = [
  ['하자보수 이관 의무', '업체는 관련 법령 및 계약에 따른 하자보수 이관 의무를 성실히 이행한다.'],
  ['이관 대상', '설비·마감공사 등 업체가 시공·납품한 품목에서 입주민 하자가 발생하면 계약서에 명시한 보수 범위에 따라 보수한다.'],
  ['하자 통보', '하자 통보와 회신은 서면(내용증명·전자문서를 포함한다)으로 하며, 접수 및 처리의 근거를 남긴다.'],
  ['계약 해지', '업체 사정으로 계약을 해지하는 경우 중도 정산을 하고, 잔여 권리에 대한 포기 각서를 제출한다.'],
  ['보증 기간', '하자 접수 기간은 시공·납품 완료일부터 최소 2년으로 하며, 그 기간 동안 보증 책임과 조치 의무를 진다.'],
  ['연대 책임', '업체가 폐업·도산하는 경우 별도 계약 없이도 주관사 또는 주관사가 지정한 동종업체의 하자보수 승계를 승인한다.'],
  ['지연 배상', '하자보수 비용의 지급 기한을 지키지 않으면 지연배상금을 지급하며, 그로 인하여 발생한 손해를 배상한다.'],
  ['민원 처리', '입주민 민원이 발생하면 즉시 처리하고, 그 결과를 주관사 및 입주예정자협의회에 보고한다.'],
  ['주관사 이관 동의', '업체의 도산·연락 두절 등으로 하자보수가 불가능한 경우, 주식회사 엣지컴퍼니의 사후관리·하자보수 이관 및 그 비용의 구상에 동의한다.'],
];
?><!doctype html>
<html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>특약이행각서 · <?= h($a['company']) ?></title><meta name="robots" content="noindex">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Nanum+Myeongjo:wght@400;700;800&display=swap">
<style>
@page{size:A4;margin:16mm 16mm 14mm}
*{box-sizing:border-box}
body{margin:0;background:#e9e4dc;font-family:"Nanum Myeongjo","Batang","바탕",serif;color:#111}
.bar{position:sticky;top:0;background:#1f1b18;color:#f3ebdd;padding:10px 16px;font-family:"Malgun Gothic",sans-serif;font-size:14px;display:flex;gap:10px;align-items:center;flex-wrap:wrap}
.bar button{font:inherit;font-weight:700;border:0;border-radius:8px;padding:8px 14px;background:#c99a52;color:#1f1b18;cursor:pointer}
.pg{width:210mm;min-height:297mm;margin:16px auto;background:#fff;padding:16mm 16mm 14mm;box-shadow:0 6px 20px rgba(0,0,0,.12)}
h1{text-align:center;font-size:30px;letter-spacing:.6em;margin:0 0 18px;padding-left:.6em}
table{width:100%;border-collapse:collapse;font-size:13.5px}
td{border:1px solid #111;padding:7px 10px;height:34px}
td.h{width:19%;text-align:center;letter-spacing:.2em;background:#fafafa}
p{font-size:13.5px;line-height:1.75;margin:10px 0}
.art{margin:6px 0;font-size:13.5px;line-height:1.7}
.c{text-align:center}
.sig{margin:18px 0 0 38%;font-size:14px;line-height:2.1}
.sig span{display:inline-block;width:92px;letter-spacing:.3em}
.to{text-align:center;font-size:19px;margin-top:22px;line-height:1.6}
@media print{body{background:#fff}.bar{display:none}.pg{margin:0;box-shadow:none;padding:0;width:auto;min-height:0}}
</style></head><body>
<div class="bar">인쇄(또는 'PDF로 저장')한 뒤 대표자 칸에 <b>법인인감(또는 사용인감)</b>을 직접 찍고, 스캔 · 사진을 업체 전용 링크에서 올려 주세요. <button type="button" onclick="window.print()">인쇄 · PDF로 저장</button></div>
<div class="pg">
  <h1>특약이행각서</h1>
  <table>
    <tr><td class="h">상호</td><td><?= h($a['company']) ?></td><td class="h">대표자</td><td><?= h($a['ceo']) ?></td></tr>
    <tr><td class="h">사업자등록번호</td><td><?= h($bz) ?></td><td class="h">참여 품목</td><td><?= h($a['item']) ?></td></tr>
    <tr><td class="h">주소</td><td colspan="3"><?= h((string)$a['addr']) ?></td></tr>
    <tr><td class="h">건명</td><td colspan="3"><?= h($dj) ?> 입주박람회 참여업체 하자보수 · 사후관리 이행</td></tr>
  </table>
  <p>당사는 <?= h($dj) ?> 입주박람회(이하 “박람회”)에 참여업체로 참가함에 있어, 박람회를 통하여 입주예정자와 체결한 공동구매 계약의 하자보수 및 사후관리에 관하여 아래 사항을 성실히 이행할 것을 각서합니다.</p>
  <p class="c">- 아 래 -</p>
  <?php foreach ($ARTS as $i => $x): ?><div class="art">제<?= $i + 1 ?>조(<?= h($x[0]) ?>) <?= h($x[1]) ?></div><?php endforeach; ?>
  <p>당사는 위 사항을 위반하는 경우 입주예정자협의회의 승인에 따른 참여 자격 박탈 · 계약 이관 · 손해배상 등 어떠한 조치에도 이의를 제기하지 않겠습니다.</p>
  <p class="c">위 사항을 성실히 이행할 것을 각서합니다.</p>
  <p class="c" style="letter-spacing:.4em">20&nbsp;&nbsp;&nbsp;&nbsp;년&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;월&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;일</p>
  <div class="sig"><span>각서인</span><br><span>상호</span><?= h($a['company']) ?><br><span>사업자번호</span><?= h($bz) ?><br><span>대표자</span><?= h($a['ceo']) ?>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;(인)</div>
  <p style="margin-top:18px">붙임 1. 사업자등록증 사본 1부.<br>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;2. 공동구매 계약서 사본 1부. 끝.</p>
  <div class="to">주식회사 엣지컴퍼니 대표이사 귀하<br>(<?= h($dj) ?> 입주예정자협의회 귀중)</div>
</div>
</body></html>

<?php
// 업체 화면: 문자로 받은 링크(?t=토큰) 하나로 요청 1건만 봄 · 로그인 없음
require __DIR__ . '/lib/boot.php';
if (!installed()) { http_response_code(503); exit('준비 중입니다.'); }
header('X-Frame-Options: DENY');
header('Referrer-Policy: no-referrer');
?><!doctype html>
<html lang="ko"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>업체 처리 화면 · 엣지컴퍼니 A/S</title>
<meta name="robots" content="noindex">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@500;600;700&family=Nanum+Myeongjo:wght@700;800&family=Noto+Sans+KR:wght@400;500;700;800&display=swap">
<link rel="stylesheet" href="assets/app.css?v=1">
</head><body>
<header class="hd"><div class="wrap"><div class="top" style="border-bottom:0">
  <div class="logo" aria-label="엣지컴퍼니"><span class="mark">E</span><span class="wm"><b>엣지컴퍼니</b><span>공동구매 주관사 · 업체 처리 화면</span></span></div>
</div></div></header>
<div class="wrap"><main style="padding-top:16px">
  <div class="note gold" style="max-width:620px;margin-top:0">고객에게 연락한 뒤 버튼을 눌러 주세요. 누르면 기록이 남고 고객에게 안내 문자가 갑니다. 잘못 누른 버튼은 <b>10분 안에 직접 되돌릴 수 있고</b>, 그 뒤에는 주관사에 알려 주시면 주관사가 되돌립니다.</div>
  <div id="vCard" style="max-width:620px"></div>
</main></div>
<div class="zoom" id="lb" hidden><img id="lbImg" alt="사진 크게 보기"></div>
<footer><div class="wrap"><div class="wm2">엣지컴퍼니</div><?= h(cfg('company', '㈜엣지컴퍼니')) ?> · 공동구매 주관사 · <?= h(cfg('contact_email', '')) ?> · 고객 정보는 A/S 처리에만 쓰고, 다른 곳에 옮기거나 보관하지 마세요.</div></footer>
<script src="assets/common.js?v=1"></script>
<script src="assets/vendor.js?v=1"></script>
</body></html>

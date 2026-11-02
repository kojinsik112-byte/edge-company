<?php
// 업체 전용 링크(모집 신청 뒤 문자로 받음): 진행 상황 · 서류 보완 · 선정 뒤 특약이행각서 확인 · 날인본 올리기
require __DIR__ . '/lib/boot.php';
if (!installed()) { header('Location: install.php'); exit; }
header('X-Frame-Options: DENY');
header('Referrer-Policy: no-referrer');
?><!doctype html>
<html lang="ko"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>참여업체 전용 · 엣지컴퍼니</title>
<meta name="robots" content="noindex">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@500;600;700&family=Nanum+Myeongjo:wght@700;800&family=Noto+Sans+KR:wght@400;500;700;800&display=swap">
<link rel="stylesheet" href="assets/app.css?v=1">
<style>.dt{width:100%;border-collapse:collapse;font-size:14px;margin-top:8px}.dt td,.dt th{border-bottom:1px solid var(--hair);padding:8px 6px;text-align:left;vertical-align:top}.ok2{color:var(--ok);font-weight:700}.no2{color:var(--warn);font-weight:700}.terms{padding-left:20px;line-height:1.8;margin:6px 0 0}.req{color:var(--bad)}</style>
</head><body>
<header class="hd"><div class="wrap"><div class="top" style="border-bottom:0"><div class="logo" aria-label="엣지컴퍼니"><span class="mark">E</span><span class="wm"><b>엣지컴퍼니</b><span>공동구매 주관사 · 참여업체 전용</span></span></div></div></div></header>
<div class="wrap"><main>
  <div class="note warn" id="noA" hidden style="margin-top:22px"></div>
  <div id="pCard"></div>
</main></div>
<footer><div class="wrap"><div class="wm2">엣지컴퍼니</div><?= h(cfg('company', '㈜엣지컴퍼니')) ?> · 공동구매 주관사 · <?= h(cfg('contact_email', '')) ?> · 이 링크는 신청 업체 전용입니다. 다른 사람에게 보내지 마세요.</div></footer>
<script src="assets/common.js?v=3"></script>
<script src="assets/recruit.js?v=1"></script>
</body></html>

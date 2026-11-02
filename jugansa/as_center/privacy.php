<?php
// 개인정보 처리방침(입주민 화면 아래 링크). 보호책임자는 config.php의 privacy_officer를 채워야 함.
require __DIR__ . '/lib/boot.php';
$o = cfg('privacy_officer', []);
$co = cfg('company', '㈜엣지컴퍼니');
$officer = trim(($o['title'] ?? '') . ' ' . ($o['name'] ?? ''));
?><!doctype html>
<html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>개인정보 처리방침 · 엣지컴퍼니 A/S 도움 창구</title>
<link rel="stylesheet" href="assets/app.css?v=1">
<style>.pp{max-width:720px}.pp h3{font-family:var(--f-kserif);font-size:17px;margin:22px 0 6px}.pp p,.pp li{font-size:14.5px}.pp table{border-collapse:collapse;width:100%;font-size:14px}.pp td,.pp th{border:1px solid var(--line);padding:8px;text-align:left;vertical-align:top}</style>
</head><body>
<header class="hd"><div class="wrap"><div class="top" style="border-bottom:0"><div class="logo"><span class="mark">E</span><span class="wm"><b>엣지컴퍼니</b><span>A/S 도움 창구 · 개인정보 처리방침</span></span></div></div></div></header>
<div class="wrap"><main class="pp">
<p><?= h($co) ?>(이하 '회사')는 공동구매 품목 A/S 도움 창구를 운영하면서 입주민의 개인정보를 아래와 같이 처리합니다.</p>
<h3>1. 처리 목적</h3><p>공동구매 품목의 A/S · 불편사항 접수와 처리, 계약 업체 확인과 연결, 진행 안내 문자 발송, 아파트 자체 하자의 시공사 전달.</p>
<h3>2. 처리 항목</h3><p>동 · 호수, 성함, 휴대폰 번호, 요청 내용, 첨부 사진, 접속 기록(인터넷 주소). 사진은 올리기 전에 휴대폰에서 줄이고, 서버에서 다시 저장하면서 사진 속 위치 정보 등을 지웁니다.</p>
<h3>3. 보유 기간</h3><p>단지별 협약에서 정한 기간(보통 공동구매 품목 무상 A/S 기간이 끝날 때까지) 동안 보관하고, 기간이 끝나면 자동으로 지웁니다. 단지별 기간은 각 단지 안내문과 접수 화면의 동의 문구에 표시합니다.</p>
<h3>4. 제3자 제공</h3>
<table><tr><th>받는 곳</th><th>항목</th><th>목적</th><th>보유 기간</th></tr>
<tr><td>입주민이 계약한 공동구매 업체</td><td>동 · 호수, 성함, 연락처, 요청 내용, 사진</td><td>방문 일정 조율 · A/S 처리</td><td>처리가 끝나고 30일(업체 화면 링크가 닫힘)</td></tr>
<tr><td>업체를 모르실 때 같은 품목 업체</td><td>동 · 호수</td><td>계약 여부 확인</td><td>확인이 끝날 때까지</td></tr>
<tr><td>시공사 하자 접수 창구(아파트 자체 하자만)</td><td>동 · 호수, 성함, 연락처, 요청 내용, 사진</td><td>하자 전달 · 처리 확인</td><td>시공사 하자 처리 기준</td></tr></table>
<h3>5. 처리 위탁</h3><p>㈜가비아 — 서버 보관(웹호스팅) · 문자 발송.</p>
<h3>6. 파기</h3><p>보유 기간이 끝난 요청은 성함 · 연락처 · 내용 · 사진을 지우고, 처리 건수 같은 통계만 남깁니다.</p>
<h3>7. 정보주체의 권리</h3><p>본인의 개인정보 열람 · 정정 · 삭제 · 처리 정지를 요청할 수 있습니다. 아래 보호책임자에게 연락하시면 지체 없이 처리합니다.</p>
<h3>8. 안전성 확보 조치</h3><p>보안 연결(https), 관리자 계정 비밀번호 암호화 저장, 관리자만 볼 수 있는 화면과 접속 기록 보관, 업체 · 입주민 링크마다 다른 긴 주소 사용, 사진 폴더 외부 접근 차단.</p>
<h3>9. 개인정보 보호책임자</h3><p><?= $officer !== '' ? h($officer) : '<b style="color:var(--bad)">(config.php의 privacy_officer를 채워 주세요)</b>' ?><?= !empty($o['phone']) ? ' · ' . h($o['phone']) : '' ?><?= !empty($o['email']) ? ' · ' . h($o['email']) : '' ?></p>
<h3>10. 시행일</h3><?php $inst = installed() ? meta_get('installed') : null; ?><p><?= h($inst ? substr($inst, 0, 10) : date('Y-m-d')) ?></p>
</main></div>
</body></html>

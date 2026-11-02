<?php
// 업체 모집 공고 · 신청: ?r=모집코드(관리 페이지 '업체 모집'에서 만든 링크 · QR)
require __DIR__ . '/lib/boot.php';
if (!installed()) { header('Location: install.php'); exit; }
header('X-Frame-Options: DENY');
header('Referrer-Policy: same-origin');
?><!doctype html>
<html lang="ko"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>입주박람회 참여업체 모집 · 엣지컴퍼니</title>
<meta name="robots" content="noindex">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@500;600;700&family=Nanum+Myeongjo:wght@700;800&family=Noto+Sans+KR:wght@400;500;700;800&display=swap">
<link rel="stylesheet" href="assets/app.css?v=1">
<style>.terms{margin:8px 0 0;padding-left:20px;line-height:1.8}.terms li{margin:2px 0}.itab{width:100%;border-collapse:collapse;font-size:14px;margin-top:8px}.itab td,.itab th{border-bottom:1px solid var(--hair);padding:8px 6px;text-align:left}.fl{display:flex;flex-direction:column;gap:6px;margin-top:10px}.fl .one{display:flex;gap:8px;align-items:center;flex-wrap:wrap;font-size:14px}.fl .one b{min-width:150px}.req{color:var(--bad)}</style>
</head><body>
<header class="hd"><div class="wrap">
  <div class="top"><div class="logo" aria-label="엣지컴퍼니"><span class="mark">E</span><span class="wm"><b>엣지컴퍼니</b><span>공동구매 주관사 · 참여업체 모집</span></span></div><span class="djtag" id="djName" hidden></span></div>
  <div class="hero">
    <div class="eyebrow ko">입주박람회 참여업체 공개 모집</div>
    <h1>입주민과의 약속을 함께 지킬<br><em>참여업체를 공개 모집합니다.</em></h1>
    <p class="sub">신청서와 서류를 올리면 서류 확인 → 세부 심사 → 입주예정자협의회 선정 → 특약이행각서 확인 순서로 참여가 확정됩니다. 결과는 담당 휴대폰 문자로 알려 드립니다.</p>
  </div>
</div></header>

<div class="wrap">
  <div class="note warn" id="noRc" hidden style="margin-top:22px"></div>
  <main id="app" hidden>
    <div class="sec">
      <div class="h2"><span class="k">01</span><b>모집 품목 · 마감</b></div>
      <p class="lead" id="intro"></p>
      <table class="itab"><thead><tr><th>품목</th><th>모집 업체 수</th></tr></thead><tbody id="items"></tbody></table>
      <div class="note info" id="dl"></div>
    </div>
    <div class="sec" style="margin-top:14px">
      <div class="h2"><span class="k">02</span><b>참여 조건</b></div>
      <ol class="terms" id="terms"></ol>
    </div>

    <form class="form" id="fm" novalidate style="margin-top:14px">
      <input type="text" name="website" id="website" tabindex="-1" autocomplete="off" style="position:absolute;left:-9999px;width:1px;height:1px" aria-hidden="true">
      <div class="sec">
        <div class="h2"><span class="k">03</span><b>신청서</b></div>
        <label class="f">신청 품목 <span class="req">*</span><select id="item"></select></label>
        <div class="row" style="margin-top:10px"><label class="f">상호 <span class="req">*</span><input id="company" maxlength="100"></label><label class="f">사업자등록번호 <span class="req">*</span><input id="biz" inputmode="numeric" maxlength="12" placeholder="000-00-00000"></label></div>
        <div class="row" style="margin-top:10px"><label class="f">대표자 <span class="req">*</span><input id="ceo" maxlength="50"></label><label class="f">사업장 주소<input id="addr" maxlength="200"></label></div>
        <div class="row" style="margin-top:10px"><label class="f">담당자<input id="person" maxlength="50"></label><label class="f">담당 휴대폰 <span class="req">*</span><input id="phone" inputmode="tel" maxlength="13" placeholder="010-0000-0000"></label></div>
        <div class="row" style="margin-top:10px"><label class="f">이메일(선택)<input id="email" type="email" maxlength="100"></label><label class="f">취급 품목 · 주력 상품<input id="tag" maxlength="100" placeholder="예) 3연동 중문 · 스윙도어"></label></div>
        <label class="f" style="margin-top:10px">회사 소개 · 시공 실적(선택)<textarea id="intro2" maxlength="1000" placeholder="예) 2019년 개업 · 최근 3년 아파트 12개 단지 납품 · A/S 전담 2명"></textarea></label>
      </div>
      <div class="sec" style="margin-top:14px">
        <div class="h2"><span class="k">04</span><b>서류 올리기</b></div>
        <p class="lead">PDF · 사진(JPG · PNG) · 엑셀 · 한글 · 워드, 한 파일 20MB까지. 빠진 서류는 신청 뒤 문자로 받은 링크에서 보완할 수 있습니다.</p>
        <div class="fl" id="docs"></div>
      </div>
      <div class="sec" style="margin-top:14px">
        <div class="agree">
          <label><input type="checkbox" id="a1"> [필수] 개인정보(담당자 이름 · 휴대폰 · 이메일) 수집 · 이용 동의 — 모집 · 심사 · 결과 안내 · 참여 확정 뒤 A/S 연결에만 씁니다.</label>
          <label><input type="checkbox" id="a2"> [필수] 위 참여 조건을 지키고, 선정되면 특약이행각서(하자보수 · 사후관리 이행)를 내겠습니다.</label>
        </div>
        <div class="err" id="err" role="alert"></div>
        <button class="btn wide" type="submit" id="go">신청하기</button>
      </div>
    </form>
    <div class="receipt" id="done" hidden>
      <div class="eyebrow ko">신청 접수</div>
      <div class="no" id="doneNo"></div>
      <div class="note ok">담당 휴대폰으로 접수 문자를 보냈어요. 문자 속 링크에서 진행 상황을 보고 서류를 보완할 수 있어요.</div>
      <div class="note warn" id="doneMiss" hidden></div>
      <div class="btnrow"><a class="btn" id="doneLink" href="#" style="text-decoration:none">진행 확인 · 서류 보완</a></div>
    </div>
  </main>
</div>
<footer><div class="wrap"><div class="wm2">엣지컴퍼니</div><?= h(cfg('company', '㈜엣지컴퍼니')) ?> · 공동구매 주관사 · <?= h(cfg('contact_email', '')) ?> · <a href="privacy.php" style="color:inherit">개인정보 처리방침</a></div></footer>
<script src="assets/common.js?v=3"></script>
<script src="assets/recruit.js?v=1"></script>
</body></html>

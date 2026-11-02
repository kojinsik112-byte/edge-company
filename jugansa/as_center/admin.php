<?php
// 주관사 관리 페이지(로그인): 요청 관리 · 단지 · 업체 · 문자 기록 · 설정
require __DIR__ . '/lib/boot.php';
if (!installed()) { header('Location: install.php'); exit; }
header('X-Frame-Options: DENY');
header('Referrer-Policy: same-origin');
header('Cache-Control: no-store');
?><!doctype html>
<html lang="ko"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>주관사 관리 · 엣지컴퍼니 A/S</title>
<meta name="robots" content="noindex">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@500;600;700&family=Nanum+Myeongjo:wght@700;800&family=Noto+Sans+KR:wght@400;500;700;800&display=swap">
<link rel="stylesheet" href="assets/app.css?v=1">
<link rel="stylesheet" href="assets/admin.css?v=1">
</head><body>
<header class="hd"><div class="wrap"><div class="top" style="border-bottom:0">
  <div class="logo" aria-label="엣지컴퍼니"><span class="mark">E</span><span class="wm"><b>엣지컴퍼니</b><span>공동구매 주관사 · A/S 관리</span></span></div>
  <span class="djtag" id="who" hidden></span>
</div></div></header>

<div class="wrap">
  <!-- 로그인 -->
  <form id="login" class="sec loginbox" hidden novalidate>
    <div class="h2"><span class="k">관리</span><b>주관사 담당자 로그인</b></div>
    <label class="f">아이디<input id="lId" autocomplete="username"></label>
    <label class="f" style="margin-top:10px">비밀번호<input id="lPw" type="password" autocomplete="current-password"></label>
    <div class="err" id="lErr" role="alert"></div>
    <button class="btn wide" type="submit">로그인</button>
    <div class="hint">2시간 동안 쓰지 않으면 자동으로 로그아웃됩니다.</div>
  </form>

  <div id="app" hidden>
    <nav class="tabs" role="tablist">
      <button role="tab" id="t-req" data-v="req">요청 관리</button>
      <button role="tab" id="t-dj" data-v="dj">단지 · 업체</button>
      <button role="tab" id="t-sms" data-v="sms">문자 기록</button>
      <button role="tab" id="t-set" data-v="set">설정</button>
      <span class="sep" aria-hidden="true"></span>
      <button type="button" id="logout" class="tabbtn">로그아웃</button>
    </nav>
    <main>
      <!-- 요청 관리 -->
      <section id="v-req">
        <div class="filters">
          <label class="f">단지<select id="fDj"></select></label>
          <div class="chips" id="fSt" role="group" aria-label="상태"></div>
          <label class="f">찾기<input id="fQ" type="search" placeholder="접수번호 · 동-호 · 업체"></label>
          <a class="ghost" id="csv" href="#">보고용 엑셀(CSV)</a>
          <button class="ghost" type="button" id="notiBtn">새 요청 알림 켜기</button>
        </div>
        <div class="kpi" id="kpi" style="margin-top:14px"></div>
        <div class="tbox"><table class="adm">
          <thead><tr><th>접수번호</th><th>단지</th><th>동 · 호</th><th>품목 · 업체</th><th>업체 연락</th><th>단계</th><th>다음 기한</th><th>응대 평가</th><th></th></tr></thead>
          <tbody id="admBody"></tbody>
        </table></div>
        <div id="adDetail"></div>
        <div class="h2" style="margin-top:26px"><span class="k">업체</span><b>업체별 성적</b></div>
        <p class="lead">같은 품목에 업체가 여러 곳이면 어느 업체가 늦는지 여기서 바로 보입니다. 다음 박람회 업체 선정 때 근거로 씁니다. 주관사가 대신 연락한 건은 업체 회신 실적에서 뺍니다.</p>
        <div class="tbox" style="margin-top:0"><table class="vscore"><thead><tr><th>품목</th><th>업체</th><th>요청</th><th>기한 안 1차 회신</th><th>처리 중</th><th>기한 지남</th><th>응대 '좋았어요'</th></tr></thead><tbody id="vsBody"></tbody></table></div>
      </section>

      <!-- 단지 · 업체 -->
      <section id="v-dj" hidden>
        <div class="h2"><span class="k">단지</span><b>단지 링크 · QR · 보유 기간</b></div>
        <p class="lead">단지를 만들면 입주민용 링크와 QR이 생깁니다. 입주 안내문 · 입예협 카페 공지 · 계약서 뒷면에 넣으세요. 보유 기간 끝나는 날(무상 A/S 기간 끝)이 지나면 그 단지 요청의 개인정보와 사진을 자동으로 지웁니다.</p>
        <div id="djList"></div>
        <form id="djForm" class="sec" novalidate style="margin-top:14px">
          <div class="h2"><span class="k">추가</span><b id="djFormT">새 단지</b></div>
          <input type="hidden" id="djId">
          <div class="row"><label class="f">단지 이름<input id="djName" maxlength="100"></label><label class="f">보유 기간 끝나는 날<input id="djPurge" placeholder="예) 2030-02-28"></label></div>
          <label class="f" style="margin-top:10px">입주민 동의 화면에 보일 보유 기간 문구<input id="djKeep" maxlength="100" placeholder="예) 2030.02.28까지 보관 뒤 파기"></label>
          <label class="f" style="margin-top:10px">접수 방식<select id="djIntake"><option value="vendor">업체 먼저(업체에 먼저 연락 → 24시간 뒤 주관사에 요청)</option><option value="center">주관사 한 창구(주관사에 바로 접수 · 마감은 주관사 해피콜)</option></select></label>
          <label class="f" style="margin-top:10px">사용<select id="djActive"><option value="1">사용</option><option value="0">멈춤(링크 닫힘)</option></select></label>
          <div class="err" id="djErr"></div>
          <div class="btnrow"><button class="btn" type="submit">저장</button><button class="ghost" type="button" id="djNew">새로 쓰기</button></div>
        </form>

        <div class="h2" style="margin-top:26px"><span class="k">업체</span><b>품목별 업체</b></div>
        <p class="lead">업체 담당자 휴대폰으로 요청 문자가 갑니다. '입주민에게 보일 번호'를 비우면 담당자 휴대폰이 보입니다. 업체 이름 · 취급 품목 · 번호 뒤 4자리로 입주민이 찾습니다.</p>
        <label class="f" style="max-width:360px">단지<select id="vDj"></select></label>
        <div class="tbox"><table class="adm" style="min-width:900px"><thead><tr><th>품목</th><th>업체</th><th>취급 품목</th><th>담당자</th><th>담당 휴대폰(문자)</th><th>입주민에게 보일 번호</th><th>순서</th><th>사용</th><th></th></tr></thead><tbody id="vBody"></tbody></table></div>
        <form id="vForm" class="sec" novalidate style="margin-top:14px">
          <div class="h2"><span class="k">추가</span><b id="vFormT">새 업체</b></div>
          <input type="hidden" id="vId">
          <div class="row"><label class="f">품목<input id="vItem" maxlength="50" list="itemList" placeholder="예) 줄눈"></label><label class="f">업체 이름<input id="vCo" maxlength="100"></label></div>
          <datalist id="itemList"></datalist>
          <div class="row" style="margin-top:10px"><label class="f">취급 품목(찾기용)<input id="vTag" maxlength="100" placeholder="예) 케라폭시 · 욕실 줄눈"></label><label class="f">담당자<input id="vPerson" maxlength="50"></label></div>
          <div class="row" style="margin-top:10px"><label class="f">담당 휴대폰(문자 받을 번호)<input id="vPhone" inputmode="tel"></label><label class="f">입주민에게 보일 번호(선택)<input id="vShow" inputmode="tel"></label></div>
          <div class="row" style="margin-top:10px"><label class="f">순서(작을수록 위)<input id="vSort" inputmode="numeric" value="0"></label><label class="f">사용<select id="vActive"><option value="1">사용</option><option value="0">멈춤</option></select></label></div>
          <div class="err" id="vErr"></div>
          <div class="btnrow"><button class="btn" type="submit">저장</button><button class="ghost" type="button" id="vNew">새로 쓰기</button></div>
        </form>
      </section>

      <!-- 문자 기록 -->
      <section id="v-sms" hidden>
        <div class="note info" id="smsMode" style="margin-top:0"></div>
        <div class="tbox"><table class="adm"><thead><tr><th>보낸 시각</th><th>접수번호</th><th>받는 번호</th><th>종류</th><th>내용</th><th>결과</th></tr></thead><tbody id="smsBody"></tbody></table></div>
      </section>

      <!-- 설정 -->
      <section id="v-set" hidden>
        <div class="setgrid">
          <div class="sec"><div class="h2"><span class="k">점검</span><b>서버 · 문자 상태</b></div><div id="srv"></div>
            <div class="btnrow"><button class="ghost" type="button" id="smsTest">내 휴대폰으로 시험 문자</button></div><div class="hint" id="smsTestR"></div></div>
          <div class="sec"><div class="h2"><span class="k">공휴일</span><b>기한 계산에서 뺄 날</b></div>
            <p class="lead">한 줄에 하루씩 '2027-02-08 설날 연휴'처럼 적습니다. 주말은 따로 적지 않아도 됩니다.</p>
            <textarea id="hol" style="min-height:220px;font-family:var(--f-mono);font-size:13px"></textarea><div class="err" id="holErr"></div><div class="btnrow"><button class="btn" type="button" id="holSave">공휴일 저장</button></div></div>
          <div class="sec"><div class="h2"><span class="k">계정</span><b>주관사 담당자</b></div>
            <p class="lead">'알림'을 켜 둔 담당자 휴대폰으로 새 요청 · 기한 지남 · 다시 열림 문자가 갑니다.</p>
            <div class="tbox" style="margin-top:0"><table class="adm" style="min-width:560px"><thead><tr><th>아이디</th><th>이름</th><th>휴대폰</th><th>알림</th><th>사용</th><th></th></tr></thead><tbody id="admins"></tbody></table></div>
            <form id="adForm" novalidate style="margin-top:12px"><input type="hidden" id="aId">
              <div class="row"><label class="f">아이디(새 계정만)<input id="aLogin" autocomplete="off"></label><label class="f">이름<input id="aName"></label></div>
              <div class="row" style="margin-top:10px"><label class="f">휴대폰<input id="aPhone" inputmode="tel"></label><label class="f">비밀번호(새 계정만 · 10자 이상)<input id="aPw" type="password" autocomplete="new-password"></label></div>
              <div class="row" style="margin-top:10px"><label class="f">문자 알림<select id="aNoti"><option value="1">받음</option><option value="0">안 받음</option></select></label><label class="f">사용<select id="aAct"><option value="1">사용</option><option value="0">멈춤</option></select></label></div>
              <div class="err" id="aErr"></div><div class="btnrow"><button class="btn" type="submit">저장</button><button class="ghost" type="button" id="aNew">새로 쓰기</button></div></form></div>
          <div class="sec"><div class="h2"><span class="k">비밀번호</span><b>내 비밀번호 바꾸기</b></div>
            <form id="pwForm" novalidate><label class="f">지금 비밀번호<input id="pCur" type="password" autocomplete="current-password"></label><label class="f" style="margin-top:10px">새 비밀번호(10자 이상)<input id="pNew" type="password" autocomplete="new-password"></label>
              <div class="err" id="pErr"></div><div class="btnrow"><button class="btn" type="submit">바꾸기</button></div></form></div>
        </div>
      </section>
    </main>
  </div>
</div>
<div class="zoom" id="lb" hidden><img id="lbImg" alt="사진 크게 보기"></div>
<footer><div class="wrap"><div class="wm2">엣지컴퍼니</div>관리 페이지에서 본 입주민 정보는 A/S 처리에만 씁니다. 화면을 본 기록(접속 기록)이 남습니다.</div></footer>
<script src="https://cdnjs.cloudflare.com/ajax/libs/qrcodejs/1.0.0/qrcode.min.js"></script>
<script src="assets/common.js?v=3"></script>
<script src="assets/admin.js?v=3"></script>
</body></html>

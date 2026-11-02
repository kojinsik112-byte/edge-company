<?php
// 입주민 화면: ?d=단지코드(안내문 QR) · ?d=단지코드&k=요청토큰(문자 링크 → 진행 확인 바로 열림)
require __DIR__ . '/lib/boot.php';
if (!installed()) { header('Location: install.php'); exit; }
header('X-Frame-Options: DENY');
header('Referrer-Policy: same-origin');
// 단지 접수 방식에 따라 첫 화면 문구가 다름(주관사 한 창구 = 업체 연락처 탭 · '업체에 먼저 연락' 단계 없음)
$dj0 = one('SELECT intake FROM danji WHERE code=? AND active=1', [(string)($_GET['d'] ?? '')]);
$C = $dj0 && $dj0['intake'] === 'center';
?><!doctype html>
<html lang="ko"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>엣지컴퍼니 A/S 도움 창구</title>
<meta name="robots" content="noindex">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@500;600;700&family=Nanum+Myeongjo:wght@700;800&family=Noto+Sans+KR:wght@400;500;700;800&display=swap">
<link rel="stylesheet" href="assets/app.css?v=1">
</head><body>
<header class="hd">
  <div class="wrap">
    <div class="top">
      <div class="logo" aria-label="엣지컴퍼니"><span class="mark">E</span><span class="wm"><b>엣지컴퍼니</b><span>공동구매 주관사 · A/S 도움 창구</span></span></div>
      <span class="djtag" id="djName" hidden></span>
    </div>
    <div class="hero">
      <div class="eyebrow ko">공동구매 A/S 도움 창구</div>
<?php if ($C): ?>
      <h1>주관사 한 창구로 접수하시면,<br><em>업체 연락과 기한은 주관사가 챙깁니다.</em></h1>
      <p class="sub">박람회에서 계약한 품목에 문제가 생기면 업체를 찾지 않고 여기로 주관사에 접수하세요. 접수하면 계약 업체와 주관사 담당에게 바로 알림이 가고, 업체가 기한 안에 연락하지 않으면 주관사가 직접 연락합니다. 처리가 끝나면 주관사가 해피콜로 해결 여부를 확인합니다.</p>
<?php else: ?>
      <h1>업체에 먼저 연락하시고,<br><em>답이 늦으면 주관사가 나섭니다.</em></h1>
      <p class="sub">박람회에서 계약한 품목의 A/S는 계약 업체가 직접 합니다. 업체가 24시간 안에 답이 없거나 해결이 안 되면 여기로 요청하세요. 주관사가 업체를 챙기고, 업체가 답이 없으면 직접 연락해 해결될 때까지 챙깁니다.</p>
<?php endif; ?>
    </div>
  </div>
  <div class="wrap" style="padding-inline:0">
    <div class="promise">
      <div><div class="n">24<small>시간</small></div><div class="t">1차 연락</div><div class="s"><?= $C ? '업체 또는 주관사가' : '업체가 먼저, 없으면 주관사가' ?> · 주말 · 공휴일은 다음 영업일 12시까지</div></div>
      <div><div class="n">48<small>시간</small></div><div class="t">방문 일정 확정</div><div class="s">방문은 입주민과 협의한 날</div></div>
      <div><div class="n">24<small>시간</small></div><div class="t">업체 무응답 시 주관사가 직접 연락</div><div class="s"><?= $C ? '처리 뒤 주관사 해피콜로 확인하고 마감' : '해결될 때까지 주관사가 챙김' ?></div></div>
    </div>
  </div>
</header>

<div class="wrap">
  <div class="note warn" id="noDanji" hidden style="margin-top:22px"></div>
  <div id="app" hidden>
  <div class="flow" aria-label="이용 순서">
<?php if ($C): ?>
    <div><div class="k">01</div><div class="t">주관사에 접수</div><div class="s">품목 · 내용 · 사진만 남기면 돼요</div></div>
    <div><div class="k">02</div><div class="t">업체 · 주관사 담당에게 바로 알림</div><div class="s">업체가 기한 안에 연락 · 없으면 주관사가 직접</div></div>
    <div><div class="k">03</div><div class="t">처리 뒤 해피콜로 확인</div><div class="s">진행은 문자와 '진행 확인'에서</div></div>
<?php else: ?>
    <div><div class="k">01</div><div class="t">계약 업체에 직접 연락</div><div class="s">통화로 바로 방문 일정을 잡을 수 있어요</div></div>
    <div><div class="k">02</div><div class="t">답이 없거나 해결이 안 되면 요청</div><div class="s">업체 연락 24시간 뒤 · 일정이 안 맞을 때도</div></div>
    <div><div class="k">03</div><div class="t">주관사가 업체를 챙기고 직접 연락</div><div class="s">진행은 문자와 '진행 확인'에서</div></div>
<?php endif; ?>
  </div>

  <nav class="tabs" role="tablist">
    <button role="tab" id="t-vendors" data-v="vendors"<?= $C ? ' hidden' : '' ?>>① 업체 연락처</button>
    <button role="tab" id="t-req" data-v="req"><?= $C ? '① 주관사에 접수' : '② 주관사에 요청' ?></button>
    <button role="tab" id="t-check" data-v="check"><?= $C ? '② 진행 확인' : '③ 진행 확인' ?></button>
  </nav>

  <main>
    <section id="v-vendors">
      <div class="h2"><span class="k">01</span><b>먼저 계약 업체에 연락해 주세요</b></div>
      <p class="lead">품목별 선정 업체와 A/S 연락처입니다. 한 품목에 업체가 여러 곳이면 계약하신 업체로 연락하세요. 24시간 안에 답이 없거나, 해결이 안 되거나, 방문 일정이 맞지 않으면 '이 업체로 요청'을 누르세요.</p>
      <div class="vsearch"><input id="vq" type="search" placeholder="품목이나 업체 찾기 (예: 커튼)" aria-label="품목이나 업체 찾기"><span class="hint" style="margin:0">어느 업체였는지 기억이 안 나면 계약서 · 영수증 · 업체 문자를 확인하시거나, 요청할 때 '기억이 안 나요'를 고르세요. 주관사가 확인해 연결합니다.</span></div>
      <div class="vgrid" id="vgrid"></div>
    </section>

    <section id="v-req" hidden>
      <div class="steps" id="steps"></div>
      <form class="form" id="fm" novalidate>
        <input type="text" name="website" id="website" tabindex="-1" autocomplete="off" style="position:absolute;left:-9999px;width:1px;height:1px" aria-hidden="true">
        <div class="sec" data-step="1">
          <div class="h2"><span class="k">01</span><b>무엇이 문제인가요</b></div>
          <div class="lbl" style="margin-top:0">아파트 자체(벽 · 창호 · 배관 · 타일 등 분양 때 시공된 부분) 하자인가요?</div>
          <div class="chips" id="build" role="group" aria-label="건설 하자 여부">
            <button type="button" data-v="no" aria-pressed="true">아니요, 공동구매 품목이에요</button>
            <button type="button" data-v="yes" aria-pressed="false">네, 아파트 자체 하자예요</button>
          </div>
          <div class="note warn" id="buildNote" hidden>아파트 자체 하자는 <b>시공사 하자 접수 창구</b>에서 판정 · 보수합니다. 여기에 남기시면 주관사가 내용을 정리해 시공사에 전달하고 진행 상황을 확인해 드립니다.</div>
          <div id="itemBox">
            <label class="f" style="margin-top:14px">품목<select id="item"></select></label>
            <label class="f" id="itemFreeWrap" hidden style="margin-top:8px">품목 직접 적기<input id="itemFree" placeholder="예) 붙박이 거울" maxlength="30"></label>
            <div id="vendBox" hidden>
              <div class="lbl">계약한 업체</div>
              <div class="chips" id="vend" role="group" aria-label="계약한 업체"></div>
              <div id="vendMany" hidden>
                <input id="vendQ" type="search" placeholder="상호 · 취급 품목 · 업체 전화 뒤 4자리" aria-label="업체 찾기">
                <div class="hint" id="vendCount"></div>
                <div class="vlist" id="vlist" role="radiogroup" aria-label="계약한 업체"></div>
                <div class="chips" style="margin-top:8px"><button type="button" id="vforgot" aria-pressed="false">기억이 안 나요</button></div>
              </div>
              <div class="hint" id="vendHint" hidden>괜찮아요. 주관사가 업체들에 확인해 계약한 곳으로 연결해 드립니다.</div>
            </div>
            <div class="lbl">구분</div>
            <div class="chips" id="cat" role="group" aria-label="구분"></div>
          </div>
        </div>

        <div class="sec" data-step="2" hidden>
          <div class="h2"><span class="k">02</span><b>업체에 먼저 연락해 보셨나요</b></div>
          <div class="chips col" id="vc" role="group" aria-label="업체 연락 여부"></div>
          <div class="note warn" id="vcNote" hidden>먼저 계약 업체에 연락해 주세요. 통화로 바로 방문 일정을 잡을 수 있어요. <button type="button" class="link" id="vcGo">업체 연락처 보기</button><br>급한 경우에는 이대로 요청하셔도 됩니다.</div>
        </div>

        <div class="sec" data-step="3" hidden>
          <div class="h2"><span class="k">03</span><b>내용 · 사진 · 방문 시간</b></div>
          <label class="f">내용 <span class="req">*</span>
            <textarea id="body" maxlength="1000" placeholder="<?= $C ? '언제부터 어떤 문제가 있는지 적어 주세요. 예) 중문이 끝까지 안 닫히고 1cm 정도 떠 있어요.' : '언제부터 어떤 문제가 있는지, 업체와 어디까지 이야기됐는지 적어 주세요. 예) 어제 중문 업체에 전화했는데 아직 답이 없어요. 중문이 끝까지 안 닫히고 1cm 정도 떠 있어요.' ?>"></textarea>
          </label>
          <div style="display:flex;justify-content:space-between;gap:8px;font-size:12px;color:var(--ink-2)"><span>사진이 있으면 미리 보고 부품 · 장비를 챙길 수 있어요</span><span id="cnt">0 / 1000</span></div>
          <label class="addph" for="phIn" tabindex="0" role="button" id="phBtn">＋ 사진 올리기 <small>최대 5장 · 휴대폰에서 줄여서 올림</small></label>
          <div class="photos" id="photos"></div>
          <div class="phsize" id="phSize"></div>
          <input type="file" id="phIn" accept="image/*" multiple hidden>
          <div class="lbl">방문 시간 (여러 개 고를 수 있어요)</div>
          <div class="chips" id="slot" role="group" aria-label="방문 시간"></div>
          <div class="hint">시간을 미리 못 박아 두면 한 집 일정 때문에 다른 집 방문까지 밀릴 수 있어, 통화로 맞춰 잡는 것을 권해 드립니다.</div>
        </div>

        <div class="sec" data-step="4" hidden>
          <div class="h2"><span class="k">04</span><b>연락받으실 곳</b></div>
          <div class="row">
            <label class="f">동 <span class="req">*</span><input id="dong" inputmode="numeric" placeholder="예) 103" maxlength="6" autocomplete="off"></label>
            <label class="f">호 <span class="req">*</span><input id="ho" inputmode="numeric" placeholder="예) 1502" maxlength="6" autocomplete="off"></label>
          </div>
          <div class="row" style="margin-top:10px">
            <label class="f">성함 <span class="req">*</span><input id="nm" placeholder="예) 김입주" maxlength="20" autocomplete="name"></label>
            <label class="f">연락처 <span class="req">*</span><input id="tel" inputmode="tel" placeholder="010-0000-0000" maxlength="13" autocomplete="tel"></label>
          </div>
          <div class="hint">적어 주신 번호로 요청 확인과 진행 안내 문자를 보내 드립니다.</div>
          <div class="agree" style="margin-top:16px">
            <label><input type="checkbox" id="a1"> [필수] 개인정보 수집 · 이용 동의</label>
            <details><summary>내용 보기</summary><table>
              <tr><td>수집 항목</td><td>동 · 호수, 성함, 연락처, 요청 내용, 사진</td></tr>
              <tr><td>이용 목적</td><td>A/S · 불편사항 처리와 진행 안내 문자</td></tr>
              <tr><td>보유 기간</td><td id="keepTxt">단지 협약에서 정한 기간이 끝나면 파기(기간은 단지 안내문에 표시)</td></tr>
              <tr><td>처리 위탁</td><td>㈜가비아(서버 보관 · 문자 발송)</td></tr>
              <tr><td>거부할 권리</td><td>동의하지 않으실 수 있으나, 그러면 요청을 처리할 수 없습니다.</td></tr></table></details>
            <label><input type="checkbox" id="a2"> [필수] 업체 · 시공사 제공 동의</label>
            <details><summary>내용 보기</summary><table>
              <tr><td>제공받는 곳</td><td>계약한 공동구매 업체 · 업체를 모르실 때는 같은 품목 업체(계약 확인용 동 · 호만) · 아파트 자체 하자는 시공사 하자 접수 창구</td></tr>
              <tr><td>제공 항목</td><td>동 · 호수, 성함, 연락처, 요청 내용, 사진</td></tr>
              <tr><td>제공 목적</td><td>방문 일정 조율 · A/S 처리 · 계약 업체 확인 · 하자 전달</td></tr>
              <tr><td>거부할 권리</td><td>동의하지 않으실 수 있으나, 그러면 업체 · 시공사에 연결할 수 없습니다.</td></tr></table></details>
            <div class="hint"><a href="privacy.php" target="_blank" rel="noopener">개인정보 처리방침 전문 보기</a></div>
          </div>
        </div>

        <div class="err" id="err" role="alert"></div>
        <div class="btnrow" style="margin-top:6px">
          <button class="ghost" type="button" id="prev" hidden>이전</button>
          <button class="btn" type="button" id="next" style="flex:1">다음</button>
          <button class="btn" type="submit" id="go" style="flex:1" hidden><?= $C ? '주관사에 접수하기' : '주관사에 요청하기' ?></button>
        </div>
      </form>

      <div class="receipt" id="done" hidden>
        <div class="eyebrow ko">요청 접수증</div>
        <div class="no" id="doneNo"></div>
        <div class="clock" id="doneClock"></div>
        <div id="donePh"></div>
        <ul class="tl" id="doneTl"></ul>
        <div class="note ok" id="doneSms">적어 주신 번호로 접수 확인 문자를 보냈어요. 문자 속 링크를 누르면 진행 상황을 바로 볼 수 있어요.</div>
        <div class="btnrow">
          <button class="ghost" type="button" id="copyNo">접수번호 복사</button>
          <button class="ghost" type="button" id="toCheck">진행 확인</button>
          <button class="ghost" type="button" id="again">새로 요청</button>
        </div>
      </div>
    </section>

    <section id="v-check" hidden>
      <form class="form" id="ck" novalidate>
        <div class="sec">
          <div class="h2"><span class="k"><?= $C ? '02' : '03' ?></span><b>진행 확인</b></div>
          <div class="row">
            <label class="f">동 · 호 또는 접수번호<input id="cDh" placeholder="예) 103-1502 또는 EC-261102-004"></label>
            <label class="f">연락처 뒤 4자리<input id="cTel" inputmode="numeric" maxlength="4" placeholder="예) 1234"></label>
          </div>
          <button class="btn wide" style="margin-top:14px" type="submit">확인하기</button>
          <div class="note info">문자로 받은 링크를 누르면 입력 없이 바로 열립니다. '103동 1502호'처럼 적어도 되고, 접수번호(접수 문자에 있음)로도 찾을 수 있어요.</div>
        </div>
      </form>
      <div class="list" id="ckList"></div>
    </section>
  </main>
  </div>
</div>

<div class="zoom" id="lb" hidden><img id="lbImg" alt="사진 크게 보기"></div>
<footer><div class="wrap"><div class="wm2">엣지컴퍼니</div><?= h(cfg('company', '㈜엣지컴퍼니')) ?> · 공동구매 주관사 · <?= h(cfg('contact_email', '')) ?><?= cfg('callcenter') ? ' · 콜센터 ' . h(cfg('callcenter')) : ' · 콜센터 번호는 단지 협약 뒤 안내합니다' ?> · <a href="privacy.php" style="color:inherit">개인정보 처리방침</a></div></footer>
<script src="assets/common.js?v=3"></script>
<script src="assets/resident.js?v=3"></script>
</body></html>

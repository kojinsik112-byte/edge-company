/* ============================================================
   ACRO STORE — 통합 엔진
   · 공통 헤더/푸터/드로어 주입 (모든 페이지 일관성)
   · 상품 샘플 데이터 + 카드/그리드 렌더
   · 카테고리/상세/장바구니/검색/슬라이더
   · 데이터 기반 제품 랜딩(landing.html?p=...)
   실제 데이터로 바꾸려면 PRODUCTS / LANDINGS 만 교체하면 됩니다.
   ============================================================ */
(function () {
  "use strict";

  var SMARTSTORE = "https://smartstore.naver.com/edge2050";
  var FAN_BUY = "https://smartstore.naver.com/edge2050/products/11887564363";
  var CS_TEL = "1670-0000";

  /* ---------- 카테고리 ---------- */
  var CATEGORIES = [
    { id: "switch",   name: "스위치",        icon: "switch",  landing: "switch" },
    { id: "fan",      name: "실링팬",        icon: "fan",     page: "fan.html" },
    { id: "curtain",  name: "전동커튼",      icon: "curtain", landing: "curtain" },
    { id: "blind",    name: "블라인드",      icon: "blind",   landing: "curtain" },
    { id: "light",    name: "조명",          icon: "light",   landing: "light" },
    { id: "outlet",   name: "콘센트",        icon: "outlet",  landing: "outlet" },
    { id: "fancoil",  name: "환풍기",        icon: "vent" },
    { id: "package",  name: "패키지/기획전", icon: "box" }
  ];

  /* ---------- 샘플 상품 데이터 (가격은 샘플) ---------- */
  var PRODUCTS = [
    { id:"sw5", cat:"switch",  name:"ACRO 5채널 블루투스 유선 스위치", price:89000, sale:69000, rate:4.9, reviews:1284, badges:["BEST","국내최초"], hue:218,
      summary:"화이트 글래스 터치 패널 · 5채널 제어 · 아크로 스마트 앱 연동. 유선 설치 + 블루투스 제어.",
      specs:["블루투스 연결","유선 스위치","5채널 제어","ACRO Smart 앱 제어"] },
    { id:"sw3", cat:"switch",  name:"ACRO 3채널 블루투스 유선 스위치", price:69000, sale:53000, rate:4.8, reviews:842, badges:[], hue:222,
      summary:"방 조명을 한 패널에서. 글래스 터치 + 블루투스 직접 제어, 무계정.",
      specs:["블루투스 연결","유선 스위치","3채널 제어","ACRO Smart 앱 제어"] },
    { id:"fan1",cat:"fan",     name:"아크로 실링팬 마스터 (조명형) 132cm", price:249000, sale:199000, rate:4.9, reviews:2015, badges:["BEST","앵커"], hue:205,
      summary:"완성형 마스터. 3색변환·밝기조절 조명 일체형. 6단계 풍속, 사계절 역회전, 약 20dB 저소음 BLDC.",
      specs:["블루투스 연결","6단계 풍속","3색변환 조명","약 20dB 저소음","DC 모터"], buyUrl:FAN_BUY },
    { id:"fan2",cat:"fan",     name:"아크로 실링팬 마스터 (비조명형) 132cm", price:199000, sale:159000, rate:4.9, reviews:1120, badges:[], hue:30,
      summary:"조명 없는 기본형 마스터. 심플한 인테리어에. 수면풍·타이머·메모리 기능.",
      specs:["블루투스 연결","6단계 풍속","수면 모드","1~8시간 타이머","KC 인증"], buyUrl:FAN_BUY },
    { id:"fanslim",cat:"fan",  name:"아크로 NEW SLIM 실링팬 (준비중)", price:199000, sale:159000, rate:5.0, reviews:0, badges:["NEW","준비중"], hue:35,
      summary:"14.5cm 초슬림 바디 저가형. DC모터 저소음, 6단계 풍속, 사계절 역회전, 앱·리모컨. 출시 준비중입니다.",
      specs:["14.5cm 초슬림","DC 모터 저소음","6단계 풍속","사계절 역회전","앱 & 리모컨"], soon:true, new:true },
    { id:"cur1",cat:"curtain", name:"ACRO 스마트 전동커튼", price:189000, sale:159000, rate:4.7, reviews:640, badges:["NEW"], hue:42,
      summary:"Smart Motorized Curtain. 블루투스 연결·전용 앱 원격 제어·음성 제어·스케줄·안전 감지.",
      specs:["블루투스 연결","전용 앱 원격 제어","음성 제어","스케줄 기능","안전 감지"], new:true },
    { id:"bl1", cat:"blind",   name:"ACRO 전동 블라인드", price:180000, sale:149000, rate:4.6, reviews:410, badges:["NEW"], hue:200,
      summary:"앱으로 채광 조절. 무타공 옵션 지원. 스케줄·타이머 제어.",
      specs:["블루투스 연결","앱 채광 제어","무타공 옵션","스케줄"], new:true },
    { id:"li1", cat:"light",   name:"ACRO 36V 우물조명 PVC 키트", price:89000, sale:69000, rate:4.8, reviews:530, badges:["스토어단독"], hue:45,
      summary:"디밍·색밝기·조도 조절되는 36V. 국내최초 블루투스 연동, 셀프 시공 가능 키트.",
      specs:["DC 36V 저전압","디밍 0~100%","색온도 2700~6500K","블루투스 연동","A/S 3년 보장"] },
    { id:"li2", cat:"light",   name:"ACRO 36V 간접조명 라인", price:45000, sale:35000, rate:4.7, reviews:320, badges:[], hue:48,
      summary:"낮엔 메인등, 밤엔 은은한 간접조명. 3색변환+디밍 동시 제어.",
      specs:["DC 36V 저전압","3색변환","디밍 1~100%","블루투스 연동"] },
    { id:"li3", cat:"light",   name:"ACRO T5 슬림 조명", price:25000, sale:19000, rate:4.6, reviews:210, badges:[], hue:210,
      summary:"주방·붙박이장 어디든. 슬림 라인 조명, 36V 시스템과 모두 호환.",
      specs:["DC 36V 호환","슬림 디자인","5년 이상 수명"] },
    { id:"li4", cat:"light",   name:"ACRO 다운라이트 조명", price:18000, sale:14000, rate:4.6, reviews:160, badges:[], hue:212,
      summary:"매립형 다운라이트. 3색변환·디밍 시스템과 모두 호환.",
      specs:["DC 36V 호환","3색변환","디밍"] },
    { id:"ou1", cat:"outlet",  name:"ACRO 블루투스 콘센트", price:35000, sale:27000, rate:4.7, reviews:290, badges:[], hue:225,
      summary:"조명·선풍기·히터·커피머신까지 앱으로 ON/OFF. 타이머·스케줄, 과전류·과열 방지.",
      specs:["블루투스 연결","앱 ON/OFF","타이머·스케줄","과전류·과열 방지"] },
    { id:"ve1", cat:"fancoil", name:"ACRO 욕실 환풍기", price:79000, sale:65000, rate:4.6, reviews:180, badges:[], hue:195,
      summary:"습기·냄새 자동 관리. 조용한 BLDC 모터.",
      specs:["블루투스 연결","저소음 BLDC","타이머"] },
    { id:"pk1", cat:"package", name:"ACRO 스타터 패키지 (스위치+실링팬+조명)", price:450000, sale:349000, rate:5.0, reviews:95, badges:["기획전","BEST"], hue:218,
      summary:"실링팬을 중심으로 묶은 첫 집 풀세트. 가장 합리적인 시작.",
      specs:["블루투스 연결","무계정","DC 36V 저전압","직접 시공·A/S"] }
  ];

  /* ---------- 아이콘 ---------- */
  var ICONS = {
    switch:  '<rect x="6" y="3" width="12" height="18" rx="2"/><circle cx="12" cy="9" r="2"/><line x1="12" y1="14" x2="12" y2="17"/>',
    fan:     '<circle cx="12" cy="12" r="2"/><path d="M12 10c0-4 4-6 4-3s-2 5-4 5M12 14c0 4-4 6-4 3s2-5 4-5M14 12c4 0 6 4 3 4s-5-2-5-4M10 12c-4 0-6-4-3-4s5 2 5 4"/>',
    curtain: '<path d="M4 3h16M5 3v18c2 0 2-3 3.5-3S10 21 10 21V3M14 3v18s0-3 1.5-3S19 21 19 21V3"/>',
    blind:   '<rect x="4" y="3" width="16" height="18" rx="1"/><line x1="4" y1="8" x2="20" y2="8"/><line x1="4" y1="12" x2="20" y2="12"/><line x1="4" y1="16" x2="20" y2="16"/>',
    light:   '<path d="M9 18h6M10 21h4M12 3a6 6 0 0 0-4 10.5c1 1 1 1.5 1 2.5h6c0-1 0-1.5 1-2.5A6 6 0 0 0 12 3z"/>',
    outlet:  '<rect x="4" y="4" width="16" height="16" rx="3"/><line x1="10" y1="9" x2="10" y2="12"/><line x1="14" y1="9" x2="14" y2="12"/>',
    vent:    '<circle cx="12" cy="12" r="8"/><path d="M12 12l5-3M12 12l-5-3M12 12v6"/>',
    box:     '<path d="M3 7l9-4 9 4-9 4-9-4z"/><path d="M3 7v10l9 4 9-4V7"/><line x1="12" y1="11" x2="12" y2="21"/>',
    bt:      '<path d="M7 7l10 10-5 5V2l5 5L7 17"/>',
    app:     '<rect x="7" y="2" width="10" height="20" rx="2"/><path d="M11 18h2"/>',
    shield:  '<path d="M12 3l8 4v5c0 5-3.5 7.5-8 9-4.5-1.5-8-4-8-9V7z"/><path d="M9 12l2 2 4-4"/>',
    timer:   '<circle cx="12" cy="13" r="8"/><path d="M12 9v4l3 2M9 2h6"/>',
    voice:   '<rect x="9" y="2" width="6" height="12" rx="3"/><path d="M5 11a7 7 0 0 0 14 0M12 18v3"/>',
    leaf:    '<path d="M5 21c0-9 7-16 16-16 0 9-7 16-16 16z"/><path d="M5 21c4-6 9-9 13-10"/>',
    home:    '<path d="M3 11l9-7 9 7"/><path d="M5 10v10h14V10"/>',
    levels:  '<path d="M4 8h12M4 12h16M4 16h9"/>',
    color:   '<circle cx="12" cy="12" r="5"/><path d="M12 1v3M12 20v3M4 12H1M23 12h-3M5 5l2 2M17 17l2 2M19 5l-2 2M7 17l-2 2"/>',
    channel: '<rect x="4" y="3" width="16" height="18" rx="2"/><circle cx="9" cy="9" r="1.3"/><circle cx="15" cy="9" r="1.3"/><circle cx="9" cy="15" r="1.3"/><circle cx="15" cy="15" r="1.3"/>',
    plug:    '<path d="M9 2v6M15 2v6M6 8h12v3a6 6 0 0 1-12 0z M12 17v5"/>',
    bolt:    '<path d="M13 2L4 14h7l-1 8 9-12h-7z"/>',
    moon:    '<path d="M21 12.8A8 8 0 1 1 11.2 3 6 6 0 0 0 21 12.8z"/>',
    schedule:'<rect x="3" y="5" width="18" height="16" rx="2"/><path d="M3 9h18M8 3v4M16 3v4"/>',
    memory:  '<path d="M9 3h6l1 4H8zM7 7h10v13a1 1 0 0 1-1 1H8a1 1 0 0 1-1-1z"/>',
    user:    '<circle cx="12" cy="8" r="4"/><path d="M4 21c0-4 4-6 8-6s8 2 8 6"/>'
  };
  function svg(key, cls) {
    return '<svg class="' + (cls||"") + '" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round">' + (ICONS[key]||ICONS.box) + '</svg>';
  }

  function won(n) { return n.toLocaleString("ko-KR") + "원"; }
  function discountPct(p) { return Math.round((1 - p.sale / p.price) * 100); }
  function catObj(id) { return CATEGORIES.filter(function (x){return x.id===id;})[0]; }
  function catName(id) { var c = catObj(id); return c ? c.name : id; }
  function catIcon(id) { var c = catObj(id); return c ? c.icon : "box"; }
  function catLink(c) { return c.page ? c.page : (c.landing ? "landing.html?p=" + c.landing : "category.html?cat=" + c.id); }

  /* 상품 썸네일: p.img 있으면 사진, 없으면 카테고리 아이콘 SVG */
  function thumb(p, big) {
    if (p.img) return '<img class="thumb__img" src="' + p.img + '" alt="' + p.name + '" loading="lazy" />';
    var h = p.hue, c1 = "hsl(" + h + ",70%,52%)", c2 = "hsl(" + (h + 20) + ",65%,32%)", size = big ? 220 : 110;
    return '<svg class="thumb__svg" viewBox="0 0 200 200" preserveAspectRatio="xMidYMid slice" aria-hidden="true">' +
      '<defs><linearGradient id="tg' + p.id + (big?'b':'') + '" x1="0" y1="0" x2="1" y2="1">' +
      '<stop offset="0" stop-color="' + c1 + '"/><stop offset="1" stop-color="' + c2 + '"/></linearGradient></defs>' +
      '<rect width="200" height="200" fill="url(#tg' + p.id + (big?'b':'') + ')"/>' +
      '<g transform="translate(100,100)"><g transform="translate(-' + size/2 + ',-' + size/2 + ') scale(' + size/24 + ')" ' +
      'fill="none" stroke="rgba(255,255,255,.92)" stroke-width="1.1" stroke-linecap="round" stroke-linejoin="round">' +
      (ICONS[catIcon(p.cat)]||ICONS.box) + '</g></g></svg>';
  }

  function stars(r) {
    var full = Math.round(r), s = "";
    for (var i = 1; i <= 5; i++) s += '<span class="' + (i <= full ? "on" : "") + '">★</span>';
    return '<span class="stars">' + s + '</span>';
  }

  function storeLink(p) { return (p && p.buyUrl) ? p.buyUrl : SMARTSTORE; }

  function card(p) {
    var badges = (p.badges || []).map(function (b) {
      var cls = b === "BEST" ? "b-best" : b === "NEW" ? "b-new" : b === "앵커" ? "b-anchor" : "b-event";
      return '<span class="pbadge ' + cls + '">' + b + '</span>';
    }).join("");
    return '<a class="card" href="product.html?id=' + p.id + '">' +
      '<div class="card__thumb">' + thumb(p) + (badges ? '<div class="card__badges">' + badges + '</div>' : '') + '</div>' +
      '<div class="card__body"><p class="card__cat">' + catName(p.cat) + '</p>' +
      '<h3 class="card__name">' + p.name + '</h3>' +
      '<p class="card__sum">' + (p.summary || "") + '</p>' +
      '<span class="card__more">자세히 보기 →</span></div></a>';
  }
  function renderGrid(el, list) { if (el) el.innerHTML = list.map(card).join(""); }
  function dedupe(arr){ var seen={}; return arr.filter(function(p){ if(seen[p.id])return false; seen[p.id]=1; return true;});}

  /* ---------- 장바구니 ---------- */
  var CART_KEY = "acro_cart";
  function getCart() { try { return JSON.parse(localStorage.getItem(CART_KEY)) || []; } catch (e) { return []; } }
  function setCart(c) { localStorage.setItem(CART_KEY, JSON.stringify(c)); updateCartCount(); }
  function addToCart(id, qty) {
    var cart = getCart(), line = cart.filter(function (x){return x.id===id;})[0];
    if (line) line.qty += qty; else cart.push({ id: id, qty: qty });
    setCart(cart);
  }
  function updateCartCount() {
    var n = getCart().reduce(function (a, b){return a + b.qty;}, 0);
    [].forEach.call(document.querySelectorAll("[data-cart-count]"), function (el){ el.textContent = n; el.style.display = n ? "" : "none"; });
  }

  /* ============================================================
     공통 헤더 / 푸터 / 드로어 주입
     각 페이지는 <div data-header></div> ... <div data-footer></div> 만 두면 됨.
     ============================================================ */
  var CART_SVG = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6"><circle cx="9" cy="20" r="1.5"/><circle cx="18" cy="20" r="1.5"/><path d="M2 3h3l2.5 13h11l2-9H6"/></svg>';
  var HEART_SVG = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6"><path d="M12 21C-2 11 5-3 12 5 19-3 26 11 12 21z"/></svg>';
  var USER_SVG = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6"><circle cx="12" cy="8" r="4"/><path d="M4 21c0-4 4-6 8-6s8 2 8 6"/></svg>';

  function headerHTML() {
    return '' +
    '<div class="drawer" data-drawer><div class="drawer__panel">' +
      '<a class="logo" href="index.html">ACRO<small>SMART HOME</small></a>' +
      '<h4>제품</h4><nav data-gnb></nav>' +
      '<h4>바로가기</h4>' +
      '<a href="videos.html">영상</a><a href="coming.html">신제품 준비</a>' +
      '<a href="fan.html">실링팬</a><a href="landing.html?p=app">아크로 스마트 앱</a>' +
      '<a href="brand.html">브랜드 스토리</a><a href="about.html">회사 소개</a><a href="support.html">고객센터</a>' +
      '<h4>구매</h4><a href="' + SMARTSTORE + '" target="_blank" rel="noopener">네이버 스토어팜에서 구매 →</a>' +
    '</div></div>' +
    '<div class="util"><div class="wrap">' +
      '<a href="about.html">회사소개</a><a href="videos.html">영상</a>' +
      '<a href="support.html">고객센터</a>' +
      '<a href="' + SMARTSTORE + '" target="_blank" rel="noopener">스토어팜</a>' +
    '</div></div>' +
    '<header class="head"><div class="wrap">' +
      '<button class="burger" data-burger aria-label="메뉴"><span></span><span></span><span></span></button>' +
      '<a class="logo" href="index.html">ACRO<small>SMART HOME</small></a>' +
      '<div class="search"><form data-search-form><input placeholder="제품을 검색하세요" aria-label="제품 검색"/><button aria-label="검색">⌕</button></form></div>' +
      '<div class="headicons">' +
        '<a class="storecta" href="' + SMARTSTORE + '" target="_blank" rel="noopener">' + CART_SVG + '<span>스토어팜 구매</span></a>' +
      '</div>' +
    '</div></header>' +
    '<nav class="gnb"><div class="wrap" data-gnb></div></nav>';
  }

  function footerHTML() {
    return '<footer class="foot"><div class="wrap">' +
      '<div class="foot__top">' +
        '<div class="foot__links">' +
          '<a href="index.html">제품 소개</a><a href="videos.html">영상</a>' +
          '<a href="coming.html">신제품 준비</a><a href="brand.html">브랜드 스토리</a>' +
          '<a href="about.html">회사 소개</a><a href="support.html">고객센터</a>' +
          '<a href="' + SMARTSTORE + '" target="_blank" rel="noopener">스토어팜 구매</a>' +
        '</div>' +
        '<div class="foot__cs"><b>' + CS_TEL + '</b>' +
          '<span>평일 10:00 – 17:00 · 점심 12:00 – 13:00 · 주말·공휴일 휴무</span></div>' +
      '</div>' +
      '<div class="foot__info">' +
        '<p class="foot__logo">ACRO</p>' +
        '<div class="foot__promise-row"><span>Bluetooth 전용</span><span>무계정</span><span>DC 36V 저전압 안전</span></div>' +
        '<div class="biz"><span>상호: 주식회사 엣지컴퍼니</span><span>대표: 고진식</span>' +
          '<span>본사: 울산</span><span>사업자등록번호: 000-00-00000</span>' +
          '<span>통신판매업: 2026-울산-0000</span></div>' +
        '<div class="biz"><span>고객센터: ' + CS_TEL + '</span><span>이메일: help@acro.kr</span>' +
          '<span>구매: <a href="' + SMARTSTORE + '" target="_blank" rel="noopener" style="color:inherit;text-decoration:underline">네이버 스토어팜(edge2050)</a></span></div>' +
        '<p class="foot__copy">© 2026 Edge Company. ACRO는 엣지컴퍼니의 자체 브랜드입니다. 제품 구매·결제·배송은 네이버 스토어팜에서 진행됩니다. (※ 사업자정보·연락처는 샘플 값)</p>' +
      '</div>' +
    '</div></footer>';
  }

  function injectChrome() {
    var h = document.querySelector("[data-header]");
    if (h) h.outerHTML = headerHTML();
    var f = document.querySelector("[data-footer]");
    if (f) f.outerHTML = footerHTML();
  }

  function buildGNB() {
    var hosts = document.querySelectorAll("[data-gnb]");
    if (!hosts.length) return;
    var html = CATEGORIES.map(function (c) { return '<a href="' + catLink(c) + '">' + c.name + '</a>'; }).join("") +
      '<a href="fan.html" class="gnb-strong">✦ 실링팬</a>' +
      '<a href="videos.html" class="gnb-strong">영상</a>' +
      '<a href="coming.html" class="gnb-strong">신제품 준비</a>' +
      '<a href="brand.html" class="gnb-strong">브랜드 스토리</a>';
    [].forEach.call(hosts, function (h){ h.innerHTML = html; });
  }

  function wireSearch() {
    [].forEach.call(document.querySelectorAll("[data-search-form]"), function (f) {
      f.addEventListener("submit", function (e) {
        e.preventDefault();
        location.href = "category.html?q=" + encodeURIComponent(f.querySelector("input").value.trim());
      });
    });
  }
  function wireMobile() {
    var burger = document.querySelector("[data-burger]"), drawer = document.querySelector("[data-drawer]");
    if (!burger || !drawer) return;
    burger.addEventListener("click", function () {
      var open = drawer.classList.toggle("open"); document.body.style.overflow = open ? "hidden" : "";
    });
    drawer.addEventListener("click", function (e) {
      if (e.target === drawer || e.target.matches("a")) { drawer.classList.remove("open"); document.body.style.overflow = ""; }
    });
  }

  function param(name) { return new URLSearchParams(location.search).get(name); }

  /* ============================================================
     홈
     ============================================================ */
  function renderHome() {
    renderGrid(document.querySelector("[data-grid=best]"),
      dedupe(PRODUCTS.filter(function (p){return (p.badges||[]).indexOf("BEST")>=0;}).concat(PRODUCTS)).slice(0, 8));
    renderGrid(document.querySelector("[data-grid=new]"),
      dedupe(PRODUCTS.filter(function (p){return p.new;}).concat(PRODUCTS)).slice(0, 4));
    renderGrid(document.querySelector("[data-grid=all]"), PRODUCTS);
    var qhost = document.querySelector("[data-quickcat]");
    if (qhost) qhost.innerHTML = CATEGORIES.map(function (c) {
      return '<a class="qcat" href="' + catLink(c) + '"><span class="qcat__ico">' + svg(c.icon) + '</span>' +
        '<span class="qcat__name">' + c.name + '</span></a>';
    }).join("");
    startSlider();
  }

  /* ============================================================
     카테고리 목록
     ============================================================ */
  function renderCategory() {
    var cat = param("cat"), q = param("q"), sort = param("sort");
    var list = PRODUCTS.slice(), title = "전체 상품";
    if (cat) { list = list.filter(function (p){return p.cat===cat;}); title = catName(cat); }
    if (q)   { list = list.filter(function (p){return (p.name+p.summary).toLowerCase().indexOf(q.toLowerCase())>=0;}); title = '"' + q + '" 검색 결과'; }
    if (sort === "best") { list.sort(function (a,b){return b.reviews-a.reviews;}); title = "베스트"; }
    var sortSel = document.querySelector("[data-sort]");
    function apply() {
      var s = sortSel ? sortSel.value : "rec", l = list.slice();
      if (s === "low") l.sort(function (a,b){return a.sale-b.sale;});
      else if (s === "high") l.sort(function (a,b){return b.sale-a.sale;});
      else if (s === "review") l.sort(function (a,b){return b.reviews-a.reviews;});
      else if (s === "rate") l.sort(function (a,b){return b.rate-a.rate;});
      renderGrid(document.querySelector("[data-grid=list]"), l);
      var cnt = document.querySelector("[data-count]"); if (cnt) cnt.textContent = l.length;
    }
    var t = document.querySelector("[data-cat-title]"); if (t) t.textContent = title;
    if (sortSel) sortSel.addEventListener("change", apply);
    apply();
  }

  /* ============================================================
     상품 상세
     ============================================================ */
  function renderProduct() {
    var p = PRODUCTS.filter(function (x){return x.id===param("id");})[0] || PRODUCTS[0];
    var host = document.querySelector("[data-product]");
    if (!host) return;
    document.title = p.name + " · ACRO";
    var specs = (p.specs && p.specs.length ? p.specs : ["블루투스 전용 · 무계정","DC 36V 저전압 안전","엣지컴퍼니 직접 시공·A/S"]);
    var badges = (p.badges || []).map(function (b){ return '<span class="pdbadge">' + b + '</span>'; }).join("");
    var cta = p.soon
      ? '<button class="btn btn--primary btn--lg" type="button" data-soon>🛠️ 출시 준비중 — 알림받기</button>'
      : '<a class="btn btn--primary btn--lg" href="' + storeLink(p) + '" target="_blank" rel="noopener">네이버 스토어팜에서 구매하기 →</a>';
    host.innerHTML =
      '<div class="pd__gallery">' + thumb(p, true) + '</div>' +
      '<div class="pd__info"><p class="pd__cat">' + catName(p.cat) + (badges?' '+badges:'') + '</p>' +
      '<h1 class="pd__name">' + p.name + '</h1>' +
      '<p class="pd__summary">' + p.summary + '</p>' +
      '<ul class="pd__promise">' + specs.map(function (s){ return '<li>' + s + '</li>'; }).join("") + '</ul>' +
      '<div class="pd__cta">' + cta + '</div>' +
      '<p class="pd__ship">구매·결제·배송은 네이버 스토어팜에서 진행됩니다 · 설치·A/S는 엣지컴퍼니 자체 시공팀</p>' +
      '<p class="pd__ship"><a href="index.html" style="color:var(--blue);font-weight:700">← 전체 제품 보기</a></p></div>';

    var soonBtn = host.querySelector("[data-soon]");
    if (soonBtn) soonBtn.addEventListener("click", function () {
      alert("출시 준비중인 제품입니다. 출시 소식은 고객센터(" + CS_TEL + ") 또는 스토어팜 알림으로 받아보실 수 있어요!");
    });

    renderGrid(document.querySelector("[data-grid=related]"),
      dedupe(PRODUCTS.filter(function (x){return x.cat===p.cat && x.id!==p.id;}).concat(PRODUCTS.filter(function(x){return x.id!==p.id;}))).slice(0, 4));
  }

  /* ---------- 영상 ---------- */
  var VIDEOS = [
    { id:"", title:"ACRO 실링팬 설치 & 사용 후기", desc:"실제 설치 현장과 1년 사용 후기" },
    { id:"", title:"블루투스 스위치 — 인터넷 끊겨도 켜질까?", desc:"직접 테스트 영상" },
    { id:"", title:"36V 스마트 조명 3색변환 + 디밍", desc:"낮과 밤, 공간이 달라집니다" },
    { id:"", title:"스마트 전동커튼 설치기", desc:"실측부터 설치까지" },
    { id:"", title:"아크로 스마트 앱 사용법", desc:"무계정으로 1분 만에 시작" },
    { id:"", title:"입주박람회 ACRO 부스 현장", desc:"현장에서 직접 보고 사는 법" }
  ];
  function renderVideos() {
    var host = document.querySelector("[data-videos]");
    if (!host) return;
    host.innerHTML = VIDEOS.map(function (v, i) {
      return '<button class="rev" data-yt="' + v.id + '" aria-label="영상 재생">' +
        '<div class="rev__thumb"><span class="rev__play">▶</span></div>' +
        '<p class="rev__t">' + v.title + '</p><p class="rev__d">' + v.desc + '</p></button>';
    }).join("");
    [].forEach.call(host.querySelectorAll(".rev"), function (btn) {
      btn.addEventListener("click", function () {
        var id = btn.getAttribute("data-yt");
        if (!id) { alert("영상 ID가 아직 등록되지 않았습니다.\nshop.js 의 VIDEOS 배열에 유튜브 영상 ID를 넣어주세요."); return; }
        btn.querySelector(".rev__thumb").innerHTML =
          '<iframe src="https://www.youtube.com/embed/' + id + '?autoplay=1&rel=0" title="ACRO 영상" allow="autoplay; encrypted-media" allowfullscreen></iframe>';
      });
    });
  }

  /* ---------- 신제품 준비 ---------- */
  function renderComing() {
    renderGrid(document.querySelector("[data-grid=coming]"),
      PRODUCTS.filter(function (p){ return p.soon || p.new; }));
  }

  /* ============================================================
     장바구니
     ============================================================ */
  function renderCart() {
    var host = document.querySelector("[data-cart]");
    if (!host) return;
    var cart = getCart();
    if (!cart.length) { host.innerHTML = '<p class="cart-empty">장바구니가 비어 있습니다.<br><a href="category.html">상품 보러 가기 →</a></p>'; return; }
    var rows = "", total = 0;
    cart.forEach(function (line) {
      var p = PRODUCTS.filter(function (x){return x.id===line.id;})[0]; if (!p) return;
      var sum = p.sale * line.qty; total += sum;
      rows += '<div class="cartrow" data-id="' + p.id + '"><div class="cartrow__thumb">' + thumb(p) + '</div>' +
        '<div class="cartrow__info"><a href="product.html?id=' + p.id + '">' + p.name + '</a><span>' + won(p.sale) + '</span></div>' +
        '<div class="cartrow__qty"><button data-cq="-1">−</button><b>' + line.qty + '</b><button data-cq="1">+</button></div>' +
        '<div class="cartrow__sum">' + won(sum) + '</div>' +
        '<button class="cartrow__del" data-del aria-label="삭제">✕</button></div>';
    });
    host.innerHTML = rows + '<div class="cart-total"><span>총 결제금액</span><b>' + won(total) + '</b></div>' +
      '<button class="btn btn--primary btn--lg cart-checkout">주문하기</button>' +
      '<p class="cart-note">※ 데모 화면입니다. 실제 결제는 스마트스토어/박람회에서 진행됩니다.</p>';
    [].forEach.call(host.querySelectorAll(".cartrow"), function (row) {
      var id = row.dataset.id;
      [].forEach.call(row.querySelectorAll("[data-cq]"), function (b) {
        b.addEventListener("click", function () {
          var c = getCart(), l = c.filter(function (x){return x.id===id;})[0];
          l.qty = Math.max(1, l.qty + parseInt(b.dataset.cq,10)); setCart(c); renderCart();
        });
      });
      row.querySelector("[data-del]").addEventListener("click", function () {
        setCart(getCart().filter(function (x){return x.id!==id;})); renderCart();
      });
    });
    var co = host.querySelector(".cart-checkout");
    if (co) co.addEventListener("click", function () { alert("데모 주문이 접수되었습니다. 감사합니다, 엣지님!"); });
  }

  /* ============================================================
     슬라이더
     ============================================================ */
  function startSlider() {
    var slider = document.querySelector("[data-slider]"); if (!slider) return;
    var slides = slider.querySelectorAll(".slide"), dots = slider.querySelectorAll(".slide-dot"), i = 0, timer;
    function go(n) {
      i = (n + slides.length) % slides.length;
      [].forEach.call(slides, function (s, k){ s.classList.toggle("on", k === i); });
      [].forEach.call(dots, function (d, k){ d.classList.toggle("on", k === i); });
    }
    [].forEach.call(dots, function (d, k){ d.addEventListener("click", function (){ go(k); reset(); }); });
    var prev = slider.querySelector("[data-prev]"), next = slider.querySelector("[data-next]");
    if (prev) prev.addEventListener("click", function (){ go(i-1); reset(); });
    if (next) next.addEventListener("click", function (){ go(i+1); reset(); });
    function reset(){ clearInterval(timer); timer = setInterval(function (){ go(i+1); }, 5000); }
    go(0); reset();
  }

  /* ============================================================
     데이터 기반 제품 랜딩 (landing.html?p=...)
     ============================================================ */
  var LANDINGS = {
    switch: {
      theme: "blue",
      cat: "switch",
      hero: { kicker:"ACRO BLUETOOTH WIRED SWITCH", h1:"터치 한 번으로,<br><b>집 전체를 켜고 끈다</b>",
        sub:"화이트 글래스 터치 패널 · 최대 5채널 제어 · 아크로 스마트 앱 연동. 유선으로 안정적이게, 블루투스로 편리하게.",
        tags:["블루투스 연결","유선 스위치","5채널 제어","앱 제어 지원"], icon:"switch",
        primary:{label:"스위치 보러가기", href:"category.html?cat=switch"} },
      features: [
        {icon:"bt", t:"블루투스 연결", d:"공유기·계정 없이 스마트폰과 바로 연결."},
        {icon:"switch", t:"유선 스위치", d:"매립 유선 설치로 끊김 없이 안정적인 동작."},
        {icon:"channel", t:"최대 5채널 제어", d:"여러 등을 한 패널에서 개별 제어."},
        {icon:"app", t:"ACRO Smart 앱", d:"국산 전용 앱으로 직관적이고 편리하게."},
        {icon:"home", t:"홈 버튼 씬", d:"한 번의 터치로 원하는 조명 조합 호출."},
        {icon:"shield", t:"무계정·로컬 동작", d:"인터넷이 끊겨도 손으로도 그대로 작동."}
      ],
      spec: [["연결 방식","Bluetooth"],["설치","유선(매립형)"],["채널","1 / 3 / 5채널"],["패널","강화 글래스 터치"],["앱","ACRO Smart"],["전원","DC 저전압 제어"]],
      faq: [
        {q:"인터넷이 끊기면 스위치를 못 쓰나요?", a:"아니요. 모든 제어가 블루투스로 직접 이뤄지고 물리 터치도 동작하므로 인터넷·공유기 없이 그대로 작동합니다."},
        {q:"기존 스위치 자리에 설치 가능한가요?", a:"유선 매립형으로 기존 스위치 박스에 시공합니다. 엣지컴퍼니 자체 시공팀이 설치·A/S까지 진행합니다."},
        {q:"앱은 어떤 걸 쓰나요?", a:"아크로 공식 'ACRO Smart' 앱만 사용합니다. 타사 앱 연동은 지원하지 않아 개인정보·보안에 안전합니다."}
      ],
      close: {h:"가장 많이 만지는 물건일수록,<br><b>가장 잘 만들어야 합니다</b>", d:"매일 손이 닿는 스위치부터 ACRO로 바꿔보세요.", cta:{label:"스위치 보러가기", href:"category.html?cat=switch"}}
    },

    light: {
      theme: "gold",
      cat: "light",
      hero: { kicker:"ACRO 36V LIGHTING", h1:"디밍·색밝기·조도 조절되는<br><b>36V 스마트 조명</b>",
        sub:"국내최초 블루투스 연동 조명. 낮엔 밝은 메인등, 밤엔 은은한 간접조명 — 빛이 바뀌면 공간의 품격이 달라집니다.",
        tags:["DC 36V 저전압","3색변환","디밍 1~100%","블루투스 연동","A/S 3년"], icon:"light",
        primary:{label:"조명 보러가기", href:"category.html?cat=light"} },
      features: [
        {icon:"bolt", t:"DC 36V 저전압", d:"감전·화재 리스크를 낮춘 안전한 저전압 설계."},
        {icon:"color", t:"3색변환", d:"전구색·주백색·주광색을 자유롭게."},
        {icon:"levels", t:"디밍 1~100%", d:"분위기에 맞춰 밝기를 정밀하게."},
        {icon:"bt", t:"블루투스 제어", d:"앱으로 집 전체 조명을 한 번에."},
        {icon:"moon", t:"낮/밤 한 번에", d:"메인등과 간접조명을 동시에 연출."},
        {icon:"shield", t:"5년 이상 수명", d:"뛰어난 내구성과 A/S 3년 보장."}
      ],
      spec: [["전압","DC 36V 저전압"],["색온도","3000K / 4000K / 6500K"],["디밍","1~100%"],["연결","Bluetooth"],["호환","T5 · 다운라이트 · 우물/간접"],["보증","A/S 3년"]],
      cct: true,
      faq: [
        {q:"36V면 일반 조명과 뭐가 다른가요?", a:"가정용 220V가 아닌 DC 36V 저전압으로 구동해 감전·화재 리스크를 물리적으로 낮춘 설계입니다."},
        {q:"우물천장·간접조명도 되나요?", a:"우물조명 PVC 키트, 간접조명 라인, T5, 다운라이트까지 36V 시스템으로 모두 호환됩니다."},
        {q:"색과 밝기를 같이 조절할 수 있나요?", a:"네, 하나의 앱(또는 리모컨)으로 3색변환과 디밍을 동시에 제어합니다."}
      ],
      close: {h:"빛이 바뀌면,<br><b>공간의 품격이 달라집니다</b>", d:"낮엔 밝게, 밤엔 호텔처럼. 36V 스마트 조명으로 완성하세요.", cta:{label:"조명 보러가기", href:"category.html?cat=light"}}
    },

    curtain: {
      theme: "green",
      cat: "curtain",
      hero: { kicker:"ACRO SMART MOTORIZED CURTAIN", h1:"아침이 스스로 열리는,<br><b>스마트 전동커튼</b>",
        sub:"블루투스 연결·전용 앱 원격 제어·음성 제어·스케줄·안전 감지. 실측부터 설치까지 자체 시공팀이 직접.",
        tags:["블루투스 연결","앱 원격 제어","음성 제어","스케줄","안전 감지"], icon:"curtain",
        primary:{label:"전동커튼 보러가기", href:"category.html?cat=curtain"} },
      features: [
        {icon:"bt", t:"블루투스 연결", d:"빠르고 안정적인 연결로 즉시 제어."},
        {icon:"app", t:"전용 앱 원격 제어", d:"누워서도, 외출 전에도 손끝으로."},
        {icon:"voice", t:"음성 제어 지원", d:"말 한마디로 커튼을 열고 닫기."},
        {icon:"schedule", t:"스케줄 기능", d:"기상·취침 시간에 맞춰 자동으로."},
        {icon:"shield", t:"안전 감지 기능", d:"장애물을 감지해 멈추는 안심 설계."},
        {icon:"home", t:"무타공 옵션", d:"전동 블라인드는 무타공 설치도 지원."}
      ],
      spec: [["연결","Bluetooth"],["제어","전용 앱 · 음성 · 스케줄"],["안전","장애물 안전 감지"],["설치","자체 시공팀 실측·설치"],["라인업","전동커튼 · 전동 블라인드"]],
      faq: [
        {q:"우리 집 창에도 맞나요?", a:"엣지컴퍼니 시공팀이 직접 실측 후 맞춤 설치합니다. 창 크기·형태에 맞춰 진행됩니다."},
        {q:"음성 제어는 어떻게 하나요?", a:"전용 앱과 연동된 음성 명령으로 커튼을 열고 닫을 수 있습니다."},
        {q:"전동 블라인드도 있나요?", a:"네, 무타공 옵션을 지원하는 전동 블라인드도 함께 제공합니다."}
      ],
      close: {h:"매일 아침,<br><b>커튼이 먼저 일어납니다</b>", d:"빛과 함께 시작하는 하루. 스마트 전동커튼으로.", cta:{label:"전동커튼 보러가기", href:"category.html?cat=curtain"}}
    },

    outlet: {
      theme: "navy",
      cat: "outlet",
      hero: { kicker:"ACRO BLUETOOTH OUTLET", h1:"멀리서도 끄고 켜는,<br><b>블루투스 콘센트</b>",
        sub:"조명·선풍기·히터·커피머신까지 앱으로 ON/OFF. 타이머·스케줄로 자동 제어, 과전류·과열 방지로 더 안전하게.",
        tags:["블루투스 연결","앱 ON/OFF","타이머·스케줄","과전류·과열 방지"], icon:"outlet",
        primary:{label:"콘센트 보러가기", href:"category.html?cat=outlet"} },
      features: [
        {icon:"bt", t:"블루투스 연결", d:"빠르고 안정적인 연결로 간편 제어."},
        {icon:"app", t:"스마트 ON/OFF", d:"전용 앱으로 어디서든 전원 제어."},
        {icon:"timer", t:"타이머 & 스케줄", d:"원하는 시간에 자동으로 켜고 끄기."},
        {icon:"shield", t:"과전류·과열 방지", d:"안전 보호 회로로 더 안심."},
        {icon:"plug", t:"다양한 기기 호환", d:"조명·선풍기·히터·커피머신 등."},
        {icon:"leaf", t:"대기전력 절감", d:"안 쓰는 전원을 자동으로 차단."}
      ],
      spec: [["연결","Bluetooth"],["제어","앱 ON/OFF · 타이머 · 스케줄"],["안전","과전류 · 과열 방지"],["호환","조명·선풍기·히터·커피머신 등"]],
      faq: [
        {q:"어떤 가전이든 연결되나요?", a:"정격 범위 내 일반 가전(조명·선풍기·히터·커피머신 등)을 콘센트에 꽂아 앱으로 제어합니다."},
        {q:"예약 켜짐/꺼짐이 되나요?", a:"타이머와 스케줄 기능으로 원하는 시간에 자동 ON/OFF 됩니다."},
        {q:"안전한가요?", a:"과전류·과열 방지 보호 설계로 안전하게 사용할 수 있습니다."}
      ],
      close: {h:"플러그 하나로,<br><b>모든 가전이 스마트해집니다</b>", d:"꽂기만 하면 시작되는 스마트홈.", cta:{label:"콘센트 보러가기", href:"category.html?cat=outlet"}}
    },

    app: {
      theme: "dark",
      hero: { kicker:"ACRO SMART APP", h1:"아크로 스마트,<br><b>하나면 충분합니다</b>",
        sub:"구글 플레이·애플 앱스토어에서 '아크로 스마트'를 검색하세요. 블루투스 연결 후 모든 ACRO 기기를 한 앱에서.",
        tags:["블루투스 연동","국산 전용 앱","무계정 사용","개인정보 보호"], icon:"app",
        primary:{label:"전체 상품 보기", href:"index.html"} },
      features: [
        {icon:"bt", t:"블루투스 기능 탑재", d:"앱과 빠르고 안정적인 연결."},
        {icon:"home", t:"집 전체 그룹 제어", d:"방·기기별로 묶어 한 번에 제어."},
        {icon:"schedule", t:"스케줄 / 타이머", d:"자동 켜짐·꺼짐 예약."},
        {icon:"user", t:"가족과 간편 공유", d:"홈 단위 QR로 손쉽게 공유."},
        {icon:"shield", t:"타사 앱 미사용", d:"개인정보·보안을 위해 공식 앱만 지원."},
        {icon:"app", t:"국산 전용 앱", d:"직관적이고 편리한 한국어 인터페이스."}
      ],
      store: true,
      spec: [["지원","Google Play · App Store"],["검색어","아크로 스마트"],["연결","Bluetooth"],["계정","불필요(무가입)"],["공유","홈 단위 QR"]],
      faq: [
        {q:"왜 타사 앱은 안 쓰나요?", a:"고객님의 개인정보 보호와 제품 안전성을 위해 아크로 공식 앱만 지원합니다. 타사 앱 연동은 지원하지 않습니다."},
        {q:"회원가입을 꼭 해야 하나요?", a:"아니요. 무계정·무가입으로 권한 팝업 한 번이면 바로 사용할 수 있습니다."},
        {q:"앱은 어디서 받나요?", a:"구글 플레이 또는 애플 앱스토어에서 '아크로 스마트'로 검색해 설치하세요."}
      ],
      close: {h:"믿을 수 있는,<br><b>아크로 공식앱</b>", d:"'아크로 스마트'로 검색하고 지금 시작하세요.", cta:{label:"전체 상품 보기", href:"index.html"}}
    }
  };

  function renderLanding() {
    var key = param("p") || "switch";
    var L = LANDINGS[key] || LANDINGS.switch;
    var host = document.querySelector("[data-landing]");
    if (!host) return;
    document.body.classList.add("lp", "lp--" + (L.theme||"blue"));
    document.title = (L.hero.kicker || "ACRO") + " · ACRO";

    var H = L.hero;
    var html = '<section class="lhero"><div class="lwrap lhero__inner">' +
      '<div class="lhero__txt"><span class="lkicker">' + H.kicker + '</span>' +
      '<h1>' + H.h1 + '</h1><p>' + H.sub + '</p>' +
      '<div class="ltags">' + H.tags.map(function (t){return '<span>'+t+'</span>';}).join("") + '</div>' +
      '<div class="lcta"><a class="lbtn lbtn--solid" href="' + H.primary.href + '">' + H.primary.label + '</a>' +
      '<a class="lbtn lbtn--ghost" href="#lfeat">자세히 보기</a></div></div>' +
      '<div class="lhero__viz" aria-hidden="true"><div class="lviz">' + svg(H.icon,"lviz__ico") + '</div></div>' +
      '</div></section>';

    html += '<section class="lfeat" id="lfeat"><div class="lwrap lcenter">' +
      '<span class="lkicker">FEATURES</span><h2 class="lh2">핵심 기능</h2></div>' +
      '<div class="lwrap"><div class="lfeat__grid">' +
      L.features.map(function (f){ return '<div class="lfcard"><div class="lfcard__ico">' + svg(f.icon) + '</div>' +
        '<h4>' + f.t + '</h4><p>' + f.d + '</p></div>'; }).join("") +
      '</div></div></section>';

    if (L.cct) {
      html += '<section class="lcct"><div class="lwrap lcenter"><span class="lkicker">LIGHT</span>' +
        '<h2 class="lh2">3색변환 + 디밍</h2><p class="llead">색온도와 밝기를 한 번에.</p></div>' +
        '<div class="lwrap"><div class="lcct__row">' +
        '<div class="lcct__c warm">전구색<span>3000K</span></div>' +
        '<div class="lcct__c nat">주백색<span>4000K</span></div>' +
        '<div class="lcct__c cool">주광색<span>6500K</span></div></div>' +
        '<div class="ldim"><small>1%</small><small>100%</small></div></div></section>';
    }

    if (L.store) {
      html += '<section class="lstore"><div class="lwrap lcenter"><span class="lkicker">DOWNLOAD</span>' +
        '<h2 class="lh2">‘아크로 스마트’ 검색</h2><p class="llead">구글 플레이 · 애플 앱스토어에서 지금 받으세요.</p>' +
        '<div class="lstore__btns"><span class="storebtn">▶ Google Play</span><span class="storebtn"> App Store</span></div></div></section>';
    }

    if (L.spec) {
      html += '<section class="lspec"><div class="lwrap lcenter"><span class="lkicker">SPEC</span><h2 class="lh2">제품 사양</h2></div>' +
        '<div class="lwrap"><table class="lspec__t"><tbody>' +
        L.spec.map(function (r){ return '<tr><th>' + r[0] + '</th><td>' + r[1] + '</td></tr>'; }).join("") +
        '</tbody></table></div></section>';
    }

    if (L.faq) {
      html += '<section class="lfaq"><div class="lwrap lcenter"><span class="lkicker">FAQ</span><h2 class="lh2">자주 묻는 질문</h2></div>' +
        '<div class="lwrap lfaq__list">' +
        L.faq.map(function (f){ return '<details class="lfaq__i"><summary>' + f.q + '</summary><p>' + f.a + '</p></details>'; }).join("") +
        '</div></section>';
    }

    if (L.cat) {
      html += '<section class="lrel"><div class="lwrap"><div class="shead"><div><h2>이 카테고리 상품</h2></div>' +
        '<a href="category.html?cat=' + L.cat + '">전체보기 →</a></div><div class="grid" data-grid="lprod"></div></div></section>';
    }

    var C = L.close;
    html += '<section class="lclose"><div class="lwrap lcenter"><h2>' + C.h + '</h2><p>' + C.d + '</p>' +
      '<div class="lcta lcta--center">' +
        '<a class="lbtn lbtn--solid" href="' + SMARTSTORE + '" target="_blank" rel="noopener">스토어팜에서 구매하기 →</a>' +
        '<a class="lbtn lbtn--ghost" href="' + C.cta.href + '">' + C.cta.label + '</a>' +
      '</div></div></section>';

    host.innerHTML = html;
    if (L.cat) renderGrid(document.querySelector("[data-grid=lprod]"), dedupe(PRODUCTS.filter(function (p){return p.cat===L.cat;})).slice(0,4));
  }

  /* ============================================================
     부트스트랩
     ============================================================ */
  document.addEventListener("DOMContentLoaded", function () {
    injectChrome();
    buildGNB(); wireSearch(); wireMobile(); updateCartCount();
    var page = document.body.getAttribute("data-page");
    if (page === "home") renderHome();
    else if (page === "category") renderCategory();
    else if (page === "product") renderProduct();
    else if (page === "landing") renderLanding();
    else if (page === "videos") renderVideos();
    else if (page === "coming") renderComing();
  });

  window.ACRO = { PRODUCTS: PRODUCTS, CATEGORIES: CATEGORIES, LANDINGS: LANDINGS };
})();

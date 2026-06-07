/* ============================================================
   ACRO STORE — 샘플 데이터 + 렌더링 엔진 (창안애 스타일 쇼핑몰)
   실제 상품/가격/후기가 생기면 PRODUCTS 배열만 교체하면 됩니다.
   장바구니는 localStorage 에 저장됩니다.
   ============================================================ */
(function () {
  "use strict";

  /* ---------- 카테고리 ---------- */
  var CATEGORIES = [
    { id: "switch",   name: "스위치",        icon: "switch" },
    { id: "fan",      name: "실링팬",        icon: "fan" },
    { id: "curtain",  name: "전동커튼",      icon: "curtain" },
    { id: "blind",    name: "블라인드",      icon: "blind" },
    { id: "light",    name: "조명",          icon: "light" },
    { id: "outlet",   name: "콘센트",        icon: "outlet" },
    { id: "fancoil",  name: "환풍기",        icon: "vent" },
    { id: "package",  name: "패키지/기획전", icon: "box" }
  ];

  /* ---------- 샘플 상품 데이터 ---------- */
  var PRODUCTS = [
    { id:"sw1", cat:"switch",  name:"ACRO 블루투스 스위치 1구", price:39000, sale:29000, rate:4.9, reviews:1284, badges:["BEST"], hue:218, summary:"생태계의 허브. 손으로도 앱으로도 켜고 끄는 가장 기본 제품.", new:false },
    { id:"sw2", cat:"switch",  name:"ACRO 블루투스 스위치 3구", price:59000, sale:45000, rate:4.8, reviews:842,  badges:[],      hue:222, summary:"방 전체 조명을 한 패널에서. 무계정·블루투스 직접 제어." },
    { id:"fan1",cat:"fan",     name:"ACRO 실링팬 화이트", price:249000, sale:199000, rate:4.9, reviews:2015, badges:["BEST","앵커"], hue:205, summary:"옵션·비옵션 세대 모두에서 사랑받는 전천후 냉난방·환기." },
    { id:"fan2",cat:"fan",     name:"ACRO 실링팬 우드에디션", price:289000, sale:229000, rate:4.9, reviews:1120, badges:[], hue:36,  summary:"우드 블레이드로 인테리어까지. DC 36V 저전압 안전 설계." },
    { id:"cur1",cat:"curtain", name:"엣지리브 전동커튼 풀세트", price:350000, sale:290000, rate:4.7, reviews:640, badges:["NEW"], hue:150, summary:"포레스트 그린 패키지. 실측·설치까지 자체 시공팀이 직접." , new:true},
    { id:"bl1", cat:"blind",   name:"엣지리브 전동 블라인드", price:180000, sale:149000, rate:4.6, reviews:410, badges:["NEW"], hue:200, summary:"앱으로 채광 조절. 무타공 옵션 지원.", new:true },
    { id:"li1", cat:"light",   name:"ACRO 우물조명 PVC 키트", price:89000, sale:69000, rate:4.8, reviews:530, badges:["스토어단독"], hue:45, summary:"스마트스토어 단독 라인. 셀프 시공도 가능한 키트 구성." },
    { id:"li2", cat:"light",   name:"ACRO 간접조명 라인", price:45000, sale:35000, rate:4.7, reviews:320, badges:[], hue:48, summary:"은은한 무드. 블루투스로 밝기·색온도 제어." },
    { id:"li3", cat:"light",   name:"ACRO T5 슬림 조명", price:25000, sale:19000, rate:4.6, reviews:210, badges:[], hue:210, summary:"주방·붙박이장 어디든. 슬림한 라인 조명." },
    { id:"ou1", cat:"outlet",  name:"ACRO 스마트 콘센트", price:35000, sale:27000, rate:4.7, reviews:290, badges:[], hue:230, summary:"전원까지 ACRO 앱 한 화면에서. 저전압 안전 설계." },
    { id:"ve1", cat:"fancoil", name:"ACRO 욕실 환풍기", price:79000, sale:65000, rate:4.6, reviews:180, badges:[], hue:195, summary:"습기·냄새 자동 관리. 조용한 BLDC 모터." },
    { id:"pk1", cat:"package", name:"ACRO 스타터 패키지 (스위치+실링팬+조명)", price:450000, sale:349000, rate:5.0, reviews:95, badges:["기획전","BEST"], hue:218, summary:"실링팬을 중심으로 묶은 첫 집 풀세트. 가장 합리적인 시작." }
  ];

  /* ---------- 아이콘 (SVG path) ---------- */
  var ICONS = {
    switch:  '<rect x="6" y="3" width="12" height="18" rx="2"/><circle cx="12" cy="9" r="2"/><line x1="12" y1="14" x2="12" y2="17"/>',
    fan:     '<circle cx="12" cy="12" r="2"/><path d="M12 10c0-4 4-6 4-3s-2 5-4 5M12 14c0 4-4 6-4 3s2-5 4-5M14 12c4 0 6 4 3 4s-5-2-5-4M10 12c-4 0-6-4-3-4s5 2 5 4"/>',
    curtain: '<path d="M4 3h16M5 3v18c2 0 2-3 3.5-3S10 21 10 21V3M14 3v18s0-3 1.5-3S19 21 19 21V3"/>',
    blind:   '<rect x="4" y="3" width="16" height="18" rx="1"/><line x1="4" y1="8" x2="20" y2="8"/><line x1="4" y1="12" x2="20" y2="12"/><line x1="4" y1="16" x2="20" y2="16"/>',
    light:   '<path d="M9 18h6M10 21h4M12 3a6 6 0 0 0-4 10.5c1 1 1 1.5 1 2.5h6c0-1 0-1.5 1-2.5A6 6 0 0 0 12 3z"/>',
    outlet:  '<rect x="4" y="4" width="16" height="16" rx="3"/><line x1="10" y1="9" x2="10" y2="12"/><line x1="14" y1="9" x2="14" y2="12"/>',
    vent:    '<circle cx="12" cy="12" r="8"/><path d="M12 12l5-3M12 12l-5-3M12 12v6"/>',
    box:     '<path d="M3 7l9-4 9 4-9 4-9-4z"/><path d="M3 7v10l9 4 9-4V7"/><line x1="12" y1="11" x2="12" y2="21"/>'
  };

  function won(n) { return n.toLocaleString("ko-KR") + "원"; }
  function discountPct(p) { return Math.round((1 - p.sale / p.price) * 100); }
  function catName(id) { var c = CATEGORIES.find(function (x){return x.id===id;}); return c ? c.name : id; }
  function catIcon(id) { var c = CATEGORIES.find(function (x){return x.id===id;}); return c ? c.icon : "box"; }

  /* 상품 썸네일(SVG 그라데이션 + 아이콘) — 사진 없이 일관된 비주얼 */
  function thumb(p, big) {
    var h = p.hue;
    var c1 = "hsl(" + h + ",70%,52%)";
    var c2 = "hsl(" + (h + 20) + ",65%,32%)";
    var size = big ? 220 : 110;
    return '' +
      '<svg class="thumb__svg" viewBox="0 0 200 200" preserveAspectRatio="xMidYMid slice" aria-hidden="true">' +
        '<defs><linearGradient id="tg' + p.id + (big?'b':'') + '" x1="0" y1="0" x2="1" y2="1">' +
          '<stop offset="0" stop-color="' + c1 + '"/><stop offset="1" stop-color="' + c2 + '"/>' +
        '</linearGradient></defs>' +
        '<rect width="200" height="200" fill="url(#tg' + p.id + (big?'b':'') + ')"/>' +
        '<g transform="translate(100,100)"><g transform="translate(-' + size/2 + ',-' + size/2 + ') scale(' + size/24 + ')" ' +
          'fill="none" stroke="rgba(255,255,255,.92)" stroke-width="1.1" stroke-linecap="round" stroke-linejoin="round">' +
          ICONS[catIcon(p.cat)] +
        '</g></g>' +
      '</svg>';
  }

  /* 별점 */
  function stars(r) {
    var full = Math.round(r);
    var s = "";
    for (var i = 1; i <= 5; i++) s += '<span class="' + (i <= full ? "on" : "") + '">★</span>';
    return '<span class="stars">' + s + '</span>';
  }

  /* 상품 카드 */
  function card(p) {
    var badges = (p.badges || []).map(function (b) {
      var cls = b === "BEST" ? "b-best" : b === "NEW" ? "b-new" : b === "앵커" ? "b-anchor" : "b-event";
      return '<span class="pbadge ' + cls + '">' + b + '</span>';
    }).join("");
    return '' +
      '<a class="card" href="product.html?id=' + p.id + '">' +
        '<div class="card__thumb">' + thumb(p) + (badges ? '<div class="card__badges">' + badges + '</div>' : '') + '</div>' +
        '<div class="card__body">' +
          '<p class="card__cat">' + catName(p.cat) + '</p>' +
          '<h3 class="card__name">' + p.name + '</h3>' +
          '<div class="card__price">' +
            '<span class="off">' + discountPct(p) + '%</span>' +
            '<span class="sale">' + won(p.sale) + '</span>' +
            '<span class="orig">' + won(p.price) + '</span>' +
          '</div>' +
          '<div class="card__meta">' + stars(p.rate) + '<span class="rcount">후기 ' + p.reviews.toLocaleString("ko-KR") + '</span></div>' +
        '</div>' +
      '</a>';
  }

  function renderGrid(el, list) {
    if (!el) return;
    el.innerHTML = list.map(card).join("");
  }

  /* ---------- 장바구니 (localStorage) ---------- */
  var CART_KEY = "acro_cart";
  function getCart() { try { return JSON.parse(localStorage.getItem(CART_KEY)) || []; } catch (e) { return []; } }
  function setCart(c) { localStorage.setItem(CART_KEY, JSON.stringify(c)); updateCartCount(); }
  function addToCart(id, qty) {
    var cart = getCart();
    var line = cart.find(function (x){return x.id===id;});
    if (line) line.qty += qty; else cart.push({ id: id, qty: qty });
    setCart(cart);
  }
  function updateCartCount() {
    var n = getCart().reduce(function (a, b){return a + b.qty;}, 0);
    document.querySelectorAll("[data-cart-count]").forEach(function (el){ el.textContent = n; el.style.display = n ? "" : "none"; });
  }

  /* ---------- 공통 UI: GNB / 검색 / 모바일 메뉴 ---------- */
  function buildGNB() {
    var hosts = document.querySelectorAll("[data-gnb]");
    if (!hosts.length) return;
    var html = CATEGORIES.map(function (c) {
      return '<a href="category.html?cat=' + c.id + '">' + c.name + '</a>';
    }).join("") +
    '<a href="category.html?sort=best" class="gnb-strong">베스트</a>' +
    '<a href="brand.html" class="gnb-strong">브랜드 스토리</a>';
    hosts.forEach(function (h){ h.innerHTML = html; });
  }

  function wireSearch() {
    document.querySelectorAll("[data-search-form]").forEach(function (f) {
      f.addEventListener("submit", function (e) {
        e.preventDefault();
        var q = f.querySelector("input").value.trim();
        location.href = "category.html?q=" + encodeURIComponent(q);
      });
    });
  }

  function wireMobile() {
    var burger = document.querySelector("[data-burger]");
    var drawer = document.querySelector("[data-drawer]");
    if (!burger || !drawer) return;
    burger.addEventListener("click", function () {
      var open = drawer.classList.toggle("open");
      document.body.style.overflow = open ? "hidden" : "";
    });
    drawer.addEventListener("click", function (e) {
      if (e.target === drawer || e.target.matches("a")) { drawer.classList.remove("open"); document.body.style.overflow = ""; }
    });
  }

  /* ---------- 페이지별 렌더 ---------- */
  function param(name) { return new URLSearchParams(location.search).get(name); }

  function renderHome() {
    var best = PRODUCTS.filter(function (p){return (p.badges||[]).includes("BEST");}).concat(PRODUCTS).slice(0, 8);
    renderGrid(document.querySelector("[data-grid=best]"), dedupe(best).slice(0, 8));
    renderGrid(document.querySelector("[data-grid=new]"), PRODUCTS.filter(function (p){return p.new;}).concat(PRODUCTS).slice(0,4));
    renderGrid(document.querySelector("[data-grid=all]"), PRODUCTS);

    var qhost = document.querySelector("[data-quickcat]");
    if (qhost) {
      qhost.innerHTML = CATEGORIES.map(function (c) {
        return '<a class="qcat" href="category.html?cat=' + c.id + '">' +
          '<span class="qcat__ico"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round">' + ICONS[c.icon] + '</svg></span>' +
          '<span class="qcat__name">' + c.name + '</span></a>';
      }).join("");
    }
    startSlider();
  }
  function dedupe(arr){ var seen={}; return arr.filter(function(p){ if(seen[p.id])return false; seen[p.id]=1; return true;});}

  function renderCategory() {
    var cat = param("cat"), q = param("q"), sort = param("sort");
    var list = PRODUCTS.slice();
    var title = "전체 상품";
    if (cat) { list = list.filter(function (p){return p.cat===cat;}); title = catName(cat); }
    if (q)   { list = list.filter(function (p){return (p.name+p.summary).toLowerCase().includes(q.toLowerCase());}); title = '"' + q + '" 검색 결과'; }
    if (sort === "best") { list.sort(function (a,b){return b.reviews-a.reviews;}); title = "베스트"; }

    var sortSel = document.querySelector("[data-sort]");
    function apply() {
      var s = sortSel ? sortSel.value : "rec";
      var l = list.slice();
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

  function renderProduct() {
    var p = PRODUCTS.find(function (x){return x.id===param("id");}) || PRODUCTS[0];
    var host = document.querySelector("[data-product]");
    if (!host) return;
    document.title = p.name + " · ACRO STORE";
    host.innerHTML = '' +
      '<div class="pd__gallery">' + thumb(p, true) + '</div>' +
      '<div class="pd__info">' +
        '<p class="pd__cat">' + catName(p.cat) + '</p>' +
        '<h1 class="pd__name">' + p.name + '</h1>' +
        '<div class="pd__meta">' + stars(p.rate) + '<b>' + p.rate.toFixed(1) + '</b><span>· 후기 ' + p.reviews.toLocaleString("ko-KR") + '개</span></div>' +
        '<p class="pd__summary">' + p.summary + '</p>' +
        '<div class="pd__price"><span class="off">' + discountPct(p) + '%</span><span class="sale">' + won(p.sale) + '</span><span class="orig">' + won(p.price) + '</span></div>' +
        '<ul class="pd__promise"><li>블루투스 전용 · 무계정</li><li>DC 36V 저전압 안전</li><li>엣지컴퍼니 직접 시공·A/S</li></ul>' +
        '<div class="pd__qty"><button data-q="-1">−</button><input data-qty value="1" inputmode="numeric"/><button data-q="1">+</button></div>' +
        '<div class="pd__actions">' +
          '<button class="btn btn--line" data-add>장바구니</button>' +
          '<button class="btn btn--primary" data-buy>바로 구매</button>' +
        '</div>' +
        '<p class="pd__ship">무료배송 · 평일 14시 이전 주문 시 당일 출고</p>' +
      '</div>';

    var qtyEl = host.querySelector("[data-qty]");
    host.querySelectorAll("[data-q]").forEach(function (b) {
      b.addEventListener("click", function () {
        var v = Math.max(1, (parseInt(qtyEl.value, 10) || 1) + parseInt(b.dataset.q, 10));
        qtyEl.value = v;
      });
    });
    host.querySelector("[data-add]").addEventListener("click", function () {
      addToCart(p.id, parseInt(qtyEl.value, 10) || 1);
      if (confirm("장바구니에 담았습니다. 장바구니로 이동할까요?")) location.href = "cart.html";
    });
    host.querySelector("[data-buy]").addEventListener("click", function () {
      addToCart(p.id, parseInt(qtyEl.value, 10) || 1); location.href = "cart.html";
    });

    renderGrid(document.querySelector("[data-grid=related]"),
      PRODUCTS.filter(function (x){return x.cat===p.cat && x.id!==p.id;}).concat(PRODUCTS.filter(function(x){return x.id!==p.id;})).slice(0, 4));
  }

  function renderCart() {
    var host = document.querySelector("[data-cart]");
    if (!host) return;
    var cart = getCart();
    if (!cart.length) { host.innerHTML = '<p class="cart-empty">장바구니가 비어 있습니다.<br><a href="category.html">상품 보러 가기 →</a></p>'; return; }
    var rows = "", total = 0;
    cart.forEach(function (line) {
      var p = PRODUCTS.find(function (x){return x.id===line.id;}); if (!p) return;
      var sum = p.sale * line.qty; total += sum;
      rows += '<div class="cartrow" data-id="' + p.id + '">' +
        '<div class="cartrow__thumb">' + thumb(p) + '</div>' +
        '<div class="cartrow__info"><a href="product.html?id=' + p.id + '">' + p.name + '</a><span>' + won(p.sale) + '</span></div>' +
        '<div class="cartrow__qty"><button data-cq="-1">−</button><b>' + line.qty + '</b><button data-cq="1">+</button></div>' +
        '<div class="cartrow__sum">' + won(sum) + '</div>' +
        '<button class="cartrow__del" data-del aria-label="삭제">✕</button>' +
      '</div>';
    });
    host.innerHTML = rows +
      '<div class="cart-total"><span>총 결제금액</span><b>' + won(total) + '</b></div>' +
      '<button class="btn btn--primary btn--lg cart-checkout">주문하기</button>' +
      '<p class="cart-note">※ 데모 화면입니다. 실제 결제는 스마트스토어/박람회에서 진행됩니다.</p>';

    host.querySelectorAll(".cartrow").forEach(function (row) {
      var id = row.dataset.id;
      row.querySelectorAll("[data-cq]").forEach(function (b) {
        b.addEventListener("click", function () {
          var c = getCart(); var l = c.find(function (x){return x.id===id;});
          l.qty = Math.max(1, l.qty + parseInt(b.dataset.cq, 10)); setCart(c); renderCart();
        });
      });
      row.querySelector("[data-del]").addEventListener("click", function () {
        setCart(getCart().filter(function (x){return x.id!==id;})); renderCart();
      });
    });
    var co = host.querySelector(".cart-checkout");
    if (co) co.addEventListener("click", function () { alert("데모 주문이 접수되었습니다. 감사합니다, 엣지님!"); });
  }

  /* ---------- 히어로 배너 슬라이더 ---------- */
  function startSlider() {
    var slider = document.querySelector("[data-slider]");
    if (!slider) return;
    var slides = slider.querySelectorAll(".slide");
    var dots = slider.querySelectorAll(".slide-dot");
    var i = 0, timer;
    function go(n) {
      i = (n + slides.length) % slides.length;
      slides.forEach(function (s, k){ s.classList.toggle("on", k === i); });
      dots.forEach(function (d, k){ d.classList.toggle("on", k === i); });
    }
    dots.forEach(function (d, k){ d.addEventListener("click", function (){ go(k); reset(); }); });
    var prev = slider.querySelector("[data-prev]"), next = slider.querySelector("[data-next]");
    if (prev) prev.addEventListener("click", function (){ go(i-1); reset(); });
    if (next) next.addEventListener("click", function (){ go(i+1); reset(); });
    function reset(){ clearInterval(timer); timer = setInterval(function (){ go(i+1); }, 5000); }
    go(0); reset();
  }

  /* ---------- 부트스트랩 ---------- */
  document.addEventListener("DOMContentLoaded", function () {
    buildGNB(); wireSearch(); wireMobile(); updateCartCount();
    var page = document.body.getAttribute("data-page");
    if (page === "home") renderHome();
    else if (page === "category") renderCategory();
    else if (page === "product") renderProduct();
    else if (page === "cart") renderCart();
  });

  /* 외부에서 쓸 수 있게 노출 */
  window.ACRO = { PRODUCTS: PRODUCTS, CATEGORIES: CATEGORIES };
})();

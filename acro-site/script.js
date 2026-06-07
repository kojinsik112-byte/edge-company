/* ACRO Brand Site — script.js */
(function () {
  "use strict";

  var nav = document.getElementById("nav");
  var burger = document.getElementById("burger");

  /* 스크롤 시 네비게이션 배경 전환 */
  function onScroll() {
    if (window.scrollY > 40) nav.classList.add("scrolled");
    else nav.classList.remove("scrolled");
  }
  window.addEventListener("scroll", onScroll, { passive: true });
  onScroll();

  /* 모바일 메뉴 토글 */
  if (burger) {
    burger.addEventListener("click", function () {
      var open = nav.classList.toggle("open");
      burger.setAttribute("aria-expanded", open ? "true" : "false");
    });
    nav.querySelectorAll(".nav__links a").forEach(function (a) {
      a.addEventListener("click", function () {
        nav.classList.remove("open");
        burger.setAttribute("aria-expanded", "false");
      });
    });
  }

  /* 유튜브 리뷰 영상: data-id 가 있으면 클릭 시 임베드 재생.
     실제 영상 ID를 index.html 의 data-id 속성에 채워 넣으세요. */
  document.querySelectorAll(".rev").forEach(function (btn) {
    btn.addEventListener("click", function () {
      var id = btn.getAttribute("data-id");
      if (!id) {
        alert("리뷰 영상 ID가 아직 등록되지 않았습니다.\nindex.html 의 data-id 속성에 유튜브 영상 ID를 넣어주세요.");
        return;
      }
      var thumb = btn.querySelector(".rev__thumb");
      thumb.innerHTML =
        '<iframe src="https://www.youtube.com/embed/' + id +
        '?autoplay=1&rel=0" title="ACRO 리뷰 영상" allow="autoplay; encrypted-media" allowfullscreen></iframe>';
    });
  });

  /* 스크롤 등장 애니메이션 (선택적, 가벼운 fade-up) */
  if ("IntersectionObserver" in window) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (e.isIntersecting) {
          e.target.style.opacity = 1;
          e.target.style.transform = "none";
          io.unobserve(e.target);
        }
      });
    }, { threshold: 0.12 });

    document.querySelectorAll(".pcard, .prod, .moat__item, .buy__card, .why__row, .rev").forEach(function (el) {
      el.style.opacity = 0;
      el.style.transform = "translateY(24px)";
      el.style.transition = "opacity .6s ease, transform .6s cubic-bezier(.22,.61,.36,1)";
      io.observe(el);
    });
  }
})();

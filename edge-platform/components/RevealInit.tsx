"use client";

import { useEffect } from "react";

// .reveal 요소를 스크롤 진입 시 부드럽게 등장시킨다.
// 안전 설계: 관찰자가 한 번 놓쳐도 화면 안에 들어온 요소는 스크롤/로드 시 강제로 표시한다.
// (어떤 경우에도 '빈 화면'으로 멈추지 않게 — JS 없으면 CSS 폴백으로 항상 보임)
export default function RevealInit() {
  useEffect(() => {
    const root = document.documentElement;
    root.classList.add("reveal-ready");
    const els = Array.from(document.querySelectorAll<HTMLElement>(".reveal"));
    if (els.length === 0) return;

    const show = (el: Element) => el.classList.add("is-visible");

    // 화면 안(또는 막 들어오는) 요소를 즉시 표시 — 관찰자 누락 대비 안전망
    const revealInView = () => {
      const vh = window.innerHeight || document.documentElement.clientHeight;
      for (const el of els) {
        if (el.classList.contains("is-visible")) continue;
        const r = el.getBoundingClientRect();
        if (r.top < vh - 40 && r.bottom > 0) show(el);
      }
    };

    if (!("IntersectionObserver" in window)) {
      els.forEach(show);
      return;
    }

    const io = new IntersectionObserver(
      (entries) => {
        for (const e of entries) {
          if (e.isIntersecting) {
            show(e.target);
            io.unobserve(e.target);
          }
        }
      },
      { rootMargin: "0px 0px -40px 0px", threshold: 0 },
    );
    els.forEach((el) => io.observe(el));

    // 마운트 직후 + 스크롤/리사이즈/이미지로드 시 화면 안 요소 강제 표시
    revealInView();
    const onScroll = () => revealInView();
    window.addEventListener("scroll", onScroll, { passive: true });
    window.addEventListener("resize", onScroll);
    window.addEventListener("load", onScroll);

    return () => {
      io.disconnect();
      window.removeEventListener("scroll", onScroll);
      window.removeEventListener("resize", onScroll);
      window.removeEventListener("load", onScroll);
    };
  }, []);

  return null;
}

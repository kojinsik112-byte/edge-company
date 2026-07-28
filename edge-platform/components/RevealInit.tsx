"use client";

import { useEffect } from "react";
import { usePathname } from "next/navigation";

// .reveal 요소를 스크롤 진입 시 부드럽게 등장시킨다.
// 안전 설계: 관찰자가 한 번 놓쳐도 화면 안에 들어온 요소는 스크롤/로드 시 강제로 표시한다.
// (어떤 경우에도 '빈 화면'으로 멈추지 않게 — JS 없으면 CSS 폴백으로 항상 보임)
// 주의: 레이아웃에 마운트되므로 클라이언트 라우팅으로 페이지가 바뀌면 새 .reveal 요소가 생긴다
//       → pathname 을 의존성으로 걸어 페이지 이동마다 다시 수집·관찰한다 (안 하면 이동 후 빈 화면).
export default function RevealInit() {
  const pathname = usePathname();

  useEffect(() => {
    const root = document.documentElement;
    root.classList.add("reveal-ready");

    const show = (el: Element) => el.classList.add("is-visible");
    const query = () => Array.from(document.querySelectorAll<HTMLElement>(".reveal:not(.is-visible)"));

    // 화면 안(또는 막 들어오는) 요소를 즉시 표시 — 관찰자 누락 대비 안전망
    const revealInView = () => {
      const vh = window.innerHeight || document.documentElement.clientHeight;
      for (const el of query()) {
        const r = el.getBoundingClientRect();
        if (r.top < vh - 40 && r.bottom > 0) show(el);
      }
    };

    if (!("IntersectionObserver" in window)) {
      query().forEach(show);
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
    query().forEach((el) => io.observe(el));

    // 마운트/페이지 이동 직후 + 스크롤/리사이즈/이미지로드 시 화면 안 요소 강제 표시
    revealInView();
    // 렌더 직후 레이아웃이 늦게 잡히는 경우 대비 한 번 더
    const t = window.setTimeout(revealInView, 300);
    // 최후 안전망: 5초 뒤에도 안 풀린 요소는 전부 표시 (빈 화면 절대 금지)
    const tAll = window.setTimeout(() => query().forEach(show), 5000);
    const onScroll = () => revealInView();
    window.addEventListener("scroll", onScroll, { passive: true });
    window.addEventListener("resize", onScroll);
    window.addEventListener("load", onScroll);

    return () => {
      io.disconnect();
      window.clearTimeout(t);
      window.clearTimeout(tAll);
      window.removeEventListener("scroll", onScroll);
      window.removeEventListener("resize", onScroll);
      window.removeEventListener("load", onScroll);
    };
  }, [pathname]);

  return null;
}

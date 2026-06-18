"use client";

import { useEffect } from "react";

// .reveal 요소를 스크롤 진입 시 부드럽게 등장시킨다. (JS 없으면 항상 보임 — 안전)
export default function RevealInit() {
  useEffect(() => {
    const root = document.documentElement;
    root.classList.add("reveal-ready");
    const els = Array.from(document.querySelectorAll<HTMLElement>(".reveal"));
    if (!("IntersectionObserver" in window) || els.length === 0) {
      els.forEach((el) => el.classList.add("is-visible"));
      return;
    }
    const io = new IntersectionObserver(
      (entries) => {
        entries.forEach((e) => {
          if (e.isIntersecting) {
            e.target.classList.add("is-visible");
            io.unobserve(e.target);
          }
        });
      },
      { rootMargin: "0px 0px -8% 0px", threshold: 0.08 },
    );
    els.forEach((el) => io.observe(el));
    return () => io.disconnect();
  });

  return null;
}

"use client";

import { useCallback, useEffect, useRef, useState } from "react";

// 가로 스크롤 줄: 마우스 드래그 + 좌우 화살표 버튼 + 가장자리 페이드.
// 항목이 넘칠 때만 화살표/페이드가 보이고, 끝에 닿으면 그쪽 화살표는 사라진다.
// fade = 섹션 배경색(페이드가 배경과 자연스럽게 섞이도록). 기본 흰색.
export default function ScrollRow({
  children,
  className = "",
  fade = "#ffffff",
}: {
  children: React.ReactNode;
  className?: string;
  fade?: string;
}) {
  const ref = useRef<HTMLDivElement>(null);
  const drag = useRef({ down: false, startX: 0, startLeft: 0 });
  const [left, setLeft] = useState(false);
  const [right, setRight] = useState(false);

  const update = useCallback(() => {
    const el = ref.current;
    if (!el) return;
    setLeft(el.scrollLeft > 8);
    setRight(el.scrollLeft + el.clientWidth < el.scrollWidth - 8);
  }, []);

  useEffect(() => {
    update();
    window.addEventListener("resize", update);
    return () => window.removeEventListener("resize", update);
  }, [update]);

  const by = (d: number) => ref.current?.scrollBy({ left: d, behavior: "smooth" });

  return (
    <div className="relative mx-auto max-w-[1320px]">
      <div
        ref={ref}
        onScroll={update}
        className={`no-scrollbar cursor-grab select-none overflow-x-auto px-6 active:cursor-grabbing ${className}`}
        onMouseDown={(e) => {
          const el = ref.current;
          if (!el) return;
          drag.current = { down: true, startX: e.pageX, startLeft: el.scrollLeft };
        }}
        onMouseMove={(e) => {
          const el = ref.current;
          if (!el || !drag.current.down) return;
          e.preventDefault();
          el.scrollLeft = drag.current.startLeft - (e.pageX - drag.current.startX);
        }}
        onMouseUp={() => (drag.current.down = false)}
        onMouseLeave={() => (drag.current.down = false)}
      >
        {children}
      </div>

      {/* 가장자리 페이드 (배경과 동일 색으로 자연스럽게) */}
      {left && (
        <div className="pointer-events-none absolute inset-y-0 left-0 w-12 md:w-16" style={{ background: `linear-gradient(to right, ${fade}, transparent)` }} />
      )}
      {right && (
        <div className="pointer-events-none absolute inset-y-0 right-0 w-12 md:w-16" style={{ background: `linear-gradient(to left, ${fade}, transparent)` }} />
      )}

      {/* 좌우 화살표 (넘칠 때만, 데스크탑/태블릿) */}
      {left && (
        <button
          aria-label="이전"
          onClick={() => by(-340)}
          className="absolute left-1 top-1/2 hidden h-11 w-11 -translate-y-1/2 items-center justify-center rounded-full border border-line bg-white/95 text-ink shadow-[0_6px_20px_-8px_rgba(15,35,66,0.35)] backdrop-blur transition hover:bg-white sm:flex"
        >
          <Chevron dir="left" />
        </button>
      )}
      {right && (
        <button
          aria-label="다음"
          onClick={() => by(340)}
          className="absolute right-1 top-1/2 hidden h-11 w-11 -translate-y-1/2 items-center justify-center rounded-full border border-line bg-white/95 text-ink shadow-[0_6px_20px_-8px_rgba(15,35,66,0.35)] backdrop-blur transition hover:bg-white sm:flex"
        >
          <Chevron dir="right" />
        </button>
      )}
    </div>
  );
}

function Chevron({ dir }: { dir: "left" | "right" }) {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2} className="h-5 w-5">
      <path d={dir === "left" ? "M15 6l-6 6 6 6" : "M9 6l6 6-6 6"} strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  );
}

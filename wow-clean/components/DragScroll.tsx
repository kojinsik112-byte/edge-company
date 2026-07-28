"use client";

import { useRef } from "react";

// 마우스로 클릭 후 좌우 드래그하여 가로 스크롤 (모바일은 기본 터치 스크롤)
export default function DragScroll({ children, className = "" }: { children: React.ReactNode; className?: string }) {
  const ref = useRef<HTMLDivElement>(null);
  const st = useRef({ down: false, startX: 0, startLeft: 0 });

  return (
    <div
      ref={ref}
      className={`cursor-grab select-none active:cursor-grabbing ${className}`}
      onMouseDown={(e) => {
        const el = ref.current;
        if (!el) return;
        st.current = { down: true, startX: e.pageX, startLeft: el.scrollLeft };
      }}
      onMouseMove={(e) => {
        const el = ref.current;
        if (!el || !st.current.down) return;
        e.preventDefault();
        el.scrollLeft = st.current.startLeft - (e.pageX - st.current.startX);
      }}
      onMouseUp={() => (st.current.down = false)}
      onMouseLeave={() => (st.current.down = false)}
    >
      {children}
    </div>
  );
}

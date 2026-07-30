"use client";

import { useEffect, useRef, useState } from "react";

export default function HeroVideo({ src, poster }: { src: string; poster?: string }) {
  const ref = useRef<HTMLVideoElement>(null);
  const [muted, setMuted] = useState(true);

  useEffect(() => {
    const v = ref.current;
    if (!v) return;
    // 버튼 상태를 실제 영상 상태와 동기화
    const sync = () => setMuted(v.muted);
    v.addEventListener("volumechange", sync);

    // 가능하면 처음부터 소리 ON 시도 (브라우저가 허용하면)
    v.muted = false;
    v.play().catch(() => {
      // 차단되면 무음으로 재생 유지
      v.muted = true;
      v.play().catch(() => {});
    });

    // 방문자가 화면을 '탭/클릭'하면 소리 ON. 스크롤(wheel)은 제외 —
    // 스크롤로 소리 켜기를 시도하면 브라우저가 막아 재생이 멈추기 때문.
    // 소리 켜기가 막히면 음소거 상태로 재생을 계속 유지한다.
    const onGesture = () => {
      v.muted = false;
      v.play().catch(() => {
        v.muted = true;
        v.play().catch(() => {});
      });
      cleanup();
    };
    const evts = ["pointerdown", "keydown", "touchstart"] as const;
    const cleanup = () => evts.forEach((e) => window.removeEventListener(e, onGesture));
    evts.forEach((e) => window.addEventListener(e, onGesture, { passive: true }));

    return () => {
      v.removeEventListener("volumechange", sync);
      cleanup();
    };
  }, []);

  function toggle() {
    const v = ref.current;
    if (!v) return;
    v.muted = !v.muted;
    if (!v.muted) v.play().catch(() => {});
  }

  return (
    <>
      <video ref={ref} src={src} autoPlay muted loop playsInline poster={poster} className="absolute inset-0 h-full w-full object-cover" />
      <button
        onClick={toggle}
        aria-label={muted ? "소리 켜기" : "소리 끄기"}
        className="absolute bottom-4 right-4 z-20 flex items-center gap-1.5 rounded-full bg-black/45 px-4 py-2.5 text-[13px] font-semibold text-white backdrop-blur-md transition hover:bg-black/65"
      >
        {muted ? (
          <>
            <svg viewBox="0 0 24 24" className="h-[18px] w-[18px]" fill="none" stroke="currentColor" strokeWidth={1.8} strokeLinecap="round" strokeLinejoin="round"><path d="M11 5 6 9H2v6h4l5 4V5z" /><path d="m23 9-6 6M17 9l6 6" /></svg>
            소리 켜기
          </>
        ) : (
          <>
            <svg viewBox="0 0 24 24" className="h-[18px] w-[18px]" fill="none" stroke="currentColor" strokeWidth={1.8} strokeLinecap="round" strokeLinejoin="round"><path d="M11 5 6 9H2v6h4l5 4V5z" /><path d="M15.5 8.5a5 5 0 0 1 0 7M19 5a9 9 0 0 1 0 14" /></svg>
            소리 끄기
          </>
        )}
      </button>
    </>
  );
}

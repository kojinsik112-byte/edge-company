"use client";

import { useRef, useState } from "react";

export default function HeroVideo({ src, poster }: { src: string; poster?: string }) {
  const ref = useRef<HTMLVideoElement>(null);
  const [muted, setMuted] = useState(true);

  function toggle() {
    const v = ref.current;
    if (!v) return;
    v.muted = !v.muted;
    setMuted(v.muted);
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

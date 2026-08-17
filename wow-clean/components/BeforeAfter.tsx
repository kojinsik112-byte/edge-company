"use client";

import { useRef, useState } from "react";
import Image from "next/image";

/** Before/After 드래그 비교 슬라이더 — 시공 전후를 한 장면에서 (사진 없으면 일러스트 폴백) */
export default function BeforeAfter({ before, after }: { before?: string; after?: string }) {
  const [pos, setPos] = useState(50);
  const ref = useRef<HTMLDivElement>(null);

  const move = (clientX: number) => {
    const el = ref.current;
    if (!el) return;
    const r = el.getBoundingClientRect();
    setPos(Math.min(96, Math.max(4, ((clientX - r.left) / r.width) * 100)));
  };

  return (
    <section className="bg-surface py-16 md:py-24">
      <div className="reveal mx-auto max-w-[1080px] px-6">
        <div className="mx-auto mb-10 max-w-[640px] text-center">
          <p className="kicker">Before &amp; After</p>
          <h2 className="mt-3 text-[26px] font-extrabold text-ink md:text-[32px]">직접 밀어서 확인해 보세요</h2>
          <p className="mt-3 text-[14.5px] text-muted">가운데 손잡이를 좌우로 움직이면 시공 전후가 비교됩니다.</p>
        </div>

        <div
          ref={ref}
          className="relative mx-auto aspect-[16/8] w-full cursor-ew-resize touch-none select-none overflow-hidden rounded-3xl border border-line shadow-[0_18px_50px_rgba(18,52,94,0.14)]"
          onPointerDown={(e) => { (e.target as Element).setPointerCapture?.(e.pointerId); move(e.clientX); }}
          onPointerMove={(e) => e.buttons > 0 && move(e.clientX)}
          role="slider"
          aria-label="시공 전후 비교"
          aria-valuenow={Math.round(pos)}
          aria-valuemin={0}
          aria-valuemax={100}
        >
          {/* AFTER (아래층 — 전체) */}
          <div className="absolute inset-0">
            {after ? (
              <Image src={after} alt="시공 후 — 깨끗해진 배수" fill sizes="1080px" className="object-cover" />
            ) : (
              <div className="absolute inset-0 bg-[linear-gradient(135deg,#eaf6ff,#f6fbff_55%,#e3f2fd)]">
                <div className="absolute inset-0 flex flex-col items-center justify-center">
                  <span className="text-[64px] md:text-[88px]" aria-hidden>✨🚿</span>
                  <p className="mt-3 text-[18px] font-extrabold text-navy md:text-[24px]">콸콸 — 새 배관처럼</p>
                  <p className="mt-1 text-[13px] font-medium text-gold-d">고압세척 후 물길이 완전히 열린 상태</p>
                </div>
              </div>
            )}
            <span className="absolute right-4 top-4 rounded-full bg-gold px-3.5 py-1.5 text-[12.5px] font-extrabold text-white">AFTER · 시공 후</span>
          </div>

          {/* BEFORE (위층 — 클립) */}
          <div className="absolute inset-0" style={{ clipPath: `inset(0 ${100 - pos}% 0 0)` }}>
            {before ? (
              <Image src={before} alt="시공 전 — 막힌 배수" fill sizes="1080px" className="object-cover" />
            ) : (
              <div className="absolute inset-0 bg-[linear-gradient(135deg,#2b3440,#3a4552_55%,#232b34)]">
                <div className="absolute inset-0 flex flex-col items-center justify-center">
                  <span className="text-[64px] md:text-[88px]" aria-hidden>🌊🚽</span>
                  <p className="mt-3 text-[18px] font-extrabold text-white md:text-[24px]">역류 직전 — 물이 안 내려감</p>
                  <p className="mt-1 text-[13px] font-medium text-white/60">기름 슬러지 · 이물질로 관로 협착</p>
                </div>
              </div>
            )}
            <span className="absolute left-4 top-4 rounded-full bg-ink/80 px-3.5 py-1.5 text-[12.5px] font-extrabold text-white">BEFORE · 시공 전</span>
          </div>

          {/* 핸들 */}
          <div className="absolute inset-y-0" style={{ left: `${pos}%` }}>
            <div className="absolute inset-y-0 -ml-px w-[2px] bg-white shadow-[0_0_12px_rgba(0,0,0,0.35)]" />
            <div className="absolute top-1/2 -ml-[22px] -mt-[22px] flex h-[44px] w-[44px] items-center justify-center rounded-full border-2 border-white bg-gold text-white shadow-lg">
              <svg viewBox="0 0 24 24" className="h-5 w-5" fill="none" stroke="currentColor" strokeWidth={2.6} strokeLinecap="round" strokeLinejoin="round" aria-hidden>
                <path d="M8 7 3 12l5 5M16 7l5 5-5 5" />
              </svg>
            </div>
          </div>
        </div>

        <p className="mt-6 text-center text-[13px] text-muted">실제 현장 사진은 <a href="/cases" className="font-semibold text-gold-d underline-offset-2 hover:underline">시공사례</a>에서 더 보실 수 있습니다.</p>
      </div>
    </section>
  );
}

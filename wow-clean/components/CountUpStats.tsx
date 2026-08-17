"use client";

import { useEffect, useRef, useState } from "react";

/** 누적 시공 카운터 + 쭉 올라가는 월별 그래프 (스크롤 진입 시 애니메이션) */
const BARS = [34, 42, 39, 51, 58, 66, 72, 81, 90, 97, 108, 118]; // 최근 12개월 상대 추이
const MONTHS = ["9월", "10월", "11월", "12월", "1월", "2월", "3월", "4월", "5월", "6월", "7월", "8월"];
const TARGET = 8500;

export default function CountUpStats() {
  const [on, setOn] = useState(false);
  const [n, setN] = useState(0);
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const el = ref.current;
    if (!el) return;
    const io = new IntersectionObserver(([e]) => e.isIntersecting && setOn(true), { threshold: 0.3 });
    io.observe(el);
    return () => io.disconnect();
  }, []);

  useEffect(() => {
    if (!on) return;
    const t0 = performance.now();
    const dur = 1800;
    let raf = 0;
    const tick = (t: number) => {
      const p = Math.min(1, (t - t0) / dur);
      setN(Math.round(TARGET * (1 - Math.pow(1 - p, 3))));
      if (p < 1) raf = requestAnimationFrame(tick);
    };
    raf = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(raf);
  }, [on]);

  return (
    <section ref={ref} className="relative overflow-hidden bg-navy-d py-16 text-white md:py-24">
      <div
        className="pointer-events-none absolute inset-0 opacity-[0.14]"
        style={{ backgroundImage: "url(/img/photo/bg-tools.jpg)", backgroundSize: "cover", backgroundPosition: "center" }}
        aria-hidden
      />
      <div className="pointer-events-none absolute inset-0 bg-[radial-gradient(900px_400px_at_50%_-10%,rgba(31,131,224,0.35),transparent_65%)]" aria-hidden />

      <div className="relative mx-auto grid max-w-[1320px] items-center gap-12 px-6 md:grid-cols-2">
        {/* 좌: 카운터 */}
        <div>
          <p className="text-[11px] font-bold uppercase tracking-[0.22em] text-[#7cc0ff]">Track Record</p>
          <h2 className="mt-3 text-[26px] font-extrabold md:text-[32px]">숫자가 말하는 와우클린</h2>
          <p className="mt-6 text-[15px] text-white/60">누적 시공</p>
          <p className="text-[64px] font-extrabold leading-none tracking-tight text-white md:text-[84px]">
            {n.toLocaleString()}
            <span className="text-[#7cc0ff]">+</span>
            <span className="ml-2 align-middle text-[22px] font-bold text-white/70 md:text-[26px]">건</span>
          </p>
          <div className="mt-8 grid max-w-[440px] grid-cols-3 gap-3">
            {[
              ["24시간", "연중무휴 접수"],
              ["전국", "출동 네트워크"],
              ["당일", "긴급 대응 원칙"],
            ].map(([b, s]) => (
              <div key={b} className="rounded-xl border border-white/12 bg-white/[0.07] px-4 py-3.5 text-center">
                <p className="text-[18px] font-extrabold">{b}</p>
                <p className="mt-0.5 text-[11.5px] text-white/55">{s}</p>
              </div>
            ))}
          </div>
        </div>

        {/* 우: 쭉 올라가는 그래프 */}
        <div className="rounded-3xl border border-white/12 bg-white/[0.06] p-6 backdrop-blur-sm md:p-8">
          <div className="flex items-baseline justify-between">
            <p className="text-[15px] font-bold">월별 시공 추이</p>
            <p className="text-[12px] font-semibold text-emerald-300">▲ 꾸준한 상승세</p>
          </div>
          <div className="mt-6 flex h-[220px] items-end gap-[6px] md:gap-2">
            {BARS.map((h, i) => (
              <div key={i} className="group relative flex h-full flex-1 items-end">
                <div
                  className="w-full rounded-t-md bg-gradient-to-t from-gold-d to-[#7cc0ff] transition-transform duration-700 ease-out"
                  style={{
                    height: `${(h / 120) * 100}%`,
                    transform: on ? "scaleY(1)" : "scaleY(0)",
                    transformOrigin: "bottom",
                    transitionDelay: `${i * 90}ms`,
                  }}
                />
              </div>
            ))}
          </div>
          <div className="mt-2 flex gap-[6px] md:gap-2">
            {MONTHS.map((m, i) => (
              <p key={m} className={`flex-1 text-center text-[10px] ${i % 2 ? "text-white/45" : "text-white/70"}`}>{m}</p>
            ))}
          </div>
          <p className="mt-4 text-center text-[11.5px] text-white/45">최근 12개월 시공 건수 상대 추이</p>
        </div>
      </div>
    </section>
  );
}

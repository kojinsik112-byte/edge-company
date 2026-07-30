"use client";

import Image from "next/image";
import { useState } from "react";

// Kelvin → RGB (Tanner Helland 근사식) — 색온도를 화면 색으로 변환
function kelvinRGB(k: number): [number, number, number] {
  const t = k / 100;
  let r: number, g: number, b: number;
  if (t <= 66) {
    r = 255;
    g = 99.47 * Math.log(t) - 161.12;
  } else {
    r = 329.7 * Math.pow(t - 60, -0.1332);
    g = 288.12 * Math.pow(t - 60, -0.0755);
  }
  if (t >= 66) b = 255;
  else if (t <= 19) b = 0;
  else b = 138.52 * Math.log(t - 10) - 305.04;
  const c = (v: number) => Math.max(0, Math.min(255, Math.round(v)));
  return [c(r), c(g), c(b)];
}

function moodLabel(k: number): { name: string; mood: string } {
  if (k < 3100) return { name: "전구색 2700K", mood: "아늑한 저녁 · 호텔 라운지" };
  if (k < 3800) return { name: "전구색 3500K", mood: "따뜻하고 편안한 거실" };
  if (k < 4600) return { name: "주백색 4000K", mood: "자연스러운 생활 조명" };
  if (k < 5600) return { name: "주백색 5000K", mood: "산뜻하고 환한 공간" };
  return { name: "주광색 6500K", mood: "시원하고 또렷한 집중광" };
}

const PRESETS = [
  { label: "아늑한 저녁", k: 2700, dim: 55 },
  { label: "편안한 거실", k: 3500, dim: 80 },
  { label: "밝은 주방", k: 5000, dim: 100 },
  { label: "집중 모드", k: 6500, dim: 100 },
];

export default function LightSimulator({
  image = "/img/sofa.webp",
  title = "색온도를 직접 바꿔보세요",
  subtitle = "전구색부터 주광색까지 — 슬라이더를 움직여 우리 집 조명을 미리 경험하세요.",
}: {
  image?: string;
  title?: string;
  subtitle?: string;
}) {
  const [k, setK] = useState(3500);
  const [dim, setDim] = useState(85);
  const [rr, gg, bb] = kelvinRGB(k);
  const { name, mood } = moodLabel(k);
  const d = dim / 100;

  return (
    <section className="bg-warm py-16 md:py-24">
      <div className="reveal mx-auto max-w-[1100px] px-6">
        <div className="mx-auto mb-9 max-w-[680px] text-center">
          <p className="kicker">Light Experience</p>
          <h2 className="mt-3 text-[26px] font-display font-extrabold leading-snug text-ink md:text-[32px]">{title}</h2>
          <p className="mt-3 text-[16px] leading-relaxed text-muted">{subtitle}</p>
        </div>

        {/* 시뮬레이션 화면 */}
        <div className="relative overflow-hidden rounded-[28px] shadow-[0_30px_70px_-30px_rgba(15,35,66,0.4)] ring-1 ring-line">
          <div className="relative aspect-[16/10]" style={{ filter: `brightness(${0.52 + d * 0.48}) contrast(${1 + (1 - d) * 0.06}) saturate(${0.96 + d * 0.12})` }}>
            <Image src={image} alt="조명 색온도 시뮬레이션" fill sizes="(max-width:1100px) 100vw, 1100px" className="object-cover" style={{ objectPosition: "center 68%" }} />
            {/* 색온도 — 곱하기 블렌드(빛이 공간을 물들이듯, 시원한 빛에서도 안 뜸) */}
            <div className="pointer-events-none absolute inset-0 transition-colors duration-300" style={{ backgroundColor: `rgb(${rr},${gg},${bb})`, mixBlendMode: "multiply", opacity: 0.3 }} />
            {/* 디밍 — 가장자리부터 어두워지는 '빛 고임' 효과 */}
            <div className="pointer-events-none absolute inset-0 transition-opacity duration-300" style={{ background: `radial-gradient(ellipse at 50% 40%, transparent 28%, rgba(8,10,18,${(1 - d) * 0.8}) 100%)` }} />
          </div>

          {/* 상태 배지 */}
          <div className="absolute left-4 top-4 flex items-center gap-2.5 rounded-full bg-black/45 px-4 py-2 backdrop-blur-md">
            <span className="inline-block h-3.5 w-3.5 rounded-full ring-2 ring-white/40" style={{ backgroundColor: `rgb(${rr},${gg},${bb})` }} />
            <span className="text-[13px] font-bold text-white">{name}</span>
            <span className="hidden text-[12px] text-white/60 sm:inline">· {mood}</span>
          </div>
          <div className="absolute right-4 top-4 rounded-full bg-black/45 px-3.5 py-2 text-[12.5px] font-bold text-white backdrop-blur-md">밝기 {dim}%</div>
        </div>

        {/* 컨트롤 */}
        <div className="mt-7 grid gap-6 md:grid-cols-2">
          <div>
            <div className="mb-2 flex items-center justify-between text-[13px] font-semibold text-ink/75">
              <span>색온도 (Color Temperature)</span>
              <span className="text-gold-d">{k}K</span>
            </div>
            <input
              type="range" min={2700} max={6500} step={100} value={k} onChange={(e) => setK(Number(e.target.value))}
              className="ct-slider h-2.5 w-full cursor-pointer appearance-none rounded-full"
              style={{ background: "linear-gradient(90deg,#ff9b4d,#ffd9a8,#fff4e6,#eef4ff,#cfe2ff)" }}
            />
            <div className="mt-1.5 flex justify-between text-[11px] text-muted"><span>따뜻한 빛</span><span>시원한 빛</span></div>
          </div>
          <div>
            <div className="mb-2 flex items-center justify-between text-[13px] font-semibold text-ink/75">
              <span>밝기 (Dimming)</span>
              <span className="text-gold-d">{dim}%</span>
            </div>
            <input
              type="range" min={20} max={100} step={1} value={dim} onChange={(e) => setDim(Number(e.target.value))}
              className="ct-slider h-2.5 w-full cursor-pointer appearance-none rounded-full"
              style={{ background: "linear-gradient(90deg,#cdbfa6,#d4b97a,#fff6df)" }}
            />
            <div className="mt-1.5 flex justify-between text-[11px] text-muted"><span>은은하게</span><span>환하게</span></div>
          </div>
        </div>

        {/* 프리셋 */}
        <div className="mt-7 flex flex-wrap justify-center gap-2.5">
          {PRESETS.map((p) => {
            const active = k === p.k && dim === p.dim;
            return (
              <button key={p.label} onClick={() => { setK(p.k); setDim(p.dim); }}
                className={`rounded-full px-4 py-2 text-[13px] font-bold transition ${active ? "bg-gold text-white shadow-sm" : "border border-line bg-surface text-ink/70 hover:border-gold hover:text-ink"}`}>
                {p.label}
              </button>
            );
          })}
        </div>
        <p className="mt-6 text-center text-[12.5px] text-muted">* 실제 시공은 색온도·디밍을 앱·리모컨으로 자유롭게 조절할 수 있습니다.</p>
      </div>
    </section>
  );
}

"use client";

import Image from "next/image";
import { useEffect, useState } from "react";
import type { Hero, SiteInfo } from "@/lib/settings";

const SYMPTOMS = ["물이 안 내려가나요?", "변기가 역류하나요?", "싱크대에서 냄새 나나요?", "배수구가 꾸르륵대나요?"];

/** 긴급출동형 히어로 — 타이핑 헤드라인 + 실시간 접수 티커 + 물결 애니메이션 */
export default function EmergencyHero({ site, hero }: { site: SiteInfo; hero: Hero }) {
  const tel = `tel:${site.phone.replace(/-/g, "")}`;
  const [today, setToday] = useState<number | null>(null);
  const [dots, setDots] = useState(0);
  const [txt, setTxt] = useState(SYMPTOMS[0]);
  const [idx, setIdx] = useState(0);
  const [del, setDel] = useState(false);

  // 타이핑 애니메이션 (증상 문구 로테이션)
  useEffect(() => {
    const full = SYMPTOMS[idx];
    let t: ReturnType<typeof setTimeout>;
    if (!del) {
      if (txt.length < full.length) t = setTimeout(() => setTxt(full.slice(0, txt.length + 1)), 75);
      else t = setTimeout(() => setDel(true), 1900);
    } else {
      if (txt.length > 0) t = setTimeout(() => setTxt(txt.slice(0, -1)), 32);
      else { setDel(false); setIdx((idx + 1) % SYMPTOMS.length); }
    }
    return () => clearTimeout(t);
  }, [txt, del, idx]);

  useEffect(() => {
    // 날짜 기반 결정적 접수 카운트 (18~34건) + 시간대 가중
    const d = new Date();
    const seed = d.getFullYear() * 372 + (d.getMonth() + 1) * 31 + d.getDate();
    const base = 18 + (seed % 17);
    const hourBoost = Math.min(d.getHours(), 22) / 22;
    setToday(Math.max(3, Math.round(base * (0.35 + 0.65 * hourBoost))));
    const t = setInterval(() => setDots((v) => (v + 1) % 4), 600);
    return () => clearInterval(t);
  }, []);

  const chips = [
    { big: "24시간", small: "연중무휴 출동" },
    { big: "30분~", small: "수도권 평균 도착" },
    { big: "0원", small: "출장 · 견적비" },
    { big: "뒷정리", small: "시공 후 마무리까지" },
  ];

  return (
    <section className="relative overflow-hidden bg-navy-d text-white">
      {/* 배경 — 관리자 업로드 배너 사진(있으면) + 그라디언트 + 물결 */}
      <div className="pointer-events-none absolute inset-0">
        {hero.image && (
          <>
            <Image src={hero.image} alt="" fill priority sizes="100vw" className="hidden object-cover md:block" />
            <Image src={hero.imageMobile || hero.image} alt="" fill priority sizes="100vw" className="object-cover md:hidden" />
            {/* 글자 가독성용 딤 — 사진은 살리고 텍스트는 선명하게 */}
            <div className="absolute inset-0 bg-gradient-to-r from-[#0b1b30]/88 via-[#0b1b30]/62 to-[#0b1b30]/30" />
          </>
        )}
        <div className={`absolute inset-0 bg-[radial-gradient(1100px_540px_at_78%_-10%,rgba(31,131,224,0.45),transparent_60%),radial-gradient(700px_420px_at_8%_110%,rgba(31,131,224,0.28),transparent_60%)] ${hero.image ? "opacity-55" : ""}`} />
        <svg className="absolute bottom-0 left-0 w-[200%] animate-[wave_14s_linear_infinite]" viewBox="0 0 2880 140" fill="none" aria-hidden>
          <path d="M0 90 Q 180 40 360 90 T 720 90 T 1080 90 T 1440 90 T 1800 90 T 2160 90 T 2520 90 T 2880 90 V140 H0 Z" fill="rgba(31,131,224,0.16)" />
          <path d="M0 108 Q 180 70 360 108 T 720 108 T 1080 108 T 1440 108 T 1800 108 T 2160 108 T 2520 108 T 2880 108 V140 H0 Z" fill="rgba(255,255,255,0.06)" />
        </svg>
      </div>

      <div className="relative mx-auto grid max-w-[1320px] gap-10 px-6 pb-20 pt-14 md:grid-cols-[1.15fr_0.85fr] md:pb-28 md:pt-24">
        {/* 좌: 카피 + CTA */}
        <div>
          {/* 실시간 접수 티커 */}
          <div className="inline-flex items-center gap-2.5 rounded-full border border-white/15 bg-white/10 px-4 py-2 backdrop-blur-sm">
            <span className="relative flex h-2.5 w-2.5">
              <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-emerald-400 opacity-75" />
              <span className="relative inline-flex h-2.5 w-2.5 rounded-full bg-emerald-400" />
            </span>
            <span className="text-[13.5px] font-semibold text-white/90">
              오늘 접수 <b className="text-emerald-300">{today ?? "—"}건</b> · 지금 통화 가능{".".repeat(dots)}
            </span>
          </div>

          {/* 헤드라인 — 관리자에 입력한 라이브 텍스트가 있으면 그걸 그대로 쓴다 */}
          {hero.overlayTitle ? (
            <>
              <h1
                className={`mt-6 whitespace-pre-line leading-[1.2] tracking-tight ${hero.overlaySerif ? "font-lux" : ""}`}
                style={{ color: hero.overlayColor || "#ffffff", fontWeight: Number(hero.overlayWeight) || 800, fontSize: `clamp(30px, 7vw, ${hero.overlayTitleSize || 54}px)` }}
              >
                {hero.overlayTitle}
              </h1>
              <p className="mt-4 text-[15px] font-semibold text-[#7cc0ff] md:text-[17px]">
                {txt}
                <span className="ml-1 inline-block w-[3px] animate-[blink_1s_step-start_infinite] bg-[#7cc0ff] align-middle" style={{ height: "0.95em" }} aria-hidden />
              </p>
            </>
          ) : (
            <h1 className="mt-6 text-[34px] font-extrabold leading-[1.18] tracking-tight md:text-[54px]">
              <span className="block min-h-[1.2em]">
                {txt}
                <span className="ml-1 inline-block w-[3px] animate-[blink_1s_step-start_infinite] bg-[#7cc0ff] align-middle" style={{ height: "0.95em" }} aria-hidden />
              </span>
              <span className="text-[#7cc0ff]">전화 한 통</span>이면 끝납니다
            </h1>
          )}
          <p className="mt-5 max-w-[520px] whitespace-pre-line text-[15.5px] leading-relaxed text-white/75 md:text-[17px]">
            {hero.overlaySub || (
              <>
                하수구·변기·싱크대 막힘부터 배관 고압세척까지 — 전문 장비를 갖춘 기사가 바로 출발합니다. 뚫는 것으로 끝내지 않고{" "}
                <b className="text-white">뒷정리까지</b> 와우클린이 책임집니다.
              </>
            )}
          </p>

          {/* CTA */}
          <div className="mt-8 flex flex-wrap items-center gap-3">
            <a
              href={tel}
              className="group inline-flex items-center gap-3 rounded-2xl bg-gold px-7 py-4.5 text-[18px] font-extrabold text-white shadow-[0_10px_30px_rgba(31,131,224,0.45)] transition hover:bg-gold-d md:text-[20px]"
            >
              <svg viewBox="0 0 24 24" className="h-5 w-5 animate-[ring_1.8s_ease-in-out_infinite]" fill="currentColor" aria-hidden>
                <path d="M6.6 10.8c1.4 2.8 3.8 5.1 6.6 6.6l2.2-2.2c.3-.3.7-.4 1-.2 1.1.4 2.3.6 3.6.6.6 0 1 .4 1 1V20c0 .6-.4 1-1 1C10.8 21 3 13.2 3 4c0-.6.4-1 1-1h3.5c.6 0 1 .4 1 1 0 1.2.2 2.4.6 3.6.1.3 0 .7-.2 1l-2.3 2.2z" />
              </svg>
              {site.phone}
            </a>
            <a
              href={site.kakao || "/contact"}
              className="inline-flex items-center gap-2.5 rounded-2xl bg-[#FEE500] px-6 py-4.5 text-[16px] font-bold text-[#191919] transition hover:brightness-95"
            >
              <svg viewBox="0 0 24 24" className="h-5 w-5" fill="currentColor" aria-hidden>
                <path d="M12 3C6.5 3 2 6.5 2 10.8c0 2.7 1.8 5.1 4.5 6.5-.2.7-.7 2.6-.8 3-.1.5.2.5.4.4.2-.1 2.7-1.8 3.8-2.6.7.1 1.4.2 2.1.2 5.5 0 10-3.5 10-7.8S17.5 3 12 3z" />
              </svg>
              카톡 사진 견적
            </a>
          </div>
          <p className="mt-3 text-[12.5px] text-white/55">📷 막힌 곳 사진을 카톡으로 보내주시면 출동 전에 예상 견적을 알려드립니다</p>

          {/* 스탯 칩 */}
          <div className="mt-9 grid max-w-[560px] grid-cols-2 gap-3 sm:grid-cols-4">
            {chips.map((c) => (
              <div key={c.big} className="rounded-xl border border-white/12 bg-white/[0.07] px-4 py-3.5 text-center backdrop-blur-sm">
                <p className="text-[19px] font-extrabold text-white">{c.big}</p>
                <p className="mt-0.5 text-[11.5px] font-medium text-white/60">{c.small}</p>
              </div>
            ))}
          </div>
        </div>

        {/* 우: 증상 셀프 체크 카드 */}
        <div className="hidden md:block">
          <div className="rounded-3xl border border-white/12 bg-white/[0.06] p-7 backdrop-blur-md">
            <p className="text-[13px] font-bold uppercase tracking-[0.18em] text-[#7cc0ff]">Symptom Check</p>
            <h2 className="mt-2 text-[21px] font-extrabold">지금 이런 증상인가요?</h2>
            <ul className="mt-5 space-y-3.5">
              {[
                ["🚿", "샤워하면 발목까지 물이 차오른다", "하수구 막힘 초기 → 오늘 해결 가능"],
                ["🚽", "변기 물이 차올랐다 천천히 빠진다", "이물질 협착 → 압입·스프링 작업"],
                ["🍜", "싱크대에서 꾸르륵 소리·역한 냄새", "기름 슬러지 → 고압세척 권장"],
                ["🏢", "건물 전체 배관이 자주 막힌다", "관로 내시경 진단 → 정기 관리"],
              ].map(([ico, t, d]) => (
                <li key={t as string} className="flex items-start gap-3.5 rounded-xl border border-white/10 bg-white/[0.05] px-4 py-3.5">
                  <span className="text-[22px]" aria-hidden>{ico}</span>
                  <span>
                    <p className="text-[15px] font-bold leading-snug">{t}</p>
                    <p className="mt-0.5 text-[12.5px] text-[#8fc6f8]">{d}</p>
                  </span>
                </li>
              ))}
            </ul>
            <p className="mt-5 text-center text-[12.5px] text-white/55">하나라도 해당되면 미루지 마세요 — 역류가 시작되면 비용이 커집니다</p>
          </div>
        </div>
      </div>

    </section>
  );
}

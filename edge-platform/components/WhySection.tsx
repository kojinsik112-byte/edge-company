import Image from "next/image";
import type { Company } from "@/lib/settings";

// 강점 카드 아이콘 (장식용 기본값 — 카드 순서대로 사용, 텍스트는 관리자 편집)
const ICONS = [
  "M3 9.5 12 4l9 5.5M5 10.5V20h14v-9.5M9.5 20v-5h5v5",
  "M4 19V5m0 14h16M8 19v-6m4 6V9m4 10v-9",
  "M12 3l7 3v5c0 4.5-3 8.3-7 10-4-1.7-7-5.5-7-10V6zM9.3 12l1.8 1.8 3.6-3.6",
  "M8 3h8a1 1 0 0 1 1 1v16a1 1 0 0 1-1 1H8a1 1 0 0 1-1-1V4a1 1 0 0 1 1-1zM11 18h2",
];

export default function WhySection({ company }: { company: Company }) {
  const features = company.features?.length ? company.features : [];
  const trust = company.trust?.length ? company.trust : [];
  return (
    <section className="bg-surface py-16 md:py-24">
      <div className="reveal mx-auto max-w-[1320px] px-6">
        <div className="grid items-center gap-10 lg:grid-cols-2 lg:gap-14">
          {/* 좌측 비주얼 */}
          <div className="relative aspect-[4/5] overflow-hidden rounded-[24px] bg-warm md:aspect-[4/4.4]">
            <Image src={company.image} alt={company.heading || "엣지컴퍼니 시공 공간"} fill sizes="(max-width:1024px) 100vw, 560px" className="object-cover" />
          </div>

          {/* 우측 소개 + 강점 카드 */}
          <div>
            {company.eyebrow && <p className="kicker">{company.eyebrow}</p>}
            <h2 className="mt-3 text-[28px] font-extrabold leading-snug text-ink md:text-[36px]">{company.heading}</h2>
            {company.lead && <p className="mt-4 whitespace-pre-line text-[15.5px] leading-relaxed text-muted">{company.lead}</p>}
            {features.length > 0 && (
              <div className="mt-8 grid gap-4 sm:grid-cols-2">
                {features.map((f, i) => (
                  <div key={i} className="rounded-2xl border border-line bg-surface p-6 transition duration-300 hover:-translate-y-1 hover:shadow-[0_22px_45px_-24px_rgba(15,35,66,0.3)]">
                    <span className="flex h-14 w-14 items-center justify-center rounded-full bg-[#f7e8c8] text-gold-d">
                      <svg viewBox="0 0 24 24" className="h-7 w-7" fill="none" stroke="currentColor" strokeWidth={1.6} strokeLinecap="round" strokeLinejoin="round"><path d={ICONS[i % ICONS.length]} /></svg>
                    </span>
                    <h3 className="mt-4 text-[16px] font-bold text-ink">{f.title}</h3>
                    <p className="mt-1.5 text-[13px] leading-relaxed text-muted">{f.desc}</p>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* 신뢰 문구 */}
        {trust.length > 0 && (
          <div className="mt-14 grid grid-cols-2 gap-px overflow-hidden rounded-2xl border border-line bg-line md:grid-cols-4">
            {trust.map((t, i) => (
              <div key={i} className="flex items-center justify-center gap-2.5 bg-surface px-5 py-7 text-center">
                <svg viewBox="0 0 24 24" className="h-5 w-5 shrink-0 text-gold" fill="none" stroke="currentColor" strokeWidth={2.2} strokeLinecap="round" strokeLinejoin="round"><path d="M20 6 9 17l-5-5" /></svg>
                <span className="text-[15px] font-extrabold text-ink">{t}</span>
              </div>
            ))}
          </div>
        )}
      </div>
    </section>
  );
}

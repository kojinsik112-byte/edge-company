import type { SiteInfo } from "@/lib/settings";

/** 투명 요금 원칙 — 고정가 대신 '어떻게 정해지는지'를 공개 (전화 전환 신뢰 장치) */
export default function PricePrinciple({ site }: { site: SiteInfo }) {
  const tel = `tel:${site.phone.replace(/-/g, "")}`;
  const items = [
    { ico: "🚿", name: "하수구 막힘", desc: "욕실 · 베란다 · 마당 배수구", factor: "막힌 깊이 · 이물질 종류" },
    { ico: "🍜", name: "싱크대 막힘", desc: "기름 슬러지 · 음식물 협착", factor: "슬러지 정도 · 배관 길이" },
    { ico: "🚽", name: "변기 막힘", desc: "이물질 · 협착 · 역류", factor: "이물질 종류 · 탈착 필요 여부" },
    { ico: "🧯", name: "배관 고압세척", desc: "건물 · 상가 · 정기 관리", factor: "배관 규모 · 오염도" },
  ];
  return (
    <section className="bg-warm py-16 md:py-24">
      <div className="reveal mx-auto max-w-[1320px] px-6">
        <div className="mx-auto mb-12 max-w-[680px] text-center">
          <p className="kicker">Price</p>
          <h2 className="mt-3 text-[26px] font-extrabold text-ink md:text-[32px]">요금, 이렇게 정해집니다</h2>
          <p className="mt-3 text-[14.5px] leading-relaxed text-muted">
            부르는 게 값인 업체가 많아서, 와우클린은 반대로 합니다 —
            <b className="text-ink"> 출장·견적비 0원, 작업 전 금액 확정, 확정 후 추가 요금 없음.</b>
          </p>
        </div>

        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          {items.map((it) => (
            <div key={it.name} className="rounded-2xl border border-line bg-surface p-6">
              <p className="text-[30px]" aria-hidden>{it.ico}</p>
              <p className="mt-3 text-[17px] font-extrabold text-ink">{it.name}</p>
              <p className="mt-1 text-[13px] text-muted">{it.desc}</p>
              <div className="mt-4 rounded-lg bg-warm px-3.5 py-2.5">
                <p className="text-[11.5px] font-bold uppercase tracking-wide text-gold-d">요금 결정 요인</p>
                <p className="mt-0.5 text-[13px] font-medium text-ink">{it.factor}</p>
              </div>
              <p className="mt-3 text-[12.5px] font-semibold text-emerald-600">출장 · 견적비 0원</p>
            </div>
          ))}
        </div>

        <div className="mx-auto mt-10 max-w-[760px] rounded-2xl border border-line bg-surface p-6 text-center md:p-8">
          <p className="text-[15px] font-bold text-ink">3가지 약속</p>
          <div className="mt-4 grid gap-3 sm:grid-cols-3">
            {[
              ["작업 전 금액 확정", "확인 후 금액을 먼저 말씀드리고 동의 후 시작"],
              ["추가 요금 없음", "확정 금액 외 현장에서 더 붙는 비용 없음"],
              ["안 뚫리면 비용 없음", "해결하지 못한 작업은 청구하지 않습니다"],
            ].map(([t, d]) => (
              <div key={t} className="rounded-xl bg-warm px-4 py-4">
                <p className="text-[14.5px] font-extrabold text-navy">{t}</p>
                <p className="mt-1 text-[12.5px] leading-relaxed text-muted">{d}</p>
              </div>
            ))}
          </div>
          <a href={tel} className="mt-6 inline-flex items-center gap-2 rounded-xl bg-navy px-7 py-3.5 text-[15.5px] font-bold text-white transition hover:bg-navy-d">
            지금 견적 받기 — {site.phone}
          </a>
        </div>
      </div>
    </section>
  );
}

// 히어로 바로 아래 신뢰 스트립 — 전부 사실 기반(면허·상담·A/S·서비스 지역). 과대광고 표현 없음.
const ITEMS = [
  "전기공사업 면허 보유 법인",
  "무료 방문 상담·견적",
  "A/S 책임 시공",
  "울산·부산·포항·경주",
];

export default function TrustBar() {
  return (
    <section className="border-b border-line bg-surface">
      <div className="mx-auto flex max-w-[1320px] flex-wrap items-center justify-center gap-x-8 gap-y-3 px-6 py-5 md:py-6">
        {ITEMS.map((t, i) => (
          <div key={i} className="flex items-center gap-2.5">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2.2} strokeLinecap="round" strokeLinejoin="round" className="h-[17px] w-[17px] shrink-0 text-gold-d">
              <path d="M20 6 9 17l-5-5" />
            </svg>
            <span className="text-[14.5px] font-semibold text-ink">{t}</span>
          </div>
        ))}
      </div>
    </section>
  );
}

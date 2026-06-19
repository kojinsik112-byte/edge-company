const STEPS = [
  { n: "01", title: "상담 신청", desc: "전화·문자·카톡 또는 온라인 상담으로 편하게 문의하세요." },
  { n: "02", title: "무료 방문 실측", desc: "창 사이즈·주름비·레일을 현장에서 정확히 측정합니다." },
  { n: "03", title: "원단 · 견적 제안", desc: "공간에 맞는 원단·색상을 추천하고 투명한 견적으로 안내합니다." },
  { n: "04", title: "맞춤 제작", desc: "선택한 원단으로 창에 딱 맞게 제작합니다." },
  { n: "05", title: "시공 및 A/S", desc: "숙련 기사가 깔끔하게 설치하고 시공 후까지 관리합니다." },
];

export default function ProcessSection() {
  return (
    <section className="bg-warm py-16 md:py-24">
      <div className="reveal mx-auto max-w-[1320px] px-6">
        <div className="mx-auto mb-12 max-w-[640px] text-center">
          <p className="kicker">Process</p>
          <h2 className="mt-3 text-[26px] font-extrabold text-ink md:text-[32px]">상담부터 A/S까지</h2>
          <p className="mt-3 text-[14.5px] text-muted">복잡하지 않게, 정확하게. 엣지리브커튼의 5단계 시공 과정입니다.</p>
        </div>
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-5">
          {STEPS.map((s) => (
            <div key={s.n} className="rounded-2xl border border-line bg-surface p-6 transition hover:-translate-y-1 hover:shadow-[0_22px_45px_-26px_rgba(15,35,66,0.25)]">
              <span className="font-lux text-[24px] font-semibold text-gold">{s.n}</span>
              <h3 className="mt-3 text-[16px] font-bold text-ink">{s.title}</h3>
              <p className="mt-2 text-[13px] leading-relaxed text-muted">{s.desc}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}

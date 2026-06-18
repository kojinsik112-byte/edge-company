const STEPS = [
  { n: "01", title: "상담 신청", desc: "전화·문자·카톡 또는 온라인 상담으로 편하게 문의하세요." },
  { n: "02", title: "현장 실측", desc: "천장고·전기·공간을 확인하고 최적의 방식을 제안합니다." },
  { n: "03", title: "견적 · 디자인 제안", desc: "공간에 맞는 제품과 조명 설계를 투명한 견적으로 안내합니다." },
  { n: "04", title: "전문 시공", desc: "전기공사 면허 보유 시공팀이 안전하고 깔끔하게 설치합니다." },
  { n: "05", title: "사후관리", desc: "시공 후 점검과 A/S까지 책임지고 관리합니다." },
];

export default function ProcessSection() {
  return (
    <section className="bg-warm py-16 md:py-24">
      <div className="reveal mx-auto max-w-[1320px] px-6">
        <div className="mx-auto mb-12 max-w-[640px] text-center">
          <p className="kicker">Process</p>
          <h2 className="mt-3 text-[26px] font-extrabold text-ink md:text-[32px]">상담부터 사후관리까지</h2>
          <p className="mt-3 text-[14.5px] text-muted">복잡하지 않게, 정확하게. 엣지컴퍼니의 5단계 시공 과정입니다.</p>
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

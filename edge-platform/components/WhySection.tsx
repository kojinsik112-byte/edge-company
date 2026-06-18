const CARDS = [
  {
    title: "직접 체험 가능한 쇼룸",
    desc: "실링팬의 바람과 간접조명의 색온도를 울산 쇼룸에서 직접 켜 보고 비교하세요.",
    icon: "M3 9.5 12 4l9 5.5M5 10.5V20h14v-9.5M9.5 20v-5h5v5",
  },
  {
    title: "풍부한 시공 경험",
    desc: "울산·부산·포항·경주 전 지역, 아파트 거실부터 상가까지 다양한 현장 경험.",
    icon: "M4 19V5m0 14h16M8 19v-6m4 6V9m4 10v-9",
  },
  {
    title: "전문 시공 및 사후관리",
    desc: "전기공사업 면허 보유 법인이 직접 시공하고 설치 후 사후관리까지 책임집니다.",
    icon: "M12 3l7 3v5c0 4.5-3 8.3-7 10-4-1.7-7-5.5-7-10V6zM9.3 12l1.8 1.8 3.6-3.6",
  },
  {
    title: "스마트 조명 시스템",
    desc: "실링팬·조명·전동커튼을 앱 하나로. 색온도·밝기를 손끝에서 제어합니다.",
    icon: "M8 3h8a1 1 0 0 1 1 1v16a1 1 0 0 1-1 1H8a1 1 0 0 1-1-1V4a1 1 0 0 1 1-1zM11 18h2",
  },
];

const STATS = [
  ["3종", "ISO 9001·14001·45001 인증"],
  ["울산-00821", "전기공사업 등록 면허"],
  ["22개", "전국 지사 네트워크"],
  ["2022~", "법인 직영 운영"],
];

export default function WhySection() {
  return (
    <section className="bg-surface py-16 md:py-24">
      <div className="mx-auto max-w-[1200px] px-6">
        <div className="mx-auto mb-12 max-w-[680px] text-center">
          <p className="kicker">Why Edge Company</p>
          <h2 className="mt-3 text-[24px] font-bold leading-snug text-ink md:text-[30px]">왜 엣지컴퍼니일까요?</h2>
          <p className="mt-3 text-[15px] leading-relaxed text-muted">
            실링팬과 간접조명을 단순 설치하는 것이 아니라, 고객의 라이프스타일에 맞는 공간의 분위기를 제안합니다.
          </p>
        </div>

        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          {CARDS.map((c) => (
            <div key={c.title} className="rounded-2xl border border-line bg-bg p-7 transition hover:border-gold">
              <span className="flex h-12 w-12 items-center justify-center rounded-xl bg-navy/[0.06] text-navy">
                <svg viewBox="0 0 24 24" className="h-6 w-6" fill="none" stroke="currentColor" strokeWidth={1.6} strokeLinecap="round" strokeLinejoin="round">
                  <path d={c.icon} />
                </svg>
              </span>
              <h3 className="mt-5 text-[16.5px] font-bold text-ink">{c.title}</h3>
              <p className="mt-2 text-[13.5px] leading-relaxed text-muted">{c.desc}</p>
            </div>
          ))}
        </div>

        {/* 신뢰 숫자 영역 */}
        <div className="mt-12 grid grid-cols-2 gap-px overflow-hidden rounded-2xl border border-line bg-line md:grid-cols-4">
          {STATS.map(([num, label]) => (
            <div key={label} className="bg-surface px-5 py-8 text-center">
              <div className="text-[22px] font-extrabold tracking-tight text-navy">{num}</div>
              <div className="mt-2 text-[12.5px] leading-relaxed text-muted">{label}</div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}

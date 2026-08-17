/** 출동~완료 타임라인 — 단계별 실제 소요시간 표기 (경쟁사 6단계 목록의 상위 호환) */
const STEPS = [
  { time: "0분", title: "전화 · 카톡 접수", desc: "증상만 말씀하세요. 사진을 보내주시면 더 정확합니다.", ico: "📞" },
  { time: "~5분", title: "예상 견적 안내", desc: "증상 기준 예상 범위를 먼저 안내 — 숨은 비용 없음.", ico: "💬" },
  { time: "30분~", title: "기사 도착", desc: "가까운 기사 배정, 도착 전 연락드립니다.", ico: "🚐" },
  { time: "+5분", title: "원인 진단 · 금액 확정", desc: "관로 확인 후 작업 전 금액을 확정하고 시작합니다.", ico: "🔍" },
  { time: "10~60분", title: "시공", desc: "고압세척 · 관로 스프링 · 내시경 — 원인부터 제거.", ico: "🛠️" },
  { time: "완료", title: "확인 · 뒷정리", desc: "물 내림 확인, 현장 정리, 재발 방지 안내까지.", ico: "✅" },
];

export default function RescueTimeline() {
  return (
    <section className="bg-navy py-16 text-white md:py-24">
      <div className="reveal mx-auto max-w-[1320px] px-6">
        <div className="mx-auto mb-12 max-w-[640px] text-center">
          <p className="text-[11px] font-bold uppercase tracking-[0.22em] text-[#7cc0ff]">Process</p>
          <h2 className="mt-3 text-[26px] font-extrabold md:text-[32px]">접수부터 뒷정리까지, 시간으로 보여드립니다</h2>
          <p className="mt-3 text-[14.5px] text-white/65">한 단계도 대충 넘기지 않습니다 — 각 단계에 걸리는 실제 시간입니다.</p>
        </div>

        <ol className="grid gap-4 md:grid-cols-3 lg:grid-cols-6">
          {STEPS.map((s, i) => (
            <li key={s.title} className="relative rounded-2xl border border-white/12 bg-white/[0.06] p-5">
              <span className="absolute -top-3 left-5 rounded-full bg-gold px-3 py-1 text-[11.5px] font-extrabold text-white">{s.time}</span>
              <p className="mt-2 text-[26px]" aria-hidden>{s.ico}</p>
              <p className="mt-2 text-[15.5px] font-bold leading-snug">{i + 1}. {s.title}</p>
              <p className="mt-1.5 text-[12.5px] leading-relaxed text-white/60">{s.desc}</p>
            </li>
          ))}
        </ol>

        <p className="mt-8 text-center text-[12.5px] text-white/50">※ 도착·시공 시간은 지역과 증상에 따라 달라질 수 있으며, 접수 시 정확히 안내드립니다.</p>
      </div>
    </section>
  );
}

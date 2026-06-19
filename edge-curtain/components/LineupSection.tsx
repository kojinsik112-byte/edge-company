// 커튼·블라인드 종류 안내 — 커튼 사이트 특화 섹션 (전문성 + SEO 키워드)
const CURTAIN = [
  { name: "암막 커튼", desc: "빛을 확실히 차단해 숙면·영화 감상에 좋은 고차광 커튼. 침실·서재 추천." },
  { name: "쉬어 커튼 (속커튼)", desc: "부드러운 채광과 사생활 보호를 동시에. 겉커튼과 레이어드로 많이 사용." },
  { name: "린넨 커튼", desc: "자연스러운 주름과 질감의 내추럴 무드. 따뜻하고 편안한 거실에 잘 어울림." },
];
const BLIND = [
  { name: "롤 블라인드", desc: "깔끔한 라인과 합리적인 가격. 주방·욕실 등 어디에나 무난." },
  { name: "콤비 블라인드", desc: "투명·불투명 원단이 겹쳐 채광을 단계별로 조절하는 스크린 타입." },
  { name: "허니콤 블라인드", desc: "벌집 구조로 단열·보온·암막에 강해 냉난방 효율을 높임." },
  { name: "우드 블라인드", desc: "따뜻한 원목 질감의 클래식. 서재·카페 무드에 잘 어울림." },
];

export default function LineupSection() {
  return (
    <section className="bg-bg py-16 md:py-24">
      <div className="reveal mx-auto max-w-[1180px] px-6">
        <div className="mx-auto mb-12 max-w-[680px] text-center">
          <p className="kicker">Lineup</p>
          <h2 className="mt-3 text-[26px] font-extrabold text-ink md:text-[32px]">커튼 · 블라인드 종류 안내</h2>
          <p className="mt-3 text-[14.5px] leading-relaxed text-muted">
            공간과 용도에 맞춰 추천해 드립니다. 어떤 게 좋을지 모르겠다면 쇼룸에서 직접 만져보고 비교해 보세요.
          </p>
        </div>

        <div className="grid gap-6 md:grid-cols-2">
          <Group title="커튼" items={CURTAIN} />
          <Group title="블라인드" items={BLIND} />
        </div>

        {/* 전동커튼 강조 스트립 */}
        <div className="mt-6 flex flex-col items-start gap-3 rounded-2xl bg-warm p-7 sm:flex-row sm:items-center sm:justify-between sm:gap-6">
          <div>
            <h3 className="text-[18px] font-bold text-ink">전동커튼</h3>
            <p className="mt-1.5 text-[14px] leading-relaxed text-muted">
              리모컨 · 전용 앱 · 음성(스마트스피커 연동)으로 여닫는 전동커튼. 큰 창·높은 창도 버튼 하나로 편하게.
            </p>
          </div>
          <span className="shrink-0 whitespace-nowrap rounded-full bg-surface px-4 py-2 text-[13px] font-semibold text-gold-d">앱 · 음성 연동</span>
        </div>
      </div>
    </section>
  );
}

function Group({ title, items }: { title: string; items: { name: string; desc: string }[] }) {
  return (
    <div className="rounded-2xl border border-line bg-surface p-7">
      <h3 className="mb-5 text-[18px] font-extrabold text-ink">{title}</h3>
      <ul className="space-y-4">
        {items.map((it) => (
          <li key={it.name} className="flex gap-3">
            <span className="mt-2 h-1.5 w-1.5 shrink-0 rounded-full bg-gold" />
            <div>
              <p className="text-[15px] font-bold text-ink">{it.name}</p>
              <p className="mt-0.5 text-[13.5px] leading-relaxed text-muted">{it.desc}</p>
            </div>
          </li>
        ))}
      </ul>
    </div>
  );
}

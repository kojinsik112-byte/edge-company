import Image from "next/image";

const FEATURES = [
  { title: "직접 만져보는 원단 쇼룸", desc: "울산 쇼룸에서 색·질감 직접 비교", icon: "M3 9.5 12 4l9 5.5M5 10.5V20h14v-9.5M9.5 20v-5h5v5" },
  { title: "정확한 실측·맞춤 제작", desc: "창에 딱 맞는 사이즈로 제작", icon: "M4 19V5m0 14h16M8 19v-6m4 6V9m4 10v-9" },
  { title: "전문 시공 및 A/S", desc: "숙련 기사가 직접 설치·관리", icon: "M12 3l7 3v5c0 4.5-3 8.3-7 10-4-1.7-7-5.5-7-10V6zM9.3 12l1.8 1.8 3.6-3.6" },
  { title: "전동·스마트 연동", desc: "리모컨·앱·음성으로 편하게", icon: "M8 3h8a1 1 0 0 1 1 1v16a1 1 0 0 1-1 1H8a1 1 0 0 1-1-1V4a1 1 0 0 1 1-1zM11 18h2" },
];

const TRUST = ["맞춤 제작", "정확한 실측", "무료 방문상담", "시공 후 A/S"];

export default function WhySection({ image }: { image: string }) {
  return (
    <section className="bg-surface py-16 md:py-24">
      <div className="reveal mx-auto max-w-[1320px] px-6">
        <div className="grid items-center gap-10 lg:grid-cols-2 lg:gap-14">
          {/* 좌측 비주얼 */}
          <div className="relative aspect-[4/5] overflow-hidden rounded-[24px] bg-warm md:aspect-[4/4.4]">
            <Image src={image} alt="엣지리브커튼 시공 공간" fill sizes="(max-width:1024px) 100vw, 560px" className="object-cover" />
          </div>

          {/* 우측 소개 + 4카드 */}
          <div>
            <p className="kicker">Why Edge Live Curtain</p>
            <h2 className="mt-3 text-[28px] font-extrabold leading-snug text-ink md:text-[36px]">왜 엣지리브커튼일까요?</h2>
            <p className="mt-4 text-[15.5px] leading-relaxed text-muted">
              커튼과 블라인드를 단순 설치하는 것이 아니라, 공간과 라이프스타일에 맞는 <b className="font-semibold text-ink">맞춤 무드</b>를 실측부터 시공까지 완성합니다.
            </p>
            <div className="mt-8 grid gap-4 sm:grid-cols-2">
              {FEATURES.map((f) => (
                <div key={f.title} className="rounded-2xl border border-line bg-surface p-6 transition duration-300 hover:-translate-y-1 hover:shadow-[0_22px_45px_-24px_rgba(15,35,66,0.3)]">
                  <span className="flex h-14 w-14 items-center justify-center rounded-full bg-[#f7e8c8] text-gold-d">
                    <svg viewBox="0 0 24 24" className="h-7 w-7" fill="none" stroke="currentColor" strokeWidth={1.6} strokeLinecap="round" strokeLinejoin="round"><path d={f.icon} /></svg>
                  </span>
                  <h3 className="mt-4 text-[16px] font-bold text-ink">{f.title}</h3>
                  <p className="mt-1.5 text-[13px] leading-relaxed text-muted">{f.desc}</p>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* 신뢰 문구 */}
        <div className="mt-14 grid grid-cols-2 gap-px overflow-hidden rounded-2xl border border-line bg-line md:grid-cols-4">
          {TRUST.map((t) => (
            <div key={t} className="flex items-center justify-center gap-2.5 bg-surface px-5 py-7 text-center">
              <svg viewBox="0 0 24 24" className="h-5 w-5 shrink-0 text-gold" fill="none" stroke="currentColor" strokeWidth={2.2} strokeLinecap="round" strokeLinejoin="round"><path d="M20 6 9 17l-5-5" /></svg>
              <span className="text-[15px] font-extrabold text-ink">{t}</span>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}

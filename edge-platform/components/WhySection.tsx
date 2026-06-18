import Image from "next/image";

const FEATURES = [
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

const TRUST = ["ISO 인증기업", "전기공사 면허 보유", "전국 네트워크", "전문 시공 운영"];

export default function WhySection({ image }: { image: string }) {
  return (
    <section className="bg-surface py-16 md:py-24">
      <div className="mx-auto max-w-[1200px] px-6">
        <div className="grid items-center gap-10 lg:grid-cols-2 lg:gap-16">
          {/* 좌측 비주얼 */}
          <div className="relative aspect-[4/5] overflow-hidden rounded-3xl bg-bg md:aspect-[4/4.2]">
            <Image src={image} alt="엣지컴퍼니 시공 공간" fill sizes="(max-width:1024px) 100vw, 560px" className="object-cover" />
            <div className="absolute inset-0 bg-gradient-to-t from-navy/25 to-transparent" />
          </div>

          {/* 우측 소개 */}
          <div>
            <p className="kicker">Why Edge Company</p>
            <h2 className="mt-3 text-[26px] font-bold leading-snug text-ink md:text-[34px]">왜 엣지컴퍼니일까요?</h2>
            <p className="mt-4 text-[15.5px] leading-relaxed text-muted">
              실링팬과 간접조명을 단순 설치하는 것이 아니라, 고객의 라이프스타일에 맞는 <b className="font-semibold text-ink">공간의 분위기</b>를 제안합니다.
            </p>

            <div className="mt-8 space-y-6">
              {FEATURES.map((f) => (
                <div key={f.title} className="flex gap-4">
                  <span className="flex h-14 w-14 shrink-0 items-center justify-center rounded-full bg-gold/15 text-gold-d">
                    <svg viewBox="0 0 24 24" className="h-7 w-7" fill="none" stroke="currentColor" strokeWidth={1.6} strokeLinecap="round" strokeLinejoin="round">
                      <path d={f.icon} />
                    </svg>
                  </span>
                  <div>
                    <h3 className="text-[17px] font-bold text-ink">{f.title}</h3>
                    <p className="mt-1 text-[14px] leading-relaxed text-muted">{f.desc}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* 신뢰도 (문구형) */}
        <div className="mt-14 grid grid-cols-2 gap-px overflow-hidden rounded-2xl border border-line bg-line md:grid-cols-4">
          {TRUST.map((t) => (
            <div key={t} className="flex items-center justify-center gap-2.5 bg-surface px-5 py-6 text-center">
              <svg viewBox="0 0 24 24" className="h-5 w-5 shrink-0 text-gold-d" fill="none" stroke="currentColor" strokeWidth={2} strokeLinecap="round" strokeLinejoin="round"><path d="M20 6 9 17l-5-5" /></svg>
              <span className="text-[14.5px] font-bold text-ink">{t}</span>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}

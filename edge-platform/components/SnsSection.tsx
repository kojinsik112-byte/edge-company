import Image from "next/image";
import type { SiteInfo } from "@/lib/settings";

// 메인 SNS 채널 카드 (썸네일·설명·방문버튼). 링크는 관리자에서 수정.
// 향후 각 채널 최신 콘텐츠(인스타 6 / 유튜브 3 / 블로그 3) 자동노출로 확장 가능.
export default function SnsSection({ site }: { site: SiteInfo }) {
  const channels = [
    {
      key: "instagram", title: "인스타그램", desc: "실제 시공사진과 최신 시공현장",
      href: site.instagram, brand: "#E1306C", thumb: "/img/indirect.webp",
      icon: (<svg viewBox="0 0 24 24" className="h-5 w-5" fill="none" stroke="currentColor" strokeWidth={1.8}><rect x="3" y="3" width="18" height="18" rx="5" /><circle cx="12" cy="12" r="4" /><circle cx="17.5" cy="6.5" r="1" fill="currentColor" stroke="none" /></svg>),
    },
    {
      key: "youtube", title: "유튜브", desc: "실링팬 · 간접조명 영상 리뷰",
      href: site.youtube, brand: "#FF0000", thumb: "/img/fan.webp",
      icon: (<svg viewBox="0 0 24 24" className="h-5 w-5" fill="none" stroke="currentColor" strokeWidth={1.8}><rect x="2.5" y="5.5" width="19" height="13" rx="3.5" /><path d="M10 9.5l5 2.5-5 2.5z" fill="currentColor" stroke="none" /></svg>),
    },
    {
      key: "blog", title: "네이버 블로그", desc: "상세 시공 후기와 정보",
      href: site.blog, brand: "#03C75A", thumb: "/img/living-hero.webp",
      icon: <span className="text-[17px] font-extrabold leading-none">N</span>,
    },
  ];

  return (
    <section className="bg-bg py-16 md:py-24">
      <div className="mx-auto max-w-[1200px] px-6">
        <div className="mx-auto mb-12 max-w-[640px] text-center">
          <p className="kicker">Channels</p>
          <h2 className="mt-3 text-[24px] font-bold text-ink md:text-[30px]">엣지컴퍼니 채널</h2>
          <p className="mt-3 text-[14.5px] text-muted">최신 시공현장과 생생한 후기를 채널에서 만나보세요.</p>
        </div>
        <div className="grid gap-5 md:grid-cols-3">
          {channels.map((c) => (
            <a
              key={c.key}
              href={c.href || "#"}
              target={c.href ? "_blank" : undefined}
              rel="noopener noreferrer"
              className="group overflow-hidden rounded-2xl border border-line bg-surface transition duration-300 hover:-translate-y-1 hover:shadow-[0_26px_55px_-28px_rgba(11,31,58,0.4)]"
            >
              <div className="relative aspect-[16/10] overflow-hidden bg-bg">
                <Image src={c.thumb} alt={`${c.title} 미리보기`} fill sizes="(max-width:768px) 100vw, 380px" className="object-cover transition duration-500 group-hover:scale-105" />
                <span className="absolute left-4 top-4 flex h-10 w-10 items-center justify-center rounded-full text-white shadow-md" style={{ backgroundColor: c.brand }}>
                  {c.icon}
                </span>
              </div>
              <div className="p-6">
                <h3 className="text-[18px] font-bold text-ink">{c.title}</h3>
                <p className="mt-2 text-[13.5px] leading-relaxed text-muted">{c.desc}</p>
                <span className="mt-5 inline-flex w-full items-center justify-center gap-1.5 rounded-lg bg-navy py-3 text-[14px] font-bold text-white transition group-hover:bg-navy-d">
                  채널 방문하기
                  <span className="transition group-hover:translate-x-0.5">→</span>
                </span>
              </div>
            </a>
          ))}
        </div>
      </div>
    </section>
  );
}

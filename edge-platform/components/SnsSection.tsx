import type { SiteInfo } from "@/lib/settings";

// 메인 SNS 채널 카드 (인스타·유튜브·네이버블로그). 링크는 관리자에서 수정.
// 향후 각 채널 최신 콘텐츠(인스타 6 / 유튜브 3 / 블로그 3) 자동노출로 확장 가능한 구조.
export default function SnsSection({ site }: { site: SiteInfo }) {
  const channels = [
    {
      key: "instagram",
      title: "인스타그램",
      desc: "실제 시공사진과 최신 시공현장",
      href: site.instagram,
      brand: "#E1306C",
      icon: (
        <svg viewBox="0 0 24 24" className="h-6 w-6" fill="none" stroke="currentColor" strokeWidth={1.7}>
          <rect x="3" y="3" width="18" height="18" rx="5" /><circle cx="12" cy="12" r="4" /><circle cx="17.5" cy="6.5" r="1" fill="currentColor" stroke="none" />
        </svg>
      ),
    },
    {
      key: "youtube",
      title: "유튜브",
      desc: "실링팬 · 간접조명 영상 리뷰",
      href: site.youtube,
      brand: "#FF0000",
      icon: (
        <svg viewBox="0 0 24 24" className="h-6 w-6" fill="none" stroke="currentColor" strokeWidth={1.7}>
          <rect x="2.5" y="5.5" width="19" height="13" rx="3.5" /><path d="M10 9.5l5 2.5-5 2.5z" fill="currentColor" stroke="none" />
        </svg>
      ),
    },
    {
      key: "blog",
      title: "네이버 블로그",
      desc: "상세 시공 후기와 정보",
      href: site.blog,
      brand: "#03C75A",
      icon: <span className="text-[19px] font-extrabold leading-none">N</span>,
    },
  ];

  return (
    <section className="bg-bg py-14 md:py-16">
      <div className="mx-auto max-w-[1200px] px-6">
        <div className="grid gap-4 sm:grid-cols-3">
          {channels.map((c) => (
            <a
              key={c.key}
              href={c.href || "#"}
              target={c.href ? "_blank" : undefined}
              rel="noopener noreferrer"
              className="group flex min-h-[150px] flex-col justify-between rounded-2xl border border-line bg-surface p-6 transition duration-300 hover:-translate-y-1 hover:shadow-[0_22px_50px_-24px_rgba(11,31,58,0.35)]"
            >
              <div className="flex items-center gap-3">
                <span className="flex h-11 w-11 items-center justify-center rounded-xl" style={{ backgroundColor: `${c.brand}14`, color: c.brand }}>
                  {c.icon}
                </span>
                <span className="text-[17px] font-bold text-ink">{c.title}</span>
              </div>
              <p className="mt-3 text-[13.5px] leading-relaxed text-muted">{c.desc}</p>
              <span className="mt-4 inline-flex items-center gap-1 text-[13px] font-semibold text-navy">
                채널 방문하기
                <span className="transition group-hover:translate-x-0.5">→</span>
              </span>
            </a>
          ))}
        </div>
      </div>
    </section>
  );
}

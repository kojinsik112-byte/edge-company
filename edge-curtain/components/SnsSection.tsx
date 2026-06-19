import type { SiteInfo } from "@/lib/settings";

export default function SnsSection({ site }: { site: SiteInfo }) {
  const channels = [
    {
      key: "instagram", title: "인스타그램", desc: "실제 시공사진과 최신 시공현장", cta: "인스타그램 보기",
      href: site.instagram, bg: "#FFF5F8",
      icon: (
        <svg viewBox="0 0 56 56" className="h-full w-full" aria-hidden="true">
          <defs>
            <linearGradient id="ig-grad" x1="0" y1="56" x2="56" y2="0" gradientUnits="userSpaceOnUse">
              <stop offset="0" stopColor="#FEDA75" /><stop offset="0.25" stopColor="#FA7E1E" />
              <stop offset="0.5" stopColor="#D62976" /><stop offset="0.75" stopColor="#962FBF" /><stop offset="1" stopColor="#4F5BD5" />
            </linearGradient>
          </defs>
          <rect x="2" y="2" width="52" height="52" rx="16" fill="url(#ig-grad)" />
          <rect x="16" y="16" width="24" height="24" rx="7" fill="none" stroke="#fff" strokeWidth="3" />
          <circle cx="28" cy="28" r="6.5" fill="none" stroke="#fff" strokeWidth="3" />
          <circle cx="38" cy="18" r="2.4" fill="#fff" />
        </svg>
      ),
    },
    {
      key: "youtube", title: "유튜브", desc: "커튼 · 블라인드 시공 영상", cta: "유튜브 보기",
      href: site.youtube, bg: "#FFF5F4",
      icon: (
        <svg viewBox="0 0 56 56" className="h-full w-full" aria-hidden="true">
          <rect x="4" y="12" width="48" height="32" rx="9" fill="#FF0000" />
          <path d="M24 20l13 8-13 8z" fill="#fff" />
        </svg>
      ),
    },
    {
      key: "blog", title: "네이버 블로그", desc: "상세 시공 후기와 정보", cta: "블로그 보기",
      href: site.blog, bg: "#F3FCF6",
      icon: (
        <svg viewBox="0 0 56 56" className="h-full w-full" aria-hidden="true">
          <rect x="2" y="2" width="52" height="52" rx="14" fill="#03C75A" />
          <path d="M18 17h7.6l5.2 7.6V17H38v22h-7.6L25.2 31.4V39H18z" fill="#fff" />
        </svg>
      ),
    },
  ];

  return (
    <section className="border-b border-line bg-surface py-14 md:py-16">
      <div className="reveal mx-auto max-w-[1240px] px-6">
        <div className="grid gap-5 sm:grid-cols-3">
          {channels.map((c) => {
            const live = Boolean(c.href);
            const Tag = live ? "a" : "div";
            return (
              <Tag
                key={c.key}
                {...(live ? { href: c.href, target: "_blank", rel: "noopener noreferrer" } : {})}
                className={`group flex flex-col rounded-[20px] border border-line p-7 shadow-[0_10px_30px_rgba(0,0,0,0.05)] transition duration-300 ${live ? "cursor-pointer hover:-translate-y-1.5 hover:shadow-[0_22px_45px_-22px_rgba(15,35,66,0.22)]" : ""}`}
                style={{ backgroundColor: c.bg }}
              >
                <div className="flex items-center gap-3.5">
                  <span className="flex h-16 w-16 shrink-0 items-center justify-center">
                    {c.icon}
                  </span>
                  <span className="text-[18px] font-bold text-ink">{c.title}</span>
                </div>
                <p className="mt-4 text-[13.5px] leading-relaxed text-muted">{c.desc}</p>
                {live ? (
                  <span className="mt-5 inline-flex items-center justify-center gap-1.5 rounded-lg border border-line bg-white py-3 text-[14px] font-bold text-ink transition group-hover:border-transparent group-hover:bg-[#cbd5b6]">
                    {c.cta} <span className="transition group-hover:translate-x-0.5">→</span>
                  </span>
                ) : (
                  <span className="mt-5 inline-flex items-center justify-center gap-1.5 rounded-lg border border-dashed border-line bg-white/60 py-3 text-[13.5px] font-semibold text-muted">
                    준비 중
                  </span>
                )}
              </Tag>
            );
          })}
        </div>
      </div>
    </section>
  );
}

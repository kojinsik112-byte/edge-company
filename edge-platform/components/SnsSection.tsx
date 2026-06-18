import type { SiteInfo } from "@/lib/settings";

export default function SnsSection({ site }: { site: SiteInfo }) {
  const channels = [
    {
      key: "instagram", title: "인스타그램", desc: "실제 시공사진과 최신 시공현장",
      href: site.instagram, brand: "#E1306C", bg: "#FFF1F5",
      icon: (<svg viewBox="0 0 24 24" className="h-6 w-6" fill="none" stroke="currentColor" strokeWidth={1.8}><rect x="3" y="3" width="18" height="18" rx="5" /><circle cx="12" cy="12" r="4" /><circle cx="17.5" cy="6.5" r="1" fill="currentColor" stroke="none" /></svg>),
    },
    {
      key: "youtube", title: "유튜브", desc: "실링팬 · 간접조명 영상 리뷰",
      href: site.youtube, brand: "#FF0000", bg: "#FFF5F5",
      icon: (<svg viewBox="0 0 24 24" className="h-6 w-6" fill="none" stroke="currentColor" strokeWidth={1.8}><rect x="2.5" y="5.5" width="19" height="13" rx="3.5" /><path d="M10 9.5l5 2.5-5 2.5z" fill="currentColor" stroke="none" /></svg>),
    },
    {
      key: "blog", title: "네이버 블로그", desc: "상세 시공 후기와 정보",
      href: site.blog, brand: "#03C75A", bg: "#F2FFF4",
      icon: <span className="text-[18px] font-extrabold leading-none">N</span>,
    },
  ];

  return (
    <section className="border-b border-line bg-surface py-14 md:py-16">
      <div className="mx-auto max-w-[1100px] px-6">
        <div className="grid gap-4 sm:grid-cols-3">
          {channels.map((c) => (
            <a
              key={c.key}
              href={c.href || "#"}
              target={c.href ? "_blank" : undefined}
              rel="noopener noreferrer"
              className="group flex flex-col rounded-2xl border border-line p-6 transition duration-300 hover:-translate-y-1 hover:shadow-[0_24px_50px_-28px_rgba(15,35,66,0.35)]"
              style={{ backgroundColor: c.bg }}
            >
              <div className="flex items-center gap-3">
                <span className="flex h-12 w-12 items-center justify-center rounded-full text-white shadow-sm" style={{ backgroundColor: c.brand }}>
                  {c.icon}
                </span>
                <span className="text-[17px] font-bold text-ink">{c.title}</span>
              </div>
              <p className="mt-4 text-[13.5px] leading-relaxed text-muted">{c.desc}</p>
              <span className="mt-5 inline-flex items-center justify-center gap-1.5 rounded-lg py-3 text-[14px] font-bold text-white transition group-hover:brightness-95" style={{ backgroundColor: c.brand }}>
                채널 방문하기 <span className="transition group-hover:translate-x-0.5">→</span>
              </span>
            </a>
          ))}
        </div>
      </div>
    </section>
  );
}

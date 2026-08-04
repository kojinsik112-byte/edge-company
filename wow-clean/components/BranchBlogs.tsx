import Link from "next/link";

// 지사별 네이버 블로그 바로가기 (링크는 회장 지정). 지역명은 실제에 맞게 label만 바꾸면 됨.
const BLOGS = [
  { label: "세종 지사 블로그", handle: "ssun45100", href: "https://blog.naver.com/ssun45100" },
  { label: "대전 지사 블로그", handle: "clear-a-drain", href: "https://blog.naver.com/clear-a-drain" },
  { label: "인천·서울 지사 블로그", handle: "wowclean8282", href: "https://blog.naver.com/wowclean8282" },
];

export default function BranchBlogs() {
  return (
    <section className="bg-surface py-16 md:py-24">
      <div className="reveal mx-auto max-w-[1320px] px-6">
        <div className="mx-auto mb-10 max-w-[640px] text-center">
          <p className="kicker">Branch Blog</p>
          <h2 className="mt-3 text-[26px] font-extrabold text-ink md:text-[32px]">지사별 블로그</h2>
          <p className="mt-3 text-[16px] leading-relaxed text-muted">지역별 실제 시공 후기와 정보를 네이버 블로그에서 확인하세요.</p>
        </div>
        <div className="grid grid-cols-1 gap-5 sm:grid-cols-3">
          {BLOGS.map((b) => (
            <Link
              key={b.href}
              href={b.href}
              target="_blank"
              rel="noopener noreferrer"
              className="group flex items-center gap-4 rounded-2xl border border-line bg-surface p-6 shadow-[0_10px_30px_-20px_rgba(15,35,66,0.2)] transition hover:-translate-y-1 hover:border-[#03C75A]/50 hover:shadow-[0_22px_45px_-24px_rgba(15,35,66,0.25)]"
            >
              <span className="flex h-[52px] w-[52px] shrink-0 items-center justify-center rounded-[14px]">
                <svg viewBox="0 0 56 56" className="h-full w-full" aria-hidden="true">
                  <rect x="2" y="2" width="52" height="52" rx="14" fill="#03C75A" />
                  <path d="M18 17h7.6l5.2 7.6V17H38v22h-7.6L25.2 31.4V39H18z" fill="#fff" />
                </svg>
              </span>
              <span className="min-w-0 flex-1">
                <span className="block text-[16px] font-bold text-ink">{b.label}</span>
                <span className="mt-0.5 block truncate text-[13px] text-muted">blog.naver.com/{b.handle}</span>
              </span>
              <span className="shrink-0 text-[15px] font-bold text-[#03C75A] transition group-hover:translate-x-0.5">→</span>
            </Link>
          ))}
        </div>
      </div>
    </section>
  );
}

import Link from "next/link";
import type { SiteInfo } from "@/lib/settings";

// 모바일 하단 고정: 전화상담 · 카카오톡상담 · 쇼룸예약 (화이트·차분 톤)
export default function MobileBar({ site }: { site: SiteInfo }) {
  const tel = `tel:${site.phone.replace(/-/g, "")}`;
  const kakao = site.kakao || `sms:${site.phone.replace(/-/g, "")}`;
  const cell = "flex items-center justify-center gap-2 py-3.5 text-[13.5px] font-bold text-ink transition active:bg-bg";
  return (
    <div className="fixed inset-x-0 bottom-0 z-50 xl:hidden">
      <div className="relative grid grid-cols-3 border-t border-line bg-surface/95 pb-[env(safe-area-inset-bottom)] shadow-[0_-8px_24px_-14px_rgba(15,35,66,0.2)] backdrop-blur-md">
        <span className="pointer-events-none absolute inset-x-0 top-0 h-px bg-gradient-to-r from-transparent via-gold/55 to-transparent" />
        <a href={tel} className={cell}>
          <Ic d="M6.5 3h-.8A2.7 2.7 0 0 0 3 5.8C3 14 10 21 18.2 21a2.7 2.7 0 0 0 2.8-2.7v-.8a1 1 0 0 0-.7-1l-3.2-1a1 1 0 0 0-1.1.4l-.9 1.3a13.4 13.4 0 0 1-5.8-5.8l1.3-.9a1 1 0 0 0 .4-1.1l-1-3.2a1 1 0 0 0-1-.7z" />
          전화상담
        </a>
        <a href={kakao} className={`${cell} border-x border-line`}>
          <Ic d="M21 11.5a8.4 8.4 0 0 1-12.1 7.5L3 21l2-5.9A8.4 8.4 0 1 1 21 11.5z" />
          카톡상담
        </a>
        <Link href="/contact" className={cell}>
          <Ic d="M3.5 5h17a2 2 0 0 1 2 2v0M3.5 5v14a2 2 0 0 0 2 2h13a2 2 0 0 0 2-2V7M3.5 9.5h17M8 3v4M16 3v4" />
          쇼룸예약
        </Link>
      </div>
    </div>
  );
}

function Ic({ d }: { d: string }) {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={1.5} strokeLinecap="round" strokeLinejoin="round" className="h-[18px] w-[18px] text-gold-d">
      <path d={d} />
    </svg>
  );
}

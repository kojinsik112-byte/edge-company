import Link from "next/link";
import type { SiteInfo } from "@/lib/settings";

// 데스크탑 전용 우하단 플로팅 상담 버튼 (모바일은 MobileBar가 담당 → xl 이상에서만 노출)
export default function DesktopCTA({ site }: { site: SiteInfo }) {
  const tel = `tel:${site.phone.replace(/-/g, "")}`;
  const kakao = site.kakao || `sms:${site.phone.replace(/-/g, "")}`;
  return (
    <div className="fixed bottom-7 right-7 z-40 hidden flex-col items-end gap-3 xl:flex">
      <a
        href={tel}
        className="group flex items-center gap-0 overflow-hidden rounded-full bg-navy py-3.5 pl-4 pr-4 text-white shadow-[0_16px_36px_-16px_rgba(47,37,28,0.55)] ring-1 ring-white/10 transition hover:bg-navy-d"
      >
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={1.6} strokeLinecap="round" strokeLinejoin="round" className="h-5 w-5 text-gold">
          <path d="M6.5 3h-.8A2.7 2.7 0 0 0 3 5.8C3 14 10 21 18.2 21a2.7 2.7 0 0 0 2.8-2.7v-.8a1 1 0 0 0-.7-1l-3.2-1a1 1 0 0 0-1.1.4l-.9 1.3a13.4 13.4 0 0 1-5.8-5.8l1.3-.9a1 1 0 0 0 .4-1.1l-1-3.2a1 1 0 0 0-1-.7z" />
        </svg>
        <span className="max-w-0 overflow-hidden whitespace-nowrap text-[14px] font-bold opacity-0 transition-all duration-300 group-hover:ml-2.5 group-hover:max-w-[160px] group-hover:opacity-100">
          {site.phone} 전화상담
        </span>
      </a>
      <a
        href={kakao}
        className="group flex items-center gap-0 overflow-hidden rounded-full bg-gold py-3.5 pl-4 pr-4 text-white shadow-[0_16px_36px_-16px_rgba(169,126,57,0.6)] ring-1 ring-white/20 transition hover:brightness-105"
      >
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={1.7} strokeLinecap="round" strokeLinejoin="round" className="h-5 w-5">
          <path d="M21 11.5a8.4 8.4 0 0 1-12.1 7.5L3 21l2-5.9A8.4 8.4 0 1 1 21 11.5z" />
        </svg>
        <span className="max-w-0 overflow-hidden whitespace-nowrap text-[14px] font-bold opacity-0 transition-all duration-300 group-hover:ml-2.5 group-hover:max-w-[140px] group-hover:opacity-100">
          카카오톡 상담
        </span>
      </a>
    </div>
  );
}

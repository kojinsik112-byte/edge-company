"use client";

import Link from "next/link";
import { useState } from "react";
import { NAV } from "@/lib/constants";
import type { SiteInfo, Notice } from "@/lib/settings";

export default function Header({ site, notice }: { site: SiteInfo; notice: Notice }) {
  const [open, setOpen] = useState(false);
  const tel = `tel:${site.phone.replace(/-/g, "")}`;
  return (
    <>
      {/* 상단 공지바 */}
      {notice.enabled && notice.text && (
        <Link href={notice.link || "/contact"} className="block bg-navy py-2 text-center text-[12.5px] font-medium text-white">
          {notice.text}
          <span className="ml-2 text-gold">자세히 →</span>
        </Link>
      )}

      <header className="sticky top-0 z-50 border-b border-line bg-surface">
        <div className="mx-auto flex h-[72px] max-w-[1200px] items-center justify-between px-6">
          {/* 로고 */}
          <Link href="/" className="flex items-center gap-2.5" aria-label="엣지컴퍼니 홈">
            <span className="flex h-[38px] w-[38px] items-center justify-center rounded-[8px] bg-navy font-serif text-[18px] font-bold text-gold">
              E
            </span>
            <span className="leading-none">
              <span className="block text-[20px] font-extrabold tracking-tight text-ink">엣지컴퍼니</span>
              <span className="mt-1 block text-[10px] font-medium tracking-[2.5px] text-muted">
                LIGHTING · CEILING FAN · SHOWROOM
              </span>
            </span>
          </Link>

          {/* 데스크탑 메뉴 */}
          <nav className="hidden items-center gap-8 lg:flex">
            {NAV.filter((n) => n.label !== "상담문의").map((n) => (
              <Link key={n.href} href={n.href} className="text-[14px] font-medium text-[#333333] transition hover:text-gold">
                {n.label}
              </Link>
            ))}
          </nav>

          <div className="flex items-center gap-2">
            <a href={tel} className="hidden items-center gap-2 rounded-[8px] bg-navy px-6 py-3.5 text-[15px] font-bold text-white transition hover:bg-navy-d lg:inline-flex">
              <PhoneIcon className="h-4 w-4 text-gold" />
              전화상담 {site.phone}
            </a>
            <button
              aria-label="메뉴"
              aria-expanded={open}
              onClick={() => setOpen((v) => !v)}
              className="flex h-10 w-10 flex-col items-center justify-center gap-[5px] rounded-lg border border-line bg-surface lg:hidden"
            >
              <span className={`h-[1.6px] w-[18px] bg-ink transition ${open ? "translate-y-[6.6px] rotate-45" : ""}`} />
              <span className={`h-[1.6px] w-[18px] bg-ink transition ${open ? "opacity-0" : ""}`} />
              <span className={`h-[1.6px] w-[18px] bg-ink transition ${open ? "-translate-y-[6.6px] -rotate-45" : ""}`} />
            </button>
          </div>
        </div>

        {open && (
          <nav className="border-t border-line bg-surface px-6 pb-6 pt-2 lg:hidden">
            {NAV.map((n) => (
              <Link key={n.href} href={n.href} onClick={() => setOpen(false)} className="flex items-center justify-between border-b border-line py-4 text-lg font-semibold text-ink">
                {n.label}
              </Link>
            ))}
            <a href={tel} className="mt-5 flex items-center justify-center gap-2 rounded-[8px] bg-navy py-3.5 font-bold text-white">
              <PhoneIcon className="h-4 w-4 text-gold" /> 전화 상담 {site.phone}
            </a>
          </nav>
        )}
      </header>
    </>
  );
}

function PhoneIcon({ className }: { className?: string }) {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={1.6} className={className}>
      <path d="M6.5 3h-.8A2.7 2.7 0 0 0 3 5.8C3 14 10 21 18.2 21a2.7 2.7 0 0 0 2.8-2.7v-.8a1 1 0 0 0-.7-1l-3.2-1a1 1 0 0 0-1.1.4l-.9 1.3a13.4 13.4 0 0 1-5.8-5.8l1.3-.9a1 1 0 0 0 .4-1.1l-1-3.2a1 1 0 0 0-1-.7z" strokeLinejoin="round" />
    </svg>
  );
}

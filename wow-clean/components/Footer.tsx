import Link from "next/link";
import { REGIONS, CATEGORIES, REGION_SLUG, CATEGORY_SLUG } from "@/lib/constants";
import type { SiteInfo } from "@/lib/settings";

export default function Footer({ site }: { site: SiteInfo }) {
  const socials = [
    { label: "인스타그램", href: site.instagram },
    { label: "유튜브", href: site.youtube },
    { label: "네이버 블로그", href: site.blog },
  ].filter((s) => s.href);

  return (
    <footer className="border-t border-line bg-surface">
      <div className="mx-auto max-w-[1320px] px-6 py-12">
        {/* 지역 SEO 내부링크 */}
        <div className="mb-10 grid grid-cols-2 gap-6 sm:grid-cols-4">
          {REGIONS.map((r) => (
            <div key={r}>
              <p className="mb-3 text-sm font-bold text-ink">{r}</p>
              <ul className="space-y-2 text-[13px] text-muted">
                {CATEGORIES.map((c) => (
                  <li key={c}>
                    <Link href={`/area/${REGION_SLUG[r]}-${CATEGORY_SLUG[c]}`} className="transition hover:text-navy">
                      {r} {c}
                    </Link>
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>

        <div className="flex flex-col gap-4 border-t border-line pt-8 sm:flex-row sm:items-start sm:justify-between">
          <div>
            <div className="mb-3 flex items-center gap-2.5">
              <span className="flex h-8 w-8 items-center justify-center rounded-lg bg-navy font-lux text-base font-bold text-white">W</span>
              <span className="font-extrabold tracking-tight text-ink">{site.bizName}</span>
            </div>
            {socials.length > 0 && (
              <div className="flex gap-4 text-[12.5px] font-semibold text-muted">
                {socials.map((s) => (
                  <a key={s.label} href={s.href} target="_blank" rel="noopener noreferrer" className="hover:text-navy">
                    {s.label}
                  </a>
                ))}
              </div>
            )}
          </div>
          <div className="text-[12.5px] leading-7 text-muted">
            <b className="font-semibold text-ink/70">상호</b> {site.bizName} · <b className="font-semibold text-ink/70">대표</b> {site.ceo} · 사업자등록번호 {site.bizNo}
            <br />
            <b className="font-semibold text-ink/70">서비스 지역</b> {site.address}
            <br />
            <b className="font-semibold text-ink/70">대표번호</b> {site.phoneRep} · <b className="font-semibold text-ink/70">상담</b> {site.phone}
          </div>
        </div>

        <div className="mt-6 flex flex-wrap gap-x-5 gap-y-1.5 text-[11.5px] text-muted">
          <span><b className="font-semibold text-ink/70">사업자 정식 등록</b> 현금영수증 · 세금계산서 발행</span>
          <span><b className="font-semibold text-ink/70">접수</b> 연중무휴 24시간</span>
          <span><b className="font-semibold text-ink/70">보증</b> 작업 후 A/S (보증 기준에 따름)</span>
        </div>
        <p className="mt-3 text-[11.5px] leading-relaxed text-muted">
          시공 전 원인을 확인하고 비용을 확정한 뒤 작업하며, 작업 결과는 사진으로 남깁니다. 현장 여건(배관 상태·이물질 종류)에 따라 작업 방식과 소요 시간은 달라질 수 있습니다.
        </p>
        <p className="mt-3 text-[11.5px] tracking-wide text-line">
          © {new Date().getFullYear()} Wow Clean. All rights reserved.
        </p>
      </div>
    </footer>
  );
}

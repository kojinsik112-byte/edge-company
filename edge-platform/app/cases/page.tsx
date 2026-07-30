import type { Metadata } from "next";
import Link from "next/link";
import { getCases } from "@/lib/data";
import { REGIONS, CATEGORIES, type Region, type Category } from "@/lib/constants";
import CaseCard from "@/components/CaseCard";

// 관리자에서 등록/수정한 CMS 콘텐츠가 즉시 반영되도록 항상 최신 렌더
export const dynamic = "force-dynamic";

export const metadata: Metadata = {
  title: "시공사례 — 울산·부산·포항·경주 실링팬·간접조명",
  description:
    "엣지컴퍼니 실링팬·간접조명·센서조명 시공사례 모음. 울산·부산·포항·경주 지역별, 카테고리별로 확인하세요.",
  alternates: { canonical: "/cases" },
};

export default async function CasesPage({
  searchParams,
}: {
  searchParams: Promise<{ region?: string; category?: string; q?: string }>;
}) {
  const sp = await searchParams;
  const region = REGIONS.includes(sp.region as Region) ? (sp.region as Region) : undefined;
  const category = CATEGORIES.includes(sp.category as Category) ? (sp.category as Category) : undefined;
  const cases = await getCases({ region, category, q: sp.q });

  const chip = (active: boolean) =>
    `whitespace-nowrap rounded-full border px-4 py-2 text-[13px] font-semibold transition ${
      active ? "border-navy bg-navy text-white" : "border-line bg-surface text-ink/70 hover:border-navy"
    }`;
  const qs = (next: Record<string, string | undefined>) => {
    const merged = { region, category, ...next };
    const p = new URLSearchParams();
    Object.entries(merged).forEach(([k, v]) => v && p.set(k, v));
    const s = p.toString();
    return `/cases${s ? `?${s}` : ""}`;
  };

  return (
    <div className="mx-auto max-w-[1180px] px-5 py-12 md:py-16">
      <p className="kicker">Portfolio</p>
      <h1 className="mt-3 text-2xl font-bold text-ink md:text-3xl">
        {region ?? "울산·부산·포항·경주"} {category ?? "전체"} 시공사례
      </h1>
      <p className="mt-3 text-[14.5px] text-muted">실제 시공 현장을 지역·카테고리로 확인하세요.</p>

      {/* 필터 */}
      <div className="no-scrollbar mt-7 flex gap-2 overflow-x-auto pb-1">
        <Link href={qs({ region: undefined })} className={chip(!region)}>전지역</Link>
        {REGIONS.map((r) => (
          <Link key={r} href={qs({ region: r })} className={chip(region === r)}>{r}</Link>
        ))}
        <span className="mx-1 w-px shrink-0 bg-line" />
        <Link href={qs({ category: undefined })} className={chip(!category)}>전체</Link>
        {CATEGORIES.map((c) => (
          <Link key={c} href={qs({ category: c })} className={chip(category === c)}>{c}</Link>
        ))}
      </div>

      {cases.length > 0 ? (
        <div className="mt-8 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {cases.map((c) => <CaseCard key={c.id} c={c} />)}
        </div>
      ) : (
        <div className="mt-10 rounded-2xl border border-dashed border-line bg-bg py-20 text-center text-[14px] text-muted">
          해당 조건의 시공사례가 아직 없습니다.
        </div>
      )}
    </div>
  );
}

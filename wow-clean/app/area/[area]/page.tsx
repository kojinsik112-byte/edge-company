import type { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";
import {
  REGIONS, CATEGORIES, REGION_SLUG, CATEGORY_SLUG, CATEGORY_DESC,
  type Region, type Category,
} from "@/lib/constants";
import { areaSeo } from "@/lib/seo";
import { getCases } from "@/lib/data";
import { getSettings } from "@/lib/settings";
import CaseCard from "@/components/CaseCard";

// 지역×카테고리 = 12개 SEO 페이지 자동 생성
const COMBOS: { slug: string; region: Region; category: Category }[] = [];
for (const r of REGIONS)
  for (const c of CATEGORIES)
    COMBOS.push({ slug: `${REGION_SLUG[r]}-${CATEGORY_SLUG[c]}`, region: r, category: c });

export function generateStaticParams() {
  return COMBOS.map((x) => ({ area: x.slug }));
}

type Props = { params: Promise<{ area: string }> };

function resolve(area: string) {
  return COMBOS.find((x) => x.slug === area) ?? null;
}

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { area } = await params;
  const combo = resolve(area);
  if (!combo) return { title: "페이지를 찾을 수 없습니다" };
  const seo = areaSeo(combo.region, combo.category);
  return {
    title: seo.title,
    description: seo.description,
    alternates: { canonical: `/area/${area}` },
    openGraph: { title: seo.title, description: seo.description },
  };
}

export default async function AreaPage({ params }: Props) {
  const { area } = await params;
  const combo = resolve(area);
  if (!combo) notFound();
  const { region, category } = combo;
  const seo = areaSeo(region, category);
  const [cases, { site }] = await Promise.all([getCases({ region, category, limit: 24 }), getSettings()]);

  return (
    <div className="mx-auto max-w-[1180px] px-5 py-12 md:py-16">
      <p className="kicker">{region} · {category}</p>
      <h1 className="mt-3 text-2xl font-bold leading-snug text-ink md:text-[32px]">{seo.h1}</h1>
      <p className="mt-4 max-w-2xl text-[15px] leading-relaxed text-muted">
        {CATEGORY_DESC[category]} 와우클린은 {region}을 포함한 전국에서 {category} 시공을 24시간 접수합니다.
      </p>

      <div className="mt-6 flex flex-wrap gap-2">
        <a href={`tel:${site.phone.replace(/-/g, "")}`} className="rounded-lg bg-ink px-5 py-3 text-[14px] font-semibold text-white transition hover:bg-[#111827]">
          {region} {category} 상담 {site.phone}
        </a>
        <Link href="/contact" className="rounded-lg border border-gold bg-surface px-5 py-3 text-[14px] font-semibold text-ink transition hover:bg-warm">온라인 접수</Link>
      </div>

      {/* 다른 지역/카테고리 내부링크 (SEO) */}
      <div className="mt-8 flex flex-wrap gap-2">
        {REGIONS.filter((r) => r !== region).map((r) => (
          <Link key={r} href={`/area/${REGION_SLUG[r]}-${CATEGORY_SLUG[category]}`} className="rounded-full border border-line px-3.5 py-1.5 text-[12.5px] text-muted hover:border-navy hover:text-navy">
            {r} {category}
          </Link>
        ))}
        {CATEGORIES.filter((c) => c !== category).map((c) => (
          <Link key={c} href={`/area/${REGION_SLUG[region]}-${CATEGORY_SLUG[c]}`} className="rounded-full border border-line px-3.5 py-1.5 text-[12.5px] text-muted hover:border-navy hover:text-navy">
            {region} {c}
          </Link>
        ))}
      </div>

      <h2 className="mt-12 text-lg font-bold text-ink">{region} {category} 시공사례</h2>
      {cases.length > 0 ? (
        <div className="mt-5 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {cases.map((c) => <CaseCard key={c.id} c={c} />)}
        </div>
      ) : (
        <div className="mt-5 rounded-2xl border border-dashed border-line bg-bg py-16 text-center text-[14px] text-muted">
          {region} {category} 시공사례가 곧 등록됩니다. 먼저 상담받아 보세요.
        </div>
      )}
    </div>
  );
}

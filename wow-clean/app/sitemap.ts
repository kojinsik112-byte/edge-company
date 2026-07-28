import type { MetadataRoute } from "next";
import { SITE, REGIONS, CATEGORIES, REGION_SLUG, CATEGORY_SLUG } from "@/lib/constants";
import { getCases } from "@/lib/data";

export const revalidate = 3600; // 1시간마다 sitemap 갱신

export default async function sitemap(): Promise<MetadataRoute.Sitemap> {
  const base = SITE.url.replace(/\/$/, "");
  const now = new Date();

  const staticRoutes = ["", "/cases", "/reviews", "/faq", "/youtube", "/showroom", "/contact"].map(
    (p) => ({ url: `${base}${p}`, lastModified: now, changeFrequency: "weekly" as const, priority: p === "" ? 1 : 0.7 }),
  );

  // 지역×카테고리 SEO 페이지 (12)
  const areaRoutes = REGIONS.flatMap((r) =>
    CATEGORIES.map((c) => ({
      url: `${base}/area/${REGION_SLUG[r]}-${CATEGORY_SLUG[c]}`,
      lastModified: now,
      changeFrequency: "weekly" as const,
      priority: 0.8,
    })),
  );

  // 시공사례 상세 (DB)
  const cases = await getCases({ limit: 1000 });
  const caseRoutes = cases.map((c) => ({
    url: `${base}/cases/${c.slug}`,
    lastModified: c.updated_at ? new Date(c.updated_at) : new Date(c.created_at),
    changeFrequency: "monthly" as const,
    priority: 0.6,
  }));

  return [...staticRoutes, ...areaRoutes, ...caseRoutes];
}

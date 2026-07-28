import { SITE, type Region, type Category } from "./constants";

/** 한글/영문/숫자 유지, 공백·특수문자를 하이픈으로 → SEO 친화 슬러그 */
export function slugify(input: string): string {
  return input
    .trim()
    .toLowerCase()
    .replace(/[^\w가-힣\s-]/g, "") // 한글·영숫자·공백·하이픈만
    .replace(/[\s_]+/g, "-")
    .replace(/-+/g, "-")
    .replace(/^-|-$/g, "");
}

/** 예) "강서구 화곡동 빌라" + "하수구막힘" → "강서구-화곡동-빌라-하수구막힘-시공" */
export function buildCaseSlug(apartment: string, category: string): string {
  return slugify(`${apartment} ${category} 시공`);
}

/** SEO 제목 자동 생성 */
export function autoSeoTitle(c: {
  apartment: string;
  region: string;
  category: string;
}): string {
  return `${c.region} ${c.apartment} ${c.category} 시공 | 와우클린`;
}

/** SEO 설명 자동 생성 (본문 발췌 + 지역/카테고리 키워드) */
export function autoSeoDescription(c: {
  apartment: string;
  region: string;
  category: string;
  body?: string;
}): string {
  const excerpt = (c.body || "")
    .replace(/\s+/g, " ")
    .trim()
    .slice(0, 90);
  const base = `${c.region} ${c.apartment} ${c.category} 시공 사례. 와우클린은 하수구막힘·변기막힘·배관청소 전문 전국 24시간 출동 시공 기업입니다.`;
  return excerpt ? `${excerpt} … ${base}` : base;
}

/** 지역×카테고리 SEO 페이지 메타 (예: 서울 하수구막힘) */
export function areaSeo(region: Region, category: Category) {
  return {
    h1: `${region} ${category} 전문 시공`,
    title: `${region} ${category} 24시간 출동`,
    description: `${region} ${category}은 와우클린. 전국 24시간 출동, 원인 확인 후 시공 전 투명 견적, 작업 후 A/S 보증까지. 대표번호 1668-8982.`,
  };
}

export const abs = (path: string) =>
  path.startsWith("http") ? path : `${SITE.url}${path}`;

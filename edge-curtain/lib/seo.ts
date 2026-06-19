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

/** 예) "문수로 롯데캐슬" + "커튼" → "문수로-롯데캐슬-커튼-시공" */
export function buildCaseSlug(apartment: string, category: string): string {
  return slugify(`${apartment} ${category} 시공`);
}

/** SEO 제목 자동 생성 */
export function autoSeoTitle(c: {
  apartment: string;
  region: string;
  category: string;
}): string {
  return `${c.region} ${c.apartment} ${c.category} 시공 | 엣지리브커튼`;
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
  const base = `${c.region} ${c.apartment} ${c.category} 시공 사례. 엣지리브커튼 울산본점은 울산·양산·부산·경주 커튼·블라인드·전동커튼 전문 쇼룸입니다.`;
  return excerpt ? `${excerpt} … ${base}` : base;
}

/** 지역×카테고리 SEO 페이지 메타 (예: 울산 커튼) */
export function areaSeo(region: Region, category: Category) {
  return {
    h1: `${region} ${category} 전문 시공`,
    title: `${region} ${category} 시공 전문 | 엣지리브커튼 울산본점`,
    description: `${region} ${category} 시공은 엣지리브커튼. 울산·양산·부산·경주 커튼·블라인드·전동커튼 전문 쇼룸에서 원단을 직접 보고 비교한 뒤 맞춤 제작하세요.`,
  };
}

export const abs = (path: string) =>
  path.startsWith("http") ? path : `${SITE.url}${path}`;

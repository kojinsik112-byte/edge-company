// ===== Wow Clean — site-wide constants =====

export const SITE = {
  name: "와우클린",
  legalName: "와우클린 하수구변기막힘설비",
  tagline: "전국 24시간 하수구막힘·변기막힘·배관청소 전문",
  phone: "1668-8982",
  phoneRep: "1668-8982",
  address: "전국 24시간 출동 서비스",
  // 배포 후 실제 도메인으로 교체 (env NEXT_PUBLIC_SITE_URL 우선)
  url: process.env.NEXT_PUBLIC_SITE_URL || "https://wow-clean.vercel.app",
  // 카카오톡 채널 채팅 URL (예: https://pf.kakao.com/_xxxx/chat) — 없으면 문자로 폴백
  kakao: process.env.NEXT_PUBLIC_KAKAO_URL || "",
  // 네이버 서치어드바이저 사이트 소유확인 메타값
  naverVerification: process.env.NEXT_PUBLIC_NAVER_VERIFICATION || "",
} as const;

export const REGIONS = ["서울", "경기", "인천", "부산", "대구", "울산", "대전", "광주"] as const;
export type Region = (typeof REGIONS)[number];

export const CATEGORIES = ["하수구막힘", "변기막힘", "배관청소"] as const;
export type Category = (typeof CATEGORIES)[number];

// 한글 ↔ URL 슬러그 (지역 SEO 페이지 /area/<region>-<category>)
export const REGION_SLUG: Record<Region, string> = {
  서울: "seoul",
  경기: "gyeonggi",
  인천: "incheon",
  부산: "busan",
  대구: "daegu",
  울산: "ulsan",
  대전: "daejeon",
  광주: "gwangju",
};
export const CATEGORY_SLUG: Record<Category, string> = {
  하수구막힘: "drain",
  변기막힘: "toilet",
  배관청소: "pipe-cleaning",
};

export const REGION_BY_SLUG = Object.fromEntries(
  Object.entries(REGION_SLUG).map(([k, v]) => [v, k as Region]),
) as Record<string, Region>;
export const CATEGORY_BY_SLUG = Object.fromEntries(
  Object.entries(CATEGORY_SLUG).map(([k, v]) => [v, k as Category]),
) as Record<string, Category>;

// 카테고리별 한 줄 설명 (지역 SEO 페이지·홈 카드용)
export const CATEGORY_DESC: Record<Category, string> = {
  하수구막힘:
    "욕실·베란다·마당 하수구 막힘 뚫음. 원인을 확인한 뒤 작업 전에 비용을 확정하고 시공합니다.",
  변기막힘:
    "변기 막힘·역류·이물질 제거. 함부로 뜯지 않고 상태를 확인한 뒤 깔끔하게 해결합니다.",
  배관청소:
    "고압세척·관로 스프링 장비로 배관 내부의 기름때와 슬러지를 걷어내 재막힘을 줄입니다.",
};

export const NAV = [
  { label: "하수구막힘", href: "/area/seoul-drain" },
  { label: "변기막힘", href: "/area/seoul-toilet" },
  { label: "배관청소", href: "/area/seoul-pipe-cleaning" },
  { label: "시공사례", href: "/cases" },
  { label: "고객후기", href: "/reviews" },
  { label: "시공현장", href: "/showroom" },
  { label: "영상", href: "/youtube" },
  { label: "FAQ", href: "/faq" },
  { label: "상담문의", href: "/contact" },
] as const;

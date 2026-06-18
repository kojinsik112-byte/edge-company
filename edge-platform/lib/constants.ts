// ===== Edge Company — site-wide constants =====

export const SITE = {
  name: "엣지컴퍼니",
  legalName: "㈜엣지컴퍼니",
  tagline: "울산·부산·포항·경주 실링팬·간접조명·스마트조명 전문 쇼룸",
  phone: "010-4900-6107",
  phoneRep: "1533-3210",
  address: "울산광역시 울주군 청량읍 상남1길 28",
  // 배포 후 실제 도메인으로 교체 (env NEXT_PUBLIC_SITE_URL 우선)
  url: process.env.NEXT_PUBLIC_SITE_URL || "https://edge-company.vercel.app",
  // 카카오톡 채널 채팅 URL (예: https://pf.kakao.com/_xxxx/chat) — 없으면 문자로 폴백
  kakao: process.env.NEXT_PUBLIC_KAKAO_URL || "",
  // 네이버 서치어드바이저 사이트 소유확인 메타값
  naverVerification: process.env.NEXT_PUBLIC_NAVER_VERIFICATION || "",
} as const;

export const REGIONS = ["울산", "부산", "포항", "경주"] as const;
export type Region = (typeof REGIONS)[number];

export const CATEGORIES = ["실링팬", "간접조명", "스마트조명"] as const;
export type Category = (typeof CATEGORIES)[number];

// 한글 ↔ URL 슬러그 (지역 SEO 페이지 /area/<region>-<category>)
export const REGION_SLUG: Record<Region, string> = {
  울산: "ulsan",
  부산: "busan",
  포항: "pohang",
  경주: "gyeongju",
};
export const CATEGORY_SLUG: Record<Category, string> = {
  실링팬: "ceiling-fan",
  간접조명: "indirect-lighting",
  스마트조명: "smart-lighting",
};

export const REGION_BY_SLUG = Object.fromEntries(
  Object.entries(REGION_SLUG).map(([k, v]) => [v, k as Region]),
) as Record<string, Region>;
export const CATEGORY_BY_SLUG = Object.fromEntries(
  Object.entries(CATEGORY_SLUG).map(([k, v]) => [v, k as Category]),
) as Record<string, Category>;

// 카테고리별 한 줄 설명 (지역 SEO 페이지·홈 카드용)
export const CATEGORY_DESC: Record<Category, string> = {
  실링팬:
    "저소음 BLDC 실링팬. 천장이 낮아도 부담 없는 슬림 보디로 공기 순환과 인테리어를 함께 잡습니다.",
  간접조명:
    "우물천장·커튼박스 간접조명. 은은한 빛으로 거실에 호텔 라운지의 깊이를 더합니다.",
  스마트조명:
    "색온도·밝기를 앱과 음성으로. 실링팬·커튼까지 하나로 묶는 스마트 라이팅.",
};

export const NAV = [
  { label: "실링팬", href: "/area/ulsan-ceiling-fan" },
  { label: "간접조명", href: "/area/ulsan-indirect-lighting" },
  { label: "스마트조명", href: "/area/ulsan-smart-lighting" },
  { label: "시공사례", href: "/cases" },
  { label: "고객후기", href: "/reviews" },
  { label: "쇼룸안내", href: "/showroom" },
  { label: "유튜브", href: "/youtube" },
  { label: "FAQ", href: "/faq" },
  { label: "상담문의", href: "/contact" },
] as const;

// ===== 엣지리브커튼 울산본점 — site-wide constants =====

export const SITE = {
  name: "엣지리브커튼",
  legalName: "㈜엣지컴퍼니",
  branch: "울산본점",
  tagline: "울산·양산·부산·경주 커튼·블라인드·전동커튼 전문 쇼룸",
  phone: "010-4900-6107",
  phoneRep: "1533-3210",
  address: "울산광역시",
  // 배포 후 실제 도메인으로 교체 (env NEXT_PUBLIC_SITE_URL 우선)
  url: process.env.NEXT_PUBLIC_SITE_URL || "https://edge-curtain.vercel.app",
  // 카카오톡 채널 채팅 URL (예: https://pf.kakao.com/_xxxx/chat) — 없으면 문자로 폴백
  kakao: process.env.NEXT_PUBLIC_KAKAO_URL || "",
  // 네이버 서치어드바이저 사이트 소유확인 메타값
  naverVerification: process.env.NEXT_PUBLIC_NAVER_VERIFICATION || "",
} as const;

export const REGIONS = ["울산", "양산", "부산", "경주"] as const;
export type Region = (typeof REGIONS)[number];

export const CATEGORIES = ["커튼", "블라인드", "전동커튼"] as const;
export type Category = (typeof CATEGORIES)[number];

// 한글 ↔ URL 슬러그 (지역 SEO 페이지 /area/<region>-<category>)
export const REGION_SLUG: Record<Region, string> = {
  울산: "ulsan",
  양산: "yangsan",
  부산: "busan",
  경주: "gyeongju",
};
export const CATEGORY_SLUG: Record<Category, string> = {
  커튼: "curtain",
  블라인드: "blind",
  전동커튼: "motorized-curtain",
};

export const REGION_BY_SLUG = Object.fromEntries(
  Object.entries(REGION_SLUG).map(([k, v]) => [v, k as Region]),
) as Record<string, Region>;
export const CATEGORY_BY_SLUG = Object.fromEntries(
  Object.entries(CATEGORY_SLUG).map(([k, v]) => [v, k as Category]),
) as Record<string, Category>;

// 카테고리별 한 줄 설명 (지역 SEO 페이지·홈 카드용)
export const CATEGORY_DESC: Record<Category, string> = {
  커튼:
    "암막·쉬어·린넨 커튼. 공간 무드와 채광을 함께 잡는 맞춤 제작·실측·시공으로 완성합니다.",
  블라인드:
    "롤·콤비·허니콤·우드 블라인드. 깔끔한 라인과 정밀한 빛 조절로 공간을 정돈합니다.",
  전동커튼:
    "리모컨·앱·음성으로 여닫는 전동커튼. 큰 창·높은 창도 버튼 하나로 편하게.",
};

export const NAV = [
  { label: "커튼", href: "/area/ulsan-curtain" },
  { label: "블라인드", href: "/area/ulsan-blind" },
  { label: "전동커튼", href: "/area/ulsan-motorized-curtain" },
  { label: "시공사례", href: "/cases" },
  { label: "고객후기", href: "/reviews" },
  { label: "쇼룸안내", href: "/showroom" },
  { label: "유튜브", href: "/youtube" },
  { label: "FAQ", href: "/faq" },
  { label: "상담문의", href: "/contact" },
] as const;

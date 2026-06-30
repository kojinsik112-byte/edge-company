import { createClient } from "./supabase/server";
import { SITE } from "./constants";

export interface SiteInfo {
  phone: string;
  phoneRep: string;
  address: string;
  kakao: string;
  instagram: string;
  youtube: string;
  blog: string;
  bizName: string;
  ceo: string;
  bizNo: string;
}
export interface Notice {
  enabled: boolean;
  text: string;
  link: string;
}
export interface Hero {
  video: string; // 배경 광고영상 (mp4 URL) — 있으면 영상 자동재생 루프, 없으면 이미지
  image: string; // PC(가로) 배너
  imageMobile: string; // 모바일(세로) 배너 — 비우면 PC 이미지 사용
  overlayTitle: string; // 영상/이미지 위에 얹는 라이브 텍스트 (비우면 미표시)
  overlaySub: string;
  eyebrow: string;
  title: string;
  subline: string;
  lead: string;
}
export interface CompanyFeature {
  title: string;
  desc: string;
}
export interface Company {
  image: string;
  title: string;
  body: string;
  eyebrow: string; // 영문 키커 (예: Why Edge Company)
  heading: string; // 큰 제목 (예: 왜 엣지컴퍼니일까요?)
  lead: string; // 리드 문구
  features: CompanyFeature[]; // 강점 카드 (4개 권장)
  trust: string[]; // 하단 신뢰 문구 (4개 권장)
}
export interface ProcessStep {
  title: string;
  desc: string;
  image: string; // 단계별 사진 (관리자 업로드)
}
export interface Process {
  title: string;
  desc: string;
  steps: ProcessStep[]; // 5단계 권장
}
export interface Simulator {
  enabled: boolean;
  image: string; // 시뮬레이션할 거실 사진 (관리자 교체)
  title: string;
  subtitle: string;
}
export interface Short {
  url: string; // 유튜브 숏츠 URL 또는 mp4 URL
  title: string;
  thumb: string; // 세로 썸네일 (관리자 업로드)
}
export interface Shorts {
  enabled: boolean;
  title: string;
  desc: string;
  items: Short[]; // 세로 9:16 숏츠 (무제한)
}
export interface Showroom {
  image: string;
  title: string;
  body: string;
  hours: string;
  images: string[]; // 쇼룸 갤러리 (최대 8장 + 안내보기 타일 = 3×3)
  map: string; // 오시는 길 지도 이미지 (관리자 업로드)
}
export type Categories = Record<string, string>; // 카테고리명 → 대표이미지 URL
export interface CategorySection {
  title: string; // 홈 시공사례 섹션 제목 (관리자 변경 가능)
  desc: string;
}
export type CategorySections = Record<string, CategorySection>;
export interface SeoSettings {
  home: { title: string; description: string; keywords: string; og: string };
}

// ===== 신규 섹션 (관리자에서 이미지·텍스트 편집) =====
export interface LicenseItem {
  image: string; // 면허/등록증 사진
  caption: string; // 등록증 이름
}
export interface License {
  title: string;
  desc: string;
  items: LicenseItem[]; // 1열 2개 권장
}
export interface Branch {
  name: string; // 지사명
  area: string; // 담당 지역
  phone: string; // 연락처
}
export interface Branches {
  title: string;
  desc: string;
  rows: Branch[]; // 표 행 (무제한)
  mapImage: string; // 전국 지사 지도 이미지
}
export interface Partner {
  image: string; // 로고
  name: string; // 협력사명
}
export interface Partners {
  title: string;
  desc: string;
  logos: Partner[]; // 3열 그리드 (무제한, 9개 권장)
}

export interface Settings {
  site: SiteInfo;
  notice: Notice;
  hero: Hero;
  company: Company;
  process: Process;
  simulator: Simulator;
  shorts: Shorts;
  showroom: Showroom;
  categories: Categories;
  categorySections: CategorySections;
  seo: SeoSettings;
  license: License;
  branches: Branches;
  partners: Partners;
}

export const DEFAULT_SETTINGS: Settings = {
  site: {
    phone: SITE.phone,
    phoneRep: SITE.phoneRep,
    address: "울산광역시 울주군 온산로 615-1",
    kakao: "",
    instagram: "",
    youtube: "",
    blog: "",
    bizName: "㈜엣지컴퍼니",
    ceo: "고진식",
    bizNo: "508-81-42798",
  },
  notice: { enabled: false, text: "울산 쇼룸 예약 상담 진행중", link: "/contact" },
  hero: {
    video: "",
    image: "/img/sofa.webp",
    imageMobile: "",
    overlayTitle: "빛과 바람으로\n집을 완성하다",
    overlaySub: "공간의 본질을 이해하고, 빛과 바람을 디자인합니다.",
    eyebrow: "/ edgecompany",
    title: "빛과 바람으로 완성하는\n프리미엄 공간",
    subline: "실링팬 · 간접조명 · 센서조명 전문 쇼룸",
    lead: "직접 보고, 비교하고, 체험한 뒤 선택할 수 있는 엣지컴퍼니 조명 쇼룸입니다.",
  },
  company: {
    image: "/img/sofa.webp",
    title: "엣지컴퍼니 소개",
    body: "전기공사업 면허를 보유한 법인이 직접 시공하는 프리미엄 조명 쇼룸입니다.",
    eyebrow: "Why Edge Company",
    heading: "왜 엣지컴퍼니일까요?",
    lead: "실링팬과 간접조명을 단순 설치하는 것이 아니라, 고객의 라이프스타일에 맞는 공간의 분위기를 제안합니다.",
    features: [
      { title: "직접 체험 가능한 쇼룸", desc: "울산 쇼룸에서 직접 켜 보고 비교" },
      { title: "풍부한 시공 경험", desc: "거실부터 상가까지 다양한 현장" },
      { title: "전문 시공 및 사후관리", desc: "면허 보유 법인이 직접 시공·관리" },
      { title: "스마트 조명 시스템", desc: "실링팬·조명·커튼을 앱 하나로" },
    ],
    trust: ["ISO 인증기업", "전기공사 면허 보유", "전국 네트워크 운영", "전문 시공 및 사후관리"],
  },
  process: {
    title: "상담부터 사후관리까지",
    desc: "복잡하지 않게, 정확하게. 엣지컴퍼니의 5단계 시공 과정입니다.",
    steps: [
      { title: "상담 신청", desc: "전화·문자·카톡 또는 온라인 상담으로 편하게 문의하세요.", image: "" },
      { title: "현장 실측", desc: "천장고·전기·공간을 확인하고 최적의 방식을 제안합니다.", image: "" },
      { title: "견적 · 디자인 제안", desc: "공간에 맞는 제품과 조명 설계를 투명한 견적으로 안내합니다.", image: "" },
      { title: "전문 시공", desc: "전기공사 면허 보유 시공팀이 안전하고 깔끔하게 설치합니다.", image: "" },
      { title: "사후관리", desc: "시공 후 점검과 A/S까지 책임지고 관리합니다.", image: "" },
    ],
  },
  simulator: {
    enabled: true,
    image: "/img/sofa.webp",
    title: "색온도를 직접 바꿔보세요",
    subtitle: "전구색부터 주광색까지 — 슬라이더를 움직여 우리 집 조명을 미리 경험하세요.",
  },
  shorts: {
    enabled: true,
    title: "엣지컴퍼니 숏츠",
    desc: "조명으로 풀어낸 짧은 영상 — 패러디부터 시공 비포애프터까지.",
    items: [],
  },
  showroom: {
    image: "/img/fan.webp",
    title: "직접 보고 비교하는 엣지컴퍼니 쇼룸",
    body: "실링팬, 간접조명, 센서조명을 직접 체험하고 비교할 수 있는 울산 프리미엄 쇼룸입니다.",
    hours: "방문 전 연락 주시면 대기 없이 안내해 드립니다",
    images: ["/img/living-hero.webp", "/img/indirect.webp", "/img/fan.webp", "/img/curtain.webp", "/img/sofa.webp"],
    map: "",
  },
  categories: {
    실링팬: "/img/fan.webp",
    간접조명: "/img/indirect.webp",
    기타: "/img/curtain.webp",
  },
  categorySections: {
    실링팬: { title: "실링팬 시공사례", desc: "실제 고객 시공 현장" },
    간접조명: { title: "간접조명 시공사례", desc: "빛의 분위기가 달라지는 공간" },
    기타: { title: "기타 시공사례", desc: "센서조명 · 스위치 · 전동커튼 등 다양한 시공" },
  },
  seo: { home: { title: "", description: "", keywords: "", og: "" } },
  license: {
    title: "엣지컴퍼니 전기 면허 등록증",
    desc: "전기공사업 면허를 보유한 법인이 직접 안전하게 시공합니다.",
    items: [
      { image: "", caption: "전기공사업 등록증" },
      { image: "", caption: "한국전기공사협회 회원증" },
    ],
  },
  branches: {
    title: "엣지컴퍼니 전국 지사",
    desc: "울산 본사를 중심으로 전국 주요 지역에서 시공을 진행합니다.",
    rows: [
      { name: "울산 본사", area: "울산 전역", phone: "010-4900-6107" },
    ],
    mapImage: "",
  },
  partners: {
    title: "엣지컴퍼니 협력사",
    desc: "믿을 수 있는 파트너와 함께합니다.",
    logos: [],
  },
};

/** 모든 설정을 한 번에 읽어 기본값과 병합 (Supabase 미연결/누락 키는 기본값) */
export async function getSettings(): Promise<Settings> {
  const supabase = await createClient();
  const merged: Settings = structuredClone(DEFAULT_SETTINGS);
  if (!supabase) return merged;
  try {
    const { data } = await supabase.from("settings").select("key,value");
    for (const row of data ?? []) {
      const key = row.key as string;
      if (key in merged) {
        const m = merged as unknown as Record<string, Record<string, unknown>>;
        m[key] = { ...m[key], ...(row.value ?? {}) };
      }
    }
  } catch {
    // 무시 — 기본값 사용
  }
  return merged;
}

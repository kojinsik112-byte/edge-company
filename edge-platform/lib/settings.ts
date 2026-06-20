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
  image: string; // PC(가로) 배너
  imageMobile: string; // 모바일(세로) 배너 — 비우면 PC 이미지 사용
  eyebrow: string;
  title: string;
  subline: string;
  lead: string;
}
export interface Company {
  image: string;
  title: string;
  body: string;
}
export interface Showroom {
  image: string;
  title: string;
  body: string;
  hours: string;
  images: string[]; // 쇼룸 갤러리 (4~6장)
  map: string; // 오시는 길 지도 이미지 (관리자 업로드)
}
export type Categories = Record<string, string>; // 카테고리명 → 대표이미지 URL
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
  showroom: Showroom;
  categories: Categories;
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
    image: "/img/living-hero.webp",
    imageMobile: "",
    eyebrow: "울산 · 부산 · 포항 · 경주",
    title: "빛과 바람으로 완성하는\n프리미엄 공간",
    subline: "실링팬 · 간접조명 · 센서조명 전문 쇼룸",
    lead: "직접 보고, 비교하고, 체험한 뒤 선택할 수 있는 엣지컴퍼니 조명 쇼룸입니다.",
  },
  company: {
    image: "/img/sofa.webp",
    title: "엣지컴퍼니 소개",
    body: "전기공사업 면허를 보유한 법인이 직접 시공하는 프리미엄 조명 쇼룸입니다.",
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
    센서조명: "/img/curtain.webp",
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

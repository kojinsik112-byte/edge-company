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

export interface Settings {
  site: SiteInfo;
  notice: Notice;
  hero: Hero;
  company: Company;
  showroom: Showroom;
  categories: Categories;
  seo: SeoSettings;
}

export const DEFAULT_SETTINGS: Settings = {
  site: {
    phone: SITE.phone,
    phoneRep: SITE.phoneRep,
    address: "울산광역시",
    kakao: "",
    instagram: "",
    youtube: "",
    blog: "",
    bizName: "㈜엣지컴퍼니",
    ceo: "고진식",
    bizNo: "508-81-42798",
  },
  notice: { enabled: false, text: "울산 커튼 쇼룸 예약 상담 진행중", link: "/contact" },
  hero: {
    image: "/img/curtain.webp",
    imageMobile: "",
    eyebrow: "울산 · 양산 · 부산 · 경주",
    title: "공간의 분위기를 완성하는\n맞춤 커튼 · 블라인드",
    subline: "커튼 · 블라인드 · 전동커튼 전문 쇼룸",
    lead: "직접 보고, 만져보고, 비교한 뒤 선택하는 엣지리브커튼 울산본점입니다.",
  },
  company: {
    image: "/img/sofa.webp",
    title: "엣지리브커튼 소개",
    body: "정확한 실측과 맞춤 제작으로 시공하는 울산 커튼·블라인드 전문 쇼룸입니다.",
  },
  showroom: {
    image: "/img/curtain.webp",
    title: "직접 보고 고르는 엣지리브커튼 쇼룸",
    body: "커튼·블라인드 원단과 색상을 직접 만져보고 비교할 수 있는 울산본점 쇼룸입니다.",
    hours: "방문 전 연락 주시면 대기 없이 안내해 드립니다",
    images: ["/img/living-hero.webp", "/img/curtain.webp", "/img/indirect.webp", "/img/sofa.webp"],
    map: "",
  },
  categories: {
    커튼: "/img/curtain.webp",
    블라인드: "/img/indirect.webp",
    전동커튼: "/img/sofa.webp",
  },
  seo: { home: { title: "", description: "", keywords: "", og: "" } },
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

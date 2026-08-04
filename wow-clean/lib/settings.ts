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
  overlayColor: string; // 글자 색상 (hex)
  overlayTitleSize: number; // 큰 글자 크기 (데스크탑 px)
  overlayWeight: string; // 굵기 "300"|"500"|"600"|"700"|"800"
  overlaySerif: boolean; // true면 명조(세리프) 글꼴
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
  eyebrow: string; // 영문 키커 (예: Why Wow Clean)
  heading: string; // 큰 제목 (예: 왜 와우클린일까요?)
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
  image: string; // 시뮬레이션할 사진 (관리자 교체)
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
  images: string[]; // 현장 갤러리 (최대 8장 + 안내보기 타일 = 3×3)
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
  image: string; // 등록증/증빙 사진
  caption: string; // 등록증 이름
}
export interface License {
  title: string;
  desc: string;
  items: LicenseItem[]; // 1열 2개 권장
}
export interface Branch {
  name: string; // 지역명
  area: string; // 담당 지역
  phone: string; // 연락처
}
export interface Branches {
  title: string;
  desc: string;
  rows: Branch[]; // 표 행 (무제한)
  mapImage: string; // 전국 출동 지도 이미지
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
    address: "전국 24시간 출동 서비스",
    kakao: "",
    instagram: "https://www.instagram.com/dadongjib",
    youtube: "",
    blog: "https://blog.naver.com/ljs4510",
    bizName: "와우클린 하수구변기막힘설비",
    ceo: "안영란",
    bizNo: "575-41-01087",
  },
  notice: { enabled: true, text: "🚨 전국 24시간 긴급 출동 접수 중 — 1668-5982", link: "/contact" },
  hero: {
    video: "",
    image: "/img/hero.svg",
    imageMobile: "",
    overlayTitle: "막힌 곳은 뚫고,\n깨끗함은 남깁니다",
    overlaySub: "하수구·변기 막힘, 고압 배관청소, 누수탐지까지.\n시공 전 투명 견적, 작업 후 A/S 보증.",
    overlayColor: "#ffffff",
    overlayTitleSize: 56,
    overlayWeight: "700",
    overlaySerif: false,
    eyebrow: "전국 24시간 긴급 출동 접수 중",
    title: "막힌 곳은 뚫고,\n깨끗함은 남깁니다",
    subline: "하수구막힘 · 변기막힘 · 배관청소 전문",
    lead: "원인을 확인한 뒤 시공 전에 비용을 확정하고, 작업이 끝나면 사진으로 남기는 와우클린입니다.",
  },
  company: {
    image: "/img/why.svg",
    title: "와우클린 소개",
    body: "하수구·변기 막힘 뚫음, 고압 배관청소, 누수탐지를 전문으로 하는 전국 24시간 출동 시공 기업입니다.",
    eyebrow: "Why Wow Clean",
    heading: "왜 와우클린일까요?",
    lead: "막혔을 때 제일 무서운 건 부르고 나서 얼마 나올지 모른다는 것. 와우클린은 원인을 확인한 뒤 시공 전에 비용을 확정해서 알려드립니다.",
    features: [
      { title: "시공 전 투명 견적", desc: "원인 확인 후 작업 전에 금액 확정" },
      { title: "전국 24시간 출동", desc: "연중무휴 접수 · 야간 긴급 대응" },
      { title: "장비로 원인부터 해결", desc: "고압세척 · 관로 스프링 · 배관 내시경" },
      { title: "작업 후 A/S 보증", desc: "같은 부위 재발 시 보증 기준으로 재방문" },
    ],
    trust: ["사업자 정식 등록", "현금영수증·세금계산서 발행", "현장 사진 리포트", "가정·상가·건물 대응"],
  },
  process: {
    title: "접수부터 A/S 보증까지",
    desc: "복잡하지 않게, 정확하게. 와우클린의 5단계 시공 과정입니다.",
    steps: [
      { title: "전화 · 온라인 접수", desc: "증상과 위치를 알려주시면 연중무휴 24시간 접수됩니다.", image: "" },
      { title: "가까운 기사 배정 · 출동", desc: "지역별 담당 기사가 배정되어 빠르게 방문합니다.", image: "" },
      { title: "원인 확인 · 견적 확정", desc: "함부로 뜯지 않고 원인을 확인한 뒤, 작업 전에 비용을 확정합니다.", image: "" },
      { title: "전문 장비 시공", desc: "고압세척·관로 스프링 등 전문 장비로 깔끔하게 해결합니다.", image: "" },
      { title: "사진 리포트 · A/S 보증", desc: "작업 결과를 사진으로 남기고, 재발 시 보증 기준에 따라 다시 봐드립니다.", image: "" },
    ],
  },
  simulator: {
    enabled: false,
    image: "",
    title: "",
    subtitle: "",
  },
  shorts: {
    enabled: false, // 실제 시공 영상이 등록되면 관리자에서 ON ('곧 공개' 빈 박스 노출 방지)
    title: "현장이 증거입니다",
    desc: "말보다 확실한 시공 영상 — 어떻게 뚫고, 어떻게 마무리하는지 직접 보세요.",
    items: [],
  },
  showroom: {
    image: "/img/cat-pipe.svg",
    title: "와우클린 시공 현장",
    body: "가정 욕실부터 상가 주방, 건물 공용 배관까지 — 와우클린이 실제로 해결한 현장들입니다.",
    hours: "연중무휴 24시간 접수 · 야간 긴급 출동 가능",
    images: ["/img/van.svg", "/img/cat-drain.svg", "/img/kitchen.svg", "/img/cat-toilet.svg", "/img/cat-pipe.svg"],
    map: "",
  },
  categories: {
    하수구막힘: "/img/cat-drain.svg",
    변기막힘: "/img/cat-toilet.svg",
    배관청소: "/img/cat-pipe.svg",
    수전교체: "/img/svc-faucet.svg",
    내시경검사: "/img/svc-scope.svg",
    관로탐지: "/img/svc-detect.svg",
    누수탐지: "/img/svc-leak.svg",
  },
  categorySections: {
    하수구막힘: { title: "하수구막힘 시공사례", desc: "욕실·베란다·마당 하수구 뚫음 현장" },
    변기막힘: { title: "변기막힘 시공사례", desc: "역류·이물질까지 깔끔하게 해결한 현장" },
    배관청소: { title: "배관청소 시공사례", desc: "고압세척으로 배관 속까지 되살린 현장" },
    수전교체: { title: "수전·부속 교체 시공사례", desc: "각종 수전·배관 부속 교체 현장" },
    내시경검사: { title: "내시경 카메라 검사 사례", desc: "배관 내부를 눈으로 확인한 진단 현장" },
    관로탐지: { title: "배관 관로 탐지 사례", desc: "벽·바닥 속 배관 경로를 정확히 찾은 현장" },
    누수탐지: { title: "누수 탐지 시공사례", desc: "누수 지점을 특정해 최소 시공한 현장" },
  },
  seo: {
    home: {
      title: "와우클린 | 하수구막힘·변기막힘·배관청소 전국 24시간 출동",
      description:
        "와우클린은 하수구 막힘 뚫음, 변기막힘, 고압 배관청소, 누수탐지를 전문으로 하는 전국 24시간 출동 시공 기업입니다. 시공 전 투명 견적, 작업 후 A/S 보증. 대표번호 1668-5982.",
      keywords: "하수구막힘, 변기막힘, 배관청소, 하수구뚫음, 고압세척, 싱크대막힘, 누수탐지, 24시간 하수구, 와우클린",
      og: "",
    },
  },
  license: {
    title: "와우클린 정식 등록 업체",
    desc: "사업자 정식 등록 업체로, 현금영수증·세금계산서 등 정식 증빙을 발행합니다.",
    items: [
      { image: "", caption: "사업자등록증" },
    ],
  },
  branches: {
    title: "와우클린 전국 출동 지역",
    desc: "전국 주요 지역에 담당 기사가 배정되어 있어 어디서든 빠르게 출동합니다.",
    rows: [
      { name: "서울", area: "서울 전역", phone: "1668-5982" },
      { name: "경기 · 인천", area: "경기 전역 · 인천", phone: "1668-5982" },
      { name: "부산 · 경남", area: "부산 · 울산 · 창원 · 김해", phone: "1668-5982" },
      { name: "대구 · 경북", area: "대구 · 포항 · 구미 · 경주", phone: "1668-5982" },
      { name: "대전 · 충청", area: "대전 · 세종 · 천안 · 청주", phone: "1668-5982" },
      { name: "광주 · 전라", area: "광주 · 전주 · 목포 · 여수", phone: "1668-5982" },
    ],
    mapImage: "",
  },
  partners: {
    title: "와우클린 협력사",
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

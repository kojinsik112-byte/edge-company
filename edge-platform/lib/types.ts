import type { Region, Category } from "./constants";

export interface CaseRow {
  id: string;
  created_at: string;
  updated_at: string | null;
  title: string;
  slug: string;
  region: Region;
  category: Category;
  apartment: string;
  cover: string | null; // public URL
  images: string[]; // public URLs
  body: string;
  tags: string[];
  seo_title: string | null;
  seo_description: string | null;
  published: boolean;
}

export interface ReviewRow {
  id: string;
  created_at: string;
  name: string; // 작성자
  apartment: string | null; // 아파트명
  region: Region | null;
  rating: number; // 1~5
  content: string;
  image: string | null;
  published: boolean;
}

export interface FaqRow {
  id: string;
  created_at: string;
  question: string;
  answer: string;
  sort: number;
  published: boolean;
}

export interface ProductRow {
  id: string;
  created_at: string;
  name: string;
  category: string;
  image: string | null;
  body: string;
  sort: number;
  published: boolean;
}

export interface YoutubeRow {
  id: string;
  created_at: string;
  video_id: string; // 유튜브 영상 ID
  title: string;
  views: string | null; // "1.2만회" 등 표기 텍스트
  sort: number;
  published: boolean;
}

// 이미지 미연결(빈 DB) 상태에서도 사이트가 보이도록 쓰는 기본 비주얼
export const FALLBACK_IMAGES = {
  hero: "/img/living-hero.webp",
  fan: "/img/fan.webp",
  indirect: "/img/indirect.webp",
  curtain: "/img/curtain.webp",
  sofa: "/img/sofa.webp",
} as const;

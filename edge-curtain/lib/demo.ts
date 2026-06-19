// 미리보기용 예시 콘텐츠 — DB가 비었을 때 메인이 꽉 차 보이도록 사용.
// 실제 데이터(관리자 등록)가 있으면 그쪽이 우선 노출된다. (전부 '예시' 표기)

const IMGS = ["/img/living-hero.webp", "/img/curtain.webp", "/img/indirect.webp", "/img/sofa.webp"];

export function demoTiles(n = 6): { img: string }[] {
  return Array.from({ length: n }, (_, i) => ({ img: IMGS[i % IMGS.length] }));
}

export interface DemoReview {
  id: string;
  title: string | null;
  name: string;
  apartment: string | null;
  region: string;
  rating: number;
  content: string;
  image: string | null;
  demo: true;
}

export const DEMO_REVIEWS: DemoReview[] = [
  { id: "d1", title: "거실 분위기가 완전히 달라졌어요", name: "김○○ 고객님", apartment: "예시 아파트", region: "울산", rating: 5, content: "암막 커튼 설치 후 거실 분위기가 확 살았어요. 색감도 딱 원하던 대로였습니다.", image: "/img/living-hero.webp", demo: true },
  { id: "d2", title: "원단 색이 사진보다 예뻐요", name: "이○○ 고객님", apartment: "예시 아파트", region: "부산", rating: 5, content: "쇼룸에서 직접 보고 고른 린넨 커튼, 채광이 은은해서 정말 만족합니다.", image: "/img/curtain.webp", demo: true },
  { id: "d3", title: "실측·상담이 꼼꼼했어요", name: "박○○ 고객님", apartment: "예시 아파트", region: "양산", rating: 5, content: "방문 실측부터 시공까지 친절하고 깔끔했습니다. 추천해요.", image: null, demo: true },
  { id: "d4", title: "전동커튼 너무 편해요", name: "최○○ 고객님", apartment: "예시 아파트", region: "경주", rating: 4, content: "큰 창이라 고민했는데 전동커튼으로 리모컨 한 번에 여닫아 편합니다.", image: "/img/indirect.webp", demo: true },
  { id: "d5", title: "블라인드 라인이 깔끔해요", name: "정○○ 고객님", apartment: "예시 아파트", region: "울산", rating: 5, content: "콤비 블라인드로 빛 조절이 쉬워졌고 공간이 정돈된 느낌이에요.", image: "/img/sofa.webp", demo: true },
  { id: "d6", title: "직접 보고 골라서 후회 없어요", name: "한○○ 고객님", apartment: "예시 아파트", region: "부산", rating: 5, content: "쇼룸에서 원단 만져보고 골라서 후회 없습니다. A/S도 친절했어요.", image: "/img/living-hero.webp", demo: true },
];

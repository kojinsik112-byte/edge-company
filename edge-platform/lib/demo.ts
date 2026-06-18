// 미리보기용 예시 콘텐츠 — DB가 비었을 때 메인이 꽉 차 보이도록 사용.
// 실제 데이터(관리자 등록)가 있으면 그쪽이 우선 노출된다. (전부 '예시' 표기)

const IMGS = ["/img/living-hero.webp", "/img/indirect.webp", "/img/fan.webp", "/img/sofa.webp", "/img/curtain.webp"];

export function demoTiles(n = 6): { img: string }[] {
  return Array.from({ length: n }, (_, i) => ({ img: IMGS[i % IMGS.length] }));
}

export interface DemoReview {
  id: string;
  name: string;
  region: string;
  rating: number;
  content: string;
  image: string | null;
  demo: true;
}

export const DEMO_REVIEWS: DemoReview[] = [
  { id: "d1", name: "예시 고객", region: "울산", rating: 5, content: "실링팬 설치 후 거실 분위기가 완전히 달라졌습니다.", image: "/img/living-hero.webp", demo: true },
  { id: "d2", name: "예시 고객", region: "부산", rating: 5, content: "간접조명 색감이 정말 만족스럽습니다.", image: "/img/indirect.webp", demo: true },
  { id: "d3", name: "예시 고객", region: "포항", rating: 5, content: "상담부터 시공까지 친절하고 깔끔했습니다.", image: null, demo: true },
  { id: "d4", name: "예시 고객", region: "경주", rating: 4, content: "스마트조명으로 생활이 한결 편해졌어요.", image: "/img/curtain.webp", demo: true },
  { id: "d5", name: "예시 고객", region: "울산", rating: 5, content: "저천장이라 걱정했는데 슬림팬으로 깔끔하게 설치됐습니다.", image: "/img/fan.webp", demo: true },
  { id: "d6", name: "예시 고객", region: "부산", rating: 5, content: "쇼룸에서 직접 보고 골라서 후회 없습니다.", image: "/img/sofa.webp", demo: true },
];

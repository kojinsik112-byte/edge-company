// 미리보기용 예시 콘텐츠 — DB가 비었을 때 메인이 꽉 차 보이도록 사용.
// 실제 데이터(관리자 등록)가 있으면 그쪽이 우선 노출된다. (전부 '예시' 표기)

const IMGS = ["/img/hero.svg", "/img/cat-drain.svg", "/img/cat-toilet.svg", "/img/cat-pipe.svg"];

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
  { id: "d1", title: "10분 만에 뻥 뚫렸어요", name: "김○○ 고객님", apartment: "예시 현장", region: "서울", rating: 5, content: "욕실 하수구가 꽉 막혔었는데 기사님이 장비로 10분 만에 뚫어주셨어요. 뒷정리까지 깔끔합니다.", image: "/img/cat-drain.svg", demo: true },
  { id: "d2", title: "부르기 전에 가격부터 알려줘서 안심", name: "이○○ 고객님", apartment: "예시 현장", region: "경기", rating: 5, content: "작업 전에 비용을 확정해서 알려주시니 바가지 걱정이 없었어요. 영수증도 바로 발행해 주셨습니다.", image: null, demo: true },
  { id: "d3", title: "새벽에 변기 역류, 바로 와주셨어요", name: "박○○ 고객님", apartment: "예시 현장", region: "부산", rating: 5, content: "새벽에 변기가 역류해서 전화했는데 가까운 기사님이 배정돼 금방 오셨어요. 응대도 친절했습니다.", image: "/img/cat-toilet.svg", demo: true },
  { id: "d4", title: "식당 배관 고압세척, 냄새까지 해결", name: "최○○ 사장님", apartment: "예시 상가", region: "대구", rating: 5, content: "주방 배관 기름때를 고압세척으로 싹 걷어내니 물 빠짐도 냄새도 해결됐습니다. 정기 관리 맡기려고요.", image: "/img/cat-pipe.svg", demo: true },
  { id: "d5", title: "작업 사진으로 남겨줘서 믿음이 가요", name: "정○○ 고객님", apartment: "예시 현장", region: "인천", rating: 5, content: "작업 전후 사진을 찍어 보내주셔서 뭘 어떻게 했는지 한눈에 알 수 있었어요.", image: null, demo: true },
  { id: "d6", title: "재발 없게 원인까지 잡아줌", name: "한○○ 고객님", apartment: "예시 현장", region: "울산", rating: 5, content: "그냥 뚫고 끝이 아니라 막힌 원인을 설명해 주시고 재발 방지 방법까지 알려주셨습니다.", image: "/img/hero.svg", demo: true },
];

// 미리보기용 예시 콘텐츠 — DB가 비었을 때 메인이 꽉 차 보이도록 사용.
// 실제 데이터(관리자 등록)가 있으면 그쪽이 우선 노출된다. (전부 '예시' 표기)

const IMGS = ["/img/hero.svg", "/img/cat-drain.svg", "/img/cat-toilet.svg", "/img/cat-pipe.svg", "/img/kitchen.svg", "/img/van.svg"];

export function demoTiles(n = 6): { img: string }[] {
  return Array.from({ length: n }, (_, i) => ({ img: IMGS[i % IMGS.length] }));
}

// 서비스 폴백 — DB(제품) 비어있을 때 홈·서비스 페이지에 표시 (관리자 등록 시 대체)
export interface DemoService {
  name: string;
  category: string;
  body: string;
  image: string;
}

export const DEMO_SERVICES: DemoService[] = [
  { name: "하수구 막힘 뚫음", category: "하수구", body: "욕실·베란다·마당 하수구 막힘. 원인 확인 후 장비로 관통합니다.", image: "/img/cat-drain.svg" },
  { name: "변기 막힘 · 역류", category: "변기", body: "변기 막힘·역류·이물질 제거. 함부로 뜯지 않고 해결합니다.", image: "/img/cat-toilet.svg" },
  { name: "싱크대 · 주방 배관 막힘", category: "싱크대", body: "기름때로 굳은 주방 배관을 관통하고 재발 방지법까지 안내합니다.", image: "/img/kitchen.svg" },
  { name: "고압 배관청소", category: "배관청소", body: "고압세척으로 배관 속 기름때·슬러지를 걷어내 재막힘을 줄입니다.", image: "/img/cat-pipe.svg" },
  { name: "각종 수전 · 부속 교체", category: "설비교체", body: "세면대·주방 수전, 배관 부속을 규격에 맞게 교체 시공합니다.", image: "/img/svc-faucet.svg" },
  { name: "하수구 내시경 카메라 검사", category: "정밀진단", body: "배관 내부를 카메라로 직접 확인해 막힘·파손 원인을 눈으로 보여드립니다.", image: "/img/svc-scope.svg" },
  { name: "배관 관로 탐지", category: "정밀진단", body: "벽·바닥 속 배관의 위치와 경로를 장비로 정확히 찾아냅니다.", image: "/img/svc-detect.svg" },
  { name: "누수 탐지", category: "정밀진단", body: "장비 탐지로 누수 지점을 특정해 필요한 부위만 정확히 시공합니다.", image: "/img/svc-leak.svg" },
];

// FAQ 폴백 — DB(Supabase) 미연결/비어있을 때 홈·FAQ 페이지에 표시 (관리자 등록 시 대체)
export interface DemoFaq {
  id: string;
  question: string;
  answer: string;
}

export const DEMO_FAQS: DemoFaq[] = [
  { id: "f1", question: "정말 24시간 접수되나요?", answer: "네, 접수는 연중무휴 24시간 가능합니다. 야간·새벽 긴급 상황은 전화 접수(1668-8982)를 이용하시면 가장 빠르게 안내해 드립니다." },
  { id: "f2", question: "비용은 언제 알 수 있나요?", answer: "전화·상담 시 증상과 위치를 바탕으로 예상 범위를 먼저 안내합니다. 현장 확인 후 작업 전에 최종 금액을 확정하며, 동의하신 뒤에만 시공을 시작합니다." },
  { id: "f3", question: "출동까지 얼마나 걸리나요?", answer: "지역별 담당 기사가 배정되어 가까운 기사가 방문합니다. 지역·시간대·현장 상황에 따라 소요 시간은 달라질 수 있으며, 접수 시 예상 시간을 안내드립니다." },
  { id: "f4", question: "결제는 어떻게 하나요? 증빙 발행되나요?", answer: "현금·카드·계좌이체 모두 가능합니다. 현금영수증, 세금계산서 등 정식 증빙도 발행해 드립니다. 사업자 정식 등록 업체입니다." },
  { id: "f5", question: "야간·주말·공휴일에도 오나요?", answer: "접수는 연중무휴 24시간 가능합니다. 야간·주말 긴급 상황은 전화로 접수하시면 가장 빠르게 안내해 드립니다." },
  { id: "f6", question: "작업 후 또 막히면 어떻게 하나요?", answer: "작업 부위에 문제가 재발하면 보증 기준에 따라 다시 봐드립니다. 작업 결과는 사진으로 남겨 투명하게 확인하실 수 있습니다." },
  { id: "f7", question: "함부로 뜯거나 부수지 않나요?", answer: "원인을 확인하기 전에는 함부로 해체하지 않습니다. 상태를 확인하고 필요한 작업과 비용을 먼저 안내한 뒤, 동의하신 범위에서만 시공합니다." },
  { id: "f8", question: "가정집 말고 상가·건물도 되나요?", answer: "네. 가정 욕실·주방부터 식당·카페 등 상가 주방 배관, 건물 공용 배관 고압세척까지 모두 대응합니다." },
];

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

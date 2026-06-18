import Image from "next/image";
import DragScroll from "@/components/DragScroll";
import type { ProductRow } from "@/lib/types";

const DEMO: { name: string; category: string; body: string; image: string }[] = [
  { name: "유선 스위치", category: "스위치", body: "공간에 어울리는 디자인 유선 스위치. 깔끔한 매립 시공.", image: "/img/curtain.webp" },
  { name: "실링팬", category: "실링팬", body: "저소음 BLDC 슬림 실링팬. 저천장에도 부담 없는 디자인.", image: "/img/fan.webp" },
  { name: "COB 조명", category: "조명", body: "선처럼 매립되는 COB 라인조명. 간접조명의 깊이를 더합니다.", image: "/img/indirect.webp" },
];

export default function ProductsSection({ products }: { products: ProductRow[] }) {
  const showDemo = products.length === 0;
  const items = showDemo ? DEMO : products;
  return (
    <section className="bg-surface py-16 md:py-24">
      <div className="reveal mx-auto mb-10 max-w-[640px] px-6 text-center">
        <p className="kicker">Products</p>
        <h2 className="mt-3 text-[26px] font-extrabold text-ink md:text-[32px]">엣지컴퍼니 제품 소개</h2>
        <p className="mt-3 text-[14.5px] text-muted">유선스위치 · 실링팬 · COB조명까지. 항목이 많으면 옆으로 넘겨보세요.</p>
      </div>
      {/* 적으면 가운데 정렬, 많으면 옆으로 스크롤 */}
      <DragScroll className="no-scrollbar mx-auto max-w-[1320px] overflow-x-auto px-6">
        <div className="mx-auto flex w-max gap-5 pb-3">
          {items.map((p, i) => (
            <div key={"id" in p ? p.id : i} className="w-[300px] shrink-0 overflow-hidden rounded-2xl border border-line bg-surface shadow-[0_10px_30px_-20px_rgba(15,35,66,0.2)]">
              <div className="relative aspect-[4/3] overflow-hidden bg-bg">
                {p.image && <Image src={p.image} alt={p.name} fill sizes="300px" className="object-cover" />}
                {showDemo && <span className="absolute left-3 top-3 rounded-full bg-white/85 px-2.5 py-1 text-[11px] font-semibold text-ink/70 backdrop-blur-sm">예시</span>}
              </div>
              <div className="p-6">
                {p.category && <span className="text-[12px] font-semibold text-gold-d">{p.category}</span>}
                <h3 className="mt-1 text-[18px] font-bold text-ink">{p.name}</h3>
                {p.body && <p className="mt-2 whitespace-pre-wrap text-[13.5px] leading-relaxed text-muted">{p.body}</p>}
              </div>
            </div>
          ))}
        </div>
      </DragScroll>
    </section>
  );
}

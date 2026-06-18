import Image from "next/image";
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
      <div className="mx-auto max-w-[1320px] px-6">
        <div className="mx-auto mb-12 max-w-[640px] text-center">
          <p className="kicker">Products</p>
          <h2 className="mt-3 text-[26px] font-extrabold text-ink md:text-[32px]">엣지컴퍼니 제품 소개</h2>
          <p className="mt-3 text-[14.5px] text-muted">유선스위치 · 실링팬 · COB조명까지, 공간을 완성하는 제품을 직접 만나보세요.</p>
        </div>
        <div className="grid gap-5 sm:grid-cols-2 lg:grid-cols-3">
          {items.map((p, i) => (
            <div key={"id" in p ? p.id : i} className="group overflow-hidden rounded-2xl border border-line bg-surface shadow-[0_10px_30px_-18px_rgba(15,35,66,0.2)] transition hover:-translate-y-1 hover:shadow-[0_24px_50px_-26px_rgba(15,35,66,0.3)]">
              <div className="relative aspect-[4/3] overflow-hidden bg-bg">
                {p.image && <Image src={p.image} alt={p.name} fill sizes="(max-width:768px) 100vw, 400px" className="object-cover transition duration-500 group-hover:scale-[1.04]" />}
                {showDemo && <span className="absolute left-3 top-3 rounded-full bg-white/85 px-2.5 py-1 text-[11px] font-semibold text-ink/70 backdrop-blur-sm">예시</span>}
              </div>
              <div className="p-6">
                {p.category && <span className="text-[12px] font-semibold text-gold-d">{p.category}</span>}
                <h3 className="mt-1 text-[18px] font-bold text-ink">{p.name}</h3>
                {p.body && <p className="mt-2 line-clamp-3 text-[13.5px] leading-relaxed text-muted">{p.body}</p>}
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}

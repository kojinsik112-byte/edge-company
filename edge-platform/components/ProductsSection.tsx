import Image from "next/image";
import Link from "next/link";
import type { ProductRow } from "@/lib/types";

const DEMO: { name: string; category: string; body: string; image: string }[] = [
  { name: "유선 스위치", category: "스위치", body: "공간에 어울리는 디자인 유선 스위치. 깔끔한 매립 시공.", image: "/img/curtain.webp" },
  { name: "실링팬", category: "실링팬", body: "저소음 BLDC 슬림 실링팬. 저천장에도 부담 없는 디자인.", image: "/img/fan.webp" },
  { name: "COB 조명", category: "간접조명", body: "선처럼 매립되는 COB 라인조명. 간접조명의 깊이를 더합니다.", image: "/img/indirect.webp" },
  { name: "센서등", category: "센서조명", body: "사람이 다가오면 자동으로 켜지는 현관·복도 센서등.", image: "/img/sofa.webp" },
];

export default function ProductsSection({ products }: { products: ProductRow[] }) {
  const showDemo = products.length === 0;
  const items = (showDemo ? DEMO : products).slice(0, 4); // 한 줄 2개 × 2줄 = 4개
  const hasMore = !showDemo && products.length > 4;
  return (
    <section className="bg-surface py-16 md:py-24">
      <div className="reveal mx-auto mb-10 max-w-[640px] px-6 text-center">
        <p className="kicker">Products</p>
        <h2 className="mt-3 text-[26px] font-extrabold text-ink md:text-[32px]">엣지컴퍼니 제품 소개</h2>
        <p className="mt-3 text-[16px] leading-relaxed text-muted">실링팬 · 스위치 · COB 간접조명 · 전동커튼 · 센서등까지. 엣지컴퍼니가 직접 시공하는 제품들입니다.</p>
      </div>
      {/* 한 줄 2개 × 2줄 = 4개, 클릭 시 상세 */}
      <div className="reveal mx-auto grid max-w-[1320px] grid-cols-2 gap-5 px-6 md:gap-6">
        {items.map((p, i) => {
          const inner = (
            <>
              <div className="relative aspect-[4/3] overflow-hidden bg-bg">
                {p.image && <Image src={p.image} alt={p.name} fill sizes="(max-width:1360px) 46vw, 640px" className="object-cover transition duration-500 group-hover:scale-[1.04]" />}
                {showDemo && <span className="absolute left-3 top-3 rounded-full bg-white/85 px-2.5 py-1 text-[11px] font-semibold text-ink/70 backdrop-blur-sm">예시</span>}
              </div>
              <div className="p-5">
                {p.category && <span className="text-[12px] font-semibold text-gold-d">{p.category}</span>}
                <h3 className="mt-1 text-[16px] font-bold text-ink">{p.name}</h3>
                {p.body && <p className="mt-2 line-clamp-3 whitespace-pre-wrap text-[13px] leading-relaxed text-muted">{p.body}</p>}
              </div>
            </>
          );
          const cls = "group overflow-hidden rounded-2xl border border-line bg-surface shadow-[0_10px_30px_-20px_rgba(15,35,66,0.2)] transition hover:-translate-y-1 hover:shadow-[0_22px_45px_-24px_rgba(15,35,66,0.25)]";
          return showDemo ? (
            <div key={i} className={cls}>{inner}</div>
          ) : (
            <Link key={(p as ProductRow).id} href={`/products/${(p as ProductRow).id}`} className={`block ${cls}`}>{inner}</Link>
          );
        })}
      </div>
      <div className="mt-9 text-center">
        <Link href="/products" className="inline-block rounded-lg border border-line bg-surface px-7 py-3.5 text-[15px] font-semibold text-ink transition hover:border-gold">
          {hasMore ? "제품 더 보기" : "전체 상품 보러가기"}
        </Link>
      </div>
    </section>
  );
}

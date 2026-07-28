import Image from "next/image";
import Link from "next/link";
import type { ProductRow } from "@/lib/types";
import { DEMO_SERVICES as DEMO } from "@/lib/demo";

export default function ProductsSection({ products }: { products: ProductRow[] }) {
  const showDemo = products.length === 0;
  const items = (showDemo ? DEMO : products).slice(0, 8); // 한 줄 4개 × 2줄 = 8개
  const hasMore = !showDemo && products.length > 8;
  return (
    <section className="bg-surface py-16 md:py-24">
      <div className="reveal mx-auto mb-10 max-w-[640px] px-6 text-center">
        <p className="kicker">Services</p>
        <h2 className="mt-3 text-[26px] font-extrabold text-ink md:text-[32px]">와우클린 서비스 안내</h2>
        <p className="mt-3 text-[14.5px] text-muted">막힘 뚫음부터 수전 교체, 내시경 검사, 관로·누수 탐지까지. 와우클린이 직접 시공하는 서비스입니다.</p>
      </div>
      {/* 한 줄 4개 그리드 (모바일 2열) · 최대 8개, 클릭 시 상세 */}
      <div className="reveal mx-auto grid max-w-[1200px] grid-cols-2 gap-5 px-6 md:grid-cols-4">
        {items.map((p, i) => {
          const inner = (
            <>
              <div className="relative aspect-[4/3] overflow-hidden bg-bg">
                {p.image && <Image src={p.image} alt={p.name} fill sizes="(max-width:768px) 50vw, 280px" className="object-cover transition duration-500 group-hover:scale-[1.04]" />}
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
          {hasMore ? "서비스 더 보기" : "서비스 전체 보기"}
        </Link>
      </div>
    </section>
  );
}

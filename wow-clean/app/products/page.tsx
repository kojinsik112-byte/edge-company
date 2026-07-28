import type { Metadata } from "next";
import Image from "next/image";
import Link from "next/link";
import { getProducts } from "@/lib/data";

export const dynamic = "force-dynamic";

export const metadata: Metadata = {
  title: "서비스 안내 — 와우클린",
  description: "하수구막힘 · 변기막힘 · 고압 배관청소 · 누수탐지까지. 와우클린이 직접 시공하는 서비스입니다.",
};

export default async function ProductsPage() {
  const products = await getProducts();

  return (
    <div className="mx-auto max-w-[1200px] px-6 py-12 md:py-16">
      <div className="mx-auto mb-10 max-w-[640px] text-center">
        <p className="kicker">Services</p>
        <h1 className="mt-3 text-[28px] font-extrabold text-ink md:text-[36px]">와우클린 서비스 안내</h1>
        <p className="mt-3 text-[14.5px] text-muted">하수구막힘 · 변기막힘 · 고압 배관청소 · 누수탐지까지. 직접 시공하는 서비스를 자세히 확인하세요.</p>
      </div>

      {products.length === 0 ? (
        <p className="py-20 text-center text-muted">등록된 제품이 곧 추가됩니다.</p>
      ) : (
        <div className="grid grid-cols-2 gap-5 md:grid-cols-4">
          {products.map((p) => (
            <Link key={p.id} href={`/products/${p.id}`} className="group overflow-hidden rounded-2xl border border-line bg-surface shadow-[0_10px_30px_-20px_rgba(15,35,66,0.2)] transition hover:-translate-y-1 hover:shadow-[0_22px_45px_-24px_rgba(15,35,66,0.25)]">
              <div className="relative aspect-[4/3] overflow-hidden bg-bg">
                {p.image && <Image src={p.image} alt={p.name} fill sizes="(max-width:768px) 50vw, 280px" className="object-cover transition duration-500 group-hover:scale-[1.04]" />}
              </div>
              <div className="p-5">
                {p.category && <span className="text-[12px] font-semibold text-gold-d">{p.category}</span>}
                <h3 className="mt-1 text-[16px] font-bold text-ink">{p.name}</h3>
                {p.body && <p className="mt-2 line-clamp-2 text-[13px] leading-relaxed text-muted">{p.body}</p>}
              </div>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}

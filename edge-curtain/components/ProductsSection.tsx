import Image from "next/image";
import ScrollRow from "@/components/ScrollRow";
import type { ProductRow } from "@/lib/types";

const DEMO: { name: string; category: string; body: string; image: string }[] = [
  { name: "암막 커튼", category: "커튼", body: "빛을 확실히 차단하는 암막 커튼. 침실·서재 숙면에 좋습니다.", image: "/img/curtain.webp" },
  { name: "콤비 블라인드", category: "블라인드", body: "채광을 단계별로 조절하는 콤비(스크린) 블라인드. 깔끔한 라인.", image: "/img/indirect.webp" },
  { name: "전동 커튼", category: "전동커튼", body: "리모컨·앱으로 여닫는 전동 커튼. 큰 창·높은 창도 편리하게.", image: "/img/sofa.webp" },
];

export default function ProductsSection({ products }: { products: ProductRow[] }) {
  const showDemo = products.length === 0;
  const items = showDemo ? DEMO : products;
  return (
    <section className="bg-surface py-16 md:py-24">
      <div className="reveal mx-auto mb-10 max-w-[640px] px-6 text-center">
        <p className="kicker">Products</p>
        <h2 className="mt-3 text-[26px] font-extrabold text-ink md:text-[32px]">엣지리브커튼 제품 소개</h2>
        <p className="mt-3 text-[14.5px] text-muted">커튼 · 블라인드 · 전동커튼까지. 옆으로 넘기면 더 많은 제품을 볼 수 있어요.</p>
      </div>
      {/* 적으면 가운데 정렬, 많으면 옆으로 스크롤 (화살표·페이드 자동) */}
      <ScrollRow fade="#ffffff">
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
      </ScrollRow>
    </section>
  );
}

import type { Metadata } from "next";
import Image from "next/image";
import Link from "next/link";
import { notFound } from "next/navigation";
import { getProductById, getProducts } from "@/lib/data";
import { getSettings } from "@/lib/settings";
import { FALLBACK_IMAGES } from "@/lib/types";

type Props = { params: Promise<{ id: string }> };

export const dynamic = "force-dynamic";

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { id } = await params;
  const p = await getProductById(id);
  if (!p) return { title: "제품을 찾을 수 없습니다" };
  return {
    title: `${p.name} — 엣지컴퍼니 ${p.category}`,
    description: (p.body || "").slice(0, 120) || `엣지컴퍼니 ${p.category} ${p.name}`,
    openGraph: { images: [p.image || FALLBACK_IMAGES.hero] },
  };
}

export default async function ProductDetail({ params }: Props) {
  const { id } = await params;
  const p = await getProductById(id);
  if (!p || !p.published) notFound();

  const cover = p.image || FALLBACK_IMAGES.hero;
  const gallery = (p.images ?? []).filter(Boolean);
  const [related, { site }] = await Promise.all([
    getProducts().then((r) => r.filter((x) => x.id !== p.id).slice(0, 4)),
    getSettings(),
  ]);

  return (
    <article className="mx-auto max-w-[960px] px-5 py-10 md:py-14">
      <nav className="text-[12.5px] text-muted">
        <Link href="/products" className="hover:text-navy">제품 소개</Link>
        <span className="mx-1.5">/</span>
        <span>{p.category || p.name}</span>
      </nav>

      <div className="mt-4 grid gap-8 md:grid-cols-2">
        <div className="relative aspect-[4/3] overflow-hidden rounded-2xl bg-line">
          <Image src={cover} alt={p.name} fill priority sizes="(max-width:768px) 100vw, 480px" className="object-cover" />
        </div>
        <div className="flex flex-col justify-center">
          {p.category && <span className="text-[13px] font-semibold text-gold-d">{p.category}</span>}
          <h1 className="mt-2 text-[26px] font-display font-extrabold leading-snug text-ink md:text-[34px]">{p.name}</h1>
          {p.body && <p className="mt-4 whitespace-pre-wrap text-[15px] leading-relaxed text-muted">{p.body}</p>}
          <div className="mt-7 flex gap-3">
            <a href={`tel:${site.phone.replace(/-/g, "")}`} className="rounded-lg bg-ink px-6 py-3.5 text-[15px] font-bold text-white transition hover:bg-[#111827]">전화 상담</a>
            <Link href="/contact" className="rounded-lg border border-gold bg-surface px-6 py-3.5 text-[15px] font-bold text-ink transition hover:bg-bg">쇼룸 예약</Link>
          </div>
        </div>
      </div>

      {gallery.length > 0 && (
        <div className="mt-10 grid gap-3 sm:grid-cols-2">
          {gallery.map((src, i) => (
            <div key={i} className="relative aspect-[4/3] overflow-hidden rounded-xl bg-line">
              <Image src={src} alt={`${p.name} 상세 사진 ${i + 1}`} fill sizes="(max-width:768px) 100vw, 460px" className="object-cover" />
            </div>
          ))}
        </div>
      )}

      {related.length > 0 && (
        <section className="mt-14">
          <h2 className="mb-5 text-lg font-bold text-ink">다른 제품</h2>
          <div className="grid grid-cols-2 gap-4 md:grid-cols-4">
            {related.map((r) => (
              <Link key={r.id} href={`/products/${r.id}`} className="group overflow-hidden rounded-2xl border border-line bg-surface transition hover:-translate-y-1 hover:shadow-[0_22px_45px_-24px_rgba(15,35,66,0.25)]">
                <div className="relative aspect-[4/3] overflow-hidden bg-bg">
                  {r.image && <Image src={r.image} alt={r.name} fill sizes="(max-width:768px) 50vw, 240px" className="object-cover transition duration-500 group-hover:scale-[1.04]" />}
                </div>
                <div className="p-4">
                  {r.category && <span className="text-[11.5px] font-semibold text-gold-d">{r.category}</span>}
                  <h3 className="mt-0.5 line-clamp-1 text-[14px] font-bold text-ink">{r.name}</h3>
                </div>
              </Link>
            ))}
          </div>
        </section>
      )}
    </article>
  );
}

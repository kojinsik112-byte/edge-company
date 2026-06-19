import type { Metadata } from "next";
import Image from "next/image";
import Link from "next/link";
import { notFound } from "next/navigation";
import { getCaseBySlug, getCases } from "@/lib/data";
import { autoSeoTitle, autoSeoDescription, abs } from "@/lib/seo";
import { REGION_SLUG, CATEGORY_SLUG } from "@/lib/constants";
import { getSettings } from "@/lib/settings";
import { FALLBACK_IMAGES } from "@/lib/types";
import CaseCard from "@/components/CaseCard";

type Props = { params: Promise<{ slug: string }> };

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { slug } = await params;
  const c = await getCaseBySlug(slug);
  if (!c) return { title: "시공사례를 찾을 수 없습니다" };
  const title = c.seo_title || autoSeoTitle(c);
  const description = c.seo_description || autoSeoDescription(c);
  const image = c.cover || FALLBACK_IMAGES.hero;
  return {
    title,
    description,
    alternates: { canonical: `/cases/${c.slug}` },
    openGraph: {
      type: "article",
      title,
      description,
      images: [abs(image)],
    },
  };
}

export default async function CaseDetail({ params }: Props) {
  const { slug } = await params;
  const c = await getCaseBySlug(slug);
  if (!c) notFound();

  const cover = c.cover || FALLBACK_IMAGES.hero;
  const [related, { site }] = await Promise.all([
    getCases({ region: c.region, limit: 4 }).then((r) => r.filter((x) => x.id !== c.id).slice(0, 3)),
    getSettings(),
  ]);

  const jsonLd = {
    "@context": "https://schema.org",
    "@type": "Article",
    headline: c.title,
    image: [abs(cover)],
    datePublished: c.created_at,
    dateModified: c.updated_at || c.created_at,
    author: { "@type": "Organization", name: "엣지리브커튼" },
    publisher: { "@type": "Organization", name: "엣지리브커튼" },
    articleSection: `${c.region} ${c.category}`,
    description: c.seo_description || autoSeoDescription(c),
  };

  return (
    <article className="mx-auto max-w-[860px] px-5 py-10 md:py-14">
      <script type="application/ld+json" dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd) }} />

      <nav className="text-[12.5px] text-muted">
        <Link href="/cases" className="hover:text-navy">시공사례</Link>
        <span className="mx-1.5">/</span>
        <Link href={`/area/${REGION_SLUG[c.region]}-${CATEGORY_SLUG[c.category]}`} className="hover:text-navy">
          {c.region} {c.category}
        </Link>
      </nav>

      <div className="mt-3 flex flex-wrap items-center gap-2">
        <span className="rounded-full bg-navy px-3 py-1 text-[11.5px] font-semibold text-white">{c.region}</span>
        <span className="rounded-full bg-gold/20 px-3 py-1 text-[11.5px] font-semibold text-gold-d">{c.category}</span>
      </div>
      <h1 className="mt-3 text-2xl font-bold leading-snug text-ink md:text-[30px]">{c.title}</h1>
      {c.apartment && <p className="mt-2 text-[14px] text-muted">{c.region} · {c.apartment}</p>}

      <div className="relative mt-6 aspect-[4/3] overflow-hidden rounded-2xl bg-line md:aspect-[16/10]">
        <Image src={cover} alt={`${c.apartment} ${c.category} 시공 대표 이미지`} fill priority sizes="(max-width:860px) 100vw, 860px" className="object-cover" />
      </div>

      {c.body && <div className="prose mt-8">{c.body}</div>}

      {c.images?.length > 0 && (
        <div className="mt-8 grid gap-3 sm:grid-cols-2">
          {c.images.map((src, i) => (
            <div key={i} className="relative aspect-[4/3] overflow-hidden rounded-xl bg-line">
              <Image src={src} alt={`${c.apartment} ${c.category} 상세 사진 ${i + 1}`} fill sizes="(max-width:768px) 100vw, 420px" className="object-cover" />
            </div>
          ))}
        </div>
      )}

      {c.tags?.length > 0 && (
        <div className="mt-8 flex flex-wrap gap-2">
          {c.tags.map((t) => (
            <Link key={t} href={`/cases?q=${encodeURIComponent(t)}`} className="rounded-full border border-line px-3 py-1.5 text-[12.5px] text-muted hover:border-navy hover:text-navy">
              #{t}
            </Link>
          ))}
        </div>
      )}

      {/* 상담 CTA */}
      <div className="mt-10 rounded-2xl bg-warm px-6 py-8 text-center">
        <p className="text-[15px] font-semibold text-ink">{c.region} {c.category} 시공, 우리 집은 어떨까요?</p>
        <p className="mt-1 text-[13px] text-muted">문자·카톡으로 남기시면 바로 전화드립니다.</p>
        <a href={`tel:${site.phone.replace(/-/g, "")}`} className="mt-4 inline-block rounded-lg bg-ink px-6 py-3 text-[15px] font-semibold text-white transition hover:bg-[#161b15]">
          {site.phone} 전화 상담
        </a>
      </div>

      {related.length > 0 && (
        <section className="mt-14">
          <h2 className="mb-5 text-lg font-bold text-ink">{c.region} 다른 시공사례</h2>
          <div className="grid gap-4 sm:grid-cols-3">
            {related.map((r) => <CaseCard key={r.id} c={r} />)}
          </div>
        </section>
      )}
    </article>
  );
}

import type { Metadata } from "next";
import Image from "next/image";
import Link from "next/link";
import { REGION_SLUG, CATEGORY_SLUG } from "@/lib/constants";
import { getSettings } from "@/lib/settings";
import { getCases, getReviews, getFaqs, getProducts, getYoutube } from "@/lib/data";
import YoutubeSection from "@/components/YoutubeSection";
import ProductsSection from "@/components/ProductsSection";
import ProcessSection from "@/components/ProcessSection";
import Stars from "@/components/Stars";
import Popup from "@/components/Popup";
import SnsSection from "@/components/SnsSection";
import ShowroomGallery from "@/components/ShowroomGallery";
import CategoryCases from "@/components/CategoryCases";
import WhySection from "@/components/WhySection";
import { DEMO_REVIEWS } from "@/lib/demo";
import ScrollRow from "@/components/ScrollRow";

export async function generateMetadata(): Promise<Metadata> {
  const { seo } = await getSettings();
  const h = seo.home;
  if (!h?.title && !h?.description) return {};
  return {
    title: h.title || undefined,
    description: h.description || undefined,
    keywords: h.keywords ? h.keywords.split(",").map((s) => s.trim()) : undefined,
    openGraph: h.og ? { images: [h.og] } : undefined,
  };
}

export default async function Home() {
  const [settings, fanCases, indirectCases, smartCases, reviews, faqs, products, videos] = await Promise.all([
    getSettings(),
    getCases({ category: "실링팬", limit: 6 }),
    getCases({ category: "간접조명", limit: 6 }),
    getCases({ category: "스마트조명", limit: 6 }),
    getReviews(12),
    getFaqs(),
    getProducts(),
    getYoutube(),
  ]);
  const { site, hero, showroom, company } = settings;
  const tel = `tel:${site.phone.replace(/-/g, "")}`;
  const reviewList = reviews.length >= 4 ? reviews : [...reviews, ...DEMO_REVIEWS].slice(0, 8);
  const moreHref = (cat: keyof typeof CATEGORY_SLUG) => `/area/${REGION_SLUG["울산"]}-${CATEGORY_SLUG[cat]}`;

  return (
    <>
      <Popup />

      {/* ===== HERO (이미지 배너 — PC/모바일 분리, 관리자에서 교체) ===== */}
      <section className="relative h-[calc(100svh-72px)] min-h-[560px] overflow-hidden bg-warm">
        {/* PC(가로) */}
        <Image src={hero.image} alt={`${hero.subline} — 엣지컴퍼니`} fill priority sizes="100vw" className="hidden object-cover md:block" />
        {/* 모바일(세로) — 없으면 PC 이미지 */}
        <Image src={hero.imageMobile || hero.image} alt={`${hero.subline} — 엣지컴퍼니`} fill priority sizes="100vw" className="object-cover md:hidden" />
        <h1 className="sr-only">{hero.title} · {hero.subline}</h1>
      </section>

      {/* ===== SNS 채널 (히어로 바로 아래) ===== */}
      <SnsSection site={site} />

      {/* ===== 회사소개 (Why Edge Company) ===== */}
      <WhySection image={company.image} />

      {/* ===== 제품 소개 (WHY 바로 아래) ===== */}
      <ProductsSection products={products} />

      {/* ===== 쇼룸 갤러리 ===== */}
      <ShowroomGallery showroom={showroom} />

      {/* ===== 시공 영상 (쇼룸 바로 밑, 인페이지 재생) ===== */}
      <YoutubeSection videos={videos} />

      {/* ===== 카테고리별 시공사례 (사진 중심·전면 배치) ===== */}
      <CategoryCases title="실링팬 시공사례" desc="실제 고객 시공 현장" cases={fanCases} moreHref={moreHref("실링팬")} bg="bg-bg" />
      <CategoryCases title="간접조명 시공사례" desc="빛의 분위기가 달라지는 공간" cases={indirectCases} moreHref={moreHref("간접조명")} bg="bg-surface" />
      <CategoryCases title="스마트조명 시공사례" desc="앱 하나로 완성하는 스마트 라이프" cases={smartCases} moreHref={moreHref("스마트조명")} bg="bg-bg" />

      {/* ===== 시공 절차 ===== */}
      <ProcessSection />

      {/* ===== 고객후기 ===== */}
      <section className="bg-[#f8f5f0] py-16 md:py-24">
        <div className="reveal mx-auto max-w-[1320px] px-6">
          <div className="mx-auto mb-10 max-w-[640px] text-center">
            <p className="kicker">Reviews</p>
            <h2 className="mt-3 text-[26px] font-extrabold text-ink md:text-[32px]">고객 후기</h2>
            <p className="mt-3 text-[14.5px] text-muted">실제 시공 고객님들의 이야기입니다. 옆으로 넘겨 더 많은 후기를 확인하세요.</p>
          </div>
        </div>
        <ScrollRow fade="#f8f5f0">
          <div className="mx-auto flex w-max gap-5 pb-3">
            {reviewList.map((r) => (
              <div key={r.id} className="relative w-[290px] shrink-0 overflow-hidden rounded-2xl border border-line bg-surface">
                {"demo" in r && <span className="absolute right-3 top-3 z-10 rounded-full bg-white/85 px-2.5 py-1 text-[11px] font-semibold text-ink/60 backdrop-blur-sm">예시</span>}
                {r.image && (
                  <div className="relative aspect-[16/10] bg-bg">
                    <Image src={r.image} alt={`${r.name} 후기`} fill sizes="290px" className="object-cover" />
                  </div>
                )}
                <div className="p-6">
                  <Stars n={r.rating} />
                  <p className="mt-3 text-[14.5px] leading-relaxed text-ink">“{r.content}”</p>
                  <p className="mt-4 text-[13px] font-semibold text-muted">{[r.region, r.apartment, r.name].filter(Boolean).join(" · ")}</p>
                </div>
              </div>
            ))}
          </div>
        </ScrollRow>
        <div className="mt-9 text-center">
          <Link href="/reviews" className="text-sm font-semibold text-gold-d">후기 더 보기 →</Link>
        </div>
      </section>

      {/* ===== FAQ ===== */}
      {faqs.length > 0 && (
        <section className="reveal mx-auto max-w-[1080px] px-6 py-16 md:py-24">
          <div className="mx-auto mb-12 max-w-[640px] text-center">
            <p className="kicker">FAQ</p>
            <h2 className="mt-3 text-[24px] font-bold text-ink md:text-[30px]">자주 묻는 질문</h2>
          </div>
          <div className="grid gap-x-8 md:grid-cols-2">
            {faqs.slice(0, 8).map((f) => (
              <details key={f.id} className="h-fit border-b border-line">
                <summary className="flex cursor-pointer list-none items-center justify-between gap-4 py-5 text-[16px] font-semibold text-ink">
                  {f.question}
                  <span className="text-xl font-light text-gold">+</span>
                </summary>
                <p className="prose pb-5">{f.answer}</p>
              </details>
            ))}
          </div>
          <div className="mt-6 text-center">
            <Link href="/faq" className="text-sm font-semibold text-gold-d">전체 FAQ 보기 →</Link>
          </div>
        </section>
      )}

      {/* ===== 상담 CTA (라이트) ===== */}
      <section className="bg-warm py-20 text-center md:py-28">
        <div className="reveal mx-auto max-w-[1320px] px-6">
          <p className="kicker">Contact</p>
          <h2 className="mt-4 whitespace-pre-line text-[30px] font-extrabold leading-[1.2] text-ink md:text-[48px]">실링팬 · 간접조명 시공{"\n"}지금 상담받으세요</h2>
          <a href={tel} className="mt-6 block text-[40px] font-extrabold tracking-tight text-navy md:text-[64px]">{site.phone}</a>
          <div className="mt-8 flex justify-center gap-3">
            <a href={tel} className="rounded-lg bg-ink px-7 py-4 text-[16px] font-bold text-white transition hover:bg-[#111827]">무료 상담</a>
            <Link href="/contact" className="rounded-lg border border-gold bg-surface px-7 py-4 text-[16px] font-bold text-ink transition hover:bg-bg">쇼룸 예약</Link>
          </div>
        </div>
      </section>
    </>
  );
}

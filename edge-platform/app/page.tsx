import type { Metadata } from "next";
import Image from "next/image";
import Link from "next/link";
import { REGION_SLUG, CATEGORY_SLUG } from "@/lib/constants";
import { getSettings } from "@/lib/settings";
import { getCases, getReviews, getFaqs } from "@/lib/data";
import Stars from "@/components/Stars";
import Popup from "@/components/Popup";
import SnsSection from "@/components/SnsSection";
import ShowroomGallery from "@/components/ShowroomGallery";
import CategoryCases from "@/components/CategoryCases";
import WhySection from "@/components/WhySection";

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
  const [settings, fanCases, indirectCases, smartCases, reviews, faqs] = await Promise.all([
    getSettings(),
    getCases({ category: "실링팬", limit: 6 }),
    getCases({ category: "간접조명", limit: 6 }),
    getCases({ category: "스마트조명", limit: 6 }),
    getReviews(3),
    getFaqs(),
  ]);
  const { site, hero, showroom } = settings;
  const tel = `tel:${site.phone.replace(/-/g, "")}`;
  const moreHref = (cat: keyof typeof CATEGORY_SLUG) => `/area/${REGION_SLUG["울산"]}-${CATEGORY_SLUG[cat]}`;

  return (
    <>
      <Popup />

      {/* ===== HERO ===== */}
      <section className="relative h-[calc(100svh-72px)] min-h-[680px] overflow-hidden bg-navy">
        <Image src={hero.image} alt="엣지컴퍼니 프리미엄 조명 쇼룸" fill priority sizes="100vw" className="object-cover" />
        <div className="absolute inset-0" style={{ background: "linear-gradient(90deg, rgba(8,16,32,0.72) 0%, rgba(8,16,32,0.48) 42%, rgba(8,16,32,0.18) 100%)" }} />
        <div className="relative z-10 flex h-full items-center">
          <div className="mx-auto w-full max-w-[1200px] px-6 md:px-20">
            <div className="max-w-[620px]">
              <p className="mb-[18px] text-[14px] font-semibold tracking-[0.5px] text-gold">{hero.eyebrow}</p>
              <h1 className="mb-[22px] whitespace-pre-line text-[34px] font-extrabold leading-[1.25] tracking-[-1.2px] text-white md:text-[48px]">{hero.title}</h1>
              <p className="mb-[12px] text-[17px] font-bold text-white">{hero.subline}</p>
              <p className="whitespace-pre-line text-[15px] font-normal leading-[1.8] text-white/90">{hero.lead}</p>
              <div className="mt-[30px] flex flex-wrap gap-3">
                <a href={tel} className="rounded-[8px] bg-navy px-[30px] py-4 text-[16px] font-bold text-white transition hover:bg-navy-d">무료 상담</a>
                <Link href="/contact" className="rounded-[8px] bg-gold px-[30px] py-4 text-[16px] font-bold text-ink transition hover:bg-gold-d">쇼룸 예약</Link>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* ===== 회사소개 (Why Edge Company) ===== */}
      <WhySection />

      {/* ===== SNS 채널 ===== */}
      <SnsSection site={site} />

      {/* ===== 쇼룸 갤러리 ===== */}
      <ShowroomGallery showroom={showroom} />

      {/* ===== 카테고리별 시공사례 ===== */}
      <CategoryCases title="실링팬 시공사례" desc="실제 고객 시공 현장" cases={fanCases} moreHref={moreHref("실링팬")} bg="bg-bg" />
      <CategoryCases title="간접조명 시공사례" desc="빛의 분위기가 달라지는 공간" cases={indirectCases} moreHref={moreHref("간접조명")} bg="bg-surface" />
      <CategoryCases title="스마트조명 시공사례" desc="앱 하나로 완성하는 스마트 라이프" cases={smartCases} moreHref={moreHref("스마트조명")} bg="bg-bg" />

      {/* ===== 고객후기 ===== */}
      {reviews.length > 0 && (
        <section className="bg-surface py-16 md:py-24">
          <div className="mx-auto max-w-[1200px] px-6">
            <div className="mx-auto mb-12 max-w-[640px] text-center">
              <p className="kicker">Reviews</p>
              <h2 className="mt-3 text-[24px] font-bold text-ink md:text-[30px]">고객 후기</h2>
              <p className="mt-3 text-[14.5px] text-muted">실제 시공 고객님들의 이야기입니다.</p>
            </div>
            <div className="grid gap-5 md:grid-cols-3">
              {reviews.map((r) => (
                <div key={r.id} className="overflow-hidden rounded-2xl border border-line bg-surface">
                  {r.image && (
                    <div className="relative aspect-[16/10] bg-bg">
                      <Image src={r.image} alt={`${r.name} 후기`} fill sizes="(max-width:768px) 100vw, 380px" className="object-cover" />
                    </div>
                  )}
                  <div className="p-6">
                    <Stars n={r.rating} />
                    <p className="mt-3 text-[15px] leading-relaxed text-ink">“{r.content}”</p>
                    <p className="mt-4 text-[13px] font-semibold text-muted">{r.region ? `${r.region} · ` : ""}{r.name}</p>
                  </div>
                </div>
              ))}
            </div>
            <div className="mt-10 text-center">
              <Link href="/reviews" className="text-sm font-semibold text-gold-d">후기 더 보기 →</Link>
            </div>
          </div>
        </section>
      )}

      {/* ===== FAQ ===== */}
      {faqs.length > 0 && (
        <section className="mx-auto max-w-[1080px] px-6 py-16 md:py-24">
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

      {/* ===== 상담 CTA ===== */}
      <section className="bg-navy-d py-20 text-center text-white">
        <div className="mx-auto max-w-[1200px] px-6">
          <p className="kicker text-gold">Contact</p>
          <h2 className="mt-4 whitespace-pre-line text-2xl font-bold leading-snug md:text-3xl">실링팬 · 간접조명 시공{"\n"}지금 상담받으세요</h2>
          <a href={tel} className="mt-7 block text-3xl font-extrabold tracking-tight md:text-4xl">{site.phone}</a>
          <div className="mt-7 flex justify-center gap-3">
            <a href={tel} className="rounded-lg bg-gold px-6 py-3.5 text-[15px] font-bold text-ink">무료 상담</a>
            <Link href="/contact" className="rounded-lg border border-white/30 px-6 py-3.5 text-[15px] font-semibold text-white">쇼룸 예약</Link>
          </div>
        </div>
      </section>
    </>
  );
}

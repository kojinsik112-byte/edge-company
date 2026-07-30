import type { Metadata } from "next";
import Image from "next/image";
import Link from "next/link";
import { REGION_SLUG, CATEGORY_SLUG } from "@/lib/constants";
import { getSettings } from "@/lib/settings";
import { getCases, getReviews, getFaqs, getProducts } from "@/lib/data";
import ShortsSection from "@/components/ShortsSection";
import ProductsSection from "@/components/ProductsSection";
import ProcessSection from "@/components/ProcessSection";
import Stars from "@/components/Stars";
import Popup from "@/components/Popup";
import SnsSection from "@/components/SnsSection";
import ShowroomGallery from "@/components/ShowroomGallery";
import LightSimulator from "@/components/LightSimulator";
import HeroVideo from "@/components/HeroVideo";
import CategoryCases from "@/components/CategoryCases";
import WhySection from "@/components/WhySection";
import LicenseSection from "@/components/LicenseSection";
import BranchesSection from "@/components/BranchesSection";
import PartnersSection from "@/components/PartnersSection";
import { DEMO_REVIEWS } from "@/lib/demo";
import ScrollRow from "@/components/ScrollRow";

// 관리자에서 등록/수정한 CMS 콘텐츠가 즉시 반영되도록 항상 최신 렌더
export const dynamic = "force-dynamic";

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
  const [settings, fanCases, indirectCases, etcCases, reviews, faqs, products] = await Promise.all([
    getSettings(),
    getCases({ category: "실링팬", limit: 9 }),
    getCases({ category: "간접조명", limit: 9 }),
    getCases({ category: "기타", limit: 9 }),
    getReviews(12),
    getFaqs(),
    getProducts(),
  ]);
  const { site, hero, showroom, company, process, simulator, shorts, categorySections: cs, categories: catImg, license, branches, partners } = settings;
  const tel = `tel:${site.phone.replace(/-/g, "")}`;
  const reviewList = (reviews.length >= 9 ? reviews : [...reviews, ...DEMO_REVIEWS]).slice(0, 9);
  const moreHref = (cat: keyof typeof CATEGORY_SLUG) => `/area/${REGION_SLUG["울산"]}-${CATEGORY_SLUG[cat]}`;

  return (
    <>
      <Popup />

      {/* ===== HERO (광고영상 자동재생 루프 또는 이미지 — 관리자에서 교체) ===== */}
      <section className={`relative overflow-hidden bg-warm ${hero.video ? "aspect-video" : "h-[calc(100svh-72px)] min-h-[560px]"}`}>
        {hero.video ? (
          <HeroVideo src={hero.video} poster={hero.image || undefined} />
        ) : (
          <>
            <Image src={hero.image} alt={`${hero.subline} — 엣지컴퍼니`} fill priority sizes="100vw" className="hidden object-cover md:block" />
            <Image src={hero.imageMobile || hero.image} alt={`${hero.subline} — 엣지컴퍼니`} fill priority sizes="100vw" className="object-cover md:hidden" />
          </>
        )}
        {/* 라이브 텍스트 오버레이 (관리자 입력 — 이미지에 글자 안 박아 안 잘림·선명) */}
        {(hero.overlayTitle || hero.overlaySub) && (
          <div className="absolute inset-0 flex flex-col justify-center bg-gradient-to-r from-black/80 via-black/45 to-transparent px-8 md:px-20">
            {hero.eyebrow && <p className="mb-5 text-[13px] font-medium tracking-[0.06em] opacity-85 md:text-[15px]" style={{ color: hero.overlayColor }}>{hero.eyebrow}</p>}
            {hero.overlayTitle && (
              <h1 className={`max-w-[640px] whitespace-pre-line leading-[1.22] tracking-[-0.01em] [text-shadow:0_2px_24px_rgba(0,0,0,0.35)] ${hero.overlaySerif ? "font-lux" : ""}`} style={{ color: hero.overlayColor, fontWeight: Number(hero.overlayWeight) || 600, fontSize: `clamp(28px, 7vw, ${hero.overlayTitleSize || 56}px)` }}>{hero.overlayTitle}</h1>
            )}
            <span className="mt-6 block h-px w-[180px]" style={{ backgroundColor: hero.overlayColor, opacity: 0.45 }} />
            {hero.overlaySub && <p className="mt-6 max-w-[460px] whitespace-pre-line text-[15px] font-light leading-relaxed opacity-90 md:text-[17px]" style={{ color: hero.overlayColor }}>{hero.overlaySub}</p>}
            <p className="mt-5 font-lux text-[15px] font-semibold tracking-[0.34em] opacity-75 md:text-[17px]" style={{ color: hero.overlayColor }}>EDGE COMPANY</p>
            <div className="mt-8">
              <Link href="/cases" className="inline-flex items-center gap-2 rounded-full border border-white/40 bg-white/10 px-7 py-3.5 text-[15px] font-semibold text-white backdrop-blur-sm transition hover:bg-white hover:text-ink">시공사례 보기 <span aria-hidden>→</span></Link>
            </div>
          </div>
        )}
        {!hero.overlayTitle && <h1 className="sr-only">{hero.title} · {hero.subline}</h1>}
      </section>

      {/* ===== SNS 채널 (메인 바로 아래 — 유튜브·블로그·인스타) ===== */}
      <SnsSection site={site} />

      {/* ===== 쇼룸 갤러리 ===== */}
      <ShowroomGallery showroom={showroom} />

      {/* ===== 색온도·디밍 체험 시뮬레이터 ===== */}
      {simulator.enabled && <LightSimulator image={simulator.image} title={simulator.title} subtitle={simulator.subtitle} />}

      {/* ===== 회사소개 (왜 엣지컴퍼니일까요?) ===== */}
      <WhySection company={company} />

      {/* ===== 엣지컴퍼니 전기 면허 등록증 (1열 2개) ===== */}
      <LicenseSection license={license} />

      {/* ===== 엣지컴퍼니 전국 지사 (표 + 지도) ===== */}
      <BranchesSection branches={branches} />

      {/* ===== 엣지컴퍼니 협력사 소개 (로고 3열) ===== */}
      <PartnersSection partners={partners} />

      {/* ===== 제품 소개 (한 줄 4개·무제한) ===== */}
      <ProductsSection products={products} />

      {/* ===== 숏츠 (세로 영상 — 패러디·비포애프터) ===== */}
      <ShortsSection shorts={shorts} />

      {/* ===== 카테고리별 시공사례 (사진 중심·전면 배치) ===== */}
      <CategoryCases title={cs["실링팬"]?.title ?? "실링팬 시공사례"} desc={cs["실링팬"]?.desc ?? ""} cases={fanCases} moreHref={moreHref("실링팬")} bg="bg-bg" heroImg={catImg?.["실링팬"]} />
      <CategoryCases title={cs["간접조명"]?.title ?? "간접조명 시공사례"} desc={cs["간접조명"]?.desc ?? ""} cases={indirectCases} moreHref={moreHref("간접조명")} bg="bg-surface" heroImg={catImg?.["간접조명"]} />
      <CategoryCases title={cs["기타"]?.title ?? "기타 시공사례"} desc={cs["기타"]?.desc ?? ""} cases={etcCases} moreHref={moreHref("기타")} bg="bg-bg" heroImg={catImg?.["기타"]} />

      {/* ===== 시공 절차 ===== */}
      <ProcessSection process={process} />

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
                  {r.title && <p className="mt-3 text-[16px] font-bold leading-snug text-ink">{r.title}</p>}
                  <p className={`${r.title ? "mt-1.5" : "mt-3"} text-[14.5px] leading-relaxed text-muted`}>“{r.content}”</p>
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

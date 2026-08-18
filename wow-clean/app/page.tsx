import type { Metadata } from "next";
import Image from "next/image";
import Link from "next/link";
import { REGION_SLUG, CATEGORY_SLUG } from "@/lib/constants";
import { getSettings } from "@/lib/settings";
import { getCases, getReviews, getFaqs, getProducts } from "@/lib/data";
import ShortsSection from "@/components/ShortsSection";
import ProcessSection from "@/components/ProcessSection";
import ProductsSection from "@/components/ProductsSection";
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
import { DEMO_REVIEWS, DEMO_FAQS } from "@/lib/demo";
import ScrollRow from "@/components/ScrollRow";
import EmergencyHero from "@/components/EmergencyHero";
import BeforeAfter from "@/components/BeforeAfter";
import RescueTimeline from "@/components/RescueTimeline";
import PricePrinciple from "@/components/PricePrinciple";
import LiveFeed from "@/components/LiveFeed";
import CountUpStats from "@/components/CountUpStats";

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
    getCases({ category: "하수구막힘", limit: 9 }),
    getCases({ category: "변기막힘", limit: 9 }),
    getCases({ category: "배관청소", limit: 9 }),
    getReviews(12),
    getFaqs(),
    getProducts(),
  ]);
  const { site, hero, showroom, company, process, simulator, shorts, categorySections: cs, license, branches, partners } = settings;
  const tel = `tel:${site.phone.replace(/-/g, "")}`;
  const reviewList = (reviews.length >= 9 ? reviews : [...reviews, ...DEMO_REVIEWS]).slice(0, 9);
  const faqList = faqs.length > 0 ? faqs : DEMO_FAQS;
  const moreHref = (cat: keyof typeof CATEGORY_SLUG) => `/area/${REGION_SLUG["서울"]}-${CATEGORY_SLUG[cat]}`;

  return (
    <>
      <Popup />

      {/* ===== HERO — 긴급출동형 (타이핑 헤드라인 + 실시간 티커 + 카톡 사진견적) ===== */}
      <EmergencyHero site={site} hero={hero} />

      {/* ===== 실시간 접수 현황 롤링 피드 ===== */}
      <LiveFeed />
      {hero.video && (
        <section className="relative aspect-video overflow-hidden bg-warm">
          <HeroVideo src={hero.video} poster={hero.image || undefined} />
        </section>
      )}

      {/* ===== 신뢰 스트립 (히어로 바로 아래) ===== */}
      <div className="border-b border-line bg-navy">
        <div className="mx-auto flex max-w-[1320px] flex-wrap items-center justify-center gap-x-8 gap-y-2.5 px-6 py-4">
          {["시공 전 투명 견적", "작업 후 A/S 보증", "사업자 정식 등록", "현장 사진 리포트", "가정·상가·건물 대응"].map((t) => (
            <span key={t} className="inline-flex items-center gap-2 text-[13.5px] font-semibold text-white/90">
              <svg viewBox="0 0 24 24" className="h-4 w-4 text-gold" fill="none" stroke="currentColor" strokeWidth={2.4} strokeLinecap="round" strokeLinejoin="round"><path d="M20 6 9 17l-5-5" /></svg>
              {t}
            </span>
          ))}
        </div>
      </div>

      {/* ===== Before/After 드래그 비교 ===== */}
      <BeforeAfter before={fanCases.find((c) => c.cover)?.cover ?? "/img/photo/before-drain.jpg"} after={etcCases.find((c) => c.cover)?.cover ?? "/img/photo/after-flow.jpg"} />

      {/* ===== 누적 시공 카운터 + 상승 그래프 ===== */}
      <CountUpStats />

      {/* ===== SNS 채널 (유튜브·블로그·인스타) ===== */}
      <SnsSection site={site} />

      {/* ===== 시공 현장 갤러리 ===== */}
      <ShowroomGallery showroom={showroom} />

      {/* ===== 시뮬레이터 (와우클린 기본 OFF) ===== */}
      {simulator.enabled && <LightSimulator image={simulator.image} title={simulator.title} subtitle={simulator.subtitle} />}

      {/* ===== 회사소개 (왜 와우클린일까요?) ===== */}
      <WhySection company={company} />

      {/* ===== 와우클린 사업자등록증·증빙 (1열 2개) ===== */}
      <LicenseSection license={license} />

      {/* ===== 와우클린 전국 출동 지역 (표 + 지도) ===== */}
      <BranchesSection branches={branches} />

      {/* ===== 와우클린 협력사 소개 (로고 3열) ===== */}
      <PartnersSection partners={partners} />

      {/* ===== 제품 소개 (한 줄 4개·무제한) ===== */}
      <ProductsSection products={products} />

      {/* ===== 숏츠 (세로 영상 — 패러디·비포애프터) ===== */}
      <ShortsSection shorts={shorts} />

      {/* ===== 카테고리별 시공사례 (사진 중심·전면 배치) ===== */}
      <CategoryCases title={cs["하수구막힘"]?.title ?? "하수구막힘 시공사례"} desc={cs["하수구막힘"]?.desc ?? ""} cases={fanCases} moreHref={moreHref("하수구막힘")} bg="bg-bg" />
      <CategoryCases title={cs["변기막힘"]?.title ?? "변기막힘 시공사례"} desc={cs["변기막힘"]?.desc ?? ""} cases={indirectCases} moreHref={moreHref("변기막힘")} bg="bg-surface" />
      <CategoryCases title={cs["배관청소"]?.title ?? "배관청소 시공사례"} desc={cs["배관청소"]?.desc ?? ""} cases={etcCases} moreHref={moreHref("배관청소")} bg="bg-bg" />

      {/* ===== 시공 절차 — 관리자에 등록한 단계(사진 포함)가 있으면 그걸 우선 노출 ===== */}
      {process.steps?.length ? <ProcessSection process={process} /> : null}

      {/* ===== 시공 절차 — 시간 타임라인 ===== */}
      <RescueTimeline />

      {/* ===== 투명 요금 원칙 ===== */}
      <PricePrinciple site={site} />

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

      {/* ===== FAQ (DB 비어있으면 기본 8문항 폴백) ===== */}
      {faqList.length > 0 && (
        <section className="reveal mx-auto max-w-[1080px] px-6 py-16 md:py-24">
          <div className="mx-auto mb-12 max-w-[640px] text-center">
            <p className="kicker">FAQ</p>
            <h2 className="mt-3 text-[24px] font-bold text-ink md:text-[30px]">자주 묻는 질문</h2>
          </div>
          <div className="grid gap-x-8 md:grid-cols-2">
            {faqList.slice(0, 8).map((f) => (
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
          <h2 className="mt-4 whitespace-pre-line text-[30px] font-extrabold leading-[1.2] text-ink md:text-[48px]">하수구 · 변기 막힘{"\n"}지금 바로 접수하세요</h2>
          <a href={tel} className="mt-6 block text-[40px] font-extrabold tracking-tight text-navy md:text-[64px]">{site.phone}</a>
          <div className="mt-8 flex justify-center gap-3">
            <a href={tel} className="rounded-lg bg-ink px-7 py-4 text-[16px] font-bold text-white transition hover:bg-[#111827]">무료 상담</a>
            <Link href="/contact" className="rounded-lg border border-gold bg-surface px-7 py-4 text-[16px] font-bold text-ink transition hover:bg-bg">온라인 접수</Link>
          </div>
        </div>
      </section>
    </>
  );
}

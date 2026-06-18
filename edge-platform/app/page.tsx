import type { Metadata } from "next";
import Image from "next/image";
import Link from "next/link";
import { CATEGORIES, CATEGORY_DESC, CATEGORY_SLUG } from "@/lib/constants";
import { getSettings } from "@/lib/settings";
import { getCases, getReviews, getFaqs, getYoutube } from "@/lib/data";
import CaseCard from "@/components/CaseCard";
import Stars from "@/components/Stars";
import Popup from "@/components/Popup";

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
  const [settings, cases, reviews, faqs, videos] = await Promise.all([
    getSettings(),
    getCases({ limit: 6 }),
    getReviews(4),
    getFaqs(),
    getYoutube(),
  ]);
  const { site, hero, categories } = settings;
  const tel = `tel:${site.phone.replace(/-/g, "")}`;

  return (
    <>
      <Popup />

      {/* ===== HERO ===== */}
      <section className="relative h-[calc(100svh-72px)] min-h-[680px] overflow-hidden bg-navy">
        <Image src={hero.image} alt="엣지컴퍼니 프리미엄 조명 쇼룸" fill priority sizes="100vw" className="object-cover" />
        <div
          className="absolute inset-0"
          style={{
            background:
              "linear-gradient(90deg, rgba(8,16,32,0.72) 0%, rgba(8,16,32,0.48) 42%, rgba(8,16,32,0.18) 100%)",
          }}
        />
        <div className="relative z-10 flex h-full items-center">
          <div className="mx-auto w-full max-w-[1200px] px-6 md:px-20">
            <div className="max-w-[620px]">
              <p className="mb-[18px] text-[14px] font-semibold tracking-[0.5px] text-gold">{hero.eyebrow}</p>
              <h1 className="mb-[22px] whitespace-pre-line text-[34px] font-extrabold leading-[1.25] tracking-[-1.2px] text-white md:text-[48px]">
                {hero.title}
              </h1>
              <p className="mb-[12px] text-[17px] font-bold text-white">{hero.subline}</p>
              <p className="whitespace-pre-line text-[15px] font-normal leading-[1.8] text-white/90">{hero.lead}</p>
              <div className="mt-[30px] flex flex-wrap gap-3">
                <a href={tel} className="rounded-[8px] bg-navy px-[30px] py-4 text-[16px] font-bold text-white transition hover:bg-navy-d">
                  무료 상담
                </a>
                <Link href="/contact" className="rounded-[8px] bg-gold px-[30px] py-4 text-[16px] font-bold text-ink transition hover:bg-gold-d">
                  쇼룸 예약
                </Link>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* ===== TRUST STRIP ===== */}
      <div className="border-b border-line bg-surface">
        <div className="mx-auto grid max-w-[1200px] grid-cols-2 md:grid-cols-4">
          {[
            ["울산-00821", "전기공사업 등록 면허"],
            ["ISO 3종", "9001 · 14001 · 45001"],
            ["22개 지사", "전국 네트워크"],
            ["2022~", "법인 직영 · 기술사 보유"],
          ].map(([a, b], i) => (
            <div key={i} className="border-line px-4 py-7 text-center [&:not(:first-child)]:border-l [&:nth-child(n+3)]:border-t md:[&:nth-child(n+3)]:border-t-0">
              <div className="text-lg font-extrabold text-ink">{a}</div>
              <div className="mt-1.5 text-[12px] text-muted">{b}</div>
            </div>
          ))}
        </div>
      </div>

      {/* ===== COLLECTIONS ===== */}
      <section className="mx-auto max-w-[1200px] px-6 py-16 md:py-24">
        <Head2 kicker="Collections" title="실링팬 · 간접조명 · 스마트조명 전문" desc="울산·부산·포항·경주, 제품 하나가 아니라 공간 전체의 무드를 설계합니다." />
        <div className="grid gap-5 sm:grid-cols-2 lg:grid-cols-3">
          {CATEGORIES.map((cat) => (
            <Link key={cat} href={`/area/ulsan-${CATEGORY_SLUG[cat]}`} className="group overflow-hidden rounded-2xl bg-surface shadow-[0_10px_30px_-18px_rgba(11,31,58,0.25)] transition hover:shadow-[0_22px_50px_-24px_rgba(11,31,58,0.35)]">
              <div className="relative aspect-[4/3] overflow-hidden">
                <Image src={categories[cat] || "/img/fan.webp"} alt={`${cat} 시공`} fill sizes="(max-width:768px) 100vw, 360px" className="object-cover transition duration-500 group-hover:scale-[1.04]" />
              </div>
              <div className="p-6">
                <h3 className="text-xl font-bold text-ink">{cat}</h3>
                <p className="mt-2 text-[13.5px] leading-relaxed text-muted">{CATEGORY_DESC[cat]}</p>
                <span className="mt-4 inline-block text-[13px] font-semibold text-gold-d">자세히 보기 →</span>
              </div>
            </Link>
          ))}
        </div>
      </section>

      {/* ===== FEATURED CASES ===== */}
      <section className="bg-surface py-16 md:py-24">
        <div className="mx-auto max-w-[1200px] px-6">
          <Head2 kicker="Portfolio" title="울산·부산·포항·경주 시공사례" desc="실제 시공 현장을 그대로 담았습니다." />
          {cases.length > 0 ? (
            <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
              {cases.map((c) => <CaseCard key={c.id} c={c} />)}
            </div>
          ) : (
            <Empty text="시공사례가 곧 등록됩니다. 관리자에서 사례를 추가하면 이곳에 자동으로 노출됩니다." />
          )}
          <div className="mt-10 text-center">
            <Link href="/cases" className="inline-block rounded-lg border border-line px-6 py-3 text-sm font-semibold text-ink transition hover:border-navy">
              시공사례 전체 보기
            </Link>
          </div>
        </div>
      </section>

      {/* ===== REVIEWS ===== */}
      {reviews.length > 0 && (
        <section className="mx-auto max-w-[1200px] px-6 py-16 md:py-24">
          <Head2 kicker="Reviews" title="고객 후기" desc="실제 시공 고객님들의 이야기입니다." />
          <div className="grid gap-4 sm:grid-cols-2">
            {reviews.map((r) => (
              <div key={r.id} className="rounded-2xl border border-line bg-surface p-6">
                <Stars n={r.rating} />
                <p className="mt-3 text-[15px] leading-relaxed text-ink">“{r.content}”</p>
                <p className="mt-4 text-[13px] font-semibold text-muted">
                  {r.region ? `${r.region} · ` : ""}{r.name}
                </p>
              </div>
            ))}
          </div>
          <div className="mt-8 text-center">
            <Link href="/reviews" className="text-sm font-semibold text-gold-d">후기 더 보기 →</Link>
          </div>
        </section>
      )}

      {/* ===== YOUTUBE ===== */}
      {videos.length > 0 && (
        <section className="bg-surface py-16 md:py-24">
          <div className="mx-auto max-w-[1200px] px-6">
            <Head2 kicker="Youtube" title="시공 영상" desc="실링팬·간접조명 시공 과정을 영상으로 확인하세요." />
            <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
              {videos.slice(0, 6).map((v) => (
                <a key={v.id} href={`https://youtu.be/${v.video_id}`} target="_blank" rel="noopener noreferrer" className="group overflow-hidden rounded-2xl bg-bg shadow-[0_10px_30px_-18px_rgba(11,31,58,0.25)]">
                  <div className="relative aspect-video overflow-hidden bg-line">
                    {/* eslint-disable-next-line @next/next/no-img-element */}
                    <img src={`https://i.ytimg.com/vi/${v.video_id}/hqdefault.jpg`} alt={v.title} className="h-full w-full object-cover transition duration-500 group-hover:scale-105" />
                    <span className="absolute left-1/2 top-1/2 flex h-12 w-12 -translate-x-1/2 -translate-y-1/2 items-center justify-center rounded-full bg-white/90">
                      <svg viewBox="0 0 24 24" className="ml-0.5 h-5 w-5 fill-navy"><path d="M7 4.5v15l13-7.5z" /></svg>
                    </span>
                  </div>
                  <div className="p-4">
                    <h3 className="line-clamp-2 text-[14px] font-semibold text-ink">{v.title}</h3>
                    {v.views && <p className="mt-1 text-[12px] text-muted">조회수 {v.views}</p>}
                  </div>
                </a>
              ))}
            </div>
          </div>
        </section>
      )}

      {/* ===== FAQ ===== */}
      {faqs.length > 0 && (
        <section className="mx-auto max-w-[760px] px-6 py-16 md:py-24">
          <Head2 kicker="FAQ" title="자주 묻는 질문" />
          <div>
            {faqs.slice(0, 4).map((f) => (
              <details key={f.id} className="border-b border-line">
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

      {/* ===== CONTACT CTA ===== */}
      <section className="relative overflow-hidden bg-navy-d py-20 text-center text-white">
        <div className="relative z-10 mx-auto max-w-[1200px] px-6">
          <p className="kicker text-gold">Contact</p>
          <h2 className="mt-4 text-2xl font-bold md:text-3xl">실링팬 · 간접조명 시공, 지금 상담받으세요</h2>
          <p className="mt-3 text-[14.5px] text-white/60">울산·부산·포항·경주 어디든 방문 상담. 문자·카톡으로 남기시면 바로 전화드립니다.</p>
          <a href={tel} className="mt-7 block text-3xl font-bold tracking-tight md:text-4xl">{site.phone}</a>
          <div className="mt-7 flex justify-center gap-3">
            <a href={tel} className="rounded-lg bg-gold px-6 py-3.5 text-[15px] font-bold text-ink">무료 상담</a>
            <Link href="/contact" className="rounded-lg border border-white/30 px-6 py-3.5 text-[15px] font-semibold text-white">쇼룸 예약</Link>
          </div>
        </div>
      </section>
    </>
  );
}

function Head2({ kicker, title, desc }: { kicker: string; title: string; desc?: string }) {
  return (
    <div className="mx-auto mb-12 max-w-[640px] text-center">
      <p className="kicker">{kicker}</p>
      <h2 className="mt-3 text-[22px] font-bold leading-snug text-ink md:text-[28px]">{title}</h2>
      {desc && <p className="mt-3 text-[14.5px] leading-relaxed text-muted">{desc}</p>}
    </div>
  );
}

function Empty({ text }: { text: string }) {
  return <div className="rounded-2xl border border-dashed border-line bg-bg py-16 text-center text-[13.5px] text-muted">{text}</div>;
}

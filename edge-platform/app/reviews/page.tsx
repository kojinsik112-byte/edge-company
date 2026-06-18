import type { Metadata } from "next";
import Image from "next/image";
import { getReviews } from "@/lib/data";
import Stars from "@/components/Stars";

export const metadata: Metadata = {
  title: "고객 후기 — 울산·부산·포항·경주 실링팬·간접조명",
  description: "엣지컴퍼니 실링팬·간접조명·스마트조명 시공 고객 후기. 실제 시공 만족도를 확인하세요.",
  alternates: { canonical: "/reviews" },
};

export default async function ReviewsPage() {
  const reviews = await getReviews();
  return (
    <div className="mx-auto max-w-[900px] px-5 py-12 md:py-16">
      <p className="kicker">Reviews</p>
      <h1 className="mt-3 text-2xl font-bold text-ink md:text-3xl">고객 후기</h1>
      <p className="mt-3 text-[14.5px] text-muted">실제 시공 고객님들의 이야기입니다.</p>

      {reviews.length > 0 ? (
        <div className="mt-8 grid gap-4 sm:grid-cols-2">
          {reviews.map((r) => (
            <div key={r.id} className="overflow-hidden rounded-2xl border border-line bg-surface">
              {r.image && (
                <div className="relative aspect-[16/10] bg-line">
                  <Image src={r.image} alt={`${r.name} 후기 사진`} fill sizes="(max-width:768px) 100vw, 440px" className="object-cover" />
                </div>
              )}
              <div className="p-6">
                <Stars n={r.rating} />
                <p className="mt-3 text-[15px] leading-relaxed text-ink">“{r.content}”</p>
                <p className="mt-4 text-[13px] font-semibold text-muted">
                  {r.region ? `${r.region} · ` : ""}{r.name}
                </p>
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="mt-10 rounded-2xl border border-dashed border-line bg-bg py-20 text-center text-[14px] text-muted">
          등록된 후기가 아직 없습니다.
        </div>
      )}
    </div>
  );
}

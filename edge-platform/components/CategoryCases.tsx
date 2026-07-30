import Image from "next/image";
import Link from "next/link";
import CaseCard from "@/components/CaseCard";
import { demoTiles } from "@/lib/demo";
import type { CaseRow } from "@/lib/types";

export default function CategoryCases({
  title,
  desc,
  cases,
  moreHref,
  bg = "bg-bg",
  heroImgs = [],
}: {
  title: string;
  desc: string;
  cases: CaseRow[];
  moreHref: string;
  bg?: string;
  heroImgs?: string[]; // 관리자 '카테고리 대표 이미지'(최대 6장). 등록 사례가 없을 때 이 사진들을 대표로 보여준다.
}) {
  const showDemo = cases.length === 0;
  const covers = heroImgs.filter(Boolean).slice(0, 10);
  return (
    <section className={`${bg} py-16 md:py-24`}>
      <div className="reveal mx-auto max-w-[1320px] px-6">
        <div className="mb-10 flex items-end justify-between gap-4">
          <div>
            <h2 className="text-[24px] font-extrabold leading-snug text-ink md:text-[32px]">{title}</h2>
            <p className="mt-2 text-[14.5px] text-muted">{desc}</p>
          </div>
          <Link href={moreHref} className="hidden shrink-0 text-[14px] font-semibold text-gold-d hover:text-gold sm:inline">
            더 많은 시공사례 →
          </Link>
        </div>

        {showDemo && covers.length > 0 ? (
          // 등록된 시공사례가 없으면 관리자가 올린 '카테고리 대표 이미지'들을 한 줄에 2개씩(최대 6칸) 노출.
          <div className="grid grid-cols-2 gap-5 md:gap-6">
            {covers.map((src, i) => (
              <div key={i} className="group relative aspect-[4/3] overflow-hidden rounded-2xl bg-surface shadow-[0_10px_30px_-18px_rgba(15,35,66,0.2)]">
                <Image src={src} alt={`${title} ${i + 1}`} fill sizes="(max-width:768px) 50vw, 640px" className="object-cover transition duration-500 group-hover:scale-[1.03]" />
              </div>
            ))}
          </div>
        ) : (
          <div className="grid grid-cols-2 gap-5 md:gap-6">
            {showDemo
              ? demoTiles(9).map((t, i) => (
                  <div key={i} className="group relative aspect-[4/3] overflow-hidden rounded-2xl bg-surface shadow-[0_10px_30px_-18px_rgba(15,35,66,0.2)]">
                    <Image src={t.img} alt={`${title} 예시 ${i + 1}`} fill sizes="(max-width:768px) 50vw, 400px" className="object-cover transition duration-500 group-hover:scale-[1.03]" />
                    <span className="absolute left-3 top-3 rounded-full bg-white/85 px-2.5 py-1 text-[11px] font-semibold text-ink/70 backdrop-blur-sm">예시</span>
                  </div>
                ))
              : cases.map((c) => <CaseCard key={c.id} c={c} />)}
          </div>
        )}

        <div className="mt-9 text-center">
          <Link href={moreHref} className="inline-block rounded-lg border border-line bg-surface px-7 py-3.5 text-[15px] font-semibold text-ink transition hover:border-gold">
            더 많은 시공사례 보기
          </Link>
        </div>
      </div>
    </section>
  );
}

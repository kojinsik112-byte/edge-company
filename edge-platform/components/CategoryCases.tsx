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
  heroImg,
}: {
  title: string;
  desc: string;
  cases: CaseRow[];
  moreHref: string;
  bg?: string;
  heroImg?: string; // 관리자 '카테고리 대표 이미지'. 등록 사례가 없을 때 이 사진을 대표로 보여준다.
}) {
  const showDemo = cases.length === 0;
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

        {showDemo && heroImg ? (
          // 등록된 시공사례가 없으면 관리자가 올린 '카테고리 대표 이미지' 1장을 대표로 노출.
          <div className="group relative aspect-[16/9] w-full overflow-hidden rounded-2xl bg-surface shadow-[0_10px_30px_-18px_rgba(15,35,66,0.2)]">
            <Image src={heroImg} alt={title} fill sizes="(max-width:1320px) 100vw, 1320px" priority className="object-cover transition duration-500 group-hover:scale-[1.02]" />
          </div>
        ) : (
          <div className="grid grid-cols-2 gap-4 md:grid-cols-3 md:gap-6">
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

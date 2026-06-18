import Link from "next/link";
import CaseCard from "@/components/CaseCard";
import type { CaseRow } from "@/lib/types";

export default function CategoryCases({
  title,
  desc,
  cases,
  moreHref,
  bg = "bg-bg",
}: {
  title: string;
  desc: string;
  cases: CaseRow[];
  moreHref: string;
  bg?: string;
}) {
  return (
    <section className={`${bg} py-16 md:py-24`}>
      <div className="mx-auto max-w-[1240px] px-6">
        <div className="mb-10 flex items-end justify-between gap-4">
          <div>
            <h2 className="text-[24px] font-bold leading-snug text-ink md:text-[30px]">{title}</h2>
            <p className="mt-2 text-[14.5px] text-muted">{desc}</p>
          </div>
          <Link href={moreHref} className="hidden shrink-0 text-[14px] font-semibold text-navy hover:text-gold sm:inline">
            더 많은 시공사례 →
          </Link>
        </div>

        {cases.length > 0 ? (
          <div className="grid grid-cols-2 gap-4 md:grid-cols-3 md:gap-6">
            {cases.map((c) => <CaseCard key={c.id} c={c} />)}
          </div>
        ) : (
          <div className="rounded-2xl border border-dashed border-line bg-surface py-16 text-center text-[14px] text-muted">
            시공사례가 곧 등록됩니다.
          </div>
        )}

        <div className="mt-9 text-center">
          <Link href={moreHref} className="inline-block rounded-lg border border-line bg-surface px-7 py-3.5 text-[15px] font-semibold text-ink transition hover:border-navy">
            더 많은 시공사례 보기
          </Link>
        </div>
      </div>
    </section>
  );
}

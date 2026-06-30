import Image from "next/image";
import Link from "next/link";
import type { CaseRow } from "@/lib/types";
import { FALLBACK_IMAGES } from "@/lib/types";

const FALLBACK_BY_CATEGORY: Record<string, string> = {
  실링팬: FALLBACK_IMAGES.fan,
  간접조명: FALLBACK_IMAGES.indirect,
  기타: FALLBACK_IMAGES.curtain,
};

export default function CaseCard({ c }: { c: CaseRow }) {
  const src = c.cover || FALLBACK_BY_CATEGORY[c.category] || FALLBACK_IMAGES.hero;
  return (
    <Link
      href={`/cases/${c.slug}`}
      className="group block overflow-hidden rounded-2xl bg-surface shadow-[0_10px_30px_-18px_rgba(16,37,66,0.25)] transition hover:shadow-[0_22px_50px_-24px_rgba(16,37,66,0.35)]"
    >
      <div className="relative aspect-[4/3] overflow-hidden bg-line">
        <Image
          src={src}
          alt={`${c.region} ${c.apartment} ${c.category} 시공`}
          fill
          sizes="(max-width:768px) 50vw, 360px"
          className="object-cover transition duration-500 group-hover:scale-[1.04]"
        />
        <span className="absolute left-3 top-3 rounded-full bg-navy/85 px-3 py-1.5 text-[11.5px] font-semibold text-white backdrop-blur-sm">
          <span className="text-gold">{c.region}</span> · {c.category}
        </span>
      </div>
      <div className="p-4">
        <h3 className="line-clamp-1 text-[15px] font-bold text-ink">
          {c.apartment || c.title}
        </h3>
        <p className="mt-1 line-clamp-1 text-[12.5px] text-muted">{c.title}</p>
      </div>
    </Link>
  );
}

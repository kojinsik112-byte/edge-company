import Link from "next/link";
import Image from "next/image";
import { requireAdmin } from "@/lib/admin";
import { getCases } from "@/lib/data";
import { CATEGORIES } from "@/lib/constants";
import { DeleteCaseButton } from "@/components/admin/AdminButtons";

export const dynamic = "force-dynamic";

export default async function AdminCases() {
  await requireAdmin();
  const cases = await getCases({ includeUnpublished: true, limit: 1000 });
  const countBy = (c: string) => cases.filter((x) => x.category === c).length;

  return (
    <div className="mx-auto max-w-[1000px] px-5 py-8">
      <Link href="/admin" className="text-[13px] text-muted hover:text-navy">← 대시보드</Link>
      <h1 className="mb-4 mt-3 text-xl font-extrabold text-ink">시공사례 <span className="text-[14px] font-medium text-muted">총 {cases.length}건</span></h1>

      {/* 카테고리별 등록 — 셋 다 여기서 올립니다(사진·제목·아파트명·내용·태그) */}
      <div className="mb-7 grid gap-3 sm:grid-cols-3">
        {CATEGORIES.map((c) => (
          <Link
            key={c}
            href={`/admin/cases/new?category=${encodeURIComponent(c)}`}
            className="flex items-center justify-between rounded-xl border border-line bg-surface px-4 py-3.5 transition hover:border-navy hover:shadow-[0_14px_30px_-20px_rgba(11,31,58,0.4)]"
          >
            <span className="text-[14px] font-bold text-ink">+ {c} 사례 등록</span>
            <span className="text-[12px] font-semibold text-muted">{countBy(c)}건</span>
          </Link>
        ))}
      </div>

      {cases.length === 0 ? (
        <div className="rounded-2xl border border-dashed border-line bg-surface py-20 text-center text-[14px] text-muted">
          등록된 시공사례가 없습니다. <Link href="/admin/cases/new" className="font-semibold text-navy">첫 사례를 등록</Link>해 보세요.
        </div>
      ) : (
        <div className="overflow-hidden rounded-2xl border border-line bg-surface">
          {cases.map((c) => (
            <div key={c.id} className="flex items-center gap-4 border-b border-line p-3 last:border-b-0">
              <div className="relative h-14 w-20 shrink-0 overflow-hidden rounded-lg bg-line">
                {c.cover && <Image src={c.cover} alt="" fill sizes="80px" className="object-cover" />}
              </div>
              <div className="min-w-0 flex-1">
                <p className="truncate text-[14px] font-semibold text-ink">{c.title}</p>
                <p className="mt-0.5 text-[12px] text-muted">
                  {c.region} · {c.category}{c.apartment && ` · ${c.apartment}`}
                  {!c.published && <span className="ml-2 rounded bg-gold/20 px-1.5 py-0.5 text-[10.5px] font-bold text-gold-d">비공개</span>}
                </p>
              </div>
              <div className="flex shrink-0 items-center gap-3">
                <Link href={`/cases/${c.slug}`} target="_blank" className="text-[12.5px] text-muted hover:text-navy">보기</Link>
                <Link href={`/admin/cases/${c.id}/edit`} className="text-[12.5px] font-semibold text-navy">수정</Link>
                <DeleteCaseButton id={c.id} />
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

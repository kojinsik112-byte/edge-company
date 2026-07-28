import Link from "next/link";
import Image from "next/image";
import { requireAdmin } from "@/lib/admin";
import { getCases } from "@/lib/data";
import { DeleteCaseButton } from "@/components/admin/AdminButtons";

export const dynamic = "force-dynamic";

export default async function AdminCases() {
  await requireAdmin();
  const cases = await getCases({ includeUnpublished: true, limit: 1000 });

  return (
    <div className="mx-auto max-w-[1000px] px-5 py-8">
      <Link href="/admin" className="text-[13px] text-muted hover:text-navy">← 대시보드</Link>
      <div className="mb-6 mt-3 flex items-center justify-between">
        <h1 className="text-xl font-extrabold text-ink">시공사례 <span className="text-[14px] font-medium text-muted">총 {cases.length}건</span></h1>
        <Link href="/admin/cases/new" className="rounded-lg bg-navy px-5 py-2.5 text-[14px] font-semibold text-white hover:bg-navy-d">+ 새 시공사례</Link>
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

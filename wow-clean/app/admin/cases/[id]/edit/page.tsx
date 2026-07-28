import Link from "next/link";
import { notFound } from "next/navigation";
import { requireAdmin } from "@/lib/admin";
import { getCaseById } from "@/lib/data";
import CaseForm from "@/components/admin/CaseForm";

export const dynamic = "force-dynamic";

export default async function EditCase({ params }: { params: Promise<{ id: string }> }) {
  await requireAdmin();
  const { id } = await params;
  const c = await getCaseById(id);
  if (!c) notFound();

  return (
    <div className="mx-auto max-w-[680px] px-5 py-8">
      <Link href="/admin" className="text-[13px] text-muted hover:text-navy">← 목록</Link>
      <h1 className="mb-7 mt-3 text-xl font-extrabold text-ink">시공사례 수정</h1>
      <CaseForm initial={c} />
    </div>
  );
}

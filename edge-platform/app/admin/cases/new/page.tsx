import Link from "next/link";
import { requireAdmin } from "@/lib/admin";
import CaseForm from "@/components/admin/CaseForm";

export const dynamic = "force-dynamic";

export default async function NewCase() {
  await requireAdmin();
  return (
    <div className="mx-auto max-w-[680px] px-5 py-8">
      <Link href="/admin" className="text-[13px] text-muted hover:text-navy">← 목록</Link>
      <h1 className="mb-7 mt-3 text-xl font-extrabold text-ink">새 시공사례 등록</h1>
      <CaseForm />
    </div>
  );
}

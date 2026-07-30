import Link from "next/link";
import { requireAdmin } from "@/lib/admin";
import CaseForm from "@/components/admin/CaseForm";
import { CATEGORIES, type Category } from "@/lib/constants";

export const dynamic = "force-dynamic";

export default async function NewCase({
  searchParams,
}: {
  searchParams: Promise<{ category?: string }>;
}) {
  await requireAdmin();
  const sp = await searchParams;
  const category = CATEGORIES.includes(sp.category as Category) ? (sp.category as Category) : undefined;
  return (
    <div className="mx-auto max-w-[680px] px-5 py-8">
      <Link href="/admin/cases" className="text-[13px] text-muted hover:text-navy">← 목록</Link>
      <h1 className="mb-7 mt-3 text-xl font-extrabold text-ink">
        새 {category ?? ""} 시공사례 등록
      </h1>
      <CaseForm defaultCategory={category} />
    </div>
  );
}

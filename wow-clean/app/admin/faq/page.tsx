import Link from "next/link";
import { requireAdmin } from "@/lib/admin";
import { createClient } from "@/lib/supabase/server";
import FaqAdmin from "@/components/admin/FaqAdmin";
import type { FaqRow } from "@/lib/types";

export const dynamic = "force-dynamic";

export default async function AdminFaq() {
  await requireAdmin();
  const supabase = await createClient();
  let rows: FaqRow[] = [];
  if (supabase) {
    const { data } = await supabase.from("faq").select("*").order("sort", { ascending: true });
    rows = (data as FaqRow[]) ?? [];
  }
  return (
    <div className="mx-auto max-w-[760px] px-5 py-8">
      <Link href="/admin" className="text-[13px] text-muted hover:text-navy">← 대시보드</Link>
      <h1 className="mb-6 mt-3 text-xl font-extrabold text-ink">FAQ 관리</h1>
      <FaqAdmin rows={rows} />
    </div>
  );
}

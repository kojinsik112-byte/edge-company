import Link from "next/link";
import { requireAdmin } from "@/lib/admin";
import { createClient } from "@/lib/supabase/server";
import PopupsAdmin from "@/components/admin/PopupsAdmin";

export const dynamic = "force-dynamic";

export default async function AdminPopups() {
  await requireAdmin();
  const supabase = await createClient();
  let rows: never[] = [];
  if (supabase) {
    const { data } = await supabase.from("popups").select("*").order("sort", { ascending: true });
    rows = (data as never[]) ?? [];
  }
  return (
    <div className="mx-auto max-w-[760px] px-5 py-8">
      <Link href="/admin" className="text-[13px] text-muted hover:text-navy">← 대시보드</Link>
      <h1 className="mb-6 mt-3 text-xl font-extrabold text-ink">팝업 관리</h1>
      <PopupsAdmin rows={rows} />
    </div>
  );
}

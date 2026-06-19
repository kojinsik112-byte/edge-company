import Link from "next/link";
import { requireAdmin } from "@/lib/admin";
import { createClient } from "@/lib/supabase/server";
import YoutubeAdmin from "@/components/admin/YoutubeAdmin";
import type { YoutubeRow } from "@/lib/types";

export const dynamic = "force-dynamic";

export default async function AdminYoutube() {
  await requireAdmin();
  const supabase = await createClient();
  let rows: YoutubeRow[] = [];
  if (supabase) {
    const { data } = await supabase.from("youtube").select("*").order("sort", { ascending: true });
    rows = (data as YoutubeRow[]) ?? [];
  }
  return (
    <div className="mx-auto max-w-[760px] px-5 py-8">
      <Link href="/admin" className="text-[13px] text-muted hover:text-navy">← 대시보드</Link>
      <h1 className="mb-6 mt-3 text-xl font-extrabold text-ink">유튜브 관리</h1>
      <YoutubeAdmin rows={rows} />
    </div>
  );
}

import Link from "next/link";
import { requireAdmin } from "@/lib/admin";
import { createClient } from "@/lib/supabase/server";
import ReviewsAdmin from "@/components/admin/ReviewsAdmin";
import type { ReviewRow } from "@/lib/types";

export const dynamic = "force-dynamic";

export default async function AdminReviews() {
  await requireAdmin();
  const supabase = await createClient();
  let rows: ReviewRow[] = [];
  if (supabase) {
    const { data } = await supabase.from("reviews").select("*").order("created_at", { ascending: false });
    rows = (data as ReviewRow[]) ?? [];
  }
  return (
    <div className="mx-auto max-w-[760px] px-5 py-8">
      <Link href="/admin" className="text-[13px] text-muted hover:text-navy">← 대시보드</Link>
      <h1 className="mb-6 mt-3 text-xl font-extrabold text-ink">고객후기 관리</h1>
      <ReviewsAdmin rows={rows} />
    </div>
  );
}

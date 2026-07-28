import Link from "next/link";
import { requireAdmin } from "@/lib/admin";
import { createClient } from "@/lib/supabase/server";
import InquiryTable from "@/components/admin/InquiryTable";

export const dynamic = "force-dynamic";

export default async function AdminInquiries() {
  await requireAdmin();
  const supabase = await createClient();
  let rows: never[] = [];
  if (supabase) {
    const { data } = await supabase.from("inquiries").select("*").order("created_at", { ascending: false });
    rows = (data as never[]) ?? [];
  }
  return (
    <div className="mx-auto max-w-[900px] px-5 py-8">
      <Link href="/admin" className="text-[13px] text-muted hover:text-navy">← 대시보드</Link>
      <h1 className="mb-6 mt-3 text-xl font-extrabold text-ink">상담문의</h1>
      <InquiryTable rows={rows} />
    </div>
  );
}

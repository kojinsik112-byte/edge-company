import Link from "next/link";
import { requireAdmin } from "@/lib/admin";
import { createClient } from "@/lib/supabase/server";
import ProductsAdmin from "@/components/admin/ProductsAdmin";
import type { ProductRow } from "@/lib/types";

export const dynamic = "force-dynamic";

export default async function AdminProducts() {
  await requireAdmin();
  const supabase = await createClient();
  let rows: ProductRow[] = [];
  if (supabase) {
    const { data } = await supabase.from("products").select("*").order("sort", { ascending: true });
    rows = (data as ProductRow[]) ?? [];
  }
  return (
    <div className="mx-auto max-w-[760px] px-5 py-8">
      <Link href="/admin" className="text-[13px] text-muted hover:text-navy">← 대시보드</Link>
      <h1 className="mb-6 mt-3 text-xl font-extrabold text-ink">제품 소개 관리</h1>
      <ProductsAdmin rows={rows} />
    </div>
  );
}

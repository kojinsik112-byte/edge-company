"use client";

import { useMemo, useState } from "react";
import { useRouter } from "next/navigation";
import { createClient } from "@/lib/supabase/client";
import { uploadImage } from "@/lib/upload";
import type { ProductRow } from "@/lib/types";

export default function ProductsAdmin({ rows }: { rows: ProductRow[] }) {
  const router = useRouter();
  const supabase = useMemo(() => createClient(), []);
  const [list, setList] = useState(rows);
  const [f, setF] = useState({ name: "", category: "", body: "" });
  const [file, setFile] = useState<File | null>(null);
  const [busy, setBusy] = useState(false);

  async function add(e: React.FormEvent) {
    e.preventDefault();
    if (!f.name) return;
    setBusy(true);
    let image: string | null = null;
    if (file) image = await uploadImage(supabase, file);
    const sort = (list.at(-1)?.sort ?? 0) + 1;
    const { data, error } = await supabase.from("products").insert({ ...f, image, sort }).select().single();
    setBusy(false);
    if (!error && data) {
      setList([...list, data as ProductRow]);
      setF({ name: "", category: "", body: "" });
      setFile(null);
      router.refresh();
    }
  }
  async function del(id: string) {
    if (!confirm("삭제할까요?")) return;
    await supabase.from("products").delete().eq("id", id);
    setList(list.filter((r) => r.id !== id));
    router.refresh();
  }
  async function toggle(p: ProductRow) {
    await supabase.from("products").update({ published: !p.published }).eq("id", p.id);
    setList(list.map((x) => (x.id === p.id ? { ...x, published: !x.published } : x)));
    router.refresh();
  }

  const inp = "w-full rounded-lg border border-line bg-bg px-3 py-2.5 text-[14px] outline-none focus:border-navy";

  return (
    <>
      <form onSubmit={add} className="mb-8 space-y-3 rounded-2xl border border-line bg-surface p-5">
        <p className="text-[14px] font-bold text-ink">+ 제품 추가</p>
        <div className="grid gap-3 sm:grid-cols-2">
          <input className={inp} placeholder="제품명 (예: COB 조명)" value={f.name} onChange={(e) => setF({ ...f, name: e.target.value })} />
          <input className={inp} placeholder="분류 (예: 조명 / 실링팬 / 스위치)" value={f.category} onChange={(e) => setF({ ...f, category: e.target.value })} />
        </div>
        <textarea className={inp} placeholder="제품 설명" value={f.body} onChange={(e) => setF({ ...f, body: e.target.value })} />
        <p className="text-[11.5px] text-gold-d">제품 사진 권장 크기 1200 × 900px (4:3)</p>
        <input type="file" accept="image/*" onChange={(e) => setFile(e.target.files?.[0] ?? null)} className="text-[12.5px] text-muted file:mr-2 file:rounded-md file:border-0 file:bg-navy file:px-3 file:py-2 file:text-white" />
        <button disabled={busy} className="rounded-lg bg-navy px-5 py-2.5 text-[14px] font-semibold text-white disabled:opacity-60">{busy ? "저장 중…" : "제품 등록"}</button>
      </form>
      <div className="grid gap-3 sm:grid-cols-2">
        {list.map((p) => (
          <div key={p.id} className="flex items-center gap-3 rounded-xl border border-line bg-surface p-3">
            {p.image && (
              // eslint-disable-next-line @next/next/no-img-element
              <img src={p.image} alt="" className="h-14 w-20 rounded object-cover" />
            )}
            <div className="min-w-0 flex-1">
              <p className="truncate text-[14px] font-semibold text-ink">{p.name} {!p.published && <span className="text-[11px] text-muted">(비공개)</span>}</p>
              <p className="truncate text-[12px] text-muted">{p.category}</p>
            </div>
            <div className="flex shrink-0 gap-2">
              <button onClick={() => toggle(p)} className="text-[12px] font-semibold text-muted hover:text-navy">{p.published ? "비공개" : "공개"}</button>
              <button onClick={() => del(p.id)} className="text-[12px] font-semibold text-red-600">삭제</button>
            </div>
          </div>
        ))}
      </div>
    </>
  );
}

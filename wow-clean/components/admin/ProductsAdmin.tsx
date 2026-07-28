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
  const [files, setFiles] = useState<File[]>([]);
  const [busy, setBusy] = useState(false);

  async function add(e: React.FormEvent) {
    e.preventDefault();
    if (!f.name) return;
    setBusy(true);
    const urls: string[] = [];
    for (const fl of files) urls.push(await uploadImage(supabase, fl));
    const image = urls[0] ?? null;
    const sort = (list.at(-1)?.sort ?? 0) + 1;
    let res = await supabase.from("products").insert({ ...f, image, images: urls, sort }).select().single();
    if (res.error && /images/i.test(res.error.message)) {
      // images 컬럼이 아직 없으면(마이그레이션 전) 대표 이미지만 저장
      res = await supabase.from("products").insert({ ...f, image, sort }).select().single();
    }
    setBusy(false);
    if (!res.error && res.data) {
      setList([...list, res.data as ProductRow]);
      setF({ name: "", category: "", body: "" });
      setFiles([]);
      router.refresh();
    } else if (res.error) {
      alert(`저장 오류: ${res.error.message}`);
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
          <input className={inp} placeholder="서비스명 (예: 고압 배관청소)" value={f.name} onChange={(e) => setF({ ...f, name: e.target.value })} />
          <input className={inp} placeholder="분류 (예: 하수구 / 변기 / 배관청소)" value={f.category} onChange={(e) => setF({ ...f, category: e.target.value })} />
        </div>
        <textarea className={inp} placeholder="제품 설명" value={f.body} onChange={(e) => setF({ ...f, body: e.target.value })} />
        <p className="text-[11.5px] text-gold-d">제품 사진 (여러 장 · 첫 장이 대표) · 권장 1200 × 900px (4:3) — 상세페이지에 갤러리로 표시됩니다</p>
        <input type="file" accept="image/*" multiple onChange={(e) => setFiles(Array.from(e.target.files ?? []))} className="text-[12.5px] text-muted file:mr-2 file:rounded-md file:border-0 file:bg-navy file:px-3 file:py-2 file:text-white" />
        {files.length > 0 && <p className="text-[11.5px] text-navy">{files.length}장 선택됨 (첫 장이 대표 이미지)</p>}
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

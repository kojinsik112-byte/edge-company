"use client";

import { useMemo, useState } from "react";
import { useRouter } from "next/navigation";
import { createClient } from "@/lib/supabase/client";
import { uploadImage } from "@/lib/upload";
import { REGIONS } from "@/lib/constants";
import type { ReviewRow } from "@/lib/types";

export default function ReviewsAdmin({ rows }: { rows: ReviewRow[] }) {
  const router = useRouter();
  const supabase = useMemo(() => createClient(), []);
  const [list, setList] = useState(rows);
  const [f, setF] = useState({ title: "", name: "", apartment: "", region: "울산", rating: 5, content: "" });
  const [file, setFile] = useState<File | null>(null);
  const [busy, setBusy] = useState(false);

  async function add(e: React.FormEvent) {
    e.preventDefault();
    if (!f.content || (!f.name && !f.apartment)) return;
    setBusy(true);
    let image: string | null = null;
    if (file) image = await uploadImage(supabase, file);
    const { data, error } = await supabase.from("reviews").insert({ ...f, image }).select().single();
    setBusy(false);
    if (!error && data) {
      setList([data as ReviewRow, ...list]);
      setF({ title: "", name: "", apartment: "", region: "울산", rating: 5, content: "" });
      setFile(null);
      router.refresh();
    }
  }
  async function del(id: string) {
    if (!confirm("삭제할까요?")) return;
    await supabase.from("reviews").delete().eq("id", id);
    setList(list.filter((r) => r.id !== id));
    router.refresh();
  }
  async function toggle(r: ReviewRow) {
    await supabase.from("reviews").update({ published: !r.published }).eq("id", r.id);
    setList(list.map((x) => (x.id === r.id ? { ...x, published: !x.published } : x)));
    router.refresh();
  }

  const inp = "rounded-lg border border-line bg-bg px-3 py-2.5 text-[14px] outline-none focus:border-navy";

  return (
    <>
      <form onSubmit={add} className="mb-8 space-y-3 rounded-2xl border border-line bg-surface p-5">
        <p className="text-[14px] font-bold text-ink">+ 후기 추가</p>
        <input className={`${inp} w-full`} placeholder="제목 (예: 거실 분위기가 완전히 달라졌어요)" value={f.title} onChange={(e) => setF({ ...f, title: e.target.value })} />
        <div className="grid gap-3 sm:grid-cols-2">
          <input className={inp} placeholder="아파트명 (예: 문수로 롯데캐슬)" value={f.apartment} onChange={(e) => setF({ ...f, apartment: e.target.value })} />
          <input className={inp} placeholder="작성자 (예: 김○○ 고객님)" value={f.name} onChange={(e) => setF({ ...f, name: e.target.value })} />
          <select className={inp} value={f.region} onChange={(e) => setF({ ...f, region: e.target.value })}>{REGIONS.map((r) => <option key={r}>{r}</option>)}</select>
          <select className={inp} value={f.rating} onChange={(e) => setF({ ...f, rating: Number(e.target.value) })}>{[5, 4, 3, 2, 1].map((n) => <option key={n} value={n}>{"★".repeat(n)} ({n}점)</option>)}</select>
        </div>
        <textarea className={`${inp} w-full`} placeholder="후기 내용" value={f.content} onChange={(e) => setF({ ...f, content: e.target.value })} />
        <p className="text-[11.5px] text-gold-d">후기 사진 권장 크기 1200 × 750px (16:10)</p>
        <input type="file" accept="image/*" onChange={(e) => setFile(e.target.files?.[0] ?? null)} className="text-[12.5px] text-muted file:mr-2 file:rounded-md file:border-0 file:bg-navy file:px-3 file:py-2 file:text-white" />
        <button disabled={busy} className="rounded-lg bg-navy px-5 py-2.5 text-[14px] font-semibold text-white disabled:opacity-60">{busy ? "저장 중…" : "후기 등록"}</button>
      </form>

      <div className="space-y-3">
        {list.map((r) => (
          <div key={r.id} className="flex items-start justify-between gap-3 rounded-xl border border-line bg-surface p-4">
            <div>
              <p className="text-[13px] font-bold text-gold-d">{"★".repeat(r.rating)} <span className="text-ink">{[r.region, r.apartment, r.name].filter(Boolean).join(" · ")}</span> {!r.published && <span className="ml-1 text-[11px] text-muted">(비공개)</span>}</p>
              {r.title && <p className="mt-1 text-[14px] font-bold text-ink">{r.title}</p>}
              <p className="mt-1 text-[13.5px] text-muted">{r.content}</p>
            </div>
            <div className="flex shrink-0 gap-2">
              <button onClick={() => toggle(r)} className="text-[12px] font-semibold text-muted hover:text-navy">{r.published ? "비공개" : "공개"}</button>
              <button onClick={() => del(r.id)} className="text-[12px] font-semibold text-red-600">삭제</button>
            </div>
          </div>
        ))}
      </div>
    </>
  );
}

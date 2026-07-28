"use client";

import { useMemo, useState } from "react";
import { useRouter } from "next/navigation";
import { createClient } from "@/lib/supabase/client";
import type { FaqRow } from "@/lib/types";

export default function FaqAdmin({ rows }: { rows: FaqRow[] }) {
  const router = useRouter();
  const supabase = useMemo(() => createClient(), []);
  const [list, setList] = useState(rows);
  const [f, setF] = useState({ question: "", answer: "" });
  const [busy, setBusy] = useState(false);

  async function add(e: React.FormEvent) {
    e.preventDefault();
    if (!f.question) return;
    setBusy(true);
    const sort = (list.at(-1)?.sort ?? 0) + 1;
    const { data, error } = await supabase.from("faq").insert({ ...f, sort }).select().single();
    setBusy(false);
    if (!error && data) {
      setList([...list, data as FaqRow]);
      setF({ question: "", answer: "" });
      router.refresh();
    }
  }
  async function del(id: string) {
    if (!confirm("삭제할까요?")) return;
    await supabase.from("faq").delete().eq("id", id);
    setList(list.filter((r) => r.id !== id));
    router.refresh();
  }

  const inp = "w-full rounded-lg border border-line bg-bg px-3 py-2.5 text-[14px] outline-none focus:border-navy";

  return (
    <>
      <form onSubmit={add} className="mb-8 space-y-3 rounded-2xl border border-line bg-surface p-5">
        <p className="text-[14px] font-bold text-ink">+ 질문 추가</p>
        <input className={inp} placeholder="질문" value={f.question} onChange={(e) => setF({ ...f, question: e.target.value })} />
        <textarea className={inp} placeholder="답변" value={f.answer} onChange={(e) => setF({ ...f, answer: e.target.value })} />
        <button disabled={busy} className="rounded-lg bg-navy px-5 py-2.5 text-[14px] font-semibold text-white disabled:opacity-60">{busy ? "저장 중…" : "등록"}</button>
      </form>
      <div className="space-y-3">
        {list.map((r) => (
          <div key={r.id} className="flex items-start justify-between gap-3 rounded-xl border border-line bg-surface p-4">
            <div>
              <p className="text-[14px] font-semibold text-ink">Q. {r.question}</p>
              <p className="mt-1 text-[13px] text-muted">{r.answer}</p>
            </div>
            <button onClick={() => del(r.id)} className="shrink-0 text-[12px] font-semibold text-red-600">삭제</button>
          </div>
        ))}
      </div>
    </>
  );
}

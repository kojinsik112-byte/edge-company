"use client";

import { useMemo, useState } from "react";
import { useRouter } from "next/navigation";
import { createClient } from "@/lib/supabase/client";
import type { YoutubeRow } from "@/lib/types";

// 유튜브 URL/ID 에서 video_id 추출
function extractId(input: string): string {
  const m = input.match(/(?:youtu\.be\/|v=|shorts\/|embed\/)([\w-]{11})/);
  return m ? m[1] : input.trim();
}

export default function YoutubeAdmin({ rows }: { rows: YoutubeRow[] }) {
  const router = useRouter();
  const supabase = useMemo(() => createClient(), []);
  const [list, setList] = useState(rows);
  const [f, setF] = useState({ url: "", title: "", views: "" });
  const [busy, setBusy] = useState(false);

  async function add(e: React.FormEvent) {
    e.preventDefault();
    const video_id = extractId(f.url);
    if (!video_id) return;
    setBusy(true);
    const sort = (list.at(-1)?.sort ?? 0) + 1;
    const { data, error } = await supabase.from("youtube").insert({ video_id, title: f.title, views: f.views || null, sort }).select().single();
    setBusy(false);
    if (!error && data) {
      setList([...list, data as YoutubeRow]);
      setF({ url: "", title: "", views: "" });
      router.refresh();
    }
  }
  async function del(id: string) {
    if (!confirm("삭제할까요?")) return;
    await supabase.from("youtube").delete().eq("id", id);
    setList(list.filter((r) => r.id !== id));
    router.refresh();
  }

  const inp = "w-full rounded-lg border border-line bg-bg px-3 py-2.5 text-[14px] outline-none focus:border-navy";

  return (
    <>
      <form onSubmit={add} className="mb-8 space-y-3 rounded-2xl border border-line bg-surface p-5">
        <p className="text-[14px] font-bold text-ink">+ 영상 추가</p>
        <input className={inp} placeholder="유튜브 링크 또는 영상 ID" value={f.url} onChange={(e) => setF({ ...f, url: e.target.value })} />
        <div className="grid gap-3 sm:grid-cols-2">
          <input className={inp} placeholder="제목" value={f.title} onChange={(e) => setF({ ...f, title: e.target.value })} />
          <input className={inp} placeholder="조회수 표기 (예: 1.2만회)" value={f.views} onChange={(e) => setF({ ...f, views: e.target.value })} />
        </div>
        <button disabled={busy} className="rounded-lg bg-navy px-5 py-2.5 text-[14px] font-semibold text-white disabled:opacity-60">{busy ? "저장 중…" : "등록"}</button>
      </form>
      <div className="grid gap-3 sm:grid-cols-2">
        {list.map((r) => (
          <div key={r.id} className="flex items-center gap-3 rounded-xl border border-line bg-surface p-3">
            {/* eslint-disable-next-line @next/next/no-img-element */}
            <img src={`https://i.ytimg.com/vi/${r.video_id}/default.jpg`} alt="" className="h-12 w-20 rounded object-cover" />
            <div className="min-w-0 flex-1">
              <p className="truncate text-[13px] font-semibold text-ink">{r.title || r.video_id}</p>
              {r.views && <p className="text-[11.5px] text-muted">조회수 {r.views}</p>}
            </div>
            <button onClick={() => del(r.id)} className="shrink-0 text-[12px] font-semibold text-red-600">삭제</button>
          </div>
        ))}
      </div>
    </>
  );
}

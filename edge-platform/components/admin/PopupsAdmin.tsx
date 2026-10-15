"use client";

import { useMemo, useState } from "react";
import { useRouter } from "next/navigation";
import { createClient } from "@/lib/supabase/client";
import { uploadImage } from "@/lib/upload";

interface PopupRow {
  id: string;
  title: string;
  content: string | null;
  image: string | null;
  link: string | null;
  enabled: boolean;
  start_at: string | null;
  end_at: string | null;
}

const EMPTY = { title: "", content: "", link: "", start_at: "", end_at: "", enabled: true };

export default function PopupsAdmin({ rows }: { rows: PopupRow[] }) {
  const router = useRouter();
  const supabase = useMemo(() => createClient(), []);
  const [list, setList] = useState(rows);
  const [f, setF] = useState(EMPTY);
  const [file, setFile] = useState<File | null>(null);
  const [busy, setBusy] = useState(false);
  // 수정 모드
  const [editId, setEditId] = useState<string | null>(null);
  const [ef, setEf] = useState(EMPTY);
  const [eFile, setEFile] = useState<File | null>(null);

  async function add(e: React.FormEvent) {
    e.preventDefault();
    setBusy(true);
    let image: string | null = null;
    if (file) image = await uploadImage(supabase, file);
    const rec = {
      title: f.title,
      content: f.content || null,
      link: f.link || null,
      image,
      enabled: f.enabled,
      start_at: f.start_at || null,
      end_at: f.end_at || null,
    };
    const { data, error } = await supabase.from("popups").insert(rec).select().single();
    setBusy(false);
    if (!error && data) {
      setList([data as PopupRow, ...list]);
      setF(EMPTY);
      setFile(null);
      router.refresh();
    }
  }

  function startEdit(p: PopupRow) {
    setEditId(p.id);
    setEf({
      title: p.title ?? "",
      content: p.content ?? "",
      link: p.link ?? "",
      start_at: p.start_at ?? "",
      end_at: p.end_at ?? "",
      enabled: p.enabled,
    });
    setEFile(null);
  }

  async function saveEdit(e: React.FormEvent) {
    e.preventDefault();
    if (!editId) return;
    setBusy(true);
    const rec: Record<string, unknown> = {
      title: ef.title,
      content: ef.content || null,
      link: ef.link || null,
      enabled: ef.enabled,
      start_at: ef.start_at || null,
      end_at: ef.end_at || null,
    };
    if (eFile) rec.image = await uploadImage(supabase, eFile); // 새 이미지 선택 시에만 교체
    const { error } = await supabase.from("popups").update(rec).eq("id", editId);
    setBusy(false);
    if (!error) {
      setList(list.map((x) => (x.id === editId ? ({ ...x, ...rec } as PopupRow) : x)));
      setEditId(null);
      router.refresh();
    }
  }

  async function toggle(p: PopupRow) {
    await supabase.from("popups").update({ enabled: !p.enabled }).eq("id", p.id);
    setList(list.map((x) => (x.id === p.id ? { ...x, enabled: !x.enabled } : x)));
    router.refresh();
  }
  async function del(id: string) {
    if (!confirm("삭제할까요?")) return;
    await supabase.from("popups").delete().eq("id", id);
    setList(list.filter((p) => p.id !== id));
    if (editId === id) setEditId(null);
    router.refresh();
  }

  const inp = "w-full rounded-lg border border-line bg-bg px-3 py-2.5 text-[14px] outline-none focus:border-navy";

  return (
    <>
      <form onSubmit={add} className="mb-8 space-y-3 rounded-2xl border border-line bg-surface p-5">
        <p className="text-[14px] font-bold text-ink">+ 팝업 추가 <span className="font-normal text-muted">(갯수 제한 없음 — 등록한 만큼 사이트에 나란히 뜸)</span></p>
        <input className={inp} placeholder="제목 (예: 울산 신규아파트 공동구매 행사)" value={f.title} onChange={(e) => setF({ ...f, title: e.target.value })} />
        <textarea className={inp} placeholder="공지/메모 내용 (텍스트만으로도 팝업 가능, 이미지 없어도 됨)" value={f.content} onChange={(e) => setF({ ...f, content: e.target.value })} />
        <input className={inp} placeholder="클릭 시 이동 링크 (예: /contact) — 선택" value={f.link} onChange={(e) => setF({ ...f, link: e.target.value })} />
        <div className="grid gap-3 sm:grid-cols-2">
          <label className="text-[12.5px] text-muted">시작일<input type="date" className={inp} value={f.start_at} onChange={(e) => setF({ ...f, start_at: e.target.value })} /></label>
          <label className="text-[12.5px] text-muted">종료일<input type="date" className={inp} value={f.end_at} onChange={(e) => setF({ ...f, end_at: e.target.value })} /></label>
        </div>
        <p className="text-[11.5px] text-gold-d">팝업 이미지 권장 840 × 1188px (A4 세로 비율) — 화면에 A4 절반 크기 카드로 뜹니다</p>
        <input type="file" accept="image/*" onChange={(e) => setFile(e.target.files?.[0] ?? null)} className="text-[12.5px] text-muted file:mr-2 file:rounded-md file:border-0 file:bg-navy file:px-3 file:py-2 file:text-white" />
        <label className="flex items-center gap-2 text-[14px] font-medium text-ink"><input type="checkbox" checked={f.enabled} onChange={(e) => setF({ ...f, enabled: e.target.checked })} className="h-4 w-4" />노출 ON</label>
        <button disabled={busy} className="rounded-lg bg-navy px-5 py-2.5 text-[14px] font-semibold text-white disabled:opacity-60">{busy ? "저장 중…" : "팝업 등록"}</button>
      </form>

      <div className="space-y-3">
        {list.map((p) =>
          editId === p.id ? (
            <form key={p.id} onSubmit={saveEdit} className="space-y-3 rounded-xl border border-navy bg-surface p-4">
              <p className="text-[13px] font-bold text-navy">✏️ 팝업 수정</p>
              <input className={inp} placeholder="제목" value={ef.title} onChange={(e) => setEf({ ...ef, title: e.target.value })} />
              <textarea className={inp} placeholder="내용" value={ef.content} onChange={(e) => setEf({ ...ef, content: e.target.value })} />
              <input className={inp} placeholder="클릭 시 이동 링크" value={ef.link} onChange={(e) => setEf({ ...ef, link: e.target.value })} />
              <div className="grid gap-3 sm:grid-cols-2">
                <label className="text-[12.5px] text-muted">시작일<input type="date" className={inp} value={ef.start_at} onChange={(e) => setEf({ ...ef, start_at: e.target.value })} /></label>
                <label className="text-[12.5px] text-muted">종료일<input type="date" className={inp} value={ef.end_at} onChange={(e) => setEf({ ...ef, end_at: e.target.value })} /></label>
              </div>
              <div className="flex items-center gap-3">
                {p.image && (
                  // eslint-disable-next-line @next/next/no-img-element
                  <img src={p.image} alt="" className="h-14 w-20 rounded object-cover" />
                )}
                <label className="text-[12.5px] text-muted">이미지 교체 (선택 안 하면 기존 유지)
                  <input type="file" accept="image/*" onChange={(e) => setEFile(e.target.files?.[0] ?? null)} className="block text-[12.5px] text-muted file:mr-2 file:rounded-md file:border-0 file:bg-navy file:px-3 file:py-1.5 file:text-white" />
                </label>
              </div>
              <label className="flex items-center gap-2 text-[14px] font-medium text-ink"><input type="checkbox" checked={ef.enabled} onChange={(e) => setEf({ ...ef, enabled: e.target.checked })} className="h-4 w-4" />노출 ON</label>
              <div className="flex gap-2">
                <button disabled={busy} className="rounded-lg bg-navy px-5 py-2.5 text-[14px] font-semibold text-white disabled:opacity-60">{busy ? "저장 중…" : "저장"}</button>
                <button type="button" onClick={() => setEditId(null)} className="rounded-lg border border-line px-5 py-2.5 text-[14px] font-semibold text-ink">취소</button>
              </div>
            </form>
          ) : (
            <div key={p.id} className="flex items-center gap-3 rounded-xl border border-line bg-surface p-3">
              {p.image && (
                // eslint-disable-next-line @next/next/no-img-element
                <img src={p.image} alt="" className="h-14 w-20 rounded object-cover" />
              )}
              <div className="min-w-0 flex-1">
                <p className="truncate text-[14px] font-semibold text-ink">{p.title || "(제목 없음)"} {!p.enabled && <span className="text-[11px] text-muted">(꺼짐)</span>}</p>
                <p className="text-[11.5px] text-muted">{p.start_at ?? "상시"} ~ {p.end_at ?? "상시"}</p>
              </div>
              <div className="flex shrink-0 gap-2">
                <button onClick={() => startEdit(p)} className="text-[12px] font-semibold text-muted hover:text-navy">수정</button>
                <button onClick={() => toggle(p)} className="text-[12px] font-semibold text-muted hover:text-navy">{p.enabled ? "끄기" : "켜기"}</button>
                <button onClick={() => del(p.id)} className="text-[12px] font-semibold text-red-600">삭제</button>
              </div>
            </div>
          ),
        )}
      </div>
    </>
  );
}

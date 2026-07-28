"use client";

import { useState } from "react";
import { createClient } from "@/lib/supabase/client";

interface Inquiry {
  id: string;
  created_at: string;
  name: string;
  phone: string;
  region: string | null;
  category: string | null;
  message: string;
  status: string;
}

const STATUSES = ["신규", "상담중", "완료"];

export default function InquiryTable({ rows }: { rows: Inquiry[] }) {
  const [items, setItems] = useState(rows);

  async function setStatus(id: string, status: string) {
    setItems((p) => p.map((x) => (x.id === id ? { ...x, status } : x)));
    await createClient().from("inquiries").update({ status }).eq("id", id);
  }

  function downloadCsv() {
    const header = ["접수일", "이름", "연락처", "지역", "품목", "내용", "상태"];
    const lines = items.map((r) =>
      [r.created_at?.slice(0, 16).replace("T", " "), r.name, r.phone, r.region ?? "", r.category ?? "", (r.message ?? "").replace(/[\r\n]+/g, " "), r.status]
        .map((v) => `"${String(v).replace(/"/g, '""')}"`)
        .join(","),
    );
    const csv = "﻿" + [header.join(","), ...lines].join("\r\n"); // BOM → 엑셀 한글 깨짐 방지
    const url = URL.createObjectURL(new Blob([csv], { type: "text/csv;charset=utf-8;" }));
    const a = document.createElement("a");
    a.href = url;
    a.download = `상담문의_${new Date().toISOString().slice(0, 10)}.csv`;
    a.click();
    URL.revokeObjectURL(url);
  }

  const badge = (s: string) =>
    s === "신규" ? "bg-gold/20 text-gold-d" : s === "상담중" ? "bg-blue-100 text-blue-700" : "bg-green-100 text-green-700";

  return (
    <>
      <div className="mb-4 flex items-center justify-between">
        <p className="text-[13px] text-muted">총 {items.length}건</p>
        <button onClick={downloadCsv} className="rounded-lg border border-line bg-surface px-4 py-2 text-[13px] font-semibold text-ink hover:border-navy">
          엑셀(CSV) 다운로드
        </button>
      </div>

      {items.length === 0 ? (
        <div className="rounded-2xl border border-dashed border-line bg-surface py-20 text-center text-[14px] text-muted">접수된 문의가 없습니다.</div>
      ) : (
        <div className="space-y-3">
          {items.map((r) => (
            <div key={r.id} className="rounded-xl border border-line bg-surface p-4">
              <div className="flex flex-wrap items-center justify-between gap-2">
                <div className="flex items-center gap-2">
                  <span className={`rounded-full px-2.5 py-1 text-[11px] font-bold ${badge(r.status)}`}>{r.status}</span>
                  <span className="text-[14px] font-bold text-ink">{r.name}</span>
                  <a href={`tel:${r.phone.replace(/-/g, "")}`} className="text-[13px] font-semibold text-navy">{r.phone}</a>
                </div>
                <div className="flex gap-1">
                  {STATUSES.map((s) => (
                    <button key={s} onClick={() => setStatus(r.id, s)} className={`rounded-md px-2.5 py-1 text-[11.5px] font-semibold ${r.status === s ? "bg-navy text-white" : "border border-line text-muted hover:border-navy"}`}>
                      {s}
                    </button>
                  ))}
                </div>
              </div>
              <p className="mt-2 text-[12.5px] text-muted">
                {r.region} · {r.category} · {r.created_at?.slice(0, 16).replace("T", " ")}
              </p>
              {r.message && <p className="mt-2 whitespace-pre-wrap text-[13.5px] text-ink">{r.message}</p>}
            </div>
          ))}
        </div>
      )}
    </>
  );
}

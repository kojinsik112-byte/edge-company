"use client";

import { useMemo, useState } from "react";
import { createClient } from "@/lib/supabase/client";
import { REGIONS, CATEGORIES } from "@/lib/constants";

export default function ContactForm() {
  const supabase = useMemo(() => createClient(), []);
  const [form, setForm] = useState({ name: "", phone: "", region: "울산", category: "실링팬", message: "" });
  const [done, setDone] = useState(false);
  const [busy, setBusy] = useState(false);
  const [err, setErr] = useState("");

  async function submit(e: React.FormEvent) {
    e.preventDefault();
    if (!form.name || !form.phone) {
      setErr("이름과 연락처를 입력해 주세요.");
      return;
    }
    setBusy(true);
    setErr("");
    const { error } = await supabase.from("inquiries").insert(form);
    setBusy(false);
    if (error) setErr("접수 중 오류가 발생했습니다. 전화로 문의해 주세요.");
    else setDone(true);
  }

  if (done)
    return (
      <div className="rounded-2xl bg-white/10 p-8 text-center">
        <p className="text-[17px] font-bold text-white">상담 신청이 접수되었습니다.</p>
        <p className="mt-2 text-[14px] text-white/70">빠른 시간 안에 연락드리겠습니다. 감사합니다.</p>
      </div>
    );

  const inp = "w-full rounded-lg border border-white/20 bg-white/10 px-3.5 py-3 text-[14px] text-white placeholder:text-white/45 outline-none focus:border-gold";

  return (
    <form onSubmit={submit} className="rounded-2xl bg-white/[0.06] p-6 text-left sm:p-8">
      <p className="mb-4 text-center text-[15px] font-bold text-white">온라인 상담 신청</p>
      <div className="grid gap-3 sm:grid-cols-2">
        <input className={inp} placeholder="이름" value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} />
        <input className={inp} placeholder="연락처 (예: 010-0000-0000)" value={form.phone} onChange={(e) => setForm({ ...form, phone: e.target.value })} />
        <select className={inp} value={form.region} onChange={(e) => setForm({ ...form, region: e.target.value })}>
          {REGIONS.map((r) => <option key={r} className="text-ink">{r}</option>)}
        </select>
        <select className={inp} value={form.category} onChange={(e) => setForm({ ...form, category: e.target.value })}>
          {CATEGORIES.map((c) => <option key={c} className="text-ink">{c}</option>)}
        </select>
      </div>
      <textarea className={`${inp} mt-3 min-h-[90px]`} placeholder="문의 내용 (선택)" value={form.message} onChange={(e) => setForm({ ...form, message: e.target.value })} />
      {err && <p className="mt-2 text-[13px] text-gold">{err}</p>}
      <button type="submit" disabled={busy} className="mt-4 w-full rounded-lg bg-gold py-3.5 text-[15px] font-bold text-ink disabled:opacity-60">
        {busy ? "접수 중…" : "상담 신청하기"}
      </button>
      <p className="mt-3 text-center text-[11.5px] text-white/45">접수 즉시 관리자에게 전달되며, 빠르게 연락드립니다.</p>
    </form>
  );
}

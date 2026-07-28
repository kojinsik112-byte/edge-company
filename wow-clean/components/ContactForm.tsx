"use client";

import { useMemo, useState } from "react";
import { createClient } from "@/lib/supabase/client";
import { REGIONS, CATEGORIES } from "@/lib/constants";

export default function ContactForm() {
  const supabase = useMemo(() => createClient(), []);
  const [form, setForm] = useState({ name: "", phone: "", region: "서울", category: "하수구막힘", message: "" });
  const [agree, setAgree] = useState(false);
  const [done, setDone] = useState(false);
  const [busy, setBusy] = useState(false);
  const [err, setErr] = useState("");

  async function submit(e: React.FormEvent) {
    e.preventDefault();
    if (!form.name || !form.phone) {
      setErr("이름과 연락처를 입력해 주세요.");
      return;
    }
    if (!agree) {
      setErr("개인정보 수집·이용에 동의해 주세요.");
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
      <div className="rounded-2xl border border-line bg-surface p-8 text-center">
        <p className="text-[17px] font-bold text-ink">상담 신청이 접수되었습니다.</p>
        <p className="mt-2 text-[14px] text-muted">빠른 시간 안에 연락드리겠습니다. 감사합니다.</p>
      </div>
    );

  const inp = "w-full rounded-lg border border-line bg-bg px-3.5 py-3 text-[14px] text-ink placeholder:text-muted outline-none focus:border-gold";

  return (
    <form onSubmit={submit} className="rounded-2xl border border-line bg-surface p-6 text-left sm:p-8">
      <p className="mb-4 text-center text-[15px] font-bold text-ink">온라인 상담 신청</p>
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
      <label className="mt-3 flex items-start gap-2 text-[12.5px] text-muted">
        <input type="checkbox" checked={agree} onChange={(e) => setAgree(e.target.checked)} className="mt-0.5 h-4 w-4 shrink-0" />
        <span>상담을 위한 <b className="font-semibold text-ink">개인정보(이름·연락처) 수집·이용</b>에 동의합니다. 수집된 정보는 상담 목적 외 사용하지 않습니다.</span>
      </label>
      {err && <p className="mt-2 text-[13px] text-red-600">{err}</p>}
      <button type="submit" disabled={busy} className="mt-4 w-full rounded-lg bg-ink py-3.5 text-[15px] font-bold text-white transition hover:bg-[#111827] disabled:opacity-60">
        {busy ? "접수 중…" : "상담 신청하기"}
      </button>
      <p className="mt-3 text-center text-[11.5px] text-muted">접수 즉시 관리자에게 전달되며, 빠르게 연락드립니다.</p>
    </form>
  );
}

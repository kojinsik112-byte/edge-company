"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { createClient } from "@/lib/supabase/client";
import { SUPABASE_READY } from "@/lib/supabase/env";

export default function AdminLogin() {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      const supabase = createClient();
      const { error } = await supabase.auth.signInWithPassword({ email, password });
      if (error) {
        setError("이메일 또는 비밀번호가 올바르지 않습니다.");
        return;
      }
      router.push("/admin");
      router.refresh();
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="flex min-h-screen items-center justify-center px-5">
      <form onSubmit={onSubmit} className="w-full max-w-sm rounded-2xl border border-line bg-surface p-8 shadow-[0_22px_60px_-30px_rgba(16,37,66,0.4)]">
        <div className="mb-6 flex items-center gap-2.5">
          <span className="flex h-9 w-9 items-center justify-center rounded-lg bg-navy font-serif text-lg font-bold text-gold">E</span>
          <span className="font-extrabold tracking-tight text-ink">엣지리브커튼 관리자</span>
        </div>

        {!SUPABASE_READY && (
          <p className="mb-4 rounded-lg bg-gold/15 px-3 py-2 text-[12.5px] text-gold-d">
            Supabase 환경변수가 설정되지 않았습니다. <code>.env.local</code> 을 먼저 채워 주세요.
          </p>
        )}

        <label className="mb-1 block text-[13px] font-semibold text-ink">이메일</label>
        <input
          type="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          required
          autoComplete="username"
          className="mb-4 w-full rounded-lg border border-line bg-bg px-3.5 py-3 text-[14px] outline-none focus:border-navy"
        />
        <label className="mb-1 block text-[13px] font-semibold text-ink">비밀번호</label>
        <input
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
          autoComplete="current-password"
          className="mb-2 w-full rounded-lg border border-line bg-bg px-3.5 py-3 text-[14px] outline-none focus:border-navy"
        />

        {error && <p className="mb-2 text-[12.5px] text-red-600">{error}</p>}

        <button
          type="submit"
          disabled={loading}
          className="mt-3 w-full rounded-lg bg-navy py-3 text-[15px] font-semibold text-white transition hover:bg-navy-d disabled:opacity-60"
        >
          {loading ? "로그인 중…" : "로그인"}
        </button>
        <p className="mt-4 text-center text-[11.5px] text-muted">
          계정은 Supabase &gt; Authentication 에서 발급합니다.
        </p>
      </form>
    </div>
  );
}

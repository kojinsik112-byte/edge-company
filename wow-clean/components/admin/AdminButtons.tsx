"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";
import { createClient } from "@/lib/supabase/client";

export function LogoutButton() {
  const router = useRouter();
  return (
    <button
      onClick={async () => {
        await createClient().auth.signOut();
        router.push("/admin/login");
        router.refresh();
      }}
      className="text-[13px] font-semibold text-muted hover:text-navy"
    >
      로그아웃
    </button>
  );
}

export function DeleteCaseButton({ id }: { id: string }) {
  const router = useRouter();
  const [busy, setBusy] = useState(false);
  return (
    <button
      disabled={busy}
      onClick={async () => {
        if (!confirm("이 시공사례를 삭제할까요? 되돌릴 수 없습니다.")) return;
        setBusy(true);
        const { error } = await createClient().from("cases").delete().eq("id", id);
        if (error) {
          alert(`삭제 실패: ${error.message}`);
          setBusy(false);
          return;
        }
        router.refresh();
      }}
      className="text-[12.5px] font-semibold text-red-600 disabled:opacity-50"
    >
      {busy ? "삭제 중…" : "삭제"}
    </button>
  );
}

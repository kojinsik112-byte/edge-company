"use client";

import { createBrowserClient } from "@supabase/ssr";
import { SUPABASE_URL, SUPABASE_ANON_KEY, SUPABASE_READY } from "./env";

// 브라우저(클라이언트 컴포넌트)용 Supabase 클라이언트
// 키 미설정(드라이런)이어도 빌드·프리렌더가 죽지 않도록 플레이스홀더로 생성 —
// 실제 요청 시점에 실패하고, 폼 쪽 에러 처리("전화로 문의")로 안내된다.
export function createClient() {
  if (!SUPABASE_READY) {
    return createBrowserClient("https://placeholder.supabase.co", "public-anon-key-placeholder");
  }
  return createBrowserClient(SUPABASE_URL, SUPABASE_ANON_KEY);
}

import { createServerClient } from "@supabase/ssr";
import { cookies } from "next/headers";
import { SUPABASE_URL, SUPABASE_ANON_KEY, SUPABASE_READY } from "./env";

/**
 * 서버 컴포넌트 / 서버 액션용 Supabase 클라이언트.
 * env 미설정 시 null 을 반환해 사이트가 폴백으로 렌더되게 한다.
 */
export async function createClient() {
  if (!SUPABASE_READY) return null;
  const cookieStore = await cookies();
  return createServerClient(SUPABASE_URL, SUPABASE_ANON_KEY, {
    cookies: {
      getAll() {
        return cookieStore.getAll();
      },
      setAll(cookiesToSet) {
        try {
          cookiesToSet.forEach(({ name, value, options }) =>
            cookieStore.set(name, value, options),
          );
        } catch {
          // 서버 컴포넌트에서 호출되면 무시 (미들웨어/액션에서만 set 가능)
        }
      },
    },
  });
}

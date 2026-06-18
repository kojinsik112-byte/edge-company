import { redirect } from "next/navigation";
import { createClient } from "./supabase/server";

/** 현재 로그인 사용자 조회 (서버). Supabase 미설정 시 user=null */
export async function getAdmin() {
  const supabase = await createClient();
  if (!supabase) return { supabase: null, user: null };
  const {
    data: { user },
  } = await supabase.auth.getUser();
  return { supabase, user };
}

/** 보호된 관리자 페이지 가드. 미로그인 시 /admin/login 으로 리다이렉트 */
export async function requireAdmin() {
  const { supabase, user } = await getAdmin();
  if (!supabase) redirect("/admin/login?nosupabase=1");
  if (!user) redirect("/admin/login");
  return { supabase, user };
}

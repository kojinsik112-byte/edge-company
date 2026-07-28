export const SUPABASE_URL = process.env.NEXT_PUBLIC_SUPABASE_URL || "";
export const SUPABASE_ANON_KEY = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY || "";

// Supabase 키가 채워졌는지 (미설정이면 사이트는 디자인/폴백으로 동작)
export const SUPABASE_READY = Boolean(SUPABASE_URL && SUPABASE_ANON_KEY);

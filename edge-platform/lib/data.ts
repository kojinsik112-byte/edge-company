import { createClient } from "./supabase/server";
import type { CaseRow, ReviewRow, FaqRow, YoutubeRow, ProductRow } from "./types";
import type { Region, Category } from "./constants";

// 모든 fetch 는 Supabase 미연결/에러 시 빈 배열을 반환해 사이트가 죽지 않게 한다.

export async function getCases(opts?: {
  region?: Region;
  category?: Category;
  tag?: string;
  q?: string;
  limit?: number;
  includeUnpublished?: boolean;
}): Promise<CaseRow[]> {
  const supabase = await createClient();
  if (!supabase) return [];
  try {
    let query = supabase
      .from("cases")
      .select("*")
      .order("created_at", { ascending: false });
    if (!opts?.includeUnpublished) query = query.eq("published", true);
    if (opts?.region) query = query.eq("region", opts.region);
    if (opts?.category) query = query.eq("category", opts.category);
    if (opts?.tag) query = query.contains("tags", [opts.tag]);
    if (opts?.q) query = query.ilike("title", `%${opts.q}%`);
    if (opts?.limit) query = query.limit(opts.limit);
    const { data, error } = await query;
    if (error) return [];
    return (data as CaseRow[]) ?? [];
  } catch {
    return [];
  }
}

export async function getCaseBySlug(slug: string): Promise<CaseRow | null> {
  const supabase = await createClient();
  if (!supabase) return null;
  // 한글 슬러그가 인코딩/디코딩 어느 상태로 들어와도 매칭되도록 후보를 모두 시도
  const candidates = new Set<string>([slug]);
  try { candidates.add(decodeURIComponent(slug)); } catch {}
  try { candidates.add(encodeURIComponent(slug)); } catch {}
  try {
    for (const s of candidates) {
      const { data, error } = await supabase
        .from("cases")
        .select("*")
        .eq("slug", s)
        .eq("published", true)
        .limit(1);
      if (error) continue;
      if (data && data[0]) return data[0] as CaseRow;
    }
    return null;
  } catch {
    return null;
  }
}

export async function getCaseById(id: string): Promise<CaseRow | null> {
  const supabase = await createClient();
  if (!supabase) return null;
  try {
    const { data } = await supabase
      .from("cases")
      .select("*")
      .eq("id", id)
      .maybeSingle();
    return (data as CaseRow) ?? null;
  } catch {
    return null;
  }
}

export async function getReviews(limit?: number): Promise<ReviewRow[]> {
  const supabase = await createClient();
  if (!supabase) return [];
  try {
    let q = supabase
      .from("reviews")
      .select("*")
      .eq("published", true)
      .order("created_at", { ascending: false });
    if (limit) q = q.limit(limit);
    const { data } = await q;
    return (data as ReviewRow[]) ?? [];
  } catch {
    return [];
  }
}

export async function getFaqs(): Promise<FaqRow[]> {
  const supabase = await createClient();
  if (!supabase) return [];
  try {
    const { data } = await supabase
      .from("faq")
      .select("*")
      .eq("published", true)
      .order("sort", { ascending: true });
    return (data as FaqRow[]) ?? [];
  } catch {
    return [];
  }
}

export async function getProducts(): Promise<ProductRow[]> {
  const supabase = await createClient();
  if (!supabase) return [];
  try {
    const { data } = await supabase
      .from("products")
      .select("*")
      .eq("published", true)
      .order("sort", { ascending: true });
    return (data as ProductRow[]) ?? [];
  } catch {
    return [];
  }
}

export async function getProductById(id: string): Promise<ProductRow | null> {
  const supabase = await createClient();
  if (!supabase) return null;
  try {
    const { data } = await supabase
      .from("products")
      .select("*")
      .eq("id", id)
      .maybeSingle();
    return (data as ProductRow) ?? null;
  } catch {
    return null;
  }
}

export async function getYoutube(): Promise<YoutubeRow[]> {
  const supabase = await createClient();
  if (!supabase) return [];
  try {
    const { data } = await supabase
      .from("youtube")
      .select("*")
      .eq("published", true)
      .order("sort", { ascending: true });
    return (data as YoutubeRow[]) ?? [];
  } catch {
    return [];
  }
}

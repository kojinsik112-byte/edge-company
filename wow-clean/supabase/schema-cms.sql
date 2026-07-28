-- =====================================================================
--  와우클린 CMS 확장 — settings / popups / inquiries
--  Supabase > SQL Editor 에 붙여넣고 [Run] (schema.sql 실행 후 1회)
-- =====================================================================

-- 1) 사이트 설정 (key/value) — 배너·회사소개·시공현장·카테고리·공지바·기본정보·SEO ----
create table if not exists public.settings (
  key text primary key,
  value jsonb not null default '{}'::jsonb,
  updated_at timestamptz not null default now()
);
alter table public.settings enable row level security;
drop policy if exists settings_public_read on public.settings;
create policy settings_public_read on public.settings for select using (true);
drop policy if exists settings_admin_all on public.settings;
create policy settings_admin_all on public.settings for all to authenticated using (true) with check (true);

-- 기본값 시드 (관리자에서 자유롭게 수정)
insert into public.settings (key, value) values
('site', '{
  "phone":"1668-8982","phoneRep":"1668-8982",
  "address":"전국 24시간 출동 서비스",
  "kakao":"","instagram":"https://www.instagram.com/dadongjib","youtube":"","blog":"https://blog.naver.com/ljs4510",
  "bizName":"와우클린 하수구변기막힘설비","ceo":"안영란","bizNo":"575-41-01087"
}'),
('notice', '{"enabled":false,"text":"전국 24시간 긴급 출동 접수 중","link":"/contact"}'),
('hero', '{
  "image":"/img/hero.svg",
  "eyebrow":"전국 24시간 긴급 출동 접수 중",
  "title":"막힌 곳은 뚫고,\n깨끗함은 남깁니다",
  "subline":"하수구막힘 · 변기막힘 · 배관청소 전문",
  "lead":"원인을 확인한 뒤 시공 전에 비용을 확정하고, 작업이 끝나면 사진으로 남기는 와우클린입니다."
}'),
('company', '{"image":"/img/hero.svg","title":"와우클린 소개","body":"하수구·변기 막힘 뚫음, 고압 배관청소, 누수탐지를 전문으로 하는 전국 24시간 출동 시공 기업입니다."}'),
('showroom', '{"image":"/img/cat-pipe.svg","title":"와우클린 시공 현장","body":"가정 욕실부터 상가 주방, 건물 공용 배관까지 — 와우클린이 실제로 해결한 현장들입니다.","hours":"연중무휴 24시간 접수 · 야간 긴급 출동 가능"}'),
('categories', '{"하수구막힘":"/img/cat-drain.svg","변기막힘":"/img/cat-toilet.svg","배관청소":"/img/cat-pipe.svg","수전교체":"/img/svc-faucet.svg","내시경검사":"/img/svc-scope.svg","관로탐지":"/img/svc-detect.svg","누수탐지":"/img/svc-leak.svg"}'),
('seo', '{"home":{"title":"","description":"","keywords":"","og":""}}')
on conflict (key) do nothing;

-- 2) 팝업 (이벤트/공지) -----------------------------------------------
create table if not exists public.popups (
  id uuid primary key default gen_random_uuid(),
  created_at timestamptz not null default now(),
  title text not null default '',
  image text,
  link text,
  enabled boolean not null default true,
  start_at date,
  end_at date,
  sort int not null default 0
);
alter table public.popups enable row level security;
drop policy if exists popups_public_read on public.popups;
create policy popups_public_read on public.popups for select using (enabled = true);
drop policy if exists popups_admin_all on public.popups;
create policy popups_admin_all on public.popups for all to authenticated using (true) with check (true);

-- 3) 상담문의 (방문자 접수 → 관리자 확인) -----------------------------
create table if not exists public.inquiries (
  id uuid primary key default gen_random_uuid(),
  created_at timestamptz not null default now(),
  name text not null default '',
  phone text not null default '',
  region text,
  category text,
  message text not null default '',
  status text not null default '신규' check (status in ('신규','상담중','완료'))
);
alter table public.inquiries enable row level security;
-- 누구나 문의 접수(insert)는 가능, 읽기/수정/삭제는 관리자만 (개인정보 보호)
drop policy if exists inquiries_public_insert on public.inquiries;
create policy inquiries_public_insert on public.inquiries for insert to anon, authenticated with check (true);
drop policy if exists inquiries_admin_read on public.inquiries;
create policy inquiries_admin_read on public.inquiries for select to authenticated using (true);
drop policy if exists inquiries_admin_update on public.inquiries;
create policy inquiries_admin_update on public.inquiries for update to authenticated using (true);
drop policy if exists inquiries_admin_delete on public.inquiries;
create policy inquiries_admin_delete on public.inquiries for delete to authenticated using (true);

-- 4) 정렬 컬럼 추가 (후기·시공사례) -----------------------------------
alter table public.reviews add column if not exists sort int not null default 0;
alter table public.cases   add column if not exists sort int not null default 0;

-- 5) 팝업 본문(메모/공지형 텍스트) 컬럼 추가 --------------------------
alter table public.popups add column if not exists content text;

-- 5-1) 후기 아파트명 컬럼 추가 ----------------------------------------
alter table public.reviews add column if not exists apartment text;

-- 5-2) 후기 제목(한 줄 헤드라인) 컬럼 추가 ---------------------------
alter table public.reviews add column if not exists title text;

-- 6) 서비스 안내 (하수구막힘·변기막힘·배관청소 등) -------------------------
create table if not exists public.products (
  id uuid primary key default gen_random_uuid(),
  created_at timestamptz not null default now(),
  name text not null default '',
  category text not null default '',
  image text,
  body text not null default '',
  sort int not null default 0,
  published boolean not null default true
);
alter table public.products enable row level security;
drop policy if exists products_public_read on public.products;
create policy products_public_read on public.products for select using (published = true);
drop policy if exists products_admin_all on public.products;
create policy products_admin_all on public.products for all to authenticated using (true) with check (true);

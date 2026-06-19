-- =====================================================================
--  엣지리브커튼 울산본점 CMS 확장 — settings / popups / inquiries
--  Supabase > SQL Editor 에 붙여넣고 [Run] (schema.sql 실행 후 1회)
-- =====================================================================

-- 1) 사이트 설정 (key/value) — 배너·회사소개·쇼룸·카테고리·공지바·기본정보·SEO ----
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
  "phone":"010-4900-6107","phoneRep":"1533-3210",
  "address":"울산광역시",
  "kakao":"","instagram":"","youtube":"","blog":"",
  "bizName":"㈜엣지컴퍼니","ceo":"고진식","bizNo":"508-81-42798"
}'),
('notice', '{"enabled":false,"text":"울산 커튼 쇼룸 예약 상담 진행중","link":"/contact"}'),
('hero', '{
  "image":"/img/curtain.webp",
  "eyebrow":"울산 · 양산 · 부산 · 경주",
  "title":"공간의 분위기를 완성하는\n맞춤 커튼 · 블라인드",
  "subline":"커튼 · 블라인드 · 전동커튼 전문 쇼룸",
  "lead":"직접 보고, 만져보고, 비교한 뒤 선택하는 엣지리브커튼 울산본점입니다."
}'),
('company', '{"image":"/img/sofa.webp","title":"엣지리브커튼 소개","body":"정확한 실측과 맞춤 제작으로 시공하는 울산 커튼·블라인드 전문 쇼룸입니다."}'),
('showroom', '{"image":"/img/curtain.webp","title":"울산 커튼·블라인드 쇼룸에서 직접 골라보세요","body":"원단의 색감과 질감, 블라인드의 라인은 사진만으로 알 수 없습니다. 직접 만져보고 비교한 뒤 우리 집 창에 맞는 조합을 찾으실 수 있도록 쇼룸을 운영합니다.","hours":"방문 전 연락 주시면 대기 없이 안내해 드립니다"}'),
('categories', '{"커튼":"/img/curtain.webp","블라인드":"/img/indirect.webp","전동커튼":"/img/sofa.webp"}'),
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

-- 6) 제품 소개 (커튼·블라인드·전동커튼 등) ----------------------------
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

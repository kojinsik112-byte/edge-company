-- =====================================================================
--  와우클린 시공사례 플랫폼 — Supabase 스키마
--  Supabase 대시보드 > SQL Editor 에 붙여넣고 [Run] 하세요. (한 번만)
-- =====================================================================

-- 1) 테이블 ------------------------------------------------------------
create table if not exists public.cases (
  id uuid primary key default gen_random_uuid(),
  created_at timestamptz not null default now(),
  updated_at timestamptz,
  title text not null,
  slug text not null unique,
  region text not null check (region in ('서울','경기','인천','부산','대구','울산','대전','광주')),
  category text not null check (category in ('하수구막힘','변기막힘','배관청소')),
  apartment text not null default '',
  cover text,
  images jsonb not null default '[]'::jsonb,
  body text not null default '',
  tags jsonb not null default '[]'::jsonb,
  seo_title text,
  seo_description text,
  published boolean not null default true
);
create index if not exists cases_region_idx   on public.cases(region);
create index if not exists cases_category_idx on public.cases(category);
create index if not exists cases_pub_idx      on public.cases(published, created_at desc);

create table if not exists public.reviews (
  id uuid primary key default gen_random_uuid(),
  created_at timestamptz not null default now(),
  name text not null,
  region text check (region in ('서울','경기','인천','부산','대구','울산','대전','광주')),
  rating int not null default 5 check (rating between 1 and 5),
  content text not null default '',
  image text,
  published boolean not null default true
);

create table if not exists public.faq (
  id uuid primary key default gen_random_uuid(),
  created_at timestamptz not null default now(),
  question text not null,
  answer text not null default '',
  sort int not null default 0,
  published boolean not null default true
);

create table if not exists public.youtube (
  id uuid primary key default gen_random_uuid(),
  created_at timestamptz not null default now(),
  video_id text not null,
  title text not null default '',
  views text,
  sort int not null default 0,
  published boolean not null default true
);

-- updated_at 자동 갱신
create or replace function public.touch_updated_at()
returns trigger language plpgsql as $$
begin new.updated_at = now(); return new; end; $$;
drop trigger if exists cases_touch on public.cases;
create trigger cases_touch before update on public.cases
  for each row execute function public.touch_updated_at();

-- 2) RLS (행 보안) -----------------------------------------------------
alter table public.cases   enable row level security;
alter table public.reviews enable row level security;
alter table public.faq     enable row level security;
alter table public.youtube enable row level security;

-- 공개(published) 행은 누구나 읽기
drop policy if exists cases_public_read on public.cases;
create policy cases_public_read on public.cases
  for select using (published = true);
drop policy if exists reviews_public_read on public.reviews;
create policy reviews_public_read on public.reviews
  for select using (published = true);
drop policy if exists faq_public_read on public.faq;
create policy faq_public_read on public.faq
  for select using (published = true);
drop policy if exists youtube_public_read on public.youtube;
create policy youtube_public_read on public.youtube
  for select using (published = true);

-- 로그인한 관리자는 모든 작업(읽기/쓰기/수정/삭제) 가능
drop policy if exists cases_admin_all on public.cases;
create policy cases_admin_all on public.cases
  for all to authenticated using (true) with check (true);
drop policy if exists reviews_admin_all on public.reviews;
create policy reviews_admin_all on public.reviews
  for all to authenticated using (true) with check (true);
drop policy if exists faq_admin_all on public.faq;
create policy faq_admin_all on public.faq
  for all to authenticated using (true) with check (true);
drop policy if exists youtube_admin_all on public.youtube;
create policy youtube_admin_all on public.youtube
  for all to authenticated using (true) with check (true);

-- 3) 스토리지 (이미지 업로드 버킷) -------------------------------------
insert into storage.buckets (id, name, public)
values ('media', 'media', true)
on conflict (id) do nothing;

drop policy if exists media_public_read on storage.objects;
create policy media_public_read on storage.objects
  for select using (bucket_id = 'media');
drop policy if exists media_admin_write on storage.objects;
create policy media_admin_write on storage.objects
  for insert to authenticated with check (bucket_id = 'media');
drop policy if exists media_admin_update on storage.objects;
create policy media_admin_update on storage.objects
  for update to authenticated using (bucket_id = 'media');
drop policy if exists media_admin_delete on storage.objects;
create policy media_admin_delete on storage.objects
  for delete to authenticated using (bucket_id = 'media');

-- 4) 시드 데이터 (예시 — 관리자에서 자유롭게 수정/삭제) ----------------
insert into public.faq (question, answer, sort) values
  ('정말 24시간 접수되나요?', '네, 접수는 연중무휴 24시간 가능합니다. 야간·새벽 긴급 상황은 전화 접수를 이용하시면 가장 빠르게 안내해 드립니다.', 1),
  ('비용은 언제 알 수 있나요?', '전화·상담 시 증상과 위치를 바탕으로 예상 범위를 먼저 안내합니다. 현장 확인 후 작업 전에 최종 금액을 확정하며, 동의하신 뒤에만 시공을 시작합니다.', 2),
  ('결제는 어떻게 하나요? 증빙 발행되나요?', '현금·카드·계좌이체 모두 가능합니다. 현금영수증, 세금계산서 등 정식 증빙도 발행해 드립니다. 사업자 정식 등록 업체입니다.', 3),
  ('야간·주말·공휴일에도 오나요?', '접수는 연중무휴 24시간 가능합니다. 야간·주말 긴급 상황은 전화로 접수하시면 가장 빠르게 안내해 드립니다. 지역·시간대에 따라 방문 시간은 달라질 수 있습니다.', 4)
on conflict do nothing;

insert into public.reviews (name, region, rating, content) values
  ('예시 고객', '서울', 5, '[예시] 전화하니까 바로 근처 기사님 배정해주셔서 금방 오셨어요. 응대도 친절하고 일 처리도 깔끔합니다.'),
  ('예시 고객', '부산', 5, '[예시] 작업 전에 비용을 확정해서 알려주시니 안심하고 맡길 수 있었습니다.')
on conflict do nothing;
-- ⚠️ 위 후기는 예시입니다. 실제 고객 후기로 교체하세요 (표시광고법: 허위 후기 금지).

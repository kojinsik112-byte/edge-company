-- =====================================================================
--  엣지컴퍼니 시공사례 플랫폼 — Supabase 스키마
--  Supabase 대시보드 > SQL Editor 에 붙여넣고 [Run] 하세요. (한 번만)
-- =====================================================================

-- 1) 테이블 ------------------------------------------------------------
create table if not exists public.cases (
  id uuid primary key default gen_random_uuid(),
  created_at timestamptz not null default now(),
  updated_at timestamptz,
  title text not null,
  slug text not null unique,
  region text not null check (region in ('울산','부산','포항','경주')),
  category text not null check (category in ('실링팬','간접조명','스마트조명')),
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
  region text check (region in ('울산','부산','포항','경주')),
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
  ('실링팬, 머리에 부딪히지 않나요?', '천장고와 날개 위치를 고려해 안전 높이로 설치합니다. 14.5cm 슬림 보디는 저천장에도 부담이 적어 일반 거실에서 머리에 닿지 않습니다. 현장 실측 시 정확한 높이를 안내드립니다.', 1),
  ('전기요금이 많이 나오나요?', 'BLDC(DC) 모터 실링팬은 소비전력이 낮아 24시간 가동해도 전기요금 부담이 크지 않습니다. 형광등 대비 LED 조명까지 함께 교체하면 오히려 절감되는 경우가 많습니다.', 2),
  ('간접조명, 생각보다 어둡지 않나요?', '간접조명은 분위기용이며, 메인 조명·다운라이트와 함께 설계해 밝기를 확보합니다. 색온도(전구색/주백색)와 디밍을 조합하면 낮에는 밝게, 밤에는 은은하게 사용할 수 있습니다.', 3),
  ('스마트조명은 어떻게 제어하나요?', '전용 앱과 리모컨, 음성(스마트스피커 연동)으로 제어합니다. 실링팬·전동커튼·스위치까지 하나의 앱으로 묶어 통합 제어가 가능합니다.', 4)
on conflict do nothing;

insert into public.reviews (name, region, rating, content) values
  ('문수로 롯데캐슬', '울산', 5, '실링팬 설치 후 거실 분위기가 완전히 달라졌습니다.'),
  ('센트럴 아이파크', '부산', 5, '간접조명 색감이 정말 만족스럽습니다.')
on conflict do nothing;
-- ⚠️ 위 후기는 예시입니다. 실제 고객 후기로 교체하세요 (표시광고법: 허위 후기 금지).

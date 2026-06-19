-- =====================================================================
--  엣지리브커튼 울산본점 — 시공사례 플랫폼 Supabase 스키마
--  Supabase 대시보드 > SQL Editor 에 붙여넣고 [Run] 하세요. (한 번만)
-- =====================================================================

-- 1) 테이블 ------------------------------------------------------------
create table if not exists public.cases (
  id uuid primary key default gen_random_uuid(),
  created_at timestamptz not null default now(),
  updated_at timestamptz,
  title text not null,
  slug text not null unique,
  region text not null check (region in ('울산','양산','부산','경주')),
  category text not null check (category in ('커튼','블라인드','전동커튼')),
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
  region text check (region in ('울산','양산','부산','경주')),
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
  ('실측은 어떻게 진행되나요?', '전화·카톡으로 상담 후 원하시는 날짜에 방문하여 창 사이즈·주름비·레일 위치를 정확히 측정합니다. 울산·양산·부산·경주는 무료 방문 실측이며, 실측 결과에 맞춰 정확한 견적을 드립니다.', 1),
  ('커튼과 블라인드 중 무엇이 좋나요?', '공간과 목적에 따라 다릅니다. 침실·거실 무드와 단열엔 커튼, 깔끔한 라인과 정밀한 빛 조절엔 블라인드가 강점입니다. 쇼룸에서 직접 비교해 보고 추천해 드립니다.', 2),
  ('암막 커튼은 빛이 완전히 차단되나요?', '암막 원단과 레일·주름 구성에 따라 차광률이 달라집니다. 침실 숙면을 원하시면 고차광 원단과 측면 빛샘을 줄이는 시공으로 최대한 어둡게 맞춰 드립니다.', 3),
  ('전동커튼은 어떻게 작동하나요?', '리모컨·전용 앱·음성(스마트스피커 연동)으로 여닫을 수 있습니다. 큰 창·높은 창에 특히 편리하며, 기존 콘센트 위치에 맞춰 깔끔하게 설치합니다.', 4)
on conflict do nothing;

insert into public.reviews (name, region, rating, content) values
  ('문수로 롯데캐슬', '울산', 5, '암막 커튼 설치 후 거실 분위기가 완전히 달라졌습니다.'),
  ('센트럴 아이파크', '부산', 5, '쇼룸에서 직접 고른 원단 색감이 정말 만족스럽습니다.')
on conflict do nothing;
-- ⚠️ 위 후기는 예시입니다. 실제 고객 후기로 교체하세요 (표시광고법: 허위 후기 금지).

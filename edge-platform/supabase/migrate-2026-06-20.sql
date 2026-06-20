-- =====================================================================
--  엣지컴퍼니 마이그레이션 2026-06-20
--  Supabase 대시보드 > SQL Editor 에 붙여넣고 [Run] 하세요. (한 번만, 안전 — 여러 번 실행해도 OK)
--  해결: ① 후기 등록 안 되던 버그  ② 카테고리 '스마트조명' → '센서조명'
-- =====================================================================

-- 1) 후기(reviews) 누락 컬럼 보정 — 후기 등록이 조용히 실패하던 원인 -------
alter table public.reviews add column if not exists title text;       -- 한 줄 제목
alter table public.reviews add column if not exists apartment text;    -- 아파트명
alter table public.reviews add column if not exists sort int not null default 0;

-- 2) 시공사례(cases) 카테고리 '스마트조명' → '센서조명' --------------------
--    (a) 기존 CHECK 제약 제거
alter table public.cases drop constraint if exists cases_category_check;
--    (b) 기존에 '스마트조명'으로 저장된 사례를 '센서조명'으로 이전
update public.cases set category = '센서조명' where category = '스마트조명';
--    (c) 새 CHECK 제약 추가
alter table public.cases add constraint cases_category_check
  check (category in ('실링팬','간접조명','센서조명'));

-- 3) 카테고리 대표이미지 설정 키 '스마트조명' → '센서조명' ------------------
update public.settings
set value = (value - '스마트조명')
            || jsonb_build_object('센서조명', coalesce(value->'스마트조명', '"/img/curtain.webp"'::jsonb))
where key = 'categories' and value ? '스마트조명';

-- 끝. (제품·면허·전국지사·협력사 등 신규 섹션은 코드 기본값으로 자동 동작하며,
--      관리자 '사이트 설정'에서 저장하면 settings 테이블에 자동 누적됩니다.)

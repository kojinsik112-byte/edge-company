-- =====================================================================
--  엣지컴퍼니 플랫폼 — 2026-06 업그레이드 마이그레이션
--  Supabase 대시보드 > SQL Editor 에 붙여넣고 [Run] 하세요. (한 번만)
--  (안전: 이미 적용된 항목은 자동으로 건너뜁니다)
-- =====================================================================

-- 1) 제품: 상세 사진 여러 장(images) 컬럼 추가 -----------------------
alter table public.products
  add column if not exists images jsonb not null default '[]'::jsonb;

-- 2) 시공사례 카테고리: '센서조명' → '기타' 변경 ---------------------
--    기존 CHECK 제약 해제 → 데이터 변경 → 새 제약 추가
alter table public.cases drop constraint if exists cases_category_check;
update public.cases set category = '기타' where category = '센서조명';
alter table public.cases
  add constraint cases_category_check check (category in ('실링팬','간접조명','기타'));

-- 끝. (회사소개·시공절차 등 설정값은 settings 테이블 JSON 으로 저장되어
--      별도 스키마 변경이 필요 없습니다 — 관리자 페이지에서 바로 편집됩니다.)

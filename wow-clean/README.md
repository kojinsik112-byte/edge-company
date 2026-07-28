# 와우클린 — 시공사례 SEO 플랫폼

전국 24시간 **하수구막힘·변기막힘·배관청소 전문** 사이트.
관리자 페이지에서 코드 수정 없이 시공사례를 무한 등록할 수 있는 **Next.js + Supabase + Vercel** SEO 플랫폼.
(조명 사이트 `edge-platform`·커튼 사이트 `edge-curtain`의 형제 프로젝트 — 독립 Supabase·Vercel·도메인으로 운영)

- 프레임워크: **Next.js 16** (App Router, SSR → 네이버 SEO)
- DB·인증·이미지저장: **Supabase** (Postgres + Auth + Storage)
- 배포: **Vercel**
- 디자인: Pretendard, 클린화이트 + 딥네이비 + 클린블루(#1f83e0), 모바일 우선
- 브랜드: 와우클린 하수구변기막힘설비 · 대표 안영란 · 사업자 575-41-01087 · 대표번호 **1668-8982**
- 슬로건: **"막힌 곳은 뚫고, 깨끗함은 남깁니다"**

---

## 1. 로컬 실행

```bash
cd wow-clean
cp .env.local.example .env.local   # 값 채우기 (아래 2번)
npm install
npm run dev                        # http://localhost:3000
```

Supabase 키가 없어도 디자인/페이지는 기본 일러스트로 동작합니다(시공사례·후기 등 DB 데이터만 빈 상태).

## 2. Supabase 연결 (한 번만 — 반드시 **새 프로젝트**로, 엣지 프로젝트 재사용 금지)

1. <https://supabase.com> 에서 프로젝트 생성
2. **SQL Editor** 에 [`supabase/schema.sql`](./supabase/schema.sql) → [`supabase/schema-cms.sql`](./supabase/schema-cms.sql) 순서로 붙여넣고 **Run**
   (선택) [`supabase/seed-demo.sql`](./supabase/seed-demo.sql) 로 샘플 사례·후기 채우기
3. **Project Settings → API** 에서 값 복사 → `.env.local`
   - `NEXT_PUBLIC_SUPABASE_URL`
   - `NEXT_PUBLIC_SUPABASE_ANON_KEY`
4. **Authentication → Users → Add user** 로 관리자 계정(이메일/비밀번호) 생성
   → 이 계정으로 `/admin/login` 로그인

## 3. 관리자 사용 (코드 수정 없음)

- `/admin/login` 로그인 → `/admin` 대시보드
- **+ 새 시공사례**: 제목·지역·카테고리(하수구막힘/변기막힘/배관청소)·현장명·대표이미지·상세사진·본문·태그·공개여부
- 사진은 업로드 시 **자동 WebP 변환·압축**(모바일 사진 회전 자동 보정) 후 Supabase Storage 저장
- 실제 시공 현장 사진이 쌓일수록 기본 일러스트를 대체 → 사이트 신뢰도 상승
- 등록 즉시 공개 사이트(홈·시공사례·지역 페이지·sitemap)에 자동 반영

## 4. Vercel 배포

1. 이 폴더를 GitHub 저장소에 push
2. <https://vercel.com> → New Project → 저장소 선택 (Root Directory = `wow-clean`)
3. **Environment Variables** 에 `.env.local` 값 + `NEXT_PUBLIC_SITE_URL`(배포 도메인) 입력
4. Deploy

## 5. 네이버 SEO

- **서치어드바이저**(searchadvisor.naver.com) 사이트 등록 → 소유확인 메타값을
  `.env.local` / Vercel 의 `NEXT_PUBLIC_NAVER_VERIFICATION` 에 입력
- 사이트맵 제출: `https://<도메인>/sitemap.xml` (시공사례·지역페이지 자동 포함)
- robots: `https://<도메인>/robots.txt` (네이버 Yeti 허용, /admin 차단)
- 지역×카테고리 24개 SEO 페이지 자동 생성: `/area/seoul-drain`, `/area/busan-toilet` 등
  (지역 8: 서울·경기·인천·부산·대구·울산·대전·광주 × 카테고리 3: drain·toilet·pipe-cleaning)

## 6. 환경변수

| 변수 | 필수 | 설명 |
|---|---|---|
| `NEXT_PUBLIC_SUPABASE_URL` | ✅ | Supabase 프로젝트 URL |
| `NEXT_PUBLIC_SUPABASE_ANON_KEY` | ✅ | Supabase anon public key |
| `NEXT_PUBLIC_SITE_URL` | 권장 | 배포 도메인 (sitemap/canonical) |
| `NEXT_PUBLIC_KAKAO_URL` | 선택 | 카카오톡 채널 채팅 URL (없으면 문자 폴백) |
| `NEXT_PUBLIC_NAVER_VERIFICATION` | 선택 | 네이버 서치어드바이저 소유확인 값 |

## 구조

```
app/            홈·cases·area(지역SEO)·reviews·faq·youtube·showroom(시공현장)·contact·admin
  sitemap.ts    sitemap.xml 자동
  robots.ts     robots.txt
components/      Header·Footer·MobileBar·CaseCard·admin/CaseForm 등
lib/             supabase 클라이언트·constants·types·seo·data·upload
supabase/        schema.sql(DB·RLS·스토리지) · schema-cms.sql(설정·팝업·문의·제품) · seed-demo.sql
public/img/      기본 일러스트 (hero.svg · cat-drain.svg · cat-toilet.svg · cat-pipe.svg)
```

## SNS 연동 (기본값에 이미 반영)

- 네이버 블로그: <https://blog.naver.com/ljs4510>
- 인스타그램: <https://www.instagram.com/dadongjib>

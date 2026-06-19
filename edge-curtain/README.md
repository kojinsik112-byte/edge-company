# 엣지리브커튼 울산본점 — 시공사례 SEO 플랫폼

울산·양산·부산·경주 **커튼·블라인드·전동커튼 전문 쇼룸** 사이트.
관리자 페이지에서 코드 수정 없이 시공사례를 무한 등록할 수 있는 **Next.js + Supabase + Vercel** SEO 플랫폼.
(조명 사이트 `edge-platform`의 형제 프로젝트 — 독립 Supabase·Vercel·도메인으로 운영)

- 프레임워크: **Next.js 16** (App Router, SSR → 네이버 SEO)
- DB·인증·이미지저장: **Supabase** (Postgres + Auth + Storage)
- 배포: **Vercel**
- 디자인: Pretendard, 웜화이트 + 딥네이비 + 샴페인골드, 모바일 우선

---

## 1. 로컬 실행

```bash
cd edge-platform
cp .env.local.example .env.local   # 값 채우기 (아래 2번)
npm install
npm run dev                        # http://localhost:3000
```

Supabase 키가 없어도 디자인/페이지는 폴백 이미지로 동작합니다(시공사례·후기 등 DB 데이터만 빈 상태).

## 2. Supabase 연결 (한 번만)

1. <https://supabase.com> 에서 프로젝트 생성
2. **SQL Editor** 에 [`supabase/schema.sql`](./supabase/schema.sql) 전체를 붙여넣고 **Run** → 테이블·RLS·`media` 스토리지 버킷·예시 데이터 생성
3. **Project Settings → API** 에서 값 복사 → `.env.local`
   - `NEXT_PUBLIC_SUPABASE_URL`
   - `NEXT_PUBLIC_SUPABASE_ANON_KEY`
4. **Authentication → Users → Add user** 로 관리자 계정(이메일/비밀번호) 생성
   → 이 계정으로 `/admin/login` 로그인

## 3. 관리자 사용 (코드 수정 없음)

- `/admin/login` 로그인 → `/admin` 대시보드
- **+ 새 시공사례**: 제목·지역·카테고리·아파트명·대표이미지·상세사진(여러 장)·본문·태그·공개여부
- 사진은 업로드 시 **자동 WebP 변환·압축**(모바일 사진 회전 자동 보정) 후 Supabase Storage 저장
- 수정·삭제·비공개 토글 가능. **모바일 브라우저에서도 동일하게 업로드** 가능
- 등록 즉시 공개 사이트(홈·시공사례·지역 페이지·sitemap)에 자동 반영

## 4. Vercel 배포

1. 이 폴더를 GitHub 저장소에 push
2. <https://vercel.com> → New Project → 저장소 선택 (Root Directory = `edge-platform`)
3. **Environment Variables** 에 `.env.local` 값 + `NEXT_PUBLIC_SITE_URL`(배포 도메인) 입력
4. Deploy

## 5. 네이버 SEO

- **서치어드바이저**(searchadvisor.naver.com) 사이트 등록 → 소유확인 메타값을
  `.env.local` / Vercel 의 `NEXT_PUBLIC_NAVER_VERIFICATION` 에 입력
- 사이트맵 제출: `https://<도메인>/sitemap.xml` (시공사례·지역페이지 자동 포함)
- robots: `https://<도메인>/robots.txt` (네이버 Yeti 허용, /admin 차단)
- 지역×카테고리 12개 SEO 페이지 자동 생성: `/area/ulsan-ceiling-fan` 등

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
app/            홈·cases·area(지역SEO)·reviews·faq·youtube·showroom·contact·admin
  sitemap.ts    sitemap.xml 자동
  robots.ts     robots.txt
components/      Header·Footer·MobileBar·CaseCard·admin/CaseForm 등
lib/             supabase 클라이언트·constants·types·seo·data·upload
supabase/schema.sql   DB·RLS·스토리지·시드
public/img/      폴백 거실 이미지(webp)
```

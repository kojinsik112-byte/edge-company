# 엣지컴퍼니 · 클린벤더 스크리닝

입주박람회 **업체 평판 검증** 웹앱. 업체명을 넣으면 **네이버 카페·블로그**에서 그 업체의
후기·불만·하자·분쟁 정황을 실시간 검색해 **신호등(안전/주의/위험)**으로 보여준다.
→ 입주박람회 PT에서 **"우리는 이렇게 업체를 검증합니다"** 라이브 데모용.

## 구조
```
index.html                     프론트엔드 (발표용 디자인: 네이비/골드)
netlify/functions/screen.js    서버리스 함수 (네이버 API 호출, 키 숨김)
netlify.toml                   배포 설정 (/api/screen → 함수)
```
- 프론트 → `/api/screen?q=업체명` → 서버리스 함수가 네이버 검색 API 호출 → 결과 JSON 반환.
- 🔐 **API 키는 코드/깃에 없음.** Netlify 환경변수로만 주입한다.

## 배포 (회장님, 1회)
1. https://app.netlify.com 로그인 → **Add new site → Import from Git** (이 저장소) 또는
   `business-ops/vendor-screen/` 폴더를 **드래그&드롭(수동 배포)**.
   - Base directory: `business-ops/vendor-screen`
   - Publish directory: `business-ops/vendor-screen` (또는 `.`)
   - Functions directory: 자동(`netlify/functions`)
2. **Site configuration → Environment variables** 에 2개 추가:
   - `NAVER_CLIENT_ID` = (네이버 개발자센터 검색 API 키)
   - `NAVER_CLIENT_SECRET` = (시크릿)
3. **Deploy**. 발급된 주소(예: `클린벤더.netlify.app`) 접속 → 업체명 입력 → 검증.
   - 도메인 별칭은 Netlify → Domain settings에서 변경 가능.

> 키 값은 `.env`/로컬에만. 절대 코드·깃에 커밋하지 않는다(보안규칙·key_watch).

## 로컬 테스트 (선택)
```bash
npm i -g netlify-cli
cd business-ops/vendor-screen
NAVER_CLIENT_ID=xxx NAVER_CLIENT_SECRET=yyy netlify dev
# http://localhost:8888 접속
```

## 작동·한계 (솔직)
- ✅ 네이버 **검색 노출 카페·블로그 글**을 가져온다(비공개 카페라도 검색 노출 설정된 글은 잡힘).
- ⚠️ **동명 업체 노이즈**: 흔한 이름은 무관 업체 글이 섞일 수 있음 → 업체명 미포함 글은 자동 제외하지만 완벽치 않음.
- ⚠️ **검색 비노출 글**(카페가 검색 차단)은 안 잡힘 → 결과 없음 = 안전 보증 아님.
- ⚖️ **명예훼손 주의**: 무대에서 실제 경쟁업체명을 검색해 공개 저격하지 말 것. **시스템 작동 시연**으로만(중립 예시·자사 협력사).
- 최종 선정 판단은 **담당자 교차검증** (소명 단계) 후.

## 검증 시스템 전체 흐름 (PT 자료)
`business-ops/movein/일광노르웨이숲_주관사_종합자료.md` §10(업체 선별 기준) 참조.
본 앱 = 그 6단 게이트 중 **2단계 "평판검색"**의 실제 구현체.

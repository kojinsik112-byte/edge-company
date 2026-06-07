# ACRO 브랜드 웹사이트

엣지컴퍼니 ACRO(아크로) — 블루투스 전용 스마트홈 브랜드 사이트.
단일 페이지 정적 사이트(HTML/CSS/JS)라 빌드 도구 없이 바로 열고 배포할 수 있습니다.

## 구성
```
acro-site/
├─ index.html          # 전체 페이지 구조
├─ styles.css          # 디자인 (흰 배경 + 네이비/블루투스 블루/골드, Pretendard)
├─ hero.js             # 코드로 생성하는 히어로 모션 + 푸터 시그널 웨이브 (Canvas)
├─ script.js           # 네비/모바일메뉴/유튜브 임베드/등장 애니메이션
└─ assets/
   └─ hero-poster.svg  # reduced-motion / 구형 브라우저용 히어로 폴백 이미지
```

## 히어로 영상 (코드 생성)
히어로 배경은 **별도 mp4 파일 없이 `hero.js` 의 Canvas 애니메이션**으로 그려집니다.
- 블루투스 신호 링 + 스마트홈 기기 연결 네트워크(별자리) 모션
- 해상도 무관(4K도 선명) · 완벽 루프 · 파일 무게 0
- `prefers-reduced-motion` 사용자는 자동으로 정적 포스터(`hero-poster.svg`)만 표시
- 푸터에도 동일 엔진으로 흐르는 시그널 웨이브가 깔립니다.

> 실제 촬영 영상을 쓰고 싶어지면 hero 섹션의 `<canvas>` 를 `<video>` 로 교체하면 됩니다.

## 로컬에서 보기
파일을 더블클릭해 열어도 되지만, 영상/임베드 때문에 로컬 서버 권장:
```bash
cd acro-site
python3 -m http.server 8080
# 브라우저에서 http://localhost:8080
```

## 내용 채워 넣을 곳 (실제 자산 연결)
1. **유튜브 리뷰** — `index.html` 의 `.rev` 버튼 `data-id=""` 에 유튜브 영상 ID를 넣으면 클릭 시 임베드 재생됩니다.
   예: `<button class="rev" data-id="dQw4w9WgXcQ">`
2. **구매 채널 링크** — `#buy` 섹션 `.buy__card` 의 `href="#"` 를 실제 스마트스토어/박람회/문의 URL로 교체.
3. **푸터 채널 링크** — 푸터 `.fbtn`(YouTube/카페/스마트스토어) `href="#"` 도 실제 URL로 교체.

## 디자인 가이드 (고정 규칙 — 브랜드 문서 기준)
- 톤: 흰 배경 + 네이비/골드 또는 블루투스 블루/네이비 포인트
- 서체: Pretendard
- 3대 메시지 필수 노출: **블루투스 전용 · 무계정 · DC 36V 저전압 안전**
- 금지: 유치하거나 산만한 장식 요소

## 배포 (예시)
정적 호스팅이면 어디든 가능 — GitHub Pages / Netlify / Vercel / 카페24 등.
GitHub Pages 사용 시 `acro-site` 폴더를 루트로 지정하거나 별도 레포로 분리하세요.

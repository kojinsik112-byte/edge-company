# ACRO STORE — 공식 사이트

엣지컴퍼니 ACRO(아크로) 공식 사이트. 한국형 커머스 구조 + 제품별 랜딩 + 브랜드 스토리까지
하나로 묶은 정적 사이트입니다. 빌드 도구 없이 바로 열고 배포할 수 있습니다.

## 페이지 구성
```
acro-site/
├─ index.html       # 쇼핑몰 메인 (롤링배너·베스트·기획전·신상품·포토후기)
├─ category.html    # 상품 목록 (카테고리/검색/베스트 + 정렬)
├─ product.html     # 상품 상세 (수량·장바구니·바로구매/스마트스토어·연관상품)
├─ cart.html        # 장바구니 (localStorage)
├─ landing.html     # 제품별 랜딩 (?p=switch|light|curtain|outlet|app) ← 데이터 기반
├─ fan.html         # 아크로 실링팬 전용 랜딩 (마스터형 / NEW SLIM 준비중)
├─ brand.html       # 브랜드 스토리 (다크 톤, Canvas 히어로 모션)
├─ about.html       # 회사 소개 (엣지컴퍼니, 4박자 구조)
├─ support.html     # 고객센터 (FAQ, A/S, 문의)
├─ mall.css         # 메인 디자인 시스템 + 랜딩/회사/고객센터 스타일
├─ fan.css          # 실링팬 페이지 전용
├─ shop.js          # 통합 엔진 (헤더/푸터 주입·상품데이터·렌더·카트·랜딩)
├─ hero.js, script.js # brand.html 전용
├─ robots.txt, sitemap.xml
└─ assets/
   ├─ favicon.svg
   ├─ hero-poster.svg      # brand.html 히어로 폴백
   └─ products/            # 상품 사진 넣는 곳 (README 참고)
```

## 핵심 구조
- **공통 헤더/푸터 일원화**: 각 페이지는 `<div data-header></div>` / `<div data-footer></div>` 만 두면
  `shop.js` 가 헤더·GNB·드로어·푸터를 자동 주입합니다. 메뉴/회사정보 수정은 `shop.js` 한 곳에서.
- **상품 데이터**: `shop.js` 의 `PRODUCTS` 배열 (현재 14개 샘플). 썸네일은 사진 없으면 SVG 자동 생성,
  `img` 필드를 넣으면 실제 사진으로 교체 (assets/products/README.md 참고).
- **제품 랜딩**: `shop.js` 의 `LANDINGS` 객체. `landing.html?p=키` 로 접근하며, 기능/사양/FAQ/연관상품을
  자동 렌더. 새 제품 랜딩은 `LANDINGS` 에 항목만 추가하면 됩니다.
- **장바구니**: 브라우저 `localStorage`. 실링팬 마스터형 등은 `buyUrl`(스마트스토어)로 바로 연결.

## 실제 운영 데이터로 바꾸기
1. **상품/가격/후기** — `shop.js` 의 `PRODUCTS` 교체.
2. **상품 사진** — `assets/products/` 에 파일 업로드 후 상품에 `img` 필드 추가.
3. **회사/사업자 정보·고객센터 번호** — `shop.js` 의 `footerHTML()` / `CS_TEL`, about/support 페이지.
4. **스마트스토어 링크** — `shop.js` 상단 `SMARTSTORE`, `FAN_BUY` 상수.
5. **도메인** — `robots.txt` / `sitemap.xml` 의 `https://acro.kr` 를 실제 도메인으로 교체.
6. **로그인·결제** — 현재 데모. 실제 판매는 스마트스토어 연동 또는 카페24·고도몰 이식 필요.

## 로컬에서 보기
```bash
cd acro-site
python3 -m http.server 8080
# http://localhost:8080
```

## 디자인 가이드 (브랜드 문서 기준 · 고정)
- 톤: 흰 배경 + 네이비/블루투스 블루(+제품별 골드/그린 액센트), Pretendard
- 3대 메시지 필수 노출: **블루투스 전용 · 무계정 · DC 36V 저전압 안전**
- 금지: 유치하거나 산만한 장식 요소

> ※ 사업자등록번호·통신판매업·고객센터 번호·이메일·일부 가격은 **샘플 값**입니다. 운영 전 실제 값으로 교체하세요.

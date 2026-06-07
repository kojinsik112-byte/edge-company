# ACRO — 공식 브랜드 사이트

엣지컴퍼니 ACRO(아크로) **브랜드 쇼케이스** 사이트.
판매·결제·배송은 **네이버 스토어팜(edge2050)** 에서 진행하고, 이 사이트는
**제품 소개 · 회사 소개 · 영상 · 신제품 준비**를 보여주는 역할입니다.
빌드 도구 없이 바로 열고 배포할 수 있는 정적 사이트입니다.

## 페이지 구성
```
acro-site/
├─ index.html       # 메인 (롤링배너·제품 라인업·영상/신제품 띠·회사소개·후기·스토어팜 CTA)
├─ category.html    # 제품 전체 보기 (가격/장바구니 없음, 스토어팜 구매 연결)
├─ product.html     # 제품 소개 상세 (사양 + 스토어팜 구매 버튼·연관제품)
├─ landing.html     # 제품별 랜딩 (?p=switch|light|curtain|outlet|app) ← 데이터 기반
├─ fan.html         # 아크로 실링팬 전용 랜딩 (마스터형 / NEW SLIM 준비중)
├─ videos.html      # 영상 (유튜브 임베드, VIDEOS 배열로 관리)
├─ coming.html      # 신제품 준비 (출시 예정 + 로드맵)
├─ brand.html       # 브랜드 스토리 (다크 톤, Canvas 히어로 모션)
├─ about.html       # 회사 소개 (엣지컴퍼니, 4박자 구조)
├─ support.html     # 고객센터 (FAQ, A/S, 문의)
├─ 404.html
├─ mall.css / fan.css   # 디자인
├─ shop.js              # 통합 엔진 (헤더/푸터 주입·데이터·렌더·랜딩·영상)
├─ hero.js / script.js  # brand.html 전용
├─ robots.txt / sitemap.xml
└─ assets/ (favicon.svg, hero-poster.svg, products/)
```

## 핵심 구조
- **판매는 스토어팜**: 모든 구매 버튼은 네이버 스토어팜으로 연결됩니다. 사이트엔 장바구니·결제·가격비교가 없습니다.
- **공통 헤더/푸터 일원화**: 각 페이지는 `<div data-header></div>` / `<div data-footer></div>` 만 두면
  `shop.js` 가 헤더·GNB·드로어·푸터를 자동 주입. 메뉴·회사정보 수정은 `shop.js` 한 곳에서.
- **제품 데이터 단일화**: `shop.js` 의 `PRODUCTS`(14개), 썸네일은 SVG 자동생성(또는 `img` 필드로 사진).
- **제품 랜딩**: `shop.js` 의 `LANDINGS` 객체. `landing.html?p=키` 로 접근, 자동 렌더.
- **영상**: `shop.js` 의 `VIDEOS` 배열에 유튜브 ID만 넣으면 `videos.html` 에서 재생.

## 운영 전 채워야 할 것
1. **제품 사진** — `assets/products/` 에 업로드 후 `PRODUCTS` 에 `img` 필드 추가.
2. **영상 ID** — `shop.js` 의 `VIDEOS` 배열에 유튜브 영상 ID.
3. **스토어팜 링크** — `shop.js` 상단 `SMARTSTORE`, `FAN_BUY` 상수(현재 edge2050 연결).
4. **회사/사업자 정보·고객센터 번호** — `shop.js` 의 `footerHTML()` / `CS_TEL`, about/support.
5. **도메인** — `robots.txt` / `sitemap.xml` 의 `https://acro.kr` 교체.

## 로컬에서 보기
```bash
cd acro-site && python3 -m http.server 8080
# http://localhost:8080
```

## 디자인 가이드 (고정)
- 톤: 흰 배경 + 네이비/블루투스 블루(+제품별 골드/그린 액센트), Pretendard
- 3대 메시지 필수 노출: **블루투스 전용 · 무계정 · DC 36V 저전압 안전**
- 금지: 유치하거나 산만한 장식 요소

> ※ 사업자등록번호·통신판매업·고객센터 번호·이메일은 **샘플 값**입니다. 운영 전 실제 값으로 교체하세요.

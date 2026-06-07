# 상품 사진 넣는 법

채팅에 붙인 이미지는 자동 저장되지 않습니다. 실제 사진을 사이트에 띄우려면:

1. 이미지 **파일**을 이 폴더(`assets/products/`)에 업로드합니다.
   권장 형식: 정사각형(1:1) `.jpg` 또는 `.webp`, 800×800px 이상.

2. `shop.js` 의 `PRODUCTS` 배열에서 해당 상품에 `img` 필드를 추가합니다.

   ```js
   { id:"sw5", cat:"switch", name:"ACRO 5채널 블루투스 유선 스위치",
     img:"assets/products/switch-5ch.jpg",   // ← 이 줄 추가
     price:89000, sale:69000, ... }
   ```

3. `img` 가 있으면 자동으로 SVG 대신 실제 사진이 표시됩니다. 없으면 기존 아이콘 썸네일이 그대로 쓰입니다.

## 권장 파일명 (예시)
| 상품 id | 권장 파일명 |
|---|---|
| sw5  | switch-5ch.jpg |
| sw3  | switch-3ch.jpg |
| fan1 | fan-light.jpg |
| fan2 | fan-plain.jpg |
| cur1 | curtain.jpg |
| bl1  | blind.jpg |
| li1  | light-umul.jpg |
| li2  | light-indirect.jpg |
| li3  | light-t5.jpg |
| li4  | light-downlight.jpg |
| ou1  | outlet.jpg |
| ve1  | vent.jpg |
| pk1  | package.jpg |

# 비즈니스 운영 본부 (Business Ops)

아크로 브랜드를 **대기업처럼** 운영하기 위한 실무 시스템. 상세페이지 제작 너머의
**상품·재고·식별(바코드)·전략** 백오피스다.

## 전략 한 줄
**실링팬 = 미끼(로스리더). 진짜 수익 = 조명·스위치·전동커튼.**
"아크로 실링팬 달면 우리 걸로 다 통일" → 생태계 락인. (product_strategy·ecosystem·pricing 팀이 운용)

## 구성
```
business-ops/
├── data/
│   ├── catalog.csv          # 제품 마스터 (SKU·가격·원가·재고·발주점·바코드)
│   └── inventory_log.csv    # 입출고 로그 (자동 생성)
├── barcodes/                # 생성된 바코드 이미지 (자동 생성)
└── tools/
    ├── inventory.py         # 재고 관리 CLI
    └── barcode_gen.py       # 바코드 생성
```

## 재고관리 (inventory팀)
```bash
cd business-ops
python tools/inventory.py list                 # 전체 현황 + 발주필요 표시
python tools/inventory.py in  ACRO-CF-145 100   # 신형 실링팬 100개 입고
python tools/inventory.py out ACRO-CF-145 5     # 5개 출고
python tools/inventory.py low                   # 발주점 이하 품목
```

## 바코드 (barcode팀)
```bash
pip install python-barcode pillow
python tools/barcode_gen.py --all               # 전 품목 Code128 생성
python tools/barcode_gen.py --sku ACRO-CF-145
```
- 내부 식별/재고용 = **Code128** (SKU 그대로 자유 사용)
- 유통용 **EAN-13**은 GS1 정식 발급번호만 (임의 생성 금지)

## SKU 체계
`ACRO-<카테고리>-<식별>` — 예: 신형 실링팬 `ACRO-CF-145`, COB조명 `ACRO-LT-COB`,
유선스위치 `ACRO-SW`, 전동커튼 `ACRO-CT`.

## 신형 실링팬 메모
저가형 / 몸통 14.5cm(저천장 대응) / 블루투스 / **입고원가 약 70,000원**(원가 65,000 + 화물 5,000, 부가세별도).
판매가는 pricing팀이 미끼 전략으로 확정.

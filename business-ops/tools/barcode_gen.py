#!/usr/bin/env python3
"""아크로 바코드 생성 — SKU(품번)로 Code128 바코드 이미지 생성.

카탈로그(business-ops/data/catalog.csv)의 sku 또는 barcode 값을 바코드 이미지로 만든다.
내부 식별/재고용은 Code128(자유). 유통용 EAN-13은 GS1 정식번호만 사용할 것.

설치: pip install python-barcode pillow
사용:
    python tools/barcode_gen.py --all              # 카탈로그 전 품목
    python tools/barcode_gen.py --sku ACRO-CF-145  # 한 품목
    python tools/barcode_gen.py --code 8801234567890 --type ean13
"""
from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CATALOG = ROOT / "data" / "catalog.csv"
OUTDIR = ROOT / "barcodes"


def _gen(code: str, kind: str, name: str) -> bool:
    OUTDIR.mkdir(parents=True, exist_ok=True)
    try:
        import barcode
        from barcode.writer import ImageWriter
    except ImportError:
        print("  ⚠️ python-barcode 미설치 → 'pip install python-barcode pillow' 후 재실행")
        print(f"     (지금은 품번만 기록: {code})")
        (OUTDIR / f"{_safe(name)}.txt").write_text(code, encoding="utf-8")
        return False
    try:
        cls = barcode.get_barcode_class(kind)
        obj = cls(code, writer=ImageWriter())
        path = obj.save(str(OUTDIR / _safe(name)))  # 확장자 자동(.png)
        print(f"  ✅ {name} [{kind}] {code} → {path}")
        return True
    except Exception as exc:
        print(f"  ❌ {name} 생성 실패: {exc}")
        return False


def _safe(s: str) -> str:
    return "".join(c if c.isalnum() or c in "-_" else "_" for c in s)


def main() -> None:
    ap = argparse.ArgumentParser(description="아크로 바코드 생성")
    ap.add_argument("--all", action="store_true", help="카탈로그 전 품목")
    ap.add_argument("--sku", help="특정 SKU")
    ap.add_argument("--code", help="임의 코드 직접 지정")
    ap.add_argument("--type", default="code128", help="바코드 종류 (code128 | ean13)")
    args = ap.parse_args()

    if args.code:
        _gen(args.code, args.type, args.code)
        return

    if not CATALOG.exists():
        sys.exit(f"❌ 카탈로그 없음: {CATALOG}")
    with open(CATALOG, encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    targets = rows if args.all else [r for r in rows if r["sku"] == args.sku]
    if not targets:
        sys.exit("대상 없음. --all 또는 --sku <SKU> 를 지정하세요.")

    print(f"\n바코드 생성 ({len(targets)}건) → {OUTDIR}")
    for r in targets:
        code = (r.get("barcode") or "").strip() or r["sku"]  # 바코드 없으면 SKU(Code128)
        kind = "ean13" if code.isdigit() and len(code) in (12, 13) else "code128"
        _gen(code, kind, r["sku"])
    print()


if __name__ == "__main__":
    main()

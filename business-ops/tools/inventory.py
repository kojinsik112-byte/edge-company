#!/usr/bin/env python3
"""아크로 재고관리 — 대기업식 SKU 재고 원장 (CSV 기반).

카탈로그: business-ops/data/catalog.csv
컬럼: sku,name,category,cost,price,barcode,stock,reorder_point

사용:
    python tools/inventory.py list                 # 전체 현황 (발주필요 표시)
    python tools/inventory.py in  ACRO-CF-145 100  # 입고 +100
    python tools/inventory.py out ACRO-CF-145 5    # 출고 -5
    python tools/inventory.py low                  # 발주점 이하 품목
"""
from __future__ import annotations

import csv
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CATALOG = ROOT / "data" / "catalog.csv"
LOG = ROOT / "data" / "inventory_log.csv"
FIELDS = ["sku", "name", "category", "cost", "price", "barcode", "stock", "reorder_point"]


def _load() -> list[dict]:
    with open(CATALOG, encoding="utf-8") as f:
        return list(csv.DictReader(f))


def _save(rows: list[dict]) -> None:
    with open(CATALOG, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        w.writeheader()
        w.writerows(rows)


def _int(v: str, default: int = 0) -> int:
    try:
        return int(float(v))
    except (ValueError, TypeError):
        return default


def _log(sku: str, delta: int, stock: int, kind: str) -> None:
    new = not LOG.exists()
    with open(LOG, "a", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        if new:
            w.writerow(["time", "sku", "type", "delta", "stock_after"])
        w.writerow([datetime.now().isoformat(timespec="seconds"), sku, kind, delta, stock])


def cmd_list(rows: list[dict]) -> None:
    print(f"\n{'SKU':<14}{'제품':<34}{'재고':>6}{'발주점':>7}  상태")
    print("-" * 72)
    for r in rows:
        stock, rop = _int(r["stock"]), _int(r["reorder_point"])
        flag = "⚠️ 발주필요" if stock <= rop else "✅"
        name = r["name"][:30]
        print(f"{r['sku']:<14}{name:<34}{stock:>6}{rop:>7}  {flag}")
    print()


def cmd_adjust(rows: list[dict], sku: str, qty: int, kind: str) -> None:
    for r in rows:
        if r["sku"] == sku:
            cur = _int(r["stock"])
            new = cur + qty if kind == "in" else cur - qty
            if new < 0:
                sys.exit(f"❌ 재고 부족: {sku} 현재 {cur}, 출고 {qty} 불가")
            r["stock"] = str(new)
            _save(rows)
            _log(sku, qty if kind == "in" else -qty, new, kind)
            print(f"✅ {sku} {kind.upper()} {qty} → 현재고 {new}")
            return
    sys.exit(f"❌ SKU 없음: {sku} (catalog.csv 확인)")


def cmd_low(rows: list[dict]) -> None:
    low = [r for r in rows if _int(r["stock"]) <= _int(r["reorder_point"])]
    if not low:
        print("✅ 발주 필요 품목 없음")
        return
    print("\n⚠️ 발주 필요:")
    for r in low:
        print(f"  - {r['sku']} {r['name']} : 재고 {_int(r['stock'])} ≤ 발주점 {_int(r['reorder_point'])}")
    print()


def main() -> None:
    args = sys.argv[1:]
    if not args:
        print(__doc__)
        return
    rows = _load()
    cmd = args[0]
    if cmd == "list":
        cmd_list(rows)
    elif cmd == "low":
        cmd_low(rows)
    elif cmd in ("in", "out"):
        if len(args) < 3:
            sys.exit(f"사용: python tools/inventory.py {cmd} <SKU> <수량>")
        cmd_adjust(rows, args[1], _int(args[2]), cmd)
    else:
        sys.exit(f"알 수 없는 명령: {cmd} (list|in|out|low)")


if __name__ == "__main__":
    main()

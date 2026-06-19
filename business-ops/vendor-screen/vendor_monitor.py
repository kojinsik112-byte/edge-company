#!/usr/bin/env python3
"""클린벤더 — 매일 아침 업체 자동 감시 (B)

watchlist.csv 의 업체들을 매일 스캔해서, **어제 대비 새로 생긴 위험글**만 골라
회장 카카오톡으로 아침 보고한다. (선정으로 끝이 아니라 입주 끝까지 감시하는 주관사)

동작:
  1) watchlist.csv 읽기 (업체명 목록)
  2) 각 업체를 배포된 클린벤더 API로 검증 → 위험글(링크) 수집
  3) state/snapshot.json (어제 본 위험글)과 비교 → '새 위험글'만 추출
  4) 새 위험이 있으면 카카오톡으로 보고 (kakao_send.send_to_me 재활용)
  5) 오늘 스냅샷 저장

키 불필요: 검증은 배포된 API가 대신 함(API에 네이버 키 내장). 카톡 토큰만 있으면 됨.

사용:
  python vendor_monitor.py            # 실제 감시 + 카톡 보고
  python vendor_monitor.py --dry-run  # 카톡 안 보내고 화면 출력만
  python vendor_monitor.py --list     # 감시 목록 확인

스케줄 등록(매일 아침): Windows 작업 스케줄러에 'EdgeVendorMonitor'로
  프로그램: python  /  인수: 이 파일 경로  /  트리거: 매일 08:40
또는 morning_routine.py 에 한 줄 추가.
"""
from __future__ import annotations
import csv
import json
import sys
import time
import urllib.parse
import urllib.request
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent
API = "https://aquamarine-cajeta-ee235f.netlify.app/api/screen"
WATCHLIST = ROOT / "watchlist.csv"
STATE_DIR = ROOT / "state"
SNAPSHOT = STATE_DIR / "snapshot.json"

# 카카오 발송기 재활용
sys.path.insert(0, str(ROOT.parent / "secretary" / "tools"))
try:
    from kakao_send import send_to_me  # type: ignore
except Exception:
    send_to_me = None


def load_watchlist() -> list[str]:
    """watchlist.csv 에서 업체명 목록을 읽는다. '업체명' 열 우선, 없으면 첫 열."""
    if not WATCHLIST.exists():
        print(f"[!] 감시 목록이 없습니다: {WATCHLIST}")
        print("    watchlist.csv 에 '업체명' 열로 업체를 적어주세요.")
        return []
    names: list[str] = []
    with WATCHLIST.open(encoding="utf-8-sig") as f:
        rows = list(csv.reader(f))
    if not rows:
        return []
    header = [c.strip() for c in rows[0]]
    col = header.index("업체명") if "업체명" in header else 0
    start = 1 if ("업체명" in header or any("업체" in h or "이름" in h for h in header)) else 0
    for r in rows[start:]:
        if col < len(r) and r[col].strip():
            names.append(r[col].strip())
    return names


def screen(vendor: str) -> dict:
    """배포된 클린벤더 API로 1개 업체 검증."""
    url = f"{API}?q={urllib.parse.quote(vendor)}"
    with urllib.request.urlopen(url, timeout=60) as r:
        return json.load(r)


def risk_urls(result: dict) -> dict:
    """검증 결과에서 위험글만 {link: {title, risk}} 로."""
    out = {}
    for it in result.get("items", []):
        if it.get("risk"):
            out[it.get("link", "")] = {"title": it.get("title", ""), "risk": it.get("risk", [])}
    return out


def main() -> None:
    dry = "--dry-run" in sys.argv
    if "--list" in sys.argv:
        for n in load_watchlist():
            print(" -", n)
        return

    vendors = load_watchlist()
    if not vendors:
        return

    STATE_DIR.mkdir(exist_ok=True)
    snapshot = {}
    if SNAPSHOT.exists():
        try:
            snapshot = json.loads(SNAPSHOT.read_text(encoding="utf-8"))
        except Exception:
            snapshot = {}

    today = date.today().isoformat()
    new_snapshot: dict = {}
    alerts: list[str] = []          # 새 위험 발견 업체별 메시지
    checked = 0

    print(f"[클린벤더 감시] {today} · 업체 {len(vendors)}개")
    for v in vendors:
        try:
            res = screen(v)
        except Exception as e:
            print(f"  · {v}: 검증 실패({e}) — 건너뜀")
            # 실패한 업체는 어제 스냅샷 유지
            if v in snapshot:
                new_snapshot[v] = snapshot[v]
            continue
        checked += 1
        today_risks = risk_urls(res)
        new_snapshot[v] = {"urls": list(today_risks.keys()), "checked": today}

        yesterday = set((snapshot.get(v) or {}).get("urls", []))
        fresh = [(u, today_risks[u]) for u in today_risks if u not in yesterday]
        mark = "🆕" if fresh else ("⚠️" if today_risks else "🛡️")
        print(f"  {mark} {v}: 위험 {len(today_risks)}건 (새 {len(fresh)}건)")

        if fresh:
            kws = sorted({k for _, d in fresh for k in d["risk"]})
            line = f"⚠️ {v} — 새 위험글 {len(fresh)}건 ({', '.join(kws[:5])})"
            sample = fresh[0][1]["title"][:40]
            line += f"\n  └ \"{sample}…\"\n  {fresh[0][0]}"
            alerts.append(line)
        time.sleep(0.8)   # API/네이버 과부하 방지

    # 보고 메시지 구성
    head = f"🔍 클린벤더 아침 감시 ({today[5:].replace('-', '/')})\n감시 {checked}개 업체 · 새 이상징후 {len(alerts)}건"
    if alerts:
        body = head + "\n\n" + "\n\n".join(alerts) + "\n\n→ 클린벤더에서 해당 업체 재검토 권장"
    else:
        body = head + "\n\n✅ 어제 대비 새로 터진 문제 없음. 전 업체 안정."

    print("\n" + "=" * 50 + "\n" + body + "\n" + "=" * 50)

    # 카톡 발송
    if dry:
        print("\n[--dry-run] 카톡 미발송")
    elif send_to_me is None:
        print("\n[!] kakao_send 를 불러오지 못해 카톡 미발송 (설정 확인)")
    else:
        try:
            ok = send_to_me(body)
            print("\n[카톡] 발송 " + ("성공" if ok else "실패"))
        except Exception as e:
            print(f"\n[카톡] 발송 오류: {e}")

    # 스냅샷 저장 (다음날 비교 기준)
    SNAPSHOT.write_text(json.dumps(new_snapshot, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"[스냅샷 저장] {SNAPSHOT}")


if __name__ == "__main__":
    main()

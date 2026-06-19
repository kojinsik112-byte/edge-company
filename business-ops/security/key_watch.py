#!/usr/bin/env python3
"""키 유출 감시·차단 (보안감시팀 security_guardian).

회장 지시: 누가 키를 가져가려는 낌새(깃 커밋에 키가 섞이는 등)면 → 즉시 차단 + 카톡 경보.

무엇을 막나:
 - 실제 키 값이 git 추적 파일 / 스테이징(커밋 직전)에 들어갔는지 탐지
 - 흔한 키 패턴(AIza…, fal Key, sk-…) 노출 탐지
 - 발견 시: ① pre-commit 훅이 커밋 자체를 '차단'(exit 1) ② 회장 카톡 경보

사용:
    python business-ops/security/key_watch.py scan          # 전체 점검(추적파일)
    python business-ops/security/key_watch.py precommit      # 스테이징 점검(훅이 호출, 유출시 exit 1)
    python business-ops/security/key_watch.py scan --kakao   # 점검+이상시 카톡
"""
from __future__ import annotations
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ENV = ROOT / "design-division" / ".env"
sys.path.insert(0, str(ROOT / "business-ops" / "secretary" / "tools"))

GENERIC = [
    re.compile(r"AIzaSy[A-Za-z0-9_\-]{30,}"),          # Google/YouTube
    re.compile(r"sk-[A-Za-z0-9]{20,}"),                # OpenAI
    re.compile(r"\bKey [a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}"),  # fal.ai
]
SKIP = (".env", ".env.example", "key_watch.py")


def _secrets() -> list[str]:
    """.env 의 실제 키 값들(길이 12+ 비밀값만)."""
    out = []
    if not ENV.exists():
        return out
    for ln in ENV.read_text(encoding="utf-8", errors="ignore").splitlines():
        if "=" in ln and not ln.strip().startswith("#"):
            k, v = ln.split("=", 1)
            k, v = k.strip(), v.strip()
            # 비밀키만(모델명·URI·짧은 ID 등 공개값 제외)
            if (v and len(v) >= 16 and "localhost" not in v
                    and not k.endswith(("REDIRECT_URI", "MODEL", "CUSTOMER_ID"))):
                out.append((k, v))
    return out


def _mask(v: str) -> str:
    return v[:5] + "…" + v[-3:] if len(v) > 10 else "(키)"


def _git(args: list[str]) -> str:
    try:
        return subprocess.check_output(["git"] + args, cwd=str(ROOT), text=True, errors="ignore")
    except Exception:
        return ""


def scan_text(text: str, where: str, secrets) -> list[str]:
    leaks = []
    for k, v in secrets:
        if v in text:
            leaks.append(f"{where}: 실제 키 '{k}' ({_mask(v)}) 노출!")
    for pat in GENERIC:
        for m in set(pat.findall(text)):
            leaks.append(f"{where}: 키 패턴 노출 {_mask(m)}")
    return leaks


def scan_tracked() -> list[str]:
    secrets = _secrets()
    leaks = []
    for f in _git(["ls-files"]).splitlines():
        if any(f.endswith(s) for s in SKIP):
            continue
        p = ROOT / f
        try:
            txt = p.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue
        leaks += scan_text(txt, f, secrets)
    return leaks


def scan_staged() -> list[str]:
    secrets = _secrets()
    diff = _git(["diff", "--cached"])
    return scan_text(diff, "스테이징(커밋 직전)", secrets)


def alert(leaks: list[str]):
    msg = ("🚨🔒 [보안경보] 키 유출 위험 감지!\n\n"
           + "\n".join("· " + x for x in leaks[:8])
           + "\n\n커밋이 차단됐습니다. 해당 키를 즉시 재발급(차단)하세요:\n"
           "fal.ai/dashboard · console.cloud.google.com · developers.kakao.com · searchad.naver.com")
    print(msg)
    try:
        import kakao_send
        kakao_send.send_to_me(msg)
    except Exception as e:
        print("(카톡 경보 실패:", e, ")")


def main():
    a = sys.argv[1:]
    cmd = a[0] if a else "scan"
    kakao = "--kakao" in a
    if cmd == "precommit":
        leaks = scan_staged()
        if leaks:
            alert(leaks)
            print("\n❌ 커밋 차단됨 — 키가 섞였습니다. (.env 만 쓰고 커밋에서 빼세요)")
            sys.exit(1)
        sys.exit(0)
    else:
        leaks = scan_tracked()
        if leaks:
            print("🔴 유출 발견:")
            for x in leaks:
                print("  " + x)
            if kakao:
                alert(leaks)
            sys.exit(1)
        print("✅ 키 유출 없음 — 모든 키 안전(.env에만 분리).")


if __name__ == "__main__":
    main()

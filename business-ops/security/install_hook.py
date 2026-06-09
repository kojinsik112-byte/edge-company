#!/usr/bin/env python3
"""pre-commit 차단 훅 설치 (보안감시팀). 새 PC/클론 시 1회 실행하면 키 섞인 커밋이 자동 차단된다.

    python business-ops/security/install_hook.py
"""
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
hook = ROOT / ".git" / "hooks" / "pre-commit"
py = (sys.executable or "python").replace("\\", "/")
content = ("#!/bin/sh\n"
           "# 🔒 보안감시팀 — 커밋에 API키가 섞이면 차단 + 카톡 경보\n"
           f'"{py}" "business-ops/security/key_watch.py" precommit\n')
hook.parent.mkdir(parents=True, exist_ok=True)
hook.write_text(content, encoding="utf-8")
try:
    os.chmod(hook, 0o755)
except Exception:
    pass
print("✅ pre-commit 차단 훅 설치 완료:", hook)

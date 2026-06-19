#!/usr/bin/env python3
"""카카오톡 '나에게 보내기' 전송기 — 비서실(JARVIS)이 회장 카톡으로 보고.

1인 대표가 자기 카카오톡으로 메시지를 받는 정석 경로 = Kakao '메모(나에게 보내기)' API.
친구추가/채널/알림톡 승인 없이, 카카오 로그인 + talk_message 권한만으로 내 톡에 꽂힌다.

■ 최초 1회 세팅(회장이 브라우저로, 비번은 본인만 — 나는 입력 안 함):
  1) https://developers.kakao.com → 내 애플리케이션 생성 → [앱 키]의 'REST API 키' 복사
  2) [카카오 로그인] 활성화 ON, [동의항목]에서 '카카오톡 메시지 전송(talk_message)' 사용
  3) [카카오 로그인] > Redirect URI 에 https://localhost 등록
  4) .env(design-division/.env)에  KAKAO_REST_API_KEY=...  KAKAO_REDIRECT_URI=https://localhost  채움
  5) 동의 URL 출력 →  python kakao_send.py authorize-url
     그 URL 브라우저로 열어 동의 → 주소창 ...?code=XXXX 의 XXXX 복사
  6) 토큰 발급:  python kakao_send.py exchange XXXX     → refresh_token 이 .env 에 자동 저장
  7) 테스트:    python kakao_send.py send "자비스 테스트 보고"

이후엔 access_token 만료돼도 refresh_token 으로 자동 갱신해 계속 보낸다.

사용:
    python kakao_send.py authorize-url
    python kakao_send.py exchange <authorization_code>
    python kakao_send.py send "메시지"            # 길면 자동 분할 전송
"""
from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path

import requests

ENV_PATH = Path(__file__).resolve().parents[3] / "design-division" / ".env"
STATE = Path(__file__).resolve().parent.parent / "state" / "kakao_token.json"  # gitignore 대상
AUTH = "https://kauth.kakao.com/oauth"
KAPI = "https://kapi.kakao.com"
TEXT_LIMIT = 190   # 카카오 text 템플릿 안전 길이(분할 기준)

try:
    from dotenv import load_dotenv
    load_dotenv(ENV_PATH)
except Exception:
    pass


def _env(k: str, default: str = "") -> str:
    return os.environ.get(k, default).strip()


def _set_env_file(key: str, value: str) -> None:
    """design-division/.env 의 key 값을 추가/갱신(다른 키 보존)."""
    lines, found = [], False
    if ENV_PATH.exists():
        lines = ENV_PATH.read_text(encoding="utf-8").splitlines()
    for i, ln in enumerate(lines):
        if ln.strip().startswith(f"{key}="):
            lines[i] = f"{key}={value}"; found = True; break
    if not found:
        lines.append(f"{key}={value}")
    ENV_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")
    os.environ[key] = value


def _mask(t: str) -> str:
    return (t[:6] + "…" + t[-4:]) if t and len(t) > 12 else "(set)"


# ── OAuth ───────────────────────────────────────────────────────────────
def authorize_url() -> str:
    key = _env("KAKAO_REST_API_KEY")
    redirect = _env("KAKAO_REDIRECT_URI", "https://localhost")
    if not key:
        sys.exit("KAKAO_REST_API_KEY 가 .env 에 없습니다. (developers.kakao.com REST API 키)")
    return (f"{AUTH}/authorize?client_id={key}&redirect_uri={redirect}"
            f"&response_type=code&scope=talk_message")


def exchange(code: str) -> None:
    key = _env("KAKAO_REST_API_KEY")
    redirect = _env("KAKAO_REDIRECT_URI", "https://localhost")
    data = {"grant_type": "authorization_code", "client_id": key,
            "redirect_uri": redirect, "code": code}
    secret = _env("KAKAO_CLIENT_SECRET")
    if secret:
        data["client_secret"] = secret
    r = requests.post(f"{AUTH}/token", data=data, timeout=20)
    d = r.json()
    if "refresh_token" not in d:
        sys.exit(f"토큰 발급 실패: {d}")
    _set_env_file("KAKAO_REFRESH_TOKEN", d["refresh_token"])
    _save_access(d.get("access_token", ""), d.get("expires_in", 0))
    print(f"✅ 발급 완료. refresh_token 저장({_mask(d['refresh_token'])}). 이제 send 사용 가능.")


def _save_access(token: str, expires_in: int) -> None:
    STATE.parent.mkdir(parents=True, exist_ok=True)
    STATE.write_text(json.dumps({"access_token": token,
                                 "exp": time.time() + max(expires_in - 60, 0)}), encoding="utf-8")


def _load_access() -> str | None:
    if STATE.exists():
        d = json.loads(STATE.read_text(encoding="utf-8"))
        if d.get("access_token") and d.get("exp", 0) > time.time():
            return d["access_token"]
    return None


def _refresh_access() -> str:
    rt = _env("KAKAO_REFRESH_TOKEN")
    key = _env("KAKAO_REST_API_KEY")
    if not rt:
        sys.exit("KAKAO_REFRESH_TOKEN 없음 → 먼저 authorize-url → exchange 로 1회 인증하세요.")
    data = {"grant_type": "refresh_token", "client_id": key, "refresh_token": rt}
    secret = _env("KAKAO_CLIENT_SECRET")
    if secret:
        data["client_secret"] = secret
    r = requests.post(f"{AUTH}/token", data=data, timeout=20)
    d = r.json()
    if "access_token" not in d:
        sys.exit(f"토큰 갱신 실패: {d}")
    _save_access(d["access_token"], d.get("expires_in", 0))
    if d.get("refresh_token"):              # 가끔 새 refresh_token 내려줌
        _set_env_file("KAKAO_REFRESH_TOKEN", d["refresh_token"])
    return d["access_token"]


def _access_token() -> str:
    return _load_access() or _refresh_access()


# ── 전송 ────────────────────────────────────────────────────────────────
def _chunks(text: str, n: int = TEXT_LIMIT) -> list[str]:
    out, buf = [], ""
    for line in text.split("\n"):
        if len(buf) + len(line) + 1 > n and buf:
            out.append(buf); buf = ""
        # 한 줄이 너무 길면 강제 분할
        while len(line) > n:
            out.append(line[:n]); line = line[n:]
        buf = (buf + "\n" + line) if buf else line
    if buf:
        out.append(buf)
    return out


def send_to_me(text: str, link_url: str = "") -> bool:
    """text를 길이에 맞춰 분할해 '나에게 보내기'로 순차 전송. 토큰 없으면 False(드라이런)."""
    if not _env("KAKAO_REFRESH_TOKEN"):
        print("⚠️ KAKAO_REFRESH_TOKEN 없음 → 실발송 생략(드라이런). 세팅법은 secretary/README.md")
        return False
    token = _access_token()
    parts = _chunks(text)
    total = len(parts)
    for i, part in enumerate(parts, 1):
        tag = f"({i}/{total})\n" if total > 1 else ""
        tmpl = {"object_type": "text", "text": tag + part,
                "link": {"web_url": link_url or "https://shopping.naver.com"}}
        r = requests.post(f"{KAPI}/v2/api/talk/memo/default/send",
                          headers={"Authorization": f"Bearer {token}"},
                          data={"template_object": json.dumps(tmpl, ensure_ascii=False)}, timeout=20)
        if r.status_code != 200:
            # access 만료 등 1회 강제 갱신 후 재시도
            token = _refresh_access()
            r = requests.post(f"{KAPI}/v2/api/talk/memo/default/send",
                              headers={"Authorization": f"Bearer {token}"},
                              data={"template_object": json.dumps(tmpl, ensure_ascii=False)}, timeout=20)
        if r.status_code != 200:
            print(f"❌ 전송 실패 {r.status_code}: {r.text[:200]}")
            return False
        time.sleep(0.4)
    print(f"✅ 카톡 전송 완료 ({total}건)")
    return True


def main() -> None:
    a = sys.argv[1:]
    if not a:
        print(__doc__); return
    if a[0] == "authorize-url":
        print("\n아래 URL을 브라우저로 열어 동의 후, 주소창 code= 값을 복사하세요:\n")
        print(authorize_url()); print()
    elif a[0] == "exchange":
        if len(a) < 2:
            sys.exit("사용: exchange <authorization_code>")
        exchange(a[1])
    elif a[0] == "send":
        if len(a) < 2:
            sys.exit('사용: send "메시지"')
        send_to_me(" ".join(a[1:]))
    else:
        sys.exit("명령: authorize-url | exchange | send")


if __name__ == "__main__":
    main()

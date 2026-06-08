#!/usr/bin/env python3
"""음성 브리핑(JARVIS voice) — 타입캐스트(Typecast) TTS로 아침 보고를 목소리로.

회장이 타입캐스트 유료 사용 중 → 그 API로 브리핑 텍스트를 mp3로 만들어 데스크탑에서 재생(자비스).
카톡엔 텍스트로 보고하고, 음성은 PC에서 읽어준다(원하면).

■ 세팅(.env, design-division/.env):
    TYPECAST_API_KEY=...        # 타입캐스트 [내 계정 > API] 토큰
    TYPECAST_ACTOR_ID=...       # 쓰고 싶은 보이스(액터) id  (없으면 actors 명령으로 조회)

사용:
    python voice_brief.py actors            # 내 계정의 보이스(액터) 목록 조회
    python voice_brief.py speak "텍스트"     # mp3 생성(+재생)
    (morning_brief.py --voice 가 speak()를 호출)

※ 타입캐스트 API 스펙은 버전에 따라 필드명이 바뀔 수 있다. 엔드포인트/필드는 .env로 덮어쓸 수 있게
   TYPECAST_BASE(기본 https://typecast.ai/api)로 분리. 실패 시 무엇을 고칠지 안내만 하고 멈추지 않는다.
"""
from __future__ import annotations

import os
import sys
import time
from pathlib import Path

import requests

ENV_PATH = Path(__file__).resolve().parents[3] / "design-division" / ".env"
OUT = Path(__file__).resolve().parent.parent / "briefs"
OUT.mkdir(parents=True, exist_ok=True)

try:
    from dotenv import load_dotenv
    load_dotenv(ENV_PATH)
except Exception:
    pass

BASE = os.environ.get("TYPECAST_BASE", "https://typecast.ai/api").strip()


def _key() -> str:
    k = os.environ.get("TYPECAST_API_KEY", "").strip()
    if not k:
        raise SystemExit("TYPECAST_API_KEY 없음 → .env 에 타입캐스트 API 토큰을 넣으세요.")
    return k


def _headers() -> dict:
    return {"Authorization": f"Bearer {_key()}"}


def actors() -> None:
    r = requests.get(f"{BASE}/actor", headers=_headers(), timeout=20)
    print(r.status_code)
    try:
        data = r.json()
    except Exception:
        print(r.text[:500]); return
    items = data.get("result") or data.get("actors") or data
    if isinstance(items, list):
        for a in items[:30]:
            print(f"- {a.get('actor_id') or a.get('id')}  {a.get('name') or a.get('display_name','')}")
    else:
        print(data)


def speak(text: str, play: bool = False) -> Path | None:
    """텍스트 → mp3. 성공 시 파일경로 반환, 실패/미설정 시 None(멈추지 않음)."""
    try:
        actor = os.environ.get("TYPECAST_ACTOR_ID", "").strip()
        if not actor:
            print("⚠️ TYPECAST_ACTOR_ID 없음 → 'python voice_brief.py actors'로 보이스 id 확인 후 .env에 설정.")
            return None
        # 1) 합성 요청(비동기)
        payload = {
            "actor_id": actor,
            "text": text[:900],
            "lang": "auto",
            "model_version": "latest",
            "xapi_hd": True,
            "tempo": 1.0,
            "volume": 100,
            "pitch": 0,
        }
        r = requests.post(f"{BASE}/speak", headers=_headers(), json=payload, timeout=30)
        if r.status_code not in (200, 201):
            print(f"⚠️ 타입캐스트 합성요청 실패 {r.status_code}: {r.text[:200]}")
            return None
        res = r.json().get("result", {})
        poll_url = res.get("speak_v2_url") or res.get("speak_url")
        if not poll_url:
            print(f"⚠️ 폴링 URL 없음(스펙 변경 가능): {r.text[:200]}")
            return None
        # 2) 완료까지 폴링
        audio_url = None
        for _ in range(30):
            time.sleep(1)
            p = requests.get(poll_url, headers=_headers(), timeout=20).json().get("result", {})
            if p.get("status") == "done":
                audio_url = p.get("audio_download_url") or p.get("audio_url")
                break
        if not audio_url:
            print("⚠️ 음성 생성 시간초과/실패."); return None
        # 3) 다운로드
        mp3 = OUT / f"voice_{int(time.time())}.mp3"
        mp3.write_bytes(requests.get(audio_url, headers=_headers(), timeout=60).content)
        print(f"🔊 음성 브리핑 생성: {mp3}")
        if play:
            try:
                os.startfile(str(mp3))    # Windows 기본 플레이어로 재생(자비스)
            except Exception:
                pass
        return mp3
    except SystemExit as e:
        print(f"음성 브리핑 보류: {e}"); return None
    except Exception as e:
        print(f"음성 브리핑 오류: {e}"); return None


def main() -> None:
    a = sys.argv[1:]
    if not a:
        print(__doc__); return
    if a[0] == "actors":
        actors()
    elif a[0] == "speak":
        if len(a) < 2:
            sys.exit('사용: speak "텍스트"')
        speak(" ".join(a[1:]), play=True)
    else:
        sys.exit("명령: actors | speak")


if __name__ == "__main__":
    main()

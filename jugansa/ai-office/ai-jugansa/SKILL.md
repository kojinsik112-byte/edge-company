---
name: ai-jugansa
description: AI 주관사업부 오피스 서버를 켜고 접속 주소를 알려준다. /ai-jugansa 로 직접 부를 때만 사용.
disable-model-invocation: true
allowed-tools: Bash(python *) Bash(python3 *) Bash(py *) Bash(curl *)
---

1. `curl -s -o NUL -w "%{http_code}" http://127.0.0.1:8790/health` (맥·리눅스는 `-o /dev/null`) 가 200이면 이미 켜져 있다. 새로 켜지 않는다.
2. 아니면 백그라운드로 켠다: `(python "${CLAUDE_SKILL_DIR}/server.py" >/dev/null 2>&1 &)` (python이 없으면 `py -3`, 맥·리눅스는 `python3`).
3. 2초 뒤 1번을 다시 확인하고 한 줄로만 알린다: `AI 주관사업부 오피스 켜짐 → http://127.0.0.1:8790`
4. 그래도 안 되면 포트가 다른 프로그램에 잡힌 것. `server.py` 위쪽 `PORT` 와 settings.json 의 주소를 같이 바꾸라고 알린다.

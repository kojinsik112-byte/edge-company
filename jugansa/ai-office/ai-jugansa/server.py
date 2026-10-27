#!/usr/bin/env python3
"""AI 주관사업부 오피스 — Claude Code hooks 수신 서버 (표준 라이브러리만 · 127.0.0.1 전용 · 외부 전송 없음)

실행:  python server.py        화면: http://127.0.0.1:8790
신호:  settings.json 의 http 훅 → POST /event (빈 200 응답 = Claude 대화에 아무것도 안 들어감)

방(=업무 단계)은 '어느 팀이 일하나(agent_type)'로 먼저 정하고,
팀 이름이 없으면(본부장 직접 작업) 만지는 파일 경로로 단계를 추정한다.
"""
import json, os, re, sys, time, threading, datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse, parse_qs

HOST, PORT = "127.0.0.1", 8790
HERE = os.path.dirname(os.path.abspath(__file__))

# ── 팀(서브에이전트 agent_type) → 방 ────────────────────────────────
TEAM_ROOM = {
    "bid_watch": "scout", "bid_outreach": "scout",
    "bid_notice_analyst": "analysis", "realestate_analyst": "analysis", "cafe_insight": "analysis",
    "bid_economist": "analysis", "bid_venue": "analysis", "jugansa_scholar": "analysis",
    "pt_builder": "build", "bid_docs": "build", "bid_visual": "build",
    "auditor": "audit", "legal": "audit", "visual_qa": "audit",
    "bid_mail": "mail",
    "bid_pt_coach": "pt",
    "bid_retro": "retro", "bid_pmo": "retro",
}
TEAM_KR = {
    "bid_watch": "공고 감시팀", "bid_outreach": "신규 개척팀",
    "bid_notice_analyst": "공고 분석관", "realestate_analyst": "단지 분석팀", "cafe_insight": "카페 인사이트팀",
    "bid_economist": "손익 분석관", "bid_venue": "행사장 조사관", "jugansa_scholar": "주관사 연구팀",
    "pt_builder": "제안서 빌더", "bid_docs": "제출서류 담당", "bid_visual": "단지 비주얼팀",
    "auditor": "검수팀", "legal": "법무팀", "visual_qa": "비주얼 QA팀",
    "bid_mail": "발송 담당", "bid_pt_coach": "PT 코치", "bid_retro": "결과 분석팀", "bid_pmo": "마감 관제팀",
    "general-purpose": "독립 검수관", "Explore": "탐색 요원",
}
# 팀 이름이 없을 때(본부장 직접 작업) 경로 · 스킬 · 명령어로 단계를 추정 — 위에서부터 먼저 맞는 것
PATH_RULES = [
    ("audit",    r"court|검증|법정|GPT_검증|검수|verify|audit|gpt2"),
    ("mail",     r"mail_|메일|GIF|lx_gif|align_pair|assemble_|_dl/|보관함|제출본"),
    ("pt",       r"PT_|pt_coach|PT용|발표"),
    ("retro",    r"입찰_결과분석|입찰현황판|scorecard|결과분석|retro"),
    ("analysis", r"착수|kickoff|notice\.txt|분석|analysis|hwp2txt|mask_notice|손익"),
    ("build",    r"build_[a-z]+\.py|docs_[a-z]+\.py|data\.py|reorg|polish|vis\.py|pages21|light_build|제안서|summary_|tjlight|card_fit"),
    ("scout",    r"watch/|개척|outreach|notice_watch|공고"),
]
SITES = {"상주자이르네": "상주", "엘리프한신더휴수원": "엘리프", "롯데캐슬나리벡시티": "나리벡", "북수원디에트르더리체2": "북수원",
         "고양창릉S5": "고양", "경산상방공원호반써밋1단지": "경산", "탕정푸르지오센터파크": "탕정", "오산세교아테라": "오산",
         "분당퍼스트빌리지": "분당", "지웰엘리움양주덕계역": "지웰", "철산역자이": "철산", "판교테크노밸리중흥S": "판교", "동탄파라곤3차": "동탄"}
def site_for(h):
    for k, v in SITES.items():
        if k in h: return v
    for v in SITES.values():              # 약칭만 적혀 있어도 잡는다 ("상주 올려줘")
        if v in h: return v
    m = re.search(r"jugansa[\\/]([^\\/]+)", h)
    return m.group(1)[:5] if m and not m.group(1).endswith((".py", ".md")) and not m.group(1).startswith(("ai-office", "tools")) else ""
# ── 단지 보드: jugansa/입찰현황판.md 의 '진행 중' 표에서 마감 · PT · 제출 여부를 읽는다 ──
BOARD_FILE = [None]          # 찾은 현황판 경로 (SessionStart 의 cwd · 환경변수 JUGANSA_DIR · 이 폴더 위쪽 순으로 찾음)
def find_board(start=None):
    cands = []
    if os.environ.get("JUGANSA_DIR"): cands.append(os.path.join(os.environ["JUGANSA_DIR"], "입찰현황판.md"))
    for base in [start, HERE]:
        if not base: continue
        d = os.path.abspath(base)
        for _ in range(6):
            cands.append(os.path.join(d, "입찰현황판.md")); cands.append(os.path.join(d, "jugansa", "입찰현황판.md")); d = os.path.dirname(d)
    for c in cands:
        if os.path.isfile(c): BOARD_FILE[0] = c; return c
    return BOARD_FILE[0]

def parse_date(txt, today):
    m = re.search(r"(\d{1,2})\.(\d{1,2})(?:\([^)]*\))?(?:\s*(\d{1,2}):(\d{2}))?", txt or "")
    if not m: return None, ""
    mo, da = int(m.group(1)), int(m.group(2)); yr = today.year
    if mo < today.month - 6: yr += 1
    try: d = datetime.date(yr, mo, da)
    except ValueError: return None, ""
    return d, (f"{m.group(3)}:{m.group(4)}" if m.group(3) else "")

def board():
    f = find_board()
    if not f: return {"file": "", "sites": []}
    today = datetime.date.today(); rows = []; on = False
    try: lines = open(f, encoding="utf-8").read().splitlines()
    except OSError: return {"file": f, "sites": []}
    for ln in lines:
        if ln.startswith("| 단지 |") and "제출 마감" in ln: on = True; continue
        if on and not ln.startswith("|"): on = False
        if not on or ln.startswith("|---") or ln.startswith("| ---"): continue
        c = [x.strip() for x in ln.strip().strip("|").split("|")]
        if len(c) < 7: continue
        name, hh, q, due, pt, status, rest = c[0], c[1], c[2], c[3], c[5], c[6], " ".join(c[7:])
        short = site_for(name) or name[:4]
        d, tm = parse_date(due, today)
        done = "✅" in status or "✅" in rest or "제출 완료" in status
        dday = (d - today).days if d else None
        ptd, _ = parse_date(pt, today)
        rows.append({"site": short, "name": name, "hh": hh, "due": re.sub(r"\*", "", due), "dday": dday, "time": tm,
                     "pt": re.sub(r"\*", "", pt)[:28], "pt_dday": (ptd - today).days if ptd else None, "done": done})
    rows.sort(key=lambda r: (r["done"], r["dday"] if r["dday"] is not None else 999))
    return {"file": f, "today": today.isoformat(), "sites": rows}

BOSS = "boss"            # 본부장 캐릭터 id
ROOM_OF_CHAR = {"boss": "office", "scout": "scout", "analyst": "analysis", "builder": "build",
                "auditor": "audit", "mailer": "mail", "coach": "pt", "retro": "retro", "pmo": "retro"}
CHAR_OF_ROOM = {"scout": "scout", "analysis": "analyst", "build": "builder", "audit": "auditor",
                "mail": "mailer", "pt": "coach", "retro": "retro", "office": "boss"}

def short(s, n=40):
    s = str(s).replace("\n", " ").strip()
    return s if len(s) <= n else s[:n] + "…"

def label_for(tool, ti):
    ti = ti or {}
    if tool == "Skill":                 return "/" + str(ti.get("skill", ""))
    if tool == "Agent":                 return str(ti.get("subagent_type") or ti.get("description") or "팀 호출")
    for k in ("file_path", "notebook_path"):
        if k in ti: return re.split(r"[\\/]", str(ti[k]))[-1]      # 윈도우 · 리눅스 경로 모두
    if "command" in ti:                 return short(ti["command"], 34)
    if "pattern" in ti:                 return short(ti["pattern"], 28)
    if "query" in ti:                   return short(ti["query"], 28)
    if "url" in ti:                     return short(urlparse(str(ti["url"])).netloc, 28)
    if "subject" in ti:                 return short(ti["subject"], 28)
    return ""

def haystack(tool, ti):
    ti = ti or {}
    parts = [tool]
    for k in ("file_path", "notebook_path", "command", "pattern", "path", "skill", "args", "subagent_type", "description", "prompt", "subject"):
        if k in ti: parts.append(str(ti[k])[:400])
    return " ".join(parts)

def stage_for(tool, ti):
    """본부장 직접 작업의 단계 추정. 못 정하면 본부장실."""
    if tool == "Skill":
        s = str((ti or {}).get("skill", ""))
        if s == "court": return "audit"
        if s == "kickoff": return "analysis"
    if tool == "Agent":
        return TEAM_ROOM.get(str((ti or {}).get("subagent_type", "")), "office")
    h = haystack(tool, ti)
    for room, rx in PATH_RULES:
        if re.search(rx, h, re.I): return room
    return "office"

LOCK = threading.Lock(); EVENTS = []; SEQ = [0]
LOG_PATH = os.path.join(HERE, "events.log")

def push(ev):
    with LOCK:
        SEQ[0] += 1; ev["id"] = SEQ[0]; ev["t"] = time.time(); EVENTS.append(ev); del EVENTS[:-600]
    try:
        with open(LOG_PATH, "a", encoding="utf-8") as f: f.write(json.dumps(ev, ensure_ascii=False) + "\n")
    except OSError: pass

def translate(h):
    name = h.get("hook_event_name", ""); tool = h.get("tool_name", ""); ti = h.get("tool_input") or {}
    agent = h.get("agent_type") or ""           # 서브에이전트(팀) 안에서 온 신호면 팀 이름이 붙어 있다
    team = agent if agent in TEAM_ROOM or agent in TEAM_KR else ""
    if name == "SubagentStart":
        a = h.get("agent_type", "")
        return {"kind": "team_start", "team": a, "team_kr": TEAM_KR.get(a, a), "room": TEAM_ROOM.get(a, "analysis"), "agent_id": h.get("agent_id", ""), "site": site_for(str(h.get("cwd", "")))}
    if name == "SubagentStop":
        a = h.get("agent_type", "")
        return {"kind": "team_stop", "team": a, "room": TEAM_ROOM.get(a, "analysis"), "agent_id": h.get("agent_id", "")}
    if name == "PreToolUse":
        if team:
            return {"kind": "work", "who": CHAR_OF_ROOM[TEAM_ROOM.get(team, "analysis")], "room": TEAM_ROOM.get(team, "analysis"),
                    "team": team, "team_kr": TEAM_KR.get(team, team), "tool": tool, "label": label_for(tool, ti), "agent_id": h.get("agent_id", ""), "site": site_for(haystack(tool, ti))}
        room = stage_for(tool, ti)
        return {"kind": "work", "who": BOSS, "room": room, "team": "", "team_kr": "본부장", "tool": tool, "label": label_for(tool, ti), "site": site_for(haystack(tool, ti)),
                "call": str(ti.get("subagent_type", "")) if tool == "Agent" else ""}
    if name == "PostToolUse":
        return {"kind": "done", "who": CHAR_OF_ROOM[TEAM_ROOM.get(team, "analysis")] if team else BOSS, "tool": tool}
    if name == "Notification":
        return {"kind": "memo", "memo_type": h.get("notification_type", "notice"), "label": short(h.get("title") or h.get("message") or "알림", 36)}
    if name in ("Stop", "SessionEnd"):
        return {"kind": "rest", "reason": name}
    if name == "SessionStart":
        find_board(h.get("cwd"))
        return {"kind": "start", "source": h.get("source", ""), "model": h.get("model", ""), "cwd": os.path.basename(h.get("cwd", "") or "")}
    if name == "UserPromptSubmit":
        return {"kind": "prompt", "label": short(h.get("prompt", ""), 40), "site": site_for(str(h.get("prompt", "")) + " " + str(h.get("cwd", "")))}
    return None

MIME = {".html": "text/html; charset=utf-8", ".png": "image/png", ".js": "text/javascript", ".json": "application/json"}

class H(BaseHTTPRequestHandler):
    def log_message(self, *a): pass
    def _send(self, code, body=b"", ctype="text/plain; charset=utf-8"):
        self.send_response(code); self.send_header("Content-Type", ctype); self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store"); self.end_headers()
        if body: self.wfile.write(body)
    def _file(self, rel):
        p = os.path.join(HERE, rel)
        if not os.path.isfile(p): return self._send(404, b"not found")
        with open(p, "rb") as f: data = f.read()
        self._send(200, data, MIME.get(os.path.splitext(p)[1], "application/octet-stream"))
    def do_GET(self):
        u = urlparse(self.path)
        if u.path in ("/", "/index.html"): return self._file("index.html")
        if u.path.startswith("/static/"): return self._file(os.path.join("static", os.path.basename(u.path)))
        if u.path == "/poll":
            since = int(parse_qs(u.query).get("since", ["0"])[0])
            with LOCK: evs = [e for e in EVENTS if e["id"] > since]; seq = SEQ[0]
            return self._send(200, json.dumps({"seq": seq, "events": evs}, ensure_ascii=False).encode(), MIME[".json"])
        if u.path == "/health": return self._send(200, b"ok")
        if u.path == "/sites": return self._send(200, json.dumps(board(), ensure_ascii=False).encode(), MIME[".json"])
        self._send(404, b"not found")
    def do_POST(self):
        u = urlparse(self.path); n = int(self.headers.get("Content-Length") or 0); raw = self.rfile.read(n) if n else b""
        if u.path == "/event":
            try: h = json.loads(raw.decode("utf-8") or "{}")
            except ValueError: h = {}
            ev = translate(h) if isinstance(h, dict) else None
            if ev: push(ev)
            return self._send(200)
        if u.path == "/sim":
            try: push(json.loads(raw.decode("utf-8")))
            except ValueError: return self._send(400, b"bad json")
            return self._send(200)
        self._send(404, b"not found")

def main():
    try: srv = ThreadingHTTPServer((HOST, PORT), H)
    except OSError as e:
        print(f"[ai-jugansa] {HOST}:{PORT} 를 열 수 없음: {e} (이미 켜져 있으면 브라우저에서 주소만 여세요)"); sys.exit(1)
    print(f"[ai-jugansa] 켜짐 → http://{HOST}:{PORT}   (끄기: Ctrl+C)")
    try: srv.serve_forever()
    except KeyboardInterrupt: pass

if __name__ == "__main__":
    main()

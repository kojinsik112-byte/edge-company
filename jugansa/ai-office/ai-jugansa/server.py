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
    # 개척 = 새 단지 첫 확인(공고 · 상권 · 아파트 · 카페) / 착수분석 = 그 결과로 참여 여부 · 손익 · 착수 보고
    "bid_watch": "scout", "bid_outreach": "scout",
    "bid_notice_analyst": "scout", "realestate_analyst": "scout", "cafe_insight": "scout",
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
    ("audit",    r"court|검증|법정|GPT_검증|검수|verify|audit|gpt2|after_p|before_p|ctx_p|대조|page_audit|overlap_audit|compare|diff"),
    ("mail",     r"mail_|메일|GIF|lx_gif|align_pair|assemble_|_dl/|보관함|제출본"),
    ("pt",       r"(?<![a-z])PT_|pt_coach|PT용|발표"),     # 'javascript_tool' 같은 도구 이름에 걸리지 않게
    ("retro",    r"입찰_결과분석|입찰현황판|scorecard|결과분석|retro"),
    ("build",    r"build_[a-z]+\.py|docs_[a-z]+\.py|data\.py|reorg|polish|vis\.py|pages21|light_build|제안서|summary_|tjlight|card_fit|patch|fix_|merge_|stamp|mask_rect|seal|덧패치|ctx_[a-z]+\.py|find_[a-z]+\.py"),
    # 폴더 이름 '05주관사 입찰공고'에 걸리지 않게 '공고' 한 단어는 쓰지 않는다
    ("scout",    r"watch/|개척|outreach|notice_watch|notice\.txt|hwp2txt|mask_notice|공고 ?(감시|확인|분석|원문)|공고문|새 공고|상권|입지|카페|cafe|청약|realestate|단지 ?분석|아파트 ?분석"),
    ("analysis", r"착수|kickoff|분석|analysis|손익|사업성|economist|venue|행사장"),
]
SITES = {"상주자이르네": "상주", "엘리프한신더휴수원": "엘리프", "롯데캐슬나리벡시티": "나리벡", "북수원디에트르더리체2": "북수원",
         "고양창릉S5": "고양", "경산상방공원호반써밋1단지": "경산", "탕정푸르지오센터파크": "탕정", "오산세교아테라": "오산",
         "분당퍼스트빌리지": "분당", "지웰엘리움양주덕계역": "지웰", "철산역자이": "철산", "판교테크노밸리중흥S": "판교", "동탄파라곤3차": "동탄", "군포대야미A2": "군포",
         "청주센트럴파크": "청주센트럴", "청주 센트럴파크": "청주센트럴", "두산위브더제니스": "청주센트럴"}      # 폴더 이름 · 현황판 이름을 한 단지로 (본부장 10-31)
def site_for(h):
    for k, v in SITES.items():
        if k in h: return v
    for v in SITES.values():              # 약칭만 적혀 있어도 잡는다 ("상주 올려줘")
        if v in h: return v
    m = re.search(r"(?<![-\w])jugansa[\\/]([^\\/\"'\s&|;<>]+)", h)     # ai-jugansa(스킬 폴더) · 따옴표 · 명령 기호는 단지가 아니다
    n = m.group(1) if m else ""                # 파일 · 공용 폴더(_fonts · 양식 · 착수 …)는 단지가 아니다
    return n[:5] if n and "." not in n and not n.startswith("_") and n not in NOT_SITE else ""
NOT_SITE = {"ai-office", "tools", "watch", "개척", "매뉴얼", "양식", "요약제안서", "착수", "통합제안서", "행사장비용", "협력사실적"}
# ── 단지 보드: jugansa/입찰현황판.md 의 '진행 중' 표에서 마감 · PT · 제출 여부를 읽는다 ──
BOARD_FILE = [None]          # 찾은 현황판 경로 (SessionStart 의 cwd · 환경변수 JUGANSA_DIR · 이 폴더 위쪽 · 기본 경로 순으로 찾음)
DEFAULT_JUGANSA = r"C:\본부장\Claude_Code\edge-company\jugansa"   # 스킬 폴더에서 켜거나 C:\본부장 에서 세션을 열어도 보드가 뜨게
def find_board(start=None):
    cands = []
    if os.environ.get("JUGANSA_DIR"): cands.append(os.path.join(os.environ["JUGANSA_DIR"], "입찰현황판.md"))
    for base in [start, HERE]:
        if not base: continue
        d = os.path.abspath(base)
        for _ in range(6):
            cands.append(os.path.join(d, "입찰현황판.md")); cands.append(os.path.join(d, "jugansa", "입찰현황판.md")); d = os.path.dirname(d)
    cands.append(os.path.join(DEFAULT_JUGANSA, "입찰현황판.md"))
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

STAGE_KEY = {"발송대기": "ready", "개척": "scout", "착수": "analysis", "착수분석": "analysis", "제작": "build", "빌드": "build", "검증": "audit",
             "발송": "mail", "PT": "pt", "관제": "retro", "결과": "retro", "결과·관제": "retro"}

def board():
    f = find_board()
    if not f: return {"file": "", "sites": []}
    today = datetime.date.today(); rows = []; on = False
    try: lines = open(f, encoding="utf-8").read().splitlines()
    except OSError: return {"file": f, "sites": []}
    # '1-1. 단계' 표: | 단지 | 단계 | 근거 | → 단지 이름 → 작업대 키
    stage_of, son = {}, False
    for ln in lines:
        if ln.startswith("| 단지 | 단계 |"): son = True; continue
        if son and not ln.startswith("|"): son = False
        if not son or ln.startswith("|---") or ln.startswith("| ---"): continue
        c = [x.strip() for x in ln.strip().strip("|").split("|")]
        w = re.sub(r"[(（].*", "", c[1]).replace(" ", "") if len(c) >= 2 else ""      # '빌드(확인본)' → 빌드 (본부장 10-31)
        if STAGE_KEY.get(w): stage_of[c[0]] = STAGE_KEY[w]
    for ln in lines:
        if ln.startswith("| 단지 |") and "제출 마감" in ln: on = True; continue
        if on and not ln.startswith("|"): on = False
        if not on or ln.startswith("|---") or ln.startswith("| ---"): continue
        c = [x.strip() for x in ln.strip().strip("|").split("|")]
        if len(c) < 7: continue
        name, hh, q, due, pt, status, rest = c[0], c[1], c[2], c[3], c[5], c[6], " ".join(c[7:])
        short = site_for(name) or re.sub(r"\s*\(.*$", "", name)[:4].strip()
        d, tm = parse_date(due, today)
        done = "✅" in status or "✅" in rest or "제출 완료" in status
        dday = (d - today).days if d else None
        ptx = re.sub(r"\*", "", pt); ptd, ptt = parse_date(ptx, today)
        # PT 확정 = 현황판 '단계' 표가 PT(서류심사 통과 · 일정 통보) + PT 칸에 날짜 → 보드 맨 위 강조 · D-3 ~ D-1 알림
        head, _, more = ptx.partition(" · ")
        place = re.sub(r"^.*?\d{1,2}\.\d{1,2}(?:\([^)]*\))?(?:\s*\d{1,2}:\d{2})?\s*", "", head).strip()
        rows.append({"site": short, "name": name, "hh": hh, "due": re.sub(r"\*", "", due), "dday": dday, "time": tm,
                     "pt": ptx[:28], "pt_dday": (ptd - today).days if ptd else None, "done": done,
                     "stage": stage_of.get(name, ""), "pt_ok": bool(ptd) and stage_of.get(name) == "pt",
                     "pt_date": ptd.isoformat() if ptd else "", "pt_time": ptt, "pt_place": place, "pt_more": more})
    rows.sort(key=lambda r: (not (r["pt_ok"] and r["pt_dday"] >= 0), r["pt_dday"] if r["pt_ok"] else 0,
                             r["done"], r["dday"] if r["dday"] is not None else 999))
    return {"file": f, "today": today.isoformat(), "sites": rows}

# ── PT 확정 알림: PT 3일 전 · 2일 전 · 1일 전 × 10:00 · 16:00 (작업 스케줄러가 --pt-alert 로 부름 → 윈도우 알림) ──
PT_ALERT_DAYS, PT_ALERT_HOURS = (3, 2, 1), (10, 16)
WD = "월화수목금토일"
def pt_line(r):
    d = datetime.date.fromisoformat(r["pt_date"])
    when = f"{d.month}.{d.day:02d}({WD[d.weekday()]})" + (f" {r['pt_time']}" if r["pt_time"] else "")
    return f"{r['name']} 2차 PT · {when}" + (f" · {r['pt_place']}" if r["pt_place"] else "") + (f" · {r['pt_more']}" if r["pt_more"] else "")
def pt_alerts():
    return [(r["pt_dday"], pt_line(r)) for r in board()["sites"] if r["pt_ok"] and r["pt_dday"] in PT_ALERT_DAYS]
def toast(title, body):
    import subprocess                              # 윈도우 기본 알림 (PowerShell · 외부 전송 없음)
    ps = ("[Windows.UI.Notifications.ToastNotificationManager,Windows.UI.Notifications,ContentType=WindowsRuntime]>$null;"
          "$x=[Windows.UI.Notifications.ToastNotificationManager]::GetTemplateContent([Windows.UI.Notifications.ToastTemplateType]::ToastText02);"
          "$t=$x.GetElementsByTagName('text');$t.Item(0).AppendChild($x.CreateTextNode($env:PT_T))>$null;$t.Item(1).AppendChild($x.CreateTextNode($env:PT_B))>$null;"
          "$a='{1AC14E77-02E7-4E5D-B744-2EB1AE5198B7}\\WindowsPowerShell\\v1.0\\powershell.exe';"
          "[Windows.UI.Notifications.ToastNotificationManager]::CreateToastNotifier($a).Show([Windows.UI.Notifications.ToastNotification]::new($x))")
    subprocess.run(["powershell", "-NoProfile", "-WindowStyle", "Hidden", "-Command", ps],
                   env={**os.environ, "PT_T": title, "PT_B": body}, creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
def pt_alert_main(force=False):
    al = pt_alerts()
    if not al and force: al = [(0, "(시험) PT 확정 단지가 D-3 ~ D-1 이 아니어도 알림이 뜨는지 확인")]
    for dd, line in al:
        toast(f"🎤 PT D-{dd} · 2차 PT 확정" if dd else "🎤 PT 알림 시험", line)
        try:                                        # 오피스가 켜져 있으면 메모로도 띄운다
            import urllib.request
            urllib.request.urlopen(urllib.request.Request(f"http://{HOST}:{PORT}/sim", json.dumps({"kind": "memo", "memo_type": "pt", "label": f"PT D-{dd} · " + line}, ensure_ascii=False).encode(), {"Content-Type": "application/json"}), timeout=2)
        except OSError: pass
    print("\n".join(f"D-{d} {l}" for d, l in al) or "알림 없음")

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

INTAKE = r"[\\/]uploads[\\/]|[\\/]자료[\\/]|evidence|seal_scan|[\\/]images[\\/]|스크랩"      # 본부장이 넣어 준 자료 폴더
INTAKE_EXT = r"\.(jpe?g|png|webp|pdf|hwpx?|docx?|xlsx?)$"     # 단계 이름이 없는 그림 · 문서
INTAKE_PROMPT = r"올렸|올려|올린|자료|사진|이미지|캡처|스크랩|https?://"
MAIL_PROMPT = r"메일|발송|보내|보낸|보냈|압축|zip|첨부"      # 메일 검사 · 발송 질문 = 발송팀 (본부장 10-31 '발송팀이 일을 안 한다')
LOG_CMD = r"git (commit|push|log)|입찰현황판|events\.log"
def later(ev, sec):                     # 다른 신호 뒤에 한 번 더 (화면에 팀이 움직이게)
    threading.Timer(sec, lambda: push(ev)).start()

def stage_for(tool, ti):
    """본부장 직접 작업의 단계 추정. 못 정하면 본부장실."""
    if tool == "Read" and re.search(INTAKE, str((ti or {}).get("file_path", "")), re.I): return "scout"       # 본부장 자료 확인 = 개척팀 겸업 (본부장 10-31)
    if tool in ("Bash", "PowerShell") and re.search(LOG_CMD, str((ti or {}).get("command", ""))): return "retro"   # 커밋 · 기록 = 결과·관제팀
    if tool == "Skill":
        s = str((ti or {}).get("skill", ""))
        if s == "court": return "audit"
        if s == "kickoff": return "analysis"
    if tool == "Agent":
        return TEAM_ROOM.get(str((ti or {}).get("subagent_type", "")), "office")
    h = haystack(tool, ti)
    for room, rx in PATH_RULES:
        if re.search(rx, h, re.I): return room
    if tool == "Read" and re.search(INTAKE_EXT, str((ti or {}).get("file_path", "")), re.I): return "scout"   # mail_final.png 처럼 단계 이름이 있으면 그 팀이 먼저
    return "office"

LOCK = threading.Lock(); EVENTS = []; SEQ = [0]; SEEN = set()
STICKY = {}                                      # 세션 → (직전 단계, 시각)
WORK_TOOLS = {"Edit", "Write", "MultiEdit", "Read", "Bash", "PowerShell", "Grep", "Glob", "NotebookEdit"}
LOG_PATH = os.path.join(HERE, "events.log")

def push(ev):
    with LOCK:
        SEQ[0] += 1; ev["id"] = SEQ[0]; ev["t"] = time.time(); EVENTS.append(ev); del EVENTS[:-600]
    try:
        with open(LOG_PATH, "a", encoding="utf-8") as f: f.write(json.dumps(ev, ensure_ascii=False) + "\n")
    except OSError: pass

def translate(h):
    name = h.get("hook_event_name", ""); tool = h.get("tool_name", ""); ti = h.get("tool_input") or {}
    aid = h.get("agent_id") or ""                # 서브에이전트(팀) 안에서 온 신호면 agent_id · agent_type 이 붙어 있다
    agent = h.get("agent_type") or ""
    team = agent or ("팀" if aid else "")
    if name == "SubagentStart":
        SEEN.add(aid)
        return {"kind": "team_start", "team": agent, "team_kr": TEAM_KR.get(agent, agent), "room": TEAM_ROOM.get(agent, "analysis"), "agent_id": aid, "site": site_for(str(h.get("cwd", "")))}
    if name == "SubagentStop":
        SEEN.discard(aid)
        return {"kind": "team_stop", "team": agent, "room": TEAM_ROOM.get(agent, "analysis"), "agent_id": aid}
    if name == "PreToolUse":
        if aid:
            guess = stage_for(tool, ti)
            room = TEAM_ROOM.get(agent) or (guess if guess != "office" else "analysis")
            ev = {"kind": "work", "who": CHAR_OF_ROOM.get(room, "analyst"), "room": room,
                  "team": team, "team_kr": TEAM_KR.get(agent, agent or "지원팀"), "tool": tool, "label": label_for(tool, ti), "agent_id": aid, "site": site_for(haystack(tool, ti))}
            if aid not in SEEN:                  # 시작 신호(SubagentStart)를 못 받은 팀도 첫 작업 때 출근시킨다
                SEEN.add(aid); push({**ev, "kind": "team_start"})
            return ev
        room = stage_for(tool, ti); sid = h.get("session_id", "")
        if room != "office": STICKY[sid] = (room, time.time())
        elif tool in WORK_TOOLS and sid in STICKY and time.time() - STICKY[sid][1] < 300: room = STICKY[sid][0]   # 단계가 안 보이는 잔손질은 그 세션의 직전 단계로
        return {"kind": "work", "who": BOSS, "room": room, "team": "", "team_kr": "본부장", "tool": tool, "label": label_for(tool, ti), "site": site_for(haystack(tool, ti)), "sid": sid[:8],
                "call": str(ti.get("subagent_type", "")) if tool == "Agent" else ""}
    if name == "PostToolUse":
        return {"kind": "done", "who": CHAR_OF_ROOM[TEAM_ROOM.get(team, "analysis")] if team else BOSS, "tool": tool}
    if name == "Notification":
        return {"kind": "memo", "memo_type": h.get("notification_type", "notice"), "label": short(h.get("title") or h.get("message") or "알림", 36)}
    if name in ("Stop", "SessionEnd"):
        if name == "Stop": later({"kind": "work", "who": BOSS, "room": "retro", "team": "", "team_kr": "결과·관제", "tool": "기록", "label": "작업 기록 · 현황 정리", "site": ""}, 2.5)
        return {"kind": "rest", "reason": name, "sid": str(h.get("session_id", ""))[:8]}     # 그 세션 일만 쉬게 (다른 세션의 발송 · 제작은 계속)
    if name == "SessionStart":
        find_board(h.get("cwd"))
        return {"kind": "start", "source": h.get("source", ""), "model": h.get("model", ""), "cwd": os.path.basename(h.get("cwd", "") or "")}
    if name == "UserPromptSubmit":
        if re.search(MAIL_PROMPT, str(h.get("prompt", "")), re.I):
            later({"kind": "work", "who": BOSS, "room": "mail", "team": "", "team_kr": "발송팀", "tool": "검사", "label": "메일 · 첨부 확인",
                   "site": site_for(str(h.get("prompt", "")) + " " + str(h.get("cwd", ""))), "sid": str(h.get("session_id", ""))[:8]}, 0.6)
        elif re.search(INTAKE_PROMPT, str(h.get("prompt", ""))):
            later({"kind": "work", "who": BOSS, "room": "scout", "team": "", "team_kr": "개척팀", "tool": "자료", "label": "본부장 자료 확인", "site": site_for(str(h.get("prompt", "")))}, 0.6)
        return {"kind": "prompt", "label": short(h.get("prompt", ""), 40), "site": site_for(str(h.get("prompt", "")) + " " + str(h.get("cwd", "")))}
    return None

MIME = {".html": "text/html; charset=utf-8", ".png": "image/png", ".js": "text/javascript", ".json": "application/json", ".svg": "image/svg+xml"}

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
        if u.path.startswith("/v4/"): return self._file(os.path.join("static", "v4", os.path.basename(u.path)))     # v4 오피스 그림 · 배치
        if u.path in ("/v3", "/v3/"): return self._file("index_v3.html")                                          # 옛 오픈 플로어 화면
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
    if "--pt-alert" in sys.argv: pt_alert_main(force="--test" in sys.argv)
    else: main()

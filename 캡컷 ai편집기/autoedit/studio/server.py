"""엣지 스튜디오 — 자동 편집기 화면 프로그램 (로컬 웹 서버 + 앱 창).

영상은 이 PC 안에서만 처리된다. 브라우저(Edge)를 '앱 모드' 창으로 띄워 일반 프로그램처럼 보인다.

흐름: 영상 끌어다 놓기 → 분석(컷·자막·AI 오타교정) → 자막 편집(글자·띄어쓰기·줄바꿈·
위치·정렬·강조·효과음) → 스타일 고르기 → 완성본(본편+숏츠+썸네일) 만들기.
"""

from __future__ import annotations

import json
import logging
import mimetypes
import os
import re
import shutil
import subprocess
import sys
import threading
import time
import traceback
import urllib.parse
import uuid
import webbrowser
from dataclasses import asdict
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any, Dict, List, Optional

from .. import ffmpeg as ff
from ..config import Config, DEFAULT_VOCAB
from ..utils import logger

HERE = Path(__file__).resolve().parent
APP_ROOT = HERE.parent.parent  # 캡컷 ai편집기/
PORT = int(os.environ.get("EDGE_STUDIO_PORT", "8817"))


def _code_version() -> str:
    """프로그램 파일이 바뀌면 달라지는 버전 표식 (업데이트 감지용)."""
    import hashlib

    h = hashlib.md5()
    for f in sorted((HERE.parent).rglob("*.py")) + [HERE / "index.html"]:
        try:
            h.update(f"{f.name}:{f.stat().st_mtime_ns}".encode())
        except OSError:
            pass
    return h.hexdigest()[:10]


APP_VERSION = _code_version()


# ───────────────────────────── 경로 ─────────────────────────────


def _desktop() -> Path:
    try:
        import winreg  # type: ignore

        with winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders",
        ) as k:
            return Path(winreg.QueryValueEx(k, "Desktop")[0])
    except Exception:  # noqa: BLE001
        return Path.home() / "Desktop"


OUT_ROOT = _desktop() / "캡컷_완성본"
DATA_DIR = Path(os.environ.get("LOCALAPPDATA", Path.home())) / "EdgeStudio"
UPLOADS = DATA_DIR / "uploads"
PREVIEWS = DATA_DIR / "previews"
SETTINGS_FILE = DATA_DIR / "settings.json"
for _d in (UPLOADS, PREVIEWS):
    _d.mkdir(parents=True, exist_ok=True)


def _safe_name(name: str) -> str:
    name = re.sub(r'[\\/:*?"<>|]+', "_", name).strip() or "영상"
    return name[:80]


def _allowed(p: Path) -> bool:
    try:
        rp = p.resolve()
    except Exception:  # noqa: BLE001
        return False
    roots = [OUT_ROOT.resolve(), DATA_DIR.resolve(), Path(os.environ.get("TEMP", DATA_DIR)).resolve()]
    return any(str(rp).lower().startswith(str(r).lower()) for r in roots)


# ───────────────────────────── 설정 저장 ─────────────────────────────

DEFAULT_SETTINGS: Dict[str, Any] = {
    "cut": "gentle",          # none / gentle / normal / strong
    "accuracy": "small",      # base / small / medium
    "smart_edit": True,
    "ai_typo_fix": True,
    "vocab": list(DEFAULT_VOCAB),
    "style": "pop",
    "pos": "bottom",
    "align": "center",
    "scale": 100,
    "offset": 0,
    "shorts": 3,
    "shorts_subs": True,
    "bgm": True,
    "bgm_choice": "mood:bright",  # mood:<분위기> / file:<내 음악> / ""
    "genre": "promo",
    "color_fix": True,
    "stabilize": False,
    "punch_zoom": True,
    "speed": 1.0,
    "auto_products": True,
    "card_opening": False,
    "card_ending": False,
    "card_theme": "blur",
    "card_title": "",
    "card_subtitle": "",
    "card_company": "엣지컴퍼니",
    "card_phone": "",
    "card_site": "",
    "card_message": "박람회에서 뵙겠습니다",
    "card_logo": "",
    "card_qr": "",
    "auto_sfx": True,
    "sfx_volume": 0.5,
}


def load_settings() -> Dict[str, Any]:
    s = dict(DEFAULT_SETTINGS)
    try:
        s.update(json.loads(SETTINGS_FILE.read_text(encoding="utf-8")))
    except Exception:  # noqa: BLE001
        pass
    return s


def save_settings(upd: Dict[str, Any]) -> Dict[str, Any]:
    s = load_settings()
    s.update({k: v for k, v in upd.items() if k in DEFAULT_SETTINGS})
    SETTINGS_FILE.write_text(json.dumps(s, ensure_ascii=False, indent=1), encoding="utf-8")
    return s


def has_api_key() -> bool:
    from ..config import SmartEditConfig
    from ..smart_edit import _resolve_api_key

    return bool(_resolve_api_key(SmartEditConfig()))


def build_config(opts: Dict[str, Any]) -> Config:
    cfg_path = APP_ROOT / "config.yaml"
    cfg = Config.load(cfg_path if cfg_path.exists() else None)
    cut = opts.get("cut", "gentle")
    pad, gap = {"gentle": (0.25, 0.6), "normal": (0.12, 0.3), "strong": (0.08, 0.18)}.get(cut, (0.25, 0.6))
    cfg.silence.enabled = cut != "none"  # 안 자름 = 자막·효과음만
    cfg.silence.speech_pad, cfg.silence.bridge_gap = pad, gap
    cfg.subtitle.model = opts.get("accuracy", "small")
    cfg.subtitle.ai_typo_fix = bool(opts.get("ai_typo_fix", True))
    cfg.subtitle.vocab = [v for v in opts.get("vocab", DEFAULT_VOCAB) if str(v).strip()]
    cfg.smart_edit.enabled = bool(opts.get("smart_edit", True))
    style = opts.get("style", "pop")
    cfg.subtitle.burn_in = style != "none"
    cfg.subtitle.style = style if style != "none" else "pop"
    cfg.subtitle.pos = opts.get("pos", "bottom")
    cfg.subtitle.align = opts.get("align", "center")
    cfg.subtitle.scale = int(opts.get("scale", 100))
    cfg.subtitle.offset = float(opts.get("offset", 0))
    cfg.subtitle.auto_sfx = bool(opts.get("auto_sfx", True))
    cfg.subtitle.sfx_volume = float(opts.get("sfx_volume", 0.5))
    cfg.subtitle.punch_zoom = bool(opts.get("punch_zoom", True))
    cfg.video.color = bool(opts.get("color_fix", True))
    cfg.video.stabilize = bool(opts.get("stabilize", False))
    cfg.output.speed = float(opts.get("speed", 1.0) or 1.0)
    cc = cfg.cards
    cc.opening, cc.ending = bool(opts.get("card_opening")), bool(opts.get("card_ending"))
    cc.theme = opts.get("card_theme", "blur")
    cc.title, cc.subtitle = opts.get("card_title", ""), opts.get("card_subtitle", "")
    cc.company, cc.phone = opts.get("card_company", "엣지컴퍼니"), opts.get("card_phone", "")
    cc.site, cc.message = opts.get("card_site", ""), opts.get("card_message", "")
    cc.logo, cc.qr = opts.get("card_logo", ""), opts.get("card_qr", "")
    n = int(opts.get("shorts", 3))
    cfg.shorts.enabled = n > 0
    cfg.shorts.count = max(1, n)
    cfg.shorts.burn_subtitles = bool(opts.get("shorts_subs", True)) and style != "none"
    cfg.branding.enabled = True
    from ..bgm import resolve as bgm_resolve

    track = bgm_resolve(str(opts.get("bgm_choice") or ""), APP_ROOT / "assets") if opts.get("bgm", True) else None
    cfg.branding.bgm = str(track) if track else None
    return cfg


# ───────────────────────────── 작업(Job) ─────────────────────────────

ANALYZE_STEPS = [
    ("prep", "영상 준비 · 음질 개선"),
    ("asr", "음성 인식 (자막 받아쓰기)"),
    ("smart", "AI 편집 판단 (반복·잡담 찾기)"),
    ("cut", "컷 편집 (무음·추임새 제거)"),
    ("typo", "AI 오타 교정 · 핵심 단어"),
]
RENDER_STEPS = [
    ("burn", "자막 입히기"),
    ("sfx", "효과음"),
    ("shorts", "숏츠 만들기"),
    ("brand", "인트로 · 배경음악"),
    ("thumb", "썸네일"),
]


class Job:
    def __init__(self, src: Path, name: str):
        self.id = uuid.uuid4().hex[:10]
        self.src = src
        self.name = name
        self.out_dir = OUT_ROOT / name
        self.stage = "ready"       # ready / analyzing / review / rendering / done / error
        self.steps: List[Dict[str, Any]] = []
        self.step_key = ""
        self.progress = 0.0
        self.detail = ""
        self.error = ""
        self.log: List[str] = []
        self.started = 0.0
        self.clean_video: Optional[Path] = None
        self.captions: List[Dict[str, Any]] = []
        self.keywords: List[str] = []
        self.overlays: List[Dict[str, Any]] = []  # 로고·스티커
        self.cut: Optional[Dict[str, Any]] = None  # 컷 타임라인 {source, keep, total}
        self.result: Dict[str, Any] = {}
        self.duration = 0.0
        self.poster: Optional[Path] = None

    def public(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "stage": self.stage,
            "steps": self.steps,
            "step": self.step_key,
            "progress": round(self.progress, 1),
            "detail": self.detail,
            "error": self.error,
            "log": self.log[-60:],
            "elapsed": round(time.time() - self.started, 1) if self.started else 0,
            "clean_video": str(self.clean_video) if self.clean_video else None,
            "out_dir": str(self.out_dir),
            "result": self.result,
            "duration": self.duration,
            "poster": str(self.poster) if self.poster else None,
            "n_captions": len(self.captions),
        }

    # 단계 표시
    def set_steps(self, steps):
        self.steps = [{"key": k, "label": l, "state": "wait"} for k, l in steps]

    def enter(self, key: str, progress: float):
        found = False
        for s in self.steps:
            if s["key"] == key:
                s["state"] = "run"
                found = True
            elif not found and s["state"] in ("wait", "run"):
                s["state"] = "done"
        self.step_key = key
        self.progress = max(self.progress, progress)

    def finish_steps(self):
        for s in self.steps:
            if s["state"] in ("run", "wait"):
                s["state"] = "done" if s["state"] == "run" else "skip"


JOBS: Dict[str, Job] = {}
WORK_LOCK = threading.Lock()  # 한 번에 한 작업 (CPU를 다 쓰므로)


class JobLog(logging.Handler):
    """파이프라인 로그 → 화면 진행 단계·퍼센트."""

    ANALYZE = [
        (r"음질|입력 영상|화면 밝기|손떨림", "prep", 3),
        (r"Whisper 모델|음성 분석|음성 인식 시작", "asr", 8),
        (r"AI 스마트 편집", "smart", 48),
        (r"과감한 컷|무음 구간", "cut", 55),
        (r"오타 교정|메타데이터", "typo", 85),
    ]
    RENDER = [
        (r"자막 번인", "burn", 5),
        (r"효과음", "sfx", 35),
        (r"숏츠", "shorts", 40),
        (r"인트로|브랜딩|BGM", "brand", 75),
        (r"썸네일", "thumb", 92),
    ]

    def __init__(self, job: Job, table):
        super().__init__(logging.INFO)
        self.job, self.table = job, table

    def emit(self, record):
        try:
            msg = record.getMessage()
        except Exception:  # noqa: BLE001
            return
        j = self.job
        j.log.append(time.strftime("%H:%M:%S ") + msg)
        j.log = j.log[-300:]
        for pat, key, pct in self.table:
            if re.search(pat, msg):
                if j.step_key != key:
                    j.detail = ""
                j.enter(key, pct)
                break
        m = re.search(r"자막 인식 중\.\.\. (\d+)%", msg)
        if m:
            j.progress = max(j.progress, 8 + int(m.group(1)) * 0.38)
            j.detail = f"받아쓰기 {m.group(1)}%"
        m = re.search(r"숏츠 (\d+)/(\d+) 생성", msg)
        if m:
            a, b = int(m.group(1)), int(m.group(2))
            j.progress = max(j.progress, 40 + 35 * (a - 1) / max(b, 1))
            j.detail = f"숏츠 {a}/{b}"


def _attach(job: Job, table) -> JobLog:
    h = JobLog(job, table)
    logger.addHandler(h)
    logger.setLevel(logging.INFO)

    def hook(sec: float):
        if job.duration:
            job.detail = f"인코딩 {int(sec // 60)}:{int(sec % 60):02d} / {int(job.duration // 60)}:{int(job.duration % 60):02d}"

    ff.PROGRESS_HOOK = hook
    return h


def _detach(h: JobLog):
    logger.removeHandler(h)
    ff.PROGRESS_HOOK = None


def _run_analyze(job: Job, opts: Dict[str, Any]):
    from ..pipeline import process

    with WORK_LOCK:
        job.stage, job.started, job.progress, job.error = "analyzing", time.time(), 0, ""
        job.set_steps(ANALYZE_STEPS)
        h = _attach(job, JobLog.ANALYZE)
        try:
            cfg = build_config(opts)
            if not has_api_key():
                cfg.smart_edit.enabled = False
                cfg.subtitle.ai_typo_fix = False
            job.out_dir.mkdir(parents=True, exist_ok=True)
            res = process(job.src, job.out_dir, cfg, assets_dir=APP_ROOT / "assets", review=True)
            job.clean_video = res.clean_video
            from ..transcribe import captions_from_json

            if res.captions_json and res.captions_json.exists():
                job.captions = json.loads(res.captions_json.read_text(encoding="utf-8"))
            job.keywords = sorted(res.keywords)
            job.cut = res.cut
            job.duration = ff.probe_duration(res.clean_video) if res.clean_video else 0
            _save_project(job)
            job.finish_steps()
            job.progress = 100
            job.stage = "review"
            job.detail = ""
        except Exception as exc:  # noqa: BLE001
            job.stage, job.error = "error", f"{exc}"
            job.log.append(traceback.format_exc())
        finally:
            _detach(h)


def _run_render(job: Job, opts: Dict[str, Any]):
    from ..pipeline import render_final
    from ..transcribe import captions_from_json

    with WORK_LOCK:
        job.stage, job.started, job.progress, job.error = "rendering", time.time(), 0, ""
        job.result = {}
        job.set_steps(RENDER_STEPS)
        h = _attach(job, JobLog.RENDER)
        try:
            cfg = build_config(opts)
            caps = captions_from_json(job.captions)
            res = render_final(
                job.clean_video, caps, job.out_dir, cfg,
                keywords=set(job.keywords), assets_dir=APP_ROOT / "assets",
                overlays=job.overlays,
            )
            job.finish_steps()
            job.progress = 100
            job.result = {
                "final": str(res.final_video) if res.final_video else None,
                "shorts": [str(s) for s in res.shorts],
                "thumbnail": str(res.thumbnail) if res.thumbnail else None,
                "srt": str(res.srt) if res.srt else None,
                "steps": res.steps,
            }
            meta = job.out_dir / f"{job.name}_업로드정보.txt"
            if meta.exists():
                job.result["meta"] = meta.read_text(encoding="utf-8")[:4000]
            job.stage = "done"
            job.detail = ""
        except Exception as exc:  # noqa: BLE001
            job.stage, job.error = "error", f"{exc}"
            job.log.append(traceback.format_exc())
        finally:
            _detach(h)


def _save_project(job: Job):
    """다시 열어 고칠 수 있게 프로젝트 정보 저장."""
    data = {
        "name": job.name,
        "clean_video": str(job.clean_video) if job.clean_video else None,
        "keywords": job.keywords,
        "overlays": job.overlays,
        "cut": job.cut,
        "saved": time.strftime("%Y-%m-%d %H:%M"),
    }
    (job.out_dir / "_project.json").write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")
    if job.captions:
        (job.out_dir / f"{job.name}_자막.json").write_text(
            json.dumps(job.captions, ensure_ascii=False, indent=1), encoding="utf-8"
        )


def _save_version(job: Job, label: str, settings: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """임시저장: 지금 자막·로고·디자인 설정을 따로 보관 (덮어쓰지 않음)."""
    d = job.out_dir / "_versions"
    d.mkdir(parents=True, exist_ok=True)
    vid = time.strftime("%Y%m%d-%H%M%S")
    data = {
        "id": vid,
        "label": (label or "").strip()[:40],
        "saved": time.strftime("%m/%d %H:%M:%S"),
        "captions": job.captions,
        "overlays": job.overlays,
        "settings": settings or {},
    }
    (d / f"{vid}.json").write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
    # 너무 많아지면 오래된 것부터 정리 (최근 50개 보관)
    files = sorted(d.glob("*.json"))
    for old in files[:-50]:
        old.unlink(missing_ok=True)
    return {"id": vid, "saved": data["saved"]}


def _list_versions(job: Job) -> List[Dict[str, Any]]:
    d = job.out_dir / "_versions"
    out = []
    for f in sorted(d.glob("*.json"), reverse=True) if d.exists() else []:
        try:
            j = json.loads(f.read_text(encoding="utf-8"))
            out.append({"id": j["id"], "label": j.get("label", ""), "saved": j.get("saved", ""),
                        "n": len(j.get("captions", [])), "logos": len(j.get("overlays", []))})
        except Exception:  # noqa: BLE001
            continue
    return out


def list_projects() -> List[Dict[str, Any]]:
    out = []
    if not OUT_ROOT.exists():
        return out
    for d in OUT_ROOT.iterdir():
        pj = d / "_project.json"
        if not pj.exists():
            continue
        try:
            info = json.loads(pj.read_text(encoding="utf-8"))
        except Exception:  # noqa: BLE001
            continue
        final = d / f"{info.get('name', d.name)}_edited.mp4"
        thumb = d / f"{info.get('name', d.name)}_썸네일.png"
        out.append(
            {
                "dir": str(d),
                "name": info.get("name", d.name),
                "saved": info.get("saved", ""),
                "done": final.exists(),
                "thumb": str(thumb) if thumb.exists() else None,
                "mtime": pj.stat().st_mtime,
            }
        )
    out.sort(key=lambda x: -x["mtime"])
    return out[:12]


def open_project(dir_path: Path) -> Job:
    info = json.loads((dir_path / "_project.json").read_text(encoding="utf-8"))
    name = info.get("name", dir_path.name)
    clean = Path(info["clean_video"]) if info.get("clean_video") else dir_path / f"{name}_clean.mp4"
    job = Job(clean, name)
    job.out_dir = dir_path
    job.clean_video = clean
    job.keywords = info.get("keywords", [])
    job.overlays = info.get("overlays", [])
    job.cut = info.get("cut")
    cj = dir_path / f"{name}_자막.json"
    job.captions = json.loads(cj.read_text(encoding="utf-8")) if cj.exists() else []
    job.duration = ff.probe_duration(clean) if clean.exists() else 0
    job.stage = "review"
    final = dir_path / f"{name}_edited.mp4"
    if final.exists():
        shorts = sorted((dir_path / "shorts").glob("*.mp4")) if (dir_path / "shorts").exists() else []
        thumb = dir_path / f"{name}_썸네일.png"
        job.result = {
            "final": str(final),
            "shorts": [str(s) for s in shorts],
            "thumbnail": str(thumb) if thumb.exists() else None,
        }
    JOBS[job.id] = job
    return job


# ───────────────────────────── 미리보기 ─────────────────────────────


def _poster(video: Path, out: Path, at: float) -> Optional[Path]:
    try:
        ff.run(["ffmpeg", "-y", "-ss", f"{at:.2f}", "-i", str(video), "-frames:v", "1",
                "-vf", "scale=960:-2", "-q:v", "3", str(out)])
        return out if out.exists() else None
    except Exception:  # noqa: BLE001
        return None


def style_preview(job: Optional[Job], style: str, opts: Dict[str, Any]) -> Path:
    """실제 영상 프레임 위에 스타일을 입힌 미리보기 이미지."""
    from ..styles import Layout, estimate_words, fonts_dir, write_styled_ass
    from ..subtitles import _escape_filter_path
    from ..transcribe import Caption, captions_from_json

    text = "아크로 슬림 실링팬 소음은 단 24dB"
    emph = None
    at = 1.0
    video = None
    if job and job.clean_video and job.clean_video.exists():
        video = job.clean_video
        caps = captions_from_json(job.captions) if job.captions else []
        # 강조가 들어간 자막을 우선, 첫 구절(약 18자)만 잘라서 보여준다
        cand = sorted(caps, key=lambda c: (not c.emph, c.start))
        if cand:
            c = cand[0]
            toks, n = [], 0
            for tk in c.text.split():
                if toks and n + len(tk) + 1 > 18:
                    break
                toks.append(tk)
                n += len(tk) + 1
            text, at = " ".join(toks), c.start
            emph = {k: v for k, v in (c.emph or {}).items() if k < len(toks)}
    cap = Caption(0.0, 3.0, text, emph=emph)
    cap.words = estimate_words(cap)
    lay = Layout.from_dict(opts)
    key = f"{job.id if job else 'demo'}_{style}_{lay.pos}_{lay.align}_{lay.scale}_{lay.offset}_{abs(hash(text)) % 99999}"
    out = PREVIEWS / f"{key}.jpg"
    if out.exists():
        return out
    W, H = (1920, 1080)
    if video:
        dims = ff.probe_dimensions(video)
        if dims:
            W, H = dims
    ass = PREVIEWS / f"{key}.ass"
    write_styled_ass([cap], ass, style, W, H, layout=lay)
    vf = f"subtitles='{_escape_filter_path(ass)}'"
    if fonts_dir().exists():
        vf += f":fontsdir='{_escape_filter_path(fonts_dir())}'"
    vf += ",scale=960:-2"
    if video:
        src = ["-ss", f"{max(0.0, at):.2f}", "-t", "3", "-i", str(video)]
    else:
        src = ["-f", "lavfi", "-i",
               f"gradients=s={W}x{H}:c0=0x8aa0b4:c1=0x2a3440:x0=0:y0=0:x1={W}:y1={H}:d=3"]
    ff.run(["ffmpeg", "-y", *src, "-vf", vf, "-ss", "1.2", "-frames:v", "1", "-q:v", "3", str(out)])
    return out


# ───────────────────────────── HTTP ─────────────────────────────


class Handler(BaseHTTPRequestHandler):
    server_version = "EdgeStudio/1.0"

    def log_message(self, fmt, *args):  # 조용히
        pass

    # 응답 도우미
    def _json(self, obj, code=200):
        body = json.dumps(obj, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def _body(self) -> Dict[str, Any]:
        n = int(self.headers.get("Content-Length") or 0)
        if not n:
            return {}
        return json.loads(self.rfile.read(n).decode("utf-8") or "{}")

    def _file(self, p: Path, ctype: Optional[str] = None):
        if not p.exists() or not p.is_file():
            return self._json({"error": "파일 없음"}, 404)
        size = p.stat().st_size
        ctype = ctype or mimetypes.guess_type(str(p))[0] or "application/octet-stream"
        rng = self.headers.get("Range")
        start, end = 0, size - 1
        if rng:
            m = re.match(r"bytes=(\d*)-(\d*)", rng)
            if m:
                if m.group(1):
                    start = int(m.group(1))
                    if m.group(2):
                        end = min(int(m.group(2)), size - 1)
                elif m.group(2):
                    start = max(0, size - int(m.group(2)))
            self.send_response(206)
            self.send_header("Content-Range", f"bytes {start}-{end}/{size}")
        else:
            self.send_response(200)
        length = end - start + 1
        self.send_header("Content-Type", ctype)
        self.send_header("Accept-Ranges", "bytes")
        self.send_header("Content-Length", str(length))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        try:
            with open(p, "rb") as f:
                f.seek(start)
                left = length
                while left > 0:
                    chunk = f.read(min(1 << 20, left))
                    if not chunk:
                        break
                    self.wfile.write(chunk)
                    left -= len(chunk)
        except (ConnectionResetError, BrokenPipeError, ConnectionAbortedError):
            pass

    def _job(self, jid: str) -> Optional[Job]:
        return JOBS.get(jid)

    # 보안: 이 PC의 스튜디오 화면에서 온 요청만 받는다.
    def _guard(self, write: bool) -> bool:
        host = (self.headers.get("Host") or "").lower()
        ok_hosts = {f"127.0.0.1:{PORT}", f"localhost:{PORT}"}
        if host not in ok_hosts:
            # 다른 도메인 이름으로 우회 접속(DNS 리바인딩) 차단
            self._json({"error": "허용되지 않은 접속"}, 403)
            return False
        if write:
            origin = self.headers.get("Origin")
            if origin and urllib.parse.urlparse(origin).netloc.lower() not in ok_hosts:
                self._json({"error": "다른 사이트의 요청은 받지 않습니다"}, 403)
                return False
            # 전용 표식 헤더: 다른 웹사이트는 이 헤더를 붙여 보낼 수 없다(브라우저가 차단)
            if self.headers.get("X-Edge-Studio") != "1":
                self._json({"error": "허용되지 않은 요청"}, 403)
                return False
        return True

    # 라우팅
    def do_GET(self):
        if not self._guard(False):
            return
        u = urllib.parse.urlparse(self.path)
        q = urllib.parse.parse_qs(u.query)
        path = u.path
        try:
            if path in ("/", "/index.html"):
                return self._file(HERE / "index.html", "text/html; charset=utf-8")
            m = re.match(r"^/fonts/([\w\-]+\.(?:ttf|otf))$", path)
            if m:
                from ..styles import fonts_dir

                return self._file(fonts_dir() / m.group(1), "font/" + m.group(1).rsplit(".", 1)[1])
            if path == "/api/ping":
                if q.get("alive"):
                    _touch()
                return self._json({"ok": True, "app": "edge-studio", "version": APP_VERSION})
            if path == "/api/init":
                from ..bgm import MOODS, user_tracks
                from ..director import GENRES
                from ..sfx import SFX_LIST
                from ..styles import EMPHASIS, STYLES, font_available

                return self._json(
                    {
                        "settings": load_settings(),
                        "api_key": has_api_key(),
                        "styles": [
                            {"key": s.key, "label": s.label, "desc": s.desc,
                             "font_ok": font_available(s.font), "text": s.text,
                             "active": s.active, "keyword": s.keyword, "box": s.box,
                             "box_color": s.box_color, "glow": s.glow,
                             "size": s.size, "size_v": s.size_v, "max_chars": s.max_chars,
                             "max_chars_v": s.max_chars_v, "outline": s.outline,
                             "outline_color": s.outline_color, "font": s.font, "bold": s.bold}
                            for s in STYLES.values()
                        ],
                        "emphasis": EMPHASIS,
                        "sfx": {k: v[0] for k, v in SFX_LIST.items()},
                        "sfx_desc": {k: v[1] for k, v in SFX_LIST.items()},
                        "projects": list_projects(),
                        "genres": [{"key": g.key, "label": g.label, "desc": g.desc} for g in GENRES.values()],
                        "bgm_moods": {k: v[0] for k, v in MOODS.items()},
                        "bgm_desc": {k: v[1] for k, v in MOODS.items()},
                        "bgm_files": [p.name for p in user_tracks(APP_ROOT / "assets")],
                        "out_root": str(OUT_ROOT),
                    }
                )
            if path == "/api/projects":
                return self._json(list_projects())
            m = re.match(r"^/api/jobs/(\w+)$", path)
            if m:
                job = self._job(m.group(1))
                return self._json(job.public() if job else {"error": "없음"}, 200 if job else 404)
            m = re.match(r"^/api/jobs/(\w+)/versions$", path)
            if m:
                job = self._job(m.group(1))
                if not job:
                    return self._json({"error": "없음"}, 404)
                return self._json(_list_versions(job))
            m = re.match(r"^/api/jobs/(\w+)/versions/([\w\-]+)$", path)
            if m:
                job = self._job(m.group(1))
                f = job.out_dir / "_versions" / f"{m.group(2)}.json" if job else None
                if not f or not f.exists():
                    return self._json({"error": "없음"}, 404)
                return self._json(json.loads(f.read_text(encoding="utf-8")))
            m = re.match(r"^/api/jobs/(\w+)/captions$", path)
            if m:
                job = self._job(m.group(1))
                if not job:
                    return self._json({"error": "없음"}, 404)
                return self._json({"captions": job.captions, "keywords": job.keywords, "overlays": job.overlays, "cut": job.cut})
            m = re.match(r"^/api/preview/(\w+)\.jpg$", path)
            if m:
                job = self._job(q.get("job", [""])[0])
                opts = {k: v[0] for k, v in q.items()}
                return self._file(style_preview(job, m.group(1), opts), "image/jpeg")
            if path == "/api/products":
                from ..products import load as load_products

                return self._json(load_products(APP_ROOT))
            m = re.match(r"^/api/products/img/(.+)$", path)
            if m:
                from ..products import lib_dir

                return self._file(lib_dir(APP_ROOT) / Path(urllib.parse.unquote(m.group(1))).name)
            m = re.match(r"^/api/card-preview/(opening|ending)\.jpg$", path)
            if m:
                from ..cards import CardInfo, preview_png

                st = {**load_settings(), **{k: v[0] for k, v in q.items()}}
                job = self._job(q.get("job", [""])[0])
                vid = job.clean_video if job and job.clean_video else None
                W, H = (ff.probe_dimensions(vid) if vid else None) or (1920, 1080)
                info = CardInfo(title=st.get("card_title") or (job.name if job else ""), subtitle=st.get("card_subtitle", ""),
                                company=st.get("card_company", ""), phone=st.get("card_phone", ""), site=st.get("card_site", ""),
                                message=st.get("card_message", ""), logo=st.get("card_logo", ""), qr=st.get("card_qr", ""),
                                theme=st.get("card_theme", "blur"))
                return self._file(preview_png(m.group(1), info, vid, W, H), "image/jpeg")
            m = re.match(r"^/api/bgm/(\w+)\.wav$", path)
            if m:
                from ..bgm import MOODS, mood_path

                if m.group(1) not in MOODS:
                    return self._json({"error": "없음"}, 404)
                return self._file(mood_path(m.group(1)), "audio/wav")
            m = re.match(r"^/api/bgmfile/(.+)$", path)
            if m:
                from ..bgm import resolve as bgm_resolve

                f = bgm_resolve("file:" + urllib.parse.unquote(m.group(1)), APP_ROOT / "assets")
                return self._file(f) if f else self._json({"error": "없음"}, 404)
            m = re.match(r"^/api/sfx/(\w+)\.wav$", path)
            if m:
                from ..sfx import sample_path

                return self._file(sample_path(m.group(1)), "audio/wav")
            if path == "/media":
                p = Path(q.get("p", [""])[0])
                if not _allowed(p):
                    return self._json({"error": "허용되지 않은 경로"}, 403)
                return self._file(p)
            return self._json({"error": "없는 주소"}, 404)
        except Exception as exc:  # noqa: BLE001
            traceback.print_exc()
            return self._json({"error": str(exc)}, 500)

    def do_PUT(self):
        if not self._guard(True):
            return
        u = urllib.parse.urlparse(self.path)
        q = urllib.parse.parse_qs(u.query)
        if u.path in ("/api/products", "/api/brand-logo"):
            n = int(self.headers.get("Content-Length") or 0)
            if n > 30 * 1024 * 1024:
                return self._json({"error": "이미지가 너무 큽니다 (30MB 이하)"}, 400)
            data = self.rfile.read(n)
            name = os.path.basename(q.get("name", ["image.png"])[0])
            if os.path.splitext(name)[1].lower() not in (".png", ".jpg", ".jpeg", ".webp"):
                return self._json({"error": "PNG·JPG 이미지만 넣을 수 있어요"}, 400)
            if u.path == "/api/products":
                from ..products import add as add_product

                kws = [k for k in re.split(r"[,，\s]+", q.get("keywords", [""])[0]) if k]
                return self._json(add_product(APP_ROOT, data, name, q.get("label", [""])[0], kws))
            d = DATA_DIR / "brand"
            d.mkdir(parents=True, exist_ok=True)
            dst = d / f"logo_{uuid.uuid4().hex[:6]}{os.path.splitext(name)[1].lower()}"
            dst.write_bytes(data)
            save_settings({"card_logo": str(dst)})
            return self._json({"path": str(dst)})
        m = re.match(r"^/api/jobs/(\w+)/asset$", u.path)
        if m:
            job = JOBS.get(m.group(1))
            if not job:
                return self._json({"error": "작업이 없습니다"}, 404)
            name = os.path.basename(q.get("name", ["logo.png"])[0])
            stem, ext = os.path.splitext(name)
            if ext.lower() not in (".png", ".jpg", ".jpeg", ".webp", ".gif"):
                return self._json({"error": "PNG·JPG 이미지만 넣을 수 있어요"}, 400)
            d = job.out_dir / "_assets"
            d.mkdir(parents=True, exist_ok=True)
            dst = d / f"{_safe_name(stem)}_{uuid.uuid4().hex[:6]}{ext.lower()}"
            n = int(self.headers.get("Content-Length") or 0)
            if n > 30 * 1024 * 1024:
                return self._json({"error": "이미지가 너무 큽니다 (30MB 이하)"}, 400)
            dst.write_bytes(self.rfile.read(n))
            return self._json({"path": str(dst)})
        if u.path != "/api/upload":
            return self._json({"error": "없는 주소"}, 404)
        name = q.get("name", ["video.mp4"])[0]
        stem, ext = os.path.splitext(os.path.basename(name))
        ext = ext.lower() if ext.lower() in (".mp4", ".mov", ".mkv", ".avi", ".m4v", ".webm") else ".mp4"
        stem = _safe_name(stem)
        dst = UPLOADS / f"{stem}{ext}"
        n = int(self.headers.get("Content-Length") or 0)
        with open(dst, "wb") as f:
            left = n
            while left > 0:
                chunk = self.rfile.read(min(1 << 20, left))
                if not chunk:
                    break
                f.write(chunk)
                left -= len(chunk)
        job = Job(dst, stem)
        try:
            ff.ensure_ffmpeg()
            job.duration = ff.probe_duration(dst)
            job.poster = _poster(dst, PREVIEWS / f"{job.id}_poster.jpg", min(3.0, job.duration / 3))
        except Exception:  # noqa: BLE001
            pass
        JOBS[job.id] = job
        return self._json(job.public())

    def do_POST(self):
        if not self._guard(True):
            return
        u = urllib.parse.urlparse(self.path)
        path = u.path
        try:
            body = self._body()
            if path == "/api/settings":
                return self._json(save_settings(body))
            if path == "/api/shutdown":
                # 새 버전이 켜질 때 예전 버전을 끈다 (작업 중이면 거절)
                if WORK_LOCK.locked():
                    return self._json({"ok": False, "busy": True})
                threading.Thread(target=lambda: (time.sleep(0.3), os._exit(0)), daemon=True).start()
                return self._json({"ok": True})
            if path == "/api/products/update":
                from ..products import update as upd_product

                upd_product(APP_ROOT, body.get("file", ""), body.get("name"), body.get("keywords"))
                return self._json({"ok": True})
            if path == "/api/products/delete":
                from ..products import remove as rm_product

                rm_product(APP_ROOT, body.get("file", ""))
                return self._json({"ok": True})
            m = re.match(r"^/api/jobs/(\w+)/auto-products$", path)
            if m:
                from ..products import auto_place
                from ..transcribe import captions_from_json

                job = self._job(m.group(1))
                if not job:
                    return self._json({"error": "작업이 없습니다"}, 404)
                caps = captions_from_json(body.get("captions", job.captions))
                dims = ff.probe_dimensions(job.clean_video) if job.clean_video else None
                new = auto_place(caps, APP_ROOT, existing=body.get("overlays", []),
                                 vertical=bool(dims and dims[1] > dims[0]), copy_to=job.out_dir / "_assets")
                return self._json({"overlays": new})
            m = re.match(r"^/api/jobs/(\w+)/recut$", path)
            if m:
                # 컷 다시 적용: 살린/더 자른 구간으로 편집본을 다시 만들고 자막·로고 시간을 옮긴다
                from .. import timeline as tl
                from ..transcribe import captions_from_json, captions_to_list

                job = self._job(m.group(1))
                if not job or not job.cut:
                    return self._json({"error": "컷 정보가 없는 작업입니다 (새로 분석한 영상부터 가능)"}, 400)
                if not WORK_LOCK.acquire(blocking=False):
                    return self._json({"error": "다른 작업이 진행 중입니다"}, 409)
                try:
                    total = float(job.cut["total"])
                    old_keep = tl.normalize(job.cut["keep"], total)
                    new_keep = tl.normalize(body.get("keep", []), total)
                    if not new_keep:
                        return self._json({"error": "남길 구간이 없습니다"}, 400)
                    caps = captions_from_json(body.get("captions", job.captions))
                    ovs = body.get("overlays", job.overlays) or []
                    cfg = build_config(load_settings())
                    tmp = job.out_dir / f"{job.name}_clean_new.mp4"
                    tl.recut(Path(job.cut["source"]), new_keep, tmp, cfg.output)
                    tmp.replace(job.clean_video)
                    job.captions = captions_to_list(tl.remap_captions(caps, old_keep, new_keep))
                    job.overlays = tl.remap_overlays(ovs, old_keep, new_keep)
                    job.cut = {**job.cut, "keep": new_keep}
                    job.duration = ff.probe_duration(job.clean_video)
                    _save_project(job)
                    return self._json({"captions": job.captions, "overlays": job.overlays, "cut": job.cut,
                                       "clean_video": str(job.clean_video), "v": int(time.time())})
                finally:
                    WORK_LOCK.release()
            if path == "/api/pick":
                # 윈도우 파일 선택창 → 원본을 복사하지 않고 그 자리에서 바로 편집 (대용량에 유리)
                picked = _pick_file()
                if not picked:
                    return self._json({"cancelled": True})
                src = Path(picked)
                job = Job(src, _safe_name(src.stem))
                try:
                    job.duration = ff.probe_duration(src)
                    job.poster = _poster(src, PREVIEWS / f"{job.id}_poster.jpg", min(3.0, job.duration / 3))
                except Exception:  # noqa: BLE001
                    pass
                JOBS[job.id] = job
                return self._json(job.public())
            if path == "/api/projects/open":
                d = Path(body.get("dir", ""))
                if not _allowed(d) or not (d / "_project.json").exists():
                    return self._json({"error": "프로젝트를 열 수 없습니다"}, 400)
                return self._json(open_project(d).public())
            if path == "/api/open":
                p = Path(body.get("path", ""))
                if not _allowed(p) or not p.exists():
                    return self._json({"error": "열 수 없습니다"}, 400)
                if p.is_file():
                    subprocess.Popen(["explorer", "/select,", str(p)])
                else:
                    os.startfile(str(p))  # type: ignore[attr-defined]
                return self._json({"ok": True})
            m = re.match(r"^/api/jobs/(\w+)/direct$", path)
            if m:
                # AI 자동 연출: 문장 정리 + 강조 + 효과음 + 배경음악
                from ..config import SmartEditConfig
                from ..director import direct
                from ..transcribe import captions_from_json, captions_to_list

                job = self._job(m.group(1))
                if not job:
                    return self._json({"error": "작업이 없습니다"}, 404)
                caps = captions_from_json(body.get("captions", job.captions))
                st = load_settings()
                plan = direct(
                    caps, body.get("genre", "promo"),
                    vocab=st.get("vocab"), smart_cfg=SmartEditConfig(),
                    tidy=bool(body.get("tidy", True)), do_sfx=bool(body.get("sfx", True)),
                    do_emph=bool(body.get("emph", True)), try_ai=bool(body.get("ai", True)) and has_api_key(),
                )
                return self._json({
                    "captions": captions_to_list(plan.captions),
                    "bgm": f"mood:{plan.bgm}", "style": plan.style,
                    "used_ai": plan.used_ai, "notes": plan.notes,
                })
            m = re.match(r"^/api/jobs/(\w+)/versions$", path)
            if m:
                job = self._job(m.group(1))
                if not job:
                    return self._json({"error": "작업이 없습니다"}, 404)
                job.captions = body.get("captions", job.captions)
                if isinstance(body.get("overlays"), list):
                    job.overlays = body["overlays"]
                _save_project(job)
                return self._json(_save_version(job, body.get("label", ""), body.get("settings")))
            m = re.match(r"^/api/jobs/(\w+)/(analyze|captions|render)$", path)
            if m:
                job = self._job(m.group(1))
                if not job:
                    return self._json({"error": "작업이 없습니다"}, 404)
                action = m.group(2)
                if action == "captions":
                    job.captions = body.get("captions", [])
                    if isinstance(body.get("overlays"), list):
                        job.overlays = body["overlays"]
                    if job.out_dir.exists():
                        _save_project(job)
                    return self._json({"ok": True, "saved": time.strftime("%H:%M:%S")})
                if WORK_LOCK.locked():
                    return self._json({"error": "다른 작업이 진행 중입니다"}, 409)
                opts = {**load_settings(), **body.get("options", {})}
                save_settings(opts)
                if action == "analyze":
                    threading.Thread(target=_run_analyze, args=(job, opts), daemon=True).start()
                else:
                    if isinstance(body.get("overlays"), list):
                        job.overlays = body["overlays"]
                    if body.get("captions") is not None:
                        job.captions = body["captions"]
                        _save_project(job)
                    threading.Thread(target=_run_render, args=(job, opts), daemon=True).start()
                return self._json({"ok": True})
            return self._json({"error": "없는 주소"}, 404)
        except Exception as exc:  # noqa: BLE001
            traceback.print_exc()
            return self._json({"error": str(exc)}, 500)


LAST_SEEN = time.time()


def _touch() -> None:
    global LAST_SEEN
    LAST_SEEN = time.time()


_PICK_LOCK = threading.Lock()


def _pick_file() -> Optional[str]:
    """윈도우 '열기' 창으로 영상 파일을 고른다."""
    with _PICK_LOCK:
        try:
            import tkinter as tk
            from tkinter import filedialog
        except Exception:  # noqa: BLE001
            return None
        root = tk.Tk()
        root.withdraw()
        root.attributes("-topmost", True)
        try:
            path = filedialog.askopenfilename(
                title="편집할 영상 선택",
                filetypes=[("영상", "*.mp4 *.mov *.m4v *.mkv *.avi *.webm"), ("모든 파일", "*.*")],
                initialdir=str(Path.home() / "Videos"),
            )
        finally:
            root.destroy()
        return path or None


# ───────────────────────────── 실행 ─────────────────────────────


def _hide_child_consoles():
    """pythonw 로 실행할 때 ffmpeg 검은 창이 번쩍이지 않게."""
    if os.name != "nt":
        return
    flag = 0x08000000  # CREATE_NO_WINDOW
    orig = subprocess.Popen.__init__

    def patched(self, *a, **kw):
        kw["creationflags"] = kw.get("creationflags", 0) | flag
        orig(self, *a, **kw)

    subprocess.Popen.__init__ = patched  # type: ignore[method-assign]


def _edge_path() -> Optional[str]:
    for p in (
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    ):
        if os.path.exists(p):
            return p
    return None


def _kill_port_owner() -> None:
    """PORT 를 붙잡고 있는 python(w).exe 만 종료한다 (다른 프로그램은 건드리지 않음)."""
    if os.name != "nt":
        return
    try:
        out = subprocess.run(["netstat", "-ano", "-p", "TCP"], capture_output=True, text=True,
                             encoding="utf-8", errors="replace").stdout
        pids = {line.split()[-1] for line in out.splitlines()
                if f"127.0.0.1:{PORT}" in line and "LISTENING" in line}
        for pid in pids:
            name = subprocess.run(["tasklist", "/FI", f"PID eq {pid}", "/FO", "CSV", "/NH"], capture_output=True,
                                  text=True, encoding="utf-8", errors="replace").stdout.lower()
            if "python" in name and str(os.getpid()) != pid:
                subprocess.run(["taskkill", "/PID", pid, "/F"], capture_output=True)
    except Exception:  # noqa: BLE001
        pass


def _already_running(url: str) -> bool:
    """같은 버전이 이미 켜져 있으면 True. 예전 버전이 켜져 있으면 끄고 False(새로 시작)."""
    import urllib.request

    try:
        with urllib.request.urlopen(url + "api/ping", timeout=0.6) as r:
            info = json.loads(r.read().decode("utf-8"))
    except Exception:  # noqa: BLE001
        return False
    if info.get("app") != "edge-studio":
        return False
    if info.get("version") == APP_VERSION:
        return True
    if not info.get("version"):
        # 아주 예전 버전(끄기 기능 없음) → 그 포트를 쓰는 파이썬 프로세스를 직접 종료
        _kill_port_owner()
        time.sleep(0.8)
        return False
    # 예전 버전 → 끄기 요청 (영상 만드는 중이면 그대로 둠)
    try:
        req = urllib.request.Request(url + "api/shutdown", data=b"{}", method="POST",
                                     headers={"X-Edge-Studio": "1", "Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=2) as r:
            res = json.loads(r.read().decode("utf-8"))
        if not res.get("ok"):
            return True  # 작업 중 → 그 창을 그대로 씀
    except Exception:  # noqa: BLE001
        pass
    for _ in range(30):  # 꺼질 때까지 최대 3초
        time.sleep(0.1)
        try:
            urllib.request.urlopen(url + "api/ping", timeout=0.3)
        except Exception:  # noqa: BLE001
            return False
    return True


def _cleanup_uploads(days: int = 3):
    cutoff = time.time() - days * 86400
    for d in (UPLOADS, PREVIEWS):
        for p in d.glob("*"):
            try:
                if p.stat().st_mtime < cutoff:
                    p.unlink()
            except Exception:  # noqa: BLE001
                pass


def main(argv: Optional[List[str]] = None):
    argv = argv if argv is not None else sys.argv[1:]
    no_window = "--no-window" in argv
    url = f"http://127.0.0.1:{PORT}/"
    if _already_running(url):
        _open_window(url, wait=False)
        return
    _hide_child_consoles()
    _cleanup_uploads()
    try:
        ff.ensure_ffmpeg()
    except Exception:  # noqa: BLE001
        pass
    os.chdir(APP_ROOT)
    srv = ThreadingHTTPServer(("127.0.0.1", PORT), Handler)
    t = threading.Thread(target=srv.serve_forever, daemon=True)
    t.start()
    print(f"엣지 스튜디오 실행 중: {url}")
    if no_window:
        t.join()
        return
    _open_window(url, wait=False)
    # 화면이 10초마다 보내는 '살아있음' 신호가 끊기면(창을 닫으면) 종료.
    # (Edge 실행 파일은 창을 띄우자마자 바로 끝나므로 프로세스로는 창 닫힘을 알 수 없다)
    _touch()
    while True:
        time.sleep(5)
        idle = time.time() - LAST_SEEN
        if idle > 180 and not WORK_LOCK.locked():  # 창을 최소화해도 신호가 느려질 뿐 끊기진 않도록 여유
            break
    srv.shutdown()


def _open_window(url: str, wait: bool) -> bool:
    """앱 창을 띄운다. wait=True 이고 창 닫힘을 감지할 수 있으면 True."""
    exe = _edge_path()
    if exe:
        profile = DATA_DIR / "window"
        args = [exe, f"--app={url}", "--window-size=1480,940", f"--user-data-dir={profile}",
                "--no-first-run", "--disable-features=Translate"]
        p = subprocess.Popen(args)
        if wait:
            p.wait()
            return True
        return False
    webbrowser.open(url)
    return False


if __name__ == "__main__":
    main()

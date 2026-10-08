"""제품 사진 자동 삽입 — 말하는 내용에 맞춰 회장님 실제 제품 사진을 띄운다.

제품 사진 라이브러리(assets/products/)에 사진과 키워드를 한 번 등록해 두면
(예: 슬림팬.png ← "실링팬, 슬림, 14.5"), 자막에 그 키워드가 나오는 순간
화면 한쪽에 사진이 '톡' 나타났다 사라지는 로고·스티커 항목을 자동으로 만든다.
AI로 제품을 그려 넣지 않는다 — 등록한 실제 사진만 쓴다.
"""

from __future__ import annotations

import json
import re
import shutil
import uuid
from pathlib import Path
from typing import Dict, List, Optional

from .transcribe import Caption


def lib_dir(app_root: Path) -> Path:
    d = app_root / "assets" / "products"
    d.mkdir(parents=True, exist_ok=True)
    return d


def _index(app_root: Path) -> Path:
    return lib_dir(app_root) / "products.json"


def load(app_root: Path) -> List[Dict]:
    p = _index(app_root)
    try:
        items = json.loads(p.read_text(encoding="utf-8"))
    except Exception:  # noqa: BLE001
        items = []
    return [i for i in items if (lib_dir(app_root) / i.get("file", "")).exists()]


def save(app_root: Path, items: List[Dict]) -> None:
    _index(app_root).write_text(json.dumps(items, ensure_ascii=False, indent=1), encoding="utf-8")


def add(app_root: Path, data: bytes, filename: str, name: str, keywords: List[str]) -> Dict:
    ext = Path(filename).suffix.lower() or ".png"
    fname = f"{re.sub(r'[^0-9A-Za-z가-힣_-]+', '_', name or Path(filename).stem)[:40]}_{uuid.uuid4().hex[:6]}{ext}"
    (lib_dir(app_root) / fname).write_bytes(data)
    item = {"file": fname, "name": name or Path(filename).stem,
            "keywords": [k.strip() for k in keywords if k.strip()]}
    items = load(app_root)
    items.append(item)
    save(app_root, items)
    return item


def update(app_root: Path, file: str, name: Optional[str], keywords: Optional[List[str]]) -> None:
    items = load(app_root)
    for i in items:
        if i["file"] == file:
            if name is not None:
                i["name"] = name
            if keywords is not None:
                i["keywords"] = [k.strip() for k in keywords if k.strip()]
    save(app_root, items)


def remove(app_root: Path, file: str) -> None:
    items = [i for i in load(app_root) if i["file"] != file]
    save(app_root, items)
    (lib_dir(app_root) / Path(file).name).unlink(missing_ok=True)


def auto_place(
    captions: List[Caption],
    app_root: Path,
    existing: Optional[List[Dict]] = None,
    vertical: bool = False,
    copy_to: Optional[Path] = None,
) -> List[Dict]:
    """자막에 제품 키워드가 나오면 그 순간 제품 사진 항목(overlay)을 만든다. 새로 만든 것만 돌려준다."""
    from .styles import words_for

    lib = [i for i in load(app_root) if i.get("keywords")]
    if not lib:
        return []
    busy = [(float(o["start"]), float(o["start"]) + float(o["dur"])) for o in (existing or [])]
    last_shown: Dict[str, float] = {}
    out: List[Dict] = []
    for c in captions:
        ws = words_for(c)
        hit = None
        for k, w in enumerate(ws):
            bare = re.sub(r"[.,?!…]", "", w.text)
            for item in lib:
                if any(kw and kw in bare for kw in item["keywords"]):
                    hit = (item, w.start)
                    break
            if hit:
                break
        if not hit:
            continue
        item, t0 = hit
        start = max(0.0, t0 - 0.1)
        dur = max(2.0, min(5.0, c.end - start))
        if any(a < start + dur and start < b for a, b in busy):
            continue
        if start - last_shown.get(item["file"], -99) < 10:
            continue
        src = lib_dir(app_root) / item["file"]
        path = src
        if copy_to is not None:  # 프로젝트에 복사해 두면 라이브러리를 지워도 영상은 유지
            copy_to.mkdir(parents=True, exist_ok=True)
            path = copy_to / item["file"]
            if not path.exists():
                shutil.copy2(src, path)
        out.append({
            "path": str(path), "start": round(start, 2), "dur": round(dur, 2),
            "pos": "top" if vertical else "right", "size": 55 if vertical else 30,
            "anim": "pop", "sfx": None, "product": item["name"],
        })
        busy.append((start, start + dur))
        last_shown[item["file"]] = start
    return out

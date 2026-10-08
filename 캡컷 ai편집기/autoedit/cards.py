"""오프닝·엔딩 카드 — 영상 앞뒤에 붙는 2~3초짜리 타이틀/마무리 화면.

- 오프닝: 영상 첫 장면을 흐리게 깐 배경 + 제목 + 회사 로고 (휙 효과음)
- 엔딩:   마지막 장면을 흐리게 깐 배경 + 마무리 문구 + 회사명·전화·홈페이지 + QR (짜잔 효과음)
글자는 Pillow 로 직접 그려 한글이 깨지지 않고, 영상은 천천히 다가가는(줌인) 움직임 + 페이드.
가로·세로 영상 모두 자동 배치.
"""

from __future__ import annotations

import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from .ffmpeg import run
from .utils import logger


@dataclass
class CardInfo:
    title: str = ""
    subtitle: str = ""
    company: str = "엣지컴퍼니"
    phone: str = ""
    site: str = ""
    message: str = "박람회에서 뵙겠습니다"
    logo: str = ""        # 로고 이미지 경로
    qr: str = ""          # QR 에 담을 링크/글 (비우면 QR 없음)
    theme: str = "blur"   # blur(장면 흐림) / white / navy


def _font(size: int, bold: bool = True):
    from PIL import ImageFont

    from .styles import fonts_dir

    cands = [fonts_dir() / ("Pretendard-Bold.otf" if bold else "Pretendard-Regular.otf"),
             Path("C:/Windows/Fonts/malgunbd.ttf" if bold else "C:/Windows/Fonts/malgun.ttf")]
    for c in cands:
        if c.exists():
            return ImageFont.truetype(str(c), size)
    return ImageFont.load_default()


def _fit_text(draw, text: str, max_w: int, size: int, bold=True):
    """폭에 맞게 글자 크기를 줄인다."""
    while size > 14:
        f = _font(size, bold)
        if draw.textlength(text, font=f) <= max_w:
            return f
        size = int(size * 0.92)
    return _font(size, bold)


def _background(W: int, H: int, theme: str, frame: Optional[Path]):
    from PIL import Image, ImageDraw, ImageFilter

    if theme == "blur" and frame and frame.exists():
        im = Image.open(frame).convert("RGB")
        r = max(W / im.width, H / im.height)
        im = im.resize((int(im.width * r) + 1, int(im.height * r) + 1))
        l, t = (im.width - W) // 2, (im.height - H) // 2
        im = im.crop((l, t, l + W, t + H)).filter(ImageFilter.GaussianBlur(max(W, H) / 45))
        dark = Image.new("RGB", (W, H), (8, 14, 28))
        return Image.blend(im, dark, 0.55), (255, 255, 255), (255, 214, 74)
    if theme == "navy":
        im = Image.new("RGB", (W, H), (19, 37, 74))
        d = ImageDraw.Draw(im)
        for y in range(H):  # 아래로 갈수록 살짝 밝게
            c = int(10 * y / H)
            d.line([(0, y), (W, y)], fill=(19 + c, 37 + c, 74 + c * 2))
        return im, (255, 255, 255), (255, 164, 59)
    return Image.new("RGB", (W, H), (247, 248, 250)), (19, 37, 74), (53, 87, 255)


def _paste_fit(canvas, img_path: str, box_w: int, box_h: int, cx: int, cy: int):
    from PIL import Image

    try:
        im = Image.open(img_path).convert("RGBA")
    except Exception:  # noqa: BLE001
        return 0
    r = min(box_w / im.width, box_h / im.height)
    im = im.resize((max(1, int(im.width * r)), max(1, int(im.height * r))))
    canvas.paste(im, (cx - im.width // 2, cy - im.height // 2), im)
    return im.height


def make_card_png(kind: str, info: CardInfo, W: int, H: int, frame: Optional[Path], out: Path) -> Path:
    from PIL import ImageDraw

    img, fg, accent = _background(W, H, info.theme, frame)
    img = img.convert("RGBA")
    d = ImageDraw.Draw(img)
    vertical = H > W
    unit = min(W, H)
    cx = W // 2
    y = int(H * (0.30 if vertical else 0.24))

    if info.logo:
        lh = _paste_fit(img, info.logo, int(W * (0.5 if vertical else 0.24)), int(unit * 0.16), cx, y)
        y += lh // 2 + int(unit * 0.07)
    else:
        y += int(unit * 0.04)

    if kind == "opening":
        title = info.title or info.company
        f = _fit_text(d, title, int(W * 0.86), int(unit * (0.11 if vertical else 0.105)))
        d.text((cx, y), title, font=f, fill=fg, anchor="mt")
        y += int(f.size * 1.35)
        d.rectangle([cx - int(unit * 0.05), y, cx + int(unit * 0.05), y + max(3, unit // 160)], fill=accent)
        y += int(unit * 0.05)
        sub = info.subtitle or (info.company if info.title else "")
        if sub:
            fs = _fit_text(d, sub, int(W * 0.8), int(unit * 0.05), bold=False)
            d.text((cx, y), sub, font=fs, fill=fg, anchor="mt")
    else:
        msg = info.message or "감사합니다"
        f = _fit_text(d, msg, int(W * 0.86), int(unit * (0.1 if vertical else 0.095)))
        d.text((cx, y), msg, font=f, fill=fg, anchor="mt")
        y += int(f.size * 1.5)
        lines = [s for s in (info.company, info.phone and f"Tel. {info.phone}", info.site) if s]
        has_qr = bool(info.qr)
        text_cx = cx if (vertical or not has_qr) else int(W * 0.40)
        ty = y
        for i, s in enumerate(lines):
            fs = _fit_text(d, s, int(W * (0.8 if vertical or not has_qr else 0.45)), int(unit * (0.06 if i == 0 else 0.047)), bold=(i == 0))
            d.text((text_cx, ty), s, font=fs, fill=accent if i == 1 else fg, anchor="mt")
            ty += int(fs.size * 1.45)
        if has_qr:
            import qrcode

            q = qrcode.QRCode(border=2, box_size=10)
            q.add_data(info.qr)
            q.make(fit=True)
            qimg = q.make_image(fill_color="black", back_color="white").convert("RGBA")
            qs = int(unit * (0.26 if vertical else 0.24))
            qimg = qimg.resize((qs, qs))
            if vertical:
                qx, qy = cx - qs // 2, ty + int(unit * 0.03)
            else:
                qx, qy = int(W * 0.66), y - int(unit * 0.02)
            pad = int(qs * 0.06)
            d.rounded_rectangle([qx - pad, qy - pad, qx + qs + pad, qy + qs + pad], radius=pad * 2, fill=(255, 255, 255))
            img.paste(qimg, (qx, qy), qimg)
            cap = _font(int(unit * 0.032), bold=False)
            d.text((qx + qs // 2, qy + qs + pad * 2), "QR을 찍어보세요", font=cap, fill=fg, anchor="mt")
    img.convert("RGB").save(out, quality=95)
    return out


def grab_frame(video: Path, at: float, out: Path) -> Optional[Path]:
    try:
        run(["ffmpeg", "-y", "-ss", f"{max(0.0, at):.2f}", "-i", str(video), "-frames:v", "1", "-q:v", "2", str(out)])
        return out if out.exists() else None
    except Exception:  # noqa: BLE001
        return None


def make_card_video(
    kind: str, info: CardInfo, video: Path, W: int, H: int, fps: int, dur: float, work_dir: Path
) -> Path:
    """카드 PNG → 천천히 다가가는 짧은 영상 + 효과음."""
    from .ffmpeg import probe_duration
    from .sfx import sample_path

    vdur = probe_duration(video)
    frame = grab_frame(video, 0.5 if kind == "opening" else max(0.0, vdur - 0.6), work_dir / f"{kind}_bg.jpg")
    png = make_card_png(kind, info, W, H, frame, work_dir / f"{kind}.jpg")
    out = work_dir / f"{kind}.mp4"
    sfx = sample_path("whoosh" if kind == "opening" else "tada")
    z = f"(1+0.05*t/{dur:.2f})"
    vf = (
        f"scale=w='trunc({W}*{z}/2)*2':h='trunc({H}*{z}/2)*2':eval=frame,crop={W}:{H},setsar=1,"
        f"fps={fps},fade=t=in:st=0:d=0.35,fade=t=out:st={max(0.0, dur - 0.4):.2f}:d=0.4,format=yuv420p"
    )
    run([
        "ffmpeg", "-y", "-loop", "1", "-t", f"{dur:.2f}", "-i", str(png), "-i", str(sfx),
        "-filter_complex", f"[0:v]{vf}[v];[1:a]volume=0.6,apad,atrim=0:{dur:.2f},aformat=channel_layouts=stereo:sample_rates=44100[a]",
        "-map", "[v]", "-map", "[a]", "-t", f"{dur:.2f}",
        "-c:v", "libx264", "-crf", "18", "-preset", "fast", "-c:a", "aac", "-b:a", "192k", str(out),
    ])
    logger.info("%s 카드 생성 (%.1f초)", "오프닝" if kind == "opening" else "엔딩", dur)
    return out


def preview_png(kind: str, info: CardInfo, video: Optional[Path], W: int, H: int) -> Path:
    d = Path(tempfile.mkdtemp(prefix="card_"))
    frame = None
    if video and video.exists():
        from .ffmpeg import probe_duration

        frame = grab_frame(video, 0.5 if kind == "opening" else max(0.0, probe_duration(video) - 0.6), d / "bg.jpg")
    return make_card_png(kind, info, W, H, frame, d / f"{kind}.jpg")

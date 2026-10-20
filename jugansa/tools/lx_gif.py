"""단지 비주얼팀(bid_visual) · 경관조명 메일 GIF 합성기.

사용: python lx_gif.py <사진1> <사진2> ... -o 결과.gif [--title 상단문구] [--cap 하단캡션]
                       [--width 640] [--ratio 16:9] [--hold 1.6] [--fade 0.6] [--max-mb 5]

- 순서 = 낮(조감도) → 밤 → 경관조명 켜짐. 사진마다 hold초 보여 주고 fade초 동안 겹쳐 넘긴다(무한 반복).
- 모든 사진을 같은 비율로 가운데 잘라 맞춘다(--ratio, 기본 = 첫 사진 비율).
- 하단 캡션 기본값 = '경관조명 연출 시뮬레이션 · 실제와 다를 수 있음'(빼지 않는다 — 시뮬레이션 표시 규칙).
- 한글은 Pretendard로 얹는다(AI 한글 깨짐 방지). 용량이 --max-mb를 넘으면 폭 · 색 수를 줄여 다시 만든다.
"""
import argparse
import os
import sys

from PIL import Image, ImageDraw, ImageFont

FONT_DIRS = [os.path.expanduser("~/.local/share/fonts"), "C:/Windows/Fonts", "/usr/share/fonts"]
CAP = "경관조명 연출 시뮬레이션 · 실제와 다를 수 있음"


def font(weight, size):
    names = {"bold": ["Pretendard-Bold.otf", "malgunbd.ttf"], "reg": ["Pretendard-Medium.otf", "malgun.ttf"]}[weight]
    for d in FONT_DIRS:
        for n in names:
            p = os.path.join(d, n)
            if os.path.exists(p):
                return ImageFont.truetype(p, size)
    return ImageFont.load_default()


def fit(im, w, h):
    """가운데 기준으로 잘라 w×h에 맞춘다."""
    im = im.convert("RGB")
    r = max(w / im.width, h / im.height)
    im = im.resize((round(im.width * r), round(im.height * r)), Image.LANCZOS)
    x, y = (im.width - w) // 2, (im.height - h) // 2
    return im.crop((x, y, x + w, y + h))


def overlay(im, title, cap):
    """위 = 제목 띠(선택) · 아래 = 시뮬레이션 캡션 띠. 반투명 검정 위에 흰 글씨."""
    im = im.convert("RGBA")
    w, h = im.size
    layer = Image.new("RGBA", im.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    s = max(11, w // 48)
    if title:
        f = font("bold", round(s * 1.5))
        bh = round(s * 2.8)
        d.rectangle((0, 0, w, bh), fill=(8, 18, 38, 150))
        tw = d.textlength(title, font=f)
        d.text(((w - tw) / 2, (bh - f.size) / 2 - 1), title, font=f, fill=(233, 206, 140, 255))
    if cap:
        f = font("reg", s)
        bh = round(s * 2.1)
        d.rectangle((0, h - bh, w, h), fill=(0, 0, 0, 120))
        tw = d.textlength(cap, font=f)
        d.text((w - tw - s, h - bh + (bh - f.size) / 2 - 1), cap, font=f, fill=(255, 255, 255, 235))
    return Image.alpha_composite(im, layer).convert("RGB")


def frames(paths, w, h, title, cap, hold, fade, fps=10):
    base = [overlay(fit(Image.open(p), w, h), title, cap) for p in paths]
    out, dur = [], []
    n = max(2, round(fade * fps))
    for i, a in enumerate(base):
        b = base[(i + 1) % len(base)]
        out.append(a)
        dur.append(round(hold * 1000))
        for k in range(1, n):
            out.append(Image.blend(a, b, k / n))
            dur.append(round(1000 / fps))
    return out, dur


def save(fr, dur, path, colors):
    pal = [f.quantize(colors=colors, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.FLOYDSTEINBERG) for f in fr]
    pal[0].save(path, save_all=True, append_images=pal[1:], duration=dur, loop=0, optimize=True, disposal=1)
    return os.path.getsize(path) / 1e6


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("images", nargs="+")
    ap.add_argument("-o", "--out", required=True)
    ap.add_argument("--title", default="")
    ap.add_argument("--cap", default=CAP)
    ap.add_argument("--width", type=int, default=640)
    ap.add_argument("--ratio", default="")
    ap.add_argument("--hold", type=float, default=1.6)
    ap.add_argument("--fade", type=float, default=0.6)
    ap.add_argument("--max-mb", type=float, default=5.0)
    a = ap.parse_args()
    if len(a.images) < 2:
        sys.exit("사진은 2장 이상(낮 → 밤 → 조명 켜짐 순)")
    if a.ratio:
        rw, rh = (float(x) for x in a.ratio.split(":"))
    else:
        im0 = Image.open(a.images[0])
        rw, rh = im0.width, im0.height
    w, colors = a.width, 256
    while True:
        h = round(w * rh / rw / 2) * 2
        fr, dur = frames(a.images, w, h, a.title, a.cap, a.hold, a.fade)
        mb = save(fr, dur, a.out, colors)
        if mb <= a.max_mb or w <= 360:
            break
        w, colors = round(w * 0.88), max(96, colors - 48)
    print(f"{a.out}  {w}×{h}px · {len(fr)}프레임 · 한 바퀴 {sum(dur) / 1000:.1f}초 · {mb:.2f}MB · 색 {colors}")


if __name__ == "__main__":
    main()

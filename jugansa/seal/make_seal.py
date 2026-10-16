"""입예협 사각 도장(인영) 생성기.

사용: python make_seal.py <폰트폴더>
  폰트폴더: Pretendard-Black.otf 와 fontsource nanum-myeongjo 800 woff 조각들이 있는 곳
산출: 같은 폴더(seal/)에 PNG(투명배경) — clean(제작용) / stamp(찍힌 느낌, 문서용)
"""
import glob
import os
import random
import sys

import numpy as np

from fontTools.ttLib import TTFont
from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont

ROWS = ["e편한세상", "에코델타", "센터포인트", "입예협회장"]
RED = (200, 22, 29)
SIZE = 1200          # 최종 한 변(px) ≈ 24mm 도장 기준 1270dpi급
BORDER = 70          # 외곽 테두리 두께
GAP = 34             # 테두리-글자 여백
LINE_GAP = 26        # 행 간격
OUT = os.path.dirname(os.path.abspath(__file__))


class GlyphFonts:
    """글자별로 해당 글리프가 들어있는 폰트 파일을 찾아준다(조각난 웹폰트 대응)."""

    def __init__(self, paths):
        self.maps = []
        for p in paths:
            cmap = TTFont(p).getBestCmap() or {}
            self.maps.append((p, set(cmap)))

    def path_for(self, ch):
        for p, cps in self.maps:
            if ord(ch) in cps:
                return p
        raise KeyError(f"글리프 없음: {ch}")


def render_char(ch, fonts, px=600):
    font = ImageFont.truetype(fonts.path_for(ch), px)
    im = Image.new("L", (px * 2, px * 2), 0)
    ImageDraw.Draw(im).text((px // 2, px // 4), ch, font=font, fill=255)
    return im.crop(im.getbbox())


def render_row(text, fonts, w, h):
    """한 행을 셀(w×h)에 꽉 차게. 글자마다 같은 폭 칸에 세로로 늘려 도장 특유의 꽉 찬 느낌."""
    n = len(text)
    gap = int(w * 0.035)
    cw = (w - gap * (n - 1)) / n
    row = Image.new("L", (w, h), 0)
    for i, ch in enumerate(text):
        g = render_char(ch, fonts)
        if ch.isascii():  # 소문자 e 는 한글보다 낮으므로 높이 80%로 하단 정렬
            g = g.resize((int(cw * 0.78), int(h * 0.80)), Image.LANCZOS)
            x = int(i * (cw + gap) + (cw - g.width) / 2)
            row.paste(g, (x, h - g.height), g)
        else:
            g = g.resize((int(cw), h), Image.LANCZOS)
            row.paste(g, (int(i * (cw + gap)), 0), g)
    return row


def build_mask(fonts):
    m = Image.new("L", (SIZE, SIZE), 0)
    d = ImageDraw.Draw(m)
    d.rounded_rectangle([0, 0, SIZE - 1, SIZE - 1], radius=36, fill=255)
    d.rounded_rectangle([BORDER, BORDER, SIZE - 1 - BORDER, SIZE - 1 - BORDER], radius=14, fill=0)
    inner = BORDER + GAP
    w = SIZE - inner * 2
    rh = (w - LINE_GAP * (len(ROWS) - 1)) // len(ROWS)
    for i, t in enumerate(ROWS):
        r = render_row(t, fonts, w, rh)
        m.paste(255, (inner, inner + i * (rh + LINE_GAP)), r)
    return m


def colorize(mask):
    im = Image.new("RGBA", mask.size, RED + (0,))
    im.putalpha(mask)
    return im


def stamped(mask, seed=7):
    """인주 번짐·잉크 빠짐 질감."""
    rnd = random.Random(seed)
    fine = Image.effect_noise(mask.size, 110).filter(ImageFilter.GaussianBlur(1.3))
    holes = fine.point(lambda v: 0 if v < 78 else 255).filter(ImageFilter.GaussianBlur(0.8))
    coarse = Image.effect_noise((SIZE // 60, SIZE // 60), 40).resize(mask.size, Image.BICUBIC)
    patchy = coarse.point(lambda v: max(215, min(255, v + 110)))  # 인주가 덜 묻은 얼룩
    m = ImageChops.multiply(mask.filter(ImageFilter.GaussianBlur(1.4)), holes)
    m = ImageChops.multiply(m, patchy)
    # 가장자리 압력 불균일(한쪽이 살짝 연함)
    grad = Image.linear_gradient("L").resize(mask.size).point(lambda v: 205 + v * 50 // 255)
    m = ImageChops.multiply(m, grad.rotate(rnd.choice([0, 90, 180, 270])))
    return colorize(m.point(lambda v: 0 if v < 40 else v)).rotate(-1.2, resample=Image.BICUBIC)


def _fbm(shape, rng, scales, weights):
    """여러 주파수 노이즈 합(0~1)."""
    h, w = shape
    acc = np.zeros(shape, np.float32)
    for sc, wt in zip(scales, weights):
        g = rng.random((max(2, h // sc), max(2, w // sc))).astype(np.float32)
        acc += wt * np.asarray(Image.fromarray(g).resize((w, h), Image.BICUBIC), np.float32)
    acc -= acc.min()
    return acc / max(acc.max(), 1e-6)


def _blur(a, r):
    if r <= 0:
        return a
    im = Image.fromarray((np.clip(a, 0, 1) * 255).astype(np.uint8))
    return np.asarray(im.filter(ImageFilter.GaussianBlur(r)), np.float32) / 255


def realistic(mask, seed=1, pad=60):
    """실제 날인 재현: 지글지글한 외곽, 인주 빠짐, 압력 편차, 테두리 인주 고임, 번짐, 흐림."""
    rng = np.random.default_rng(seed)
    m = Image.new("L", (SIZE + pad * 2, SIZE + pad * 2), 0)
    m.paste(mask, (pad, pad))
    a = np.asarray(m, np.float32) / 255
    h, w = a.shape

    # 1) 외곽 떨림: 저주파+고주파 변위로 획 경계를 비틀기
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    dx = (_fbm(a.shape, rng, [90, 18, 5], [1, .5, .35]) - .5) * 9
    dy = (_fbm(a.shape, rng, [90, 18, 5], [1, .5, .35]) - .5) * 9
    xi = np.clip(xx + dx, 0, w - 1).astype(np.int32)
    yi = np.clip(yy + dy, 0, h - 1).astype(np.int32)
    a = a[yi, xi]

    # 2) 지글지글: 살짝 뭉갠 뒤 종이결 노이즈를 섞어 다시 이진화 → 톱니 외곽
    grain = _fbm(a.shape, rng, [3, 1], [1, .8])
    a = _blur(a, 2.2)
    a = (a + (grain - .5) * .75 > .5).astype(np.float32)

    # 3) 압력 편차: 한쪽으로 기운 손힘 + 얼룩
    ang = rng.uniform(0, 2 * np.pi)
    tilt = ((xx - w / 2) * np.cos(ang) + (yy - h / 2) * np.sin(ang)) / w
    pressure = np.clip(.78 + tilt * .55 + (_fbm(a.shape, rng, [140, 50], [1, .6]) - .5) * .6, .25, 1)

    # 4) 인주 빠짐: 압력 낮을수록 종이 요철에 인주가 안 묻음(하얀 점·긁힘)
    fiber = _fbm(a.shape, rng, [2, 1], [1, 1])
    streak = rng.random((h, w))  # 미세 점
    drop = (fiber > pressure * .9 + .07) | (streak > .997)
    a = a * (~drop)

    # 5) 테두리 인주 고임: 획 가장자리가 안쪽보다 진함
    core = _blur(a, 3.5)
    rim = np.clip(a - core, 0, 1) * 1.6
    dens = a * (.58 + .42 * pressure) + rim * .25

    # 6) 번짐(블리드) + 전체 흐림
    bleed = _blur(a, 4) * .22
    dens = np.maximum(dens, bleed)
    dens = _blur(dens, 1.1)
    dens = np.clip(dens * rng.uniform(.95, 1.05), 0, 1)

    # 7) 색: 진한 곳은 검붉은 주홍, 옅은 곳은 분홍빛
    t = dens[..., None]
    deep = np.array([178, 14, 26], np.float32)
    light = np.array([222, 58, 66], np.float32)
    rgb = light * (1 - t) + deep * t
    out = np.dstack([rgb, dens * 255]).astype(np.uint8)
    im = Image.fromarray(out, "RGBA")
    return im.rotate(rng.uniform(-3, 3), resample=Image.BICUBIC)


def on_paper(stamp, seed=0):
    """흰 서류 위에 찍힌 모습 미리보기(곱하기 합성)."""
    rng = np.random.default_rng(seed)
    w, h = stamp.size
    paper = 246 + (_fbm((h, w), rng, [4, 1], [1, 1]) - .5) * 10
    paper = np.dstack([paper, paper - 2, paper - 6])
    rgba = np.asarray(stamp, np.float32) / 255
    al = rgba[..., 3:4]
    out = paper * (1 - al) + paper * rgba[..., :3] * al
    return Image.fromarray(np.clip(out, 0, 255).astype(np.uint8))


def main(font_dir):
    variants = {
        "myeongjo": sorted(glob.glob(os.path.join(font_dir, "**/nanum-myeongjo-*-800-normal.woff"), recursive=True)),
        "gothic": glob.glob(os.path.join(font_dir, "**/Pretendard-Black.otf"), recursive=True),
    }
    for name, paths in variants.items():
        mask = build_mask(GlyphFonts(paths))
        colorize(mask).save(os.path.join(OUT, f"입예협회장_도장_{name}_clean.png"))
        stamped(mask).save(os.path.join(OUT, f"입예협회장_도장_{name}_stamp.png"))
        for k in (1, 2, 3):  # 실제 도장처럼 찍을 때마다 다른 3가지 인영
            r = realistic(mask, seed=k * 11 + len(name))
            r.save(os.path.join(OUT, f"입예협회장_도장_{name}_real{k}.png"))
            if k == 1:
                on_paper(r).save(os.path.join(OUT, f"입예협회장_도장_{name}_real_미리보기.jpg"), quality=92)
        print("ok", name)


if __name__ == "__main__":
    main(sys.argv[1])

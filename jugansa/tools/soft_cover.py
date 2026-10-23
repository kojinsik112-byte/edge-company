"""표지 사진 보정: 부드럽게(노이즈 정리 + 약한 선명화) + 10% 축소 + 둘레 흐림 채움 → 표지 칸(60% × 전체 높이) 비율 그대로 한 장으로 굽는다.
사용: python soft_cover.py <원본.jpg> <출력.jpg> [focal_x=0.74] [focal_y=0.40] [scale=0.9]"""
import sys
import cv2
import numpy as np
from PIL import Image, ImageFilter, ImageEnhance

src, dst = sys.argv[1], sys.argv[2]
fx = float(sys.argv[3]) if len(sys.argv) > 3 else 0.74
fy = float(sys.argv[4]) if len(sys.argv) > 4 else 0.40
k = float(sys.argv[5]) if len(sys.argv) > 5 else 0.9
W, H = 1348, 1588          # 표지 칸 1122.5 × 0.6 = 673.5 · 793.7 CSS px → 2배
im = cv2.imread(src)
# 부드럽게: JPEG 블록 · 계단 노이즈 정리(경계 보존) → 약한 언샤프
im = cv2.fastNlMeansDenoisingColored(im, None, 3, 3, 7, 21)
im = cv2.bilateralFilter(im, 5, 18, 5)
img = Image.fromarray(cv2.cvtColor(im, cv2.COLOR_BGR2RGB))
img = img.filter(ImageFilter.UnsharpMask(radius=1.4, percent=35, threshold=2))
iw, ih = img.size

def place(scale, blur=0):
    s = max(W / iw, H / ih) * scale
    w, h = round(iw * s), round(ih * s)
    x, y = round((W - w) * fx), round((H - h) * fy)
    r = img.resize((w, h), Image.LANCZOS)
    if blur:
        r = r.filter(ImageFilter.GaussianBlur(blur))
    return r, x, y, w, h

# 뒤: 같은 사진 1.08배 · 강한 흐림 · 살짝 어둡게
bg, bx, by, _, _ = place(1.08, blur=26)
bg = ImageEnhance.Brightness(bg).enhance(0.88)
canvas = Image.new("RGB", (W, H), (13, 30, 51))
canvas.paste(bg, (bx, by))
# 앞: 10% 축소 사진 · 가장자리 60px 페더
fg, x, y, w, h = place(k)
a = np.ones((h, w), np.float32)
F = 60
ramp = np.linspace(0, 1, F, dtype=np.float32)
a[:F, :] *= ramp[:, None]; a[-F:, :] *= ramp[::-1, None]
a[:, :F] *= ramp[None, :]; a[:, -F:] *= ramp[None, ::-1]
fg.putalpha(Image.fromarray((a * 255).astype(np.uint8)))
canvas.paste(fg, (x, y), fg)
canvas.save(dst, quality=92, optimize=True, progressive=True)
print(dst, canvas.size, "fg", (x, y, w, h))

"""야간 정면 컷 동 번호 '1'06' → '106' (픽셀 보정 · AI 생성 아님). 사용: fix.py 원본 출력 x오프셋"""
import cv2, numpy as np, sys
from PIL import Image, ImageDraw, ImageFont
src, dst, ox = sys.argv[1], sys.argv[2], int(sys.argv[3])
im = cv2.imread(src)
X0, Y0, X1, Y1 = 200 + ox, 572, 232 + ox, 593          # 글자 상자(벽면 · 오른쪽 어두운 동 제외)
LX = 214 + ox                                          # 글자 뒤 세로 조명 라인
g = im[Y0:Y1, X0:X1].mean(2)
m = (g < 75).astype(np.uint8) * 255
ys, xs = np.where(m > 0)
bx0, by0, bx1, by1 = xs.min() + X0, ys.min() + Y0, xs.max() + X0, ys.max() + Y0
col = im[Y0:Y1, X0:X1][m > 0]
col = tuple(int(v) for v in np.percentile(col, 30, axis=0)[::-1])   # 글자 색(RGB)
mask = np.zeros(im.shape[:2], np.uint8)
mask[Y0:Y1, X0:X1] = cv2.dilate(m, np.ones((3, 3), np.uint8), 1)
out = cv2.inpaint(im, mask, 4, cv2.INPAINT_TELEA)
ref = im[556:570, LX - 1:LX + 2].mean(0)               # 라인 색(글자 위쪽)
out[Y0:Y1, LX - 1:LX + 2] = ref.astype(np.uint8)
# '106' — 원래 글자 높이 · 폭에 맞춰 그림
H, W = by1 - by0 + 1, bx1 - bx0 + 1
f = ImageFont.truetype('/root/.local/share/fonts/Pretendard-Medium.otf', 120)
lay = Image.new('L', (400, 200), 0)
ImageDraw.Draw(lay).text((10, 10), '106', font=f, fill=255)
lay = lay.crop(lay.getbbox()).resize((W, H), Image.LANCZOS)
pil = Image.fromarray(cv2.cvtColor(out, cv2.COLOR_BGR2RGB))
pil.paste(Image.new('RGB', lay.size, col), (bx0, by0), lay)
pil.save(dst, quality=95)
print(f'{dst} · 글자 상자 {bx0},{by0} ~ {bx1},{by1} ({W}×{H}) · 색 {col}')

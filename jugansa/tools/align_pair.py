"""단지 비주얼팀(bid_visual) · 같은 구도의 낮 · 밤 사진 정렬기 (GIF 전 단계).

사용: python align_pair.py <낮.jpg> <밤.jpg> <출력폴더>
  → <출력폴더>/a_day.jpg · b_night.jpg (같은 크기 · 같은 구도, 정렬 뒤 비는 가장자리는 둘 다 잘라냄)

- 야간 연출은 보통 낮 투시도를 바탕으로 만들어 구도가 거의 같다 → SIFT 특징점 + 회전 · 이동 · 확대(닮음 변환)로 낮 사진을 밤 사진에 맞춘다.
- 겹쳐 넘길 때 건물이 두 겹으로 보이지 않게 하는 용도. 일치점이 적으면(12개 미만) 멈춘다 — 구도가 다른 사진이다.
- 확인용 반반 합성 `check_blend.jpg`도 같이 저장한다(건물 윤곽이 한 겹이면 정상).
"""
import os
import sys

import cv2
import numpy as np


def main():
    if len(sys.argv) != 4:
        sys.exit(__doc__)
    day, night, out = cv2.imread(sys.argv[1]), cv2.imread(sys.argv[2]), sys.argv[3]
    os.makedirs(out, exist_ok=True)
    g = [cv2.equalizeHist(cv2.cvtColor(x, cv2.COLOR_BGR2GRAY)) for x in (day, night)]
    sift = cv2.SIFT_create(6000)
    (k1, d1), (k2, d2) = (sift.detectAndCompute(x, None) for x in g)
    good = [a for a, b in cv2.BFMatcher().knnMatch(d1, d2, k=2) if a.distance < 0.75 * b.distance]
    src = np.float32([k1[a.queryIdx].pt for a in good])
    dst = np.float32([k2[a.trainIdx].pt for a in good])
    A, inl = cv2.estimateAffinePartial2D(src, dst, method=cv2.RANSAC, ransacReprojThreshold=4)
    if A is None or inl.sum() < 12:
        sys.exit(f"일치점 부족({0 if inl is None else int(inl.sum())}) — 같은 구도가 아님")
    H, W = night.shape[:2]
    warped = cv2.warpAffine(day, A, (W, H))
    mask = cv2.warpAffine(np.full(day.shape[:2], 255, np.uint8), A, (W, H))
    ok = mask > 250
    ys, xs = np.where(ok)
    y0, y1, x0, x1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
    while True:  # 비는 픽셀이 가장 많은 변부터 한 줄씩 깎아 빈틈 없는 사각형을 남긴다
        bad = {"t": (~ok[y0, x0:x1]).sum(), "b": (~ok[y1 - 1, x0:x1]).sum(), "l": (~ok[y0:y1, x0]).sum(), "r": (~ok[y0:y1, x1 - 1]).sum()}
        side = max(bad, key=bad.get)
        if not bad[side]:
            break
        if side == "t": y0 += 1
        elif side == "b": y1 -= 1
        elif side == "l": x0 += 1
        else: x1 -= 1
    crop = (slice(y0, y1), slice(x0, x1))
    cv2.imwrite(f"{out}/a_day.jpg", warped[crop], [cv2.IMWRITE_JPEG_QUALITY, 95])
    cv2.imwrite(f"{out}/b_night.jpg", night[crop], [cv2.IMWRITE_JPEG_QUALITY, 95])
    cv2.imwrite(f"{out}/check_blend.jpg", cv2.addWeighted(warped[crop], 0.5, night[crop], 0.5, 0))
    print(f"정렬 완료 · 일치점 {int(inl.sum())}/{len(good)} · 배율 {np.hypot(*A[0, :2]):.3f} · 남은 영역 {x1 - x0}×{y1 - y0}px → {out}")


if __name__ == "__main__":
    main()

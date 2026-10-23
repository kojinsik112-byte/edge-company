"""공고 원문(notice.txt) → 깃에 올릴 가림본. 착수 세션이 빌드 세션으로 원문을 넘길 때 쓴다(원본 hwp · pdf는 깃 제외).
가림: 휴대 · 일반 전화번호 · 주민등록번호 · 계좌번호처럼 보이는 숫자 · 개인 메일(공고의 접수 메일은 --keep으로 남김).
사람 이름은 기계로 못 가린다 → 끝에 '이름 확인' 줄을 출력하니 눈으로 보고 남은 이름은 직접 고친다.
사용: python3 jugansa/tools/mask_notice.py $SP/<약칭>/notice.txt jugansa/착수/<약칭>_공고원문_가림.txt --keep 접수@메일.com"""
import re, sys

PATS = [
    (r"\b01[016789][-.\s]?\d{3,4}[-.\s]?\d{4}\b", "010-****-****"),
    (r"\b0\d{1,2}[-.)\s]\d{3,4}[-.\s]\d{4}\b", "0**-****-****"),
    (r"\b\d{6}[-\s]?[1-4]\d{6}\b", "******-*******"),
    (r"\b\d{3,6}-\d{2,6}-\d{4,8}(-\d{1,4})?\b", "(계좌 가림)"),
]


def mask(t, keep=()):
    n = 0
    for p, r in PATS:
        t, k = re.subn(p, r, t); n += k
    def mail(m):
        nonlocal n
        if m.group(0).lower() in keep: return m.group(0)
        n += 1; return "(메일 가림)"
    t = re.sub(r"[\w.+-]+@[\w-]+(\.[\w-]+)+", mail, t)
    return t, n


if __name__ == "__main__":
    a = sys.argv[1:]
    keep = tuple(x.lower() for i, x in enumerate(a) if i and a[i - 1] == "--keep")
    src, dst = a[0], a[1]
    t, n = mask(open(src, encoding="utf-8").read(), keep)
    open(dst, "w", encoding="utf-8").write(t)
    print(f"가림 {n}곳 → {dst}")
    for m in re.finditer(r"(회장|위원장|대표|담당|총무|감사|간사|연락처)\s*[:：]?\s*([가-힣]{2,4})", t):
        print("이름 확인:", m.group(0))

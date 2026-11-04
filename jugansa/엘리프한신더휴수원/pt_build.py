"""엘리프 한신더휴 수원 2차 PT(11.08 14:20 ~ 15:10 · 1번 순서 · 발표 25분 + 질의 25분 · 호매실도서관 지하 1층) 준비자료 조립.
11.04 협의회 안내 반영: 발표 25분판 하나 · 유인물 15부 이상 · 안내 3-(4) 금전적 혜택 · 발전기금 · 타업체 비방 = 감점 → 화면 · 유인물 · 대본에 금액 0(빌드 때 검사 · 남으면 중단).
원본 HTML(PT준비/원본html · 깃 제외 폴더) → 00 ~ 04 PDF · 제출 제안서 밝은 시안(115쪽)에서 금액 없는 쪽만 + 정리 쪽 3(금액 없이 다시 쓴 다섯 질문 · 두 회차 기준 · 가격) + 요약 2 + A/S 화면 + 감사 인사.
옛 30분 · 20분판(금액 포함)은 PT준비/이전판_30분20분_금액포함_1104/. ★ = 넘기며 보여 줄 쪽. 근거 메모 = PT_준비_1108.md
    python pt_build.py
"""
import os, pathlib, re, subprocess
import pymupdf

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = r"C:\본부장\05주관사 입찰공고\20261029_엘리프 한신더휴 수원"
PT = os.path.join(BASE, "PT준비")
SRC = os.path.join(PT, "원본html")
PROP = os.path.join(HERE, "엣지컴퍼니_엘리프한신더휴수원_입주박람회_주관사_제안서_밝은시안.pdf")   # 제출본 ⑩과 같은 115쪽
DOCS = [("00_제출본_약속정리", "00_제출본_약속정리_내부용"), ("01_PT_발표대본_25분", "01_PT_발표대본_25분"),
        ("02_예상질문_답변", "02_예상질문_답변_내부용"), ("03_당일_체크리스트", "03_당일_시간표_체크리스트"),
        ("04_화면요약", "04_화면요약_2장"), ("04c_감사인사", "04c_감사인사"), ("04d_AS창구", "04d_AS창구_1장"),
        ("04e_PT정리쪽", "04e_PT정리쪽_3장"), ("09_협의회_확인메일_초안", "09_협의회_회신메일_초안")]
# 대본 01의 화면 순서와 같아야 함 — S1 · S2 = 요약 ① ②(금액 없는 판) · END = 감사 인사 · AS = A/S 한 창구 접수 화면(04d)
# Q · C6 · PR = 정리 쪽 ① 다섯 질문(p.60) ② 두 회차 기준 여섯 가지(p.66) ③ 가격 공개 · 계약 보호(p.32 · 34 · 69) — 제안서 문장에서 금액만 뺌
# BR = 경인 지사(경기남부) 계약서 모자이크본 · VR = 업체 모집 화면(파일이 있을 때만)
# 뺀 쪽: 59 · 66 · 69 · 86 ~ 90 · 113(금액) · 60 · 68 · 70 · 77(‘세대 혜택’ 표현) · 79 · 82(자기 평가 약점 · 보증 0건 = 질의 때 말로만)
#        39(견본 증권 그림에 고양창릉 S-5BL 이름이 남아 있음 = 제출본 그대로 · 화면에 띄우지 않음)
BRANCH = os.path.join(PT, "07_질의대비_경기남부지사_계약서_가림.pdf")   # 11-03 전대차계약서 모자이크본(칸 12px @200dpi)
BR_IN_DECK = True   # 11-03 본부장 확인: 소재지 '문화촌로11번길 43-8' 지번 = '비전동 866-3'(제안서 주소와 같음)
RECRUIT = os.path.join(PT, "근거", "업체모집_1장.pdf")
ORDER25 = [1, 64, "Q", 16, 17, 67, 20, 11, 75, "BR", 76, 65, "C6", 29, "VR", "PR", 34, 71, "AS", 45, 63, 72, 62, 74, "S1", "S2", "END"]
HANDOUT = [1, "S1", "Q", 16, 67, "C6", "PR", 71, "AS", 76, "S2"]   # 08 유인물 A4 11쪽 · 15부 이상(안내 3-(2)) · 금액 0 · 휴대번호 있는 p.11 · 계약서는 넣지 않음
# 금액 · 금전 혜택 · 타업체 · 협의회 임원 이름 — 화면 · 유인물 · 대본(말하는 부분)에 남으면 중단
BAN = re.compile(r"\d[\d,.]*\s*(만\s*)?원|\d\s*억|만원|상당|세대\s*혜택|지원금|발전|기금|상품권|경품|사은품|선물|이랑|목수와|칠쟁이|조동진")
CHROME = next(p for p in (r"C:\Program Files\Google\Chrome\Application\chrome.exe",
                          r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe") if os.path.exists(p))


def to_pdf(name, out):
    dst = os.path.join(PT, out + ".pdf")
    subprocess.run([CHROME, "--headless", "--no-sandbox", "--disable-gpu", "--no-pdf-header-footer", "--allow-file-access-from-files",
                    "--virtual-time-budget=8000", f"--print-to-pdf={dst}", pathlib.Path(os.path.join(SRC, name + ".html")).as_uri()],
                   check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return dst


def deck(order, prop, summ, end, asp, extra):
    d = pymupdf.open()
    for o in order:
        if o in ("Q", "C6", "PR"):
            i = ("Q", "C6", "PR").index(o)
            d.insert_pdf(extra, from_page=i, to_page=i)
        elif o == "S1" or o == "S2":
            d.insert_pdf(summ, from_page=0 if o == "S1" else 1, to_page=0 if o == "S1" else 1)
        elif o == "END":
            d.insert_pdf(end)
        elif o == "AS":
            d.insert_pdf(asp)
        elif o in ("BR", "VR"):
            f = BRANCH if o == "BR" else RECRUIT
            if os.path.exists(f) and (o == "VR" or BR_IN_DECK):
                d.insert_pdf(pymupdf.open(f))
        else:
            d.insert_pdf(prop, from_page=o - 1, to_page=o - 1)
    return d


def banned(doc, label):
    hits = []
    for i, pg in enumerate(doc):
        t = re.sub(r"\s+", " ", pg.get_text())
        hits += [f"{label} {i + 1}쪽: …{t[max(0, m.start() - 25):m.end() + 15]}…" for m in BAN.finditer(t)]
    return hits


def script_banned():
    s = open(os.path.join(SRC, "01_PT_발표대본_25분.html"), encoding="utf-8").read()
    say = " ".join(re.findall(r'<div class="say">(.*?)</div>', s, re.S))
    t = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", say))
    return [f"대본: …{t[max(0, m.start() - 25):m.end() + 15]}…" for m in BAN.finditer(t)]


def main():
    made = {out: to_pdf(name, out) for name, out in DOCS}
    prop, summ = pymupdf.open(PROP), pymupdf.open(made["04_화면요약_2장"])
    end, asp = pymupdf.open(made["04c_감사인사"]), pymupdf.open(made["04d_AS창구_1장"])
    extra = pymupdf.open(made["04e_PT정리쪽_3장"])
    assert (prop.page_count, summ.page_count, end.page_count, asp.page_count, extra.page_count) == (115, 2, 1, 1, 3),         (prop.page_count, summ.page_count, end.page_count, asp.page_count, extra.page_count)
    d = deck(ORDER25, prop, summ, end, asp, extra)
    h = deck(HANDOUT, prop, summ, end, asp, extra)
    bad = banned(d, "05 화면") + banned(h, "08 유인물") + script_banned()
    if bad:
        raise SystemExit("금액 · 금지어가 남았습니다(안내 3-(4)):\n" + "\n".join(bad))
    d.set_metadata({"title": "엘리프 한신더휴 수원 PT 발표화면 (25분 · %d쪽)" % d.page_count, "author": "주식회사 엣지컴퍼니"})
    d.save(os.path.join(PT, "05_발표화면_25분.pdf"), garbage=1, deflate=True)
    h.set_metadata({"title": "엘리프 한신더휴 수원 2차 PT 유인물 (A4 가로 · %d쪽)" % h.page_count, "author": "주식회사 엣지컴퍼니"})
    h.save(os.path.join(PT, "08_유인물_A4_%d쪽.pdf" % h.page_count), garbage=1, deflate=True)
    a = pymupdf.open()
    a.insert_pdf(prop)
    a.set_metadata({"title": "엘리프 한신더휴 수원 제안서 전체 (발표자 노트북 전용 · 화면에 띄우지 않음 · 115쪽)", "author": "주식회사 엣지컴퍼니"})
    a.save(os.path.join(PT, "06_부록_제안서전체_115쪽_화면금지.pdf"), garbage=1, deflate=True)
    for f in (end, extra):
        f.close()
    for k in ("04c_감사인사", "04e_PT정리쪽_3장"):
        os.remove(made[k])   # 05 · 08 안에만 씀
    old = os.path.join(PT, "06_부록_제안서전체_115쪽.pdf")
    if os.path.exists(old):
        os.remove(old)   # 같은 파일 · 이름만 바꿈(화면금지)
    for f in sorted(os.listdir(PT)):
        p = os.path.join(PT, f)
        if f.endswith(".pdf"):
            print(f, pymupdf.open(p).page_count, "쪽", round(os.path.getsize(p) / 1e6, 1), "MB")


if __name__ == "__main__":
    main()

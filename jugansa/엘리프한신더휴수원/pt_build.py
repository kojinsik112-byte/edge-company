"""엘리프 한신더휴 수원 2차 PT(11.08 14:00 · 호매실도서관) 준비자료 조립 — 오산 아테라 PT 패키지와 같은 구성.
원본 HTML(PT준비/원본html · 깃 제외 폴더) → 00 ~ 04 PDF · 제출 제안서 밝은 시안(115쪽) + 요약 2장 + 감사 인사 → 05 발표화면(30분 · 20분) · 06 부록.
★ = 넘기며 보여 줄 쪽(대본 한 줄). 근거 메모 = PT_준비_1108.md
    python pt_build.py
"""
import os, pathlib, subprocess
import pymupdf

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = r"C:\본부장\05주관사 입찰공고\20261029_엘리프 한신더휴 수원"
PT = os.path.join(BASE, "PT준비")
SRC = os.path.join(PT, "원본html")
PROP = os.path.join(HERE, "엣지컴퍼니_엘리프한신더휴수원_입주박람회_주관사_제안서_밝은시안.pdf")   # 제출본 ⑩과 같은 115쪽
DOCS = [("00_제출본_약속정리", "00_제출본_약속정리_내부용"), ("01_PT_발표대본_30분", "01_PT_발표대본_30분"),
        ("01b_PT_발표대본_20분", "01b_PT_발표대본_20분"), ("02_예상질문_답변", "02_예상질문_답변_내부용"),
        ("03_당일_체크리스트", "03_당일_체크리스트"), ("04_화면요약", "04_화면요약_2장"), ("04c_감사인사", "04c_감사인사"),
        ("04d_AS창구", "04d_AS창구_1장")]
# 대본 01 · 01b의 화면 순서와 같아야 함 — S1 · S2 = 요약 ① ② · END = 감사 인사(직통 번호 있는 p.115 대신)
# AS = A/S 한 창구 접수 화면(04d · 제출본 p.45 · 71 · '업체 먼저' 화면은 뺌) · BR = 경인 지사(경기남부) 계약서 가림본 — 파일이 있을 때만 넣음
BRANCH = os.path.join(PT, "07_질의대비_경기남부지사_계약서_가림.pdf")   # 11-03 전대차계약서 모자이크본(본부장 '살짝 보이게') + 기간 끝 · 전차인 주소 모자이크 추가(상자 가림 안 씀)
BR_IN_DECK = False   # 11-03: 화면에 넣지 않음(기간 2027.02.01 · 소재지 '문화촌로11번길 43-8'이 제안서 '비전동 866-3'과 같은 곳인지 미확인) → 질의 대비 출력만 · 확인되면 True
# VR = 업체 모집 프로그램 화면 1장(as-site 세션 · 11.03 뒤 재개) — 파일이 있을 때만 · 30분 = p.29 뒤 · 20분 = p.69 앞
RECRUIT = os.path.join(PT, "근거", "업체모집_1장.pdf")
ORDER30 = [1, 64, 59, 60, 11, 16, 17, 67, 75, "BR", 76, 65, 66, 68, 77, 29, "VR", 69, 34, 71, "AS", 45, 70, 72, 62, 63, 86, 87, 90, 79, 82, 74,
           "S1", "S2", 113, "END"]
ORDER20 = [1, 64, 59, 11, 67, 75, 65, 66, "VR", 69, 71, "AS", 70, 72, 87, 79, 82, "S1", "S2", "END"]
CHROME = next(p for p in (r"C:\Program Files\Google\Chrome\Application\chrome.exe",
                          r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe") if os.path.exists(p))


def to_pdf(name, out):
    dst = os.path.join(PT, out + ".pdf")
    subprocess.run([CHROME, "--headless", "--no-sandbox", "--disable-gpu", "--no-pdf-header-footer", "--allow-file-access-from-files",
                    "--virtual-time-budget=8000", f"--print-to-pdf={dst}", pathlib.Path(os.path.join(SRC, name + ".html")).as_uri()],
                   check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return dst


def deck(order, prop, summ, end, asp):
    d = pymupdf.open()
    for o in order:
        if o == "S1" or o == "S2":
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


def main():
    made = {out: to_pdf(name, out) for name, out in DOCS}
    prop, summ = pymupdf.open(PROP), pymupdf.open(made["04_화면요약_2장"])
    end, asp = pymupdf.open(made["04c_감사인사"]), pymupdf.open(made["04d_AS창구_1장"])
    assert prop.page_count == 115 and summ.page_count == 2 and end.page_count == 1 and asp.page_count == 1, (prop.page_count, summ.page_count, end.page_count, asp.page_count)
    for order, fn, title in ((ORDER30, "05_발표화면_30분.pdf", "30분 · %d쪽"), (ORDER20, "05b_발표화면_20분.pdf", "20분 · %d쪽")):
        d = deck(order, prop, summ, end, asp)
        d.set_metadata({"title": "엘리프 한신더휴 수원 PT 발표화면 (" + title % d.page_count + ")", "author": "주식회사 엣지컴퍼니"})
        d.save(os.path.join(PT, fn), garbage=1, deflate=True)
    a = pymupdf.open()
    a.insert_pdf(prop)
    a.set_metadata({"title": "엘리프 한신더휴 수원 제안서 전체 (부록 · 115쪽 · 제출본 ⑩과 같음)", "author": "주식회사 엣지컴퍼니"})
    a.save(os.path.join(PT, "06_부록_제안서전체_115쪽.pdf"), garbage=1, deflate=True)
    end.close()
    os.remove(made["04c_감사인사"])   # 05 화면 안에만 씀
    for f in sorted(os.listdir(PT)):
        p = os.path.join(PT, f)
        if f.endswith(".pdf"):
            print(f, pymupdf.open(p).page_count, "쪽", round(os.path.getsize(p) / 1e6, 1), "MB")


if __name__ == "__main__":
    main()

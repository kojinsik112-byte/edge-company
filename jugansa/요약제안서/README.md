# 엣지컴퍼니 요약제안서 — 수정·출력 방법

## 폴더 구성
| 파일 | 역할 |
|---|---|
| `build.py` | **문구·순서 전부 여기서 수정** → 실행하면 HTML+PDF 생성 |
| `make_images.py` | 경관조명 일러스트 4종(SVG) 생성 |
| `assets/` | 사진·일러스트·폰트 |
| `엣지컴퍼니_요약제안서_v5.pdf` | 최신 출력본 |

## 본부장님 PC에서 수정하기 (C:\본부장\Claude_Code)
1. 이 폴더를 `C:\본부장\Claude_Code\요약제안서` 에 둔다 (zip 압축 풀기).
2. Claude 데스크탑 앱 → **Code** 탭 → **Local** → 폴더 `C:\본부장\Claude_Code` 선택.
3. "요약제안서 2차 수정하자: ○○페이지 ~~ 바꿔줘" 라고 지시하면 Claude가 `build.py`를 고치고 PDF를 다시 뽑아 **같은 폴더에 바로 저장**한다.

## 직접 출력할 때
```powershell
cd C:\본부장\Claude_Code\요약제안서
python build.py
```
- 필요: Python 3, Chrome 또는 Edge(윈도우 기본 설치). 인터넷 연결 시 Pretendard 폰트 자동 적용(없으면 맑은 고딕).
- 문구 강조(골드색)는 `[[강조할 말]]` 로 표기.

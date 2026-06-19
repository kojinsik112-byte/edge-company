# 네이버 캡처 스크립트 — 🔴 절대 규칙

## ★★★ 상품 상세 페이지는 반드시 "상세정보 펼쳐보기" 클릭 후 캡처 ★★★
회장 반복 지시(꼭 저장). **안 누르면 인트로+요약만 나오고 본문이 빈칸(회색)으로 캡처됨.**
- 모든 캡처 스크립트에 `getByText('상세정보 펼쳐보기').click()` 가 들어가 있어야 한다.
- 펼치면 페이지가 매우 길어짐(우리 4만px, 경쟁사 10만px) → **통짜 스크린샷 금지, 화면 단위 분할 캡처**(scroll+viewport)로 캔버스 한계 회피.
- 로그인 세션 필요: 어제 프로필 `%TEMP%\arco_cdp` 재사용 (디버그 Chrome 9222). 새 프로필이면 봇차단("서비스 접속 불가").

## 스크립트
| 파일 | 용도 | 펼쳐보기 |
|---|---|---|
| `naver_cdp.js` | 경쟁사 9곳 일괄 | ✅ |
| `acro_detail.js` | 우리 제품 상세(펼침+분할) | ✅ |
| `acro_gather.js` | 검색+우리 제품 | ✅(상품페이지) |

## 실행 (회장 PC)
```powershell
# 1) 어제 로그인 프로필로 디버그 크롬 띄우기
$ud="$env:TEMP\arco_cdp"
Start-Process chrome.exe --remote-debugging-port=9222 --user-data-dir="$ud" --new-window "https://smartstore.naver.com/edge2050/products/11887564363"
# 2) 캡처(펼쳐보기 자동 클릭됨)
& "C:\Program Files\nodejs\node.exe" acro_detail.js
```
산출물: `scout_reports/`(원본=로컬, 썸네일+텍스트=git). 원본 대용량은 `scout_reports/.gitignore`.

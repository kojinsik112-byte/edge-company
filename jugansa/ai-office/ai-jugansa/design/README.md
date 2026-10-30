# AI 오피스 v2 디자인 · 캐릭터 스킨

7개 팀 사무실 + 본부장실 + 상황실(현황판) 시안과 캐릭터 스킨을 둔다. 실제 오피스 화면(`../index.html`)을 이 시안으로 바꿀 때 같은 스킨 이름을 그대로 쓴다.

## 스킨 불러오기

```
python office_mock.py --skin 귀여운직원_v1     # 오피스 전체 시안 (office_<스킨>.png)
python roster.py --skin 원피스직원_v1          # 캐릭터 전체 한 장 (skins/<스킨>/roster.png)
```

| 스킨 | 상태 | 내용 |
|---|---|---|
| `귀여운직원_v1` | 확정(본부장 10-30 시안 5) | 큰 머리 치비 · 35명 전원 다른 머리 · 소품 · 옷 · 본부장 정장 |
| `원피스직원_v1` | 3버전 시안(선택 대기) | SVG 고품질판 · 원피스 주요 캐릭터 오마주 36명 · 본부장 = 루피(기어5 니카) · 성격별 표정 · 포즈 · 팀 완장 · `python roster_svg.py --style A\|B\|C` · **본부장 PC 전용(외부 게시 · 홍보 금지)** |

## 오피스 v4 (3D 입체 사무실 · 사무실 스킨)

```
python office_html.py --office 월넛라운지 --skin 원피스직원_v1      # previews/ 에 시안 저장 (크롬 2배 해상도)
```

- 사무실 스킨 = `office_skins.py`: `월넛라운지`(월넛 패널 · 황동 · 오크 바닥) · `마블펜트하우스`(흰 대리석 · 통유리 낮 도시) · `나이트스카이`(남색 · 금색 핀스트라이프 · 야경 · 팀 색 무드등)
- 방마다 뒷벽 · 옆벽 · 원근 바닥 · 벽 조명 · 빛 웅덩이로 입체감. 책상 두 줄 · 전원 정면(면접 느낌 없앰). 일하면 눈 뜨고 노트북 켜짐 · 쉬면 눈 감고 노트북 닫힘.
- 캐릭터 스킨(skins/)과 사무실 스킨은 따로 골라 조합한다.

## 스킨 만드는 법

`skins/<이름>/` 에 아래 파일을 둔다.

- `chibi.py`: `new_look(team, i)`(자리별 캐릭터) · `BOSS_LOOK` · `chibi(cx, cy, shirt, lk, working, back=False, suit=False, stand=False, paper=False, team=None)` 를 정의한다. 그리기 함수(rr · el · poly · arc · line · rect · D · P · mix)는 부르는 쪽(office_mock · roster) 것을 쓴다.
- `skin.json`: 이름 · 저장일 · 상태 · 설명(원피스는 팀별 배역 목록도).
- `preview.png` 또는 `roster.png`: 미리보기.

팀 키(scout · analysis · build · audit · mail · pt · retro)와 좌석 수(4 · 5 · 8 · 6 · 4 · 4 · 4)는 `server.py` `TEAM_ROOM`과 같다. 스킨은 그림만 바꾸며, 팀 명령 · 훅 · 방 배정은 바꾸지 않는다.

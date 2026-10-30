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

## 스킨 만드는 법

`skins/<이름>/` 에 아래 파일을 둔다.

- `chibi.py`: `new_look(team, i)`(자리별 캐릭터) · `BOSS_LOOK` · `chibi(cx, cy, shirt, lk, working, back=False, suit=False, stand=False, paper=False, team=None)` 를 정의한다. 그리기 함수(rr · el · poly · arc · line · rect · D · P · mix)는 부르는 쪽(office_mock · roster) 것을 쓴다.
- `skin.json`: 이름 · 저장일 · 상태 · 설명(원피스는 팀별 배역 목록도).
- `preview.png` 또는 `roster.png`: 미리보기.

팀 키(scout · analysis · build · audit · mail · pt · retro)와 좌석 수(4 · 5 · 8 · 6 · 4 · 4 · 4)는 `server.py` `TEAM_ROOM`과 같다. 스킨은 그림만 바꾸며, 팀 명령 · 훅 · 방 배정은 바꾸지 않는다.

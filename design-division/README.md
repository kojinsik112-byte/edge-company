# 디자인 본부 (Edge Design Division)

아크로(ARCO) 조명·실링팬 제품의 **상세페이지를 자동으로 기획·생성·검수**하는 에이전트 조직입니다.
회장(오너) → 총괄 본부장(Claude) → 7개 팀이 하나의 파이프라인으로 움직입니다.

```
상품 + 스펙 투입
   │
   ▼
① Scout(벤치마킹) → ② Planner(기획) → ③ Writer(카피) ─┐
                                                        ├─▶ ④ Designer(이미지) ─▶ ⑤ Compose(조판)
                                       ⑥ Auditor(검수) ◀┘                              │
                                                                                       ▼
                                                                          상세페이지(긴 PNG/HTML)
                                                                                       │
                                                                                       ▼
                                                                          ⑦ Operator(네이버 등록 패키지)
```

## 설계 원칙

- **두뇌는 Claude, 손발은 이미지 API, 조립은 파이썬.** 벤더 종속을 피하려고 모든 이미지 모델은
  교체 가능한 **어댑터**로 감쌌습니다. (`edge_design/adapters/`)
- **합법적 벤치마킹.** Scout는 잘 팔리는 상세페이지의 *구성·후킹·신뢰요소 패턴*만 분해하고,
  결과물은 100% 오리지널로 만듭니다. Auditor가 표절 흔적·과대광고·표시광고법 표현을 역으로 검사합니다.
- **제품이 주연.** 아크로는 조명/실링팬이므로 *설치 높이·풍량·소음(dB)·디밍 단계·색온도·소비전력* 같은
  스펙을 **인포그래픽으로 시각화**하는 것이 승부처입니다.

## 갈락티코 라인업 (포지션별 최강 도구, 어댑터로 연결)

| 포지션 | 작업(task) | 1순위 어댑터 | 대안 |
|--------|-----------|--------------|------|
| 포토리얼 제품/공간 연출 | `scene` | `imagen` (Imagen 4 Ultra) | `gemini`, `flux` |
| 제품 합성·편집·일관성 | `edit` | `gemini` (Gemini 3 Pro Image) | `flux` |
| 한글 카피 박힌 배너 | `text_banner` | `ideogram` (Ideogram v3) | `gemini` |
| 누끼·배경교체·4K 업스케일 | `cleanup` | `claid` | `photoroom` |
| 피팅모델 착장(라이프스타일) | `tryon` | `fashn` (FASHN.ai) | `wearview` |
| 스펙 인포그래픽 조판 | `compose` | 자체 엔진(Jinja2+Playwright) | — |

> 키가 없으면 자동으로 **드라이런(placeholder)** 으로 동작해 파이프라인 전체가 끝까지 돌아갑니다.
> 실제 화질 비교는 무료 크레딧으로 같은 상품을 여러 어댑터에 돌려 본부장이 최종 확정합니다.

## 빠른 시작

```bash
cd design-division
pip install -r requirements.txt
cp .env.example .env        # 가진 API 키만 채우면 됩니다 (없어도 드라이런 동작)

# 샘플 브리프로 상세페이지 1장 만들어보기 (드라이런)
python -m edge_design.cli build briefs/sample_ceiling_fan.yaml -o output
```

## 폴더 구조

```
design-division/
├── edge_design/
│   ├── adapters/      # 교체 가능한 이미지 모델 어댑터 (갈락티코 선수들)
│   ├── pipeline/      # designer/compose 등 파이프라인 단계
│   ├── config.py      # .env + config.yaml 로딩
│   └── cli.py         # 진입점
├── templates/         # 상세페이지 / 스펙 인포그래픽 HTML 템플릿
├── briefs/            # 상품 브리프(스펙) 입력 파일
├── .env.example
└── requirements.txt
```

Claude Code 서브에이전트(감독·팀원 역할)는 저장소 루트의 `.claude/agents/` 에 정의돼 있어
Claude Max 안에서 추가 비용 없이 팀을 직접 호출할 수 있습니다.

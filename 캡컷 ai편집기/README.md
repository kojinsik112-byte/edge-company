# 캡컷 AI 편집기 (autoedit)

촬영 원본 하나만 넣으면 **무음 컷 → 자동 자막 → 숏츠 생성 → 인트로/아웃트로/BGM**까지
한 번에 끝내는, 캡컷 스타일의 AI 자동 편집 CLI 도구입니다. 당신은 촬영만, 편집은 AI가 합니다.

```
촬영본.mp4  ──▶  ✂️ 무음 컷  ──▶  💬 자막  ──▶  📱 숏츠  ──▶  🎬 인트로/아웃트로/BGM  ──▶  완성본 + 숏츠들
```

## 기능

- **무음 구간 자동 컷** — 말 사이의 침묵/공백을 감지해 잘라내 영상을 깔끔하게 압축
- **자동 자막 생성** — Whisper 음성 인식으로 자막(SRT)을 만들고 영상에 구워 넣음
- **숏츠 자동 생성** — 말소리 밀도로 하이라이트를 골라 세로형(9:16) 숏츠 N개 생성
- **인트로/아웃트로/BGM** — 정해둔 자원을 앞뒤로 붙이고 배경음악을 낮은 볼륨으로 믹싱

각 단계는 켜고 끌 수 있고, 필요한 자원(인트로 등)이 없으면 자동으로 건너뜁니다.

## 설치

### 1) ffmpeg (필수)

영상 처리는 시스템 `ffmpeg` 를 사용합니다.

```bash
# macOS
brew install ffmpeg
# Ubuntu / Debian
sudo apt install ffmpeg
# Windows: https://www.gyan.dev/ffmpeg/builds/ 에서 받아 PATH 에 등록
```

설치 확인: `ffmpeg -version`

### 2) 파이썬 패키지

```bash
pip install -r requirements.txt
# 또는 패키지로 설치 (autoedit 명령 등록)
pip install -e .
```

> 자막 생성에 쓰는 `faster-whisper` 는 첫 실행 시 모델을 자동으로 내려받습니다.
> 한글 자막을 영상에 구울 때는 시스템에 한글 폰트(예: `NanumGothic`)가 있어야 합니다.

## 사용법

```bash
# 전체 자동 편집 (출력은 ./output 폴더)
autoedit edit 촬영본.mp4

# 특정 단계만 끄기
autoedit edit 촬영본.mp4 --no-shorts
autoedit edit 촬영본.mp4 --no-subtitles --no-branding

# 숏츠 5개, 출력 폴더 지정
autoedit edit 촬영본.mp4 --shorts-count 5 -o 결과폴더

# 설정 파일로 세밀하게 제어
autoedit init-config            # config.yaml 템플릿 생성
autoedit edit 촬영본.mp4 -c config.yaml
```

`autoedit` 명령을 설치하지 않았다면 모듈로 실행해도 됩니다:

```bash
python -m autoedit.cli edit 촬영본.mp4
```

## 출력물

```
output/
├── 촬영본_edited.mp4     # 완성된 강의영상
├── 촬영본.srt            # 자막 파일
└── shorts/
    ├── 촬영본_short1.mp4  # 세로형 숏츠
    ├── 촬영본_short2.mp4
    └── 촬영본_short3.mp4
```

## 인트로/아웃트로/BGM 설정

`assets/` 폴더에 `intro.mp4`, `outro.mp4`, `bgm.mp3` 를 넣으면 자동으로 사용됩니다.
파일명/경로는 `config.yaml` 의 `branding` 항목에서 바꿀 수 있습니다. 없는 자원은 건너뜁니다.

## 설정 옵션 (config.yaml)

| 섹션 | 주요 항목 | 설명 |
|------|-----------|------|
| `silence` | `noise_db`, `min_silence`, `keep_pad` | 무음 판정 기준(dB), 잘라낼 최소 무음 길이, 말 앞뒤 여유 |
| `subtitle` | `model`, `language`, `burn_in`, `font` | Whisper 모델 크기, 언어, 번인 여부, 폰트 |
| `shorts` | `count`, `min_duration`, `max_duration` | 숏츠 개수와 길이 범위 |
| `branding` | `intro`, `outro`, `bgm`, `bgm_volume` | 브랜딩 자원 경로와 BGM 볼륨 |
| `output` | `width`, `height`, `fps`, `crf`, `preset` | 출력 해상도/프레임/화질/인코딩 속도 |

전체 옵션은 `config.example.yaml` 을 참고하세요.

## 동작 방식 (요약)

1. **무음 컷** — `ffmpeg silencedetect` 로 무음 구간을 찾고 그 여집합(말소리)만 이어 붙입니다.
2. **자막** — 오디오를 16kHz WAV로 추출 → `faster-whisper` 로 인식 → SRT 작성 → `subtitles` 필터로 번인.
3. **숏츠** — 자막의 초당 글자수로 하이라이트 후보를 점수화 → 겹치지 않게 상위 N개 선택 → 9:16 cover-crop + 자막.
4. **브랜딩** — 본 영상에 BGM을 믹싱하고 인트로/아웃트로를 규격 통일 후 이어 붙입니다.

## 라이선스

MIT

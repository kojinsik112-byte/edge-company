# 캡컷 AI 편집기 (autoedit)

촬영 원본 하나만 넣으면 **무음 컷 → 자동 자막 → 숏츠 생성 → 인트로/아웃트로/BGM**까지
한 번에 끝내는, 캡컷 스타일의 AI 자동 편집 CLI 도구입니다. 당신은 촬영만, 편집은 AI가 합니다.

```
촬영본.mp4  ──▶  ✂️ 무음 컷  ──▶  💬 자막  ──▶  📱 숏츠  ──▶  🎬 인트로/아웃트로/BGM  ──▶  완성본 + 숏츠들
```

## 기능

- **AI 스마트 편집** — Claude가 자막 내용을 이해해 **같은 뜻 반복·비문·꼬인 문장·잡담**을 잘라냄 (Anthropic API 키 필요, 없으면 글자비교 휴리스틱으로 폴백)
- **말하는 구간만 남기기** — AI가 찾은 실제 발화(단어 단위)만 남기고 준비·응시·무음·문장 내 멈칫까지 제거
- **추임새 자동 제거** — "어", "아", "음" 같은 추임새만 있는 구간을 영상·자막에서 통째로 제거
- **자동 자막 생성** — Whisper 음성 인식으로 자막(SRT)을 만들고 영상 해상도에 맞춰 구워 넣음
- **자막 오타 수정** — 만들어진 `.srt`를 고친 뒤 다시 구울 수 있음 (`자막수정반영.bat`)
- **숏츠 자동 생성** — 말소리 밀도로 하이라이트를 골라 세로형(9:16) 숏츠 N개 생성 (세로 자막 포함)
- **인트로/아웃트로/BGM** — 정해둔 자원을 앞뒤로 붙이고 배경음악을 낮은 볼륨으로 믹싱

각 단계는 켜고 끌 수 있고, 필요한 자원(인트로 등)이 없으면 자동으로 건너뜁니다.

### 자막 오타 수정 방법

AI 음성인식은 가끔 단어를 잘못 알아듣습니다. 고치는 법:

1. `편집하기.bat`로 한 번 편집하면 **바탕화면 `캡컷_완성본\(영상이름)\`** 폴더에 `(이름).srt` 자막과 `(이름)_clean.mp4`가 생깁니다.
2. 그 폴더의 `(이름).srt`를 **메모장으로 열어** 오타를 고치고 저장합니다.
3. **원래 영상**을 `자막수정반영.bat` 위로 드래그하면, 무음컷·음성인식 없이 **수정된 자막으로 빠르게 다시** 완성 영상과 숏츠를 만듭니다.

명령줄로는: `autoedit reburn output\이름_clean.mp4 output\이름.srt -o output`

---

## 🪟 Windows 사용자 — 가장 쉬운 방법 (명령어 몰라도 OK)

영상은 **본인 컴퓨터에서** 편집합니다. 어디 올릴 필요 없고, 용량 제한도 없습니다.

1. **파이썬 설치** (한 번만)
   - https://www.python.org/downloads/ 에서 다운로드 → 설치
   - ⚠️ 설치 첫 화면에서 **"Add Python to PATH"** 체크 필수!
2. 이 폴더(`캡컷 ai편집기`)를 컴퓨터에 내려받습니다.
   ([GitHub에서 **Code → Download ZIP**] 으로 받아 압축 풀기)
3. **`설치.bat`** 더블클릭 → 자동으로 모든 게 설치됩니다 (ffmpeg 포함, 몇 분 소요)
4. 편집할 영상을 **`편집하기.bat`** 위로 **마우스로 끌어다 놓기(드래그&드롭)**
5. 끝! 잠시 기다리면 **바탕화면 `캡컷_완성본\(영상이름)\`** 폴더에 **완성 영상 + 자막 + 숏츠**가 생깁니다.

> ffmpeg는 `설치.bat`이 자동으로 챙기므로 따로 설치할 필요가 없습니다.

---

## 설치 (명령줄 / 개발자용)

### 1) 파이썬 패키지

```bash
pip install -r requirements.txt
# 또는 패키지로 설치 (autoedit 명령 등록)
pip install -e .
```

`imageio-ffmpeg` 가 함께 설치되어 **ffmpeg 가 자동 동봉**됩니다 — 시스템에 ffmpeg가 없어도 동작합니다.
직접 설치하고 싶다면(더 빠름):

```bash
# macOS
brew install ffmpeg
# Ubuntu / Debian
sudo apt install ffmpeg
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

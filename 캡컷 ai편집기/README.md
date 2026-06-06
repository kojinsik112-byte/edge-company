# 캡컷 AI 편집기 (autoedit)

촬영 원본 하나만 넣으면 **무음 컷 → 자동 자막 → 숏츠 생성 → 인트로/아웃트로/BGM**까지
한 번에 끝내는, 캡컷 스타일의 AI 자동 편집 CLI 도구입니다. 당신은 촬영만, 편집은 AI가 합니다.

```
촬영본.mp4  ──▶  ✂️ 무음 컷  ──▶  💬 자막  ──▶  📱 숏츠  ──▶  🎬 인트로/아웃트로/BGM  ──▶  완성본 + 숏츠들
```

## 기능

- **무음 구간 자동 컷** — 말 사이의 침묵/공백을 감지해 잘라내 영상을 깔끔하게 압축
- **오디오 볼륨 균일화** — loudnorm으로 유튜브 권장 음량(-14 LUFS)에 맞춰 소리 크기를 고르게
- **자동 자막 생성** — Whisper 음성 인식으로 자막(SRT)을 만들고 영상에 구워 넣음 (오타는 직접 수정 가능)
- **숏츠 자동 생성** — 말소리 밀도로 하이라이트를 골라 세로형(9:16) 숏츠 N개 생성 (자막 배경 박스/시작 효과음 옵션)
- **인트로/아웃트로/BGM** — 정해둔 자원을 앞뒤로 붙이고 배경음악을 낮은 볼륨으로 믹싱

각 단계는 켜고 끌 수 있고, 필요한 자원(인트로 등)이 없으면 자동으로 건너뜁니다.

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
5. 끝! 잠시 기다리면 `output` 폴더에 **완성 영상 + 자막 + 숏츠**가 생깁니다.

> ffmpeg는 `설치.bat`이 자동으로 챙기므로 따로 설치할 필요가 없습니다.

### ✏️ 자막 오타 직접 고치기 (마우스만으로)

AI 자막은 가끔 오타가 납니다. 명령어 없이 메모장만으로 고칠 수 있습니다.

1. 평소처럼 영상을 **`편집하기.bat`** 위에 끌어다 놓아 한 번 편집합니다.
2. 편집이 끝나면 **영상 파일 바로 옆에 같은 이름의 `.srt` 자막 파일**이 생깁니다.
   (예: `촬영본.mp4` → `촬영본.srt`)
3. 그 `.srt` 파일을 **메모장으로 열어 오타를 고치고 저장**합니다.
   (시간 줄 `00:00:01,000 --> 00:00:03,000` 은 그대로 두고, 글자만 고치세요.)
4. **같은 영상을 다시 `편집하기.bat` 위에 끌어다 놓습니다.**
   → 옆에 고친 자막이 있으면 음성 인식을 건너뛰고 **고친 자막 그대로** 본편과 숏츠에 다시 입힙니다. (훨씬 빠릅니다.)

### 📱 숏츠 자막이 너무 크거나 짤릴 때

자막 크기는 `config.yaml` 에서 **픽셀 단위**로 직접 조절합니다.

- 숏츠 자막이 크거나 양옆이 짤리면 → `shorts.font_size` 를 줄이고(예: 56→48),
  `shorts.max_line_chars`(한 줄 글자수)도 줄이면 더 안전합니다.
- 자막이 너무 아래/위에 붙으면 → `shorts.margin_v`(하단 여백) 조절.
- 배경이 복잡해 글자가 안 보이면 → `shorts.background_box: true`(기본 켜짐)로 반투명 박스.

### 🔊 효과음 넣기 (옵션)

`assets/` 폴더에 효과음 파일(예: `hook.wav`)을 넣고 `config.yaml` 에서 지정하면,
**각 숏츠 시작**에 한 번 깔립니다.

```yaml
shorts:
  start_sfx: hook.wav   # assets/ 기준
  sfx_volume: 0.9
```

> 컷마다 자동으로 "휙" 소리를 넣지 않는 이유: 무음 컷으로 잘린 지점이 많아
> 전부 효과음을 깔면 오히려 산만하고 싸구려처럼 들리기 쉽기 때문입니다.
> 시작 효과음 하나로 "훅(hook)"을 주는 게 더 효과적입니다.

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

# 오타를 직접 고친 자막으로 다시 편집 (음성 인식 건너뜀)
autoedit edit 촬영본.mp4 --srt 촬영본.srt

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
| `subtitle` | `model`, `initial_prompt`, `font_size`, `background_box` | Whisper 모델 크기, 용어 힌트, 자막 크기(px), 배경 박스 |
| `shorts` | `count`, `font_size`, `background_box`, `start_sfx` | 숏츠 개수, 자막 크기(px), 배경 박스, 시작 효과음 |
| `branding` | `intro`, `outro`, `bgm`, `bgm_volume` | 브랜딩 자원 경로와 BGM 볼륨 |
| `output` | `crf`, `preset`, `normalize_audio`, `loudness_target` | 화질/인코딩 속도, 볼륨 균일화 여부와 목표 음량 |

전체 옵션은 `config.example.yaml` 을 참고하세요.

## 동작 방식 (요약)

1. **무음 컷** — `ffmpeg silencedetect` 로 무음 구간을 찾고 그 여집합(말소리)만 이어 붙입니다.
2. **볼륨 균일화** — `loudnorm` 으로 음량을 목표 LUFS에 맞춰 영상 간 소리 크기를 고르게 합니다.
3. **자막** — 오디오를 16kHz WAV로 추출 → `faster-whisper` 로 인식 → SRT 작성 → `subtitles` 필터로 번인. 생성된 SRT는 직접 고쳐 다시 쓸 수 있습니다.
4. **숏츠** — 자막의 초당 글자수로 하이라이트 후보를 점수화 → 겹치지 않게 상위 N개 선택 → 9:16 cover-crop + 자막(배경 박스) + 시작 효과음(옵션).
5. **브랜딩** — 본 영상에 BGM을 믹싱하고 인트로/아웃트로를 규격 통일 후 이어 붙입니다.

## 라이선스

MIT

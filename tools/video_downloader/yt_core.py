"""유튜브 영상 추출 엔진 (GUI·CLI 공용).

yt-dlp로 영상 정보를 읽어 화질 목록(2160p/1080p/720p/480p...)을 만들고,
선택한 화질로 영상+음성을 받아 MP4 한 파일로 합친다.
ffmpeg는 imageio-ffmpeg가 내장 바이너리를 제공하므로 따로 설치할 필요 없다.
"""
from __future__ import annotations

import os
from dataclasses import dataclass

import yt_dlp
from yt_dlp.postprocessor.metadataparser import MetadataParserPP

AUDIO_MP3 = "audio_mp3"


@dataclass
class QualityOption:
    key: str            # "1080" 같은 높이값, 또는 AUDIO_MP3
    label: str          # 화면 표시용 "1080p (Full HD)"
    size_bytes: int | None
    codec: str          # "H.264" / "VP9" / "AV1" / "MP3"
    fps: int | None
    fmt: str = ""       # 실제 받을 yt-dlp 포맷 ID (목록과 결과를 일치시킴)

    def display(self) -> str:
        size = f"약 {human_size(self.size_bytes)}" if self.size_bytes else "용량 미표시"
        fps = f" · {self.fps}fps" if self.fps and self.fps > 30 else ""
        return f"{self.label}  ·  {size}  ·  {self.codec}{fps}"


QUALITY_NAMES = {
    4320: "8K", 2160: "4K", 1440: "QHD", 1080: "Full HD",
    720: "HD", 480: "SD", 360: "저화질", 240: "저화질", 144: "최저화질",
}


def human_size(n: int | None) -> str:
    if not n:
        return "-"
    for unit in ("B", "KB", "MB", "GB"):
        if n < 1024 or unit == "GB":
            return f"{n:.0f}{unit}" if unit in ("B", "KB") else f"{n:.1f}{unit}"
        n /= 1024
    return f"{n:.1f}GB"


def ffmpeg_path() -> str | None:
    try:
        import imageio_ffmpeg
        return imageio_ffmpeg.get_ffmpeg_exe()
    except Exception:
        return None  # 시스템 PATH의 ffmpeg 사용


def _base_opts() -> dict:
    opts = {"noplaylist": True, "quiet": True, "no_warnings": True, "noprogress": True}
    ff = ffmpeg_path()
    if ff:
        opts["ffmpeg_location"] = ff
    return opts


def fetch_info(url: str) -> dict:
    with yt_dlp.YoutubeDL(_base_opts()) as ydl:
        return ydl.extract_info(url, download=False)


def _fsize(f: dict) -> int | None:
    return f.get("filesize") or f.get("filesize_approx")


def _codec_name(vcodec: str) -> str:
    v = (vcodec or "").lower()
    if v.startswith("avc1") or v.startswith("h264"):
        return "H.264"
    if v.startswith("vp09") or v.startswith("vp9"):
        return "VP9"
    if v.startswith("av01"):
        return "AV1"
    return vcodec or "?"


def _best_audio(formats: list[dict]) -> dict | None:
    audios = [f for f in formats
              if f.get("vcodec") == "none" and f.get("acodec") not in (None, "none")]
    m4a = [f for f in audios if f.get("ext") == "m4a"]
    pool = m4a or audios
    return max(pool, key=lambda f: f.get("abr") or f.get("tbr") or 0, default=None)


# 호환 우선 순위: H.264(어디서나 재생) > VP9 > AV1(구형 PC 재생 불가 가능)
_COMPAT_RANK = {"H.264": 3, "VP9": 2, "AV1": 1}


def _pick_video(formats: list[dict], height: int, prefer_h264: bool) -> dict | None:
    vids = [f for f in formats
            if f.get("height") == height and f.get("vcodec") not in (None, "none")]
    if not vids:
        return None
    if prefer_h264:
        key = lambda f: (_COMPAT_RANK.get(_codec_name(f.get("vcodec")), 0),
                         f.get("fps") or 0, f.get("tbr") or 0)
    else:
        key = lambda f: (f.get("fps") or 0, f.get("tbr") or 0)
    return max(vids, key=key)


def list_qualities(info: dict, prefer_h264: bool = True) -> list[QualityOption]:
    formats = info.get("formats") or []
    heights = sorted({f["height"] for f in formats
                      if f.get("height") and f.get("vcodec") not in (None, "none")},
                     reverse=True)
    audio = _best_audio(formats)
    a_size = _fsize(audio) if audio else 0

    options = []
    for h in heights:
        v = _pick_video(formats, h, prefer_h264)
        if not v:
            continue
        v_size = _fsize(v)
        # 영상+음성 합본(progressive)이면 음성 용량을 따로 더하지 않음
        has_audio = v.get("acodec") not in (None, "none")
        size = (v_size + (0 if has_audio else (a_size or 0))) if v_size else None
        name = QUALITY_NAMES.get(h, "")
        options.append(QualityOption(
            key=str(h),
            label=f"{h}p" + (f" ({name})" if name else ""),
            size_bytes=size,
            codec=_codec_name(v.get("vcodec")),
            fps=int(v["fps"]) if v.get("fps") else None,
            fmt=v["format_id"] if (has_audio or not audio)
            else f'{v["format_id"]}+{audio["format_id"]}',
        ))
    if audio:
        options.append(QualityOption(AUDIO_MP3, "음원만 (MP3)", a_size, "MP3", None,
                                     fmt=audio["format_id"]))
    return options


def format_selector(key: str, prefer_h264: bool = True) -> str:
    if key == AUDIO_MP3:
        return "bestaudio[ext=m4a]/bestaudio"
    h = int(key)
    exact = f"[height={h}]"
    parts = []
    if prefer_h264:
        parts.append(f"bv*{exact}[vcodec^=avc1]+ba[ext=m4a]")
    parts += [
        f"bv*{exact}+ba[ext=m4a]",
        f"bv*{exact}+ba",
        f"b{exact}",
        f"bv*[height<={h}]+ba/b[height<={h}]",  # 최후 안전망
    ]
    return "/".join(parts)


def build_opts(key: str, out_dir: str, prefer_h264: bool = True,
               progress_hook=None, pp_hook=None, fmt: str = "") -> dict:
    opts = _base_opts()
    suffix = "" if key == AUDIO_MP3 else f" [{key}p]"
    selector = format_selector(key, prefer_h264)
    opts.update({
        # 목록에서 고른 정확한 포맷 → 만료 등으로 없으면 같은 화질 규칙으로 대체
        "format": f"{fmt}/{selector}" if fmt else selector,
        "outtmpl": os.path.join(out_dir, f"%(title).150B{suffix}.%(ext)s"),
        "windowsfilenames": True,
        "overwrites": False,
        "continuedl": True,
        "retries": 10,
        "fragment_retries": 10,
    })
    # 파일명에 & % ^ ! 가 있으면 윈도우 .bat(캡컷 편집기 연결)이 깨진다 → 안전 문자로
    opts["postprocessors"] = [{
        "key": "MetadataParser", "when": "pre_process",
        "actions": [(MetadataParserPP.Actions.REPLACE, "title", r"[&%^!]", "_")],
    }]
    if key == AUDIO_MP3:
        opts["postprocessors"].append({
            "key": "FFmpegExtractAudio", "preferredcodec": "mp3", "preferredquality": "192",
        })
    else:
        opts["merge_output_format"] = "mp4"
    if progress_hook:
        opts["progress_hooks"] = [progress_hook]
    if pp_hook:
        opts["postprocessor_hooks"] = [pp_hook]
    return opts


def download(url: str, key: str, out_dir: str, prefer_h264: bool = True,
             progress_hook=None, pp_hook=None, fmt: str = "") -> str | None:
    """다운로드 후 최종 파일 경로를 돌려준다."""
    os.makedirs(out_dir, exist_ok=True)
    opts = build_opts(key, out_dir, prefer_h264, progress_hook, pp_hook, fmt)
    with yt_dlp.YoutubeDL(opts) as ydl:
        info = ydl.extract_info(url, download=True)
        for d in info.get("requested_downloads") or []:
            if d.get("filepath"):
                return d["filepath"]
        return ydl.prepare_filename(info)

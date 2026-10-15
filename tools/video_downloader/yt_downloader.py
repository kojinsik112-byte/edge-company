"""엣지컴퍼니 유튜브 영상 추출기.

사용법
  GUI : python yt_downloader.py
  CLI : python yt_downloader.py <유튜브주소> [--quality 1080|720|480|mp3] [--out 폴더] [--edit]
        python yt_downloader.py <유튜브주소> --list      (화질 목록만 보기)
"""
from __future__ import annotations

import argparse
import os
import queue
import subprocess
import sys
import threading

import capcut_bridge
import yt_core

DEFAULT_OUT = os.path.join(os.path.expanduser("~"), "Downloads", "유튜브추출")
UPDATE_HINT = ("※ 유튜브가 구조를 바꾸면 이런 오류가 납니다. 창을 닫고 '업데이트.bat'을 "
               "실행한 뒤 다시 시도하세요. (비공개·연령제한 영상은 받을 수 없습니다)")


# ───────────────────────── CLI ─────────────────────────
def run_cli(args) -> int:
    print(f"영상 정보 읽는 중... {args.url}")
    info = yt_core.fetch_info(args.url)
    opts = yt_core.list_qualities(info, prefer_h264=not args.any_codec)
    print(f"\n제목: {info.get('title')}  ({info.get('duration_string', '')})\n")
    for o in opts:
        print(f"  [{o.key:>9}]  {o.display()}")
    if args.list:
        return 0

    want = args.quality.lower().rstrip("p")
    key = yt_core.AUDIO_MP3 if want in ("mp3", "audio") else want
    keys = [o.key for o in opts]
    if key not in keys:
        # 요청 화질이 없으면 그 이하 최고 화질로
        lower = [k for k in keys if k.isdigit() and int(k) <= int(want)] if want.isdigit() else []
        if not lower:
            print(f"\n[오류] {args.quality} 화질이 없습니다. 위 목록에서 고르세요.")
            return 1
        print(f"\n{want}p가 없어 {lower[0]}p로 받습니다.")
        key = lower[0]

    def hook(d):
        if d["status"] == "downloading":
            total = d.get("total_bytes") or d.get("total_bytes_estimate") or 0
            done = d.get("downloaded_bytes", 0)
            pct = done / total * 100 if total else 0
            sys.stdout.write(f"\r  다운로드 {pct:5.1f}%  {yt_core.human_size(done)} / "
                             f"{yt_core.human_size(total)}   ")
            sys.stdout.flush()
        elif d["status"] == "finished":
            print()

    fmt = next(o.fmt for o in opts if o.key == key)
    path = yt_core.download(args.url, key, args.out, not args.any_codec, hook, fmt=fmt)
    print(f"\n완료: {path}")
    if args.edit or args.full_edit:
        mode = "full" if args.full_edit else "repurpose"
        print(f"\n캡컷 AI 편집기로 전송: {capcut_bridge.MODES[mode]}")
        try:
            capcut_bridge.send_to_capcut(path, mode, wait=os.name != "nt")
        except (capcut_bridge.CapcutNotReady, FileNotFoundError) as e:
            print(f"[캡컷 연결 실패] {e}")
            return 1
    return 0


# ───────────────────────── GUI ─────────────────────────
def run_gui() -> None:
    import tkinter as tk
    from tkinter import filedialog, messagebox, ttk

    root = tk.Tk()
    root.title("엣지컴퍼니 유튜브 영상 추출기")
    root.geometry("660x660")
    root.minsize(580, 620)

    events: queue.Queue = queue.Queue()
    state = {"info": None, "options": [], "busy": False, "last_file": None}

    font = ("맑은 고딕", 10) if os.name == "nt" else None
    style = ttk.Style()
    if font:
        style.configure(".", font=font)
    style.configure("Big.TButton", padding=8)

    pad = {"padx": 12, "pady": 6}

    # 1) 주소 입력
    f_url = ttk.LabelFrame(root, text=" ① 유튜브 주소 ")
    f_url.pack(fill="x", **pad)
    url_var = tk.StringVar()
    url_entry = ttk.Entry(f_url, textvariable=url_var)
    url_entry.pack(side="left", fill="x", expand=True, padx=8, pady=8)
    btn_fetch = ttk.Button(f_url, text="화질 조회")
    btn_fetch.pack(side="right", padx=8, pady=8)

    def paste_clipboard(_e=None):
        try:
            clip = root.clipboard_get().strip()
            if "youtu" in clip and not url_var.get():
                url_var.set(clip)
        except tk.TclError:
            pass
    root.after(200, paste_clipboard)

    title_var = tk.StringVar(value="주소를 붙여넣고 [화질 조회]를 누르세요.")
    ttk.Label(root, textvariable=title_var, wraplength=600, foreground="#444").pack(
        fill="x", padx=16)

    # 2) 화질 선택
    f_q = ttk.LabelFrame(root, text=" ② 화질 선택 ")
    f_q.pack(fill="both", expand=True, **pad)
    q_list = tk.Listbox(f_q, height=8, activestyle="none", exportselection=False,
                        font=font)
    q_list.pack(fill="both", expand=True, padx=8, pady=(8, 4))
    h264_var = tk.BooleanVar(value=True)
    ttk.Checkbutton(
        f_q, variable=h264_var,
        text="편집·호환 우선 (H.264 MP4 — 캡컷·윈도우 플레이어에서 바로 재생)",
    ).pack(anchor="w", padx=8, pady=(0, 8))

    # 3) 저장 위치
    f_out = ttk.LabelFrame(root, text=" ③ 저장 폴더 ")
    f_out.pack(fill="x", **pad)
    out_var = tk.StringVar(value=DEFAULT_OUT)
    ttk.Entry(f_out, textvariable=out_var).pack(side="left", fill="x", expand=True,
                                                padx=8, pady=8)

    def choose_dir():
        d = filedialog.askdirectory(initialdir=out_var.get() or os.path.expanduser("~"))
        if d:
            out_var.set(d)
    ttk.Button(f_out, text="변경", command=choose_dir).pack(side="right", padx=8)

    # 4) 캡컷 AI 편집기 연결
    f_cc = ttk.LabelFrame(root, text=" ④ 캡컷 AI 편집 연결 ")
    f_cc.pack(fill="x", **pad)
    auto_edit_var = tk.BooleanVar(value=False)
    ttk.Checkbutton(f_cc, variable=auto_edit_var,
                    text="다운로드 끝나면 캡컷 AI 편집기로 바로 보내기").pack(
        anchor="w", padx=8, pady=(6, 2))
    mode_var = tk.StringVar(value="repurpose")
    for k, label in capcut_bridge.MODES.items():
        ttk.Radiobutton(f_cc, text=label, value=k, variable=mode_var).pack(
            anchor="w", padx=28)
    ttk.Label(f_cc, foreground="#666",
              text="결과: 바탕화면\\캡컷_완성본\\(영상제목)\\  숏츠·자막·썸네일·업로드정보").pack(
        anchor="w", padx=8, pady=(2, 6))

    # 5) 실행·진행
    f_run = ttk.Frame(root)
    f_run.pack(fill="x", **pad)
    btn_dl = ttk.Button(f_run, text="⬇  다운로드", style="Big.TButton", state="disabled")
    btn_dl.pack(side="left")
    btn_open = ttk.Button(f_run, text="폴더 열기", state="disabled")
    btn_open.pack(side="left", padx=8)
    btn_cc = ttk.Button(f_run, text="🎬 캡컷 편집 보내기", state="disabled")
    btn_cc.pack(side="left")
    progress = ttk.Progressbar(root, maximum=100)
    progress.pack(fill="x", padx=12)
    status_var = tk.StringVar(value="대기 중")
    ttk.Label(root, textvariable=status_var).pack(anchor="w", padx=14, pady=(4, 10))

    def set_busy(b: bool):
        state["busy"] = b
        btn_fetch.config(state="disabled" if b else "normal")
        btn_dl.config(state="disabled" if b or not state["options"] else "normal")

    def refresh_options():
        if not state["info"]:
            return
        state["options"] = yt_core.list_qualities(state["info"], h264_var.get())
        q_list.delete(0, "end")
        for o in state["options"]:
            q_list.insert("end", "  " + o.display())
        # 기본 선택: 1080p 있으면 1080p, 없으면 최고 화질
        idx = next((i for i, o in enumerate(state["options"]) if o.key == "1080"), 0)
        q_list.selection_set(idx)
        q_list.see(idx)
    h264_var.trace_add("write", lambda *_: refresh_options())

    # ── 작업 스레드 ──
    def fetch_worker(url):
        try:
            events.put(("info", yt_core.fetch_info(url)))
        except Exception as e:  # noqa: BLE001
            events.put(("error", f"영상 정보를 못 읽었습니다.\n\n{e}\n\n{UPDATE_HINT}"))

    def on_fetch(_e=None):
        url = url_var.get().strip()
        if not url:
            messagebox.showinfo("안내", "유튜브 주소를 입력하세요.")
            return
        set_busy(True)
        state["info"], state["options"] = None, []
        q_list.delete(0, "end")
        title_var.set("영상 정보 읽는 중...")
        status_var.set("조회 중")
        progress.config(mode="indeterminate")
        progress.start(12)
        threading.Thread(target=fetch_worker, args=(url,), daemon=True).start()

    def download_worker(url, key, out_dir, prefer_h264, fmt):
        stage = {"n": 0}

        def hook(d):
            if d["status"] == "downloading":
                total = d.get("total_bytes") or d.get("total_bytes_estimate") or 0
                done = d.get("downloaded_bytes", 0)
                events.put(("progress", (done, total, d.get("speed"), stage["n"])))
            elif d["status"] == "finished":
                stage["n"] += 1

        def pp_hook(d):
            if d["status"] == "started":
                msg = {"Merger": "영상+음성 합치는 중... (잠시만요)",
                       "ExtractAudio": "MP3로 변환 중..."}.get(d.get("postprocessor"))
                if msg:
                    events.put(("status", msg))

        try:
            path = yt_core.download(url, key, out_dir, prefer_h264, hook, pp_hook, fmt)
            events.put(("done", path))
        except Exception as e:  # noqa: BLE001
            events.put(("error", f"다운로드 실패\n\n{e}\n\n{UPDATE_HINT}"))

    def on_download():
        sel = q_list.curselection()
        if not sel:
            messagebox.showinfo("안내", "화질을 선택하세요.")
            return
        opt = state["options"][sel[0]]
        set_busy(True)
        progress.config(mode="determinate", value=0)
        status_var.set(f"{opt.label} 다운로드 시작...")
        threading.Thread(
            target=download_worker,
            args=(url_var.get().strip(), opt.key, out_var.get().strip() or DEFAULT_OUT,
                  h264_var.get(), opt.fmt),
            daemon=True,
        ).start()

    def send_capcut():
        target = state["last_file"]
        if not target:
            return
        try:
            capcut_bridge.send_to_capcut(target, mode_var.get())
            status_var.set("🎬 캡컷 AI 편집기 실행됨 — 새로 뜬 검은 창에서 진행 (닫지 마세요)")
        except (capcut_bridge.CapcutNotReady, FileNotFoundError) as e:
            messagebox.showwarning("캡컷 연결", str(e))

    def open_folder():
        target = state["last_file"]
        folder = out_var.get()
        if os.name == "nt":
            if target and os.path.exists(target):
                subprocess.Popen(["explorer", "/select,", os.path.normpath(target)])
            else:
                os.startfile(folder)  # type: ignore[attr-defined]
        elif sys.platform == "darwin":
            subprocess.Popen(["open", folder])
        else:
            subprocess.Popen(["xdg-open", folder])

    # ── 메인 스레드 이벤트 펌프 ──
    def pump():
        try:
            while True:
                kind, data = events.get_nowait()
                if kind == "info":
                    progress.stop()
                    progress.config(mode="determinate", value=0)
                    state["info"] = data
                    dur = data.get("duration_string") or ""
                    title_var.set(f"🎬 {data.get('title')}   ({dur}) — {data.get('uploader', '')}")
                    refresh_options()
                    status_var.set(f"화질 {len(state['options'])}개 확인. 고르고 [다운로드]")
                    set_busy(False)
                elif kind == "progress":
                    done, total, speed, n = data
                    pct = done / total * 100 if total else 0
                    progress.config(value=pct)
                    part = "영상" if n == 0 else "음성"
                    spd = f" · {yt_core.human_size(speed)}/s" if speed else ""
                    status_var.set(f"{part} 받는 중 {pct:.0f}%  "
                                   f"({yt_core.human_size(done)} / {yt_core.human_size(total)}){spd}")
                elif kind == "status":
                    status_var.set(data)
                elif kind == "done":
                    progress.config(value=100)
                    state["last_file"] = data
                    status_var.set(f"✅ 완료: {os.path.basename(data or '')}")
                    btn_open.config(state="normal")
                    is_video = not str(data or "").lower().endswith((".mp3", ".m4a"))
                    btn_cc.config(state="normal" if is_video else "disabled")
                    set_busy(False)
                    if auto_edit_var.get() and is_video:
                        send_capcut()
                elif kind == "error":
                    progress.stop()
                    progress.config(mode="determinate", value=0)
                    status_var.set("오류")
                    set_busy(False)
                    messagebox.showerror("오류", data)
        except queue.Empty:
            pass
        root.after(100, pump)

    btn_fetch.config(command=on_fetch)
    btn_dl.config(command=on_download)
    btn_open.config(command=open_folder)
    btn_cc.config(command=send_capcut)
    url_entry.bind("<Return>", on_fetch)
    q_list.bind("<Double-Button-1>", lambda _e: on_download() if not state["busy"] else None)
    url_entry.focus_set()
    pump()
    root.mainloop()


def main() -> int:
    p = argparse.ArgumentParser(description="엣지컴퍼니 유튜브 영상 추출기")
    p.add_argument("url", nargs="?", help="유튜브 주소 (없으면 창 모드)")
    p.add_argument("-q", "--quality", default="1080", help="1080 / 720 / 480 / mp3 ...")
    p.add_argument("-o", "--out", default=DEFAULT_OUT, help="저장 폴더")
    p.add_argument("--list", action="store_true", help="화질 목록만 출력")
    p.add_argument("--any-codec", action="store_true",
                   help="H.264 우선 끄기 (VP9/AV1 허용, 1440p·4K는 자동 허용)")
    p.add_argument("--edit", action="store_true",
                   help="받은 뒤 캡컷 AI 편집기로 재가공 (숏츠·자막·썸네일·업로드정보)")
    p.add_argument("--full-edit", action="store_true",
                   help="--edit 와 함께: 무음·추임새 컷까지 하는 풀 편집 (촬영 원본용)")
    args = p.parse_args()
    if args.url:
        return run_cli(args)
    run_gui()
    return 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
엣지컴퍼니 인스타 성장 매크로 (완전자동 + 안전가드 내장)
=========================================================
- 기술: playwright(실제 크롬). 모바일 API 흉내보다 챌린지·밴 위험 낮음.
- 안전: 일일/시간 한도 · 30~50초 랜덤간격 · 워밍업 · 문구 비반복 로테이션
        · 활동시간대 제한 · 휴먼라이크 타이핑/스크롤 · 상태영속(중복방지).
- 검증: 기본 --dry-run. 실제 발행 전 "무슨 글에 무슨 댓글 달지" 로그로 먼저 확인.

⚠️ 비공식 자동화는 인스타 ToS 위반입니다. 2.5만 계정 보호를 위해 한도를 절대 넘기지 마세요.
   계정 비밀번호는 코드/깃에 저장하지 않습니다. 최초 1회 브라우저에서 직접 로그인 →
   세션이 .browser_profile/ 에 저장되어 재사용됩니다(gitignore).

설치:
   pip install playwright
   playwright install chromium

사용:
   python insta_macro.py --login                  # 1회: 브라우저 열고 직접 로그인
   python insta_macro.py --dry-run                # 검증: 실제 발행 없이 계획만 출력
   python insta_macro.py --run                     # 실발행 (한도 내 자동)
   python insta_macro.py --run --max-comments 30   # 옵션 덮어쓰기
   python insta_macro.py --status                  # 오늘 활동량 확인
"""
import argparse
import json
import os
import random
import sys
import time
from datetime import datetime, date
from pathlib import Path

# 윈도우 콘솔(cp949)에서 이모지 출력 시 크래시 방지 → stdout/stderr UTF-8 강제
for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

HERE = Path(__file__).resolve().parent
POOL_PATH = HERE / "comment_pool.json"
STATE_PATH = HERE / "state.json"
PROFILE_DIR = HERE / ".browser_profile"
LOG_DIR = HERE / "logs"
LOG_DIR.mkdir(exist_ok=True)

# ---------------------------------------------------------------- 유틸·로그
def log(msg, tag="INFO"):
    line = f"[{datetime.now().strftime('%H:%M:%S')}] {tag:4} {msg}"
    print(line, flush=True)
    with open(LOG_DIR / f"{date.today().isoformat()}.log", "a", encoding="utf-8") as f:
        f.write(line + "\n")

def load_json(path, default):
    if Path(path).exists():
        try:
            return json.loads(Path(path).read_text(encoding="utf-8"))
        except Exception as e:
            log(f"{path} 읽기 실패: {e}", "WARN")
    return default

def save_json(path, data):
    Path(path).write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

# ---------------------------------------------------------------- 상태(영속)
def fresh_state():
    return {
        "first_run_date": date.today().isoformat(),
        "day": date.today().isoformat(),
        "comments": 0, "follows": 0, "likes": 0,
        "comment_hour_bucket": "", "comment_in_hour": 0,
        "used_comments": [],          # 오늘 쓴 댓글(반복금지)
        "seen_posts": [],             # 처리한 게시물 shortcode(중복금지, 최근 600개 유지)
        "last_action_ts": 0,
    }

def load_state():
    st = load_json(STATE_PATH, None)
    if st is None:
        st = fresh_state()
        save_json(STATE_PATH, st)
        return st
    # 날짜 바뀌면 일일 카운터 리셋(누적 이력은 유지)
    if st.get("day") != date.today().isoformat():
        st["day"] = date.today().isoformat()
        st["comments"] = st["follows"] = st["likes"] = 0
        st["comment_in_hour"] = 0
        st["comment_hour_bucket"] = ""
        st["used_comments"] = []
        save_json(STATE_PATH, st)
    return st

# ---------------------------------------------------------------- 안전 한도
def warmup_factor(state):
    """설치 후 경과일 기반. 첫 주는 한도의 40%→100%로 점증."""
    try:
        d0 = datetime.fromisoformat(state["first_run_date"]).date()
    except Exception:
        return 1.0
    days = (date.today() - d0).days
    if days >= 7:
        return 1.0
    base = 0.40
    return round(base + (1.0 - base) * (days / 7.0), 2)

def within_active_hours(cfg):
    h = datetime.now().hour
    return cfg["active_hour_start"] <= h < cfg["active_hour_end"]

def can_comment(state, limits, factor):
    daily_cap = int(limits["comments_per_day"] * factor)
    if state["comments"] >= daily_cap:
        return False, f"오늘 댓글 한도 도달({state['comments']}/{daily_cap}, warmup×{factor})"
    bucket = datetime.now().strftime("%Y%m%d%H")
    in_hour = state["comment_in_hour"] if state["comment_hour_bucket"] == bucket else 0
    if in_hour >= limits["comments_per_hour"]:
        return False, f"시간당 댓글 한도 도달({in_hour}/{limits['comments_per_hour']})"
    return True, ""

def can_follow(state, limits, factor):
    cap = int(limits["follows_per_day"] * factor)
    return state["follows"] < cap, f"맞팔 {state['follows']}/{cap}"

# ---------------------------------------------------------------- 댓글 선택
def pick_comment(pool, state, post_tags):
    """태그 가중치로 카테고리 고르고, 오늘 안 쓴 문구를 선택."""
    cats = pool["categories"]
    weights = dict(pool["tag_weights"]["_default"])
    for t in post_tags:
        if t in pool["tag_weights"]:
            for k, v in pool["tag_weights"][t].items():
                weights[k] = weights.get(k, 0) + v
    cat_names = [c for c in weights if c in cats]
    cat_w = [weights[c] for c in cat_names]
    used = set(state["used_comments"])
    for _ in range(40):
        cat = random.choices(cat_names, weights=cat_w, k=1)[0]
        candidates = [c for c in cats[cat] if c not in used]
        if candidates:
            return random.choice(candidates)
    # 다 썼으면(드묾) generic에서 아무거나
    return random.choice(cats["generic"])

# ---------------------------------------------------------------- 휴먼라이크 대기
def human_delay(limits, state, long_chance=0.18):
    base = random.uniform(limits["min_delay_sec"], limits["max_delay_sec"])
    if random.random() < long_chance:
        base += random.uniform(60, 240)   # 가끔 긴 휴식
    base += random.uniform(-3, 6)
    base = max(8, base)
    log(f"... {base:.0f}초 대기(사람처럼)", "WAIT")
    time.sleep(base)

# ---------------------------------------------------------------- 셀렉터(한/영 폴백)
SEL = {
    "like":   ['svg[aria-label="좋아요"]', 'svg[aria-label="Like"]'],
    "unlike": ['svg[aria-label="좋아요 취소"]', 'svg[aria-label="Unlike"]'],
    "comment_box": ['textarea[aria-label="댓글 달기..."]', 'textarea[aria-label="Add a comment…"]',
                    'textarea[placeholder*="댓글"]', 'textarea[placeholder*="comment"]'],
    "post_btn": ['게시', 'Post'],
    "follow_btn": ['팔로우', 'Follow'],
    "close_btn": ['svg[aria-label="닫기"]', 'svg[aria-label="Close"]'],
}

# ---------------------------------------------------------------- 핵심 액션
def type_like_human(locator, text):
    for ch in text:
        locator.type(ch, delay=random.uniform(40, 140))

def process_post(page, link, pool, state, cfg, limits, factor, dry):
    """게시물 모달 열어 좋아요+댓글(+맞팔) 수행. 반환: 'done'|'skip'|'stop'"""
    shortcode = link.rstrip("/").split("/")[-1]
    if shortcode in set(state["seen_posts"]):
        return "skip"

    ok, why = can_comment(state, limits, factor)
    if not ok:
        log(why, "STOP"); return "stop"

    # 태그 힌트(가중 댓글용): 현재 사냥 중인 해시태그
    post_tags = cfg.get("_current_tags", [])
    comment = pick_comment(pool, state, post_tags)

    log(f"게시물 {shortcode} → 댓글 예정: \"{comment}\"", "PLAN")

    if dry:
        # 검증모드: 실제 클릭/타이핑/발행 안 함. 계획만 기록하고 카운터만 모의 증가.
        state["seen_posts"].append(shortcode)
        state["used_comments"].append(comment)
        state["comments"] += 1
        return "done"

    try:
        page.goto(f"https://www.instagram.com{link}", wait_until="domcontentloaded", timeout=30000)
        time.sleep(random.uniform(2, 4))

        # 좋아요 (이미 눌렀으면 패스)
        if limits.get("do_like", True):
            liked = False
            for s in SEL["unlike"]:
                if page.locator(s).count() > 0:
                    liked = True; break
            if not liked:
                for s in SEL["like"]:
                    el = page.locator(s).first
                    if el.count() > 0:
                        el.click(timeout=5000)
                        state["likes"] += 1
                        time.sleep(random.uniform(1, 2.5))
                        break

        # 댓글
        box = None
        for s in SEL["comment_box"]:
            if page.locator(s).count() > 0:
                box = page.locator(s).first; break
        if box is None:
            log(f"{shortcode}: 댓글창 못 찾음(셀렉터 확인 필요). skip", "WARN")
            state["seen_posts"].append(shortcode)
            return "skip"
        box.click(); time.sleep(random.uniform(0.5, 1.2))
        type_like_human(box, comment)
        time.sleep(random.uniform(0.6, 1.5))
        posted = False
        for label in SEL["post_btn"]:
            btn = page.get_by_role("button", name=label)
            if btn.count() > 0:
                btn.first.click(timeout=5000); posted = True; break
        if not posted:
            box.press("Enter")
        time.sleep(random.uniform(1.5, 3))

        state["comments"] += 1
        bucket = datetime.now().strftime("%Y%m%d%H")
        if state["comment_hour_bucket"] != bucket:
            state["comment_hour_bucket"] = bucket; state["comment_in_hour"] = 0
        state["comment_in_hour"] += 1
        state["used_comments"].append(comment)
        state["seen_posts"].append(shortcode)
        log(f"{shortcode}: 댓글 완료 ✓ (오늘 {state['comments']})", "OK")

        # 맞팔(확률적 + 한도 내)
        if limits.get("do_follow", True) and random.random() < cfg["follow_probability"]:
            okf, whyf = can_follow(state, limits, factor)
            if okf:
                for label in SEL["follow_btn"]:
                    fb = page.get_by_role("button", name=label, exact=True)
                    if fb.count() > 0:
                        fb.first.click(timeout=5000)
                        state["follows"] += 1
                        log(f"{shortcode}: 맞팔 완료 ✓ (오늘 {state['follows']})", "OK")
                        time.sleep(random.uniform(1, 2))
                        break
        return "done"
    except Exception as e:
        log(f"{shortcode}: 처리 중 오류 {e}", "WARN")
        state["seen_posts"].append(shortcode)
        return "skip"
    finally:
        # seen_posts 최근 600개만 유지
        if len(state["seen_posts"]) > 600:
            state["seen_posts"] = state["seen_posts"][-600:]
        save_json(STATE_PATH, state)

def collect_recent_links(page, hashtag, want=40):
    """해시태그 페이지에서 '최근' 게시물 링크 수집(인기글은 댓글 폭주라 회피)."""
    page.goto(f"https://www.instagram.com/explore/tags/{hashtag}/",
              wait_until="domcontentloaded", timeout=30000)
    time.sleep(random.uniform(3, 5))
    links = set()
    for _ in range(6):
        hrefs = page.eval_on_selector_all(
            'a[href*="/p/"], a[href*="/reel/"]',
            "els => els.map(e => new URL(e.href).pathname)")
        for h in hrefs:
            if "/p/" in h or "/reel/" in h:
                links.add(h)
        if len(links) >= want:
            break
        page.mouse.wheel(0, random.randint(1200, 2200))
        time.sleep(random.uniform(1.5, 3))
    return list(links)[:want]

# ---------------------------------------------------------------- 실행 흐름
def run(args):
    pool = load_json(POOL_PATH, None)
    if pool is None:
        log("comment_pool.json 없음. 중단", "STOP"); sys.exit(1)
    state = load_state()
    cfg = {
        "active_hour_start": 9, "active_hour_end": 24,
        "follow_probability": 0.5,   # 댓글 단 글의 50%만 맞팔(자연스럽게)
    }
    limits = dict(pool["safety_limits"])
    if args.max_comments: limits["comments_per_day"] = args.max_comments
    limits["do_like"] = not args.no_like
    limits["do_follow"] = not args.no_follow

    dry = not args.run   # --run 없으면 무조건 dry
    factor = warmup_factor(state)
    mode = "🟢 실발행" if args.run else "🟡 검증(dry-run)"
    log(f"=== 인스타 매크로 시작 [{mode}] warmup×{factor} ===")
    log(f"오늘: 댓글 {state['comments']} · 맞팔 {state['follows']} · 좋아요 {state['likes']}")

    if args.run and not within_active_hours(cfg):
        log(f"활동시간({cfg['active_hour_start']}~{cfg['active_hour_end']}시) 외. 안전상 중단.", "STOP")
        return

    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        ctx = p.chromium.launch_persistent_context(
            user_data_dir=str(PROFILE_DIR),
            headless=False,                    # 사람처럼: 실제 창
            viewport={"width": 1280, "height": 900},
            locale="ko-KR",
            args=["--disable-blink-features=AutomationControlled"],
        )
        page = ctx.pages[0] if ctx.pages else ctx.new_page()

        # 로그인 확인
        page.goto("https://www.instagram.com/", wait_until="domcontentloaded", timeout=30000)
        time.sleep(3)
        if "accounts/login" in page.url or page.get_by_role("button", name="로그인").count() > 0:
            log("로그인 세션 없음. `python insta_macro.py --login` 으로 먼저 로그인하세요.", "STOP")
            ctx.close(); return

        targets = pool["target_hashtags"]["A_active"][:]
        random.shuffle(targets)
        done_this_run = 0
        for tag in targets:
            ok, why = can_comment(state, limits, factor)
            if not ok:
                log(why, "STOP"); break
            cfg["_current_tags"] = [tag]
            log(f"🔎 #{tag} 최근글 수집 중...")
            try:
                links = collect_recent_links(page, tag, want=30)
            except Exception as e:
                log(f"#{tag} 수집 실패: {e}", "WARN"); continue
            log(f"#{tag}: {len(links)}개 후보")
            for link in links:
                ok, why = can_comment(state, limits, factor)
                if not ok:
                    log(why, "STOP"); break
                r = process_post(page, link, pool, state, cfg, limits, factor, dry)
                if r == "stop": break
                if r == "done":
                    done_this_run += 1
                    if not dry:
                        human_delay(limits, state)
                    else:
                        time.sleep(0.05)
            ok, _ = can_comment(state, limits, factor)
            if not ok: break

        save_json(STATE_PATH, state)
        log(f"=== 종료: 이번 실행 {done_this_run}건 처리 | 오늘 누적 댓글 {state['comments']} 맞팔 {state['follows']} ===")
        if dry:
            log("검증 완료. 계획이 마음에 들면 `python insta_macro.py --run` 으로 실발행하세요.", "HINT")
        if not args.run:
            time.sleep(2)
        ctx.close()

def do_login():
    from playwright.sync_api import sync_playwright
    log("브라우저를 엽니다. 인스타에 직접 로그인하세요(비번은 저장 안 됨). 끝나면 이 창에서 Enter.")
    with sync_playwright() as p:
        ctx = p.chromium.launch_persistent_context(
            user_data_dir=str(PROFILE_DIR), headless=False, locale="ko-KR",
            viewport={"width": 1280, "height": 900},
            args=["--disable-blink-features=AutomationControlled"])
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        page.goto("https://www.instagram.com/accounts/login/")
        try:
            input("로그인 완료 후 Enter를 누르세요... ")
        except EOFError:
            time.sleep(120)
        ctx.close()
        log("세션 저장 완료(.browser_profile/). 이제 --dry-run 으로 검증하세요.", "OK")

def show_status():
    st = load_state()
    pool = load_json(POOL_PATH, {"safety_limits": {}})
    lim = pool.get("safety_limits", {})
    f = warmup_factor(st)
    print(f"""
[오늘 활동]  {st['day']}   (워밍업 계수 ×{f})
  댓글  {st['comments']:>3} / {int(lim.get('comments_per_day',30)*f)}
  맞팔  {st['follows']:>3} / {int(lim.get('follows_per_day',100)*f)}
  좋아요 {st['likes']:>3} / {lim.get('likes_per_day','-')}
  처리 게시물 누적: {len(st['seen_posts'])}개 기억(중복방지)
  최초 실행일: {st['first_run_date']}
""")

def main():
    ap = argparse.ArgumentParser(description="엣지컴퍼니 인스타 성장 매크로(안전가드 내장)")
    ap.add_argument("--login", action="store_true", help="브라우저 열어 1회 직접 로그인")
    ap.add_argument("--dry-run", action="store_true", help="검증: 실발행 없이 계획만 출력(기본)")
    ap.add_argument("--run", action="store_true", help="실제 발행(한도 내 자동)")
    ap.add_argument("--status", action="store_true", help="오늘 활동량 확인")
    ap.add_argument("--max-comments", type=int, default=0, help="오늘 댓글 상한 덮어쓰기")
    ap.add_argument("--no-like", action="store_true", help="좋아요 끄기")
    ap.add_argument("--no-follow", action="store_true", help="맞팔 끄기")
    args = ap.parse_args()

    if args.login:   do_login();  return
    if args.status:  show_status(); return
    run(args)   # --run 없으면 자동으로 dry-run

if __name__ == "__main__":
    main()

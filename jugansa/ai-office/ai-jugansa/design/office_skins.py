# 사무실 스킨 — 벽 · 바닥 · 조명 · 장식 재질 묶음 (office_html.py 가 고름)
OFFICE_SKINS = {
    "월넛라운지": dict(
        name="기본 배경 1", desc="따뜻한 월넛 패널 · 황동 장식 · 헤링본 오크 바닥 · 노란 간접조명",
        bg="#ece4d6", ceil="#3a281d", wall="#5e3d2a", wall2="#4f3222", wall_line="#7a5236", trim="#c9a45c",
        side="#4a2f20", side2="#3a2418", side_kind="panel", floor_kind="herring", floor="#c8925e", floor2="#b37d4c", floor_line="#9c6a3e",
        light="#ffd8a0", light_op=0.55, sconce="#ffe3b0", plaque="#1b2433", plaque_text="#fbf3e2", header="#1b2433", header2="#2a3550",
        board="#121a2a", board_frame="#c9a45c", rug_mix=0.55, glass=False, night=False),
    "마블펜트하우스": dict(
        name="기본 배경 2", desc="흰 대리석 벽 · 검은 철제 라인 · 통유리 창(낮 도시) · 밝은 대리석 바닥",
        bg="#eef0f2", ceil="#d9dde2", wall="#f3f0ea", wall2="#e6e1d8", wall_line="#cfc8bc", trim="#2a2d33",
        side="#bcd6ea", side2="#9cc2e0", side_kind="window_day", floor_kind="marble", floor="#e8e5df", floor2="#dcd8d0", floor_line="#c9c4ba",
        light="#ffffff", light_op=0.65, sconce="#ffffff", plaque="#2a2d33", plaque_text="#ffffff", header="#2a2d33", header2="#3a3f48",
        board="#16191f", board_frame="#2a2d33", rug_mix=0.7, glass=True, night=False),
    "나이트스카이": dict(
        name="기본 배경 3", desc="짙은 남색 벽 · 금색 핀스트라이프 · 통유리 야경 · 반짝이는 검은 돌 바닥 · 팀 색 무드등",
        bg="#0f1420", ceil="#0b0f18", wall="#1c2436", wall2="#161d2c", wall_line="#c9a45c", trim="#c9a45c",
        side="#0e1a33", side2="#0a1226", side_kind="window_night", floor_kind="stone", floor="#262c38", floor2="#1e2430", floor_line="#343b4a",
        light="#9fc4ff", light_op=0.35, sconce="#ffd8a0", plaque="#0b0f18", plaque_text="#ffe7a6", header="#0b0f18", header2="#141b2a",
        board="#0a0e16", board_frame="#c9a45c", rug_mix=0.35, glass=True, night=True),
    "써니호선실": dict(
        name="원피스", desc="원피스 배 안 선실 — 나무 판자 벽 · 갑판 바닥 · 둥근 현창(바다) · 천장 들보 · 랜턴 · 밧줄 · 술통 · 해적 깃발",
        bg="#9fd0e6", ceil="#5a3a22", wall="#a87644", wall2="#8a5c32", wall_line="#6e4626", trim="#6a4426",
        side="#8a5c32", side2="#6e4626", side_kind="hull", wall_kind="plank", floor_kind="deck", floor="#c8945a", floor2="#b8844c", floor_line="#7a5030",
        light="#ffd08a", light_op=0.5, sconce="#ffc86a", plaque="#3a2416", plaque_text="#ffe7b0", header="#3a2416", header2="#5a3a22",
        board="#16201c", board_frame="#8a5a30", rug_mix=0.55, glass=False, night=False, theme="ship", accent="#e8c27a"),
    "어벤져스본부": dict(
        name="어벤져스 사무실", desc="어벤져스 사무실 — 짙은 강철 패널 · 파란 LED 라인 · 육각 바닥 · 야경 통유리 + 홀로그램 · A 엠블럼",
        bg="#0b1018", ceil="#121822", wall="#252d3a", wall2="#1b222d", wall_line="#3aa8ff", trim="#6a7484",
        side="#0e1a33", side2="#0a1226", side_kind="window_night", wall_kind="steel", floor_kind="hex", floor="#262d38", floor2="#20262f", floor_line="#3a4454",
        light="#7ac8ff", light_op=0.32, sconce="#8ad8ff", plaque="#0e141e", plaque_text="#cfe8ff", header="#0e141e", header2="#1a2232",
        board="#0a0f18", board_frame="#3a8ad8", rug_mix=0.3, glass=True, night=True, theme="avengers", accent="#3aa8ff"),
}

# 부르는 이름 (본부장 10-31: 기존 3종 = 기본 배경 1 · 2 · 3 / 새 2종 = 원피스 · 어벤져스 사무실)
ALIAS = {"기본배경1": "월넛라운지", "기본배경2": "마블펜트하우스", "기본배경3": "나이트스카이", "원피스": "써니호선실", "어벤져스사무실": "어벤져스본부"}

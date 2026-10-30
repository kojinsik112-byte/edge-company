# 사무실 스킨 — 벽 · 바닥 · 조명 · 장식 재질 묶음 (office_html.py 가 고름)
OFFICE_SKINS = {
    "월넛라운지": dict(
        name="월넛 라운지", desc="따뜻한 월넛 패널 · 황동 장식 · 헤링본 오크 바닥 · 노란 간접조명",
        bg="#ece4d6", ceil="#3a281d", wall="#5e3d2a", wall2="#4f3222", wall_line="#7a5236", trim="#c9a45c",
        side="#4a2f20", side2="#3a2418", side_kind="panel", floor_kind="herring", floor="#c8925e", floor2="#b37d4c", floor_line="#9c6a3e",
        light="#ffd8a0", light_op=0.55, sconce="#ffe3b0", plaque="#1b2433", plaque_text="#fbf3e2", header="#1b2433", header2="#2a3550",
        board="#121a2a", board_frame="#c9a45c", rug_mix=0.55, glass=False, night=False),
    "마블펜트하우스": dict(
        name="마블 펜트하우스", desc="흰 대리석 벽 · 검은 철제 라인 · 통유리 창(낮 도시) · 밝은 대리석 바닥",
        bg="#eef0f2", ceil="#d9dde2", wall="#f3f0ea", wall2="#e6e1d8", wall_line="#cfc8bc", trim="#2a2d33",
        side="#bcd6ea", side2="#9cc2e0", side_kind="window_day", floor_kind="marble", floor="#e8e5df", floor2="#dcd8d0", floor_line="#c9c4ba",
        light="#ffffff", light_op=0.65, sconce="#ffffff", plaque="#2a2d33", plaque_text="#ffffff", header="#2a2d33", header2="#3a3f48",
        board="#16191f", board_frame="#2a2d33", rug_mix=0.7, glass=True, night=False),
    "나이트스카이": dict(
        name="나이트 스카이라운지", desc="짙은 남색 벽 · 금색 핀스트라이프 · 통유리 야경 · 반짝이는 검은 돌 바닥 · 팀 색 무드등",
        bg="#0f1420", ceil="#0b0f18", wall="#1c2436", wall2="#161d2c", wall_line="#c9a45c", trim="#c9a45c",
        side="#0e1a33", side2="#0a1226", side_kind="window_night", floor_kind="stone", floor="#262c38", floor2="#1e2430", floor_line="#343b4a",
        light="#9fc4ff", light_op=0.35, sconce="#ffd8a0", plaque="#0b0f18", plaque_text="#ffe7a6", header="#0b0f18", header2="#141b2a",
        board="#0a0e16", board_frame="#c9a45c", rug_mix=0.35, glass=True, night=True),
}

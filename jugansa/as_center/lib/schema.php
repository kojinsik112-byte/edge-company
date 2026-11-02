<?php
// 표 만들기(가비아 = MySQL · 내 PC 시험 = SQLite). 시각은 모두 유닉스 초.
function schema_sql($type) {
  $id = $type === 'sqlite' ? 'INTEGER PRIMARY KEY AUTOINCREMENT' : 'INT UNSIGNED AUTO_INCREMENT PRIMARY KEY';
  $end = $type === 'sqlite' ? '' : ' ENGINE=InnoDB DEFAULT CHARSET=utf8mb4';
  $t = [
    "CREATE TABLE danji (id $id, code VARCHAR(16) NOT NULL UNIQUE, name VARCHAR(100) NOT NULL, active INT NOT NULL DEFAULT 1, purge_date VARCHAR(10) NULL, keep_text VARCHAR(100) NULL, intake VARCHAR(10) NOT NULL DEFAULT 'vendor', created BIGINT NOT NULL DEFAULT 0)$end",
    "CREATE TABLE vendor (id $id, danji_id INT NOT NULL, item VARCHAR(50) NOT NULL, company VARCHAR(100) NOT NULL, tag VARCHAR(100) NULL, person VARCHAR(50) NULL, phone VARCHAR(20) NOT NULL, show_phone VARCHAR(20) NULL, active INT NOT NULL DEFAULT 1, sort INT NOT NULL DEFAULT 0)$end",
    "CREATE TABLE ticket (id $id, danji_id INT NOT NULL, no VARCHAR(20) NOT NULL UNIQUE, dong VARCHAR(10) NOT NULL, ho VARCHAR(10) NOT NULL, name VARCHAR(50) NOT NULL, phone VARCHAR(20) NOT NULL, tel4 VARCHAR(4) NOT NULL,
      cat VARCHAR(40) NOT NULL, is_build INT NOT NULL DEFAULT 0, item VARCHAR(60) NOT NULL, vendor_id INT NULL, vc VARCHAR(60) NULL, body TEXT NOT NULL, slot VARCHAR(200) NULL,
      st INT NOT NULL DEFAULT 0, created BIGINT NOT NULL, va BIGINT NULL, r_at BIGINT NULL, r_by VARCHAR(10) NULL, v_at BIGINT NULL, visit VARCHAR(60) NULL, d_at BIGINT NULL,
      confirm INT NULL, rating INT NULL, c_at BIGINT NULL, hc_at BIGINT NULL, vd BIGINT NULL, ro BIGINT NULL, rw VARCHAR(300) NULL, reopen INT NOT NULL DEFAULT 0, ph INT NOT NULL DEFAULT 0, phd INT NOT NULL DEFAULT 0,
      hist TEXT NULL, late_key VARCHAR(40) NULL, remind_key VARCHAR(40) NULL, vtoken VARCHAR(32) NOT NULL, rtoken VARCHAR(32) NOT NULL, ip VARCHAR(45) NULL, purged INT NOT NULL DEFAULT 0)$end",
    "CREATE INDEX ix_ticket_dj ON ticket (danji_id, st)",
    "CREATE INDEX ix_ticket_dh ON ticket (danji_id, dong, ho, tel4)",
    "CREATE INDEX ix_ticket_vt ON ticket (vtoken)",
    "CREATE INDEX ix_ticket_rt ON ticket (rtoken)",
    "CREATE TABLE photo (id $id, ticket_id INT NOT NULL, kind VARCHAR(8) NOT NULL, file VARCHAR(80) NOT NULL, size INT NOT NULL DEFAULT 0, created BIGINT NOT NULL)$end",
    "CREATE INDEX ix_photo_t ON photo (ticket_id, kind)",
    "CREATE TABLE log (id $id, ticket_id INT NOT NULL, at BIGINT NOT NULL, who VARCHAR(60) NOT NULL, what VARCHAR(500) NOT NULL, rev INT NOT NULL DEFAULT 0)$end",
    "CREATE INDEX ix_log_t ON log (ticket_id)",
    "CREATE TABLE sms_log (id $id, ticket_id INT NULL, at BIGINT NOT NULL, phone VARCHAR(20) NOT NULL, kind VARCHAR(20) NOT NULL, msg TEXT NOT NULL, ok INT NOT NULL DEFAULT 0, resp VARCHAR(300) NULL)$end",
    "CREATE INDEX ix_sms_t ON sms_log (ticket_id)",
    "CREATE TABLE admin (id $id, login VARCHAR(40) NOT NULL UNIQUE, pass VARCHAR(255) NOT NULL, name VARCHAR(50) NOT NULL, phone VARCHAR(20) NULL, notify INT NOT NULL DEFAULT 1, active INT NOT NULL DEFAULT 1, created BIGINT NOT NULL)$end",
    "CREATE TABLE access_log (id $id, admin_id INT NOT NULL, at BIGINT NOT NULL, ip VARCHAR(45) NULL, act VARCHAR(40) NOT NULL, target VARCHAR(100) NULL)$end",
    "CREATE TABLE holiday (d VARCHAR(10) PRIMARY KEY, name VARCHAR(40) NULL)$end",
    "CREATE TABLE hit (id $id, ip VARCHAR(45) NOT NULL, kind VARCHAR(20) NOT NULL, at BIGINT NOT NULL)$end",
    "CREATE INDEX ix_hit ON hit (ip, kind, at)",
    "CREATE TABLE meta (k VARCHAR(40) PRIMARY KEY, v TEXT NULL)$end",
    // 업체 모집 · 심사: 단지별 모집 공고 · 신청 업체 · 올린 서류 · 처리 이력
    "CREATE TABLE recruit (id $id, danji_id INT NOT NULL UNIQUE, code VARCHAR(16) NOT NULL UNIQUE, open INT NOT NULL DEFAULT 0, deadline VARCHAR(16) NULL, items TEXT NULL, intro TEXT NULL, terms TEXT NULL, created BIGINT NOT NULL)$end",
    "CREATE TABLE applicant (id $id, danji_id INT NOT NULL, no VARCHAR(20) NOT NULL UNIQUE, item VARCHAR(50) NOT NULL, company VARCHAR(100) NOT NULL, biz_no VARCHAR(20) NOT NULL, ceo VARCHAR(50) NOT NULL,
      addr VARCHAR(200) NULL, person VARCHAR(50) NULL, phone VARCHAR(20) NOT NULL, email VARCHAR(100) NULL, tag VARCHAR(100) NULL, intro TEXT NULL,
      stage INT NOT NULL DEFAULT 0, checks TEXT NULL, scores TEXT NULL, score INT NULL, memo TEXT NULL, reason VARCHAR(300) NULL, hist TEXT NULL,
      token VARCHAR(32) NOT NULL, agree_at BIGINT NULL, gk_at BIGINT NULL, gk_ip VARCHAR(45) NULL, gk_ua VARCHAR(200) NULL, gk_ok BIGINT NULL, vendor_id INT NULL, created BIGINT NOT NULL, ip VARCHAR(45) NULL)$end",
    "CREATE INDEX ix_app_dj ON applicant (danji_id, stage)",
    "CREATE INDEX ix_app_tok ON applicant (token)",
    "CREATE TABLE rc_file (id $id, applicant_id INT NOT NULL, kind VARCHAR(10) NOT NULL, file VARCHAR(80) NOT NULL, orig VARCHAR(120) NULL, size INT NOT NULL DEFAULT 0, created BIGINT NOT NULL)$end",
    "CREATE INDEX ix_rcf_a ON rc_file (applicant_id, kind)",
    "CREATE TABLE rc_log (id $id, applicant_id INT NOT NULL, at BIGINT NOT NULL, who VARCHAR(60) NOT NULL, what VARCHAR(500) NOT NULL)$end",
    "CREATE INDEX ix_rcl_a ON rc_log (applicant_id)",
  ];
  return $t;
}
// 공휴일 기본값(대체공휴일 · 2026.06.03 지방선거 포함). 관리 페이지 '설정'에서 고칠 수 있음.
function default_holidays() {
  return [
    '2026-01-01' => '신정', '2026-02-16' => '설날 연휴', '2026-02-17' => '설날', '2026-02-18' => '설날 연휴', '2026-03-02' => '삼일절 대체', '2026-05-05' => '어린이날',
    '2026-05-25' => '부처님오신날 대체', '2026-06-03' => '지방선거', '2026-08-17' => '광복절 대체', '2026-09-24' => '추석 연휴', '2026-09-25' => '추석', '2026-09-28' => '추석 대체',
    '2026-10-05' => '개천절 대체', '2026-10-09' => '한글날', '2026-12-25' => '성탄절', '2027-01-01' => '신정', '2027-02-08' => '설날 연휴', '2027-02-09' => '설날 대체',
    '2027-03-01' => '삼일절', '2027-05-05' => '어린이날', '2027-05-13' => '부처님오신날', '2027-08-16' => '광복절 대체', '2027-09-14' => '추석 연휴', '2027-09-15' => '추석',
    '2027-09-16' => '추석 연휴', '2027-10-04' => '개천절 대체', '2027-10-11' => '한글날 대체', '2027-12-27' => '성탄절 대체',
  ];
}

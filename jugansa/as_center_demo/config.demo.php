<?php
// 시험판(내 PC · 127.0.0.1:8091) 설정 — 실제 운영 설정 아님. 시험판 폴더의 app/config.php로 복사됨
return [
  'base_url' => 'http://127.0.0.1:8091',
  'brand'   => '엣지컴퍼니',
  'company' => '㈜엣지컴퍼니',
  'contact_email' => 'edgecompany1@naver.com',
  'callcenter' => '',
  'privacy_officer' => ['name' => '(시험판)', 'title' => '', 'phone' => '', 'email' => 'edgecompany1@naver.com'],
  'db' => ['type' => 'sqlite', 'path' => __DIR__ . '/data/as.sqlite'],
  // 시험판은 문자를 실제로 보내지 않고 '문자 기록'에만 남김
  'sms' => ['mode' => 'off', 'sms_id' => '', 'api_key' => '', 'callback' => '', 'subject' => '엣지컴퍼니 A/S'],
  'cron_key' => '',
  'install_key' => '',
  // 시연 중 같은 PC(127.0.0.1)에서 여러 번 접수해도 막히지 않게
  'limits' => ['per_phone_day' => 50, 'per_ip_day' => 300],
  // 시연용 관리자(시험판에서만 쓰는 값 · seed_demo.php가 만들고 demo.php가 보여 줌)
  // 본부장 11-02: 시험판 관리자 = admin / admin(실제 서버는 install.php에서 10자 이상 비밀번호로 따로 만듦)
  'demo_admin' => ['login' => 'admin', 'pw' => 'admin', 'name' => '주관사 담당(시연)', 'phone' => '01000009999'],
];

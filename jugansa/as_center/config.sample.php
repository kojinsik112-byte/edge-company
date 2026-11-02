<?php
// 이 파일을 config.php로 복사한 뒤 값을 채웁니다. config.php에는 비밀값이 들어가므로 깃에 올리지 않습니다.
return [
  // 접수창 주소(끝에 / 없이). 비워 두면 접속한 주소를 그대로 씁니다.
  'base_url' => '',

  'brand'   => '엣지컴퍼니',
  'company' => '㈜엣지컴퍼니',
  'contact_email' => 'edgecompany1@naver.com',
  // 콜센터 번호가 정해지면 넣습니다. 비우면 화면에 '단지 협약 뒤 안내'로 나옵니다.
  'callcenter' => '',

  // 개인정보 처리방침에 나오는 보호책임자(꼭 채워야 함)
  'privacy_officer' => ['name' => '', 'title' => '', 'phone' => '', 'email' => 'edgecompany1@naver.com'],

  // 가비아 웹호스팅 = mysql. 가비아 호스팅 관리 화면의 DB 이름 · 아이디 · 비밀번호를 넣습니다.
  'db' => ['type' => 'mysql', 'host' => 'localhost', 'name' => '', 'user' => '', 'pass' => ''],
  // 내 PC 시험용: 'db' => ['type' => 'sqlite', 'path' => __DIR__ . '/data/as.sqlite'],

  // 문자: mode 'off' = 실제로 보내지 않고 관리 페이지 '문자 기록'에만 남김 / 'gabia' = 가비아 문자 API로 발송
  // sms_id · api_key = sms.gabia.com 관리자 → 서비스 정보 → API 인증키 정보
  // callback = 가비아에 등록한 발신번호(사전 등록한 번호만 보낼 수 있음)
  'sms' => ['mode' => 'off', 'sms_id' => '', 'api_key' => '', 'callback' => '', 'subject' => '엣지컴퍼니 A/S'],

  // 바깥 크론(정해진 시각마다 주소를 불러 주는 서비스)을 쓸 때만: cron.php?key=이 값
  // 비워 두면 cron.php는 막히고, 접수창 · 관리 페이지가 열릴 때마다 10분 간격으로 기한 점검이 돕니다.
  'cron_key' => '',

  // 설치 열쇠: 아무 글자나 정해 넣고, install.php 화면에 같은 글자를 넣어야 설치됩니다(남이 먼저 설치하는 것을 막음)
  'install_key' => '',

  // 같은 연락처 · 같은 인터넷 주소에서 하루에 받을 수 있는 접수 수(장난 접수 막기)
  'limits' => ['per_phone_day' => 5, 'per_ip_day' => 20],
];

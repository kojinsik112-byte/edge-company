<?php
// 처음 한 번: 표 만들기 · 공휴일 · 첫 관리자 계정 · data 폴더 막기. 설치가 끝나면 다시 열려도 아무것도 하지 않음.
require __DIR__ . '/lib/boot.php';
require __DIR__ . '/lib/schema.php';
header('X-Frame-Options: DENY');
$msg = ''; $done = false;
$checks = [
  ['PHP 7.4 이상', version_compare(PHP_VERSION, '7.4.0', '>='), PHP_VERSION],
  ['DB 연결 도구(PDO ' . db_type() . ')', in_array(db_type() === 'sqlite' ? 'sqlite' : 'mysql', PDO::getAvailableDrivers(), true), implode(', ', PDO::getAvailableDrivers())],
  ['바깥 연결(curl · 문자 발송)', function_exists('curl_init'), ''],
  ['사진 줄이기(GD)', function_exists('imagecreatefromstring'), '없어도 동작'],
  ['보안 연결(https)', is_https(), '가비아에서 SSL을 켠 뒤 이 주소를 https로 열어 주세요'],
];
if (installed()) {
  $done = true; $msg = '이미 설치되어 있습니다. 보안을 위해 이 파일(install.php)을 서버에서 지워 주세요.';
} elseif (($_SERVER['REQUEST_METHOD'] ?? '') === 'POST') {
  $key = (string)cfg('install_key', '');
  $login = trim((string)($_POST['login'] ?? '')); $name = trim((string)($_POST['name'] ?? '')); $phone = digits($_POST['phone'] ?? '');
  $pw = (string)($_POST['pw'] ?? ''); $pw2 = (string)($_POST['pw2'] ?? '');
  if ($key === '' ) $msg = 'config.php의 install_key에 아무 글자나 먼저 넣어 주세요.';
  elseif (!hash_equals($key, (string)($_POST['key'] ?? ''))) $msg = '설치 열쇠가 config.php의 install_key와 다릅니다.';
  elseif (!preg_match('/^[A-Za-z0-9_.-]{3,40}$/', $login)) $msg = '아이디는 영문 · 숫자 3자 이상으로 적어 주세요.';
  elseif ($name === '') $msg = '이름을 적어 주세요.';
  elseif ($phone !== '' && !preg_match('/^01[016789]\d{7,8}$/', $phone)) $msg = '휴대폰 번호를 다시 확인해 주세요.';
  elseif (mb_strlen($pw) < 10) $msg = '비밀번호는 10자 이상으로 정해 주세요.';
  elseif ($pw !== $pw2) $msg = '비밀번호 두 칸이 서로 다릅니다.';
  else {
    try {
      foreach (schema_sql(db_type()) as $sql) db()->exec($sql);
      foreach (default_holidays() as $d => $n) ins('holiday', ['d' => $d, 'name' => $n]);
      ins('admin', ['login' => $login, 'pass' => password_hash($pw, PASSWORD_DEFAULT), 'name' => $name, 'phone' => $phone, 'notify' => 1, 'active' => 1, 'created' => time()]);
      if (!is_dir(DATA . '/photos')) mkdir(DATA . '/photos', 0700, true);
      file_put_contents(DATA . '/.htaccess', "<IfModule mod_authz_core.c>\nRequire all denied\n</IfModule>\n<IfModule !mod_authz_core.c>\nOrder allow,deny\nDeny from all\n</IfModule>\n");
      file_put_contents(DATA . '/index.html', '');
      file_put_contents(DATA . '/probe.txt', 'data-folder-open');
      meta_set('installed', date('Y-m-d H:i'));
      $done = true; $msg = '설치를 마쳤습니다. 이제 이 파일(install.php)을 서버에서 지우고 관리 페이지로 들어가세요.';
    } catch (Exception $e) { $msg = '설치 중 오류: ' . $e->getMessage(); }
  }
}
?><!doctype html>
<html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>설치 · 엣지컴퍼니 A/S 도움 창구</title><meta name="robots" content="noindex">
<link rel="stylesheet" href="assets/app.css?v=1"><link rel="stylesheet" href="assets/admin.css?v=1">
</head><body>
<header class="hd"><div class="wrap"><div class="top" style="border-bottom:0"><div class="logo"><span class="mark">E</span><span class="wm"><b>엣지컴퍼니</b><span>A/S 도움 창구 · 처음 설치</span></span></div></div></div></header>
<div class="wrap"><main>
  <div class="sec" style="max-width:620px">
    <div class="h2"><span class="k">점검</span><b>서버 상태</b></div>
    <div class="chk"><?php foreach ($checks as $c): ?><span><?= h($c[0]) ?></span><span class="<?= $c[1] ? 'y' : 'n' ?>"><?= $c[1] ? '됨' : '안 됨' ?><?= $c[2] !== '' ? ' · ' . h($c[2]) : '' ?></span><?php endforeach; ?></div>
  </div>
  <?php if ($msg): ?><div class="note <?= $done ? 'ok' : 'warn' ?>" style="max-width:620px"><?= h($msg) ?></div><?php endif; ?>
  <?php if ($done): ?>
    <div class="btnrow"><a class="btn" href="admin.php" style="text-decoration:none">관리 페이지로</a></div>
  <?php else: ?>
  <form method="post" class="sec" style="max-width:620px;margin-top:14px" autocomplete="off">
    <div class="h2"><span class="k">계정</span><b>첫 관리자 만들기</b></div>
    <label class="f">설치 열쇠(config.php의 install_key와 같은 글자)<input name="key" type="password"></label>
    <div class="row" style="margin-top:10px"><label class="f">아이디<input name="login" value="<?= h($_POST['login'] ?? '') ?>"></label><label class="f">이름<input name="name" value="<?= h($_POST['name'] ?? '') ?>"></label></div>
    <label class="f" style="margin-top:10px">휴대폰(새 요청 알림 문자 받을 번호)<input name="phone" inputmode="tel" value="<?= h($_POST['phone'] ?? '') ?>"></label>
    <div class="row" style="margin-top:10px"><label class="f">비밀번호(10자 이상)<input name="pw" type="password"></label><label class="f">비밀번호 한 번 더<input name="pw2" type="password"></label></div>
    <div class="btnrow"><button class="btn" type="submit">설치하기</button></div>
  </form>
  <?php endif; ?>
</main></div>
</body></html>

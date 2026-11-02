<?php
// 주관사 관리 API: 로그인 세션(2시간 안 쓰면 끝남) · 보안 확인값(CSRF) · 접속 기록(개인정보를 본 기록)
function adm_session() {
  if (session_status() !== PHP_SESSION_ACTIVE) {
    session_name('ascadm');
    session_set_cookie_params(['lifetime' => 0, 'path' => '/', 'secure' => is_https(), 'httponly' => true, 'samesite' => 'Strict']);
    session_start();
  }
  if (!empty($_SESSION['adm']) && time() - (int)($_SESSION['seen'] ?? 0) > 7200) $_SESSION = [];
  if (!empty($_SESSION['adm'])) $_SESSION['seen'] = time();
}
function alog($act, $target = '') { ins('access_log', ['admin_id' => (int)$_SESSION['adm'], 'at' => time(), 'ip' => ip(), 'act' => $act, 'target' => mb_substr((string)$target, 0, 100)]); }
function me() { return one('SELECT * FROM admin WHERE id=?', [(int)$_SESSION['adm']]); }

function admin_route($a) {
  adm_session();
  if ($a === 'login') a_login();
  if ($a === 'me') out(['ok' => true, 'in' => !empty($_SESSION['adm']), 'name' => $_SESSION['name'] ?? '', 'csrf' => $_SESSION['csrf'] ?? '']);
  if (empty($_SESSION['adm'])) fail('로그인이 필요합니다.', 401);
  if (($_SERVER['REQUEST_METHOD'] ?? '') === 'POST' && !hash_equals((string)($_SESSION['csrf'] ?? ''), (string)($_SERVER['HTTP_X_CSRF'] ?? ''))) fail('화면을 새로 고쳐 주세요(보안 확인 실패).', 403);
  switch ($a) {
    case 'logout': $_SESSION = []; session_destroy(); out(['ok' => true]);
    case 'adm_list': a_list(); break;
    case 'adm_get': a_get(); break;
    case 'adm_act': a_act(); break;
    case 'adm_danji': a_danji_list(); break;
    case 'adm_danji_save': a_danji_save(); break;
    case 'adm_vendor_save': a_vendor_save(); break;
    case 'adm_sms': a_sms_log(); break;
    case 'adm_export': a_export(); break;
    case 'adm_settings': a_settings(); break;
    case 'adm_holidays_save': a_holidays_save(); break;
    case 'adm_admin_save': a_admin_save(); break;
    case 'adm_pw': a_pw(); break;
    case 'adm_sms_test': a_sms_test(); break;
  }
  fail('잘못된 요청입니다.', 404);
}

function a_login() {
  if (($_SERVER['REQUEST_METHOD'] ?? '') !== 'POST') fail('잘못된 요청입니다.', 405);
  $n = (int)one('SELECT COUNT(*) c FROM hit WHERE ip=? AND kind=? AND at>?', [ip(), 'login_fail', time() - 600])['c'];
  if ($n >= 5) fail('비밀번호를 여러 번 틀렸습니다. 10분 뒤 다시 해 주세요.', 429);
  $u = one('SELECT * FROM admin WHERE login=? AND active=1', [str_in($_POST['login'] ?? '', 40)]);
  if (!$u || !password_verify((string)($_POST['pw'] ?? ''), $u['pass'])) { ins('hit', ['ip' => ip(), 'kind' => 'login_fail', 'at' => time()]); fail('아이디나 비밀번호가 맞지 않습니다.', 401); }
  session_regenerate_id(true);
  $_SESSION['adm'] = (int)$u['id']; $_SESSION['name'] = $u['name']; $_SESSION['csrf'] = bin2hex(random_bytes(16)); $_SESSION['seen'] = time();
  alog('login');
  out(['ok' => true, 'name' => $u['name'], 'csrf' => $_SESSION['csrf']]);
}

// 요청 목록 + 단지 · 업체(점수표용)
function a_list() {
  $dj = (int)($_GET['danji'] ?? 0);
  $rows = all(T_SEL . ' WHERE t.purged=0' . ($dj ? ' AND t.danji_id=?' : '') . ' ORDER BY t.id DESC LIMIT 2000', $dj ? [$dj] : []);
  $list = []; foreach ($rows as $t) { $o = t_pub($t, 'adm', true); unset($o['tel']); $list[] = $o; }
  $vend = all('SELECT id, danji_id, item, company FROM vendor' . ($dj ? ' WHERE danji_id=?' : '') . ' ORDER BY danji_id, sort, id', $dj ? [$dj] : []);
  out(['ok' => true, 'list' => $list, 'vendors' => $vend, 'danji' => all('SELECT id, name, code, active FROM danji ORDER BY active DESC, id DESC'), 'now' => time() * 1000]);
}
function adm_detail($t) {
  $o = t_pub($t, 'adm');
  $o['log'] = array_map(function ($l) { return ['at' => ms($l['at']), 'who' => $l['who'], 'what' => $l['what'], 'rev' => (int)$l['rev']]; }, all('SELECT * FROM log WHERE ticket_id=? ORDER BY id DESC', [$t['id']]));
  $o['sms'] = array_map(function ($s) { return ['at' => ms($s['at']), 'to' => $s['phone'], 'kind' => $s['kind'], 'msg' => $s['msg'], 'ok' => (int)$s['ok'], 'resp' => $s['resp']]; }, all('SELECT * FROM sms_log WHERE ticket_id=? ORDER BY id DESC', [$t['id']]));
  $o['vendors'] = all('SELECT id, item, company FROM vendor WHERE danji_id=? AND active=1 ORDER BY sort, id', [$t['danji_id']]);
  return $o;
}
function a_get() {
  $t = t_get('t.id=? AND t.purged=0', [(int)($_GET['id'] ?? 0)]);
  if (!$t) fail('요청을 찾지 못했습니다.', 404);
  alog('view', $t['no']);
  out(['ok' => true, 't' => adm_detail($t)]);
}

// 주관사 처리: 업체 지정 · 바꾸기 / 직접 연락 / 방문 일정 / 시공사 처리 확인 / 처리 완료 / 메모 / 되돌리기 / 업체 링크 다시 보내기
function a_act() {
  if (($_SERVER['REQUEST_METHOD'] ?? '') !== 'POST') fail('잘못된 요청입니다.', 405);
  $t = t_get('t.id=? AND t.purged=0', [(int)($_POST['id'] ?? 0)]);
  if (!$t) fail('요청을 찾지 못했습니다.', 404);
  $act = (string)($_POST['act'] ?? ''); $st = (int)$t['st']; $now = time(); $who = '주관사 ' . ($_SESSION['name'] ?? '');
  if ($act === 'vend') {
    if ($t['is_build'] || $st === 3) fail('이 요청은 업체를 바꿀 수 없습니다.');
    $v = one('SELECT * FROM vendor WHERE id=? AND danji_id=? AND active=1', [(int)($_POST['vendor_id'] ?? 0), $t['danji_id']]);
    if (!$v) fail('업체를 골라 주세요.');
    if ((int)$t['vendor_id'] === (int)$v['id']) fail('지금과 같은 업체입니다.');
    $was = t_known($t) ? ['co' => $t['vend'], 'phone' => $t['vphone']] : null;
    // 새 업체 기준으로 1차 회신부터 다시(기한도 지금부터) · 이전 업체 링크는 닫음
    snap($t, '주관사', $was ? '업체 바꾸기' : '업체 지정');
    $t['item'] = $v['item']; $t['vendor_id'] = (int)$v['id']; $t['va'] = $now; $t['st'] = 0; $t['r_at'] = null; $t['r_by'] = null; $t['v_at'] = null; $t['visit'] = null;
    t_save($t); upd('ticket', $t['id'], ['vtoken' => rnd(24)]);
    tlog($t['id'], $who, ($was ? '업체 바꿈: ' . $was['co'] . ' → ' : '업체 지정: ') . $v['company']);
    n_assign(t_reload($t), $was ? $was['phone'] : null);
  } elseif ($act === 'reply' && $st === 0) {
    snap($t, '주관사', $t['is_build'] ? '시공사에 전달함' : '주관사 직접 연락'); $t['st'] = 1; $t['r_at'] = $now; $t['r_by'] = '주관사'; t_save($t);
    tlog($t['id'], $who, $t['is_build'] ? '시공사 하자 창구에 전달 · 입주민 연락' : '주관사가 입주민에게 직접 연락');
  } elseif ($act === 'visit' && $st <= 1 && need_visit($t)) {
    $w = str_in($_POST['when'] ?? '', 60); if ($w === '') fail('방문 날짜 · 시간을 적어 주세요.');
    snap($t, '주관사', '방문 일정 확정', 1); $t['st'] = 2; if (!$t['r_at']) { $t['r_at'] = $now; $t['r_by'] = '주관사'; } $t['v_at'] = $now; $t['visit'] = $w; t_save($t);
    tlog($t['id'], $who, '방문 일정 확정: ' . $w); n_visit(t_reload($t));
  } elseif ($act === 'bcheck' && $st === 1 && $t['is_build']) {
    snap($t, '주관사', '시공사 처리 확인'); $t['st'] = 2; $t['v_at'] = $now; t_save($t);
    tlog($t['id'], $who, '시공사 처리 상황 확인 · 입주민 안내');
  } elseif ($act === 'done' && $st <= 2) {
    snap($t, '주관사', '처리 완료', 1); $t['st'] = 3; if (!$t['r_at']) { $t['r_at'] = $now; $t['r_by'] = '주관사'; } $t['d_at'] = $now; t_save($t);
    tlog($t['id'], $who, '처리 완료'); n_done(t_reload($t));
  } elseif ($act === 'memo') {
    $m = str_in($_POST['memo'] ?? '', 300); if ($m === '') fail('메모를 적어 주세요.');
    tlog($t['id'], $who, '메모: ' . $m);
  } elseif ($act === 'undo') {
    $why = str_in($_POST['why'] ?? '', 200); if ($why === '') fail('되돌리는 사유를 적어 주세요(필수).');
    $s = undo($t, $who, $why);
    if (!$s) fail('되돌릴 처리가 없습니다.');
    if ($s['res'] && ($_POST['fix'] ?? '') === '1') n_fix(t_reload($t), $s['label']);
  } elseif ($act === 'resend' && t_known($t) && $st < 3) {
    n_vendor($t); tlog($t['id'], $who, '업체에 링크 문자 다시 보냄');
  } else fail('지금 단계에서는 할 수 없는 처리입니다. 화면을 새로 고쳐 주세요.');
  out(['ok' => true, 't' => adm_detail(t_reload($t))]);
}

// ---------- 단지 · 업체 ----------
function a_danji_list() {
  $dj = all('SELECT * FROM danji ORDER BY active DESC, id DESC');
  $v = all('SELECT * FROM vendor ORDER BY danji_id, sort, id');
  out(['ok' => true, 'danji' => $dj, 'vendors' => $v, 'base' => base_url()]);
}
function a_danji_save() {
  $id = (int)($_POST['id'] ?? 0); $name = str_in($_POST['name'] ?? '', 100);
  if ($name === '') fail('단지 이름을 적어 주세요.');
  $pd = (string)($_POST['purge_date'] ?? '');
  if ($pd !== '' && !preg_match('/^\d{4}-\d{2}-\d{2}$/', $pd)) fail('보유 기간 끝나는 날은 2028-12-31처럼 적어 주세요.');
  $row = ['name' => $name, 'active' => ($_POST['active'] ?? '1') === '1' ? 1 : 0, 'purge_date' => $pd ?: null, 'keep_text' => str_in($_POST['keep_text'] ?? '', 100) ?: null];
  if ($id) { upd('danji', $id, $row); alog('danji_edit', $name); }
  else { do { $code = rnd(6); } while (one('SELECT id FROM danji WHERE code=?', [$code])); $row['code'] = $code; $row['created'] = time(); $id = ins('danji', $row); alog('danji_add', $name); }
  out(['ok' => true, 'id' => $id]);
}
function a_vendor_save() {
  $id = (int)($_POST['id'] ?? 0); $dj = (int)($_POST['danji_id'] ?? 0);
  if (!one('SELECT id FROM danji WHERE id=?', [$dj])) fail('단지를 먼저 골라 주세요.');
  $row = ['danji_id' => $dj, 'item' => str_in($_POST['item'] ?? '', 50), 'company' => str_in($_POST['company'] ?? '', 100), 'tag' => str_in($_POST['tag'] ?? '', 100),
    'person' => str_in($_POST['person'] ?? '', 50), 'phone' => digits($_POST['phone'] ?? ''), 'show_phone' => digits($_POST['show_phone'] ?? '') ?: null,
    'active' => ($_POST['active'] ?? '1') === '1' ? 1 : 0, 'sort' => (int)($_POST['sort'] ?? 0)];
  if ($row['item'] === '' || $row['company'] === '') fail('품목과 업체 이름을 적어 주세요.');
  if (!preg_match('/^01[016789]\d{7,8}$/', $row['phone'])) fail('업체 담당자 휴대폰(문자 받을 번호)을 다시 확인해 주세요.');
  if ($id) { upd('vendor', $id, $row); alog('vendor_edit', $row['company']); } else { $id = ins('vendor', $row); alog('vendor_add', $row['company']); }
  out(['ok' => true, 'id' => $id]);
}

// ---------- 문자 기록 · 내보내기 ----------
function a_sms_log() {
  $rows = all('SELECT s.*, t.no FROM sms_log s LEFT JOIN ticket t ON t.id=s.ticket_id ORDER BY s.id DESC LIMIT 300');
  out(['ok' => true, 'list' => array_map(function ($s) { return ['at' => ms($s['at']), 'no' => $s['no'], 'to' => $s['phone'], 'kind' => $s['kind'], 'msg' => $s['msg'], 'ok' => (int)$s['ok'], 'resp' => $s['resp']]; }, $rows), 'mode' => (cfg('sms', [])['mode'] ?? 'off')]);
}
// 보고용 엑셀(CSV): 이름 · 연락처는 넣지 않음
function a_export() {
  $dj = (int)($_GET['danji'] ?? 0);
  $rows = all(T_SEL . ' WHERE t.purged=0' . ($dj ? ' AND t.danji_id=?' : '') . ' ORDER BY t.id', $dj ? [$dj] : []);
  alog('export', $dj ? 'danji ' . $dj : 'all');
  header('Content-Type: text/csv; charset=utf-8');
  header('Content-Disposition: attachment; filename="as_report_' . date('Ymd') . '.csv"');
  $o = fopen('php://output', 'w');
  fwrite($o, "\xEF\xBB\xBF");
  fputcsv($o, ['접수번호', '단지', '동', '호', '구분', '품목', '업체', '업체 연락', '단계', '요청 시각', '1차 연락 시각', '1차 연락 기한', '기한 안 여부', '연락한 쪽', '방문 확정 시각', '처리 완료 시각', '입주민 확인', '다시 열림']);
  foreach ($rows as $t) {
    $rd = reply_due($t);
    fputcsv($o, [$t['no'], $t['dname'], $t['dong'], $t['ho'], $t['cat'], $t['item'], t_known($t) ? $t['vend'] : ($t['is_build'] ? '시공사' : '확인 필요'), $t['vc'], stage_name($t),
      date('Y-m-d H:i', $t['created']), $t['r_at'] ? date('Y-m-d H:i', $t['r_at']) : '', date('Y-m-d H:i', $rd), $t['r_at'] ? ((int)$t['r_at'] <= $rd ? '예' : '아니요') : '', (string)$t['r_by'],
      $t['v_at'] ? date('Y-m-d H:i', $t['v_at']) : '', $t['d_at'] ? date('Y-m-d H:i', $t['d_at']) : '', $t['confirm'] === null ? '' : ((int)$t['confirm'] === 1 ? '해결 확인' : '마감'), (int)$t['reopen']]);
  }
  fclose($o);
  exit;
}

// ---------- 설정 ----------
function a_settings() {
  $c = cfg('sms', []);
  $h = all('SELECT d, name FROM holiday ORDER BY d');
  $txt = implode("\n", array_map(function ($r) { return $r['d'] . ' ' . $r['name']; }, $h));
  out(['ok' => true, 'holidays' => $txt, 'admins' => all('SELECT id, login, name, phone, notify, active FROM admin ORDER BY id'), 'me' => (int)$_SESSION['adm'],
    'sms' => ['mode' => $c['mode'] ?? 'off', 'callback' => !empty($c['callback']) ? tel_fmt($c['callback']) : '', 'keys' => !empty($c['sms_id']) && !empty($c['api_key'])],
    'server' => ['php' => PHP_VERSION, 'gd' => function_exists('imagecreatefromstring'), 'curl' => function_exists('curl_init'), 'https' => is_https(), 'addr' => $_SERVER['SERVER_ADDR'] ?? '', 'db' => db_type(), 'writable' => is_writable(DATA)]]);
}
function a_holidays_save() {
  $lines = preg_split('/\r?\n/', (string)($_POST['text'] ?? ''));
  $rows = [];
  foreach ($lines as $l) { $l = trim($l); if ($l === '') continue; if (!preg_match('/^(\d{4}-\d{2}-\d{2})\s*(.*)$/u', $l, $m)) fail('이 줄을 확인해 주세요: ' . $l); $rows[$m[1]] = mb_substr($m[2], 0, 40); }
  db()->beginTransaction(); q('DELETE FROM holiday'); foreach ($rows as $d => $n) ins('holiday', ['d' => $d, 'name' => $n]); db()->commit();
  alog('holidays', count($rows) . '일');
  out(['ok' => true, 'n' => count($rows)]);
}
function a_admin_save() {
  $id = (int)($_POST['id'] ?? 0);
  $row = ['name' => str_in($_POST['name'] ?? '', 50), 'phone' => digits($_POST['phone'] ?? ''), 'notify' => ($_POST['notify'] ?? '1') === '1' ? 1 : 0, 'active' => ($_POST['active'] ?? '1') === '1' ? 1 : 0];
  if ($row['name'] === '') fail('이름을 적어 주세요.');
  if ($row['phone'] !== '' && !preg_match('/^01[016789]\d{7,8}$/', $row['phone'])) fail('휴대폰 번호를 다시 확인해 주세요.');
  if ($id === (int)$_SESSION['adm'] && !$row['active']) fail('지금 로그인한 계정은 끌 수 없습니다.');
  if ($id) { upd('admin', $id, $row); alog('admin_edit', $row['name']); out(['ok' => true]); }
  $login = str_in($_POST['login'] ?? '', 40); $pw = (string)($_POST['pw'] ?? '');
  if (!preg_match('/^[A-Za-z0-9_.-]{3,40}$/', $login)) fail('아이디는 영문 · 숫자 3자 이상으로 적어 주세요.');
  if (mb_strlen($pw) < 10) fail('비밀번호는 10자 이상으로 정해 주세요.');
  if (one('SELECT id FROM admin WHERE login=?', [$login])) fail('이미 있는 아이디입니다.');
  $row['login'] = $login; $row['pass'] = password_hash($pw, PASSWORD_DEFAULT); $row['created'] = time();
  ins('admin', $row); alog('admin_add', $login);
  out(['ok' => true]);
}
function a_pw() {
  $u = me();
  if (!password_verify((string)($_POST['cur'] ?? ''), $u['pass'])) fail('지금 비밀번호가 맞지 않습니다.');
  $pw = (string)($_POST['pw'] ?? '');
  if (mb_strlen($pw) < 10) fail('새 비밀번호는 10자 이상으로 정해 주세요.');
  upd('admin', $u['id'], ['pass' => password_hash($pw, PASSWORD_DEFAULT)]); alog('pw');
  out(['ok' => true]);
}
function a_sms_test() {
  $u = me();
  if (empty($u['phone'])) fail('설정에서 내 휴대폰 번호를 먼저 넣어 주세요.');
  $ok = sms($u['phone'], brand() . ' A/S 접수창 문자 시험입니다. ' . date('m.d H:i'), 'test');
  $r = one('SELECT resp FROM sms_log ORDER BY id DESC LIMIT 1');
  out(['ok' => true, 'sent' => $ok, 'resp' => $r ? $r['resp'] : '']);
}

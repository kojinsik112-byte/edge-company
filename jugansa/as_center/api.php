<?php
// 접수창 API: 입주민(단지 정보 · 접수 · 진행 확인 · 해결 확인) · 업체(문자 링크 토큰) · 사진 · 주관사(로그인 세션 → lib/admin_api.php)
require __DIR__ . '/lib/boot.php';
require __DIR__ . '/lib/notify.php';
if (!installed()) fail('아직 설치 전입니다. install.php를 먼저 열어 주세요.', 503);
tick();
$a = $_GET['a'] ?? '';
switch ($a) {
  case 'danji': a_danji(); break;
  case 'submit': a_submit(); break;
  case 'lookup': a_lookup(); break;
  case 'confirm': a_confirm(); break;
  case 'photo': a_photo(); break;
  case 'v_get': a_v_get(); break;
  case 'v_act': a_v_act(); break;
}
require_once __DIR__ . '/lib/admin_api.php';
admin_route($a);

function must_post() { if (($_SERVER['REQUEST_METHOD'] ?? '') !== 'POST') fail('잘못된 요청입니다.', 405); }
function danji_by_code($c) { return one('SELECT * FROM danji WHERE code=? AND active=1', [(string)$c]); }
function req_danji() { $d = danji_by_code($_REQUEST['d'] ?? ''); if (!$d) fail('단지 링크가 맞지 않습니다. 안내문의 QR이나 링크로 다시 들어와 주세요.', 404); return $d; }

// 사진 저장: 서버에서도 긴 변 1600px JPEG로 다시 저장(사진 속 위치 정보 등 지움). GD가 없으면 받은 파일 그대로
function save_photos($tid, $kind, $field, $max) {
  if (empty($_FILES[$field]) || $max <= 0) return 0;
  $f = $_FILES[$field];
  $tmp = (array)$f['tmp_name']; $err = (array)$f['error']; $size = (array)$f['size'];
  $dir = DATA . '/photos'; if (!is_dir($dir)) mkdir($dir, 0700, true);
  $n = 0;
  foreach ($tmp as $i => $file) {
    if ($n >= $max) break;
    if ((int)$err[$i] !== UPLOAD_ERR_OK || (int)$size[$i] > 8 * 1048576 || !is_uploaded_file($file)) continue;
    $info = @getimagesize($file);
    if (!$info || !in_array($info[2], [IMAGETYPE_JPEG, IMAGETYPE_PNG, IMAGETYPE_WEBP], true)) continue;
    $name = $tid . '_' . rnd(16) . '.jpg'; $dest = $dir . '/' . $name; $ok = false;
    if (function_exists('imagecreatefromstring')) {
      $im = @imagecreatefromstring((string)file_get_contents($file));
      if ($im) {
        $w = imagesx($im); $h = imagesy($im); $s = min(1, 1600 / max($w, $h));
        if ($s < 1) { $nw = (int)round($w * $s); $nh = (int)round($h * $s); $im2 = imagecreatetruecolor($nw, $nh); imagecopyresampled($im2, $im, 0, 0, 0, 0, $nw, $nh, $w, $h); imagedestroy($im); $im = $im2; }
        $ok = imagejpeg($im, $dest, 82); imagedestroy($im);
      }
    }
    if (!$ok) $ok = move_uploaded_file($file, $dest);
    if ($ok) { ins('photo', ['ticket_id' => $tid, 'kind' => $kind, 'file' => $name, 'size' => (int)@filesize($dest), 'created' => time()]); $n++; }
  }
  return $n;
}

// ---------- 입주민 ----------
function a_danji() {
  $d = req_danji();
  $list = [];
  foreach (all('SELECT id, item, company, tag, phone, show_phone FROM vendor WHERE danji_id=? AND active=1 ORDER BY sort, id', [$d['id']]) as $v)
    $list[] = ['id' => (int)$v['id'], 'item' => $v['item'], 'co' => $v['company'], 'tag' => (string)$v['tag'], 'tel' => tel_fmt($v['show_phone'] ?: $v['phone'])];
  out(['ok' => true, 'name' => $d['name'], 'vendors' => $list, 'keep' => (string)$d['keep_text'], 'callcenter' => (string)cfg('callcenter', ''), 'email' => (string)cfg('contact_email', ''), 'company' => (string)cfg('company', '')]);
}

function a_submit() {
  must_post();
  $d = req_danji();
  if (!empty($_POST['website'])) out(['ok' => true, 't' => null]); // 자동 입력 막기(사람에겐 안 보이는 칸)
  $build = ($_POST['build'] ?? '0') === '1';
  $cat = $build ? BUILD_CAT : (in_array($_POST['cat'] ?? '', CATS, true) ? $_POST['cat'] : CATS[0]);
  $item = '—'; $vid = null; $vc = '';
  if (!$build) {
    $mode = $_POST['item_mode'] ?? '';
    if ($mode === 'list') {
      $item = str_in($_POST['item'] ?? '', 50);
      if (!(int)one('SELECT COUNT(*) c FROM vendor WHERE danji_id=? AND item=? AND active=1', [$d['id'], $item])['c']) fail('품목을 다시 골라 주세요.');
      $vs = (string)($_POST['vendor'] ?? '');
      if ($vs !== 'forgot') {
        $v = one('SELECT id FROM vendor WHERE id=? AND danji_id=? AND item=? AND active=1', [(int)$vs, $d['id'], $item]);
        if (!$v) fail("계약한 업체를 골라 주세요. 모르시면 '기억이 안 나요'를 누르세요.");
        $vid = (int)$v['id'];
      }
    } elseif ($mode === 'unknown') { $item = '잘 모르겠어요'; }
    elseif ($mode === 'free') { $item = str_in($_POST['item_free'] ?? '', 30); if ($item === '') fail('품목 이름을 적어 주세요.'); }
    else fail('품목을 골라 주세요.');
    $vc = (string)($_POST['vc'] ?? '');
    if (!in_array($vc, VC, true)) fail('업체에 연락해 보셨는지 골라 주세요.');
  }
  $body = str_in($_POST['body'] ?? '', 1000);
  if ($body === '') fail('내용을 적어 주세요.');
  $slots = array_values(array_intersect(SLOTS, (array)($_POST['slots'] ?? [])));
  $dong = clean_dh($_POST['dong'] ?? '', '동'); $ho = clean_dh($_POST['ho'] ?? '', '호');
  $name = str_in($_POST['name'] ?? '', 20); $tel = digits($_POST['tel'] ?? '');
  if ($dong === '' || $ho === '' || $name === '') fail('동 · 호수와 성함을 적어 주세요.');
  if (!preg_match('/^01[016789]\d{7,8}$/', $tel)) fail('휴대폰 번호를 다시 확인해 주세요. 010으로 시작하는 10 ~ 11자리여야 문자를 받을 수 있어요.');
  if (($_POST['a1'] ?? '') !== '1' || ($_POST['a2'] ?? '') !== '1') fail('필수 동의 2개에 체크해 주세요.');
  $lim = cfg('limits', ['per_phone_day' => 5, 'per_ip_day' => 20]);
  if ((int)one('SELECT COUNT(*) c FROM ticket WHERE phone=? AND created>?', [$tel, time() - 86400])['c'] >= (int)$lim['per_phone_day']) fail('같은 번호로 오늘 요청이 많습니다. 진행 확인에서 앞선 요청을 봐 주세요.', 429);
  if ((int)one('SELECT COUNT(*) c FROM ticket WHERE ip=? AND created>?', [ip(), time() - 86400])['c'] >= (int)$lim['per_ip_day']) fail('요청이 너무 많습니다. 잠시 뒤 다시 해 주세요.', 429);
  $now = time(); $id = 0;
  $pre = 'EC-' . date('ymd', $now) . '-';
  $base = (int)one('SELECT COUNT(*) c FROM ticket WHERE no LIKE ?', [$pre . '%'])['c'];
  for ($try = 1; $try <= 5 && !$id; $try++) {
    try {
      $id = ins('ticket', ['danji_id' => $d['id'], 'no' => $pre . sprintf('%03d', $base + $try), 'dong' => $dong, 'ho' => $ho, 'name' => $name, 'phone' => $tel, 'tel4' => substr($tel, -4),
        'cat' => $cat, 'is_build' => $build ? 1 : 0, 'item' => $item, 'vendor_id' => $vid, 'vc' => $vc, 'body' => $body, 'slot' => $slots ? implode(', ', $slots) : SLOTS[0],
        'st' => 0, 'created' => $now, 'hist' => '[]', 'vtoken' => rnd(24), 'rtoken' => rnd(24), 'ip' => ip()]);
    } catch (PDOException $e) { if ($try === 5) throw $e; }
  }
  $ph = save_photos($id, 'req', 'photos', 5);
  if ($ph) upd('ticket', $id, ['ph' => $ph]);
  $t = t_get('t.id=?', [$id]);
  tlog($id, '입주민', '주관사에 요청' . ($vc ? ' · ' . $vc : '') . ($ph ? ' · 사진 ' . $ph . '장' : ''));
  n_new($t);
  out(['ok' => true, 't' => t_pub($t, 'res')]);
}

function a_lookup() {
  must_post();
  $d = req_danji();
  $k = (string)($_POST['k'] ?? '');
  if ($k !== '') {
    $rows = all(T_SEL . ' WHERE t.danji_id=? AND t.rtoken=? AND t.purged=0', [$d['id'], $k]);
  } else {
    if (!hit_ok('lookup', 20, 600)) fail('조회가 너무 많습니다. 10분 뒤 다시 해 주세요.', 429);
    // '103-1502', '103동 1502호', '103 1502' 모두 같은 집으로
    $p = preg_split('/\s+/', trim(preg_replace('/[^0-9A-Za-z가-힣]+/u', ' ', str_replace(['동', '호'], ' ', (string)($_POST['dh'] ?? '')))));
    $tel4 = digits($_POST['tel4'] ?? '');
    if (count($p) < 2 || strlen($tel4) !== 4) fail('동 · 호수와 연락처 뒤 4자리를 넣어 주세요.');
    $rows = all(T_SEL . ' WHERE t.danji_id=? AND t.dong=? AND t.ho=? AND t.tel4=? AND t.purged=0 ORDER BY t.id DESC LIMIT 10', [$d['id'], $p[0], $p[1], $tel4]);
  }
  out(['ok' => true, 'list' => array_map(function ($t) { return t_pub($t, 'res'); }, $rows)]);
}

function a_confirm() {
  must_post();
  $d = req_danji();
  $t = t_get('t.danji_id=? AND t.rtoken=? AND t.purged=0', [$d['id'], (string)($_POST['k'] ?? '')]);
  if (!$t) fail('요청을 찾지 못했습니다.', 404);
  if ((int)$t['st'] !== 3 || $t['confirm'] !== null) fail('지금은 할 수 없는 처리입니다. 화면을 새로 고쳐 주세요.');
  if (($_POST['ok'] ?? '') === '1') {
    $rating = (int)($_POST['rating'] ?? 0); if (!t_known($t) || $rating < 1 || $rating > 3) $rating = null;
    $note = str_in($_POST['note'] ?? '', 200);
    snap($t, '입주민', '해결 확인'); $t['confirm'] = 1; $t['rating'] = $rating; $t['c_at'] = time(); t_save($t);
    tlog($t['id'], '입주민', '해결 확인' . ($rating ? ' · 업체 응대 ' . RLB[$rating] . ($rating === 1 && $note !== '' ? ' (아쉬운 점: ' . $note . ')' : '') : ''));
  } else {
    $why = str_in($_POST['why'] ?? '', 200);
    if ($why === '') fail('아직 남은 문제를 적어 주세요.');
    $now = time();
    snap($t, '입주민', '다시 요청');
    $t['st'] = 1; $t['reopen'] = (int)$t['reopen'] + 1; $t['ro'] = $now; $t['rw'] = $why; $t['vd'] = biz_due(biz_due($now, 24), 24);
    $t['v_at'] = null; $t['visit'] = null; $t['d_at'] = null; t_save($t);
    tlog($t['id'], '입주민', '아직 해결 안 됨 · 다시 열림: ' . $why);
    n_reopen(t_reload($t), $why);
  }
  out(['ok' => true, 't' => t_pub(t_reload($t), 'res')]);
}

// 사진 보기: 업체 토큰 · 입주민 토큰 · 주관사 로그인 중 하나가 맞아야
function a_photo() {
  $p = one('SELECT p.*, t.vtoken, t.rtoken FROM photo p JOIN ticket t ON t.id=p.ticket_id WHERE p.id=? AND t.purged=0', [(int)($_GET['id'] ?? 0)]);
  if (!$p) { http_response_code(404); exit; }
  $ok = (!empty($_GET['t']) && hash_equals($p['vtoken'], (string)$_GET['t'])) || (!empty($_GET['k']) && hash_equals($p['rtoken'], (string)$_GET['k']));
  if (!$ok) { require_once __DIR__ . '/lib/admin_api.php'; adm_session(); $ok = !empty($_SESSION['adm']); }
  if (!$ok) { http_response_code(403); exit; }
  $f = DATA . '/photos/' . $p['file'];
  if (!is_file($f)) { http_response_code(404); exit; }
  $info = @getimagesize($f);
  header('Content-Type: ' . ($info ? $info['mime'] : 'image/jpeg'));
  header('Cache-Control: private, max-age=3600');
  header('X-Content-Type-Options: nosniff');
  readfile($f);
  exit;
}

// ---------- 업체(문자 링크) ----------
function ven_ticket() {
  $tok = (string)($_REQUEST['t'] ?? '');
  if (strlen($tok) < 16) fail('링크가 맞지 않습니다.', 404);
  $t = t_get('t.vtoken=? AND t.purged=0', [$tok]);
  if (!$t || !t_known($t)) fail('링크가 맞지 않거나 다른 업체로 넘어간 요청입니다.', 404);
  if ($t['c_at'] && time() - (int)$t['c_at'] > 30 * 86400) fail('마감되고 30일이 지나 닫힌 링크입니다.', 410);
  return $t;
}
function a_v_get() { $t = ven_ticket(); out(['ok' => true, 't' => t_pub($t, 'ven'), 'undoMin' => 10]); }
function a_v_act() {
  must_post();
  $t = ven_ticket(); $act = (string)($_POST['act'] ?? ''); $now = time(); $st = (int)$t['st']; $who = '업체 ' . $t['vend'];
  if ($act === 'reply' && $st === 0) {
    snap($t, '업체', '연락했어요'); $t['st'] = 1; $t['r_at'] = $now; $t['r_by'] = '업체'; t_save($t);
    tlog($t['id'], $who, '고객에게 연락함(1차 회신)');
  } elseif ($act === 'visit' && $st <= 1 && need_visit($t)) {
    $w = str_in($_POST['when'] ?? '', 60); if ($w === '') fail('통화로 정한 날짜 · 시간을 적어 주세요.');
    snap($t, '업체', '방문 일정 확정', 1); $t['st'] = 2; if (!$t['r_at']) { $t['r_at'] = $now; $t['r_by'] = '업체'; } $t['v_at'] = $now; $t['visit'] = $w; t_save($t);
    tlog($t['id'], $who, '방문 일정 확정: ' . $w); n_visit(t_reload($t));
  } elseif ($act === 'done' && $st <= 2) {
    $note = str_in($_POST['note'] ?? '', 200);
    snap($t, '업체', '처리 완료', 1); $t['st'] = 3; if (!$t['r_at']) { $t['r_at'] = $now; $t['r_by'] = '업체'; } $t['d_at'] = $now;
    // 완료 사진: 되돌리기로 숨겨진 앞선 사진은 지우고, 이번 사진을 뒤에 붙임
    $keep = (int)$t['phd'];
    foreach (array_slice(all('SELECT id, file FROM photo WHERE ticket_id=? AND kind=? ORDER BY id', [$t['id'], 'done']), $keep) as $o) { @unlink(DATA . '/photos/' . $o['file']); q('DELETE FROM photo WHERE id=?', [$o['id']]); }
    $add = save_photos($t['id'], 'done', 'photos', 5);
    $t['phd'] = $keep + $add; t_save($t);
    tlog($t['id'], $who, '처리 완료' . ($note !== '' ? ' · ' . $note : '') . ($add ? ' · 완료 사진 ' . $add . '장' : ''));
    n_done(t_reload($t));
  } elseif ($act === 'undo') {
    $h = last_hist($t);
    if (!$h || $h['by'] !== '업체') fail('되돌릴 처리가 없습니다.');
    if ($now - (int)$h['at'] > 600) fail('누른 지 10분이 지났습니다. 주관사에 알려 주시면 주관사가 되돌립니다.');
    $s = undo($t, $who, '잘못 누름');
    if ($s && $s['res']) n_fix(t_reload($t), $s['label']);
  } else fail('지금 단계에서는 할 수 없는 처리입니다. 화면을 새로 고쳐 주세요.');
  out(['ok' => true, 't' => t_pub(t_reload($t), 'ven')]);
}

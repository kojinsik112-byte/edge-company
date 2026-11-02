<?php
// 업체 모집 · 심사: 단지별 모집 공고(링크 · QR) → 업체 신청 · 서류 → 서류 확인 → 세부 심사 → 입예협 선정
// → 특약이행각서 날인본 확인 → 참여 확정(A/S 창구 '품목별 업체'에 자동 등록). 날인은 업체가 직접 하고, 시스템은 도장을 만들지 않는다.

// 단계: 0 신청 접수 · 1 서류 확인 · 2 세부 심사 · 3 입예협 선정(각서 대기) · 4 참여 확정 · 9 탈락
const RC_ST = [0 => '신청 접수', 1 => '서류 확인', 2 => '세부 심사', 3 => '선정 · 각서 대기', 4 => '참여 확정', 9 => '탈락'];
// 서류: [이름, 언제 필요(apply = 신청 때 필수 · sel = 선정 뒤 필수 · opt = 선택), 최대 장수]
const RC_DOCS = [
  'biz'   => ['사업자등록증', 'apply', 1],
  'price' => ['단가표', 'apply', 3],
  'ins'   => ['보험 증권(영업배상책임 등)', 'opt', 2],
  'photo' => ['시공 사진', 'opt', 5],
  'gaksu' => ['특약이행각서(날인본)', 'sel', 3],
  'bond'  => ['업체 이행보증 증권', 'opt', 2],
];
const RC_EXT = ['pdf', 'jpg', 'jpeg', 'png', 'webp', 'xlsx', 'xls', 'hwp', 'hwpx', 'doc', 'docx'];
// 참여 조건 기본값(단지마다 모집 설정에서 고칠 수 있음)
const RC_TERMS = "계약금은 계약 금액의 10% 이하로 받습니다(세대 실측 뒤 만드는 맞춤 제작 품목 · 본사 규정 품목은 예외 — 품목과 금액을 단가표 · 계약서에 미리 표시).
카드 · 현금 결제 가격이 같습니다.
같은 모델이 인근 매장에서 더 싸면 차액의 10배를 보상합니다(1건 최대 50만원 · 주관사가 먼저 지급한 뒤 업체와 정산).
시공 품목의 무상 A/S는 최소 2년입니다(브랜드 제품은 제조사 보증).
A/S 요청은 24시간 안에 1차 회신하고, 48시간 안에 방문 일정을 확정합니다(문자로 받는 A/S 도움 창구 링크로 처리).
박람회 전에 단가표를 입주민에게 미리 공개합니다.
선정되면 특약이행각서(하자보수 · 사후관리 이행) 날인본을 내야 참여가 확정됩니다.";
// 심사 점수표 기본값(설정 → 업체 심사 점수표에서 고침) · '항목|배점'
const RC_SCORE = "가격 경쟁력(단가표)|30\n품질 · 시공 실적|25\nA/S 체계 · 회신 약속|20\n회사 안정성(업력 · 보험)|15\n지역 업체|10";

function rc_score_items() {
  $o = [];
  foreach (preg_split('/\r?\n/', (string)(meta_get('rc_score') ?: RC_SCORE)) as $l) {
    $p = explode('|', trim($l)); if (trim($p[0]) === '') continue;
    $o[] = ['name' => mb_substr(trim($p[0]), 0, 40), 'max' => max(1, (int)($p[1] ?? 10))];
  }
  return $o;
}
function rc_items($r) { $o = []; foreach (preg_split('/\r?\n/', (string)$r['items']) as $l) { $p = explode('|', trim($l)); if (trim($p[0]) !== '') $o[] = ['item' => trim($p[0]), 'n' => max(1, (int)($p[1] ?? 1))]; } return $o; }
function rc_terms($r) { return array_values(array_filter(array_map('trim', preg_split('/\r?\n/', (string)($r['terms'] ?: RC_TERMS))))); }
function rc_open($r) { return (int)$r['open'] === 1 && (!$r['deadline'] || strtotime($r['deadline']) >= time()); }
function rc_get_by_code($c) { return one('SELECT r.*, d.name dname, d.code dcode FROM recruit r JOIN danji d ON d.id=r.danji_id WHERE r.code=? AND d.active=1', [(string)$c]); }
function rc_app($where, $p) { return one('SELECT a.*, d.name dname FROM applicant a JOIN danji d ON d.id=a.danji_id WHERE ' . $where, $p); }
function rc_files($aid) { return all('SELECT id, kind, orig, size, created FROM rc_file WHERE applicant_id=? ORDER BY id', [$aid]); }
function rc_has($files, $kind) { foreach ($files as $f) if ($f['kind'] === $kind) return true; return false; }
// 신청 때 필수 서류가 다 있는지(서류 확인 단계로 넘어가는 조건)
function rc_missing($files, $stage) {
  $m = [];
  foreach (RC_DOCS as $k => $d) if (($d[1] === 'apply' || ($d[1] === 'sel' && $stage >= 3)) && !rc_has($files, $k)) $m[] = $d[0];
  return $m;
}
function rc_log($aid, $who, $what) { ins('rc_log', ['applicant_id' => $aid, 'at' => time(), 'who' => mb_substr($who, 0, 60), 'what' => mb_substr($what, 0, 500)]); }
function link_partner($a) { return base_url() . '/partner.php?t=' . $a['token']; }

// 서류 저장: 확장자 · 크기만 받고(실행 불가 · data/ 안) 원래 파일 이름은 기록만
function rc_save_files($aid, $kind, $field, $max) {
  if (empty($_FILES[$field]) || !isset(RC_DOCS[$kind])) return 0;
  $f = $_FILES[$field]; $tmp = (array)$f['tmp_name']; $err = (array)$f['error']; $size = (array)$f['size']; $name = (array)$f['name'];
  $dir = DATA . '/recruit'; if (!is_dir($dir)) mkdir($dir, 0700, true);
  $have = (int)one('SELECT COUNT(*) c FROM rc_file WHERE applicant_id=? AND kind=?', [$aid, $kind])['c']; $n = 0;
  foreach ($tmp as $i => $file) {
    if ($have + $n >= $max) break;
    if ((int)$err[$i] !== UPLOAD_ERR_OK || (int)$size[$i] > 20 * 1048576 || !is_uploaded_file($file)) continue;
    $ext = strtolower(pathinfo((string)$name[$i], PATHINFO_EXTENSION));
    if (!in_array($ext, RC_EXT, true)) continue;
    $fn = $aid . '_' . $kind . '_' . rnd(16) . '.' . $ext;
    if (!move_uploaded_file($file, $dir . '/' . $fn)) continue;
    ins('rc_file', ['applicant_id' => $aid, 'kind' => $kind, 'file' => $fn, 'orig' => mb_substr(basename((string)$name[$i]), 0, 120), 'size' => (int)$size[$i], 'created' => time()]);
    $n++;
  }
  return $n;
}
function rc_upload_err() { return '올릴 수 있는 파일은 PDF · 사진(JPG · PNG) · 엑셀 · 한글 · 워드이고, 한 파일 20MB까지입니다.'; }

// 화면으로 보낼 모양(who: pub = 업체 본인 · adm = 주관사)
function rc_pub($a, $who) {
  $files = rc_files($a['id']);
  $o = ['no' => $a['no'], 'dj' => $a['dname'], 'item' => $a['item'], 'company' => $a['company'], 'ceo' => $a['ceo'], 'bizNo' => $a['biz_no'], 'addr' => (string)$a['addr'],
    'tag' => (string)$a['tag'], 'stage' => (int)$a['stage'], 'stageName' => RC_ST[(int)$a['stage']], 'gkAt' => ms($a['gk_at']), 'gkOk' => ms($a['gk_ok']), 't' => ms($a['created']),
    'files' => array_map(function ($f) { return ['id' => (int)$f['id'], 'kind' => $f['kind'], 'name' => $f['orig'], 'size' => (int)$f['size'], 'at' => ms($f['created'])]; }, $files),
    'missing' => rc_missing($files, (int)$a['stage'])];
  if ($who === 'adm') {
    $o += ['id' => (int)$a['id'], 'person' => (string)$a['person'], 'phone' => tel_fmt($a['phone']), 'email' => (string)$a['email'], 'intro' => (string)$a['intro'],
      'checks' => json_decode($a['checks'] ?: '{}', true) ?: new stdClass(), 'scores' => json_decode($a['scores'] ?: '{}', true) ?: new stdClass(), 'score' => $a['score'] === null ? null : (int)$a['score'],
      'memo' => (string)$a['memo'], 'reason' => (string)$a['reason'], 'gkIp' => (string)$a['gk_ip'], 'gkUa' => (string)$a['gk_ua'], 'vendorId' => $a['vendor_id'] ? (int)$a['vendor_id'] : null,
      'hist' => count(json_decode($a['hist'] ?: '[]', true) ?: [])];
  }
  return $o;
}

// ---------- 업체(공개 · 전용 링크) ----------
function a_rc_info() {
  $r = rc_get_by_code($_GET['r'] ?? ''); if (!$r) fail('모집 링크가 맞지 않습니다.', 404);
  $cnt = []; foreach (all('SELECT item, COUNT(*) c FROM applicant WHERE danji_id=? AND stage=4 GROUP BY item', [$r['danji_id']]) as $x) $cnt[$x['item']] = (int)$x['c'];
  out(['ok' => true, 'dj' => $r['dname'], 'open' => rc_open($r), 'deadline' => (string)$r['deadline'], 'intro' => (string)$r['intro'], 'terms' => rc_terms($r),
    'items' => array_map(function ($i) use ($cnt) { return $i + ['done' => $cnt[$i['item']] ?? 0]; }, rc_items($r)),
    'docs' => array_map(function ($k, $d) { return ['kind' => $k, 'name' => $d[0], 'when' => $d[1], 'max' => $d[2]]; }, array_keys(RC_DOCS), RC_DOCS),
    'company' => (string)cfg('company', ''), 'email' => (string)cfg('contact_email', '')]);
}
function a_rc_apply() {
  if (($_SERVER['REQUEST_METHOD'] ?? '') !== 'POST') fail('잘못된 요청입니다.', 405);
  $r = rc_get_by_code($_POST['r'] ?? ''); if (!$r) fail('모집 링크가 맞지 않습니다.', 404);
  if (!rc_open($r)) fail('모집이 마감되었거나 아직 열리지 않았습니다.');
  if (!empty($_POST['website'])) out(['ok' => true]);
  if (!hit_ok('rc_apply', 10, 3600)) fail('신청이 너무 많습니다. 잠시 뒤 다시 해 주세요.', 429);
  $item = str_in($_POST['item'] ?? '', 50);
  if (!in_array($item, array_column(rc_items($r), 'item'), true)) fail('신청할 품목을 골라 주세요.');
  $row = ['company' => str_in($_POST['company'] ?? '', 100), 'biz_no' => digits($_POST['biz_no'] ?? ''), 'ceo' => str_in($_POST['ceo'] ?? '', 50), 'addr' => str_in($_POST['addr'] ?? '', 200),
    'person' => str_in($_POST['person'] ?? '', 50), 'phone' => digits($_POST['phone'] ?? ''), 'email' => str_in($_POST['email'] ?? '', 100), 'tag' => str_in($_POST['tag'] ?? '', 100), 'intro' => str_in($_POST['intro'] ?? '', 1000)];
  if ($row['company'] === '' || $row['ceo'] === '') fail('상호와 대표자를 적어 주세요.');
  if (strlen($row['biz_no']) !== 10) fail('사업자등록번호 10자리를 확인해 주세요.');
  if (!preg_match('/^01[016789]\d{7,8}$/', $row['phone'])) fail('담당 휴대폰 번호를 확인해 주세요. 결과 안내 문자를 이 번호로 보냅니다.');
  if (($_POST['a1'] ?? '') !== '1' || ($_POST['a2'] ?? '') !== '1') fail('필수 동의 2개에 체크해 주세요.');
  if (one('SELECT id FROM applicant WHERE danji_id=? AND item=? AND biz_no=? AND stage<>9', [$r['danji_id'], $item, $row['biz_no']])) fail('같은 사업자번호로 이 품목에 이미 신청하셨습니다. 문자로 받은 링크에서 서류를 보완해 주세요.');
  $now = time(); $pre = 'RC-' . date('ymd', $now) . '-'; $id = 0;
  $base = (int)one('SELECT COUNT(*) c FROM applicant WHERE no LIKE ?', [$pre . '%'])['c'];
  for ($try = 1; $try <= 5 && !$id; $try++) {
    try { $id = ins('applicant', $row + ['danji_id' => $r['danji_id'], 'no' => $pre . sprintf('%03d', $base + $try), 'item' => $item, 'stage' => 0, 'token' => rnd(24), 'agree_at' => $now, 'hist' => '[]', 'created' => $now, 'ip' => ip()]); }
    catch (PDOException $e) { if ($try === 5) throw $e; }
  }
  $got = [];
  foreach (RC_DOCS as $k => $d) { $n = rc_save_files($id, $k, 'f_' . $k, $d[2]); if ($n) $got[] = $d[0] . ' ' . $n; }
  $a = rc_app('a.id=?', [$id]);
  rc_log($id, '업체', '모집 신청 · 참여 조건 · 규정 준수 확약 동의' . ($got ? ' · 서류: ' . implode(', ', $got) : ''));
  require_once __DIR__ . '/notify.php';
  sms($a['phone'], brand() . ' ' . $a['dname'] . ' 업체 모집 신청 접수 ' . $a['no'] . "\n품목: " . $a['item'] . "\n심사 결과는 이 번호로 알려 드립니다. 신청 내용 확인 · 서류 보완: " . link_partner($a), 'rc_apply');
  foreach (admins_to_notify() as $ad) sms($ad['phone'], '[업체 모집 신청] ' . $a['dname'] . ' ' . $a['item'] . ' · ' . $a['company'] . "\n" . base_url() . '/admin.php#rc', 'adm_rc');
  out(['ok' => true, 'no' => $a['no'], 'missing' => rc_missing(rc_files($id), 0), 'link' => link_partner($a)]);
}
function pt_app() {
  $tok = (string)($_REQUEST['t'] ?? ''); if (strlen($tok) < 16) fail('링크가 맞지 않습니다.', 404);
  $a = rc_app('a.token=?', [$tok]); if (!$a) fail('링크가 맞지 않습니다.', 404);
  return $a;
}
function a_pt_get() {
  $a = pt_app();
  $r = one('SELECT * FROM recruit WHERE danji_id=?', [$a['danji_id']]);
  out(['ok' => true, 'a' => rc_pub($a, 'pub'), 'terms' => $r ? rc_terms($r) : [],
    'docs' => array_map(function ($k, $d) { return ['kind' => $k, 'name' => $d[0], 'when' => $d[1], 'max' => $d[2]]; }, array_keys(RC_DOCS), RC_DOCS)]);
}
// 업체가 서류를 보완하거나, 선정 뒤 각서 날인본을 올리고 전자 동의
function a_pt_upload() {
  if (($_SERVER['REQUEST_METHOD'] ?? '') !== 'POST') fail('잘못된 요청입니다.', 405);
  $a = pt_app(); $st = (int)$a['stage']; $kind = (string)($_POST['kind'] ?? '');
  if ($st === 9) fail('심사가 끝난 신청입니다.');
  if (!isset(RC_DOCS[$kind])) fail('올릴 서류를 골라 주세요.');
  if ($kind === 'gaksu') {
    if ($st !== 3) fail('특약이행각서는 선정 뒤에 올립니다.');
    if (($_POST['agree'] ?? '') !== '1') fail('각서 내용을 확인했다는 전자 동의에 체크해 주세요.');
  }
  $n = rc_save_files($a['id'], $kind, 'files', RC_DOCS[$kind][2]);
  if (!$n) fail(rc_upload_err() . ' (서류마다 올릴 수 있는 장수도 정해져 있습니다.)');
  if ($kind === 'gaksu') { upd('applicant', $a['id'], ['gk_at' => time(), 'gk_ip' => ip(), 'gk_ua' => mb_substr((string)($_SERVER['HTTP_USER_AGENT'] ?? ''), 0, 200)]); }
  rc_log($a['id'], '업체', RC_DOCS[$kind][0] . ' ' . $n . '개 올림' . ($kind === 'gaksu' ? ' · 각서 내용 전자 동의(' . ip() . ')' : ''));
  if ($kind === 'gaksu') { require_once __DIR__ . '/notify.php'; foreach (admins_to_notify() as $ad) sms($ad['phone'], '[각서 도착] ' . $a['dname'] . ' ' . $a['item'] . ' · ' . $a['company'] . "\n날인본을 확인해 주세요. " . base_url() . '/admin.php#rc', 'adm_rc'); }
  out(['ok' => true, 'a' => rc_pub(rc_app('a.id=?', [$a['id']]), 'pub')]);
}

// ---------- 주관사(관리 화면) ----------
function a_rc_list() {
  $dj = (int)($_GET['danji'] ?? 0);
  $r = $dj ? one('SELECT * FROM recruit WHERE danji_id=?', [$dj]) : null;
  $list = [];
  foreach (all('SELECT a.*, d.name dname FROM applicant a JOIN danji d ON d.id=a.danji_id' . ($dj ? ' WHERE a.danji_id=?' : '') . ' ORDER BY a.id DESC LIMIT 1000', $dj ? [$dj] : []) as $a) {
    $o = rc_pub($a, 'adm'); unset($o['intro'], $o['memo'], $o['gkUa']); $list[] = $o;
  }
  out(['ok' => true, 'r' => $r ? ['code' => $r['code'], 'open' => (int)$r['open'], 'deadline' => (string)$r['deadline'], 'items' => (string)$r['items'], 'intro' => (string)$r['intro'], 'terms' => (string)($r['terms'] ?: RC_TERMS), 'link' => base_url() . '/recruit.php?r=' . $r['code']] : null,
    'list' => $list, 'scoreItems' => rc_score_items(), 'docs' => RC_DOCS, 'st' => RC_ST, 'termsDefault' => RC_TERMS]);
}
function a_rc_save() {
  $dj = (int)($_POST['danji_id'] ?? 0); if (!one('SELECT id FROM danji WHERE id=?', [$dj])) fail('단지를 먼저 골라 주세요.');
  $dl = trim((string)($_POST['deadline'] ?? ''));
  if ($dl !== '' && !preg_match('/^\d{4}-\d{2}-\d{2}( \d{2}:\d{2})?$/', $dl)) fail('마감은 2026-11-20 18:00처럼 적어 주세요.');
  $row = ['open' => ($_POST['open'] ?? '0') === '1' ? 1 : 0, 'deadline' => $dl ?: null, 'items' => str_in($_POST['items'] ?? '', 3000), 'intro' => str_in($_POST['intro'] ?? '', 2000), 'terms' => str_in($_POST['terms'] ?? '', 4000)];
  $r = one('SELECT * FROM recruit WHERE danji_id=?', [$dj]);
  if ($r) upd('recruit', $r['id'], $row);
  else { do { $c = rnd(8); } while (one('SELECT id FROM recruit WHERE code=?', [$c])); ins('recruit', $row + ['danji_id' => $dj, 'code' => $c, 'created' => time()]); }
  alog('rc_save', 'danji ' . $dj);
  out(['ok' => true]);
}
function a_rc_get() {
  $a = rc_app('a.id=?', [(int)($_GET['id'] ?? 0)]); if (!$a) fail('신청을 찾지 못했습니다.', 404);
  alog('rc_view', $a['no']);
  $o = rc_pub($a, 'adm');
  $o['log'] = array_map(function ($l) { return ['at' => ms($l['at']), 'who' => $l['who'], 'what' => $l['what']]; }, all('SELECT * FROM rc_log WHERE applicant_id=? ORDER BY id DESC', [$a['id']]));
  $o['link'] = link_partner($a);
  out(['ok' => true, 'a' => $o]);
}
// 단계 이동 · 서류 확인 · 점수 · 메모 · 탈락 · 되돌리기 · 각서 확인(→ 참여 확정 + A/S 업체 등록) · 재촉 문자
function a_rc_act() {
  if (($_SERVER['REQUEST_METHOD'] ?? '') !== 'POST') fail('잘못된 요청입니다.', 405);
  $a = rc_app('a.id=?', [(int)($_POST['id'] ?? 0)]); if (!$a) fail('신청을 찾지 못했습니다.', 404);
  require_once __DIR__ . '/notify.php';
  $act = (string)($_POST['act'] ?? ''); $st = (int)$a['stage']; $who = '주관사 ' . ($_SESSION['name'] ?? ''); $files = rc_files($a['id']); $send = ($_POST['sms'] ?? '') === '1';
  $move = function ($to, $what, $extra = []) use (&$a, $st, $who) {
    $h = json_decode($a['hist'] ?: '[]', true) ?: []; $h[] = ['from' => $st, 'at' => time(), 'vendor_id' => $a['vendor_id'], 'gk_ok' => $a['gk_ok'], 'reason' => $a['reason']];
    upd('applicant', $a['id'], $extra + ['stage' => $to, 'hist' => json_encode($h)]); rc_log($a['id'], $who, $what);
  };
  if ($act === 'check') {
    $c = json_decode($a['checks'] ?: '{}', true) ?: []; $k = (string)($_POST['kind'] ?? ''); if (!isset(RC_DOCS[$k])) fail('서류를 골라 주세요.');
    $c[$k] = ($_POST['on'] ?? '') === '1' ? 1 : 0; upd('applicant', $a['id'], ['checks' => json_encode($c)]);
    rc_log($a['id'], $who, RC_DOCS[$k][0] . ($c[$k] ? ' 확인함' : ' 확인 취소'));
  } elseif ($act === 'score') {
    $s = []; $sum = 0;
    foreach (rc_score_items() as $i => $it) { $v = max(0, min($it['max'], (int)($_POST['s' . $i] ?? 0))); $s[$it['name']] = $v; $sum += $v; }
    upd('applicant', $a['id'], ['scores' => json_encode($s, JSON_UNESCAPED_UNICODE), 'score' => $sum]); rc_log($a['id'], $who, '세부 심사 점수 ' . $sum . '점');
  } elseif ($act === 'memo') {
    $m = str_in($_POST['memo'] ?? '', 1000); upd('applicant', $a['id'], ['memo' => $m]); rc_log($a['id'], $who, '메모 고침');
  } elseif ($act === 'next' && $st <= 2) {
    if ($st === 0 && ($m = rc_missing($files, 0))) fail('필수 서류가 아직 없습니다: ' . implode(', ', $m) . " · '서류 재촉 문자'로 보완을 요청하세요.");
    if ($st === 2 && $a['score'] === null) fail('세부 심사 점수를 먼저 저장해 주세요.');
    $to = $st + 1; $move($to, RC_ST[$to] . '(으)로 넘김');
    if ($to === 3) sms($a['phone'], brand() . ' ' . $a['dname'] . ' 입주박람회 참여업체로 선정되었습니다(품목 ' . $a['item'] . ").\n특약이행각서를 확인 · 인쇄해 날인한 뒤 링크에서 올려 주세요. 확인되면 참여가 확정됩니다.\n" . link_partner($a), 'rc_sel');
  } elseif ($act === 'gaksu_ok' && $st === 3) {
    if (!rc_has($files, 'gaksu') || !$a['gk_at']) fail('업체가 각서 날인본을 올리고 전자 동의를 해야 확인할 수 있습니다.');
    // 참여 확정: A/S 창구 '품목별 업체'에 등록(같은 단지 · 품목 · 상호가 있으면 다시 사용)
    $v = one('SELECT id FROM vendor WHERE danji_id=? AND item=? AND company=?', [$a['danji_id'], $a['item'], $a['company']]);
    if ($v) { upd('vendor', $v['id'], ['active' => 1, 'phone' => $a['phone'], 'person' => $a['person'], 'tag' => $a['tag']]); $vid = (int)$v['id']; }
    else $vid = ins('vendor', ['danji_id' => $a['danji_id'], 'item' => $a['item'], 'company' => $a['company'], 'tag' => $a['tag'], 'person' => $a['person'], 'phone' => $a['phone'], 'show_phone' => null, 'active' => 1, 'sort' => 100]);
    $move(4, '특약이행각서 날인본 확인 · 참여 확정 · A/S 창구 업체 등록', ['gk_ok' => time(), 'vendor_id' => $vid]);
    sms($a['phone'], brand() . ' ' . $a['dname'] . ' 입주박람회 참여가 확정되었습니다(품목 ' . $a['item'] . ").\n입주민 A/S 요청은 이 번호로 문자 링크가 갑니다. 진행 확인: " . link_partner($a), 'rc_ok');
  } elseif ($act === 'fail' && $st !== 9 && $st !== 4) {
    $why = str_in($_POST['why'] ?? '', 300); if ($why === '') fail('탈락 사유를 적어 주세요(내부 기록 · 업체에 보내지 않음).');
    $move(9, '탈락 · 사유: ' . $why, ['reason' => $why]);
    if ($send) sms($a['phone'], brand() . ' ' . $a['dname'] . ' 업체 모집 심사 결과, 이번에는 함께하지 못하게 되었습니다(품목 ' . $a['item'] . '). 신청해 주셔서 감사합니다.', 'rc_fail');
  } elseif ($act === 'undo') {
    $why = str_in($_POST['why'] ?? '', 200); if ($why === '') fail('되돌리는 사유를 적어 주세요(필수).');
    $h = json_decode($a['hist'] ?: '[]', true) ?: []; if (!$h) fail('되돌릴 처리가 없습니다.');
    $p = array_pop($h);
    if ($st === 4 && $a['vendor_id']) upd('vendor', $a['vendor_id'], ['active' => 0]); // 참여 확정을 되돌리면 A/S 창구 업체도 멈춤
    upd('applicant', $a['id'], ['stage' => (int)$p['from'], 'vendor_id' => $p['vendor_id'], 'gk_ok' => $p['gk_ok'], 'reason' => $p['reason'], 'hist' => json_encode($h)]);
    rc_log($a['id'], $who, "되돌림: '" . RC_ST[$st] . "' → '" . RC_ST[(int)$p['from']] . "' · 사유: " . $why);
  } elseif ($act === 'remind') {
    if (!rc_remind($a)) fail('재촉할 서류가 없습니다.');
  } else fail('지금 단계에서는 할 수 없는 처리입니다. 화면을 새로 고쳐 주세요.');
  $a2 = rc_app('a.id=?', [$a['id']]); $o = rc_pub($a2, 'adm');
  $o['log'] = array_map(function ($l) { return ['at' => ms($l['at']), 'who' => $l['who'], 'what' => $l['what']]; }, all('SELECT * FROM rc_log WHERE applicant_id=? ORDER BY id DESC', [$a['id']]));
  $o['link'] = link_partner($a2);
  out(['ok' => true, 'a' => $o]);
}
// 빠진 서류 재촉 문자(신청 때 필수 · 선정 뒤 각서)
function rc_remind($a) {
  $m = rc_missing(rc_files($a['id']), (int)$a['stage']); if (!$m || (int)$a['stage'] >= 4 || (int)$a['stage'] === 9) return false;
  require_once __DIR__ . '/notify.php';
  sms($a['phone'], brand() . ' ' . $a['dname'] . ' 업체 모집: 아직 받지 못한 서류가 있습니다(' . implode(', ', $m) . ").\n링크에서 올려 주세요: " . link_partner($a), 'rc_remind');
  rc_log($a['id'], '주관사 ' . ($_SESSION['name'] ?? ''), '서류 재촉 문자: ' . implode(', ', $m));
  return true;
}
function a_rc_remind_all() {
  if (($_SERVER['REQUEST_METHOD'] ?? '') !== 'POST') fail('잘못된 요청입니다.', 405);
  $dj = (int)($_POST['danji'] ?? 0); $n = 0;
  foreach (all('SELECT a.*, d.name dname FROM applicant a JOIN danji d ON d.id=a.danji_id WHERE a.danji_id=? AND a.stage IN (0,3)', [$dj]) as $a) if (rc_remind($a)) $n++;
  alog('rc_remind', 'danji ' . $dj . ' · ' . $n);
  out(['ok' => true, 'n' => $n]);
}
// 올린 서류 내려받기(주관사 로그인만) — 파일은 data/ 안에서만 읽음
function a_rc_file() {
  $f = one('SELECT f.*, a.no FROM rc_file f JOIN applicant a ON a.id=f.applicant_id WHERE f.id=?', [(int)($_GET['id'] ?? 0)]);
  if (!$f || !is_file(DATA . '/recruit/' . $f['file'])) { http_response_code(404); exit; }
  alog('rc_file', $f['no'] . ' ' . $f['kind']);
  $ext = strtolower(pathinfo($f['file'], PATHINFO_EXTENSION));
  $mime = ['pdf' => 'application/pdf', 'jpg' => 'image/jpeg', 'jpeg' => 'image/jpeg', 'png' => 'image/png', 'webp' => 'image/webp'][$ext] ?? 'application/octet-stream';
  $inline = ($_GET['view'] ?? '') === '1' && $mime !== 'application/octet-stream';
  header('Content-Type: ' . $mime); header('X-Content-Type-Options: nosniff'); header('Cache-Control: private, no-store');
  header('Content-Disposition: ' . ($inline ? 'inline' : 'attachment') . "; filename=\"file.$ext\"; filename*=UTF-8''" . rawurlencode($f['no'] . '_' . RC_DOCS[$f['kind']][0] . '_' . $f['orig']));
  readfile(DATA . '/recruit/' . $f['file']); exit;
}
// 입예협 공유용 심사표(CSV): 개인 연락처 · 메모 · 탈락 사유 제외
function a_rc_csv() {
  $dj = (int)($_GET['danji'] ?? 0); $items = rc_score_items();
  alog('rc_csv', 'danji ' . $dj);
  header('Content-Type: text/csv; charset=utf-8');
  header('Content-Disposition: attachment; filename="rc_review_' . date('Ymd') . '.csv"');
  $o = fopen('php://output', 'w'); fwrite($o, "\xEF\xBB\xBF");
  fputcsv($o, array_merge(['접수번호', '품목', '상호', '대표자', '취급 품목', '단계'], array_map(function ($k) { return $k[0]; }, array_values(RC_DOCS)), array_map(function ($i) { return $i['name'] . '(' . $i['max'] . ')'; }, $items), ['합계', '신청일']));
  foreach (all('SELECT a.*, d.name dname FROM applicant a JOIN danji d ON d.id=a.danji_id WHERE a.danji_id=? ORDER BY a.item, a.score DESC, a.id', [$dj]) as $a) {
    $files = rc_files($a['id']); $s = json_decode($a['scores'] ?: '{}', true) ?: [];
    fputcsv($o, array_merge([$a['no'], $a['item'], $a['company'], $a['ceo'], (string)$a['tag'], RC_ST[(int)$a['stage']]],
      array_map(function ($k) use ($files) { return rc_has($files, $k) ? '있음' : ''; }, array_keys(RC_DOCS)),
      array_map(function ($i) use ($s) { return $s[$i['name']] ?? ''; }, $items), [$a['score'] === null ? '' : (int)$a['score'], date('Y-m-d', $a['created'])]));
  }
  fclose($o); exit;
}
function a_rc_score_save() {
  $t = str_in($_POST['text'] ?? '', 1000);
  foreach (preg_split('/\r?\n/', $t) as $l) { $l = trim($l); if ($l !== '' && !preg_match('/^[^|]+\|\s*\d+\s*$/u', $l)) fail("이 줄을 '항목|배점'으로 적어 주세요: " . $l); }
  meta_set('rc_score', $t); alog('rc_score');
  out(['ok' => true, 'items' => rc_score_items()]);
}

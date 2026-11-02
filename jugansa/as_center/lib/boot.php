<?php
// 공통 바탕: 설정 · DB · 도우미 · 영업일 기한 · 요청 상태 · 자동 점검(크론 대신)
date_default_timezone_set('Asia/Seoul');
mb_internal_encoding('UTF-8');
define('ROOT', dirname(__DIR__));
define('DATA', ROOT . '/data');

if (!is_file(ROOT . '/config.php')) {
  http_response_code(500);
  header('Content-Type: text/plain; charset=utf-8');
  exit('config.php가 없습니다. config.sample.php를 config.php로 복사해 값을 채워 주세요.');
}
$GLOBALS['CFG'] = require ROOT . '/config.php';
function cfg($k, $d = null) { return array_key_exists($k, $GLOBALS['CFG']) ? $GLOBALS['CFG'][$k] : $d; }

// ---------- DB ----------
function db() {
  static $pdo = null;
  if ($pdo) return $pdo;
  $c = cfg('db');
  if (($c['type'] ?? '') === 'sqlite') {
    if (!is_dir(dirname($c['path']))) mkdir(dirname($c['path']), 0700, true);
    $pdo = new PDO('sqlite:' . $c['path']);
    $pdo->exec('PRAGMA journal_mode=WAL');
  } else {
    $pdo = new PDO('mysql:host=' . $c['host'] . ';dbname=' . $c['name'] . ';charset=utf8mb4', $c['user'], $c['pass']);
  }
  $pdo->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
  $pdo->setAttribute(PDO::ATTR_DEFAULT_FETCH_MODE, PDO::FETCH_ASSOC);
  return $pdo;
}
function db_type() { return cfg('db')['type'] ?? 'mysql'; }
function q($sql, $p = []) { $s = db()->prepare($sql); $s->execute($p); return $s; }
function one($sql, $p = []) { $r = q($sql, $p)->fetch(); return $r ?: null; }
function all($sql, $p = []) { return q($sql, $p)->fetchAll(); }
function ins($table, $row) {
  $k = array_keys($row);
  q('INSERT INTO ' . $table . ' (' . implode(',', $k) . ') VALUES (' . implode(',', array_fill(0, count($k), '?')) . ')', array_values($row));
  return (int)db()->lastInsertId();
}
function upd($table, $id, $row) {
  if (!$row) return;
  $set = []; foreach ($row as $k => $v) $set[] = $k . '=?';
  $p = array_values($row); $p[] = $id;
  q('UPDATE ' . $table . ' SET ' . implode(',', $set) . ' WHERE id=?', $p);
}
function meta_get($k) { $r = one('SELECT v FROM meta WHERE k=?', [$k]); return $r ? $r['v'] : null; }
function meta_set($k, $v) { if (q('UPDATE meta SET v=? WHERE k=?', [(string)$v, $k])->rowCount() === 0 && meta_get($k) === null) ins('meta', ['k' => $k, 'v' => (string)$v]); }
function installed() { try { return (bool)one('SELECT id FROM admin LIMIT 1'); } catch (Exception $e) { return false; } }

// ---------- 도우미 ----------
function h($s) { return htmlspecialchars((string)$s, ENT_QUOTES, 'UTF-8'); }
function out($a, $code = 200) {
  http_response_code($code);
  header('Content-Type: application/json; charset=utf-8');
  header('Cache-Control: no-store');
  echo json_encode($a, JSON_UNESCAPED_UNICODE);
  exit;
}
function fail($msg, $code = 400) { out(['ok' => false, 'msg' => $msg], $code); }
function digits($s) { return preg_replace('/\D/', '', (string)$s); }
function rnd($n) { $c = 'abcdefghjkmnpqrstuvwxyz23456789'; $s = ''; for ($i = 0; $i < $n; $i++) $s .= $c[random_int(0, strlen($c) - 1)]; return $s; }
function ip() { return substr($_SERVER['REMOTE_ADDR'] ?? '', 0, 45); }
function is_https() { return (!empty($_SERVER['HTTPS']) && $_SERVER['HTTPS'] !== 'off') || (($_SERVER['HTTP_X_FORWARDED_PROTO'] ?? '') === 'https'); }
function base_url() {
  $b = rtrim((string)cfg('base_url', ''), '/');
  if ($b) return $b;
  $dir = rtrim(str_replace('\\', '/', dirname($_SERVER['SCRIPT_NAME'] ?? '/')), '/');
  return (is_https() ? 'https' : 'http') . '://' . ($_SERVER['HTTP_HOST'] ?? 'localhost') . $dir;
}
function tel_fmt($p) { $p = digits($p); if (strlen($p) === 11) return substr($p, 0, 3) . '-' . substr($p, 3, 4) . '-' . substr($p, 7); if (strlen($p) === 10) return substr($p, 0, 3) . '-' . substr($p, 3, 3) . '-' . substr($p, 6); return $p; }
function tel_mask($p) { $p = digits($p); return strlen($p) >= 8 ? substr($p, 0, 3) . '-****-' . substr($p, -4) : '****'; }
function fmt_t($t) { if (!$t) return ''; $w = ['일', '월', '화', '수', '목', '금', '토'][(int)date('w', $t)]; return date('n.d', $t) . "($w) " . date('H:i', $t); }
function clean_dh($s, $cut) { return mb_substr(preg_replace('/[^0-9A-Za-z가-힣]/u', '', str_replace($cut, '', (string)$s)), 0, 8); }
function str_in($s, $max) { return mb_substr(trim((string)$s), 0, $max); }
// 같은 인터넷 주소의 같은 행동이 기준을 넘으면 막기(조회 · 로그인 · 접수)
function hit_ok($kind, $max, $sec) {
  $n = (int)one('SELECT COUNT(*) c FROM hit WHERE ip=? AND kind=? AND at>?', [ip(), $kind, time() - $sec])['c'];
  if ($n >= $max) return false;
  ins('hit', ['ip' => ip(), 'kind' => $kind, 'at' => time()]);
  return true;
}

// ---------- 영업일 기한 ----------
function hol() { static $h = null; if ($h === null) { $h = []; foreach (all('SELECT d FROM holiday') as $r) $h[$r['d']] = 1; } return $h; }
function is_off($t) { $w = (int)date('w', $t); return $w === 0 || $w === 6 || isset(hol()[date('Y-m-d', $t)]); }
function biz12_after($t) { $x = strtotime(date('Y-m-d', $t) . ' 12:00:00'); do { $x = strtotime('+1 day', $x); } while (is_off($x)); return $x; }
// h시간 뒤가 주말 · 공휴일이면 다음 영업일 12시. 주말 · 공휴일에 들어온 요청도 다음 영업일 12시보다 이르지 않게
function biz_due($t, $h) { $d = $t + $h * 3600; if (is_off($d)) $d = biz12_after($d); if (is_off($t)) $d = max($d, biz12_after($t)); return $d; }

// ---------- 요청 상태 ----------
const CATS = ['품목 하자 · A/S', '방문 일정 변경', '환불 · 취소', '기타 문의 · 불편'];
const BUILD_CAT = '아파트 자체 하자(시공사 전달)';
const VC = ['연락했는데 24시간 넘게 답이 없어요', '연락했지만 해결이 안 됐어요', '업체와 방문 일정이 안 맞아요', '아직 연락 안 했어요'];
const VC_SHORT = ['답 없음', '해결 안 됨', '일정 안 맞음', '업체 연락 전'];
const SLOTS = ['업체와 통화로 협의', '언제든 가능', '평일 오전', '평일 오후', '평일 저녁(18시 이후)', '토요일', '일요일'];
const RLB = ['', '아쉬워요', '보통이에요', '좋았어요'];
// 되돌리기 때 함께 돌아가는 칸
const TKEYS = ['st', 'r_at', 'r_by', 'v_at', 'visit', 'd_at', 'confirm', 'rating', 'c_at', 'vd', 'va', 'ro', 'rw', 'reopen', 'phd', 'item', 'vendor_id'];

function t_known($t) { return !$t['is_build'] && !empty($t['vendor_id']); }
function need_visit($t) { return !$t['is_build'] && ($t['cat'] === CATS[0] || $t['cat'] === CATS[1]); }
// 1차 연락 = 요청(또는 업체 지정 · 변경) 시각부터 영업일 24시간 · 방문 일정 확정 = 그 기한에서 다시 영업일 24시간
function reply_due($t) { return biz_due((int)($t['va'] ?: $t['created']), 24); }
function visit_due($t) { return $t['vd'] ? (int)$t['vd'] : biz_due(reply_due($t), 24); }
function next_due($t) { $st = (int)$t['st']; if ($st === 0) return reply_due($t); if ($st === 1 && need_visit($t)) return visit_due($t); return 0; }
function stage_name($t) {
  $st = (int)$t['st'];
  if ($t['is_build']) return ['접수', '시공사 전달', '시공사 처리 확인', '처리 완료'][$st];
  if (!need_visit($t) && $st === 2) return '처리 중';
  return ['접수', '1차 회신', '방문 일정 확정', '처리 완료'][$st];
}
// 요청 한 건(단지 · 업체 이름까지)
define('T_SEL', 'SELECT t.*, d.name dname, d.code dcode, v.company vend, v.phone vphone FROM ticket t JOIN danji d ON d.id=t.danji_id LEFT JOIN vendor v ON v.id=t.vendor_id');
function t_get($where, $p) { return one(T_SEL . ' WHERE ' . $where, $p); }
function t_reload($t) { return t_get('t.id=?', [$t['id']]); }
function t_save($t) { $row = []; foreach (array_merge(TKEYS, ['hist', 'late_key', 'remind_key']) as $k) $row[$k] = $t[$k]; upd('ticket', $t['id'], $row); }
function tlog($tid, $who, $what, $rev = 0, $at = null) { ins('log', ['ticket_id' => $tid, 'at' => $at ?: time(), 'who' => mb_substr($who, 0, 60), 'what' => mb_substr($what, 0, 500), 'rev' => $rev]); }
// 되돌리기: 바꾸기 전 상태를 hist(JSON)에 쌓고, 마지막 것을 꺼내 되돌림
function snap(&$t, $by, $label, $res = 0) {
  $h = json_decode($t['hist'] ?: '[]', true) ?: [];
  $v = []; foreach (TKEYS as $k) $v[$k] = $t[$k];
  $h[] = ['at' => time(), 'by' => $by, 'label' => $label, 'res' => $res ? 1 : 0, 'v' => $v];
  $t['hist'] = json_encode($h, JSON_UNESCAPED_UNICODE);
}
function last_hist($t) { $h = json_decode($t['hist'] ?: '[]', true) ?: []; return $h ? $h[count($h) - 1] : null; }
function undo(&$t, $by, $why) {
  $h = json_decode($t['hist'] ?: '[]', true) ?: [];
  if (!$h) return null;
  $s = array_pop($h);
  foreach (TKEYS as $k) $t[$k] = $s['v'][$k];
  $t['hist'] = json_encode($h, JSON_UNESCAPED_UNICODE);
  t_save($t);
  tlog($t['id'], $by, "되돌림: '" . $s['label'] . "' 취소" . ($why ? ' · 사유: ' . $why : ''), 1);
  return $s;
}

// ---------- 화면으로 보낼 모양(시각은 밀리초) ----------
function photos_of($t, $kind, $tokenParam) {
  $lim = $kind === 'req' ? (int)$t['ph'] : (int)$t['phd'];
  if (!$lim) return [];
  $rows = all('SELECT id FROM photo WHERE ticket_id=? AND kind=? ORDER BY id LIMIT ' . $lim, [$t['id'], $kind]);
  $u = []; foreach ($rows as $r) $u[] = 'api.php?a=photo&id=' . $r['id'] . $tokenParam;
  return $u;
}
function ms($s) { return $s ? (int)$s * 1000 : null; }
function t_pub($t, $who, $light = false) {
  // who: res(입주민) · ven(업체) · adm(주관사) · light = 목록용(사진 주소 생략)
  $tp = $who === 'res' ? '&k=' . $t['rtoken'] : ($who === 'ven' ? '&t=' . $t['vtoken'] : '');
  $o = [
    'no' => $t['no'], 'dh' => $t['dong'] . '-' . $t['ho'], 'dj' => $t['dname'], 'cat' => $t['cat'], 'build' => (int)$t['is_build'],
    'item' => $t['item'], 'vend' => t_known($t) ? $t['vend'] : null, 'vc' => $t['vc'], 'body' => $t['body'], 'slot' => $t['slot'],
    'st' => (int)$t['st'], 't' => ms($t['created']), 'va' => ms($t['va']), 'rAt' => ms($t['r_at']), 'rBy' => $t['r_by'], 'vAt' => ms($t['v_at']), 'visit' => $t['visit'],
    'dAt' => ms($t['d_at']), 'confirm' => $t['confirm'] === null ? null : (int)$t['confirm'], 'cAt' => ms($t['c_at']), 'ro' => ms($t['ro']), 'rw' => $t['rw'],
    'reopen' => (int)$t['reopen'], 'ph' => (int)$t['ph'], 'phd' => (int)$t['phd'], 'needVisit' => need_visit($t) ? 1 : 0,
    'stage' => stage_name($t), 'replyDue' => ms(reply_due($t)), 'visitDue' => ms(visit_due($t)), 'nextDue' => ms(next_due($t)),
    'photos' => $light ? null : ['req' => photos_of($t, 'req', $tp), 'done' => photos_of($t, 'done', $tp)],
  ];
  if ($who === 'res') $o['k'] = $t['rtoken'];
  if ($who !== 'res') { $o['nm'] = $t['name']; $o['tel'] = tel_fmt($t['phone']); }
  if ($who === 'adm') {
    $o['id'] = (int)$t['id']; $o['rating'] = $t['rating'] === null ? null : (int)$t['rating']; $o['vendorId'] = $t['vendor_id'] ? (int)$t['vendor_id'] : null;
    $o['danjiId'] = (int)$t['danji_id']; $o['va'] = ms($t['va']);
    $h = last_hist($t); $o['last'] = $h ? ['label' => $h['label'], 'by' => $h['by'], 'at' => ms($h['at']), 'res' => $h['res']] : null;
  }
  if ($who === 'ven') { $h = last_hist($t); $o['last'] = $h ? ['label' => $h['label'], 'by' => $h['by'], 'at' => ms($h['at'])] : null; }
  return $o;
}

// ---------- 자동 점검(크론 대신 · 10분에 한 번) ----------
// ① 업체 1차 회신 기한 6시간 전 재촉 ② 기한 지남 → 주관사 개입 문자 ③ 보유 기간 지난 단지 파기 ④ 오래된 접속 횟수 기록 지우기
function tick($force = false) {
  try {
    $last = (int)meta_get('tick');
    if (!$force && time() - $last < 600) return;
    meta_set('tick', time());
    require_once __DIR__ . '/notify.php';
    $now = time();
    foreach (all(T_SEL . ' WHERE t.st<3 AND t.purged=0') as $t) {
      $d = next_due($t);
      if (!$d) continue;
      $key = $t['st'] . '|' . (int)$t['va'] . '|' . (int)$t['reopen'];
      if ((int)$t['st'] === 0 && t_known($t) && $d > $now && $d - $now <= 6 * 3600 && $t['remind_key'] !== $key) {
        $t['remind_key'] = $key; t_save($t); n_remind($t, $d);
      }
      if ($d < $now && $t['late_key'] !== $key) {
        $t['late_key'] = $key; t_save($t);
        tlog($t['id'], '자동 점검', ((int)$t['st'] === 0 ? '1차 연락' : '방문 일정 확정') . ' 기한 지남 · 주관사 개입', 0, $d);
        n_late($t, $d);
      }
    }
    foreach (all("SELECT id FROM danji WHERE purge_date IS NOT NULL AND purge_date<>'' AND purge_date<?", [date('Y-m-d')]) as $dj) {
      foreach (all('SELECT * FROM ticket WHERE danji_id=? AND purged=0', [$dj['id']]) as $t) purge_ticket($t);
    }
    q('DELETE FROM hit WHERE at<?', [$now - 86400 * 2]);
  } catch (Exception $e) { /* 점검 실패가 화면을 막지 않게 */ }
}
// 보유 기간이 끝난 요청: 개인정보 · 사진을 지우고 통계용 칸만 남김
function purge_ticket($t) {
  foreach (all('SELECT * FROM photo WHERE ticket_id=?', [$t['id']]) as $p) { @unlink(DATA . '/photos/' . $p['file']); }
  q('DELETE FROM photo WHERE ticket_id=?', [$t['id']]);
  upd('ticket', $t['id'], ['name' => '(파기)', 'phone' => '', 'tel4' => '', 'body' => '(보유 기간이 끝나 파기했습니다)', 'rw' => null, 'visit' => null, 'ip' => '', 'purged' => 1, 'vtoken' => rnd(24), 'rtoken' => rnd(24), 'hist' => '[]']);
  q("UPDATE sms_log SET msg='(파기)', phone='' WHERE ticket_id=?", [$t['id']]);
  q("UPDATE log SET what='(파기)' WHERE ticket_id=? AND (what LIKE '메모:%' OR what LIKE '%사유:%' OR what LIKE '%아쉬운 점%')", [$t['id']]);
}

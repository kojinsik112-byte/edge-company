<?php
// 시험판 시연 데이터: 표를 비우고 시연용 단지 · 업체 · 요청을 '지금 시각' 기준으로 새로 넣는다(시연_시작.bat이 부름).
// 요청마다 실제 화면과 같은 흐름(되돌리기 이력 · 처리 이력 · 문자 기록)을 거치게 만들고, 시각만 과거로 맞춘다.
if (PHP_SAPI !== 'cli') { http_response_code(404); exit; }
require __DIR__ . '/lib/boot.php';
require __DIR__ . '/lib/schema.php';
require __DIR__ . '/lib/notify.php';

// ---------- 비우기 · 표 만들기 ----------
if (!is_dir(DATA . '/photos')) mkdir(DATA . '/photos', 0700, true);
foreach (glob(DATA . '/photos/*') ?: [] as $f) @unlink($f);
@unlink(DATA . '/sms_token.json');
foreach (all("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'") as $r) db()->exec('DROP TABLE ' . $r['name']);
foreach (schema_sql(db_type()) as $sql) db()->exec($sql);
foreach (default_holidays() as $d => $n) ins('holiday', ['d' => $d, 'name' => $n]);
$A = cfg('demo_admin');
ins('admin', ['login' => $A['login'], 'pass' => password_hash($A['pw'], PASSWORD_DEFAULT), 'name' => $A['name'], 'phone' => $A['phone'], 'notify' => 1, 'active' => 1, 'created' => time()]);
file_put_contents(DATA . '/index.html', '');
file_put_contents(DATA . '/probe.txt', 'data-folder-open');
meta_set('installed', date('Y-m-d H:i'));
db()->beginTransaction();

// ---------- 단지 · 업체(번호는 010-0000-으로 시작하는 시연용) ----------
$DJ = ins('danji', ['code' => 'demo', 'name' => '○○ 아파트(시연)', 'active' => 1, 'purge_date' => null, 'keep_text' => null, 'created' => time()]);
$VEND = [
  ['중문', '중문 업체 A', '3연동 · 슬라이딩'], ['중문', '중문 업체 B', '스윙 · 여닫이'],
  ['줄눈', '줄눈 업체 A', '욕실 · 현관'], ['탄성코트', '탄성코트 업체 A', '발코니 · 다용도실'], ['탄성코트', '탄성코트 업체 B', '발코니'],
  ['커튼 · 블라인드', '커튼 업체 A', '전동 커튼'], ['커튼 · 블라인드', '커튼 업체 B', '블라인드 · 롤스크린'],
  ['조명', '조명 업체 A', 'LED 교체 · 간접조명'], ['시스템에어컨', '에어컨 업체 A', '천장형 2 ~ 4대'], ['시스템에어컨', '에어컨 업체 B', '천장형 · 벽걸이'],
  ['붙박이장', '붙박이장 업체 A', '안방 · 드레스룸'], ['안전 방충망', '방충망 업체 A', '미세 방충망'],
];
foreach (['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H'] as $i => $c) $VEND[] = ['입주청소', '입주청소 업체 ' . $c, $i % 2 ? '새집증후군 시공 포함' : '줄눈 · 탄성 부분 보수'];
foreach ($VEND as $i => $v) ins('vendor', ['danji_id' => $DJ, 'item' => $v[0], 'company' => $v[1], 'tag' => $v[2], 'person' => '담당자', 'phone' => sprintf('0100000%04d', 1001 + $i), 'show_phone' => null, 'active' => 1, 'sort' => $i]);
function V($company) { return one('SELECT * FROM vendor WHERE company=?', [$company]); }

// ---------- 도우미 ----------
$NOW = time();
function ago($h) { return $GLOBALS['NOW'] - (int)round($h * 3600); }
function when_txt($t) { return date('n.d', $t) . '(' . ['일', '월', '화', '수', '목', '금', '토'][(int)date('w', $t)] . ') ' . date('H:i', $t); }
// 이 사이에 쌓인 문자 기록의 시각을 그때로 맞춤
function at_time($at, $fn) { $m = (int)one('SELECT COALESCE(MAX(id),0) m FROM sms_log')['m']; $fn(); q('UPDATE sms_log SET at=? WHERE id>?', [$at, $m]); }
function photo($tid, $kind, $label) {
  $w = 1200; $h = 900; $im = imagecreatetruecolor($w, $h);
  for ($y = 0; $y < $h; $y++) imageline($im, 0, $y, $w, $y, imagecolorallocate($im, 236 - intdiv($y, 18), 228 - intdiv($y, 20), 214 - intdiv($y, 16)));
  $ink = imagecolorallocate($im, 88, 74, 58); $font = 'C:/Windows/Fonts/malgun.ttf';
  // 목록의 작은 정사각 미리보기에서도 보이게 가운데 크게
  $mid = function ($size, $y, $txt) use ($im, $ink, $font, $w) { $b = imagettfbbox($size, 0, $font, $txt); imagettftext($im, $size, 0, (int)(($w - ($b[2] - $b[0])) / 2), $y, $ink, $font, $txt); };
  if (is_file($font) && function_exists('imagettftext')) { $mid(84, 460, $label); $mid(40, 560, '시연용 예시 사진'); }
  $name = $tid . '_' . rnd(16) . '.jpg'; imagejpeg($im, DATA . '/photos/' . $name, 82); imagedestroy($im);
  ins('photo', ['ticket_id' => $tid, 'kind' => $kind, 'file' => $name, 'size' => (int)filesize(DATA . '/photos/' . $name), 'created' => time()]);
}
// 요청 넣기(입주민 화면 '주관사에 요청'과 같은 결과)
function mk($o) {
  $at = $o['at']; $pre = 'EC-' . date('ymd', $at) . '-'; $build = !empty($o['build']); $v = $o['vendor'] ?? null;
  $n = (int)one('SELECT COUNT(*) c FROM ticket WHERE no LIKE ?', [$pre . '%'])['c'] + 1;
  $id = ins('ticket', ['danji_id' => $GLOBALS['DJ'], 'no' => $pre . sprintf('%03d', $n), 'dong' => $o['dh'][0], 'ho' => $o['dh'][1], 'name' => $o['name'], 'phone' => $o['tel'], 'tel4' => substr($o['tel'], -4),
    'cat' => $build ? BUILD_CAT : ($o['cat'] ?? CATS[0]), 'is_build' => $build ? 1 : 0, 'item' => $build ? '—' : $o['item'], 'vendor_id' => $v ? (int)$v['id'] : null,
    'vc' => $build ? '' : ($o['vc'] ?? VC[0]), 'body' => $o['body'], 'slot' => $o['slot'] ?? SLOTS[0], 'st' => 0, 'created' => $at, 'hist' => '[]', 'vtoken' => rnd(24), 'rtoken' => rnd(24), 'ip' => '127.0.0.1']);
  $ph = 0; foreach ($o['photos'] ?? [] as $lb) { photo($id, 'req', $lb); $ph++; }
  if ($ph) upd('ticket', $id, ['ph' => $ph]);
  $t = t_get('t.id=?', [$id]);
  tlog($id, '입주민', '주관사에 요청' . ($t['vc'] ? ' · ' . $t['vc'] : '') . ($ph ? ' · 사진 ' . $ph . '장' : ''), 0, $at);
  at_time($at, function () use ($t) { n_new($t); });
  return $t;
}
// 한 단계 처리(되돌리기 이력 · 처리 이력 · 문자) — 화면에서 누른 것과 같게, 시각만 $at
function step(&$t, $at, $by, $label, $res, $ch, $who, $what, $fn = null) {
  snap($t, $by, $label, $res);
  $h = json_decode($t['hist'], true); $h[count($h) - 1]['at'] = $at; $t['hist'] = json_encode($h, JSON_UNESCAPED_UNICODE);
  foreach ($ch as $k => $v) $t[$k] = $v;
  t_save($t); tlog($t['id'], $who, $what, 0, $at); $t = t_reload($t);
  if ($fn) { $tt = $t; at_time($at, function () use ($tt, $fn) { $fn($tt); }); }
}
function reply(&$t, $h) { step($t, ago($h), '업체', '연락했어요', 0, ['st' => 1, 'r_at' => ago($h), 'r_by' => '업체'], '업체 ' . $t['vend'], '고객에게 연락함(1차 회신)'); }
function visit(&$t, $h, $vt) { $w = when_txt($vt); step($t, ago($h), '업체', '방문 일정 확정', 1, ['st' => 2, 'v_at' => ago($h), 'visit' => $w], '업체 ' . $t['vend'], '방문 일정 확정: ' . $w, 'n_visit'); }
function done(&$t, $h, $note, $photos = []) {
  $n = (int)$t['phd']; foreach ($photos as $lb) { photo($t['id'], 'done', $lb); $n++; }
  step($t, ago($h), '업체', '처리 완료', 1, ['st' => 3, 'd_at' => ago($h), 'phd' => $n], '업체 ' . $t['vend'], '처리 완료 · ' . $note . ($photos ? ' · 완료 사진 ' . count($photos) . '장' : ''), 'n_done');
}
function confirm_ok(&$t, $h, $rating, $note = '') {
  step($t, ago($h), '입주민', '해결 확인', 0, ['confirm' => 1, 'rating' => $rating, 'c_at' => ago($h)], '입주민', '해결 확인 · 업체 응대 ' . RLB[$rating] . ($rating === 1 && $note !== '' ? ' (아쉬운 점: ' . $note . ')' : ''));
}
function reopen(&$t, $h, $why) {
  $at = ago($h);
  step($t, $at, '입주민', '다시 요청', 0, ['st' => 1, 'reopen' => (int)$t['reopen'] + 1, 'ro' => $at, 'rw' => $why, 'vd' => biz_due(biz_due($at, 24), 24), 'v_at' => null, 'visit' => null, 'd_at' => null],
    '입주민', '아직 해결 안 됨 · 다시 열림: ' . $why, function ($t) use ($why) { n_reopen($t, $why); });
}

// ---------- 요청 12건(오래된 것부터) ----------
// 주관사 개입: 업체가 기한 안에 '연락했어요'를 안 누름 → 아래 자동 점검이 빨간 줄로 바꿈
mk(['at' => ago(120), 'item' => '줄눈', 'vendor' => V('줄눈 업체 A'), 'vc' => VC[0], 'dh' => ['101', '1203'], 'name' => '김○○', 'tel' => '01000002001',
  'body' => '욕실 줄눈 일부가 들떠서 업체에 연락했는데 이틀째 답이 없어요.', 'photos' => ['욕실 줄눈 들뜸']]);
// 마감 · 좋았어요
$t = mk(['at' => ago(100), 'item' => '탄성코트', 'vendor' => V('탄성코트 업체 B'), 'vc' => VC[1], 'dh' => ['102', '804'], 'name' => '이○○', 'tel' => '01000002002',
  'body' => '발코니 탄성코트 한쪽 벽이 얼룩져 보여요.']);
reply($t, 96); visit($t, 95, ago(74)); done($t, 73, '얼룩 부분 재도장'); confirm_ok($t, 60, 3);
// 마감 · 보통이에요
$t = mk(['at' => ago(75), 'item' => '조명', 'vendor' => V('조명 업체 A'), 'vc' => VC[1], 'dh' => ['103', '502'], 'name' => '박○○', 'tel' => '01000002003',
  'body' => '거실 간접조명 한 줄이 깜빡거려요.', 'slot' => '평일 저녁(18시 이후)']);
reply($t, 70); visit($t, 66, ago(31)); done($t, 30, 'LED 바 교체', ['간접조명 교체 후']); confirm_ok($t, 26, 2);
// 마감 · 아쉬워요(내부용 평가)
$t = mk(['at' => ago(52), 'item' => '시스템에어컨', 'vendor' => V('에어컨 업체 A'), 'vc' => VC[2], 'dh' => ['104', '1701'], 'name' => '최○○', 'tel' => '01000002004',
  'body' => '안방 에어컨에서 물이 떨어져요. 업체와 방문 날짜가 계속 안 맞아요.', 'slot' => '토요일']);
reply($t, 44); visit($t, 42, ago(21)); done($t, 20, '배수 호스 재연결'); confirm_ok($t, 18, 1, '약속 시간보다 늦게 왔어요');
// 다시 열림
$t = mk(['at' => ago(49), 'item' => '붙박이장', 'vendor' => V('붙박이장 업체 A'), 'vc' => VC[1], 'dh' => ['101', '305'], 'name' => '정○○', 'tel' => '01000002005',
  'body' => '드레스룸 붙박이장 문이 끝까지 안 닫혀요.']);
reply($t, 47); visit($t, 46, ago(27)); done($t, 26, '경첩 조정'); reopen($t, 22, '문이 여전히 1cm 정도 떠 있어요');
// 방문 일정 확정
$t = mk(['at' => ago(30), 'item' => '커튼 · 블라인드', 'vendor' => V('커튼 업체 A'), 'vc' => VC[0], 'dh' => ['102', '1102'], 'name' => '강○○', 'tel' => '01000002006',
  'body' => '전동 커튼 모터가 중간에 멈춰요.', 'slot' => '평일 오후']);
reply($t, 28); visit($t, 27, strtotime(date('Y-m-d', $NOW + 2 * 86400) . ' 14:00'));
// 처리 완료 · 입주민 확인 대기(입주민 링크로 '해결됐어요' 시연)
$t = mk(['at' => ago(26), 'item' => '중문', 'vendor' => V('중문 업체 A'), 'vc' => VC[1], 'dh' => ['103', '1404'], 'name' => '조○○', 'tel' => '01000002007',
  'body' => '현관 중문이 레일에서 걸려 잘 안 밀려요.', 'photos' => ['중문 레일 걸림']]);
reply($t, 24); visit($t, 22, ago(4)); done($t, 3, '레일 청소 · 바퀴 교체', ['중문 수리 후', '레일 교체 부품']);
// 아파트 자체 하자 → 시공사 전달(주관사는 정리 · 전달 · 확인만)
$t = mk(['at' => ago(20), 'build' => true, 'dh' => ['104', '601'], 'name' => '윤○○', 'tel' => '01000002008',
  'body' => '거실 창호 틈으로 바람이 들어와요.', 'photos' => ['창호 틈']]);
step($t, ago(18), '주관사', '시공사에 전달함', 0, ['st' => 1, 'r_at' => ago(18), 'r_by' => '주관사'], '주관사 ' . $A['name'], '시공사 하자 창구에 전달 · 입주민 연락');
// 업체 확인 필요: 입주민이 업체를 기억 못 함
mk(['at' => ago(8), 'item' => '입주청소', 'vc' => VC[3], 'dh' => ['101', '902'], 'name' => '장○○', 'tel' => '01000002009',
  'body' => '입주청소 뒤 주방 상판에 얼룩이 남았어요. 어느 업체였는지 기억이 안 나요.']);
// 1차 회신 끝 · 방문 일정 기다림
$t = mk(['at' => ago(5), 'item' => '안전 방충망', 'vendor' => V('방충망 업체 A'), 'vc' => VC[0], 'dh' => ['102', '403'], 'name' => '임○○', 'tel' => '01000002010',
  'body' => '작은방 방충망이 틀에서 빠졌어요.']);
reply($t, 4);
// 목록에 없는 품목(직접 적기)
mk(['at' => ago(2.5), 'item' => '음식물 처리기', 'vc' => VC[3], 'dh' => ['103', '207'], 'name' => '한○○', 'tel' => '01000002011',
  'body' => '음식물 처리기가 작동하다 멈춰요. 공동구매로 산 것 같아요.']);
// 방금 들어온 요청(업체 링크로 '연락했어요' 시연)
mk(['at' => ago(1), 'item' => '중문', 'vendor' => V('중문 업체 B'), 'vc' => VC[0], 'dh' => ['104', '1103'], 'name' => '오○○', 'tel' => '01000002012',
  'body' => '중문 손잡이가 헐거워졌어요. 어제 업체에 문자 남겼는데 답이 없어요.', 'photos' => ['중문 손잡이']]);

db()->commit();
tick(true);
echo 'OK · 요청 ' . one('SELECT COUNT(*) c FROM ticket')['c'] . '건 · 업체 ' . one('SELECT COUNT(*) c FROM vendor')['c'] . '곳 · 문자 기록 ' . one('SELECT COUNT(*) c FROM sms_log')['c'] . "건\n";

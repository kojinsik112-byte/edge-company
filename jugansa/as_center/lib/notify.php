<?php
// 문자 문구(시연판과 같은 문구) · 누구에게 언제 보내는지
require_once __DIR__ . '/sms.php';

function brand() { return '[' . cfg('brand', '엣지컴퍼니') . ']'; }
function link_res($t) { return base_url() . '/?d=' . $t['dcode'] . '&k=' . $t['rtoken']; }
function link_ven($t) { return base_url() . '/v.php?t=' . $t['vtoken']; }
function link_adm($t) { return base_url() . '/admin.php#' . $t['no']; }
function admins_to_notify() { return all("SELECT phone FROM admin WHERE active=1 AND notify=1 AND phone<>''"); }
function to_admins($t, $msg, $kind) { foreach (admins_to_notify() as $a) sms($a['phone'], $msg, $kind, $t['id']); }
function vc_short($vc) { $i = array_search($vc, VC, true); return $i === false ? '' : VC_SHORT[$i]; }
function iv($t) { return $t['is_build'] ? '아파트 자체 하자' : $t['item'] . ' · ' . (t_known($t) ? $t['vend'] : '업체 확인 필요'); }

// 요청이 들어왔을 때: 입주민 · 업체(알 때만) · 주관사
function n_new($t) {
  $due = fmt_t(reply_due($t)); $k = t_known($t);
  sms($t['phone'], brand() . ' ' . $t['dname'] . ' ' . $t['dong'] . '-' . $t['ho'] . " 요청 접수\n접수번호 " . $t['no'] . "\n" . ($k ? '담당 업체' : '주관사 담당자') . '가 ' . $due . '까지 1차 연락드리' . ($k ? '고, 없으면 주관사가 직접 연락드립니다.' : '겠습니다.') . "\n진행 확인: " . link_res($t), 'res_new', $t['id']);
  if ($k) n_vendor($t);
  to_admins($t, '[A/S 요청] ' . $t['dname'] . ' ' . $t['no'] . "\n" . ($t['is_build'] ? '아파트 자체 하자 · 시공사 전달' : iv($t) . ($t['vc'] ? ' · ' . vc_short($t['vc']) : '')) . ($t['is_build'] || $k ? '' : "\n업체를 확인해 지정해 주세요.") . "\n" . link_adm($t), 'adm_new');
}
function n_vendor($t) {
  sms($t['vphone'], brand() . ' A/S 주관사 접수 ' . $t['no'] . "\n" . $t['dname'] . ' ' . $t['dong'] . '-' . $t['ho'] . ' · ' . $t['item'] . ($t['vc'] ? "\n입주민 사유: " . $t['vc'] : '') . "\n" . fmt_t(reply_due($t)) . "까지 고객에게 연락한 뒤 링크에서 '연락했어요'를 눌러 주세요. 기한 안에 표시가 없으면 주관사가 직접 연락합니다.\n" . link_ven($t), 'ven_new', $t['id']);
}
function n_visit($t) { sms($t['phone'], brand() . ' ' . $t['no'] . ' 방문 일정이 확정되었습니다: ' . $t['visit'] . "\n일정을 바꾸시려면 담당 업체에 전화해 주세요.", 'res_visit', $t['id']); }
function n_done($t) {
  $how = is_center($t) ? "\n주관사가 해피콜로 해결 여부를 확인드립니다. 화면에서도 알려 주실 수 있어요: " : "\n해결되었는지 눌러 주세요: ";
  sms($t['phone'], brand() . ' ' . $t['no'] . ' 처리 완료로 표시되었습니다.' . $how . link_res($t), 'res_done', $t['id']);
}
function n_reopen($t, $why) {
  if (t_known($t)) sms($t['vphone'], brand() . ' A/S ' . $t['no'] . " 입주민이 '아직 해결 안 됨'을 눌렀습니다.\n사유: " . $why . "\n" . fmt_t(visit_due($t)) . "까지 방문 일정을 다시 잡아 주세요.\n" . link_ven($t), 'ven_reopen', $t['id']);
  to_admins($t, '[A/S 다시 열림] ' . $t['dname'] . ' ' . $t['no'] . "\n사유: " . $why . "\n" . link_adm($t), 'adm_reopen');
}
function n_late($t, $d) {
  $what = (int)$t['st'] === 0 ? ($t['is_build'] ? '시공사 전달 · 1차 연락' : (t_known($t) ? '업체 1차 회신' : '1차 연락')) : '방문 일정 확정';
  to_admins($t, '[주관사 개입] ' . $t['dname'] . ' ' . $t['no'] . "\n" . $what . ' 기한(' . fmt_t($d) . ")이 지났습니다. 입주민에게 직접 연락해 주세요.\n" . link_adm($t), 'adm_late');
}
function n_remind($t, $d) { sms($t['vphone'], brand() . ' A/S ' . $t['no'] . ' 1차 회신 기한(' . fmt_t($d) . ")이 다가옵니다. 고객에게 연락하셨으면 링크에서 '연락했어요'를 눌러 주세요.\n" . link_ven($t), 'ven_remind', $t['id']); }
function n_fix($t, $label) { sms($t['phone'], brand() . ' ' . $t['no'] . " 앞서 보낸 '" . $label . "' 안내는 잘못 보낸 것입니다. 바뀐 내용은 다시 알려 드리겠습니다.", 'res_fix', $t['id']); }
// 업체 지정 · 바꾸기: 새 업체 · 입주민 · (바꿀 때) 이전 업체
function n_assign($t, $wasPhone) {
  n_vendor($t);
  if ($wasPhone) {
    sms($wasPhone, brand() . ' A/S ' . $t['no'] . ' 건은 다른 업체로 넘어갔습니다. 이 건의 링크는 닫힙니다.', 'ven_moved', $t['id']);
    sms($t['phone'], brand() . ' ' . $t['no'] . ' 담당 업체가 ' . $t['vend'] . '(으)로 바뀌었습니다. ' . fmt_t(reply_due($t)) . '까지 새 업체가 연락드립니다.', 'res_assign', $t['id']);
  } else {
    sms($t['phone'], brand() . ' ' . $t['no'] . ' 계약 업체를 확인했습니다: ' . $t['vend'] . '. ' . fmt_t(reply_due($t)) . '까지 업체가 연락드립니다.', 'res_assign', $t['id']);
  }
}

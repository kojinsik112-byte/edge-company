<?php
// 문자 보내기: 가비아 문자 API(90바이트 넘으면 장문). config의 sms.mode가 'gabia'가 아니면 실제로 보내지 않고 '문자 기록'에만 남긴다.
// 가비아 문서: https://message.gabia.com/api/documentation/ (토큰 = Basic SMS_ID:API_KEY · 발송 = Basic SMS_ID:ACCESS_TOKEN)

function euckr_len($s) { $n = 0; foreach (preg_split('//u', $s, -1, PREG_SPLIT_NO_EMPTY) as $ch) $n += strlen($ch) > 1 ? 2 : 1; return $n; }

function sms($to, $msg, $kind, $tid = null) {
  $to = digits($to);
  if (!preg_match('/^01[016789]\d{7,8}$/', $to)) return false;
  $c = cfg('sms', []);
  if (($c['mode'] ?? 'off') === 'gabia') { list($ok, $resp) = gabia_send($to, $msg, $c); }
  else { $ok = 0; $resp = '실제 발송 꺼짐(config sms.mode = off)'; }
  ins('sms_log', ['ticket_id' => $tid, 'at' => time(), 'phone' => tel_mask($to), 'kind' => $kind, 'msg' => $msg, 'ok' => $ok ? 1 : 0, 'resp' => mb_substr((string)$resp, 0, 290)]);
  return (bool)$ok;
}

function http_post($url, $fields, $auth) {
  if (!function_exists('curl_init')) return [0, 'curl 확장이 없습니다'];
  $ch = curl_init($url);
  curl_setopt_array($ch, [
    CURLOPT_POST => true, CURLOPT_POSTFIELDS => http_build_query($fields), CURLOPT_RETURNTRANSFER => true, CURLOPT_TIMEOUT => 10,
    CURLOPT_HTTPHEADER => ['Content-Type: application/x-www-form-urlencoded', 'Authorization: Basic ' . base64_encode($auth)],
  ]);
  $r = curl_exec($ch); $e = curl_error($ch); $code = curl_getinfo($ch, CURLINFO_HTTP_CODE); curl_close($ch);
  return [$r === false ? 0 : $code, $r === false ? $e : $r];
}

// 토큰은 1시간짜리라 data/에 두고 다시 씀
function gabia_token($c, $renew = false) {
  $f = DATA . '/sms_token.json';
  if (!$renew && is_file($f)) { $j = json_decode((string)file_get_contents($f), true); if ($j && $j['exp'] > time() + 60) return $j['tok']; }
  list(, $body) = http_post('https://sms.gabia.com/oauth/token', ['grant_type' => 'client_credentials'], $c['sms_id'] . ':' . $c['api_key']);
  $j = json_decode((string)$body, true);
  if (empty($j['access_token'])) return '';
  @file_put_contents($f, json_encode(['tok' => $j['access_token'], 'exp' => time() + (int)($j['expires_in'] ?? 3600)]));
  return $j['access_token'];
}

function gabia_send($to, $msg, $c) {
  for ($try = 0; $try < 2; $try++) {
    $tok = gabia_token($c, $try > 0);
    if (!$tok) return [0, '가비아 인증 실패(SMS ID · API Key 확인)'];
    $lms = euckr_len($msg) > 90;
    $f = ['phone' => $to, 'callback' => digits($c['callback']), 'message' => $msg, 'refkey' => 'asc' . date('ymdHis') . rnd(4)];
    if ($lms) $f['subject'] = $c['subject'] ?? '엣지컴퍼니 A/S';
    list($code, $body) = http_post('https://sms.gabia.com/api/send/' . ($lms ? 'lms' : 'sms'), $f, $c['sms_id'] . ':' . $tok);
    $j = json_decode((string)$body, true);
    if ($j && (string)($j['code'] ?? '') === '200') return [1, 'OK · 남은 건수 ' . ($j['data']['AFTER_SMS_QTY'] ?? '?')];
    if ($j && ($j['code'] ?? '') === 'token_verification_failed') continue;
    return [0, is_string($body) && $body !== '' ? $body : ('HTTP ' . $code)];
  }
  return [0, '토큰을 다시 받아도 실패'];
}

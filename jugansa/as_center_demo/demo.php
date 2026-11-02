<?php
// 시험판 시작 화면: 입주민 · 업체 · 관리 화면으로 바로 가는 링크와 시연 순서
require __DIR__ . '/lib/boot.php';
if (!installed()) { header('Content-Type: text/plain; charset=utf-8'); exit('시연 데이터가 없습니다. 시험판 폴더의 \'시연_시작.bat\'으로 열어 주세요.'); }
$dj = one("SELECT * FROM danji WHERE code='demo'");
$rows = $dj ? all(T_SEL . ' WHERE t.danji_id=? AND t.purged=0 ORDER BY t.id DESC', [$dj['id']]) : [];
$A = cfg('demo_admin', []);
$now = time();
function state($t, $now) {
  $d = next_due($t);
  if ($d && $d < $now) return ['주관사 개입', 'pl'];
  if (!$t['is_build'] && !$t['vendor_id']) return ['업체 확인 필요', 'p1'];
  if ((int)$t['st'] === 3) return [$t['confirm'] === null ? '입주민 확인 대기' : '마감', 'p3'];
  if ((int)$t['reopen'] && (int)$t['st'] < 3) return ['다시 열림 · ' . stage_name($t), 'p1'];
  return [stage_name($t), 'p' . (int)$t['st']];
}
?><!doctype html>
<html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>시험판 · 엣지컴퍼니 A/S 도움 창구</title><meta name="robots" content="noindex">
<link rel="stylesheet" href="assets/app.css?v=1"><link rel="stylesheet" href="assets/admin.css?v=1">
<style>
.go{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:12px;margin-top:12px}
.go a.card{display:block;text-decoration:none;color:inherit;border:1px solid var(--line);border-radius:14px;padding:16px;background:var(--paper)}
.go a.card:hover{border-color:var(--gold)}
.go .k{font-size:12px;color:var(--ink-2)}.go b{display:block;font-size:18px;margin:4px 0}
.acct{font-family:ui-monospace,Consolas,monospace;font-size:13px;margin-top:6px}
table.dm{width:100%;border-collapse:collapse;font-size:14px;margin-top:10px}
table.dm th,table.dm td{border-bottom:1px solid var(--hair);padding:8px 6px;text-align:left;vertical-align:top}
table.dm a{white-space:nowrap}
ol.flow{display:block;line-height:1.9;padding-left:20px;margin:8px 0 0}
.tag{display:inline-block;font-size:12px;border:1px solid var(--gold);color:var(--ink);border-radius:999px;padding:1px 10px;margin-left:6px}
</style></head><body>
<header class="hd"><div class="wrap"><div class="top" style="border-bottom:0"><div class="logo"><span class="mark">E</span><span class="wm"><b>엣지컴퍼니</b><span>A/S 도움 창구 · 시험판<span class="tag">내 PC에서만 · 문자는 실제로 보내지 않음</span></span></span></div></div></div></header>
<div class="wrap"><main>
  <div class="sec">
    <div class="h2"><span class="k">열기</span><b>세 화면으로 바로 가기</b></div>
    <div class="go">
      <a class="card" href="./?d=demo" target="_blank"><span class="k">입주민 · 안내문 QR로 들어오는 화면</span><b>입주민 화면</b><span class="k">업체 연락처 → 주관사에 요청 → 진행 확인</span></a>
      <a class="card" href="admin.php" target="_blank"><span class="k">주관사 담당자</span><b>관리 화면</b><span class="k">요청 관리 · 단지 · 업체 · 문자 기록 · 설정</span>
        <div class="acct">아이디 <?= h($A['login'] ?? '') ?> · 비밀번호 <?= h($A['pw'] ?? '') ?></div></a>
      <a class="card" href="#ven"><span class="k">업체 · 문자로 받는 링크</span><b>업체 화면</b><span class="k">아래 표의 '업체 화면'을 누르세요</span></a>
    </div>
  </div>

  <div class="sec" style="margin-top:14px">
    <div class="h2"><span class="k">순서</span><b>시연 순서(추천)</b></div>
    <ol class="flow">
      <li><b>입주민 화면</b> → '업체 연락처'에서 품목별 업체 · 전화 → '이 업체로 요청' → 4단계 요청(사진 · 방문 시간 '업체와 통화로 협의') → 접수증</li>
      <li><b>관리 화면</b> 로그인 → 방금 넣은 요청 · 빨간 줄(<b>주관사 개입</b>) · <b>업체 확인 필요</b> 건 → '자세히'에서 업체 지정 · 문자</li>
      <li>아래 표 맨 위(<b>방금 들어온 요청</b>)의 '업체 화면' → '고객에게 연락했어요' → 10분 안 '되돌리기'</li>
      <li><b>입주민 확인 대기</b> 건의 '입주민 화면' → '해결됐어요' + 업체 응대 평가(선택)</li>
      <li>관리 화면 '문자 기록' → 단계마다 누구에게 어떤 문자가 가는지(시험판은 기록만)</li>
    </ol>
    <p class="hint" style="margin-top:8px">'시연_시작.bat'을 다시 실행하면 시연 데이터가 지금 시각 기준으로 처음 상태로 돌아갑니다.</p>
  </div>

  <div class="sec" id="ven" style="margin-top:14px">
    <div class="h2"><span class="k">요청</span><b>시연용 요청 <?= count($rows) ?>건 · <?= h($dj['name'] ?? '') ?></b></div>
    <table class="dm"><thead><tr><th>접수번호</th><th>동 · 호</th><th>품목 · 업체</th><th>지금 상태</th><th>바로 가기</th></tr></thead><tbody>
    <?php foreach ($rows as $t): [$st, $pc] = state($t, $now); $known = t_known($t); ?>
      <tr><td class="mono"><?= h($t['no']) ?></td><td><?= h($t['dong'] . '-' . $t['ho']) ?></td>
        <td><?= h($t['is_build'] ? '아파트 자체 하자(시공사 전달)' : $t['item'] . ' · ' . ($known ? $t['vend'] : '업체 확인 필요')) ?></td>
        <td><span class="pill <?= h($pc) ?>"><?= h($st) ?></span></td>
        <td><?php if ($known): ?><a href="v.php?t=<?= h($t['vtoken']) ?>" target="_blank">업체 화면</a> · <?php endif; ?><a href="./?d=demo&amp;k=<?= h($t['rtoken']) ?>" target="_blank">입주민 화면</a></td></tr>
    <?php endforeach; ?>
    </tbody></table>
  </div>
</main></div>
</body></html>

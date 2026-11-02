<?php
// 바깥 크론(정해진 시각마다 이 주소를 불러 주는 서비스)용: cron.php?key=config의 cron_key
// 크론이 없어도 접수창 · 관리 페이지가 열릴 때마다 10분 간격으로 같은 점검이 돈다.
require __DIR__ . '/lib/boot.php';
header('Content-Type: text/plain; charset=utf-8');
$k = (string)cfg('cron_key', '');
if ($k === '' || !hash_equals($k, (string)($_GET['key'] ?? ''))) { http_response_code(403); exit('막힘'); }
if (!installed()) { http_response_code(503); exit('설치 전'); }
tick(true);
echo '점검 끝 ' . date('Y-m-d H:i:s');

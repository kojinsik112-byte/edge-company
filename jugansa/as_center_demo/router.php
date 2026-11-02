<?php
// PHP 내장 서버용(시험판): 가비아 .htaccess처럼 data · lib · 설정 · 시연 도구는 바깥에서 못 열게
$p = rawurldecode((string)parse_url($_SERVER['REQUEST_URI'] ?? '/', PHP_URL_PATH));
if (preg_match('#^/(data|lib)(/|$)#i', $p) || preg_match('#^/(config|seed_demo|router)\.php$#i', $p) || strpos($p, '/.') !== false) {
  http_response_code(403);
  header('Content-Type: text/plain; charset=utf-8');
  exit('막힘');
}
return false;

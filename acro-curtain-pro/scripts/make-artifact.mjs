// dist-artifact/index.html(완전한 문서) → Claude Artifact 본문 형식(head/body 태그 없는 조각)으로 변환
import { mkdirSync, readFileSync, writeFileSync, copyFileSync, existsSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const root = join(dirname(fileURLToPath(import.meta.url)), '..');
const src = readFileSync(join(root, 'dist-artifact', 'index.html'), 'utf8');

const styles = [...src.matchAll(/<style[^>]*>([\s\S]*?)<\/style>/g)].map((m) => m[1]);
const scripts = [...src.matchAll(/<script type="module"[^>]*>([\s\S]*?)<\/script>/g)].map((m) => m[1]);
if (!styles.length || !scripts.length) throw new Error('빌드 결과에서 style/script를 찾지 못했습니다.');

const out = `<title>ACRO CURTAIN PRO</title>
<meta name="claude:viewport-fit-sides" content="cover">
<meta name="description" content="커튼·블라인드 실측 및 원단 자동 산출 계산기">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500&family=IBM+Plex+Sans+KR:wght@400;500;600;700&family=Manrope:wght@500;600;700;800&display=swap">
<style>${styles.join('\n')}</style>
<div id="root"></div>
<div id="print-root"></div>
<script type="module">${scripts.join('\n')}</script>
`;

const outDir = join(root, 'release');
mkdirSync(outDir, { recursive: true });
writeFileSync(join(outDir, 'acro-curtain-pro.artifact.html'), out);
// PC·모바일 브라우저용 단일 파일도 함께 배치
const standalone = join(root, 'dist', 'index.html');
if (existsSync(standalone)) copyFileSync(standalone, join(outDir, 'ACRO_CURTAIN_PRO.html'));
console.log(`artifact: ${(out.length / 1024).toFixed(1)} KB → release/acro-curtain-pro.artifact.html`);

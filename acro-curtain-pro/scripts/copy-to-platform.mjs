// dist-web(웹 배포 빌드)를 엣지컴퍼니 홈페이지(edge-platform) public 폴더로 복사
// 사용: node scripts/copy-to-platform.mjs <edge-platform 폴더 경로>
// 결과: public/curtain-pro/{index.html, manifest, 아이콘} + public/curtain-pro-sw.js
//       → https://www.edgecompany.co.kr/curtain-pro (next.config.ts rewrites 필요)
import { copyFileSync, existsSync, mkdirSync, readdirSync } from 'node:fs';
import { dirname, join, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const root = join(dirname(fileURLToPath(import.meta.url)), '..');
const platform = resolve(process.argv[2] ?? join(root, '..', 'edge-platform'));
const src = join(root, 'dist-web');
if (!existsSync(join(src, 'index.html'))) throw new Error('dist-web 이 없습니다. 먼저 npm run build:web');
if (!existsSync(join(platform, 'next.config.ts'))) throw new Error(`edge-platform 폴더가 아닙니다: ${platform}`);

const dest = join(platform, 'public', 'curtain-pro');
mkdirSync(dest, { recursive: true });
for (const f of readdirSync(src)) {
  if (f === 'curtain-pro-sw.js') copyFileSync(join(src, f), join(platform, 'public', f));
  else copyFileSync(join(src, f), join(dest, f));
}
console.log(`복사 완료 → ${dest}`);

/// <reference types="vitest" />
import { defineConfig, type Plugin } from 'vite';
import react from '@vitejs/plugin-react';
import { viteSingleFile } from 'vite-plugin-singlefile';

// standalone(기본): 단일 HTML 파일 — PC 크롬에서 열어 인쇄·PDF·JSON 파일 저장까지 사용
// artifact: Claude Artifact 게시용 — 인쇄/다운로드 대신 미리보기·복사 방식
// web: www.edgecompany.co.kr/curtain-pro 배포용 — standalone + 홈 화면 추가(PWA)·오프라인·검색 제외
const WEB_HEAD = `
    <meta name="robots" content="noindex, nofollow" />
    <link rel="manifest" href="/curtain-pro/manifest.webmanifest" />
    <link rel="icon" type="image/png" href="/curtain-pro/icon-192.png" />
    <link rel="apple-touch-icon" href="/curtain-pro/apple-touch-icon.png" />
    <meta name="apple-mobile-web-app-capable" content="yes" />
    <meta name="mobile-web-app-capable" content="yes" />
    <meta name="apple-mobile-web-app-title" content="커튼계산기" />
    <meta name="apple-mobile-web-app-status-bar-style" content="default" />
`;

function webHead(): Plugin {
  return {
    name: 'acro-web-head',
    transformIndexHtml(html) {
      return html.replace('</head>', `${WEB_HEAD}  </head>`);
    },
  };
}

export default defineConfig(({ mode }) => {
  const target = mode === 'artifact' ? 'artifact' : mode === 'web' ? 'web' : 'standalone';
  return {
    plugins: [react(), viteSingleFile(), ...(target === 'web' ? [webHead()] : [])],
    define: {
      __TARGET__: JSON.stringify(target),
    },
    publicDir: target === 'web' ? 'pwa' : false,
    build: {
      outDir: target === 'artifact' ? 'dist-artifact' : target === 'web' ? 'dist-web' : 'dist',
      emptyOutDir: true,
      target: 'es2019',
    },
    test: {
      environment: 'node',
      include: ['src/**/*.test.ts'],
    },
  };
});

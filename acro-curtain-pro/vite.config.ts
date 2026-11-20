/// <reference types="vitest" />
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import { viteSingleFile } from 'vite-plugin-singlefile';

// standalone(기본): 단일 HTML 파일 — PC 크롬에서 열어 인쇄·PDF·JSON 파일 저장까지 사용
// artifact: Claude Artifact 게시용 — 인쇄/다운로드 대신 미리보기·복사 방식
export default defineConfig(({ mode }) => ({
  plugins: [react(), viteSingleFile()],
  define: {
    __TARGET__: JSON.stringify(mode === 'artifact' ? 'artifact' : 'standalone'),
  },
  build: {
    outDir: mode === 'artifact' ? 'dist-artifact' : 'dist',
    emptyOutDir: true,
    target: 'es2019',
  },
  test: {
    environment: 'node',
    include: ['src/**/*.test.ts'],
  },
}));

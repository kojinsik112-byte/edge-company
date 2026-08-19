import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // 상위 폴더에 다른 package-lock 이 있어 이 폴더를 워크스페이스 루트로 고정
  turbopack: { root: import.meta.dirname },
  images: {
    // Vercel 이미지 최적화 무료 한도 초과 시 402(OPTIMIZED_IMAGE_REQUEST_PAYMENT_REQUIRED)로
    // 사진이 통째로 안 뜨는 사고가 나므로 최적화를 끄고 원본을 그대로 서빙한다.
    // 업로드 단계(lib/upload.ts)에서 이미 webp로 변환·압축하므로 화질/용량 손해는 거의 없다.
    unoptimized: true,
    // 기본 비주얼이 로컬 SVG(일러스트)라 next/image 에서 SVG 서빙 허용 (스크립트 실행 차단 CSP 동봉)
    dangerouslyAllowSVG: true,
    contentSecurityPolicy: "default-src 'self'; script-src 'none'; sandbox;",
    // Supabase Storage 공개 이미지 허용 (프로젝트 도메인: *.supabase.co)
    remotePatterns: [
      { protocol: "https", hostname: "**.supabase.co" },
      { protocol: "https", hostname: "**.supabase.in" },
    ],
  },
};

export default nextConfig;

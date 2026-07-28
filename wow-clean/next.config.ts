import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // 상위 폴더에 다른 package-lock 이 있어 이 폴더를 워크스페이스 루트로 고정
  turbopack: { root: import.meta.dirname },
  images: {
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

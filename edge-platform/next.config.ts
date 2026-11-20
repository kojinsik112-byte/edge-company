import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // 상위 폴더에 다른 package-lock 이 있어 이 폴더를 워크스페이스 루트로 고정
  turbopack: { root: import.meta.dirname },
  images: {
    // Vercel 이미지 최적화(/_next/image)가 요금제 한도로 402 를 내며 모든 사진이 X 로 깨졌음(2026-09-21).
    // 업로드 시 이미 WebP·1600px 로 변환하므로 최적화 없이 원본 URL 을 그대로 서빙한다.
    unoptimized: true,
    // Supabase Storage 공개 이미지 허용 (프로젝트 도메인: *.supabase.co)
    remotePatterns: [
      { protocol: "https", hostname: "**.supabase.co" },
      { protocol: "https", hostname: "**.supabase.in" },
    ],
  },
};

export default nextConfig;

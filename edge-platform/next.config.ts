import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // 상위 폴더에 다른 package-lock 이 있어 이 폴더를 워크스페이스 루트로 고정
  turbopack: { root: import.meta.dirname },
  images: {
    // Vercel 이미지 최적화 무료 한도를 넘기면 /_next/image 가 402(OPTIMIZED_IMAGE_REQUEST_PAYMENT_REQUIRED)를
    // 뱉어 업로드한 사진이 통째로 안 보인다(와우클린 2026-08 사고와 동일 원인). 최적화를 끄고 원본을 그대로 서빙한다.
    // 업로드 단계(lib/upload.ts)에서 이미 최대 1600px·webp(q0.82)로 변환·압축하므로 화질/용량 손해는 사실상 없다.
    unoptimized: true,
    // Supabase Storage 공개 이미지 허용 (프로젝트 도메인: *.supabase.co)
    remotePatterns: [
      { protocol: "https", hostname: "**.supabase.co" },
      { protocol: "https", hostname: "**.supabase.in" },
    ],
  },
};

export default nextConfig;

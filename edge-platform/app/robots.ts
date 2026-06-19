import type { MetadataRoute } from "next";
import { SITE } from "@/lib/constants";

export default function robots(): MetadataRoute.Robots {
  const base = SITE.url.replace(/\/$/, "");
  return {
    rules: [
      // 네이버 / 다음 / 구글 등 모든 검색엔진 허용, 관리자만 차단
      { userAgent: "*", allow: "/", disallow: ["/admin", "/admin/"] },
      { userAgent: "Yeti", allow: "/" }, // 네이버 검색로봇
    ],
    sitemap: `${base}/sitemap.xml`,
    host: base,
  };
}

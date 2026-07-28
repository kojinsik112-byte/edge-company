import type { Metadata } from "next";
import "./globals.css";
import Header from "@/components/Header";
import Footer from "@/components/Footer";
import MobileBar from "@/components/MobileBar";
import RevealInit from "@/components/RevealInit";
import { SITE } from "@/lib/constants";
import { getSettings } from "@/lib/settings";

export const metadata: Metadata = {
  metadataBase: new URL(SITE.url),
  title: {
    default: "하수구막힘 변기막힘 배관청소 전국 24시간 출동 | 와우클린",
    template: "%s | 와우클린",
  },
  description:
    "와우클린은 하수구 막힘 뚫음, 변기막힘, 고압 배관청소, 누수탐지를 전문으로 하는 전국 24시간 출동 시공 기업입니다. 시공 전 투명 견적, 작업 후 A/S 보증.",
  keywords: [
    "하수구막힘", "변기막힘", "싱크대막힘", "하수구뚫음",
    "배관청소", "고압세척", "누수탐지", "관로탐지", "배관 내시경", "수전교체",
    "서울 하수구막힘", "부산 하수구막힘", "24시간 하수구", "와우클린",
  ],
  alternates: { canonical: "/" },
  openGraph: {
    type: "website",
    locale: "ko_KR",
    siteName: "와우클린",
    title: "하수구막힘·변기막힘·배관청소 전국 24시간 출동 | 와우클린",
    description: "막힌 곳은 뚫고, 깨끗함은 남깁니다. 시공 전 투명 견적, 작업 후 A/S 보증 — 와우클린.",
    images: ["/img/hero.svg"],
  },
  robots: { index: true, follow: true },
  ...(SITE.naverVerification
    ? { verification: { other: { "naver-site-verification": SITE.naverVerification } } }
    : {}),
};

export default async function RootLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  const { site, notice } = await getSettings();
  return (
    <html lang="ko" className="h-full antialiased">
      <body className="flex min-h-full flex-col pb-[56px] xl:pb-0">
        <RevealInit />
        <Header site={site} notice={notice} />
        <main className="flex-1">{children}</main>
        <Footer site={site} />
        <MobileBar site={site} />
      </body>
    </html>
  );
}

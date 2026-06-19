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
    default: "울산 양산 부산 경주 커튼 블라인드 전동커튼 전문 | 엣지리브커튼 울산본점",
    template: "%s | 엣지리브커튼",
  },
  description:
    "엣지리브커튼 울산본점은 울산·양산·부산·경주 지역 커튼, 블라인드, 전동커튼을 맞춤 제작·실측·시공하는 커튼·블라인드 전문 쇼룸입니다.",
  keywords: [
    "울산 커튼", "양산 커튼", "부산 커튼", "경주 커튼",
    "울산 블라인드", "양산 블라인드", "부산 블라인드", "울산 전동커튼",
    "울산 커튼 쇼룸", "암막커튼", "콤비블라인드", "우드블라인드",
    "커튼 맞춤제작", "커튼 실측", "전동커튼 설치", "허니콤 블라인드",
  ],
  alternates: { canonical: "/" },
  openGraph: {
    type: "website",
    locale: "ko_KR",
    siteName: "엣지리브커튼",
    title: "울산·양산·부산·경주 커튼·블라인드·전동커튼 전문 쇼룸 | 엣지리브커튼 울산본점",
    description: "공간의 분위기를 완성하는 커튼·블라인드. 직접 보고 고르는 울산 커튼 쇼룸, 엣지리브커튼 울산본점.",
    images: ["/img/living-hero.webp"],
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

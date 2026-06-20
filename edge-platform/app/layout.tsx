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
    default: "울산 부산 포항 경주 실링팬 간접조명 센서조명 전문 | 엣지컴퍼니",
    template: "%s | 엣지컴퍼니",
  },
  description:
    "엣지컴퍼니는 울산·부산·포항·경주 지역 실링팬, 간접조명, 센서조명, 전기공사를 전문으로 시공하는 프리미엄 조명 쇼룸입니다.",
  keywords: [
    "울산 실링팬", "부산 실링팬", "포항 실링팬", "경주 실링팬",
    "울산 간접조명", "부산 간접조명", "포항 간접조명", "경주 간접조명",
    "울산 조명 쇼룸", "부산 조명 시공", "포항 조명 시공", "경주 조명 시공",
    "아크로 실링팬", "ACRO 실링팬", "센서조명", "우물천장 간접조명",
  ],
  alternates: { canonical: "/" },
  openGraph: {
    type: "website",
    locale: "ko_KR",
    siteName: "엣지컴퍼니",
    title: "울산·부산·포항·경주 실링팬·간접조명·센서조명 전문 쇼룸 | 엣지컴퍼니",
    description: "빛과 바람으로 완성하는 프리미엄 공간. 직접 보고 비교하고 체험하는 조명 쇼룸, 엣지컴퍼니.",
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

import type { Metadata } from "next";
import { getSettings } from "@/lib/settings";
import ContactForm from "@/components/ContactForm";

export const metadata: Metadata = {
  title: "상담문의 · 쇼룸 예약 — 울산·부산·포항·경주",
  description: "엣지컴퍼니 실링팬·간접조명·스마트조명 상담 및 쇼룸 예약. 전화·문자·카카오톡·온라인으로 문의하세요.",
  alternates: { canonical: "/contact" },
};

export default async function ContactPage() {
  const { site } = await getSettings();
  const tel = `tel:${site.phone.replace(/-/g, "")}`;
  const kakao = site.kakao || `sms:${site.phone.replace(/-/g, "")}`;
  const mapUrl = `https://map.naver.com/p/search/${encodeURIComponent(site.address)}`;

  return (
    <div className="bg-navy-d text-white">
      <div className="mx-auto max-w-[760px] px-6 py-16">
        <div className="text-center">
          <p className="kicker text-gold">Contact</p>
          <h1 className="mt-4 text-2xl font-bold md:text-3xl">쇼룸 상담 예약</h1>
          <p className="mt-3 text-[14.5px] text-white/60">
            울산·부산·포항·경주 어디든 방문 상담 가능합니다.<br />아래 양식으로 남기시거나 전화·카톡으로 문의해 주세요.
          </p>
          <a href={tel} className="mt-8 block text-3xl font-bold tracking-tight md:text-4xl">{site.phone}</a>
          <div className="mx-auto mt-7 flex max-w-md flex-col gap-3 sm:flex-row sm:justify-center">
            <a href={tel} className="rounded-lg bg-gold px-6 py-3.5 text-[15px] font-bold text-ink">전화 상담</a>
            <a href={kakao} className="rounded-lg bg-white px-6 py-3.5 text-[15px] font-semibold text-navy">카톡·문자</a>
            <a href={mapUrl} target="_blank" rel="noopener noreferrer" className="rounded-lg border border-white/30 px-6 py-3.5 text-[15px] font-semibold text-white">길찾기</a>
          </div>
        </div>

        <div className="mt-10">
          <ContactForm />
        </div>

        <p className="mt-8 text-center text-[13px] text-white/50">대표번호 {site.phoneRep} · {site.address}</p>
      </div>
    </div>
  );
}

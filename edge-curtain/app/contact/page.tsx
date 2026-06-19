import type { Metadata } from "next";
import { getSettings } from "@/lib/settings";
import ContactForm from "@/components/ContactForm";

export const metadata: Metadata = {
  title: "상담문의 · 쇼룸 예약 — 울산·양산·부산·경주",
  description: "엣지리브커튼 커튼·블라인드·전동커튼 상담 및 쇼룸 예약. 전화·문자·카카오톡·온라인으로 문의하세요.",
  alternates: { canonical: "/contact" },
};

export default async function ContactPage() {
  const { site } = await getSettings();
  const tel = `tel:${site.phone.replace(/-/g, "")}`;
  const kakao = site.kakao || `sms:${site.phone.replace(/-/g, "")}`;
  const mapUrl = `https://map.naver.com/p/search/${encodeURIComponent(site.address)}`;

  return (
    <div className="bg-warm">
      <div className="mx-auto max-w-[760px] px-6 py-16 md:py-24">
        <div className="text-center">
          <p className="kicker">Contact</p>
          <h1 className="mt-4 text-[28px] font-extrabold text-ink md:text-[44px]">쇼룸 상담 예약</h1>
          <p className="mt-3 text-[14.5px] text-muted">
            울산·양산·부산·경주 어디든 방문 상담 가능합니다.<br />아래 양식으로 남기시거나 전화·카톡으로 문의해 주세요.
          </p>
          <a href={tel} className="mt-7 block text-[38px] font-extrabold tracking-tight text-navy md:text-[60px]">{site.phone}</a>
          <div className="mx-auto mt-7 flex max-w-md flex-col gap-3 sm:flex-row sm:justify-center">
            <a href={tel} className="rounded-lg bg-ink px-6 py-3.5 text-[15px] font-semibold text-white transition hover:bg-[#111827]">전화 상담</a>
            <a href={kakao} className="rounded-lg border border-gold bg-surface px-6 py-3.5 text-[15px] font-semibold text-ink transition hover:bg-bg">카톡·문자</a>
            <a href={mapUrl} target="_blank" rel="noopener noreferrer" className="rounded-lg border border-gold bg-surface px-6 py-3.5 text-[15px] font-semibold text-ink transition hover:bg-bg">길찾기</a>
          </div>
        </div>

        <div className="mt-10">
          <ContactForm />
        </div>

        <p className="mt-8 text-center text-[13px] text-muted">대표번호 {site.phoneRep} · {site.address}</p>
      </div>
    </div>
  );
}

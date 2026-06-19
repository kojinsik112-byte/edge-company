import type { Metadata } from "next";
import Image from "next/image";
import { getSettings } from "@/lib/settings";

export const metadata: Metadata = {
  title: "쇼룸안내 — 울산 커튼·블라인드 쇼룸 직접 체험",
  description: "울산 엣지리브커튼 쇼룸에서 커튼·블라인드·전동커튼 원단과 색상을 직접 보고 비교하세요. 양산·부산·경주 방문 상담 가능.",
  alternates: { canonical: "/showroom" },
};

export default async function ShowroomPage() {
  const { showroom, site } = await getSettings();
  const tel = `tel:${site.phone.replace(/-/g, "")}`;
  const mapUrl = `https://map.naver.com/p/search/${encodeURIComponent(site.address)}`;
  const mainImg = showroom.images?.[0] || showroom.image;

  return (
    <div className="mx-auto max-w-[1320px] px-6 py-14 md:py-20">
      <div className="grid items-center gap-10 md:grid-cols-2">
        <div className="relative aspect-[4/3] overflow-hidden rounded-[24px] bg-warm">
          {mainImg && <Image src={mainImg} alt="울산 엣지리브커튼 쇼룸" fill sizes="(max-width:768px) 100vw, 600px" className="object-cover" />}
        </div>
        <div>
          <p className="kicker">Showroom</p>
          <h1 className="mt-3 text-[26px] font-extrabold leading-snug text-ink md:text-[34px]">{showroom.title}</h1>
          <p className="mt-4 whitespace-pre-line text-[15px] leading-relaxed text-muted">{showroom.body}</p>
          <div className="mt-6 overflow-hidden rounded-2xl border border-line">
            {[
              ["위치", `${site.address} · 양산·부산·경주 방문 상담`],
              ["예약", showroom.hours],
              ["상담", `${site.phone} · 문자·카톡 남기시면 바로 연락드립니다`],
            ].map(([k, v], i) => (
              <div key={i} className="flex gap-4 border-b border-line bg-surface px-5 py-4 last:border-b-0">
                <span className="min-w-[44px] text-[12.5px] font-semibold text-gold-d">{k}</span>
                <span className="text-[13.5px] font-medium text-ink">{v}</span>
              </div>
            ))}
          </div>
          <div className="mt-6 flex flex-wrap gap-3">
            <a href={tel} className="rounded-lg bg-ink px-6 py-3.5 text-[15px] font-semibold text-white transition hover:bg-[#161b15]">전화 상담</a>
            <a href={mapUrl} target="_blank" rel="noopener noreferrer" className="rounded-lg border border-gold bg-surface px-6 py-3.5 text-[15px] font-semibold text-ink transition hover:bg-warm">네이버 지도 길찾기</a>
          </div>
        </div>
      </div>

      {/* 오시는 길 (지도 이미지 — 관리자 업로드) */}
      <div className="mt-14">
        <h2 className="mb-4 text-[18px] font-bold text-ink">오시는 길</h2>
        <div className="overflow-hidden rounded-2xl border border-line bg-warm">
          {showroom.map ? (
            // eslint-disable-next-line @next/next/no-img-element
            <img src={showroom.map} alt="엣지리브커튼 쇼룸 오시는 길 지도" className="w-full" />
          ) : (
            <div className="flex h-[280px] flex-col items-center justify-center gap-2 text-muted md:h-[360px]">
              <svg viewBox="0 0 24 24" className="h-8 w-8 text-gold" fill="none" stroke="currentColor" strokeWidth={1.5} strokeLinecap="round" strokeLinejoin="round"><path d="M12 21s7-6.2 7-11a7 7 0 0 0-14 0c0 4.8 7 11 7 11z" /><circle cx="12" cy="10" r="2.5" /></svg>
              <p className="text-[13px]">지도 이미지 자리 — 관리자 → 사이트설정 → 쇼룸에서 업로드</p>
            </div>
          )}
        </div>
        <p className="mt-3 flex flex-wrap items-center gap-3 text-[13px] text-muted">
          {site.address}
          <a href={mapUrl} target="_blank" rel="noopener noreferrer" className="font-semibold text-gold-d hover:text-gold">네이버 지도에서 보기 →</a>
        </p>
      </div>
    </div>
  );
}

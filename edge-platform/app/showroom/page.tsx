import type { Metadata } from "next";
import Image from "next/image";
import { getSettings } from "@/lib/settings";

export const metadata: Metadata = {
  title: "쇼룸안내 — 울산 조명 쇼룸 직접 체험",
  description: "울산 엣지컴퍼니 조명 쇼룸에서 실링팬·간접조명·스마트조명을 직접 보고 비교하고 체험하세요. 부산·포항·경주 방문 상담 가능.",
  alternates: { canonical: "/showroom" },
};

export default async function ShowroomPage() {
  const { showroom, site } = await getSettings();
  const tel = `tel:${site.phone.replace(/-/g, "")}`;
  const mapQuery = encodeURIComponent(site.address);
  const mapUrl = `https://map.naver.com/p/search/${mapQuery}`;
  const mainImg = showroom.images?.[0] || showroom.image;

  return (
    <div className="mx-auto max-w-[1320px] px-6 py-14 md:py-20">
      <div className="grid items-center gap-10 md:grid-cols-2">
        <div className="relative aspect-[4/3] overflow-hidden rounded-[24px] bg-warm">
          {mainImg && <Image src={mainImg} alt="울산 엣지컴퍼니 조명 쇼룸" fill sizes="(max-width:768px) 100vw, 600px" className="object-cover" />}
        </div>
        <div>
          <p className="kicker">Showroom</p>
          <h1 className="mt-3 text-[26px] font-extrabold leading-snug text-ink md:text-[34px]">{showroom.title}</h1>
          <p className="mt-4 whitespace-pre-line text-[15px] leading-relaxed text-muted">{showroom.body}</p>
          <div className="mt-6 overflow-hidden rounded-2xl border border-line">
            {[
              ["위치", `${site.address} · 부산·포항·경주 방문 상담`],
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
            <a href={tel} className="rounded-lg bg-ink px-6 py-3.5 text-[15px] font-semibold text-white transition hover:bg-[#111827]">전화 상담</a>
            <a href={mapUrl} target="_blank" rel="noopener noreferrer" className="rounded-lg border border-gold bg-surface px-6 py-3.5 text-[15px] font-semibold text-ink transition hover:bg-warm">네이버 지도 길찾기</a>
          </div>
        </div>
      </div>

      {/* 오시는 길 (지도) */}
      <div className="mt-14">
        <h2 className="mb-4 text-[18px] font-bold text-ink">오시는 길</h2>
        <div className="overflow-hidden rounded-2xl border border-line">
          <iframe
            title="엣지컴퍼니 쇼룸 위치"
            src={`https://maps.google.com/maps?q=${mapQuery}&hl=ko&z=16&output=embed`}
            className="h-[360px] w-full md:h-[440px]"
            loading="lazy"
            referrerPolicy="no-referrer-when-downgrade"
          />
        </div>
        <p className="mt-3 text-[13px] text-muted">{site.address}</p>
      </div>
    </div>
  );
}

import type { Metadata } from "next";
import Image from "next/image";
import { SITE } from "@/lib/constants";
import { FALLBACK_IMAGES } from "@/lib/types";

export const metadata: Metadata = {
  title: "쇼룸안내 — 울산 조명 쇼룸 직접 체험",
  description: "울산 엣지컴퍼니 조명 쇼룸에서 실링팬·간접조명·스마트조명을 직접 보고 비교하고 체험하세요. 부산·포항·경주 방문 상담 가능.",
  alternates: { canonical: "/showroom" },
};

const mapUrl = `https://map.naver.com/p/search/${encodeURIComponent(SITE.address)}`;

export default function ShowroomPage() {
  return (
    <div className="mx-auto max-w-[1180px] px-5 py-12 md:py-16">
      <div className="grid items-center gap-10 md:grid-cols-2">
        <div className="relative aspect-[4/3] overflow-hidden rounded-2xl bg-line">
          <Image src={FALLBACK_IMAGES.fan} alt="울산 엣지컴퍼니 조명 쇼룸" fill sizes="(max-width:768px) 100vw, 560px" className="object-cover" />
        </div>
        <div>
          <p className="kicker">Showroom</p>
          <h1 className="mt-3 text-2xl font-bold leading-snug text-ink md:text-[30px]">울산 조명 쇼룸에서<br />직접 체험하세요</h1>
          <p className="mt-4 text-[15px] leading-relaxed text-muted">
            실링팬의 바람과 소음, 간접조명의 색온도와 깊이는 사진만으로 알 수 없습니다. 실제로 켜 보고, 비교하고, 우리 집에 맞는 조합을 찾으실 수 있도록 쇼룸을 운영합니다.
          </p>
          <div className="mt-6 overflow-hidden rounded-2xl border border-line">
            {[
              ["위치", `${SITE.address} · 부산·포항·경주 방문 상담`],
              ["예약", "방문 전 연락 주시면 대기 없이 안내해 드립니다"],
              ["상담", `${SITE.phone} · 문자·카톡 남기시면 바로 연락드립니다`],
            ].map(([k, v], i) => (
              <div key={i} className="flex gap-4 border-b border-line bg-surface px-5 py-4 last:border-b-0">
                <span className="min-w-[44px] text-[12.5px] font-semibold text-gold-d">{k}</span>
                <span className="text-[13.5px] font-medium text-ink">{v}</span>
              </div>
            ))}
          </div>
          <div className="mt-6 flex flex-wrap gap-3">
            <a href={`tel:${SITE.phone.replace(/-/g, "")}`} className="rounded-lg bg-navy px-6 py-3.5 text-[15px] font-semibold text-white">전화 상담</a>
            <a href={mapUrl} target="_blank" rel="noopener noreferrer" className="rounded-lg bg-gold px-6 py-3.5 text-[15px] font-semibold text-navy">네이버 지도 길찾기</a>
          </div>
        </div>
      </div>
    </div>
  );
}

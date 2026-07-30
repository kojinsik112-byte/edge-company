import Image from "next/image";
import type { Partners } from "@/lib/settings";

// 엣지컴퍼니 협력사 소개 — 로고 3열 그리드(무제한, 9개 권장), 관리자에서 업로드
export default function PartnersSection({ partners }: { partners: Partners }) {
  const logos = (partners.logos ?? []).filter((l) => l.image);
  if (logos.length === 0) return null; // 로고가 없으면 섹션 숨김

  return (
    <section className="bg-bg py-16 md:py-24">
      <div className="reveal mx-auto max-w-[1080px] px-6">
        <div className="mx-auto mb-10 max-w-[640px] text-center">
          <p className="kicker">Partners</p>
          <h2 className="mt-3 text-[26px] font-extrabold text-ink md:text-[32px]">{partners.title}</h2>
          {partners.desc && <p className="mt-3 text-[16px] leading-relaxed text-muted">{partners.desc}</p>}
        </div>
        <div className="grid grid-cols-2 gap-4 sm:grid-cols-3">
          {logos.map((l, i) => (
            <div key={i} className="flex aspect-[3/2] items-center justify-center rounded-xl border border-line bg-surface p-6">
              <div className="relative h-full w-full">
                <Image src={l.image} alt={l.name || `협력사 ${i + 1}`} fill sizes="(max-width:640px) 50vw, 320px" className="object-contain" />
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}

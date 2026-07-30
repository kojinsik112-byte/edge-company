import Image from "next/image";
import type { License } from "@/lib/settings";

// 엣지컴퍼니 전기 면허 등록증 — 1열 2개(사진), 관리자에서 업로드
export default function LicenseSection({ license }: { license: License }) {
  const items = (license.items ?? []).filter((it) => it.image);
  if (items.length === 0) return null; // 면허증 사진이 없으면 섹션 숨김

  return (
    <section className="bg-bg py-16 md:py-24">
      <div className="reveal mx-auto max-w-[1080px] px-6">
        <div className="mx-auto mb-10 max-w-[640px] text-center">
          <p className="kicker">License</p>
          <h2 className="mt-3 text-[26px] font-display font-extrabold text-ink md:text-[32px]">{license.title}</h2>
          {license.desc && <p className="mt-3 text-[16px] leading-relaxed text-muted">{license.desc}</p>}
        </div>
        <div className="grid gap-6 sm:grid-cols-2">
          {items.map((it, i) => (
            <figure key={i} className="overflow-hidden rounded-2xl border border-line bg-surface shadow-[0_10px_30px_-20px_rgba(15,35,66,0.2)]">
              <div className="relative aspect-[3/4] bg-bg">
                <Image src={it.image} alt={it.caption || `엣지컴퍼니 등록증 ${i + 1}`} fill sizes="(max-width:640px) 100vw, 520px" className="object-contain" />
              </div>
              {it.caption && (
                <figcaption className="border-t border-line py-3 text-center text-[13.5px] font-semibold text-ink">{it.caption}</figcaption>
              )}
            </figure>
          ))}
        </div>
      </div>
    </section>
  );
}

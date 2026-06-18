import Image from "next/image";
import Link from "next/link";
import type { Showroom } from "@/lib/settings";

export default function ShowroomGallery({ showroom }: { showroom: Showroom }) {
  const images = (showroom.images?.length ? showroom.images : [showroom.image]).filter(Boolean).slice(0, 6);
  return (
    <section className="bg-warm py-16 md:py-24">
      <div className="mx-auto max-w-[1200px] px-6">
        <div className="mx-auto mb-12 max-w-[680px] text-center">
          <p className="kicker">Showroom</p>
          <h2 className="mt-3 text-[28px] font-extrabold leading-snug text-ink md:text-[40px]">{showroom.title}</h2>
          <p className="mt-3 whitespace-pre-line text-[15.5px] leading-relaxed text-muted">{showroom.body}</p>
        </div>

        <div className="grid grid-cols-2 gap-3 md:grid-cols-3 md:gap-4">
          {images.map((src, i) => (
            <div key={i} className="relative aspect-[4/3] overflow-hidden rounded-[20px] bg-surface">
              <Image src={src} alt={`엣지컴퍼니 쇼룸 ${i + 1}`} fill sizes="(max-width:768px) 50vw, 380px" className="object-cover transition duration-500 hover:scale-[1.04]" />
            </div>
          ))}

          {/* 마지막 칸: 쇼룸 안내 CTA 타일 (베이지) */}
          <Link href="/showroom" className="group flex aspect-[4/3] flex-col items-center justify-center gap-3.5 rounded-[20px] bg-[#dcc7ae] p-6 text-center text-ink transition hover:brightness-[0.97]">
            <span className="flex h-16 w-16 items-center justify-center rounded-full bg-white text-gold shadow-sm transition group-hover:scale-110">
              <svg viewBox="0 0 24 24" className="h-6 w-6" fill="none" stroke="currentColor" strokeWidth={1.9} strokeLinecap="round" strokeLinejoin="round"><path d="M5 12h14M13 6l6 6-6 6" /></svg>
            </span>
            <span className="text-[18px] font-extrabold">쇼룸 안내 보기</span>
            <span className="text-[12.5px] text-ink/60">울산 프리미엄 조명 쇼룸</span>
          </Link>
        </div>
      </div>
    </section>
  );
}

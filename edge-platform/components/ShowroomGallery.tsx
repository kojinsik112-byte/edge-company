import Image from "next/image";
import type { Showroom } from "@/lib/settings";

export default function ShowroomGallery({ showroom }: { showroom: Showroom }) {
  const images = (showroom.images?.length ? showroom.images : [showroom.image]).filter(Boolean).slice(0, 6);
  return (
    <section className="bg-surface py-16 md:py-24">
      <div className="mx-auto max-w-[1200px] px-6">
        <div className="mx-auto mb-12 max-w-[640px] text-center">
          <p className="kicker">Showroom</p>
          <h2 className="mt-3 text-[24px] font-bold leading-snug text-ink md:text-[30px]">{showroom.title}</h2>
          <p className="mt-3 whitespace-pre-line text-[15px] leading-relaxed text-muted">{showroom.body}</p>
        </div>
        <div className="grid grid-cols-2 gap-3 md:grid-cols-3 md:gap-4">
          {images.map((src, i) => (
            <div key={i} className={`relative overflow-hidden rounded-2xl bg-bg ${i === 0 ? "col-span-2 row-span-2 aspect-[4/3] md:aspect-auto" : "aspect-[4/3]"}`}>
              <Image src={src} alt={`엣지컴퍼니 쇼룸 ${i + 1}`} fill sizes="(max-width:768px) 50vw, 380px" className="object-cover transition duration-500 hover:scale-[1.04]" />
            </div>
          ))}
        </div>
        <div className="mt-10 text-center">
          <a href="/showroom" className="inline-block rounded-lg bg-navy px-7 py-3.5 text-[15px] font-bold text-white transition hover:bg-navy-d">
            쇼룸 안내 보기
          </a>
        </div>
      </div>
    </section>
  );
}

import Image from "next/image";
import type { Process } from "@/lib/settings";

export default function ProcessSection({ process }: { process: Process }) {
  const steps = process.steps?.length ? process.steps : [];
  return (
    <section className="bg-warm py-16 md:py-24">
      <div className="reveal mx-auto max-w-[1320px] px-6">
        <div className="mx-auto mb-12 max-w-[640px] text-center">
          <p className="kicker">Process</p>
          <h2 className="mt-3 text-[26px] font-extrabold text-ink md:text-[32px]">{process.title}</h2>
          <p className="mt-3 text-[14.5px] text-muted">{process.desc}</p>
        </div>
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-5">
          {steps.map((s, i) => (
            <div key={i} className="overflow-hidden rounded-2xl border border-line bg-surface transition hover:-translate-y-1 hover:shadow-[0_22px_45px_-26px_rgba(15,35,66,0.25)]">
              {s.image && (
                <div className="relative aspect-[4/3] overflow-hidden bg-bg">
                  <Image src={s.image} alt={`${s.title} 단계`} fill sizes="(max-width:768px) 100vw, 250px" className="object-cover" />
                  <span className="absolute left-3 top-3 rounded-full bg-navy/85 px-2.5 py-1 font-lux text-[13px] font-semibold text-white backdrop-blur-sm">{String(i + 1).padStart(2, "0")}</span>
                </div>
              )}
              <div className="p-6">
                {!s.image && <span className="font-lux text-[24px] font-semibold text-gold">{String(i + 1).padStart(2, "0")}</span>}
                <h3 className={`${s.image ? "" : "mt-3"} text-[16px] font-bold text-ink`}>{s.title}</h3>
                <p className="mt-2 text-[13px] leading-relaxed text-muted">{s.desc}</p>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}

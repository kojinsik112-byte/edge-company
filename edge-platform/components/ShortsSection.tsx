"use client";

import { useState } from "react";
import type { Shorts } from "@/lib/settings";
import ScrollRow from "./ScrollRow";

function ytId(url: string): string | null {
  const m = url.match(/(?:shorts\/|youtu\.be\/|[?&]v=)([A-Za-z0-9_-]{6,})/);
  return m ? m[1] : null;
}

export default function ShortsSection({ shorts }: { shorts: Shorts }) {
  const [play, setPlay] = useState<number | null>(null);
  const items = (shorts.items ?? []).filter((s) => s.url);
  if (!shorts.enabled) return null;
  const empty = items.length === 0;

  return (
    <section className="bg-bg py-16 md:py-24">
      <div className="reveal mx-auto mb-9 max-w-[640px] px-6 text-center">
        <p className="kicker">Shorts</p>
        <h2 className="mt-3 text-[26px] font-extrabold text-ink md:text-[32px]">{shorts.title}</h2>
        {shorts.desc && <p className="mt-3 text-[14.5px] text-muted">{shorts.desc}</p>}
      </div>
      <ScrollRow fade="var(--color-bg)">
        <div className="mx-auto flex w-max gap-4 px-6 pb-3">
          {empty
            ? [0, 1, 2, 3].map((i) => (
                <div key={i} className="relative aspect-[9/16] w-[224px] shrink-0 overflow-hidden rounded-2xl bg-gradient-to-b from-navy to-ink">
                  <span className="absolute inset-0 flex flex-col items-center justify-center gap-2 text-white/45">
                    <svg viewBox="0 0 24 24" className="h-9 w-9" fill="currentColor"><path d="M8 5v14l11-7z" /></svg>
                    <span className="text-[12px] font-semibold">곧 공개</span>
                  </span>
                </div>
              ))
            : items.map((s, i) => {
            const yt = ytId(s.url);
            const playing = play === i;
            const thumb = s.thumb || (yt ? `https://img.youtube.com/vi/${yt}/hqdefault.jpg` : "");
            return (
              <div key={i} className="relative aspect-[9/16] w-[224px] shrink-0 overflow-hidden rounded-2xl bg-ink shadow-[0_18px_40px_-22px_rgba(15,35,66,0.5)]">
                {playing ? (
                  yt ? (
                    <iframe src={`https://www.youtube.com/embed/${yt}?autoplay=1&rel=0`} title={s.title} className="h-full w-full" allow="autoplay; encrypted-media; fullscreen" allowFullScreen />
                  ) : (
                    <video src={s.url} autoPlay controls playsInline className="h-full w-full bg-black object-contain" />
                  )
                ) : (
                  <button onClick={() => setPlay(i)} className="group block h-full w-full text-left">
                    {thumb ? (
                      // eslint-disable-next-line @next/next/no-img-element
                      <img src={thumb} alt={s.title || "엣지컴퍼니 숏츠"} className="absolute inset-0 h-full w-full object-cover" />
                    ) : (
                      <span className="absolute inset-0 bg-gradient-to-b from-navy to-ink" />
                    )}
                    <span className="absolute inset-0 bg-gradient-to-t from-black/65 via-transparent to-black/10 transition group-hover:from-black/50" />
                    <span className="absolute left-1/2 top-1/2 flex h-15 w-15 -translate-x-1/2 -translate-y-1/2 items-center justify-center rounded-full bg-white/90 shadow-lg transition group-hover:scale-110" style={{ width: 60, height: 60 }}>
                      <svg viewBox="0 0 24 24" className="ml-0.5 h-6 w-6 text-ink" fill="currentColor"><path d="M8 5v14l11-7z" /></svg>
                    </span>
                    {s.title && <span className="absolute inset-x-0 bottom-0 line-clamp-2 px-4 pb-4 text-[14px] font-bold leading-snug text-white">{s.title}</span>}
                  </button>
                )}
              </div>
            );
          })}
        </div>
      </ScrollRow>
    </section>
  );
}

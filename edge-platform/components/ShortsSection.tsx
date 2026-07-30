"use client";

import Link from "next/link";
import { useState } from "react";
import type { Shorts } from "@/lib/settings";

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
        <h2 className="mt-3 text-[26px] font-display font-extrabold text-ink md:text-[32px]">{shorts.title}</h2>
        {shorts.desc && <p className="mt-3 text-[16px] leading-relaxed text-muted">{shorts.desc}</p>}
      </div>
      <div className="reveal mx-auto grid max-w-[1320px] grid-cols-2 gap-5 px-6 md:gap-6">
          {empty
            ? [0, 1, 2, 3].map((i) => (
                <div key={i} className="relative aspect-video overflow-hidden rounded-2xl bg-gradient-to-b from-navy to-ink">
                  <span className="absolute inset-0 flex flex-col items-center justify-center gap-2 text-white/45">
                    <svg viewBox="0 0 24 24" className="h-10 w-10" fill="currentColor"><path d="M8 5v14l11-7z" /></svg>
                    <span className="text-[12px] font-semibold">곧 공개</span>
                  </span>
                </div>
              ))
            : items.slice(0, 4).map((s, i) => {
                const yt = ytId(s.url);
                const isFile = /\.(mp4|mov|webm|m4v)(\?|$)/i.test(s.url);
                const isExternal = !yt && !isFile; // 인스타·틱톡 등 → 클릭 시 새 탭 이동
                const playing = play === i && !isExternal;
                const thumb = s.thumb || (yt ? `https://img.youtube.com/vi/${yt}/hqdefault.jpg` : "");
                const preview = (
                  <>
                    {thumb ? (
                      // eslint-disable-next-line @next/next/no-img-element
                      <img src={thumb} alt={s.title || "엣지컴퍼니 숏츠"} className="absolute inset-0 h-full w-full object-cover" />
                    ) : (
                      <span className="absolute inset-0 bg-gradient-to-b from-navy to-ink" />
                    )}
                    <span className="absolute inset-0 bg-gradient-to-t from-black/65 via-transparent to-black/10 transition group-hover:from-black/50" />
                    <span className="absolute left-1/2 top-1/2 flex -translate-x-1/2 -translate-y-1/2 items-center justify-center rounded-full bg-white/90 shadow-lg transition group-hover:scale-110" style={{ width: 60, height: 60 }}>
                      {isExternal ? (
                        <svg viewBox="0 0 24 24" className="h-6 w-6 text-ink" fill="none" stroke="currentColor" strokeWidth={2} strokeLinecap="round" strokeLinejoin="round"><path d="M7 17 17 7M9 7h8v8" /></svg>
                      ) : (
                        <svg viewBox="0 0 24 24" className="ml-0.5 h-6 w-6 text-ink" fill="currentColor"><path d="M8 5v14l11-7z" /></svg>
                      )}
                    </span>
                    {s.title && <span className="absolute inset-x-0 bottom-0 line-clamp-2 px-4 pb-4 text-[14px] font-bold leading-snug text-white">{s.title}</span>}
                  </>
                );
                return (
                  <div key={i} className="relative aspect-video overflow-hidden rounded-2xl bg-ink shadow-[0_18px_40px_-22px_rgba(15,35,66,0.5)]">
                    {playing ? (
                      yt ? (
                        <iframe src={`https://www.youtube.com/embed/${yt}?autoplay=1&rel=0`} title={s.title} className="h-full w-full" allow="autoplay; encrypted-media; fullscreen" allowFullScreen />
                      ) : (
                        <video src={s.url} autoPlay controls playsInline className="h-full w-full bg-black object-contain" />
                      )
                    ) : isExternal ? (
                      <a href={s.url} target="_blank" rel="noopener noreferrer" className="group block h-full w-full text-left">{preview}</a>
                    ) : (
                      <button onClick={() => setPlay(i)} className="group block h-full w-full text-left">{preview}</button>
                    )}
                  </div>
                );
              })}
      </div>
      <div className="mt-9 text-center">
        <Link href="/youtube" className="inline-block rounded-lg border border-line bg-surface px-7 py-3.5 text-[15px] font-semibold text-ink transition hover:border-gold">더 많은 영상 보기</Link>
      </div>
    </section>
  );
}

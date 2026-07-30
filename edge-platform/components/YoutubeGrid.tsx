"use client";

import { useState } from "react";
import type { YoutubeRow } from "@/lib/types";

export default function YoutubeGrid({ videos }: { videos: YoutubeRow[] }) {
  const [playing, setPlaying] = useState<string | null>(null);

  return (
    <div className="grid gap-5 sm:grid-cols-2 lg:grid-cols-3">
      {videos.map((v) => (
        <div key={v.id} className="overflow-hidden rounded-2xl border border-line bg-surface shadow-[0_10px_30px_-18px_rgba(47,37,28,0.2)]">
          <div className="relative aspect-video bg-ink">
            {playing === v.id ? (
              <iframe
                className="absolute inset-0 h-full w-full"
                src={`https://www.youtube.com/embed/${v.video_id}?autoplay=1&rel=0`}
                title={v.title}
                allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                allowFullScreen
              />
            ) : (
              <button onClick={() => setPlaying(v.id)} className="group absolute inset-0 h-full w-full" aria-label={`${v.title} 재생`}>
                {/* eslint-disable-next-line @next/next/no-img-element */}
                <img src={`https://i.ytimg.com/vi/${v.video_id}/hqdefault.jpg`} alt={v.title} className="h-full w-full object-cover transition duration-500 group-hover:scale-105" />
                <span className="absolute inset-0 bg-black/15 transition group-hover:bg-black/25" />
                <span className="absolute left-1/2 top-1/2 flex h-14 w-14 -translate-x-1/2 -translate-y-1/2 items-center justify-center rounded-full bg-white/95 shadow-lg transition group-hover:scale-110">
                  <svg viewBox="0 0 24 24" className="ml-0.5 h-6 w-6 fill-ink"><path d="M7 4.5v15l13-7.5z" /></svg>
                </span>
              </button>
            )}
          </div>
          <div className="p-4">
            <h3 className="line-clamp-2 text-[14px] font-semibold text-ink">{v.title}</h3>
            {v.views && <p className="mt-1 text-[12px] text-muted">조회수 {v.views}</p>}
          </div>
        </div>
      ))}
    </div>
  );
}

import type { Metadata } from "next";
import { getYoutube } from "@/lib/data";

export const metadata: Metadata = {
  title: "시공 영상 (유튜브) — 실링팬·간접조명 시공",
  description: "엣지컴퍼니 실링팬·간접조명·스마트조명 시공 영상 모음.",
  alternates: { canonical: "/youtube" },
};

export default async function YoutubePage() {
  const videos = await getYoutube();
  return (
    <div className="mx-auto max-w-[1180px] px-5 py-12 md:py-16">
      <p className="kicker">Youtube</p>
      <h1 className="mt-3 text-2xl font-bold text-ink md:text-3xl">시공 영상</h1>
      <p className="mt-3 text-[14.5px] text-muted">실링팬·간접조명 시공 과정을 영상으로 확인하세요.</p>

      {videos.length > 0 ? (
        <div className="mt-8 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {videos.map((v) => (
            <a key={v.id} href={`https://youtu.be/${v.video_id}`} target="_blank" rel="noopener noreferrer" className="group overflow-hidden rounded-2xl bg-surface shadow-[0_10px_30px_-18px_rgba(16,37,66,0.25)]">
              <div className="relative aspect-video overflow-hidden bg-line">
                {/* eslint-disable-next-line @next/next/no-img-element */}
                <img src={`https://i.ytimg.com/vi/${v.video_id}/hqdefault.jpg`} alt={v.title} className="h-full w-full object-cover transition duration-500 group-hover:scale-105" />
                <span className="absolute left-1/2 top-1/2 flex h-12 w-12 -translate-x-1/2 -translate-y-1/2 items-center justify-center rounded-full bg-white/90">
                  <svg viewBox="0 0 24 24" className="ml-0.5 h-5 w-5 fill-navy"><path d="M7 4.5v15l13-7.5z" /></svg>
                </span>
              </div>
              <div className="p-4">
                <h3 className="line-clamp-2 text-[14px] font-semibold text-ink">{v.title}</h3>
                {v.views && <p className="mt-1 text-[12px] text-muted">조회수 {v.views}</p>}
              </div>
            </a>
          ))}
        </div>
      ) : (
        <div className="mt-10 rounded-2xl border border-dashed border-line bg-bg py-20 text-center text-[14px] text-muted">
          등록된 영상이 아직 없습니다. 관리자에서 유튜브 링크를 추가하면 이곳에 노출됩니다.
        </div>
      )}
    </div>
  );
}

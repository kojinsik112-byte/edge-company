import Link from "next/link";
import YoutubeGrid from "@/components/YoutubeGrid";
import type { YoutubeRow } from "@/lib/types";

export default function YoutubeSection({ videos }: { videos: YoutubeRow[] }) {
  return (
    <section className="bg-surface py-16 md:py-24">
      <div className="reveal mx-auto max-w-[1320px] px-6">
        <div className="mx-auto mb-12 max-w-[640px] text-center">
          <p className="kicker">Youtube</p>
          <h2 className="mt-3 text-[26px] font-extrabold text-ink md:text-[32px]">시공 영상</h2>
          <p className="mt-3 text-[14.5px] text-muted">커튼·블라인드 시공 과정을 영상으로 확인하세요. 썸네일을 누르면 바로 재생됩니다.</p>
        </div>
        {videos.length > 0 ? (
          <>
            <YoutubeGrid videos={videos} />
            <div className="mt-10 text-center">
              <Link href="/youtube" className="inline-block rounded-lg border border-line bg-surface px-6 py-3 text-sm font-semibold text-ink transition hover:border-gold">영상 전체 보기</Link>
            </div>
          </>
        ) : (
          <div className="grid gap-5 sm:grid-cols-3">
            {[0, 1, 2].map((i) => (
              <div key={i} className="overflow-hidden rounded-2xl border border-dashed border-line bg-bg">
                <div className="flex aspect-video items-center justify-center text-muted">
                  <span className="flex h-14 w-14 items-center justify-center rounded-full bg-surface">
                    <svg viewBox="0 0 24 24" className="ml-0.5 h-6 w-6 fill-gold"><path d="M7 4.5v15l13-7.5z" /></svg>
                  </span>
                </div>
                <p className="px-4 py-3 text-center text-[13px] text-muted">유튜브 영상 준비 중</p>
              </div>
            ))}
          </div>
        )}
      </div>
    </section>
  );
}

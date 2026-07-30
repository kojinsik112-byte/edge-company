import type { Metadata } from "next";
import { getYoutube } from "@/lib/data";
import YoutubeGrid from "@/components/YoutubeGrid";

// 관리자에서 등록/수정한 CMS 콘텐츠가 즉시 반영되도록 항상 최신 렌더
export const dynamic = "force-dynamic";

export const metadata: Metadata = {
  title: "시공 영상 (유튜브) — 실링팬·간접조명 시공",
  description: "엣지컴퍼니 실링팬·간접조명·센서조명 시공 영상 모음.",
  alternates: { canonical: "/youtube" },
};

export default async function YoutubePage() {
  const videos = await getYoutube();
  return (
    <div className="mx-auto max-w-[1320px] px-6 py-12 md:py-16">
      <p className="kicker">Youtube</p>
      <h1 className="mt-3 text-2xl font-bold text-ink md:text-3xl">시공 영상</h1>
      <p className="mt-3 text-[14.5px] text-muted">실링팬·간접조명 시공 과정을 영상으로 확인하세요. 썸네일을 누르면 바로 재생됩니다.</p>

      {videos.length > 0 ? (
        <div className="mt-8">
          <YoutubeGrid videos={videos} />
        </div>
      ) : (
        <div className="mt-10 rounded-2xl border border-dashed border-line bg-bg py-20 text-center text-[14px] text-muted">
          등록된 영상이 아직 없습니다. 관리자에서 유튜브 링크를 추가하면 이곳에 노출됩니다.
        </div>
      )}
    </div>
  );
}

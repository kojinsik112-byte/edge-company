"use client";

/** 실시간 접수 현황 롤링 피드 — 동네·작업·상태가 흘러가는 마퀴 띠 */
const FEED: { time: string; who: string; job: string; status: "접수" | "출동중" | "시공완료" }[] = [
  { time: "방금", who: "화곡동 박○○님", job: "하수구 막힘", status: "접수" },
  { time: "4분 전", who: "영등포동 백○○님", job: "싱크대 막힘", status: "출동중" },
  { time: "11분 전", who: "신정동 이○○님", job: "하수구 막힘", status: "출동중" },
  { time: "23분 전", who: "문래동 오○○님", job: "하수구 배관청소", status: "시공완료" },
  { time: "31분 전", who: "목동 김○○님", job: "변기 막힘", status: "시공완료" },
  { time: "44분 전", who: "당산동 최○○님", job: "배관 고압세척", status: "시공완료" },
  { time: "58분 전", who: "성산동 정○○님", job: "변기 역류", status: "시공완료" },
  { time: "1시간 전", who: "상암동 조○○님", job: "싱크대 악취", status: "시공완료" },
  { time: "1시간 전", who: "합정동 윤○○님", job: "하수구 막힘", status: "시공완료" },
  { time: "2시간 전", who: "망원동 장○○님", job: "배관 내시경 진단", status: "시공완료" },
];

const BADGE: Record<string, string> = {
  접수: "bg-amber-400/15 text-amber-300 border-amber-400/30",
  출동중: "bg-sky-400/15 text-sky-300 border-sky-400/30",
  시공완료: "bg-emerald-400/15 text-emerald-300 border-emerald-400/30",
};

export default function LiveFeed() {
  const row = [...FEED, ...FEED]; // 무한 루프용 2배 복제
  return (
    <div className="border-y border-white/10 bg-navy-d py-3">
      <div className="mx-auto flex max-w-[1320px] items-center gap-4 px-6">
        <span className="inline-flex shrink-0 items-center gap-2 rounded-full bg-white/10 px-3.5 py-1.5 text-[12px] font-extrabold text-white">
          <span className="relative flex h-2 w-2">
            <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-red-400 opacity-75" />
            <span className="relative inline-flex h-2 w-2 rounded-full bg-red-500" />
          </span>
          실시간 접수 현황
        </span>
        <div className="relative flex-1 overflow-hidden [mask-image:linear-gradient(to_right,transparent,black_6%,black_94%,transparent)]">
          <div className="flex w-max animate-[marquee_38s_linear_infinite] gap-3 hover:[animation-play-state:paused]">
            {row.map((f, i) => (
              <span key={i} className="inline-flex shrink-0 items-center gap-2.5 rounded-full border border-white/10 bg-white/[0.06] py-1.5 pl-3.5 pr-2 text-[12.5px] text-white/80">
                <span className="font-medium text-white/50">{f.time}</span>
                <span className="font-semibold text-white">{f.who}</span>
                <span>{f.job}</span>
                <span className={`rounded-full border px-2.5 py-0.5 text-[11px] font-bold ${BADGE[f.status]}`}>{f.status}</span>
              </span>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { createClient } from "@/lib/supabase/client";

interface PopupRow {
  id: string;
  title: string;
  content: string | null;
  image: string | null;
  link: string | null;
  start_at: string | null;
  end_at: string | null;
}

// "24시간 보지 않기" — 체크하고 닫으면 지금부터 24시간 동안 해당 팝업 숨김
const HIDE_MS = 24 * 60 * 60 * 1000;
const hideKey = (id: string) => `popup_${id}_hide_until_ts`;

const isHidden = (id: string) => {
  try {
    const ts = Number(localStorage.getItem(hideKey(id)) || 0);
    return ts > Date.now();
  } catch {
    return false;
  }
};

const today = () => new Date().toISOString().slice(0, 10);

export default function Popup() {
  // 등록된 활성 팝업 전부 노출 (갯수 제한 없음 — 관리자에서 등록한 만큼)
  const [popups, setPopups] = useState<PopupRow[]>([]);

  useEffect(() => {
    (async () => {
      try {
        const supabase = createClient();
        const { data } = await supabase
          .from("popups")
          .select("id,title,content,image,link,start_at,end_at")
          .eq("enabled", true)
          .order("sort", { ascending: true });
        const t = today();
        const active = (data ?? []).filter((p: PopupRow) => {
          const okStart = !p.start_at || p.start_at <= t;
          const okEnd = !p.end_at || p.end_at >= t;
          return okStart && okEnd && !isHidden(p.id);
        });
        setPopups(active as PopupRow[]);
      } catch {
        /* 무시 */
      }
    })();
  }, []);

  if (popups.length === 0) return null;

  const closeOne = (id: string, dontShow24h: boolean) => {
    if (dontShow24h) {
      try {
        localStorage.setItem(hideKey(id), String(Date.now() + HIDE_MS));
      } catch {
        /* 무시 */
      }
    }
    setPopups((list) => list.filter((p) => p.id !== id));
  };

  return (
    // 바깥=스크롤, 안쪽=min-h-full 센터링 → 팝업이 여러 장이라 화면보다 커져도 위가 잘리지 않고 스크롤됨
    <div className="fixed inset-0 z-[100] overflow-y-auto bg-black/55" role="dialog" aria-modal="true">
      <div className="flex min-h-full flex-wrap items-center justify-center gap-5 px-5 py-10">
        {popups.map((p) => (
          <PopupCard key={p.id} popup={p} onClose={closeOne} />
        ))}
      </div>
    </div>
  );
}

// 팝업 카드 1장 — A4 세로 절반(≈A5) 크기.
// 이미지 팝업은 이미지 비율이 제각각이어도 카드가 전부 '같은 사이즈'로 뜨도록
// 이미지 영역을 A4 세로 비율(210:297)로 고정하고 넘치는 부분은 크롭(object-cover)한다.
function PopupCard({ popup, onClose }: { popup: PopupRow; onClose: (id: string, dont: boolean) => void }) {
  const [dont, setDont] = useState(false);
  const close = () => onClose(popup.id, dont);

  // 이미지 원본 비율 그대로, 카드에 꽉 차게 표시 (여백·크롭 없음 — 카드 높이가 이미지에 딱 맞춰짐)
  const img = popup.image && (
    // eslint-disable-next-line @next/next/no-img-element
    <img src={popup.image} alt={popup.title} className="block h-auto w-full" />
  );

  return (
    <div className="flex max-h-[88vh] w-[min(88vw,400px)] shrink-0 flex-col overflow-hidden rounded-2xl bg-surface shadow-2xl">
      {popup.image ? (
        <>
          {/* 이미지 영역: 원본 비율 유지, 화면보다 길면 안쪽 스크롤 */}
          <div className="min-h-0 flex-1 overflow-y-auto">
            {popup.link ? (
              <Link href={popup.link} onClick={close} className="block">{img}</Link>
            ) : (
              // 링크 없는 이미지 팝업: 클릭하면 그냥 닫힘 (깨진 # 이동 방지)
              <div className="cursor-pointer" onClick={close}>{img}</div>
            )}
          </div>
          {/* 제목 줄: 링크 유무와 관계없이 같은 높이 (사이즈 통일) */}
          {(popup.title || popup.link) && (
            <div className="flex h-12 shrink-0 items-center justify-between gap-3 px-4">
              <p className="truncate text-[14.5px] font-bold text-ink">{popup.title}</p>
              {popup.link && (
                <Link href={popup.link} onClick={close} className="shrink-0 rounded-md bg-ink px-3 py-1.5 text-[12.5px] font-semibold text-white">
                  자세히 보기
                </Link>
              )}
            </div>
          )}
        </>
      ) : (
        /* 텍스트(공지형) 팝업: 내용 길이에 맞게 표시 */
        <div className="min-h-0 flex-1 overflow-y-auto p-5">
          {popup.title && <p className="text-[16px] font-bold text-ink">{popup.title}</p>}
          {popup.content && (
            <p className={`${popup.title ? "mt-2" : ""} whitespace-pre-wrap text-[13.5px] leading-relaxed text-ink/80`}>{popup.content}</p>
          )}
          {popup.link && (
            <Link href={popup.link} onClick={close} className="mt-4 block rounded-lg bg-ink py-2.5 text-center text-[13.5px] font-semibold text-white">
              자세히 보기
            </Link>
          )}
        </div>
      )}
      <div className="flex shrink-0 items-center justify-between border-t border-line px-4 py-2.5">
        <label className="flex cursor-pointer items-center gap-2 text-[12.5px] text-muted">
          <input type="checkbox" checked={dont} onChange={(e) => setDont(e.target.checked)} className="h-4 w-4" />
          24시간 동안 보지 않기
        </label>
        <button onClick={close} className="text-[13px] font-semibold text-ink">닫기 ✕</button>
      </div>
    </div>
  );
}

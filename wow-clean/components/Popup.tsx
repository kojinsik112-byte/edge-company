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

const today = () => new Date().toISOString().slice(0, 10);

export default function Popup() {
  const [popup, setPopup] = useState<PopupRow | null>(null);
  const [dontToday, setDontToday] = useState(false);

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
        const active = (data ?? []).find((p: PopupRow) => {
          const okStart = !p.start_at || p.start_at <= t;
          const okEnd = !p.end_at || p.end_at >= t;
          const hidden = localStorage.getItem(`popup_${p.id}_until`) === t;
          return okStart && okEnd && !hidden;
        });
        if (active) setPopup(active as PopupRow);
      } catch {
        /* 무시 */
      }
    })();
  }, []);

  if (!popup) return null;

  const close = () => {
    if (dontToday) localStorage.setItem(`popup_${popup.id}_until`, today());
    setPopup(null);
  };

  return (
    <div className="fixed inset-0 z-[100] flex items-center justify-center bg-black/55 px-5" role="dialog" aria-modal="true">
      <div className="max-h-[88vh] w-full max-w-md overflow-y-auto overflow-hidden rounded-2xl bg-surface shadow-2xl">
        {popup.image && (
          popup.link ? (
            <Link href={popup.link} onClick={close}>
              {/* eslint-disable-next-line @next/next/no-img-element */}
              <img src={popup.image} alt={popup.title} className="w-full" />
            </Link>
          ) : (
            // 링크 없는 이미지 팝업: 클릭하면 그냥 닫힘 (깨진 # 이동 방지)
            // eslint-disable-next-line @next/next/no-img-element
            <img src={popup.image} alt={popup.title} className="w-full cursor-pointer" onClick={close} />
          )
        )}
        {(popup.title || popup.content || popup.link) && (
          <div className="p-6">
            {popup.title && <p className="text-[17px] font-bold text-ink">{popup.title}</p>}
            {popup.content && <p className={`${popup.title ? "mt-2" : ""} whitespace-pre-wrap text-[14px] leading-relaxed text-ink/80`}>{popup.content}</p>}
            {popup.link && (
              <Link href={popup.link} onClick={close} className="mt-4 block rounded-lg bg-ink py-3 text-center text-[14px] font-semibold text-white">
                자세히 보기
              </Link>
            )}
          </div>
        )}
        <div className="flex items-center justify-between border-t border-line px-6 py-3">
          <label className="flex cursor-pointer items-center gap-2 text-[13px] text-muted">
            <input type="checkbox" checked={dontToday} onChange={(e) => setDontToday(e.target.checked)} className="h-4 w-4" />
            오늘 하루 보지 않기
          </label>
          <button onClick={close} className="text-[13px] font-semibold text-ink">닫기 ✕</button>
        </div>
      </div>
    </div>
  );
}

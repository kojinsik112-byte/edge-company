"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { createClient } from "@/lib/supabase/client";

interface PopupRow {
  id: string;
  title: string;
  image: string | null;
  link: string | null;
  start_at: string | null;
  end_at: string | null;
}

export default function Popup() {
  const [popup, setPopup] = useState<PopupRow | null>(null);

  useEffect(() => {
    (async () => {
      try {
        const supabase = createClient();
        const { data } = await supabase
          .from("popups")
          .select("id,title,image,link,start_at,end_at")
          .eq("enabled", true)
          .order("sort", { ascending: true });
        const today = new Date().toISOString().slice(0, 10);
        const active = (data ?? []).find((p: PopupRow) => {
          const okStart = !p.start_at || p.start_at <= today;
          const okEnd = !p.end_at || p.end_at >= today;
          return okStart && okEnd;
        });
        if (active && sessionStorage.getItem(`popup_${active.id}`) !== "1") {
          setPopup(active as PopupRow);
        }
      } catch {
        /* 무시 */
      }
    })();
  }, []);

  if (!popup) return null;

  const close = () => {
    sessionStorage.setItem(`popup_${popup.id}`, "1");
    setPopup(null);
  };

  return (
    <div className="fixed inset-0 z-[100] flex items-center justify-center bg-black/60 px-5" role="dialog" aria-modal="true">
      <div className="w-full max-w-sm overflow-hidden rounded-2xl bg-surface shadow-2xl">
        {popup.image && (
          <Link href={popup.link || "#"} onClick={close}>
            {/* eslint-disable-next-line @next/next/no-img-element */}
            <img src={popup.image} alt={popup.title} className="w-full" />
          </Link>
        )}
        <div className="p-5">
          {popup.title && <p className="text-[15px] font-bold text-ink">{popup.title}</p>}
          <div className="mt-4 flex gap-2">
            {popup.link && (
              <Link href={popup.link} onClick={close} className="flex-1 rounded-lg bg-navy py-2.5 text-center text-[14px] font-semibold text-white">
                자세히 보기
              </Link>
            )}
            <button onClick={close} className="flex-1 rounded-lg border border-line py-2.5 text-[14px] font-semibold text-ink">
              닫기
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

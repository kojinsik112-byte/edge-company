import Image from "next/image";
import type { Branches } from "@/lib/settings";

// 엣지컴퍼니 전국 지사 — 표 + 지도 이미지(이미지+텍스트), 관리자에서 편집
export default function BranchesSection({ branches }: { branches: Branches }) {
  const rows = branches.rows ?? [];
  if (rows.length === 0 && !branches.mapImage) return null;

  return (
    <section className="bg-surface py-16 md:py-24">
      <div className="reveal mx-auto max-w-[1080px] px-6">
        <div className="mx-auto mb-10 max-w-[640px] text-center">
          <p className="kicker">Branches</p>
          <h2 className="mt-3 text-[26px] font-extrabold text-ink md:text-[32px]">{branches.title}</h2>
          {branches.desc && <p className="mt-3 text-[14.5px] text-muted">{branches.desc}</p>}
        </div>

        <div className="grid gap-8 md:grid-cols-2 md:items-center">
          {branches.mapImage && (
            <div className="relative aspect-[4/3] overflow-hidden rounded-2xl border border-line bg-bg">
              <Image src={branches.mapImage} alt="엣지컴퍼니 전국 지사 지도" fill sizes="(max-width:768px) 100vw, 520px" className="object-contain" />
            </div>
          )}
          {rows.length > 0 && (
            <div className={`overflow-hidden rounded-2xl border border-line ${branches.mapImage ? "" : "md:col-span-2"}`}>
              <table className="w-full border-collapse text-left text-[14px]">
                <thead>
                  <tr className="bg-bg">
                    <th className="px-4 py-3 font-bold text-ink">지사</th>
                    <th className="px-4 py-3 font-bold text-ink">담당 지역</th>
                    <th className="px-4 py-3 font-bold text-ink">연락처</th>
                  </tr>
                </thead>
                <tbody>
                  {rows.map((b, i) => (
                    <tr key={i} className="border-t border-line bg-surface">
                      <td className="px-4 py-3 font-semibold text-ink">{b.name}</td>
                      <td className="px-4 py-3 text-muted">{b.area}</td>
                      <td className="px-4 py-3 text-muted">{b.phone}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>
    </section>
  );
}

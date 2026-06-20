import Link from "next/link";
import { requireAdmin } from "@/lib/admin";
import { createClient } from "@/lib/supabase/server";
import { LogoutButton } from "@/components/admin/AdminButtons";

export const dynamic = "force-dynamic";

async function count(table: string) {
  const supabase = await createClient();
  if (!supabase) return 0;
  try {
    const { count } = await supabase.from(table).select("*", { count: "exact", head: true });
    return count ?? 0;
  } catch {
    return 0;
  }
}

export default async function AdminDashboard() {
  const { user } = await requireAdmin();
  const supabase = await createClient();
  let newInquiries = 0;
  if (supabase) {
    try {
      const { count } = await supabase.from("inquiries").select("*", { count: "exact", head: true }).eq("status", "신규");
      newInquiries = count ?? 0;
    } catch {}
  }
  const [cases, reviews, faqs, videos, popups, products] = await Promise.all([
    count("cases"), count("reviews"), count("faq"), count("youtube"), count("popups"), count("products"),
  ]);

  const cards = [
    { href: "/admin/settings", title: "사이트 설정", desc: "배너·회사·쇼룸·면허 등록증·전국 지사·협력사·카테고리·공지바·SEO", badge: "" },
    { href: "/admin/cases", title: "시공사례", desc: "등록·수정·삭제", badge: `${cases}건` },
    { href: "/admin/products", title: "제품 소개", desc: "유선스위치·실링팬·COB조명 등", badge: `${products}건` },
    { href: "/admin/reviews", title: "고객후기", desc: "별점·후기·사진 관리", badge: `${reviews}건` },
    { href: "/admin/inquiries", title: "상담문의", desc: "접수 확인·상태·엑셀", badge: newInquiries ? `신규 ${newInquiries}` : "" },
    { href: "/admin/popups", title: "팝업 관리", desc: "이벤트/공지 팝업·기간", badge: `${popups}건` },
    { href: "/admin/faq", title: "FAQ", desc: "자주 묻는 질문", badge: `${faqs}건` },
    { href: "/admin/youtube", title: "유튜브", desc: "영상 링크 노출", badge: `${videos}건` },
  ];

  return (
    <div className="mx-auto max-w-[1000px] px-5 py-8">
      <header className="mb-8 flex items-center justify-between">
        <div>
          <h1 className="text-xl font-extrabold text-ink">엣지컴퍼니 관리자</h1>
          <p className="mt-1 text-[12.5px] text-muted">{user?.email}</p>
        </div>
        <div className="flex items-center gap-4">
          <Link href="/" target="_blank" className="text-[13px] font-semibold text-muted hover:text-navy">사이트 보기</Link>
          <LogoutButton />
        </div>
      </header>

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {cards.map((c) => (
          <Link key={c.href} href={c.href} className="group rounded-2xl border border-line bg-surface p-6 transition hover:border-navy hover:shadow-[0_18px_40px_-24px_rgba(11,31,58,0.4)]">
            <div className="flex items-start justify-between">
              <h2 className="text-[16px] font-bold text-ink group-hover:text-navy">{c.title}</h2>
              {c.badge && <span className="rounded-full bg-gold/15 px-2.5 py-1 text-[11px] font-bold text-gold-d">{c.badge}</span>}
            </div>
            <p className="mt-2 text-[13px] leading-relaxed text-muted">{c.desc}</p>
          </Link>
        ))}
      </div>
    </div>
  );
}

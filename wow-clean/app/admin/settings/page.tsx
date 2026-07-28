import Link from "next/link";
import { requireAdmin } from "@/lib/admin";
import { getSettings } from "@/lib/settings";
import SettingsForm from "@/components/admin/SettingsForm";

export const dynamic = "force-dynamic";

export default async function AdminSettings() {
  await requireAdmin();
  const settings = await getSettings();
  return (
    <div className="mx-auto max-w-[760px] px-5 py-8">
      <Link href="/admin" className="text-[13px] text-muted hover:text-navy">← 대시보드</Link>
      <h1 className="mb-2 mt-3 text-xl font-extrabold text-ink">사이트 설정</h1>
      <p className="mb-7 text-[13px] text-muted">배너·회사소개·시공현장·카테고리 이미지, 기본 정보, 공지바, SEO를 수정합니다. 저장 즉시 사이트에 반영됩니다.</p>
      <SettingsForm initial={settings} />
    </div>
  );
}

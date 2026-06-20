"use client";

import { useMemo, useState } from "react";
import { useRouter } from "next/navigation";
import { createClient } from "@/lib/supabase/client";
import { uploadImage } from "@/lib/upload";
import { CATEGORIES } from "@/lib/constants";
import type { Settings } from "@/lib/settings";

export default function SettingsForm({ initial }: { initial: Settings }) {
  const router = useRouter();
  const supabase = useMemo(() => createClient(), []);
  const [s, setS] = useState<Settings>(initial);
  const [saving, setSaving] = useState<string>("");
  const [msg, setMsg] = useState("");

  function patch<K extends keyof Settings>(key: K, val: Partial<Settings[K]>) {
    setS((prev) => ({ ...prev, [key]: { ...prev[key], ...val } }));
  }

  // 배열형 섹션 편집 헬퍼 (면허증·전국지사·협력사)
  const setLicenseItem = (i: number, p: Partial<Settings["license"]["items"][number]>) =>
    patch("license", { items: s.license.items.map((it, j) => (j === i ? { ...it, ...p } : it)) });
  const setBranch = (i: number, p: Partial<Settings["branches"]["rows"][number]>) =>
    patch("branches", { rows: s.branches.rows.map((b, j) => (j === i ? { ...b, ...p } : b)) });
  const addBranch = () => patch("branches", { rows: [...s.branches.rows, { name: "", area: "", phone: "" }] });
  const delBranch = (i: number) => patch("branches", { rows: s.branches.rows.filter((_, j) => j !== i) });
  const setLogo = (i: number, p: Partial<Settings["partners"]["logos"][number]>) =>
    patch("partners", { logos: s.partners.logos.map((l, j) => (j === i ? { ...l, ...p } : l)) });
  const addLogo = () => patch("partners", { logos: [...s.partners.logos, { image: "", name: "" }] });
  const delLogo = (i: number) => patch("partners", { logos: s.partners.logos.filter((_, j) => j !== i) });

  async function save(key: keyof Settings) {
    setSaving(key);
    setMsg("");
    const { error } = await supabase
      .from("settings")
      .upsert({ key, value: s[key], updated_at: new Date().toISOString() });
    setSaving("");
    if (error) setMsg(`오류: ${error.message}`);
    else {
      setMsg(`'${LABEL[key]}' 저장 완료 — 사이트에 반영됩니다.`);
      router.refresh();
    }
  }

  async function pick(file: File | undefined, set: (url: string) => void) {
    if (!file) return;
    setMsg("이미지 변환·업로드 중…");
    try {
      const url = await uploadImage(supabase, file);
      set(url);
      setMsg("이미지 업로드 완료 — 저장 버튼을 누르세요.");
    } catch (e) {
      setMsg(`이미지 오류: ${e instanceof Error ? e.message : ""}`);
    }
  }

  async function addShowroomImages(files: FileList) {
    setMsg("이미지 변환·업로드 중…");
    try {
      const urls: string[] = [];
      for (const f of Array.from(files)) urls.push(await uploadImage(supabase, f));
      patch("showroom", { images: [...(s.showroom.images ?? []), ...urls] });
      setMsg("업로드 완료 — 저장 버튼을 누르세요.");
    } catch (e) {
      setMsg(`이미지 오류: ${e instanceof Error ? e.message : ""}`);
    }
  }

  return (
    <div className="space-y-10">
      {msg && <p className="sticky top-2 z-10 rounded-lg bg-gold/15 px-4 py-2.5 text-[13px] font-medium text-gold-d">{msg}</p>}

      {/* 기본 정보 */}
      <Section title="기본 정보" onSave={() => save("site")} saving={saving === "site"}>
        <Grid>
          <Field label="대표 상담 전화"><Inp value={s.site.phone} onChange={(v) => patch("site", { phone: v })} /></Field>
          <Field label="대표번호"><Inp value={s.site.phoneRep} onChange={(v) => patch("site", { phoneRep: v })} /></Field>
        </Grid>
        <Field label="주소"><Inp value={s.site.address} onChange={(v) => patch("site", { address: v })} /></Field>
        <p className="pt-1 text-[12px] font-bold text-gold-d">SNS · 채널 링크 (주소 입력 시 버튼/아이콘 자동 노출)</p>
        <Grid>
          <Field label="인스타그램 주소"><Inp value={s.site.instagram} onChange={(v) => patch("site", { instagram: v })} placeholder="https://instagram.com/..." /></Field>
          <Field label="유튜브 주소"><Inp value={s.site.youtube} onChange={(v) => patch("site", { youtube: v })} placeholder="https://youtube.com/@..." /></Field>
          <Field label="네이버 블로그 주소"><Inp value={s.site.blog} onChange={(v) => patch("site", { blog: v })} placeholder="https://blog.naver.com/..." /></Field>
          <Field label="카카오톡 채널 링크"><Inp value={s.site.kakao} onChange={(v) => patch("site", { kakao: v })} placeholder="https://pf.kakao.com/_xxxx/chat (카톡 상담 버튼 연결)" /></Field>
        </Grid>
        <Grid>
          <Field label="상호"><Inp value={s.site.bizName} onChange={(v) => patch("site", { bizName: v })} /></Field>
          <Field label="대표자"><Inp value={s.site.ceo} onChange={(v) => patch("site", { ceo: v })} /></Field>
          <Field label="사업자등록번호"><Inp value={s.site.bizNo} onChange={(v) => patch("site", { bizNo: v })} /></Field>
        </Grid>
      </Section>

      {/* 공지바 */}
      <Section title="상단 공지바" onSave={() => save("notice")} saving={saving === "notice"}>
        <Check checked={s.notice.enabled} onChange={(v) => patch("notice", { enabled: v })} label="공지바 노출 ON" />
        <Field label="문구"><Inp value={s.notice.text} onChange={(v) => patch("notice", { text: v })} /></Field>
        <Field label="링크"><Inp value={s.notice.link} onChange={(v) => patch("notice", { link: v })} placeholder="/contact" /></Field>
      </Section>

      {/* 메인 배너 */}
      <Section title="메인 배너 (히어로)" onSave={() => save("hero")} saving={saving === "hero"}>
        <ImageField label="PC 배너 (가로)" hint="1920 × 1080px (16:9). 텍스트는 이미지에 포함 가능" url={s.hero.image} onPick={(f) => pick(f, (url) => patch("hero", { image: url }))} />
        <ImageField label="모바일 배너 (세로)" hint="1080 × 1350px (4:5). 비우면 PC 배너 사용 — 휴대폰에서 글자 안 잘리려면 권장" url={s.hero.imageMobile} onPick={(f) => pick(f, (url) => patch("hero", { imageMobile: url }))} />
        <Field label="상단 지역 문구"><Inp value={s.hero.eyebrow} onChange={(v) => patch("hero", { eyebrow: v })} /></Field>
        <Field label="헤드라인 (줄바꿈 가능)"><Area value={s.hero.title} onChange={(v) => patch("hero", { title: v })} /></Field>
        <Field label="서브 타이틀"><Inp value={s.hero.subline} onChange={(v) => patch("hero", { subline: v })} /></Field>
        <Field label="설명 문구"><Area value={s.hero.lead} onChange={(v) => patch("hero", { lead: v })} /></Field>
      </Section>

      {/* 회사소개 */}
      <Section title="회사소개" onSave={() => save("company")} saving={saving === "company"}>
        <ImageField label="회사소개 이미지" hint="1200 × 900px (4:3)" url={s.company.image} onPick={(f) => pick(f, (url) => patch("company", { image: url }))} />
        <Field label="제목"><Inp value={s.company.title} onChange={(v) => patch("company", { title: v })} /></Field>
        <Field label="소개글"><Area value={s.company.body} onChange={(v) => patch("company", { body: v })} /></Field>
      </Section>

      {/* 쇼룸 */}
      <Section title="쇼룸 안내" onSave={() => save("showroom")} saving={saving === "showroom"}>
        <Field label="제목"><Inp value={s.showroom.title} onChange={(v) => patch("showroom", { title: v })} /></Field>
        <Field label="소개글"><Area value={s.showroom.body} onChange={(v) => patch("showroom", { body: v })} /></Field>
        <Field label="예약 안내"><Inp value={s.showroom.hours} onChange={(v) => patch("showroom", { hours: v })} /></Field>
        <MultiImage
          label="쇼룸 갤러리 (4~6장)"
          hint="1200 × 900px (4:3) · 첫 사진이 크게 노출됩니다"
          urls={s.showroom.images ?? []}
          onAdd={addShowroomImages}
          onRemove={(i) => patch("showroom", { images: (s.showroom.images ?? []).filter((_, j) => j !== i) })}
        />
        <ImageField label="오시는 길 지도 이미지" hint="1320 × 500px (가로형) · 직접 만든 지도 캡처" url={s.showroom.map} onPick={(f) => pick(f, (url) => patch("showroom", { map: url }))} />
      </Section>

      {/* 카테고리 대표이미지 */}
      <Section title="카테고리 대표 이미지" onSave={() => save("categories")} saving={saving === "categories"}>
        <div className="grid gap-4 sm:grid-cols-3">
          {CATEGORIES.map((c) => (
            <ImageField key={c} label={c} hint="1200 × 900px (4:3)" url={s.categories[c]} onPick={(f) => pick(f, (url) => patch("categories", { [c]: url } as Partial<Settings["categories"]>))} />
          ))}
        </div>
      </Section>

      {/* 전기 면허 등록증 */}
      <Section title="전기 면허 등록증" onSave={() => save("license")} saving={saving === "license"}>
        <Field label="제목"><Inp value={s.license.title} onChange={(v) => patch("license", { title: v })} /></Field>
        <Field label="설명"><Inp value={s.license.desc} onChange={(v) => patch("license", { desc: v })} /></Field>
        <p className="text-[12px] font-bold text-gold-d">등록증 사진 (1열 2개 · 세로형 권장)</p>
        <div className="grid gap-4 sm:grid-cols-2">
          {s.license.items.map((it, i) => (
            <div key={i} className="space-y-2 rounded-xl border border-line p-3">
              <ImageField label={`등록증 ${i + 1}`} hint="세로형 (A4 비율)" url={it.image} onPick={(f) => pick(f, (url) => setLicenseItem(i, { image: url }))} />
              <Inp value={it.caption} onChange={(v) => setLicenseItem(i, { caption: v })} placeholder="등록증 이름 (예: 전기공사업 등록증)" />
            </div>
          ))}
        </div>
      </Section>

      {/* 전국 지사 */}
      <Section title="전국 지사" onSave={() => save("branches")} saving={saving === "branches"}>
        <Field label="제목"><Inp value={s.branches.title} onChange={(v) => patch("branches", { title: v })} /></Field>
        <Field label="설명"><Inp value={s.branches.desc} onChange={(v) => patch("branches", { desc: v })} /></Field>
        <ImageField label="전국 지사 지도 이미지" hint="가로형 · 직접 만든 지도 캡처" url={s.branches.mapImage} onPick={(f) => pick(f, (url) => patch("branches", { mapImage: url }))} />
        <p className="text-[12px] font-bold text-gold-d">지사 목록 (표 · 무제한)</p>
        <div className="space-y-2">
          {s.branches.rows.map((b, i) => (
            <div key={i} className="flex items-center gap-2">
              <input className={inputCls} value={b.name ?? ""} onChange={(e) => setBranch(i, { name: e.target.value })} placeholder="지사명" />
              <input className={inputCls} value={b.area ?? ""} onChange={(e) => setBranch(i, { area: e.target.value })} placeholder="담당 지역" />
              <input className={inputCls} value={b.phone ?? ""} onChange={(e) => setBranch(i, { phone: e.target.value })} placeholder="연락처" />
              <button type="button" onClick={() => delBranch(i)} className="shrink-0 rounded-lg border border-line px-3 py-2.5 text-[13px] font-semibold text-red-600">삭제</button>
            </div>
          ))}
          <button type="button" onClick={addBranch} className="rounded-lg border border-dashed border-line px-4 py-2 text-[13px] font-semibold text-navy">+ 지사 추가</button>
        </div>
      </Section>

      {/* 협력사 */}
      <Section title="협력사" onSave={() => save("partners")} saving={saving === "partners"}>
        <Field label="제목"><Inp value={s.partners.title} onChange={(v) => patch("partners", { title: v })} /></Field>
        <Field label="설명"><Inp value={s.partners.desc} onChange={(v) => patch("partners", { desc: v })} /></Field>
        <p className="text-[12px] font-bold text-gold-d">협력사 로고 (3열 그리드 · 무제한, 9개 권장)</p>
        <div className="grid grid-cols-2 gap-3 sm:grid-cols-3">
          {s.partners.logos.map((l, i) => (
            <div key={i} className="relative space-y-2 rounded-xl border border-line p-3">
              <button type="button" onClick={() => delLogo(i)} className="absolute -right-1.5 -top-1.5 z-10 flex h-5 w-5 items-center justify-center rounded-full bg-red-600 text-[11px] text-white">×</button>
              <ImageField label={`로고 ${i + 1}`} url={l.image} onPick={(f) => pick(f, (url) => setLogo(i, { image: url }))} />
              <Inp value={l.name} onChange={(v) => setLogo(i, { name: v })} placeholder="협력사명" />
            </div>
          ))}
        </div>
        <button type="button" onClick={addLogo} className="rounded-lg border border-dashed border-line px-4 py-2 text-[13px] font-semibold text-navy">+ 협력사 추가</button>
      </Section>

      {/* SEO (메인) */}
      <Section title="SEO (메인 페이지)" onSave={() => save("seo")} saving={saving === "seo"}>
        <p className="text-[12px] text-muted">비워두면 기본값이 적용됩니다.</p>
        <Field label="Title"><Inp value={s.seo.home.title} onChange={(v) => setS((p) => ({ ...p, seo: { home: { ...p.seo.home, title: v } } }))} /></Field>
        <Field label="Description"><Area value={s.seo.home.description} onChange={(v) => setS((p) => ({ ...p, seo: { home: { ...p.seo.home, description: v } } }))} /></Field>
        <Field label="Keywords (쉼표 구분)"><Inp value={s.seo.home.keywords} onChange={(v) => setS((p) => ({ ...p, seo: { home: { ...p.seo.home, keywords: v } } }))} /></Field>
        <ImageField label="OG 이미지 (공유 썸네일)" hint="1200 × 630px" url={s.seo.home.og} onPick={(f) => pick(f, (url) => setS((p) => ({ ...p, seo: { home: { ...p.seo.home, og: url } } })))} />
      </Section>
    </div>
  );
}

const LABEL: Record<string, string> = {
  site: "기본 정보", notice: "공지바", hero: "메인 배너", company: "회사소개",
  showroom: "쇼룸", categories: "카테고리 이미지", seo: "SEO",
  license: "면허 등록증", branches: "전국 지사", partners: "협력사",
};

function Section({ title, children, onSave, saving }: { title: string; children: React.ReactNode; onSave: () => void; saving: boolean }) {
  return (
    <section className="rounded-2xl border border-line bg-surface p-6">
      <div className="mb-5 flex items-center justify-between">
        <h2 className="text-[16px] font-extrabold text-ink">{title}</h2>
        <button onClick={onSave} disabled={saving} className="rounded-lg bg-navy px-5 py-2.5 text-[13px] font-semibold text-white disabled:opacity-60">
          {saving ? "저장 중…" : "저장"}
        </button>
      </div>
      <div className="space-y-4">{children}</div>
    </section>
  );
}
const Grid = ({ children }: { children: React.ReactNode }) => <div className="grid gap-4 sm:grid-cols-2">{children}</div>;
function Field({ label, children }: { label: string; children: React.ReactNode }) {
  return <label className="block"><span className="mb-1.5 block text-[13px] font-semibold text-ink">{label}</span>{children}</label>;
}
const inputCls = "w-full rounded-lg border border-line bg-bg px-3.5 py-2.5 text-[14px] outline-none focus:border-navy";
const Inp = ({ value, onChange, placeholder }: { value: string; onChange: (v: string) => void; placeholder?: string }) => (
  <input className={inputCls} value={value ?? ""} onChange={(e) => onChange(e.target.value)} placeholder={placeholder} />
);
const Area = ({ value, onChange }: { value: string; onChange: (v: string) => void }) => (
  <textarea className={`${inputCls} min-h-[90px]`} value={value ?? ""} onChange={(e) => onChange(e.target.value)} />
);
function Check({ checked, onChange, label }: { checked: boolean; onChange: (v: boolean) => void; label: string }) {
  return <label className="flex items-center gap-2.5 text-[14px] font-medium text-ink"><input type="checkbox" checked={checked} onChange={(e) => onChange(e.target.checked)} className="h-4 w-4" />{label}</label>;
}
function ImageField({ label, url, onPick, hint }: { label: string; url?: string; onPick: (f: File | undefined) => void; hint?: string }) {
  return (
    <div>
      <span className="mb-1 block text-[13px] font-semibold text-ink">{label}</span>
      {hint && <span className="mb-1.5 block text-[11.5px] text-gold-d">권장 크기 {hint}</span>}
      <div className="flex items-center gap-3">
        {url && (
          // eslint-disable-next-line @next/next/no-img-element
          <img src={url} alt={label} className="h-16 w-24 rounded-lg border border-line object-cover" />
        )}
        <input type="file" accept="image/*" onChange={(e) => onPick(e.target.files?.[0])} className="text-[12.5px] text-muted file:mr-2 file:rounded-md file:border-0 file:bg-navy file:px-3 file:py-2 file:text-white" />
      </div>
    </div>
  );
}

function MultiImage({ label, urls, onAdd, onRemove, hint }: { label: string; urls: string[]; onAdd: (files: FileList) => void; onRemove: (i: number) => void; hint?: string }) {
  return (
    <div>
      <span className="mb-1 block text-[13px] font-semibold text-ink">{label}</span>
      {hint && <span className="mb-1.5 block text-[11.5px] text-gold-d">권장 크기 {hint}</span>}
      {urls.length > 0 && (
        <div className="mb-2 flex flex-wrap gap-2">
          {urls.map((u, i) => (
            <div key={i} className="relative">
              {/* eslint-disable-next-line @next/next/no-img-element */}
              <img src={u} alt="" className="h-16 w-24 rounded-lg border border-line object-cover" />
              <button type="button" onClick={() => onRemove(i)} className="absolute -right-1.5 -top-1.5 flex h-5 w-5 items-center justify-center rounded-full bg-red-600 text-[11px] text-white">×</button>
            </div>
          ))}
        </div>
      )}
      <input type="file" accept="image/*" multiple onChange={(e) => e.target.files && onAdd(e.target.files)} className="text-[12.5px] text-muted file:mr-2 file:rounded-md file:border-0 file:bg-navy file:px-3 file:py-2 file:text-white" />
    </div>
  );
}

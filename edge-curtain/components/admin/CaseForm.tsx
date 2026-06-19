"use client";

import { useMemo, useState } from "react";
import { useRouter } from "next/navigation";
import { createClient } from "@/lib/supabase/client";
import { uploadImage } from "@/lib/upload";
import { buildCaseSlug, autoSeoTitle, autoSeoDescription } from "@/lib/seo";
import { REGIONS, CATEGORIES, type Region, type Category } from "@/lib/constants";
import type { CaseRow } from "@/lib/types";

export default function CaseForm({ initial }: { initial?: CaseRow }) {
  const router = useRouter();
  const supabase = useMemo(() => createClient(), []);
  const isEdit = Boolean(initial);

  const [title, setTitle] = useState(initial?.title ?? "");
  const [region, setRegion] = useState<Region>(initial?.region ?? "울산");
  const [category, setCategory] = useState<Category>(initial?.category ?? "커튼");
  const [apartment, setApartment] = useState(initial?.apartment ?? "");
  const [body, setBody] = useState(initial?.body ?? "");
  const [tagsText, setTagsText] = useState((initial?.tags ?? []).join(", "));
  const [published, setPublished] = useState(initial?.published ?? true);

  const [cover, setCover] = useState<string | null>(initial?.cover ?? null);
  const [coverFile, setCoverFile] = useState<File | null>(null);
  const [images, setImages] = useState<string[]>(initial?.images ?? []);
  const [imageFiles, setImageFiles] = useState<File[]>([]);

  const [busy, setBusy] = useState(false);
  const [msg, setMsg] = useState("");

  const seoTitlePreview = autoSeoTitle({ apartment: apartment || "○○아파트", region, category });
  const seoDescPreview = autoSeoDescription({ apartment: apartment || "○○아파트", region, category, body });

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    setBusy(true);
    setMsg("이미지 변환·업로드 중…");
    try {
      // 대표 이미지
      let coverUrl = cover;
      if (coverFile) coverUrl = await uploadImage(supabase, coverFile);

      // 상세 이미지 (기존 유지 + 신규 업로드)
      const newImageUrls: string[] = [];
      for (const f of imageFiles) newImageUrls.push(await uploadImage(supabase, f));
      const allImages = [...images, ...newImageUrls];

      const tags = Array.from(
        new Set(
          [region, apartment, ...tagsText.split(/[,\s]+/)]
            .map((t) => t.trim())
            .filter(Boolean),
        ),
      );

      const record = {
        title: title.trim() || `${region} ${apartment} ${category} 시공`,
        region,
        category,
        apartment: apartment.trim(),
        cover: coverUrl,
        images: allImages,
        body,
        tags,
        seo_title: autoSeoTitle({ apartment, region, category }),
        seo_description: autoSeoDescription({ apartment, region, category, body }),
        published,
      };

      setMsg("저장 중…");
      if (isEdit && initial) {
        const { error } = await supabase.from("cases").update(record).eq("id", initial.id);
        if (error) throw error;
      } else {
        // 슬러그 중복 시 짧은 접미사
        let slug = buildCaseSlug(apartment || title, category);
        let { error } = await supabase.from("cases").insert({ ...record, slug });
        if (error && String(error.message).includes("duplicate")) {
          slug = `${slug}-${Date.now().toString(36).slice(-4)}`;
          ({ error } = await supabase.from("cases").insert({ ...record, slug }));
        }
        if (error) throw error;
      }

      router.push("/admin");
      router.refresh();
    } catch (err) {
      setMsg(`오류: ${err instanceof Error ? err.message : "저장 실패"}`);
      setBusy(false);
    }
  }

  const label = "mb-1.5 block text-[13px] font-semibold text-ink";
  const input =
    "w-full rounded-lg border border-line bg-bg px-3.5 py-3 text-[14px] outline-none focus:border-navy";

  return (
    <form onSubmit={onSubmit} className="space-y-6">
      <div>
        <label className={label}>제목</label>
        <input className={input} value={title} onChange={(e) => setTitle(e.target.value)} placeholder="예) 문수로 롯데캐슬 거실 암막커튼 시공" />
      </div>

      <div className="grid gap-4 sm:grid-cols-2">
        <div>
          <label className={label}>지역</label>
          <select className={input} value={region} onChange={(e) => setRegion(e.target.value as Region)}>
            {REGIONS.map((r) => <option key={r}>{r}</option>)}
          </select>
        </div>
        <div>
          <label className={label}>카테고리</label>
          <select className={input} value={category} onChange={(e) => setCategory(e.target.value as Category)}>
            {CATEGORIES.map((c) => <option key={c}>{c}</option>)}
          </select>
        </div>
      </div>

      <div>
        <label className={label}>아파트명</label>
        <input className={input} value={apartment} onChange={(e) => setApartment(e.target.value)} placeholder="예) 문수로 롯데캐슬" />
      </div>

      {/* 대표 이미지 */}
      <div>
        <label className={label}>대표 이미지 (1장)</label>
        <p className="mb-2 text-[11.5px] text-gold-d">권장 크기 1200 × 900px (4:3) — 시공사례 카드·대표 이미지로 사용됩니다.</p>
        <input type="file" accept="image/*" onChange={(e) => setCoverFile(e.target.files?.[0] ?? null)} className="block w-full text-[13px] text-muted file:mr-3 file:rounded-lg file:border-0 file:bg-navy file:px-4 file:py-2.5 file:text-white" />
        {(coverFile || cover) && (
          <div className="mt-3 flex items-center gap-3">
            {/* eslint-disable-next-line @next/next/no-img-element */}
            <img src={coverFile ? URL.createObjectURL(coverFile) : cover!} alt="대표" className="h-20 w-28 rounded-lg object-cover" />
            {cover && !coverFile && (
              <button type="button" onClick={() => setCover(null)} className="text-[12.5px] text-red-600">제거</button>
            )}
          </div>
        )}
      </div>

      {/* 상세 이미지 다중 */}
      <div>
        <label className={label}>상세 사진 (여러 장)</label>
        <p className="mb-2 text-[11.5px] text-gold-d">권장 크기 1200 × 900px (4:3) 이상</p>
        <input type="file" accept="image/*" multiple onChange={(e) => setImageFiles(Array.from(e.target.files ?? []))} className="block w-full text-[13px] text-muted file:mr-3 file:rounded-lg file:border-0 file:bg-navy file:px-4 file:py-2.5 file:text-white" />
        {(images.length > 0 || imageFiles.length > 0) && (
          <div className="mt-3 flex flex-wrap gap-2">
            {images.map((src, i) => (
              <div key={src} className="relative">
                {/* eslint-disable-next-line @next/next/no-img-element */}
                <img src={src} alt={`상세 ${i}`} className="h-16 w-20 rounded-lg object-cover" />
                <button type="button" onClick={() => setImages(images.filter((_, j) => j !== i))} className="absolute -right-1.5 -top-1.5 flex h-5 w-5 items-center justify-center rounded-full bg-red-600 text-[11px] text-white">×</button>
              </div>
            ))}
            {imageFiles.map((f, i) => (
              // eslint-disable-next-line @next/next/no-img-element
              <img key={i} src={URL.createObjectURL(f)} alt={`신규 ${i}`} className="h-16 w-20 rounded-lg object-cover opacity-80" />
            ))}
          </div>
        )}
        <p className="mt-1.5 text-[11.5px] text-muted">업로드 시 자동으로 WebP 로 변환·압축됩니다. (모바일 사진 회전 자동 보정)</p>
      </div>

      <div>
        <label className={label}>본문</label>
        <textarea className={`${input} min-h-[160px]`} value={body} onChange={(e) => setBody(e.target.value)} placeholder="시공 내용, 사용 제품, 고객 요청사항 등을 자유롭게 작성하세요." />
      </div>

      <div>
        <label className={label}>태그 (쉼표로 구분)</label>
        <input className={input} value={tagsText} onChange={(e) => setTagsText(e.target.value)} placeholder="예) 암막커튼, 린넨, 콤비블라인드" />
        <p className="mt-1.5 text-[11.5px] text-muted">지역·아파트명은 자동으로 태그에 추가됩니다.</p>
      </div>

      {/* SEO 미리보기 */}
      <div className="rounded-lg border border-line bg-bg p-4">
        <p className="text-[11px] font-bold uppercase tracking-wider text-gold-d">SEO 자동 생성 미리보기</p>
        <p className="mt-2 text-[13.5px] font-semibold text-navy">{seoTitlePreview}</p>
        <p className="mt-1 line-clamp-2 text-[12.5px] text-muted">{seoDescPreview}</p>
      </div>

      <label className="flex items-center gap-2.5 text-[14px] font-medium text-ink">
        <input type="checkbox" checked={published} onChange={(e) => setPublished(e.target.checked)} className="h-4 w-4" />
        공개 (체크 해제 시 비공개 — 사이트에 노출 안 됨)
      </label>

      {msg && <p className="text-[13px] text-gold-d">{msg}</p>}

      <div className="flex gap-3 pb-10">
        <button type="submit" disabled={busy} className="rounded-lg bg-navy px-6 py-3 text-[15px] font-semibold text-white transition hover:bg-navy-d disabled:opacity-60">
          {busy ? "저장 중…" : isEdit ? "수정 저장" : "시공사례 등록"}
        </button>
        <button type="button" onClick={() => router.push("/admin")} className="rounded-lg border border-line px-6 py-3 text-[15px] font-semibold text-ink">
          취소
        </button>
      </div>
    </form>
  );
}

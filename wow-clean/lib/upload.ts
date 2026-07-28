import type { SupabaseClient } from "@supabase/supabase-js";

/**
 * 브라우저에서 이미지 파일을 WebP 로 변환(+리사이즈).
 * createImageBitmap 의 imageOrientation 으로 모바일 사진 회전(EXIF)도 자동 보정.
 */
export async function fileToWebp(
  file: File,
  maxW = 1600,
  quality = 0.82,
): Promise<Blob> {
  const bitmap = await createImageBitmap(file, {
    imageOrientation: "from-image",
  } as ImageBitmapOptions);
  const scale = Math.min(1, maxW / bitmap.width);
  const w = Math.round(bitmap.width * scale);
  const h = Math.round(bitmap.height * scale);
  const canvas = document.createElement("canvas");
  canvas.width = w;
  canvas.height = h;
  const ctx = canvas.getContext("2d");
  if (!ctx) throw new Error("캔버스를 사용할 수 없습니다.");
  ctx.drawImage(bitmap, 0, 0, w, h);
  bitmap.close?.();
  return await new Promise<Blob>((resolve, reject) =>
    canvas.toBlob(
      (b) => (b ? resolve(b) : reject(new Error("이미지 변환에 실패했습니다."))),
      "image/webp",
      quality,
    ),
  );
}

/** 영상 파일(mp4 등)을 변환 없이 Supabase Storage(media) 업로드 → 공개 URL 반환 */
export async function uploadVideo(
  supabase: SupabaseClient,
  file: File,
): Promise<string> {
  const ext = (file.name.split(".").pop() || "mp4").toLowerCase();
  const name = `video/${crypto.randomUUID()}.${ext}`;
  const { error } = await supabase.storage
    .from("media")
    .upload(name, file, { contentType: file.type || "video/mp4", upsert: false });
  if (error) throw new Error(`영상 업로드 실패: ${error.message}`);
  return supabase.storage.from("media").getPublicUrl(name).data.publicUrl;
}

/** WebP 변환 후 Supabase Storage(media) 업로드 → 공개 URL 반환 */
export async function uploadImage(
  supabase: SupabaseClient,
  file: File,
): Promise<string> {
  const webp = await fileToWebp(file);
  const name = `cases/${crypto.randomUUID()}.webp`;
  const { error } = await supabase.storage
    .from("media")
    .upload(name, webp, { contentType: "image/webp", upsert: false });
  if (error) throw new Error(`업로드 실패: ${error.message}`);
  return supabase.storage.from("media").getPublicUrl(name).data.publicUrl;
}

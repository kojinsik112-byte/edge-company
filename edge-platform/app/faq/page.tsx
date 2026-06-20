import type { Metadata } from "next";
import { getFaqs } from "@/lib/data";

export const metadata: Metadata = {
  title: "자주 묻는 질문 (FAQ) — 실링팬·간접조명·센서조명",
  description: "실링팬 설치, 전기요금, 간접조명 밝기, 센서조명 제어 등 자주 묻는 질문과 답변.",
  alternates: { canonical: "/faq" },
};

export default async function FaqPage() {
  const faqs = await getFaqs();

  const jsonLd = {
    "@context": "https://schema.org",
    "@type": "FAQPage",
    mainEntity: faqs.map((f) => ({
      "@type": "Question",
      name: f.question,
      acceptedAnswer: { "@type": "Answer", text: f.answer },
    })),
  };

  return (
    <div className="mx-auto max-w-[760px] px-5 py-12 md:py-16">
      {faqs.length > 0 && (
        <script type="application/ld+json" dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd) }} />
      )}
      <p className="kicker">FAQ</p>
      <h1 className="mt-3 text-2xl font-bold text-ink md:text-3xl">자주 묻는 질문</h1>

      {faqs.length > 0 ? (
        <div className="mt-8">
          {faqs.map((f) => (
            <details key={f.id} className="border-b border-line">
              <summary className="flex cursor-pointer list-none items-center justify-between gap-4 py-5 text-[16px] font-semibold text-ink">
                <span><span className="mr-2 font-bold text-gold">Q.</span>{f.question}</span>
                <span className="text-xl font-light text-gold">+</span>
              </summary>
              <p className="prose pb-6">{f.answer}</p>
            </details>
          ))}
        </div>
      ) : (
        <div className="mt-10 rounded-2xl border border-dashed border-line bg-bg py-20 text-center text-[14px] text-muted">
          등록된 질문이 아직 없습니다.
        </div>
      )}
    </div>
  );
}

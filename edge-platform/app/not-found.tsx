import Link from "next/link";

export default function NotFound() {
  return (
    <div className="mx-auto flex max-w-[600px] flex-col items-center px-5 py-32 text-center">
      <p className="kicker">404</p>
      <h1 className="mt-3 text-2xl font-bold text-ink">페이지를 찾을 수 없습니다</h1>
      <p className="mt-3 text-[14.5px] text-muted">요청하신 페이지가 없거나 이동되었습니다.</p>
      <Link href="/" className="mt-7 rounded-lg bg-navy px-6 py-3 text-[15px] font-semibold text-white">
        홈으로
      </Link>
    </div>
  );
}

export default function Stars({ n = 5 }: { n?: number }) {
  return (
    <span className="inline-flex text-gold" aria-label={`별점 ${n}점`}>
      {Array.from({ length: 5 }).map((_, i) => (
        <svg
          key={i}
          viewBox="0 0 24 24"
          className="h-4 w-4"
          fill={i < n ? "currentColor" : "none"}
          stroke="currentColor"
          strokeWidth={1.4}
        >
          <path d="M12 3.5l2.6 5.3 5.9.9-4.3 4.1 1 5.8L12 17l-5.2 2.7 1-5.8-4.3-4.1 5.9-.9z" />
        </svg>
      ))}
    </span>
  );
}

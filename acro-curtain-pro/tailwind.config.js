/** @type {import('tailwindcss').Config} */
const tok = (name) => `rgb(var(--${name}) / <alpha-value>)`;

export default {
  content: ['./index.html', './src/**/*.{ts,tsx}'],
  theme: {
    extend: {
      colors: {
        bg: tok('bg'),
        surface: tok('surface'),
        sunk: tok('sunk'),
        line: tok('line'),
        ink: tok('ink'),
        ink2: tok('ink-2'),
        ink3: tok('ink-3'),
        primary: tok('primary'),
        onprimary: tok('on-primary'),
        gold: tok('gold'),
        goldsoft: tok('gold-soft'),
        ok: tok('ok'),
        warn: tok('warn'),
        warnsoft: tok('warn-soft'),
        err: tok('err'),
        errsoft: tok('err-soft'),
      },
      fontFamily: {
        sans: ['"IBM Plex Sans KR"', 'Pretendard', '"Malgun Gothic"', '"Apple SD Gothic Neo"', 'system-ui', 'sans-serif'],
        num: ['Manrope', '"IBM Plex Sans KR"', 'system-ui', 'sans-serif'],
        mono: ['"IBM Plex Mono"', 'ui-monospace', 'Consolas', 'monospace'],
      },
      borderRadius: {
        card: '14px',
        field: '10px',
      },
      boxShadow: {
        card: '0 1px 2px rgb(var(--shadow) / 0.06), 0 8px 24px -12px rgb(var(--shadow) / 0.18)',
      },
    },
  },
  plugins: [],
};

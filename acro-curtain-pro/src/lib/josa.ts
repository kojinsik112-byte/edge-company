// 한국어 조사 자동 선택: josa('원단 1폭', '을/를') → '원단 1폭을'
export function josa(word: string, pair: '을/를' | '은/는' | '이/가' | '과/와'): string {
  const ch = word.trim().slice(-1);
  const code = ch.charCodeAt(0);
  let batchim: boolean;
  if (code >= 0xac00 && code <= 0xd7a3) batchim = (code - 0xac00) % 28 !== 0;
  else if (/[0-9]/.test(ch)) batchim = '013678'.includes(ch);
  else batchim = false;
  const [a, b] = pair.split('/');
  return word + (batchim ? a : b);
}

// 엣지컴퍼니 클린벤더 스크리닝 — 서버리스 함수
// 업체명을 받아 네이버 카페/블로그에서 후기·위험정황을 검색해 돌려준다.
// 🔐 API 키는 코드에 박지 않고 Netlify 환경변수(NAVER_CLIENT_ID/SECRET)에서만 읽는다.

// 강한 위험어 = 업체명 근처에 있으면 무조건 위험(긍정문맥에 거의 안 섞임)
//   단어 일부에 우연히 섞이는 오탐(예: 신사+기구='사기', 고소+한='고소') 방지 위해 '구체형'만.
const RISK_STRONG = ['먹튀', '잠적', '연락두절', '소송', '바가지', '계약파기', '환불거부',
  '사기당', '사기꾼', '사기성', '사기쳐', '사기친', '고소장', '고소당', '부도났', '부도처리',
  '피해보상', '법적대응', '돈먹고', '돈떼'];
// 약한 위험어 = 업체명 근처 + 그 글에 칭찬이 없을 때만 위험.
//   '하자'는 "말하자면/생각하자" 등 동사형 오탐 방지 위해 '구체형'만 사용.
const RISK_SOFT = ['하자가', '하자발생', '하자투성', '하자많', '하자처리안', '부실시공', '재시공', '엉망', '최악', '불친절', '미시공', '환불요청', '환불안', '보수안'];
// 글 전체에 이 칭찬어가 있으면 약한 위험어는 무시(= 만족 후기) — 공백제거형으로 비교
const POSITIVE = ['만족', '추천', '잘했', '잘됐', '잘해', '잘해주', '친절', '꼼꼼', '감사', '강추', '최고', '이뻐', '예뻐', '깔끔', '너무좋', '정말좋', '맘에들', '마음에들', '좋아요', '좋았', '만족스'];
const RISK_KEYWORDS = [...RISK_STRONG, ...RISK_SOFT];

const strip = (s) => (s || '')
  .replace(/<[^>]+>/g, '')
  .replace(/&quot;/g, '"').replace(/&amp;/g, '&')
  .replace(/&lt;/g, '<').replace(/&gt;/g, '>').replace(/&#39;/g, "'")
  .trim();

function json(status, body) {
  return {
    statusCode: status,
    headers: { 'Content-Type': 'application/json; charset=utf-8', 'Access-Control-Allow-Origin': '*' },
    body: JSON.stringify(body),
  };
}

async function naver(ep, query, display, sort, headers, start = 1) {
  const url = `https://openapi.naver.com/v1/search/${ep}.json`
    + `?query=${encodeURIComponent(query)}&display=${display}&sort=${sort}&start=${start}`;
  try {
    const r = await fetch(url, { headers });
    if (!r.ok) return [];
    const j = await r.json();
    return (j.items || []).map((it) => ({
      title: strip(it.title),
      desc: strip(it.description),
      link: it.link,
      where: it.cafename ? `카페 · ${it.cafename}` : (it.bloggername ? `블로그 · ${it.bloggername}` : ep),
      date: it.postdate ? `${it.postdate.slice(0, 4)}.${it.postdate.slice(4, 6)}.${it.postdate.slice(6, 8)}` : '',
      ep,
    }));
  } catch (e) {
    return [];
  }
}

exports.handler = async (event) => {
  const q = ((event.queryStringParameters || {}).q || '').trim();
  if (!q) return json(400, { error: '업체명을 입력하세요.' });
  if (q.length > 40) return json(400, { error: '업체명이 너무 깁니다.' });

  const ID = process.env.NAVER_CLIENT_ID;
  const SEC = process.env.NAVER_CLIENT_SECRET;
  if (!ID || !SEC) return json(500, { error: '서버에 네이버 API 키가 설정되지 않았습니다(NAVER_CLIENT_ID/SECRET).' });
  const headers = { 'X-Naver-Client-Id': ID, 'X-Naver-Client-Secret': SEC };

  // 1) 쿼리 정의 — [ep, query, display, sort, start]
  //    업체명 자체를 카페 3페이지(최대 300건) 깊게 + 블로그 + 위험키워드
  const defs = [
    ['cafearticle', q, 100, 'date', 1],
    ['cafearticle', q, 100, 'date', 101],
    ['cafearticle', q, 100, 'date', 201],
    ['cafearticle', `${q} 후기`, 50, 'sim', 1],
    ['blog', q, 50, 'sim', 1],
    ['blog', `${q} 후기`, 30, 'sim', 1],
  ];
  for (const kw of ['사기', '먹튀', '잠적', '연락두절', '소송', '부도', '하자', '환불', '피해', '분쟁']) {
    defs.push(['cafearticle', `${q} ${kw}`, 10, 'sim', 1]);
  }

  // 2) 네이버 버스트 차단(rate limit) 방지 — 5개씩 배치로 순차 실행
  const results = [];
  for (let i = 0; i < defs.length; i += 5) {
    const batch = defs.slice(i, i + 5).map((t) => naver(t[0], t[1], t[2], t[3], headers, t[4]));
    for (const arr of await Promise.all(batch)) results.push(...arr);
  }

  // 3) 정리: 업체명 포함(공백무시) + 업체명 '근처'의 위험어만 표시 + 중복제거
  const norm = (s) => (s || '').replace(/\s+/g, '');   // "엣지 컴퍼니" == "엣지컴퍼니"
  const nVendor = norm(q);
  const WINDOW = 14; // 업체명 앞뒤 14자 = '근처'
  function segsAround(nText) {        // 업체명이 등장하는 모든 주변 구간
    const segs = [];
    let vi = nText.indexOf(nVendor);
    while (vi !== -1) {
      segs.push(nText.slice(Math.max(0, vi - WINDOW), vi + nVendor.length + WINDOW));
      vi = nText.indexOf(nVendor, vi + 1);
    }
    return segs;
  }
  function matchRisk(segs, nText) {
    const postPositive = POSITIVE.some((p) => nText.includes(p)); // 글 전체가 만족 후기인가
    const out = [];
    for (const kw of RISK_KEYWORDS) {
      if (!segs.some((s) => s.includes(kw))) continue;            // 업체명 근처에 있나
      if (RISK_SOFT.includes(kw) && postPositive) continue;       // 칭찬 후기면 약한 위험어 무시
      out.push(kw);
    }
    return out;
  }
  const seen = new Set();
  const items = [];
  for (const it of results) {
    const nText = norm(`${it.title} ${it.desc}`);
    if (!nText.includes(nVendor)) continue;     // 업체명 미포함 = 동명/무관 노이즈 제거
    if (seen.has(it.link)) continue;
    seen.add(it.link);
    const matched = matchRisk(segsAround(nText), nText); // 업체명 근처 위험어(만족후기 제외)
    items.push({ ...it, risk: matched });
  }

  // 3) 위험 우선 정렬, 위험정황 개수 집계
  items.sort((a, b) => b.risk.length - a.risk.length);
  const riskItems = items.filter((it) => it.risk.length > 0);
  const riskKeywordSet = [...new Set(riskItems.flatMap((it) => it.risk))];

  let level = 'safe';
  if (riskItems.length >= 3) level = 'danger';
  else if (riskItems.length >= 1) level = 'caution';

  return json(200, {
    vendor: q,
    total: items.length,
    riskCount: riskItems.length,
    riskKeywords: riskKeywordSet,
    level,
    items,
    note: '네이버 검색 노출글 기준. 동명 업체·일회성 글이 섞일 수 있어 최종 판단은 담당자가 합니다.',
  });
};

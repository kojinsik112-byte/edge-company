# -*- coding: utf-8 -*-
"""탕정 v2 밝은 바탕 시안(10-21 본부장 요청) — v2 HTML의 색만 바꿔 _v2_밝은시안.html/pdf로 낸다(내용 · 순서는 v2 그대로).

본문 쪽 = 아이보리 종이 + 네이비 글자 + 짙은 골드 강조. 표지 · 간지 · 연락처 · KEY POINT 띠 = 네이비 그대로.
색 기준(WCAG 대비, 아이보리 #FAF7F0 위): 글자 금색 #7A5716 = 6.1 · 라벨 금색 #866322 = 5.1 · 보조 회색 #5C6878 = 5.3 · 본문 #14243A.
금색 '채움'(막대 · 알약 · 강조 칸)은 글자 금색과 분리해 #C9A35A로 둔다(남색 글자 대비 7 이상).
화면을 그릴 때 두 단계 보정(FIX_JS): ① 남색 판(캡션 띠 · 배치도 구역 · 콜센터 원 등) 안은 네이비 색 체계로 되돌림
② 그래도 대비 기준(작은 글자 4.5 · 큰 글자 3) 미만인 글자는 진한 금색 / 남색 / 아이보리 중 기준을 넘는 색으로 — 사진 위 캡션은 건드리지 않는다(휴대폰 모형 · 보증증권 견본은 원래 색).
사용: python3 tjlight.py [05_입주박람회_입찰제안서|요약제안서|회사소개서]  (먼저 build_tangjeong.py --v2 로 v2 HTML 3개를 만든다)
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PFX = os.path.join(HERE, "엣지컴퍼니_탕정푸르지오센터파크_")
# (v2 HTML, 간지 수, 15만원 쪽 수, 간지 띠 문서명) — 05 입찰제안서 · 14 요약 제안서 · 14 회사소개서
JOBS = [("05_입주박람회_입찰제안서", 10, 1, "입주박람회 주관사 제안서"),
        ("요약제안서", 0, 0, "요약 제안서"),
        ("회사소개서", 1, 0, "회사소개서")]
EXTRA = {"회사소개서": ".cv4 h1.tj{font-size:38px!important}"}  # '주식회사 엣지컴퍼니'가 명조 50px이면 표지 사진 밑으로 들어감

DARK = "--bg:#0D1E33;--gold:#EBCB8F;--gold2:#C8A86A;--ink:#F4F6F9;--sub:#B4BECA;--mute:#8595A8;--line:rgba(255,255,255,.13)"
LIGHT = "--bg:#FAF7F0;--gold:#7A5716;--gold2:#866322;--ink:#14243A;--sub:#3B4A5D;--mute:#5C6878;--line:rgba(13,30,51,.14)"
GOLD_FILL = "#C9A35A"
DARK_PAGES = ".page.cv,.page.dv,.page.hero"  # hero = 사진 전면 쪽(요약 p.05 경관조명) — 글자가 사진 위라 어두운 색 체계

OVR = f"""
:root{{{LIGHT}}}
{DARK_PAGES}{{{DARK};color:var(--ink)}}
.page:not(.cv):not(.dv){{background:var(--bg)!important;color:var(--ink)}}
.page .hd{{border-bottom-color:rgba(13,30,51,.14)}}
.sheet{{border:1px solid #d9ccb2;box-shadow:0 6px 18px rgba(13,30,51,.12)!important}}
.kp{{{DARK};background:#0D1E33!important;color:var(--ink);border-color:transparent!important}}
.todo{{background:#FFE066;color:#0D1E33}}
"""

FIX_JS = r"""<script>
(function(){
var D={'--bg':'#0D1E33','--gold':'#EBCB8F','--gold2':'#C8A86A','--ink':'#F4F6F9','--sub':'#B4BECA','--mute':'#8595A8','--line':'rgba(255,255,255,.13)'};
var NAVY={r:20,g:36,b:58,a:1},PAPER={r:250,g:247,b:240,a:1};
function P(c){var m=c&&c.match(/rgba?\(([^)]+)\)/);if(!m)return null;var v=m[1].split(',').map(parseFloat);return{r:v[0],g:v[1],b:v[2],a:v.length>3?v[3]:1};}
function H(x){return{r:parseInt(x.substr(1,2),16),g:parseInt(x.substr(3,2),16),b:parseInt(x.substr(5,2),16),a:1};}
function lum(c){function f(x){x/=255;return x<=.03928?x/12.92:Math.pow((x+.055)/1.055,2.4);}return .2126*f(c.r)+.7152*f(c.g)+.0722*f(c.b);}
function cr(a,b){var x=lum(a),y=lum(b);return(Math.max(x,y)+.05)/(Math.min(x,y)+.05);}
function blend(t,b){return{r:t.r*t.a+b.r*(1-t.a),g:t.g*t.a+b.g*(1-t.a),b:t.b*t.a+b.b*(1-t.a),a:1};}
function grad(s){if(!s||s==='none'||s.indexOf('url(')>=0)return null;var cs=(s.match(/rgba?\([^)]+\)|#[0-9a-fA-F]{6}/g)||[]).map(function(x){return x[0]==='#'?H(x):P(x);});if(!cs.length)return null;var n=cs.length,o={r:0,g:0,b:0,a:0};cs.forEach(function(c){o.r+=c.r/n;o.g+=c.g/n;o.b+=c.b/n;o.a+=c.a/n;});return o;}
function layers(s){var l=[],bc=P(s.backgroundColor),g=grad(s.backgroundImage);if(bc&&bc.a>0)l.push(bc);if(g)l.push(g);return l;}
function eff(el){var st=[],n=el;while(n&&n.nodeType===1){var s=getComputedStyle(n),o=layers(s);for(var i=o.length-1;i>=0;i--)st.push(o[i]);var bc=P(s.backgroundColor);if(bc&&bc.a>=1)break;n=n.parentElement;}
  var bg={r:255,g:255,b:255,a:1};for(var k=st.length-1;k>=0;k--)bg=blend(st[k],bg);return bg;}
function urlUp(el,sec){for(var n=el;n&&n!==sec.parentElement;n=n.parentElement){if(getComputedStyle(n).backgroundImage.indexOf('url(')>=0)return true;}return false;}
function overImg(el,sec,imgs){var r=el.getBoundingClientRect(),x=r.left+r.width/2,y=r.top+r.height/2;
  for(var i=0;i<imgs.length;i++){var q=imgs[i].getBoundingClientRect();if(q.width>40&&x>=q.left&&x<=q.right&&y>=q.top&&y<=q.bottom&&!imgs[i].contains(el))return true;}return urlUp(el,sec);}
function ownText(el){for(var c=el.firstChild;c;c=c.nextSibling)if(c.nodeType===3&&c.textContent.trim())return true;return false;}
document.querySelectorAll('section.page:not(.cv):not(.dv)').forEach(function(sec){
  var all=sec.querySelectorAll('*'),imgs=sec.querySelectorAll('img');
  // ① 남색 판 → 네이비 색 체계(그 판 안 글자 · 금색이 원래 디자인대로)
  all.forEach(function(el){var s=getComputedStyle(el);if(s.backgroundImage.indexOf('url(')>=0||el.closest('.kp'))return;
    var o=layers(s);if(!o.length)return;var top=o.reduce(function(a,c){return c.a>a.a?c:a;});
    if(top.a>=.5&&lum(top)<.05){for(var k in D)el.style.setProperty(k,D[k]);el.setAttribute('data-dk','1');
      var fg=P(getComputedStyle(el).color);if(fg&&cr(fg,eff(el))<4.5)el.style.color='var(--ink)';}});
  // ② 남은 글자 대비 기준 미만(작은 글자 4.5 · 큰 글자 3) → 진한 금색 / 남색 / 아이보리 중 기준을 넘는 색(사진 위 캡션은 제외)
  all.forEach(function(el){if(!ownText(el)||el.closest('.kp,.todo'))return;
    var s=getComputedStyle(el);if(s.display==='none'||s.visibility==='hidden')return;
    var fg=P(s.color);if(!fg||fg.a<.05)return;if(overImg(el,sec,imgs))return;
    var bg=eff(el),f=fg.a<1?blend(fg,bg):fg,fs=parseFloat(s.fontSize),bold=parseInt(s.fontWeight)>=700;
    var need=(fs>=24||(fs>=18.5&&bold))?3:4.5;if(cr(f,bg)>=need)return;
    // 금색 글자는 더 진한 금색부터(디자인 유지) → 그래도 부족하면 남색 / 아이보리
    var cand=(f.r>f.b+30)?['#6B4C12','#14243A','#FAF7F0']:['#14243A','#FAF7F0'];
    var pick=null;for(var i=0;i<cand.length;i++){if(cr(H(cand[i]),bg)>=need){pick=cand[i];break;}}
    if(!pick)pick=cr(NAVY,bg)>=cr(PAPER,bg)?'#14243A':'#FAF7F0';
    el.style.color=pick;el.setAttribute('data-fx','1');});
});
})();
</script>""" + r"""<script>
// ③ 겹침 자동 맞춤(본부장 10-22 '2 · 24 · 42 · 66 · 105 ~ 109쪽 겹침'): 본문(.ct)이 KEY POINT · 꼬리말을 침범하거나
//    카드 · 표 안 글자가 상자 밖으로 나오거나 다른 상자를 덮으면 .ct를 3%씩 줄인다(최소 76%). 줄인 쪽은 data-fit에 배율.
(function(){
function vis(el){for(var n=el;n&&n.nodeType===1;n=n.parentElement){var s=getComputedStyle(n);if(s.display==='none'||s.visibility==='hidden'||parseFloat(s.opacity)===0)return false;}return true;}
function lines(root){var out=[],tw=document.createTreeWalker(root,NodeFilter.SHOW_TEXT),t;
  while((t=tw.nextNode())){if(!t.textContent.trim()||!vis(t.parentElement))continue;var rg=document.createRange();rg.selectNodeContents(t);
    var rs=rg.getClientRects();for(var i=0;i<rs.length;i++)if(rs[i].width>2&&rs[i].height>2)out.push({el:t.parentElement,r:rs[i]});}return out;}
function boxes(root){var out=[];root.querySelectorAll('*').forEach(function(el){var s=getComputedStyle(el);if(s.position==='absolute'||el.tagName==='IMG'||s.backgroundImage.indexOf('url(')>=0)return;
  var r=el.getBoundingClientRect();if(r.width<20||r.height<14||!vis(el))return;
  var bg=s.backgroundColor&&!/rgba\(0, 0, 0, 0\)|transparent/.test(s.backgroundColor),gr=/gradient/.test(s.backgroundImage),
      bd=parseFloat(s.borderTopWidth)>0||parseFloat(s.borderLeftWidth)>0;
  if(bg||gr||bd||s.boxShadow!=='none')out.push({el:el,r:r,c:String(el.className)});});return out;}
function ih(a,b){return Math.min(a.bottom,b.bottom)-Math.max(a.top,b.top);}
function iw(a,b){return Math.min(a.right,b.right)-Math.max(a.left,b.left);}
function bad(sec,ct,strict){var kp=sec.querySelector('.kp'),ft=sec.querySelector('.ft');
  var lim=kp?kp.getBoundingClientRect().top-3:(ft?ft.getBoundingClientRect().top-2:sec.getBoundingClientRect().bottom);
  var L=lines(ct),B=boxes(ct),i,j;
  for(i=0;i<L.length;i++)if(L[i].r.bottom>lim+1)return 'kp';
  for(j=0;j<B.length;j++)if(B[j].r.bottom>lim+2&&B[j].r.top<lim)return 'kpbox';
  for(i=0;i<L.length;i++)for(j=0;j<B.length;j++){var l=L[i],b=B[j];if(iw(l.r,b.r)<3)continue;
    if(b.el.contains(l.el)){if(l.r.bottom>b.r.bottom+2&&l.r.top<b.r.bottom)return 'out';continue;}
    if(l.el.contains(b.el))continue;if(ih(l.r,b.r)>4)return 'cover';}
  // 칸(그리드 · 묶음)보다 내용이 커서 아래 형제를 덮는 경우(카드 묶음이 전문 인력 띠 · 인용 띠를 덮음)
  if(strict){var all=ct.querySelectorAll('*');for(i=0;i<all.length;i++){var e=all[i],s=getComputedStyle(e);
    if(s.position==='absolute'||s.display.indexOf('inline')===0||s.overflowY==='hidden'||e.clientHeight<20||e.tagName==='svg'||e.closest('svg'))continue;
    if(e.scrollHeight>e.clientHeight+8&&vis(e))return 'grow';}}
  for(i=0;i<B.length;i++)for(j=i+1;j<B.length;j++){var a=B[i],c=B[j];if(a.el.contains(c.el)||c.el.contains(a.el)||a.c===c.c)continue;
    if(iw(a.r,c.r)>6&&ih(a.r,c.r)>4)return 'box';}
  return '';}
function fitAll(){document.querySelectorAll('section.page:not(.cv):not(.dv)').forEach(function(sec){var ct=sec.querySelector(':scope>.ct');if(!ct)return;
  // 엄격(칸 넘침 포함)으로 먼저 줄여 보고, 최소 배율로도 안 풀리면(장식용 넘침) 겹침 기준만으로 다시
  var st=true,why=bad(sec,ct,st);if(!why)return;var z=1;
  while(why&&z>0.77){z=Math.round((z-0.03)*100)/100;ct.style.zoom=z;why=bad(sec,ct,st);}
  if(why){st=false;z=1;ct.style.zoom='';why=bad(sec,ct,st);while(why&&z>0.77){z=Math.round((z-0.03)*100)/100;ct.style.zoom=z;why=bad(sec,ct,st);}if(z===1){sec.setAttribute('data-fit','1 칸넘침');return;}}
  sec.setAttribute('data-fit',z+(why?' 남음:'+why:''));});}
// 글꼴 · 사진이 다 들어온 뒤에 잰다(먼저 재면 대체 글꼴 기준이라 인쇄 때 다시 넘침)
(document.fonts?document.fonts.ready:Promise.resolve()).then(function(){if(document.readyState==='complete')fitAll();else addEventListener('load',fitAll);});
})();
</script>"""


CARD_SHADOW = "0 1px 2px rgba(13,30,51,.05),0 14px 30px -20px rgba(13,30,51,.32)"


def white_card(m):
    """흰 반투명 그라데이션 카드(네이비 판의 '살짝 밝은 카드') → 밝은 바탕에서는 흰 카드 + 은은한 그림자."""
    sel, body = m.group(1), m.group(2)
    g = re.search(r"background:\s*linear-gradient\(([^;]*)\)", body)
    if not g:
        return m.group(0)
    stops = re.findall(r"rgba?\([^)]*\)|#[0-9a-fA-F]{3,6}|var\(--[\w-]+\)", g.group(1))
    if not stops or not all(re.match(r"rgba\(255,\s*255,\s*255,\s*0?\.(0\d+|1[0-2]?)\)", x) for x in stops):
        return m.group(0)
    body = body.replace(g.group(0), "background:#FFFFFF")
    if "box-shadow" not in body:
        body = body.rstrip().rstrip(";") + ";box-shadow:" + CARD_SHADOW
    return sel + "{" + body + "}"


def light_css(css):
    if "{" in css:
        css = re.sub(r"([^{}]*)\{([^{}]*)\}", white_card, css)

    def decl(m):
        prop, val = m.group(1), m.group(2)
        p = prop.strip().lower()
        if p == "color":  # 글자색(사진 위 흰 캡션 등)은 그대로
            return m.group(0)
        # 금색 '채움'은 글자 금색(짙게 바뀜)과 분리해 중간 금색으로
        if p in ("background", "background-color") and re.fullmatch(r"\s*var\(--gold2?\)\s*(!important)?\s*", val):
            return f"{prop}:{GOLD_FILL}" + ("!important" if "!important" in val else "")
        # 반투명 남색 칸(원래 남색 덧칠 · 투명도 0.5 이상)은 아이보리 위에서 회색으로 비치므로 진한 남색으로
        if p in ("background", "background-color"):
            val = re.sub(r"^\s*rgba\((\d+),\s*(\d+),\s*(\d+),\s*(0?\.[5-8]\d*)\)",
                         lambda n: f"rgba({n.group(1)},{n.group(2)},{n.group(3)},.92)" if max(int(n.group(i)) for i in (1, 2, 3)) < 60 else n.group(0), val)
        # 연한 금색 채움 · 테두리(네이비 바탕용 #EBCB8F) → 샴페인 금색(밝은 바탕에서 막대 · 띠가 흐려지지 않게)
        val = re.sub(r"rgba\(235,\s*203,\s*143,\s*([.\d]+)\)", lambda n: f"rgba(184,149,90,{min(1, float(n.group(1)) * 1.15):.3f})", val)
        # 반투명 흰 덧칠(카드 · 선 · 바탕) → 반투명 네이비(밝은 바탕에서 같은 깊이로 보이게 투명도 0.8배)
        val = re.sub(r"rgba\(255,\s*255,\s*255,\s*([.\d]+)\)", lambda n: f"rgba(13,30,51,{min(1, float(n.group(1)) * .8):.3f})", val)
        return prop + ":" + val
    css = re.sub(r"([\w-]+)\s*:\s*([^;{}]*)", decl, css)
    # 어두운 판(흰 글자를 쓰지 않는 칸)의 고정 남색 바탕 → 흰 판. 휴대폰 화면 모형(.phm · .phw)은 남색 그대로(흰 화면이면 모형 글자가 안 보임)
    # · 보증증권 견본(#2f4a6b 머리 + 흰 글자)도 그대로
    def rule(m):
        sel, body = m.group(1), m.group(2)
        if re.search(r"\.ph[mw]\b", sel):
            return m.group(0)
        for a in ("#0f2237", "#0a1626", "#0b1a2d"):
            body = re.sub(rf"background(-color)?:\s*{a}", r"background\1:#FFFFFF", body, flags=re.I)
        return sel + "{" + body + "}"
    css = re.sub(r"([^{}]*)\{([^{}]*)\}", rule, css) if "{" in css else re.sub(r"background(-color)?:\s*#(0f2237|0a1626|0b1a2d)", r"background\1:#FFFFFF", css, flags=re.I)
    css = re.sub(r"background:\s*#12263d", "background:var(--bg)", css, flags=re.I)  # 일정표 테두리 위 라벨 → 종이색
    # 밝은 글자색 고정값 → 토큰
    for a, b in [("#D5DCE4", "var(--sub)"), ("#DCE3EB", "var(--sub)"), ("#9fd3c7", "#1f7a68")]:
        css = re.sub(rf"color:\s*{a}", f"color:{b}", css, flags=re.I)
    return css


SVG_FILL = {"#a9b4c2": "#5C6878", "#dce3ec": "#3B4A5D", "#ebcb8f": "#7A5716", "#c8a86a": "#866322"}  # 도식 속 글자 · 면
SVG_STROKE = {"#ebcb8f": "#C9A35A", "#c8a86a": "#866322", "#a9b4c2": "#5C6878"}  # 원 테두리 · 도넛 고리


def light_svg(html):
    """본문 쪽 SVG 속성 색(먼저 챙길 것 벤다이어그램 · 신도시 도넛 등) — 스타일시트가 닿지 않는 곳."""
    def attr(m):
        k, v = m.group(1), m.group(2).lower()
        mp = SVG_STROKE if k == "stroke" else SVG_FILL
        if v in mp:
            return f'{k}="{mp[v]}"'
        w = re.fullmatch(r"rgba\(255,\s*255,\s*255,\s*([.\d]+)\)", v)
        if w:
            return f'{k}="rgba(13,30,51,{min(1, float(w.group(1)) * .8):.3f})"'
        return m.group(0)
    return re.sub(r'\b(stroke|fill)="([^"]+)"', attr, html)


def light(src, out, n_dv, n_hi, label, extra="", hh=None, fund=None, site="탕정 푸르지오 센터파크", post=None):
    """다른 단지도 쓴다(jugansa/tools/light_build.py) — hh · fund · site를 넘기면 그 단지 값, 없으면 탕정 data.py."""
    doc = open(src, encoding="utf-8").read()
    # 48시간 = 방문 일정 확정 · 30일 안 현장 사무소(본부장 10-21 2차 · 4개 단지 공통)
    sys.path.insert(0, os.path.join(HERE, "..", "tools"))
    import common_fix as CF  # noqa: E402
    doc, rep = CF.fix48(doc)
    bad = CF.residue48(doc)
    print("[48시간 · 30일]", sum(rep.values()), "곳", rep)
    assert not bad, ("48시간 문구 남음", bad[:8])
    if post:
        doc = post(doc)
    head, rest = doc.split("</head>", 1)
    head = re.sub(r"<style>(.*?)</style>", lambda m: "<style>" + light_css(m.group(1)) + "</style>", head, flags=re.S)
    head = head.replace("</style>", OVR + extra + "</style>", 1) if head.count("</style>") == 1 else head + f"<style>{OVR}{extra}</style>"
    rest = re.sub(r"<style>(.*?)</style>", lambda m: "<style>" + light_css(m.group(1)) + "</style>", rest, flags=re.S)
    rest = re.sub(r'style="([^"]*)"', lambda m: 'style="' + light_css(m.group(1)) + '"', rest)
    rest = re.sub(r'(<section class="page(?![^"]*\b(?:cv|dv)\b)[^"]*">)(.*?)(</section>)', lambda m: m.group(1) + light_svg(m.group(2)) + m.group(3), rest, flags=re.S)
    # 디자인 레이어(명조 대제목 · 표지 · 간지 · 15만원 증서 · 배치도 · 콜센터 · 캡션 · KEY POINT)
    sys.path.insert(0, HERE)
    import tjdesign  # noqa: E402
    if hh is None:
        import data as D  # noqa: E402
        hh, fund = D.SITE["households"], D.FUND
    head, rest = tjdesign.apply(head, rest, hh, fund, n_dv=n_dv, n_hi=n_hi, label=label, site=site)
    assert rest.count("</body>") == 1
    rest = rest.replace("</body>", FIX_JS + "</body>")
    open(out, "w", encoding="utf-8").write(head + "</head>" + rest)
    print("HTML:", out)
    if "--no-pdf" not in sys.argv:
        sys.path.insert(0, os.path.join(HERE, "..", "요약제안서"))
        import build as B
        B.OUT_HTML, B.OUT_PDF = out, out[:-5] + ".pdf"
        B.build_pdf()


# 10-22 본부장 '선정 후 30일 안 현장 사무소는 힘들다' → 3단계안(선정 후 30일 전담 PM · 박람회 60일 전 사무소 · 입주 지정기간 상주 창구) — 탕정만
TJ_OFFICE = [("<b>선정 후 30일 안 현장 사무소 개설</b><p>전담 PM 배치 · 시공 품목은 인근 업체 우선 선정</p>",
              "<b>경인 지사(평택)를 탕정 거점으로</b><p>선정 후 30일 안 전담 PM 지정 · 쇼룸 상담 · 입예협 미팅 공간 · 시공 · A/S 출동 · 입주 지정기간 단지 내 상주 창구(협의)</p>")]
# 10-22 본부장(2차): 현장 사무소 개설 약속은 빼고 경인 지사(평택 · 쇼룸)를 거점으로 — tjv2.AI_FIX · pages21 · polish와 같은 말


def tj_post(doc):
    for a, b in TJ_OFFICE:
        doc = doc.replace(a, b)
    assert "선정 후 30일 안 현장 사무소" not in doc and "선정 후 30일 안 아산" not in doc, "탕정: 옛 30일 사무소 문구 남음"
    _left = re.findall(r".{0,20}(?:현장 사무소|사무소 개설|60일 전 아산|직영 4곳|직영 거점 4|협력 네트워크 8|협력 8곳|4 \+ 8|12개 지사).{0,20}", re.sub(r"<[^>]+>", " ", doc))
    assert not _left, f"탕정: 경인 지사 반영 전 문구 남음 {_left[:5]}"
    return doc


def main():
    only = [a for a in sys.argv[1:] if not a.startswith("--")]  # 예: python3 tjlight.py 요약제안서
    for name, n_dv, n_hi, label in JOBS:
        if only and name not in only:
            continue
        src = PFX + name + "_v2.html"
        assert os.path.exists(src), ("v2 HTML 없음 — build_tangjeong.py --v2 먼저", src)
        light(src, src[:-5] + "_밝은시안.html", n_dv, n_hi, label, EXTRA.get(name, ""), post=tj_post)


if __name__ == "__main__":
    main()

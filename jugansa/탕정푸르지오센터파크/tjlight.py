# -*- coding: utf-8 -*-
"""탕정 v2 밝은 바탕 시안(10-21 본부장 요청) — v2 HTML의 색만 바꿔 _v2_밝은시안.html/pdf로 낸다(내용 · 순서는 v2 그대로).

본문 쪽 = 아이보리 종이 + 네이비 글자 + 짙은 골드 강조. 표지 · 간지 · 연락처 · KEY POINT 띠 = 네이비 그대로.
색 기준(WCAG 대비, 아이보리 #FAF7F0 위): 글자 금색 #7A5716 = 6.1 · 라벨 금색 #866322 = 5.1 · 보조 회색 #5C6878 = 5.3 · 본문 #14243A.
금색 '채움'(막대 · 알약 · 강조 칸)은 글자 금색과 분리해 #C9A35A로 둔다(남색 글자 대비 7 이상).
화면을 그릴 때 두 단계 보정(FIX_JS): ① 남색 판(캡션 띠 · 배치도 구역 · 콜센터 원 등) 안은 네이비 색 체계로 되돌림
② 그래도 대비 3 미만인 글자는 남색 / 아이보리 중 잘 보이는 쪽으로 — 사진 위 캡션은 건드리지 않는다(휴대폰 모형 · 보증증권 견본은 원래 색).
사용: python3 tjlight.py  (먼저 build_tangjeong.py --v2 로 v2 HTML을 만든다)
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "엣지컴퍼니_탕정푸르지오센터파크_05_입주박람회_입찰제안서_v2.html")
OUT = os.path.join(HERE, "엣지컴퍼니_탕정푸르지오센터파크_05_입주박람회_입찰제안서_v2_밝은시안.html")

DARK = "--bg:#0D1E33;--gold:#EBCB8F;--gold2:#C8A86A;--ink:#F4F6F9;--sub:#B4BECA;--mute:#8595A8;--line:rgba(255,255,255,.13)"
LIGHT = "--bg:#FAF7F0;--gold:#7A5716;--gold2:#866322;--ink:#14243A;--sub:#3B4A5D;--mute:#5C6878;--line:rgba(13,30,51,.14)"
GOLD_FILL = "#C9A35A"
DARK_PAGES = ".page.cv,.page.dv"

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
  // ② 남은 글자 대비 3 미만 → 남색 / 아이보리 중 잘 보이는 쪽(사진 위 캡션은 제외)
  all.forEach(function(el){if(!ownText(el)||el.closest('.kp,.todo'))return;
    var s=getComputedStyle(el);if(s.display==='none'||s.visibility==='hidden')return;
    var fg=P(s.color);if(!fg||fg.a<.05)return;if(overImg(el,sec,imgs))return;
    var bg=eff(el),f=fg.a<1?blend(fg,bg):fg;if(cr(f,bg)>=3)return;
    el.style.color=cr(NAVY,bg)>=cr(PAPER,bg)?'#14243A':'#FAF7F0';el.setAttribute('data-fx','1');});
});
})();
</script>"""


def light_css(css):
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


def main():
    doc = open(SRC, encoding="utf-8").read()
    head, rest = doc.split("</head>", 1)
    head = re.sub(r"<style>(.*?)</style>", lambda m: "<style>" + light_css(m.group(1)) + "</style>", head, flags=re.S)
    head = head.replace("</style>", OVR + "</style>", 1) if head.count("</style>") == 1 else head + f"<style>{OVR}</style>"
    rest = re.sub(r"<style>(.*?)</style>", lambda m: "<style>" + light_css(m.group(1)) + "</style>", rest, flags=re.S)
    rest = re.sub(r'style="([^"]*)"', lambda m: 'style="' + light_css(m.group(1)) + '"', rest)
    rest = re.sub(r'(<section class="page(?![^"]*\b(?:cv|dv)\b)[^"]*">)(.*?)(</section>)', lambda m: m.group(1) + light_svg(m.group(2)) + m.group(3), rest, flags=re.S)
    assert rest.count("</body>") == 1
    rest = rest.replace("</body>", FIX_JS + "</body>")
    open(OUT, "w", encoding="utf-8").write(head + "</head>" + rest)
    print("HTML:", OUT)
    if "--no-pdf" not in sys.argv:
        sys.path.insert(0, os.path.join(HERE, "..", "요약제안서"))
        import build as B
        B.OUT_HTML, B.OUT_PDF = OUT, OUT[:-5] + ".pdf"
        B.build_pdf()


if __name__ == "__main__":
    main()

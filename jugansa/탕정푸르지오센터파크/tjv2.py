# -*- coding: utf-8 -*-
def apply(G):
    import json
    B = G["B"]
    json.dump([(i + 1, k, kw.get("sec"), kw.get("title"), kw.get("n"), kw.get("bl")) for i, (k, kw) in enumerate(B.PAGES)],
              open("/tmp/claude-0/tj_titles.json", "w", encoding="utf-8"), ensure_ascii=False)

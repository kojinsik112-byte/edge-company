# units.json + model4.js + tpl4.html → 박람회_행사장_비용.html (아티팩트 게시본)
import json, os
H = os.path.dirname(os.path.abspath(__file__))
U = json.load(open(f'{H}/units.json', encoding='utf-8'))
t = open(f'{H}/tpl4.html', encoding='utf-8').read()
assert t.count('/*MODEL*/') == 1 and t.count('/*DATA*/') == 1
t = t.replace('/*MODEL*/', open(f'{H}/model4.js', encoding='utf-8').read()).replace('/*DATA*/', json.dumps(U, ensure_ascii=False, separators=(',', ':')))
open(f'{H}/박람회_행사장_비용.html', 'w', encoding='utf-8').write(t)
print('bytes', len(t.encode()))

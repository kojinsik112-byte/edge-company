"""HWP(5.x) 본문 글자 추출 — 공고 · 지침서 원문을 notice.txt로. 사용: python3 jugansa/tools/hwp2txt.py 공고.hwp > notice.txt (hwpx는 zip 안 Contents/section*.xml을 읽는다)."""
import olefile, re, zlib, zipfile, struct, sys
def hwpx(path):
    z = zipfile.ZipFile(path)
    secs = sorted((n for n in z.namelist() if re.match(r"Contents/section\d+\.xml$", n)), key=lambda n: int(re.findall(r"\d+", n)[-1]))
    out = []
    for n in secs:
        x = z.read(n).decode("utf-8")
        for p in re.findall(r"<hp:p\b.*?</hp:p>", x, re.S):
            out.append("".join(re.findall(r"<hp:t\b[^>]*>(.*?)</hp:t>", p, re.S)))
    return re.sub(r"<[^>]+>", "", "\n".join(out)).replace("&lt;", "<").replace("&gt;", ">").replace("&amp;", "&")
def text(path):
    if zipfile.is_zipfile(path): return hwpx(path)
    ole = olefile.OleFileIO(path)
    hdr = ole.openstream('FileHeader').read()
    compressed = hdr[36] & 1
    out = []
    secs = sorted([e for e in ole.listdir() if e[0] == 'BodyText'], key=lambda e: int(e[1][7:]))
    for e in secs:
        data = ole.openstream(e).read()
        if compressed: data = zlib.decompress(data, -15)
        i = 0
        while i < len(data):
            h = struct.unpack_from('<I', data, i); i += 4
            tag = h[0] & 0x3ff; size = (h[0] >> 20) & 0xfff
            if size == 0xfff: size = struct.unpack_from('<I', data, i)[0]; i += 4
            rec = data[i:i+size]; i += size
            if tag == 67:
                s = []; j = 0
                while j < len(rec):
                    c = struct.unpack_from('<H', rec, j)[0]
                    if c in (1,2,3,11,12,14,15,16,17,18,21,22,23): j += 16; continue
                    if c in (4,5,6,7,8,19,20): j += 16; continue
                    if c == 9: s.append('\t'); j += 2; continue
                    if c in (10, 13): j += 2; continue
                    if c == 24: s.append('-'); j += 2; continue
                    if c == 30 or c == 31: s.append(' '); j += 2; continue
                    if c < 32: j += 2; continue
                    s.append(chr(c)); j += 2
                out.append(''.join(s))
    return '\n'.join(out)
if __name__ == '__main__':
    sys.stdout.write(text(sys.argv[1]).encode('utf-16','surrogatepass').decode('utf-16','replace'))

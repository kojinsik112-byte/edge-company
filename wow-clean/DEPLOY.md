# 와우클린 사이트 배포 가이드 (Netlify)

실제 인터넷 주소(URL)로 띄우는 방법입니다. **무료**이고, Netlify에서는 폰트(Pretendard·명조)까지 원본 그대로 나옵니다.

---

## 방법 1 — GitHub 연결 (추천, 자동 업데이트)

1. https://app.netlify.com 접속 → 가입/로그인 (GitHub 계정으로 바로 가능)
2. **Add new site › Import an existing project** 클릭
3. **GitHub** 선택 → 저장소 `kojinsik112-byte/edge-company` 선택
4. 배포 설정에서:
   - **Branch**: `claude/wow-clean-website-mobile-md43f9` (또는 main 병합 후 main)
   - **Publish directory**: `wow-clean`
   - **Build command**: 비워둠 (정적 사이트)
   - ※ 저장소 루트의 `netlify.toml`이 위 설정을 자동 적용하므로 그대로 Deploy 해도 됩니다.
5. **Deploy** → 몇 초 뒤 `랜덤이름.netlify.app` 주소 생성 → 폰에서 바로 접속!

이후 코드가 바뀌면 **자동으로 다시 배포**됩니다.

## 방법 2 — 드래그 앤 드롭 (가장 빠름, PC에서)

1. https://app.netlify.com/drop 접속
2. `wow-clean` 폴더를 **통째로 드래그** → 즉시 URL 생성 (계정 없이도 됨)

---

## 실제 도메인 연결 (예: wowclean.co.kr)

1. 가비아·후이즈 등에서 도메인 구입 (연 1~2만원대)
2. Netlify 사이트 → **Domain settings › Add a domain** → 구입한 도메인 입력
3. 안내되는 **DNS(네임서버/CNAME)** 를 도메인 업체에 등록
4. 몇 분~수 시간 뒤 `https://wowclean.co.kr` 로 접속 + 무료 SSL 자동 적용

## 배포 전 체크
- [ ] 대표번호 `1588-2424` → 실제 번호로 교체
- [ ] `assets/photos/` 에 실제 시공 사진 업로드 (README 참고)
- [ ] `assets/` 에 시공 영상 mp4 업로드 (선택)
- [ ] 카카오 채널 주소, 사업자 정보(상호·대표·등록번호) 입력
- [ ] 비용 가이드 표를 실제 요금으로 교체

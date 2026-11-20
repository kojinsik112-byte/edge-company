import { createRoot } from 'react-dom/client';
import App from './App';
import './index.css';

createRoot(document.getElementById('root')!).render(<App />);

// 홈페이지 배포판: 오프라인에서도 열리도록 서비스 워커 등록 (범위 /curtain-pro 한정)
if (__TARGET__ === 'web' && 'serviceWorker' in navigator && location.protocol === 'https:') {
  window.addEventListener('load', () => {
    navigator.serviceWorker.register('/curtain-pro-sw.js', { scope: '/curtain-pro' }).catch(() => undefined);
  });
}

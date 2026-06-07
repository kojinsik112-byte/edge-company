/* ============================================================
   ACRO — 코드로 생성하는 히어로 모션 + 푸터 웨이브
   외부 영상 파일 없이 Canvas 로 렌더링. 4K 선명 · 완벽 루프.
   prefers-reduced-motion 시 자동 정지(포스터 이미지가 대신 표시).
   ============================================================ */
(function () {
  "use strict";

  var reduce = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  if (reduce) return; // 모션 최소화 사용자는 정적 포스터만

  var NAVY = "10,26,63";
  var BLUE = "30,107,255";
  var LIGHT = "143,184,255";

  /* -------- 유틸: DPR 대응 리사이즈 -------- */
  function fit(canvas) {
    var dpr = Math.min(window.devicePixelRatio || 1, 2);
    var r = canvas.getBoundingClientRect();
    canvas.width = Math.max(1, Math.floor(r.width * dpr));
    canvas.height = Math.max(1, Math.floor(r.height * dpr));
    var ctx = canvas.getContext("2d");
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    return { w: r.width, h: r.height, ctx: ctx };
  }

  /* ============================================================
     1) HERO — 스마트홈 기기 연결 네트워크 + 블루투스 신호 링
     ============================================================ */
  (function hero() {
    var canvas = document.getElementById("heroCanvas");
    if (!canvas) return;
    var dim = fit(canvas), ctx = dim.ctx, W = dim.w, H = dim.h;

    var nodes = [];
    var rings = [];
    var hubs = [];

    function build() {
      nodes = [];
      var count = Math.round(Math.min(72, Math.max(28, (W * H) / 22000)));
      for (var i = 0; i < count; i++) {
        nodes.push({
          x: Math.random() * W,
          y: Math.random() * H,
          vx: (Math.random() - 0.5) * 0.22,
          vy: (Math.random() - 0.5) * 0.22,
          r: Math.random() * 1.6 + 0.8
        });
      }
      // 신호를 쏘는 허브 2~3개
      hubs = [];
      var hc = W < 700 ? 2 : 3;
      for (var j = 0; j < hc; j++) {
        hubs.push({
          x: W * (0.25 + 0.5 * Math.random()),
          y: H * (0.2 + 0.5 * Math.random()),
          t: Math.random() * 3
        });
      }
    }
    build();

    var LINK = 150;       // 노드 연결 거리
    var last = performance.now();

    function frame(now) {
      var dt = Math.min(40, now - last) / 16.67;
      last = now;
      ctx.clearRect(0, 0, W, H);

      // 노드 이동
      for (var i = 0; i < nodes.length; i++) {
        var n = nodes[i];
        n.x += n.vx * dt; n.y += n.vy * dt;
        if (n.x < 0 || n.x > W) n.vx *= -1;
        if (n.y < 0 || n.y > H) n.vy *= -1;
      }

      // 연결선 (constellation)
      for (var a = 0; a < nodes.length; a++) {
        for (var b = a + 1; b < nodes.length; b++) {
          var dx = nodes[a].x - nodes[b].x, dy = nodes[a].y - nodes[b].y;
          var d = Math.sqrt(dx * dx + dy * dy);
          if (d < LINK) {
            var o = (1 - d / LINK) * 0.22;
            ctx.strokeStyle = "rgba(" + LIGHT + "," + o + ")";
            ctx.lineWidth = 1;
            ctx.beginPath();
            ctx.moveTo(nodes[a].x, nodes[a].y);
            ctx.lineTo(nodes[b].x, nodes[b].y);
            ctx.stroke();
          }
        }
      }

      // 노드 점
      for (var k = 0; k < nodes.length; k++) {
        var p = nodes[k];
        ctx.fillStyle = "rgba(" + LIGHT + ",0.7)";
        ctx.beginPath();
        ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2);
        ctx.fill();
      }

      // 허브 + 주기적 블루투스 신호 링
      for (var h = 0; h < hubs.length; h++) {
        var hub = hubs[h];
        hub.t += 0.01 * dt;
        if (hub.t >= 3) { hub.t = 0; rings.push({ x: hub.x, y: hub.y, r: 0 }); }
        // 허브 글로우 코어
        var g = ctx.createRadialGradient(hub.x, hub.y, 0, hub.x, hub.y, 16);
        g.addColorStop(0, "rgba(" + BLUE + ",0.9)");
        g.addColorStop(1, "rgba(" + BLUE + ",0)");
        ctx.fillStyle = g;
        ctx.beginPath(); ctx.arc(hub.x, hub.y, 16, 0, Math.PI * 2); ctx.fill();
      }
      for (var ri = rings.length - 1; ri >= 0; ri--) {
        var rg = rings[ri];
        rg.r += 0.9 * dt;
        var maxR = 130;
        var op = Math.max(0, 1 - rg.r / maxR) * 0.5;
        if (op <= 0) { rings.splice(ri, 1); continue; }
        ctx.strokeStyle = "rgba(" + BLUE + "," + op + ")";
        ctx.lineWidth = 2;
        ctx.beginPath(); ctx.arc(rg.x, rg.y, rg.r, 0, Math.PI * 2); ctx.stroke();
      }

      raf = requestAnimationFrame(frame);
    }
    var raf = requestAnimationFrame(frame);

    var rt;
    window.addEventListener("resize", function () {
      clearTimeout(rt);
      rt = setTimeout(function () {
        dim = fit(canvas); ctx = dim.ctx; W = dim.w; H = dim.h; build();
      }, 200);
    });
  })();

  /* ============================================================
     2) FOOTER — 흐르는 블루투스 시그널 웨이브
     ============================================================ */
  (function footer() {
    var canvas = document.getElementById("footWave");
    if (!canvas) return;
    var dim = fit(canvas), ctx = dim.ctx, W = dim.w, H = dim.h;
    var t = 0;

    function wave(amp, speed, yBase, op, lw) {
      ctx.beginPath();
      for (var x = 0; x <= W; x += 6) {
        var y = yBase
          + Math.sin((x * 0.012) + t * speed) * amp
          + Math.sin((x * 0.005) - t * speed * 0.6) * amp * 0.5;
        if (x === 0) ctx.moveTo(x, y); else ctx.lineTo(x, y);
      }
      ctx.strokeStyle = "rgba(" + BLUE + "," + op + ")";
      ctx.lineWidth = lw;
      ctx.stroke();
    }

    function frame() {
      ctx.clearRect(0, 0, W, H);
      t += 0.02;
      wave(10, 1.0, H * 0.5, 0.30, 2);
      wave(16, 0.7, H * 0.55, 0.18, 1.5);
      wave(22, 0.5, H * 0.6, 0.10, 1);
      raf = requestAnimationFrame(frame);
    }
    var raf = requestAnimationFrame(frame);

    var rt;
    window.addEventListener("resize", function () {
      clearTimeout(rt);
      rt = setTimeout(function () { dim = fit(canvas); ctx = dim.ctx; W = dim.w; H = dim.h; }, 200);
    });
  })();
})();

/* ============================================================
   NEURAL SCENE — themed 3D constellations, scroll + mouse driven.
   Companion to neural-field.js (the abstract clustered background):
   where the field is ambience, a scene is a *figure* — a recognizable
   shape drawn in the same visual language (glowing nodes, capped
   edges, semantic color, breathing) that rotates and zooms with the
   user's scroll and tilts gently toward the cursor, anime.js-style.

   Shapes: brain (home hero), helm (Projects — Kubernetes), cube
   (Template — containers/lattice), globe (About — remote/worldwide),
   chart (Recruiter brief — evidence/metrics), signal (Contact —
   concentric broadcast rings). Mount via:
     <canvas data-neural-scene="brain" aria-hidden="true"></canvas>
   Technical guides keep only the passive neural-field ambient layer.

   Vanilla Canvas2D, no dependencies. Reduced motion => one static
   frame, no animation loop. Coarse pointers => fewer points, no tilt.
   ============================================================ */
(function () {
  "use strict";

  if (!window.requestAnimationFrame || !document.createElement("canvas").getContext) return;

  var REDUCED = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  var COARSE = window.matchMedia("(pointer: coarse)").matches;
  var FINE = window.matchMedia("(pointer: fine)").matches;
  var TAU = Math.PI * 2;
  var DPR = Math.min(window.devicePixelRatio || 1, 2);

  var COLORS = {
    cyan: "34,211,238",
    green: "52,211,153",
    amber: "251,191,36",
    violet: "167,139,250",
    bright: "110,231,255"
  };

  function rand(a, b) { return a + Math.random() * (b - a); }

  /* ---- shape generators: arrays of {x,y,z,color} in unit space ---- */

  function shapeBrain(n) {
    var pts = [];
    for (var i = 0; i < n; i++) {
      var r01 = Math.random();
      if (r01 < 0.82) {
        /* two wrinkled lobes */
        var side = Math.random() < 0.5 ? -1 : 1;
        var th = rand(0, TAU), ph = Math.acos(rand(-1, 1));
        var wr = 1 + 0.09 * Math.sin(6 * th + 2 * ph) * Math.sin(4 * ph);
        pts.push({
          x: side * 0.24 + Math.sin(ph) * Math.cos(th) * 0.42 * wr,
          y: Math.cos(ph) * 0.34 * wr - 0.04,
          z: Math.sin(ph) * Math.sin(th) * 0.30 * wr,
          color: Math.random() < 0.55 ? "cyan" : (Math.random() < 0.6 ? "violet" : "bright")
        });
      } else if (r01 < 0.95) {
        /* cerebellum */
        var th2 = rand(0, TAU), ph2 = Math.acos(rand(-1, 1));
        pts.push({
          x: Math.sin(ph2) * Math.cos(th2) * 0.18,
          y: 0.30 + Math.cos(ph2) * 0.10,
          z: -0.14 + Math.sin(ph2) * Math.sin(th2) * 0.13,
          color: "green"
        });
      } else {
        /* brainstem */
        var s = Math.random();
        pts.push({ x: rand(-0.03, 0.03), y: 0.34 + s * 0.16, z: -0.06 - s * 0.06, color: "amber" });
      }
    }
    return pts;
  }

  function shapeHelm(n) {
    var pts = [];
    var outer = Math.round(n * 0.42), hub = Math.round(n * 0.16);
    for (var i = 0; i < outer; i++) {
      var a = (i / outer) * TAU;
      pts.push({ x: Math.cos(a) * 0.56, y: Math.sin(a) * 0.56, z: rand(-0.05, 0.05),
                 color: Math.random() < 0.7 ? "cyan" : "bright" });
    }
    for (var j = 0; j < hub; j++) {
      var b = (j / hub) * TAU;
      pts.push({ x: Math.cos(b) * 0.16, y: Math.sin(b) * 0.16, z: rand(-0.04, 0.04), color: "green" });
    }
    var rest = n - outer - hub, perSpoke = Math.max(2, Math.floor(rest / 7));
    for (var s = 0; s < 7; s++) {
      var sa = (s / 7) * TAU;
      for (var k = 1; k <= perSpoke; k++) {
        var f = 0.16 + (k / (perSpoke + 1)) * 0.40;
        pts.push({ x: Math.cos(sa) * f, y: Math.sin(sa) * f, z: rand(-0.03, 0.03),
                   color: k === perSpoke ? "bright" : "cyan" });
      }
    }
    return pts;
  }

  function shapeCube(n) {
    var pts = [];
    var g = 3, sp = 0.36;
    for (var x = 0; x < g; x++) for (var y = 0; y < g; y++) for (var z = 0; z < g; z++) {
      var corner = (x % 2 === 0 && y % 2 === 0 && z % 2 === 0);
      pts.push({
        x: (x - 1) * sp + rand(-0.015, 0.015),
        y: (y - 1) * sp + rand(-0.015, 0.015),
        z: (z - 1) * sp + rand(-0.015, 0.015),
        color: corner ? "amber" : (Math.random() < 0.7 ? "cyan" : "green")
      });
    }
    /* orbiting satellites — pods around the cluster */
    for (var i = pts.length; i < n; i++) {
      var th = rand(0, TAU);
      pts.push({ x: Math.cos(th) * 0.62, y: rand(-0.3, 0.3), z: Math.sin(th) * 0.62, color: "violet" });
    }
    return pts;
  }

  function shapeGlobe(n) {
    var pts = [];
    for (var i = 0; i < n; i++) {
      var band = Math.random();
      var lat = band < 0.75 ? (Math.floor(rand(0, 5)) - 2) * 0.5 + rand(-0.06, 0.06) : rand(-1.2, 1.2);
      var lon = rand(0, TAU);
      var cr = Math.cos(lat) * 0.52;
      pts.push({
        x: Math.cos(lon) * cr, y: Math.sin(lat) * 0.52, z: Math.sin(lon) * cr,
        color: Math.random() < 0.6 ? "cyan" : (Math.random() < 0.5 ? "violet" : "green")
      });
    }
    return pts;
  }

  function shapeChart(n) {
    var pts = [];
    var bars = [0.30, 0.52, 0.42, 0.68, 0.58, 0.82];
    var perBar = Math.floor((n * 0.7) / bars.length);
    bars.forEach(function (hgt, bi) {
      var bx = -0.55 + bi * 0.22;
      for (var k = 0; k < perBar; k++) {
        var f = k / perBar;
        pts.push({
          x: bx + rand(-0.02, 0.02), y: 0.42 - f * hgt, z: rand(-0.04, 0.04),
          color: f > 0.85 ? (bi >= 4 ? "green" : "amber") : "cyan"
        });
      }
    });
    while (pts.length < n) {
      pts.push({ x: rand(-0.6, 0.6), y: 0.44, z: rand(-0.25, 0.25), color: "violet" });
    }
    return pts;
  }

  function shapeSignal(n) {
    var pts = [];
    var rings = [0.18, 0.34, 0.52];
    var perRing = Math.floor((n * 0.8) / rings.length);
    rings.forEach(function (rr, ri) {
      for (var i = 0; i < perRing; i++) {
        var a = (i / perRing) * TAU;
        pts.push({ x: Math.cos(a) * rr, y: rand(-0.03, 0.03) + ri * 0.02, z: Math.sin(a) * rr,
                   color: ri === 0 ? "green" : "cyan" });
      }
    });
    while (pts.length < n) {
      var f = Math.random();
      pts.push({ x: rand(-0.02, 0.02), y: -f * 0.42, z: rand(-0.02, 0.02), color: "bright" });
    }
    return pts;
  }

  var SHAPES = {
    brain: { gen: shapeBrain, count: 170, maxDist: 0.21, tiltX: 0.22 },
    helm: { gen: shapeHelm, count: 120, maxDist: 0.19, tiltX: 0.16 },
    cube: { gen: shapeCube, count: 44, maxDist: 0.42, tiltX: 0.35 },
    globe: { gen: shapeGlobe, count: 130, maxDist: 0.20, tiltX: 0.24 },
    chart: { gen: shapeChart, count: 120, maxDist: 0.18, tiltX: 0.30 },
    signal: { gen: shapeSignal, count: 110, maxDist: 0.22, tiltX: 0.55 }
  };

  /* k-nearest edges, capped degree 3 */
  function buildEdges(pts, maxDist) {
    var edges = [];
    var deg = pts.map(function () { return 0; });
    pts.forEach(function (a, i) {
      if (deg[i] >= 3) return;
      var near = [];
      pts.forEach(function (b, j) {
        if (i === j || deg[j] >= 3) return;
        var dx = a.x - b.x, dy = a.y - b.y, dz = a.z - b.z;
        var d = Math.sqrt(dx * dx + dy * dy + dz * dz);
        if (d < maxDist) near.push([d, j]);
      });
      near.sort(function (p, q) { return p[0] - q[0]; });
      for (var k = 0; k < Math.min(2, near.length) && deg[i] < 3; k++) {
        var j2 = near[k][1];
        edges.push([i, j2]);
        deg[i]++; deg[j2]++;
      }
    });
    return edges;
  }

  function mount(canvas, shapeName) {
    var spec = SHAPES[shapeName];
    if (!spec) return;
    var count = COARSE ? Math.round(spec.count * 0.55) : spec.count;
    var pts = spec.gen(count);
    pts.forEach(function (p) {
      p.phase = rand(0, TAU);
      p.period = rand(2800, 6400);
    });
    var edges = buildEdges(pts, spec.maxDist);
    var ctx = canvas.getContext("2d");
    var w = 0, h = 0;

    function resize() {
      var rect = canvas.getBoundingClientRect();
      w = Math.max(1, rect.width);
      h = Math.max(1, rect.height);
      canvas.width = w * DPR;
      canvas.height = h * DPR;
      canvas.style.width = w + "px";
      canvas.style.height = h + "px";
      ctx.setTransform(DPR, 0, 0, DPR, 0, 0);
    }
    resize();
    var rt = null;
    window.addEventListener("resize", function () {
      clearTimeout(rt); rt = setTimeout(resize, 160);
    });

    /* camera state: scroll drives rotation + zoom, mouse adds tilt */
    var mx = 0, my = 0, mxT = 0, myT = 0;
    if (FINE && !COARSE && !REDUCED) {
      window.addEventListener("mousemove", function (e) {
        mxT = (e.clientX / window.innerWidth - 0.5) * 2;
        myT = (e.clientY / window.innerHeight - 0.5) * 2;
      }, { passive: true });
    }

    function scrollProgress() {
      var rect = canvas.getBoundingClientRect();
      var vh = window.innerHeight || 1;
      /* 0 when the canvas top enters the viewport bottom, 1 when its
         bottom leaves the top — a full travel across the screen */
      return Math.min(1, Math.max(0, (vh - rect.top) / (vh + rect.height)));
    }

    var proj = { f: 2.4 };
    function render(t) {
      ctx.clearRect(0, 0, w, h);
      var sp = REDUCED ? 0.35 : scrollProgress();
      var drift = REDUCED ? 0 : t * 0.00006;
      mx += (mxT - mx) * 0.05;
      my += (myT - my) * 0.05;
      var rotY = drift + sp * 2.4 + mx * 0.35;
      var rotX = spec.tiltX + Math.sin(sp * Math.PI) * 0.12 + my * 0.18;
      var zoom = 1.06 - Math.abs(sp - 0.5) * 0.3;
      /* wide hero canvases: min(w,h) alone reads too small — let the
         figure claim real presence without overflowing the height */
      var size = Math.min(w * 0.46, h * 1.15) * zoom;
      var cx = w * 0.5, cy = h * 0.52;
      var cosY = Math.cos(rotY), sinY = Math.sin(rotY);
      var cosX = Math.cos(rotX), sinX = Math.sin(rotX);

      /* project all points */
      for (var i = 0; i < pts.length; i++) {
        var p = pts[i];
        var x1 = p.x * cosY + p.z * sinY;
        var z1 = -p.x * sinY + p.z * cosY;
        var y1 = p.y * cosX - z1 * sinX;
        var z2 = p.y * sinX + z1 * cosX;
        var per = proj.f / (proj.f + z2);
        p.sx = cx + x1 * size * per;
        p.sy = cy + y1 * size * per;
        p.sper = per;
      }

      /* edges */
      for (var e = 0; e < edges.length; e++) {
        var a = pts[edges[e][0]], b = pts[edges[e][1]];
        var ea = 0.2 * ((a.sper + b.sper) / 2);
        ctx.strokeStyle = "rgba(" + COLORS[a.color] + "," + ea.toFixed(3) + ")";
        ctx.lineWidth = 1;
        ctx.beginPath();
        ctx.moveTo(a.sx, a.sy);
        ctx.lineTo(b.sx, b.sy);
        ctx.stroke();
      }

      /* nodes: halo + core, breathing, nearer = bigger + brighter */
      for (var k = 0; k < pts.length; k++) {
        var q = pts[k];
        var br = REDUCED ? 0.75 : (Math.sin(t / q.period * TAU + q.phase) + 1) / 2;
        var alpha = Math.min(1, (0.28 + 0.5 * br) * q.sper);
        var r = (1.1 + 1.5 * br) * q.sper;
        var rgb = COLORS[q.color];
        ctx.fillStyle = "rgba(" + rgb + "," + (alpha * 0.15).toFixed(3) + ")";
        ctx.beginPath();
        ctx.arc(q.sx, q.sy, r * 2.8, 0, TAU);
        ctx.fill();
        ctx.fillStyle = "rgba(" + rgb + "," + alpha.toFixed(3) + ")";
        ctx.beginPath();
        ctx.arc(q.sx, q.sy, r, 0, TAU);
        ctx.fill();
      }
    }

    if (REDUCED) { render(0); return; }

    var raf = null;
    function tick(t) {
      raf = requestAnimationFrame(tick);
      if (document.hidden) return;
      render(t);
    }
    raf = requestAnimationFrame(tick);
    canvas.__neuralScene = { destroy: function () { if (raf) cancelAnimationFrame(raf); } };
  }

  function init() {
    document.querySelectorAll("[data-neural-scene]").forEach(function (canvas) {
      if (canvas.tagName !== "CANVAS") return;
      mount(canvas, canvas.getAttribute("data-neural-scene"));
    });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();

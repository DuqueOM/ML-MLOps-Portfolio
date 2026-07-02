/* ============================================================
   NEURAL SCENE — themed 3D constellations, scroll + mouse driven.
   Companion to neural-field.js (the abstract clustered background):
   where the field is ambience, a scene is a *figure* — a recognizable
   shape drawn in the neural visual language (glowing nodes, edges,
   semantic color, breathing) that rotates and zooms with the user's
   scroll and tilts gently toward the cursor, anime.js-style.

   v2 (user review round): shapes are normalized to one consistent
   footprint, edges are STRUCTURAL (rings, spokes, lattices — built
   by each generator) instead of nearest-neighbor mush, figures are
   bigger, and on portfolio pages the canvas is fixed full-viewport:
   the figure travels behind the content as you scroll, slowly
   dissolving into a particle cloud — assembly at the top, dispersion
   as you read. Home keeps its hero-scoped brain (the hero already
   has its own scroll choreography).
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

  /* ---- shape generators ----------------------------------------
     Each returns { pts, edges } — pts in unit space, edges as index
     pairs describing the shape's real structure (rim segments,
     spokes, lattices), so a helm reads as a wheel, not a flower. */

  function ring(pts, edges, n, fn, color, close) {
    var start = pts.length;
    for (var i = 0; i < n; i++) {
      var p = fn(i / n);
      p.color = p.color || color;
      pts.push(p);
      if (i > 0) edges.push([start + i - 1, start + i]);
    }
    if (close !== false) edges.push([start + n - 1, start]);
    return start;
  }

  function shapeBrain() {
    var pts = [], n = 165;
    for (var i = 0; i < n; i++) {
      var r01 = Math.random();
      if (r01 < 0.82) {
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
        var th2 = rand(0, TAU), ph2 = Math.acos(rand(-1, 1));
        pts.push({
          x: Math.sin(ph2) * Math.cos(th2) * 0.18,
          y: 0.30 + Math.cos(ph2) * 0.10,
          z: -0.14 + Math.sin(ph2) * Math.sin(th2) * 0.13,
          color: "green"
        });
      } else {
        var s = Math.random();
        pts.push({ x: rand(-0.03, 0.03), y: 0.34 + s * 0.16, z: -0.06 - s * 0.06, color: "amber" });
      }
    }
    return { pts: pts, edges: null, maxDist: 0.21, tiltX: 0.22 }; /* organic: k-nearest */
  }

  function shapeHelm() {
    var pts = [], edges = [];
    /* double outer rim */
    var rimA = ring(pts, edges, 28, function (f) {
      return { x: Math.cos(f * TAU) * 0.56, y: Math.sin(f * TAU) * 0.56, z: 0.02 };
    }, "cyan");
    var rimB = ring(pts, edges, 28, function (f) {
      return { x: Math.cos(f * TAU) * 0.64, y: Math.sin(f * TAU) * 0.64, z: -0.02 };
    }, "bright");
    /* rungs between the two rims every 4th node */
    for (var i = 0; i < 28; i += 4) edges.push([rimA + i, rimB + i]);
    /* hub */
    var hub = ring(pts, edges, 10, function (f) {
      return { x: Math.cos(f * TAU) * 0.14, y: Math.sin(f * TAU) * 0.14, z: 0.04 };
    }, "green");
    /* 7 straight spokes: hub -> inner rim, with handle knobs past the outer rim */
    for (var s = 0; s < 7; s++) {
      var a = (s / 7) * TAU;
      var prev = hub + Math.round((s / 7) * 10) % 10;
      for (var k = 1; k <= 3; k++) {
        var f = 0.14 + (k / 3) * 0.42;
        pts.push({ x: Math.cos(a) * f, y: Math.sin(a) * f, z: 0.02, color: "cyan" });
        edges.push([prev, pts.length - 1]);
        prev = pts.length - 1;
      }
      /* knob outside the rim — the classic helm handle */
      pts.push({ x: Math.cos(a) * 0.74, y: Math.sin(a) * 0.74, z: 0, color: "amber" });
      edges.push([prev, pts.length - 1]);
    }
    return { pts: pts, edges: edges, tiltX: 0.42 };
  }

  function shapeCube() {
    var pts = [], edges = [];
    var g = 3, sp = 0.38;
    var idx = function (x, y, z) { return x * g * g + y * g + z; };
    for (var x = 0; x < g; x++) for (var y = 0; y < g; y++) for (var z = 0; z < g; z++) {
      var corner = (x !== 1 && y !== 1 && z !== 1);
      pts.push({
        x: (x - 1) * sp, y: (y - 1) * sp, z: (z - 1) * sp,
        color: corner ? "amber" : (Math.random() < 0.7 ? "cyan" : "green")
      });
    }
    /* orthogonal lattice edges — reads as a container stack */
    for (var a = 0; a < g; a++) for (var b = 0; b < g; b++) for (var c = 0; c < g - 1; c++) {
      edges.push([idx(a, b, c), idx(a, b, c + 1)]);
      edges.push([idx(a, c, b), idx(a, c + 1, b)]);
      edges.push([idx(c, a, b), idx(c + 1, a, b)]);
    }
    /* orbiting pods */
    var ringStart = ring(pts, edges, 14, function (f) {
      return { x: Math.cos(f * TAU) * 0.82, y: Math.sin(f * TAU * 2) * 0.1, z: Math.sin(f * TAU) * 0.82 };
    }, "violet");
    return { pts: pts, edges: edges, tiltX: 0.42, ringStart: ringStart };
  }

  function shapeGlobe() {
    var pts = [], edges = [];
    var lats = [-0.9, -0.45, 0, 0.45, 0.9];
    lats.forEach(function (la) {
      var r = Math.cos(la) * 0.58, y = Math.sin(la) * 0.58;
      var count = Math.max(8, Math.round(24 * Math.cos(la)));
      ring(pts, edges, count, function (f) {
        return { x: Math.cos(f * TAU) * r, y: y, z: Math.sin(f * TAU) * r };
      }, "cyan");
    });
    /* two meridians */
    [0, Math.PI / 2].forEach(function (lon) {
      ring(pts, edges, 20, function (f) {
        var la = f * TAU;
        return {
          x: Math.cos(lon) * Math.cos(la) * 0.58,
          y: Math.sin(la) * 0.58,
          z: Math.sin(lon) * Math.cos(la) * 0.58,
          color: "violet"
        };
      }, "violet");
    });
    /* a few green "presence" markers */
    for (var i = 0; i < 8; i++) {
      var la2 = rand(-1, 1), lo2 = rand(0, TAU);
      pts.push({ x: Math.cos(lo2) * Math.cos(la2) * 0.6, y: Math.sin(la2) * 0.6,
                 z: Math.sin(lo2) * Math.cos(la2) * 0.6, color: "green" });
    }
    return { pts: pts, edges: edges, tiltX: 0.3 };
  }

  function shapeChart() {
    var pts = [], edges = [];
    var bars = [0.34, 0.55, 0.45, 0.72, 0.62, 0.9];
    var tops = [];
    /* baseline */
    var base = ring(pts, edges, bars.length, function (f) {
      return { x: -0.58 + f * 1.4, y: 0.5, z: 0 };
    }, "violet", false);
    bars.forEach(function (hgt, bi) {
      var bx = -0.58 + (bi / bars.length) * 1.4;
      var prev = base + bi;
      var steps = 3 + Math.round(hgt * 4);
      for (var k = 1; k <= steps; k++) {
        pts.push({ x: bx, y: 0.5 - (k / steps) * hgt, z: 0,
                   color: k === steps ? (bi >= 4 ? "green" : "amber") : "cyan" });
        edges.push([prev, pts.length - 1]);
        prev = pts.length - 1;
      }
      tops.push(prev);
    });
    /* trend line across the bar tops — the rising metric */
    for (var t = 0; t < tops.length - 1; t++) edges.push([tops[t], tops[t + 1]]);
    return { pts: pts, edges: edges, tiltX: 0.16 };
  }

  function shapeSignal() {
    var pts = [], edges = [];
    [0.2, 0.38, 0.56].forEach(function (rr, ri) {
      ring(pts, edges, 12 + ri * 8, function (f) {
        return { x: Math.cos(f * TAU) * rr, y: -0.05 + ri * 0.03, z: Math.sin(f * TAU) * rr };
      }, ri === 0 ? "green" : "cyan");
    });
    /* beacon mast */
    var prev = null;
    for (var i = 0; i <= 5; i++) {
      pts.push({ x: 0, y: -0.05 - (i / 5) * 0.5, z: 0, color: "bright" });
      if (prev !== null) edges.push([prev, pts.length - 1]);
      prev = pts.length - 1;
    }
    return { pts: pts, edges: edges, tiltX: 0.5 };
  }

  var SHAPES = { brain: shapeBrain, helm: shapeHelm, cube: shapeCube,
                 globe: shapeGlobe, chart: shapeChart, signal: shapeSignal };

  /* nearest-neighbor edges, only for organic shapes (brain) */
  function knnEdges(pts, maxDist) {
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
        edges.push([i, near[k][1]]);
        deg[i]++; deg[near[k][1]]++;
      }
    });
    return edges;
  }

  /* normalize every shape to the same footprint so tabs feel equal */
  function normalize(pts) {
    var maxR = 0;
    pts.forEach(function (p) {
      var r = Math.sqrt(p.x * p.x + p.y * p.y + p.z * p.z);
      if (r > maxR) maxR = r;
    });
    var s = maxR > 0 ? 0.62 / maxR : 1;
    pts.forEach(function (p) { p.x *= s; p.y *= s; p.z *= s; });
  }

  function mount(canvas, shapeName) {
    var gen = SHAPES[shapeName];
    if (!gen) return;
    var shape = gen();
    var pts = shape.pts;
    normalize(pts);
    /* mobile thinning only for organic shapes (edges built after the
       filter) — structural shapes keep their exact edge indices */
    if (COARSE && !shape.edges) pts = pts.filter(function (_, i) { return i % 3 !== 2; });
    var edges = shape.edges || knnEdges(pts, shape.maxDist || 0.2);
    pts.forEach(function (p) {
      p.phase = rand(0, TAU);
      p.period = rand(2800, 6400);
      /* dispersion target for the full-page scroll morph */
      var th = rand(0, TAU), ph = Math.acos(rand(-1, 1)), rr = rand(0.7, 1.25);
      p.dx = Math.sin(ph) * Math.cos(th) * rr;
      p.dy = Math.cos(ph) * rr;
      p.dz = Math.sin(ph) * Math.sin(th) * rr;
    });

    /* portfolio pages AND the home hero: promote the canvas to a fixed
       full-viewport layer so the figure travels behind the content
       while reading, dissolving into particles as scroll deepens */
    var fullPage = !!(canvas.closest(".portfolio-page") || canvas.closest(".ml-home"));
    if (fullPage) canvas.classList.add("pf-scene-page");

    var ctx = canvas.getContext("2d");
    var w = 0, h = 0;

    function resize() {
      var rect = fullPage
        ? { width: window.innerWidth, height: window.innerHeight }
        : canvas.getBoundingClientRect();
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

    var mx = 0, my = 0, mxT = 0, myT = 0;
    if (FINE && !COARSE && !REDUCED) {
      window.addEventListener("mousemove", function (e) {
        mxT = (e.clientX / window.innerWidth - 0.5) * 2;
        myT = (e.clientY / window.innerHeight - 0.5) * 2;
      }, { passive: true });
    }

    function scrollProgress() {
      if (fullPage) {
        var doc = document.documentElement;
        var max = doc.scrollHeight - doc.clientHeight;
        return max > 0 ? Math.min(1, Math.max(0, doc.scrollTop / max)) : 0;
      }
      var rect = canvas.getBoundingClientRect();
      var vh = window.innerHeight || 1;
      return Math.min(1, Math.max(0, (vh - rect.top) / (vh + rect.height)));
    }

    function ease(x) { return x * x * (3 - 2 * x); }

    var proj = { f: 2.4 };
    function render(t) {
      ctx.clearRect(0, 0, w, h);
      var sp = REDUCED ? 0.35 : scrollProgress();
      var drift = REDUCED ? 0 : t * 0.00006;
      mx += (mxT - mx) * 0.05;
      my += (myT - my) * 0.05;
      /* dispersion morph: only on full-page scenes — the figure holds
         through the hero, then dissolves into a drifting cloud */
      var morph = fullPage ? ease(Math.min(1, Math.max(0, (sp - 0.16) / 0.55))) : 0;
      var rotY = drift + sp * (fullPage ? 3.2 : 2.4) + mx * 0.35;
      var rotX = shape.tiltX + Math.sin(sp * Math.PI) * 0.12 + my * 0.18;
      var zoom = fullPage
        ? 1 + morph * 0.7
        : 1.06 - Math.abs(sp - 0.5) * 0.3;
      var size = (fullPage ? Math.min(w, h) * 0.62 : Math.min(w * 0.52, h * 1.3)) * zoom;
      var cx = fullPage ? w * (0.72 - morph * 0.22) : w * 0.5;
      var cy = fullPage ? h * (0.42 + morph * 0.12) : h * 0.52;
      var cosY = Math.cos(rotY), sinY = Math.sin(rotY);
      var cosX = Math.cos(rotX), sinX = Math.sin(rotX);
      var fadeE = 1 - morph * 0.85; /* edges dissolve first */
      var fadeN = 1 - morph * 0.35;

      for (var i = 0; i < pts.length; i++) {
        var p = pts[i];
        var ox = p.x + (p.dx - p.x) * morph;
        var oy = p.y + (p.dy - p.y) * morph;
        var oz = p.z + (p.dz - p.z) * morph;
        var x1 = ox * cosY + oz * sinY;
        var z1 = -ox * sinY + oz * cosY;
        var y1 = oy * cosX - z1 * sinX;
        var z2 = oy * sinX + z1 * cosX;
        var per = proj.f / (proj.f + z2);
        p.sx = cx + x1 * size * per;
        p.sy = cy + y1 * size * per;
        p.sper = per;
      }

      if (fadeE > 0.02) {
        for (var e = 0; e < edges.length; e++) {
          var a = pts[edges[e][0]], b = pts[edges[e][1]];
          if (!a || !b) continue;
          var ea = 0.22 * ((a.sper + b.sper) / 2) * fadeE;
          ctx.strokeStyle = "rgba(" + COLORS[a.color] + "," + ea.toFixed(3) + ")";
          ctx.lineWidth = 1;
          ctx.beginPath();
          ctx.moveTo(a.sx, a.sy);
          ctx.lineTo(b.sx, b.sy);
          ctx.stroke();
        }
      }

      for (var k = 0; k < pts.length; k++) {
        var q = pts[k];
        var br = REDUCED ? 0.75 : (Math.sin(t / q.period * TAU + q.phase) + 1) / 2;
        var alpha = Math.min(1, (0.3 + 0.5 * br) * q.sper * fadeN);
        var r = (1.2 + 1.6 * br) * q.sper;
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

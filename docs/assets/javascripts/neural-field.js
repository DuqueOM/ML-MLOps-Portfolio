/* ============================================================
   NEURAL FIELD — organic, intentional network background.
   Vanilla Canvas2D, no dependencies. Loaded on every page via
   mkdocs.yml (extra_javascript), so it must run unconditionally —
   unlike home.js/portfolio.js it does NOT gate on .ml-home or
   .portfolio-page, because its job is to reach pages that have
   neither (ADRs, deployment guides, runbooks).

   Design intent (see docs/decisions — this mirrors two rounds of
   design review): clusters of uneven size instead of a uniform
   particle scatter, at most 3-4 edges per node (never a full mesh),
   three movement classes (fixed / slow-drift / orbital) instead of
   everything floating uniformly, real depth via three speed/size
   layers, semantic color (cyan=data, green=healthy pipeline,
   amber=validation, violet=background/ambient), asynchronous
   "breathing" glow per node, and pulses that travel an intentional
   multi-hop path instead of firing on random edges. No literal
   "Input -> Training -> Deploy" diagram is ever drawn — the
   sequence is implied by cluster order and pulse direction only.

   Phase 4 (this revision): slow topology evolution — every ~10-16s
   one intra-cluster edge fades out while a new one fades in, and
   pulse paths are rebuilt periodically, so the network visibly
   "keeps learning" — plus restrained cursor reactivity: proximity
   makes nearby nodes bloom, a dwell (cursor at rest near a node)
   fires a short pulse from it, and a click fires a small burst.
   All three are cooldown-gated so they read as rare, special events
   rather than a toy that reacts to every pixel of mouse travel.
   The ambient preset stays static and non-reactive by design.
   ============================================================ */
(function () {
  "use strict";

  if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) return;
  if (!window.requestAnimationFrame || !document.createElement("canvas").getContext) return;

  var COARSE = window.matchMedia("(pointer: coarse)").matches;
  var FINE = window.matchMedia("(pointer: fine)").matches;
  var TAU = Math.PI * 2;
  var DPR = Math.min(window.devicePixelRatio || 1, 2);

  var COLORS = {
    cyan: "34,211,238",
    green: "52,211,153",
    amber: "251,191,36",
    violet: "167,139,250"
  };

  /* near / mid / far — size, brightness and drift speed multipliers.
     "near" is also the only layer that responds to setParallax(). */
  var LAYERS = [
    { size: 1.3, alpha: 1.15, speed: 1.35 },
    { size: 1.0, alpha: 1.0, speed: 1.0 },
    { size: 0.72, alpha: 0.62, speed: 0.6 }
  ];

  var PRESETS = {
    hero: { clusters: 5, perCluster: [4, 8], layered: true, ordered: true,
            pulses: "path", pulseGap: [3600, 5600], maxAlpha: 0.85,
            coarseScale: 0.55, evolve: true, reactive: true },
    rail: { clusters: 4, perCluster: [4, 7], layered: true, ordered: true,
            pulses: "path", pulseGap: [4600, 6600], maxAlpha: 0.65,
            coarseScale: 0.55, evolve: true, reactive: true },
    editorial: { clusters: 3, perCluster: [3, 6], layered: true, ordered: false,
                 pulses: "simple", pulseGap: [8000, 12000], maxAlpha: 0.5,
                 coarseScale: 0.55, evolve: true, reactive: true },
    ambient: { clusters: 3, perCluster: [3, 5], layered: false, ordered: false,
               pulses: "none", pulseGap: [0, 0], maxAlpha: 0.22,
               coarseScale: 0, evolve: false, reactive: false }
  };

  function rand(min, max) { return min + Math.random() * (max - min); }
  function dist(a, b) { var dx = a.bx - b.bx, dy = a.by - b.by; return Math.sqrt(dx * dx + dy * dy); }

  function pickColor(preset) {
    if (preset.pulses === "none") return Math.random() < 0.72 ? "violet" : "cyan";
    var r = Math.random();
    return r < 0.45 ? "cyan" : r < 0.8 ? "green" : r < 0.93 ? "amber" : "violet";
  }

  /* ---- build clusters + capped-degree edges ---- */
  function buildField(preset, scale) {
    var n = Math.max(1, Math.round(preset.clusters * scale));
    var clusters = [];
    var nodes = [];

    for (var c = 0; c < n; c++) {
      var slot = n > 1 ? (c + 0.5) / n : 0.5;
      var jitter = preset.ordered ? 0.07 : 0.18;
      var cx = Math.min(0.94, Math.max(0.06, slot + rand(-jitter, jitter)));
      var cy = rand(0.22, 0.78);
      var layer = preset.layered ? (c % 3) : 1;
      var count = Math.max(3, Math.round(rand(preset.perCluster[0], preset.perCluster[1]) * scale));
      var clusterNodes = [];

      for (var i = 0; i < count; i++) {
        var angle = rand(0, TAU);
        var radius = rand(0.016, 0.065);
        var node = {
          cluster: c, layer: layer,
          cls: "B",
          bx: cx + Math.cos(angle) * radius,
          by: cy + Math.sin(angle) * radius,
          cx: cx, cy: cy,
          orbitR: rand(0.014, 0.032),
          orbitSpeed: rand(0.00007, 0.00016) * (Math.random() < 0.5 ? 1 : -1),
          orbitPhase: rand(0, TAU),
          driftPhase: rand(0, TAU),
          driftPeriod: rand(16000, 38000),
          driftAmp: rand(0.007, 0.017),
          breathePhase: rand(0, TAU),
          breathePeriod: rand(3000, 6200),
          baseR: rand(1.8, 3.4),
          color: pickColor(preset),
          boost: 0,
          degree: 0
        };
        clusterNodes.push(node);
        nodes.push(node);
      }

      /* class mix: one fixed anchor, then ~20% orbital around it, rest slow drift */
      clusterNodes[0].cls = "A";
      clusterNodes[0].bx = cx; clusterNodes[0].by = cy;
      for (var j = 1; j < clusterNodes.length; j++) {
        clusterNodes[j].cls = Math.random() < 0.22 ? "C" : (Math.random() < 0.35 ? "A" : "B");
      }
      clusters.push({ cx: cx, cy: cy, nodes: clusterNodes, layer: layer, anchor: clusterNodes[0] });
    }

    nodes.forEach(function (node, i) { node.id = i; });

    /* intra-cluster edges: each node connects to at most 2 extra
       nearest neighbors, capped total degree of 4 */
    var edges = [];
    function edgeExists(a, b) {
      for (var k = 0; k < edges.length; k++) {
        var e = edges[k];
        if ((e.a === a && e.b === b) || (e.a === b && e.b === a)) return true;
      }
      return false;
    }
    clusters.forEach(function (cl) {
      cl.nodes.forEach(function (a) {
        if (a.degree >= 4) return;
        var candidates = cl.nodes
          .filter(function (b) { return b !== a && b.degree < 4 && !edgeExists(a, b); })
          .sort(function (b1, b2) { return dist(a, b1) - dist(a, b2); });
        var need = Math.min(2, candidates.length, 4 - a.degree);
        for (var k = 0; k < need; k++) {
          var b = candidates[k];
          edges.push({ a: a, b: b, bridge: false });
          a.degree++; b.degree++;
        }
      });
    });

    /* bridge edges: connect clusters left-to-right (or arbitrary order
       for abstract presets) via their most-central node — this is what
       lets a pulse cross from one cluster to the next. No line is ever
       drawn between cluster *centers*, only these normal node-to-node
       edges, so nothing reads as a deliberate diagram. */
    var order = clusters.slice().sort(function (c1, c2) { return c1.cx - c2.cx; });
    function central(cluster) {
      var best = cluster.nodes[0], bestD = Infinity;
      cluster.nodes.forEach(function (nd) {
        var dx = nd.bx - cluster.cx, dy = nd.by - cluster.cy;
        var d = dx * dx + dy * dy;
        if (d < bestD) { bestD = d; best = nd; }
      });
      return best;
    }
    var bridgeEntry = [];
    for (var ci = 0; ci < order.length - 1; ci++) {
      var from = central(order[ci]);
      var to = central(order[ci + 1]);
      edges.push({ a: from, b: to, bridge: true });
      bridgeEntry.push(to);
    }

    return { clusters: order, nodes: nodes, edges: edges, bridgeEntry: bridgeEntry };
  }

  /* adjacency for path-walking (pulses + cursor walks) */
  function adjacency(field) {
    var map = {};
    field.nodes.forEach(function (n) { map[n.id] = []; });
    field.edges.forEach(function (e) {
      if (e.dying) return;
      map[e.a.id].push(e.b);
      map[e.b.id].push(e.a);
    });
    return map;
  }

  /* one intentional walk: start at the first cluster's anchor, take
     0-1 intra-cluster hop, then the bridge edge, repeat across every
     cluster in order, ending with one final intra hop. Two calls with
     different random hops give visibly distinct "camino" variants. */
  function buildPath(field, adj) {
    if (field.clusters.length < 2) return null;
    adj = adj || adjacency(field);
    var path = [];
    var cur = field.clusters[0].anchor;
    path.push(cur);
    for (var ci = 0; ci < field.clusters.length; ci++) {
      var cluster = field.clusters[ci];
      var inCluster = adj[cur.id].filter(function (nb) { return nb.cluster === cluster.cluster; });
      if (inCluster.length && Math.random() < 0.6) {
        var hop = inCluster[(Math.random() * inCluster.length) | 0];
        if (hop !== cur) { path.push(hop); cur = hop; }
      }
      if (ci < field.clusters.length - 1) {
        var bridge = adj[cur.id].filter(function (nb) { return nb.cluster !== cluster.cluster; })[0];
        if (!bridge) {
          /* current node has no bridge — fall back to the cluster's
             designated bridge-out node (its central node) */
          var central = field.clusters[ci].anchor;
          var toNext = adj[central.id].filter(function (nb) { return nb.cluster === field.clusters[ci + 1].cluster; })[0];
          if (toNext) { path.push(central); path.push(toNext); cur = toNext; continue; }
        } else {
          path.push(bridge);
          cur = bridge;
        }
      }
    }
    return path.length > 1 ? path : null;
  }

  /* ---- one running instance on one canvas ---- */
  function mount(canvas, presetName, opts) {
    var preset = PRESETS[presetName];
    if (!preset) return;
    if (COARSE && preset.coarseScale === 0) return; /* ambient skips mobile entirely */

    var scale = COARSE ? preset.coarseScale : 1;
    var ctx = canvas.getContext("2d");
    var field = buildField(preset, scale);
    var adj = adjacency(field);
    var w = 0, h = 0;
    var parallax = 0; /* set via setParallax(), affects layer 0 (near) only */
    var pulses = [];
    var nextPulseAt = performance.now() + rand(preset.pulseGap[0] || 4000, preset.pulseGap[1] || 8000) * 0.4;
    var paths = preset.pulses === "path" ? [buildPath(field, adj), buildPath(field, adj)].filter(Boolean) : [];
    var pathIdx = 0;

    function resize() {
      var rect = canvas.parentElement === document.body
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
    var resizeTimer = null;
    window.addEventListener("resize", function () {
      clearTimeout(resizeTimer);
      resizeTimer = setTimeout(resize, 160);
    });

    /* current draw position for a node this frame (anchors/drift first,
       orbitals depend on their anchor's position so are resolved after) */
    function place(node, t) {
      var L = LAYERS[node.layer] || LAYERS[1];
      var px = node.bx, py = node.by;
      if (node.cls === "B") {
        var tp = t / node.driftPeriod * TAU * L.speed + node.driftPhase;
        px += Math.sin(tp) * node.driftAmp;
        py += Math.cos(tp * 0.82) * node.driftAmp * 0.7;
      }
      if (node.layer === 0) px += parallax * 0.045;
      node.drawX = px * w;
      node.drawY = py * h;
    }

    function placeOrbitals(t) {
      field.clusters.forEach(function (cl) {
        cl.nodes.forEach(function (node) {
          if (node.cls !== "C") return;
          var L = LAYERS[node.layer] || LAYERS[1];
          var tp = t * node.orbitSpeed * L.speed * 1000 + node.orbitPhase;
          node.drawX = cl.anchor.drawX + Math.cos(tp) * node.orbitR * w;
          node.drawY = cl.anchor.drawY + Math.sin(tp) * node.orbitR * h * 0.8;
        });
      });
    }

    function breathe(node, t) {
      return (Math.sin(t / node.breathePeriod * TAU + node.breathePhase) + 1) / 2;
    }

    /* ---- Phase 4a: topology evolution ------------------------------
       Every EVO_GAP one intra-cluster edge starts dying (alpha ramps
       to 0 over EVO_FADE, then it's removed) and one new intra-cluster
       edge is born (alpha ramps up from 0). Degree caps are respected,
       bridges are never touched (pulse paths must keep working), and a
       node is never left with zero edges. Every third evolution the
       pulse paths are rebuilt so the "caminos" themselves change. */
    var EVO_FADE = 1800;
    var evoNextAt = performance.now() + rand(9000, 15000);
    var evoCount = 0;

    function evoAlpha(e, t) {
      if (e.born) {
        var up = Math.min(1, (t - e.born) / EVO_FADE);
        if (up >= 1) e.born = 0;
        else return up;
      }
      if (e.dying) return Math.max(0, 1 - (t - e.dying) / EVO_FADE);
      return 1;
    }

    function evolve(t) {
      if (!preset.evolve || t < evoNextAt) return;
      evoNextAt = t + rand(10000, 16000);
      evoCount++;

      /* retire one intra-cluster edge whose endpoints keep >=1 other edge */
      var candidates = field.edges.filter(function (e) {
        return !e.bridge && !e.dying && e.a.degree > 1 && e.b.degree > 1;
      });
      if (candidates.length) {
        var dying = candidates[(Math.random() * candidates.length) | 0];
        dying.dying = t;
        dying.a.degree--; dying.b.degree--;
      }

      /* grow one new intra-cluster edge between currently-unlinked nodes */
      var cl = field.clusters[(Math.random() * field.clusters.length) | 0];
      var open = cl.nodes.filter(function (nd) { return nd.degree < 4; });
      outer:
      for (var i = 0; i < open.length; i++) {
        for (var j = i + 1; j < open.length; j++) {
          var a = open[i], b = open[j];
          var linked = field.edges.some(function (e) {
            return !e.dying && ((e.a === a && e.b === b) || (e.a === b && e.b === a));
          });
          if (!linked) {
            field.edges.push({ a: a, b: b, bridge: false, born: t });
            a.degree++; b.degree++;
            break outer;
          }
        }
      }

      /* purge fully-faded edges, refresh adjacency + occasionally paths */
      field.edges = field.edges.filter(function (e) {
        return !(e.dying && t - e.dying >= EVO_FADE);
      });
      adj = adjacency(field);
      if (preset.pulses === "path" && evoCount % 3 === 0) {
        paths = [buildPath(field, adj), buildPath(field, adj)].filter(Boolean);
      }
    }

    function drawEdges(t) {
      field.edges.forEach(function (e) {
        var La = LAYERS[e.a.layer] || LAYERS[1];
        var boost = 1 + Math.max(e.a.boost, e.b.boost) * 0.9;
        var alpha = preset.maxAlpha * 0.26 *
          ((La.alpha + (LAYERS[e.b.layer] || LAYERS[1]).alpha) / 2) *
          evoAlpha(e, t) * boost;
        ctx.strokeStyle = "rgba(" + COLORS[e.a.color] + "," + Math.min(1, alpha).toFixed(3) + ")";
        ctx.lineWidth = 1;
        ctx.beginPath();
        ctx.moveTo(e.a.drawX, e.a.drawY);
        ctx.lineTo(e.b.drawX, e.b.drawY);
        ctx.stroke();
      });
    }

    function drawNodes(t) {
      field.nodes.forEach(function (node) {
        var L = LAYERS[node.layer] || LAYERS[1];
        var glow = 0.55 + 0.45 * breathe(node, t);
        var boost = 1 + node.boost;
        var r = node.baseR * L.size * (0.86 + 0.24 * glow) * (1 + node.boost * 0.45);
        var alpha = Math.min(1, preset.maxAlpha * L.alpha * (0.55 + 0.45 * glow) * boost);
        var rgb = COLORS[node.color];
        /* soft halo first, core dot on top — reads as a glow without
           the cost of ctx.shadowBlur */
        ctx.fillStyle = "rgba(" + rgb + "," + (alpha * 0.16).toFixed(3) + ")";
        ctx.beginPath();
        ctx.arc(node.drawX, node.drawY, r * 2.7, 0, TAU);
        ctx.fill();
        ctx.fillStyle = "rgba(" + rgb + "," + alpha.toFixed(3) + ")";
        ctx.beginPath();
        ctx.arc(node.drawX, node.drawY, r, 0, TAU);
        ctx.fill();
        /* cursor-boost decays exponentially each frame */
        if (node.boost > 0.01) node.boost *= 0.94;
        else node.boost = 0;
      });
    }

    /* ---- pulses: travel an intentional path, pausing at each node ---- */
    var HOP_MS = 650, PAUSE_MS = 200;
    function maybeSpawnPulse(t) {
      if (preset.pulses === "none" || t < nextPulseAt) return;
      nextPulseAt = t + rand(preset.pulseGap[0], preset.pulseGap[1]);
      if (preset.pulses === "path" && paths.length) {
        var path = paths[pathIdx % paths.length];
        pathIdx++;
        var warn = Math.random() < 0.18;
        pulses.push({
          path: path, seg: 0, segStart: t, paused: false,
          color: warn ? "amber" : "cyan"
        });
      } else if (preset.pulses === "simple" && field.edges.length) {
        var e = field.edges[(Math.random() * field.edges.length) | 0];
        pulses.push({ path: [e.a, e.b], seg: 0, segStart: t, paused: false, color: "cyan" });
      }
    }

    function drawPulses(t) {
      pulses = pulses.filter(function (p) { return p.seg < p.path.length - 1 || p.done; });
      pulses.forEach(function (p) {
        if (p.done) return;
        var a = p.path[p.seg], b = p.path[p.seg + 1];
        var elapsed = t - p.segStart;
        if (p.paused) {
          if (elapsed >= PAUSE_MS) { p.paused = false; p.segStart = t; }
          return;
        }
        var frac = Math.min(1, elapsed / HOP_MS);
        /* color resolves toward green as the pulse nears the end of its path */
        var nearEnd = p.seg >= p.path.length - 2;
        var col = p.color === "amber" ? "amber" : (nearEnd ? "green" : "cyan");
        var x = a.drawX + (b.drawX - a.drawX) * frac;
        var y = a.drawY + (b.drawY - a.drawY) * frac;
        ctx.fillStyle = "rgba(" + COLORS[col] + ",0.95)";
        ctx.beginPath();
        ctx.arc(x, y, 3.1, 0, TAU);
        ctx.fill();
        ctx.strokeStyle = "rgba(" + COLORS[col] + ",0.4)";
        ctx.lineWidth = 2;
        ctx.beginPath();
        ctx.moveTo(a.drawX, a.drawY);
        ctx.lineTo(x, y);
        ctx.stroke();
        if (frac >= 1) {
          p.seg++;
          p.segStart = t;
          p.paused = p.seg < p.path.length - 1;
          if (p.seg >= p.path.length - 1) p.done = true;
        }
      });
    }

    /* ---- Phase 4b: cursor reactivity --------------------------------
       Three tiers, all cooldown-gated so they stay rare and special:
       - proximity: nodes within REACT_R of the cursor bloom softly
         (continuous but cheap — a decaying per-node boost).
       - dwell: cursor at rest >=450ms near a node fires a short pulse
         walking 2-4 hops away from it (>=5s cooldown per canvas).
       - click: nodes within a wider radius all flare at once and one
         short pulse fires (>=3s cooldown).
       Never wired on the ambient preset or coarse pointers. */
    var REACT_R = 110, DWELL_MS = 450, DWELL_COOLDOWN = 5000, CLICK_COOLDOWN = 3000;
    var mouse = { x: -1e4, y: -1e4, inside: false, movedAt: 0, dwellFiredAt: 0, clickAt: 0 };

    function shortWalk(start, hops) {
      var path = [start], cur = start;
      for (var i = 0; i < hops; i++) {
        var nbs = (adj[cur.id] || []).filter(function (nb) { return path.indexOf(nb) < 0; });
        if (!nbs.length) break;
        cur = nbs[(Math.random() * nbs.length) | 0];
        path.push(cur);
      }
      return path.length > 1 ? path : null;
    }

    function nearestNode(x, y, maxD) {
      var best = null, bestD = maxD * maxD;
      field.nodes.forEach(function (nd) {
        var dx = nd.drawX - x, dy = nd.drawY - y;
        var d = dx * dx + dy * dy;
        if (d < bestD) { bestD = d; best = nd; }
      });
      return best;
    }

    if (preset.reactive && FINE && !COARSE) {
      window.addEventListener("mousemove", function (e) {
        var rect = canvas.getBoundingClientRect();
        mouse.inside = e.clientX >= rect.left && e.clientX <= rect.right &&
                       e.clientY >= rect.top && e.clientY <= rect.bottom;
        if (!mouse.inside) return;
        mouse.x = e.clientX - rect.left;
        mouse.y = e.clientY - rect.top;
        mouse.movedAt = performance.now();
      }, { passive: true });

      window.addEventListener("click", function (e) {
        var rect = canvas.getBoundingClientRect();
        if (e.clientX < rect.left || e.clientX > rect.right ||
            e.clientY < rect.top || e.clientY > rect.bottom) return;
        var t = performance.now();
        if (t - mouse.clickAt < CLICK_COOLDOWN) return;
        mouse.clickAt = t;
        var x = e.clientX - rect.left, y = e.clientY - rect.top;
        field.nodes.forEach(function (nd) {
          var dx = nd.drawX - x, dy = nd.drawY - y;
          var d = Math.sqrt(dx * dx + dy * dy);
          if (d < REACT_R * 1.6) nd.boost = Math.max(nd.boost, 1.6 * (1 - d / (REACT_R * 1.6)));
        });
        var origin = nearestNode(x, y, REACT_R * 1.6);
        if (origin) {
          var burst = shortWalk(origin, 3);
          if (burst) pulses.push({ path: burst, seg: 0, segStart: t, paused: false, color: "cyan" });
        }
      }, { passive: true });
    }

    function reactTick(t) {
      if (!preset.reactive || !FINE || COARSE || !mouse.inside) return;
      /* proximity bloom */
      field.nodes.forEach(function (nd) {
        var dx = nd.drawX - mouse.x, dy = nd.drawY - mouse.y;
        var d = Math.sqrt(dx * dx + dy * dy);
        if (d < REACT_R) nd.boost = Math.max(nd.boost, 0.85 * (1 - d / REACT_R));
      });
      /* dwell: cursor at rest near a node -> one short pulse */
      if (t - mouse.movedAt >= DWELL_MS && t - mouse.dwellFiredAt >= DWELL_COOLDOWN) {
        var origin = nearestNode(mouse.x, mouse.y, REACT_R * 1.2);
        if (origin) {
          mouse.dwellFiredAt = t;
          origin.boost = Math.max(origin.boost, 1.4);
          var walk = shortWalk(origin, 2 + ((Math.random() * 3) | 0));
          if (walk) pulses.push({ path: walk, seg: 0, segStart: t, paused: false, color: "cyan" });
        }
      }
    }

    /* perf: scoped instances (hero/rail/editorial) stop drawing while
       scrolled out of view — the rAF stays scheduled (cheap no-op) but
       the canvas work is skipped. The body-level ambient layer is
       always in view, so it never gets an observer. */
    var inView = true;
    if (canvas.parentElement !== document.body && "IntersectionObserver" in window) {
      new IntersectionObserver(function (entries) {
        inView = entries[0].isIntersecting;
      }, { rootMargin: "12% 0px" }).observe(canvas);
    }

    var raf = null;
    function tick(t) {
      raf = requestAnimationFrame(tick);
      if (document.hidden || !inView) return;
      ctx.clearRect(0, 0, w, h);
      field.nodes.forEach(function (node) { place(node, t); });
      placeOrbitals(t);
      evolve(t);
      reactTick(t);
      drawEdges(t);
      drawNodes(t);
      maybeSpawnPulse(t);
      drawPulses(t);
    }
    raf = requestAnimationFrame(tick);

    canvas.__neuralField = {
      setParallax: function (v) { parallax = Math.max(-1, Math.min(1, v)); },
      destroy: function () { if (raf) cancelAnimationFrame(raf); }
    };
  }

  /* ---- public helper for host pages (home.js) to drive scroll parallax ---- */
  window.mlhNeuralSetParallax = function (canvas, value) {
    if (canvas && canvas.__neuralField) canvas.__neuralField.setParallax(value);
  };

  function init() {
    /* scoped instances declared in markup: <canvas data-neural-field="hero"> */
    document.querySelectorAll("[data-neural-field]").forEach(function (canvas) {
      if (canvas.tagName !== "CANVAS") return;
      var preset = canvas.getAttribute("data-neural-field");
      mount(canvas, preset, {});
    });

    /* the universal ambient layer — every page gets this, unconditionally */
    if (!(COARSE && PRESETS.ambient.coarseScale === 0)) {
      var ambient = document.createElement("canvas");
      ambient.setAttribute("aria-hidden", "true");
      ambient.className = "pf-neural-ambient";
      document.body.appendChild(ambient);
      mount(ambient, "ambient", {});
    }
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();

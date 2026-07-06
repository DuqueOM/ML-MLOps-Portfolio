/* Site-wide UI tweaks — vanilla, no dependencies. Unlike home.js and
   portfolio.js this file runs on EVERY page (loaded via mkdocs.yml
   extra_javascript), so keep it small and unconditional.

   1) Mobile drawer: the "Projects" section behaves as a direct link to
      the overview page instead of unfolding a submenu (user request —
      desktop keeps the full sidebar).
   2) pfMarquee: the generic infinite-drift rail extracted from the home
      case carousel — auto-drift, cursor-edge direction/speed, drag to
      scrub, click/tap to center, edge fade handled by CSS. Auto-mounts
      on About's ".pf-toolbox".
   3) Chat widget: the "neural agent" — a procedurally-drawn wireframe
      figure (canvas, transparent) that opens a chat panel backed by the
      Cloudflare Worker in cloudflare/portfolio-chat-worker.js. Mounted
      on every page since a recruiter can land on any tab. History lives
      in memory only — resets on reload, nothing persisted, nothing sent
      anywhere but the Worker (which only forwards to Workers AI). */
(function () {
  "use strict";

  var reduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  var finePointer = window.matchMedia("(pointer: fine)").matches;
  var CHAT_ENDPOINT = "https://portfolio-chat.duqueortegamutis.workers.dev";

  /* ---- 1) drawer: Projects goes straight to its overview ---- */
  function patchDrawer() {
    if (!window.matchMedia("(max-width: 76.1875em)").matches) return;
    document.querySelectorAll(".md-nav--primary .md-nav__item--nested").forEach(function (item) {
      var links = item.querySelectorAll("a.md-nav__link[href]");
      if (!links.length) return;
      var target = null;
      links.forEach(function (a) {
        if (!target && /\/projects\/(index\.html)?$/.test(a.pathname)) target = a;
      });
      if (!target) target = links[0];
      var label = item.querySelector(":scope > label") || item.querySelector(":scope > .md-nav__link");
      if (!label) return;
      var a = document.createElement("a");
      a.className = "md-nav__link";
      a.href = target.href;
      a.textContent = (label.textContent || "").trim();
      while (item.firstChild) item.removeChild(item.firstChild);
      item.appendChild(a);
    });
  }

  /* ---- 2) generic infinite marquee ---- */
  function pfMarquee(track) {
    if (track.dataset.marquee === "on" || track.children.length < 2) return;
    track.dataset.marquee = "on";

    /* clip viewport around the track */
    var clip = document.createElement("div");
    clip.className = "pf-marquee-clip";
    track.parentNode.insertBefore(clip, track);
    clip.appendChild(track);
    track.classList.add("pf-marquee-track");

    /* clone the set once for a seamless loop */
    track.innerHTML += track.innerHTML;
    track.querySelectorAll(".js-reveal").forEach(function (el) {
      el.classList.add("is-in");
    });

    var offset = 0, half = 0, goal = null;
    var vel = null, visible = true, dragX = null, dragged = 0;
    var MAX = reduced ? 0 : 0.45;

    function measure() { half = track.scrollWidth / 2; }
    window.addEventListener("resize", measure);
    window.addEventListener("load", measure);
    measure();

    if ("IntersectionObserver" in window) {
      new IntersectionObserver(function (entries) {
        visible = entries[0].isIntersecting;
      }, { rootMargin: "10% 0px" }).observe(clip);
    }

    if (finePointer) {
      clip.addEventListener("pointermove", function (e) {
        if (e.pointerType !== "mouse") return;
        var r = clip.getBoundingClientRect();
        var nx = ((e.clientX - r.left) / (r.width || 1)) * 2 - 1;
        var mag = Math.max(0, Math.abs(nx) - 0.16) / 0.84;
        vel = (nx < 0 ? -1 : 1) * mag * mag * MAX;
      });
      clip.addEventListener("mouseleave", function () { vel = null; });
    }

    track.addEventListener("pointerdown", function (e) {
      dragX = e.clientX; dragged = 0; goal = null;
    });
    window.addEventListener("pointermove", function (e) {
      if (dragX === null) return;
      var dx = e.clientX - dragX;
      offset -= dx;
      dragged += Math.abs(dx);
      dragX = e.clientX;
    }, { passive: true });
    window.addEventListener("pointerup", function () { dragX = null; });
    /* touch scrolling fires pointercancel, never pointerup */
    window.addEventListener("pointercancel", function () { dragX = null; });

    /* offset stays unbounded; only the rendered value wraps — wrapping
       the live value while easing toward a goal caused runaway spins */
    function wrapped() { return ((offset % half) + half) % half; }

    track.addEventListener("click", function (e) {
      if (dragged > 8) {
        dragged = 0;
        e.preventDefault();
        e.stopPropagation();
        return;
      }
      if (e.target.closest("a, button")) return;
      var card = e.target.closest(".pf-marquee-track > *");
      if (!card || half <= 0) return;
      var target = card.offsetLeft + card.offsetWidth / 2 - clip.clientWidth / 2;
      var delta = ((target - wrapped()) % half + half) % half;
      if (delta > half / 2) delta -= half;
      goal = offset + delta;
    }, true);

    /* translucent prev/next arrows — one card step per press */
    clip.style.position = "relative";
    [["prev", -1, "M15 18l-6-6 6-6"], ["next", 1, "M9 6l6 6-6 6"]].forEach(function (btn) {
      var b = document.createElement("button");
      b.type = "button";
      b.className = "pf-marquee-nav pf-marquee-nav--" + btn[0];
      b.setAttribute("aria-label", btn[0] === "prev" ? "Previous" : "Next");
      b.innerHTML = '<svg viewBox="0 0 24 24" aria-hidden="true"><path fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" d="' + btn[2] + '"/></svg>';
      b.addEventListener("click", function (e) {
        e.stopPropagation();
        var card = track.children[0];
        if (!card || half <= 0) return;
        var gap = parseFloat(getComputedStyle(track).columnGap) || 0;
        var step = card.offsetWidth + gap;
        var base = card.offsetLeft + card.offsetWidth / 2 - clip.clientWidth / 2;
        var from = goal === null ? offset : goal;
        var n = Math.round((from - base) / step);
        goal = base + (n + btn[1]) * step;
      });
      clip.appendChild(b);
    });

    (function loop() {
      requestAnimationFrame(loop);
      if (document.hidden || !visible || half <= 0) return;
      if (dragX === null) {
        if (goal !== null) {
          var d = goal - offset;
          if (Math.abs(d) < 0.5) { offset = goal; goal = null; }
          else offset += d * 0.09;
        } else {
          offset += (vel === null ? MAX : vel);
        }
      }
      track.style.transform = "translate3d(" + (-wrapped()).toFixed(1) + "px,0,0)";
    })();
  }

  /* ---- 3a) the neural agent figure --------------------------------
     A waist-up bust drawn live on a transparent canvas: a 3D ellipsoid
     head mesh that turns to look around (idle glances + occasional
     cursor tracking), hair strands of linked nodes floating as if
     weightless, and a breathing torso mesh with a pulsing energy core.
     Same visual language as neural-field.js (nodes, thin edges,
     cyan/violet palette) so she reads as made of the site's own
     network — information, energy. Nothing is ever painted behind her
     silhouette: whatever the page shows through IS her backdrop. */
  function mountChatAgent(canvas, launcher) {
    var ctx = canvas.getContext("2d");
    if (!ctx) return;
    var DPR = Math.min(window.devicePixelRatio || 1, 2);
    var TAU = Math.PI * 2;
    var CYAN = "34,211,238", VIOLET = "167,139,250", WHITE = "226,242,255";

    /* draw in fixed design units (150 wide); resizing just rescales.
       The figure sits low in the canvas on purpose: the strip above
       her head is headroom so floating hair never hits the canvas
       edge and gets shaved into a flat horizontal line. */
    var S = 1, DH = 190;
    function resize() {
      var r = canvas.getBoundingClientRect();
      var w = Math.max(1, r.width), h = Math.max(1, r.height);
      S = w / 150;
      DH = h / S;
      canvas.width = w * DPR;
      canvas.height = h * DPR;
      ctx.setTransform(DPR * S, 0, 0, DPR * S, 0, 0);
    }
    resize();
    var rsT = null;
    window.addEventListener("resize", function () {
      clearTimeout(rsT);
      rsT = setTimeout(function () { resize(); step(performance.now()); }, 150);
    });

    function clamp(v, lo, hi) { return v < lo ? lo : v > hi ? hi : v; }

    /* deterministic pseudo-random so she looks the same on every page */
    var seed = 7;
    function rnd() { seed = (seed * 16807) % 2147483647; return seed / 2147483647; }

    /* ---- head: 3D ellipsoid mesh (lat rings x meridians) ---- */
    var HEAD = { x: 75, y: 68, rx: 21.5, ry: 25.5, rz: 18.5 };
    var LATS = [-64, -38, -12, 14, 40, 64];
    var LONS = 12;
    var headNodes = [], headEdges = [];
    LATS.forEach(function (lat) {
      var phi = lat * Math.PI / 180;
      for (var lo = 0; lo < LONS; lo++) {
        var th = lo / LONS * TAU;
        headNodes.push({
          x: HEAD.rx * Math.cos(phi) * Math.sin(th),
          y: -HEAD.ry * Math.sin(phi),
          z: HEAD.rz * Math.cos(phi) * Math.cos(th)
        });
      }
    });
    headNodes.push({ x: 0, y: -HEAD.ry, z: 0 });      /* crown */
    headNodes.push({ x: 0, y: HEAD.ry, z: 2.5 });     /* chin */
    var crownIdx = headNodes.length - 2, chinIdx = headNodes.length - 1;
    headNodes.forEach(function (n, i) { n.c = i % 7 === 0 ? VIOLET : CYAN; });
    (function () {
      for (var li = 0; li < LATS.length; li++) {
        for (var lo = 0; lo < LONS; lo++) {
          var i = li * LONS + lo;
          headEdges.push([i, li * LONS + (lo + 1) % LONS]);
          if (li < LATS.length - 1) headEdges.push([i, (li + 1) * LONS + lo]);
        }
      }
      for (var lo2 = 0; lo2 < LONS; lo2 += 2) {
        headEdges.push([(LATS.length - 1) * LONS + lo2, crownIdx]);
        headEdges.push([lo2, chinIdx]);
      }
    })();

    /* a point on the head surface (lat in deg, lon in rad from front) */
    function surf(latDeg, lonRad, push) {
      var phi = latDeg * Math.PI / 180;
      return {
        x: HEAD.rx * Math.cos(phi) * Math.sin(lonRad) * (push || 1),
        y: -HEAD.ry * Math.sin(phi),
        z: HEAD.rz * Math.cos(phi) * Math.cos(lonRad) * (push || 1)
      };
    }
    /* ---- face: contour + features so she reads as a person, not a
       stick figure. All are surface polylines that rotate with the
       head; alpha is scaled by how front-facing they are. ---- */
    var eyes = [surf(0, -0.36, 1.03), surf(0, 0.36, 1.03)];
    var faceOval = [
      surf(30, -0.20), surf(26, -0.52), surf(6, -0.62), surf(-16, -0.52),
      surf(-38, -0.33), surf(-54, -0.12), surf(-54, 0.12), surf(-38, 0.33),
      surf(-16, 0.52), surf(6, 0.62), surf(26, 0.52), surf(30, 0.20)
    ];
    var browL = [surf(10, -0.50, 1.02), surf(13, -0.30, 1.02), surf(11, -0.15, 1.02)];
    var browR = [surf(11, 0.15, 1.02), surf(13, 0.30, 1.02), surf(10, 0.50, 1.02)];
    var nose = [surf(2, 0, 1.01), surf(-14, 0, 1.03)];
    var noseBase = [surf(-17, -0.08, 1.02), surf(-18, 0, 1.03), surf(-17, 0.08, 1.02)];
    var lipTop = [surf(-27, -0.16, 1.02), surf(-26, 0, 1.02), surf(-27, 0.16, 1.02)];
    var lipLow = [surf(-33, -0.10, 1.02), surf(-34, 0, 1.02), surf(-33, 0.10, 1.02)];

    /* ---- hair: strands anchored to the scalp, floating outward ---- */
    var hairs = [];
    for (var h = 0; h < 26; h++) {
      var side = h % 2 === 0 ? 1 : -1;
      hairs.push({
        a: surf(2 + rnd() * 60, side * Math.PI * (0.30 + rnd() * 0.65), 1.04),
        segs: 6 + (rnd() * 5 | 0),
        len: 5 + rnd() * 3.5,
        phase: rnd() * TAU,
        omega: 0.0007 + rnd() * 0.0007,
        amp: 0.10 + rnd() * 0.07,
        color: rnd() < 0.55 ? CYAN : VIOLET
      });
    }

    /* ---- torso rows (2D mesh; the waist is cut by the canvas edge,
       which is what makes her read as "from the waist up"). The bust
       row uses a negative crown (center dips) to give the chest
       volume instead of a flat drum. ---- */
    var ROWS = [
      { y: 118, hw: 37, yawK: 5, crown: 8 },
      { y: 130, hw: 33, yawK: 3.6, crown: 2.5 },
      { y: 143, hw: 30, yawK: 2.4, crown: -3 },
      { y: 157, hw: 26.5, yawK: 1.4, crown: 1.5 },
      { y: 172, hw: 24, yawK: 0.7, crown: 1 },
      { y: 188, hw: 25.5, yawK: 0.3, crown: 0.8 }
    ];
    var FRACS = [-1, -0.66, -0.33, 0, 0.33, 0.66, 1];

    /* ---- gaze state machine: idle glances / cursor follow / panel ---- */
    var yaw = 0.12, pitch = 0.02, tYaw = 0.12, tPitch = 0.02;
    var mode = "idle";
    var nextGlance = 1400, followUntil = 0, nextFollowOk = 6000;
    var blinkAt = 2400, blink = 0;
    var mouse = { x: 0, y: 0, at: -1e9 };
    if (finePointer && !reduced) {
      window.addEventListener("mousemove", function (e) {
        mouse.x = e.clientX; mouse.y = e.clientY; mouse.at = performance.now();
      }, { passive: true });
    }

    function step(t) {
      var open = launcher.classList.contains("is-open");
      if (open) {
        /* panel sits right above her — she looks up at it */
        mode = "panel"; tYaw = -0.04; tPitch = -0.18;
      } else if (mode === "panel") {
        mode = "idle"; nextGlance = t + 500;
      }
      if (!open && finePointer && !reduced &&
          t >= nextFollowOk && t - mouse.at < 1400) {
        mode = "follow";
        followUntil = t + 2600 + Math.random() * 1800;
        nextFollowOk = followUntil + 7000 + Math.random() * 9000;
      }
      if (mode === "follow") {
        if (t > followUntil) {
          mode = "idle"; nextGlance = t + 400;
        } else {
          var rr = canvas.getBoundingClientRect();
          var hx = rr.left + HEAD.x * S, hy = rr.top + HEAD.y * S;
          tYaw = clamp((mouse.x - hx) / 260, -0.62, 0.62);
          tPitch = clamp((mouse.y - hy) / 420, -0.30, 0.34);
        }
      }
      if (mode === "idle" && t >= nextGlance) {
        nextGlance = t + 2600 + Math.random() * 3800;
        tYaw = (Math.random() * 1.1 - 0.55) * (Math.random() < 0.75 ? 1 : 0.3);
        tPitch = Math.random() * 0.26 - 0.10;
      }
      yaw += (tYaw - yaw) * 0.055;
      pitch += (tPitch - pitch) * 0.055;
      if (t >= blinkAt) { blinkAt = t + 2400 + Math.random() * 3600; blink = 1; }
      if (blink > 0) blink = Math.max(0, blink - 0.09);

      var cy = Math.cos(yaw), sy = Math.sin(yaw);
      var cp = Math.cos(pitch), sp = Math.sin(pitch);
      var bob = Math.sin(t / 3400 * TAU) * 1.1;
      var breathe = 1 + Math.sin(t / 3400 * TAU) * 0.012;

      function proj(p) {
        var x = p.x * cy + p.z * sy;
        var z = -p.x * sy + p.z * cy;
        var y = p.y * cp - z * sp;
        z = p.y * sp + z * cp;
        return { x: HEAD.x + x, y: HEAD.y + y + bob * 0.5, z: z };
      }

      ctx.clearRect(-2, -2, 154, DH + 4);

      /* front-gated surface polyline: rotates with the head, fades
         out as it turns away from the viewer */
      function facePath(pts, alpha, close) {
        var zsum = 0;
        ctx.beginPath();
        for (var i3 = 0; i3 < pts.length; i3++) {
          var q = proj(pts[i3]);
          zsum += q.z;
          if (i3 === 0) ctx.moveTo(q.x, q.y); else ctx.lineTo(q.x, q.y);
        }
        if (close) ctx.closePath();
        var frontK = clamp(zsum / pts.length / HEAD.rz, 0, 1);
        if (frontK <= 0.05) return;
        ctx.strokeStyle = "rgba(" + WHITE + "," + (alpha * frontK).toFixed(3) + ")";
        ctx.stroke();
      }

      /* hair first, so the head mesh overlays it (reads as behind) */
      ctx.lineWidth = 1;
      hairs.forEach(function (hs) {
        var a = proj(hs.a);
        var depth = (a.z / HEAD.rz + 1) / 2;
        var alpha0 = 0.22 + depth * 0.42;
        var ang = Math.atan2(a.y - HEAD.y, a.x - HEAD.x);
        var drift = Math.sin(t / 5200 * TAU + hs.phase) * 0.15;
        var px = a.x, py = a.y;
        for (var i = 0; i < hs.segs; i++) {
          ang += Math.sin(t * hs.omega + hs.phase + i * 0.62) *
                 hs.amp * (1 + i * 0.30) + drift * 0.12;
          var nx = px + Math.cos(ang) * hs.len;
          var ny = py + Math.sin(ang) * hs.len;
          /* soft walls: steer strands back before they reach a canvas
             edge, so hair never gets shaved into a flat clipped line */
          if (ny < 12) { ang = -ang * 0.5; ny = py + Math.sin(ang) * hs.len; }
          if (nx < 6) { ang = Math.PI - ang; nx = px + Math.cos(ang) * hs.len; }
          else if (nx > 144) { ang = Math.PI - ang; nx = px + Math.cos(ang) * hs.len; }
          var fal = alpha0 * (1 - i / hs.segs);
          ctx.strokeStyle = "rgba(" + hs.color + "," + fal.toFixed(3) + ")";
          ctx.beginPath(); ctx.moveTo(px, py); ctx.lineTo(nx, ny); ctx.stroke();
          ctx.fillStyle = "rgba(" + hs.color + "," + (fal * 0.9).toFixed(3) + ")";
          ctx.beginPath(); ctx.arc(nx, ny, 1.05, 0, TAU); ctx.fill();
          px = nx; py = ny;
        }
      });

      /* head wireframe — back edges dim, front bright (real depth) */
      var P = headNodes.map(proj);
      headEdges.forEach(function (e) {
        var a = P[e[0]], b = P[e[1]];
        var d = ((a.z + b.z) / 2 / HEAD.rz + 1) / 2;
        ctx.strokeStyle = "rgba(" + CYAN + "," + (0.05 + d * 0.30).toFixed(3) + ")";
        ctx.beginPath(); ctx.moveTo(a.x, a.y); ctx.lineTo(b.x, b.y); ctx.stroke();
      });
      P.forEach(function (p, i) {
        var d = (p.z / HEAD.rz + 1) / 2;
        ctx.fillStyle = "rgba(" + headNodes[i].c + "," + (0.15 + d * 0.55).toFixed(3) + ")";
        ctx.beginPath(); ctx.arc(p.x, p.y, 0.7 + d * 0.9, 0, TAU); ctx.fill();
      });

      /* face — contour plane, brows, nose, lips: what turns the mesh
         sphere into a person. Drawn over the mesh, under the eyes. */
      ctx.lineWidth = 1;
      facePath(faceOval, 0.30, true);
      facePath(browL, 0.55);
      facePath(browR, 0.55);
      facePath(nose, 0.40);
      facePath(noseBase, 0.35);
      facePath(lipTop, 0.50);
      facePath(lipLow, 0.38);

      /* eyes — bright, blinking, only while facing forward enough */
      eyes.forEach(function (ep) {
        var e2 = proj(ep);
        if (e2.z < 3) return;
        var al = 0.9 * (1 - Math.min(1, blink * 1.5));
        ctx.fillStyle = "rgba(" + WHITE + "," + (al * 0.22).toFixed(3) + ")";
        ctx.beginPath(); ctx.arc(e2.x, e2.y, 3.4, 0, TAU); ctx.fill();
        ctx.fillStyle = "rgba(" + WHITE + "," + al.toFixed(3) + ")";
        ctx.beginPath(); ctx.arc(e2.x, e2.y, 1.6, 0, TAU); ctx.fill();
      });

      /* neck: chin down to the shoulder line, turning with the head */
      var chin = P[chinIdx];
      ctx.strokeStyle = "rgba(" + CYAN + ",0.30)";
      [-1, 1].forEach(function (s2) {
        ctx.beginPath();
        ctx.moveTo(chin.x + s2 * 5, chin.y + 1);
        ctx.lineTo(75 + yaw * 6 + s2 * 7, 113 + bob * 0.4);
        ctx.stroke();
      });

      /* torso mesh: shoulders down to the waist */
      var rowPts = ROWS.map(function (rw) {
        var cx2 = 75 + yaw * rw.yawK;
        var hw = rw.hw * breathe;
        return FRACS.map(function (f) {
          return {
            x: cx2 + f * hw,
            y: rw.y - (1 - Math.abs(f)) * rw.crown + bob * 0.35
          };
        });
      });
      ctx.strokeStyle = "rgba(" + CYAN + ",0.22)";
      rowPts.forEach(function (row) {
        for (var i2 = 0; i2 < row.length - 1; i2++) {
          ctx.beginPath();
          ctx.moveTo(row[i2].x, row[i2].y);
          ctx.lineTo(row[i2 + 1].x, row[i2 + 1].y);
          ctx.stroke();
        }
      });
      for (var ri = 0; ri < rowPts.length - 1; ri++) {
        for (var fi = 0; fi < FRACS.length; fi++) {
          ctx.beginPath();
          ctx.moveTo(rowPts[ri][fi].x, rowPts[ri][fi].y);
          ctx.lineTo(rowPts[ri + 1][fi].x, rowPts[ri + 1][fi].y);
          ctx.stroke();
        }
      }
      rowPts.forEach(function (row, ri2) {
        row.forEach(function (p, fi2) {
          var g = 0.5 + 0.5 * Math.sin(t / 2800 + ri2 * 1.7 + fi2 * 2.3);
          ctx.fillStyle = "rgba(" + (((ri2 + fi2) % 5 === 0) ? VIOLET : CYAN) + "," +
            (0.25 + g * 0.35).toFixed(3) + ")";
          ctx.beginPath(); ctx.arc(p.x, p.y, 1 + g * 0.5, 0, TAU); ctx.fill();
        });
      });

      /* collarbones: neck base out to the shoulder tips */
      ctx.strokeStyle = "rgba(" + CYAN + ",0.28)";
      [rowPts[0][0], rowPts[0][FRACS.length - 1]].forEach(function (tip, ti) {
        var s3 = ti === 0 ? -1 : 1;
        ctx.beginPath();
        ctx.moveTo(75 + yaw * 6 + s3 * 7, 113 + bob * 0.4);
        ctx.lineTo(tip.x, tip.y + 1.5);
        ctx.stroke();
      });

      /* arms: two-contour wireframe from each shoulder, swaying gently,
         cut by the canvas edge like the waist */
      [-1, 1].forEach(function (s4) {
        var tip = rowPts[0][s4 < 0 ? 0 : FRACS.length - 1];
        var inn = rowPts[1][s4 < 0 ? 0 : FRACS.length - 1];
        var sway = Math.sin(t / 2900 * TAU + (s4 < 0 ? 0 : 1.6)) * 1.0;
        var elbOut = { x: tip.x + s4 * 7 + sway, y: 154 + bob * 0.3 };
        var wriOut = { x: tip.x + s4 * 2 + sway * 1.4, y: 189 };
        var elbIn = { x: tip.x - s4 * 1 + sway, y: 155 + bob * 0.3 };
        var wriIn = { x: tip.x - s4 * 5 + sway * 1.4, y: 189 };
        ctx.strokeStyle = "rgba(" + CYAN + ",0.22)";
        ctx.beginPath();
        ctx.moveTo(tip.x, tip.y); ctx.lineTo(elbOut.x, elbOut.y); ctx.lineTo(wriOut.x, wriOut.y);
        ctx.stroke();
        ctx.beginPath();
        ctx.moveTo(inn.x, inn.y); ctx.lineTo(elbIn.x, elbIn.y); ctx.lineTo(wriIn.x, wriIn.y);
        ctx.stroke();
        /* rungs tie the two contours into a mesh */
        [[0.45, 0.45], [1, 1], [0.5, 0.5]].forEach(function (fr, k) {
          var ax, ay, bx, by;
          if (k < 2) { /* shoulder->elbow span */
            ax = tip.x + (elbOut.x - tip.x) * fr[0]; ay = tip.y + (elbOut.y - tip.y) * fr[0];
            bx = inn.x + (elbIn.x - inn.x) * fr[1]; by = inn.y + (elbIn.y - inn.y) * fr[1];
          } else { /* elbow->wrist span */
            ax = elbOut.x + (wriOut.x - elbOut.x) * fr[0]; ay = elbOut.y + (wriOut.y - elbOut.y) * fr[0];
            bx = elbIn.x + (wriIn.x - elbIn.x) * fr[1]; by = elbIn.y + (wriIn.y - elbIn.y) * fr[1];
          }
          ctx.beginPath(); ctx.moveTo(ax, ay); ctx.lineTo(bx, by); ctx.stroke();
        });
        /* joint nodes */
        [elbOut, elbIn].forEach(function (jp, ji) {
          var g2 = 0.5 + 0.5 * Math.sin(t / 2600 + s4 * 2 + ji);
          ctx.fillStyle = "rgba(" + CYAN + "," + (0.3 + g2 * 0.3).toFixed(3) + ")";
          ctx.beginPath(); ctx.arc(jp.x, jp.y, 1.1 + g2 * 0.4, 0, TAU); ctx.fill();
        });
      });

      /* energy core at the sternum — her "heartbeat" */
      var coreG = 0.5 + 0.5 * Math.sin(t / 1600 * TAU);
      var coreX = 75 + yaw * 4, coreY = 128 + bob * 0.35;
      ctx.fillStyle = "rgba(" + CYAN + "," + (0.10 + coreG * 0.18).toFixed(3) + ")";
      ctx.beginPath(); ctx.arc(coreX, coreY, 5.5, 0, TAU); ctx.fill();
      ctx.fillStyle = "rgba(" + WHITE + "," + (0.5 + coreG * 0.45).toFixed(3) + ")";
      ctx.beginPath(); ctx.arc(coreX, coreY, 1.9, 0, TAU); ctx.fill();
    }

    /* draw one frame immediately (visible even in background tabs /
       before the loop's first tick), then animate */
    step(performance.now());
    if (!reduced) {
      (function loop(t) {
        requestAnimationFrame(loop);
        if (document.hidden) return;
        step(t || performance.now());
      })(performance.now());
    }
  }

  /* ---- 3) chat widget: neural-agent assistant + panel ----
     The launcher IS the agent figure above — no bubble, no circle.
     A speech-bubble hint with three dots pulses in every so often
     before the visitor has opened it once — a quiet nudge, not a
     badge/counter. While open, a small ✕ chip appears by her shoulder
     and she looks up toward the panel. */
  function initChatWidget() {
    if (document.querySelector(".pf-chat-launcher")) return;

    var history = [];
    var pending = false;
    var greeted = false;
    var hasOpened = false;
    var hintTimer = null;

    var launcher = document.createElement("button");
    launcher.type = "button";
    launcher.className = "pf-chat-launcher";
    launcher.setAttribute("aria-label", "Open portfolio assistant");
    launcher.setAttribute("aria-expanded", "false");
    launcher.innerHTML =
      '<canvas class="pf-chat-agent" aria-hidden="true"></canvas>' +
      '<span class="pf-chat-x" aria-hidden="true">' +
        '<svg viewBox="0 0 24 24"><path fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" d="M6 6l12 12M18 6L6 18"/></svg>' +
      "</span>" +
      '<span class="pf-chat-hint" aria-hidden="true"><span></span><span></span><span></span></span>';

    var panel = document.createElement("div");
    panel.className = "pf-chat-panel";
    panel.setAttribute("role", "dialog");
    panel.setAttribute("aria-label", "Portfolio assistant chat");
    panel.hidden = true;
    panel.innerHTML =
      '<div class="pf-chat-head">' +
        "<div>" +
          "<strong>Portfolio Assistant</strong>" +
          "<span>Answers grounded in this portfolio's facts</span>" +
        "</div>" +
        '<button type="button" class="pf-chat-close" aria-label="Close">' +
          '<svg viewBox="0 0 24 24" aria-hidden="true"><path fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" d="M6 6l12 12M18 6L6 18"/></svg>' +
        "</button>" +
      "</div>" +
      '<div class="pf-chat-log" role="log" aria-live="polite"></div>' +
      '<form class="pf-chat-form">' +
        '<input type="text" name="q" placeholder="Ask about the projects, stack or availability…" autocomplete="off" maxlength="500">' +
        '<button type="submit" aria-label="Send">' +
          '<svg viewBox="0 0 24 24" aria-hidden="true"><path fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" d="M4 12h16M13 5l7 7-7 7"/></svg>' +
        "</button>" +
      "</form>";

    document.body.appendChild(launcher);
    document.body.appendChild(panel);
    /* mount after append — the figure needs real layout dimensions */
    mountChatAgent(launcher.querySelector(".pf-chat-agent"), launcher);

    var log = panel.querySelector(".pf-chat-log");
    var form = panel.querySelector(".pf-chat-form");
    var input = panel.querySelector('input[name="q"]');
    var closeBtn = panel.querySelector(".pf-chat-close");
    var hint = launcher.querySelector(".pf-chat-hint");

    function addBubble(role, text) {
      var bubble = document.createElement("div");
      bubble.className = "pf-chat-bubble pf-chat-bubble--" + role;
      bubble.textContent = text;
      log.appendChild(bubble);
      log.scrollTop = log.scrollHeight;
      return bubble;
    }

    function addTyping() {
      var t = document.createElement("div");
      t.className = "pf-chat-bubble pf-chat-bubble--assistant pf-chat-typing";
      t.innerHTML = "<span></span><span></span><span></span>";
      log.appendChild(t);
      log.scrollTop = log.scrollHeight;
      return t;
    }

    /* quiet periodic nudge: only before the first open, only with motion
       allowed, stops for good the moment the visitor engages once */
    function scheduleHint() {
      if (reduced || hasOpened) return;
      hintTimer = setTimeout(function () {
        if (hasOpened) return;
        hint.classList.add("is-on");
        setTimeout(function () { hint.classList.remove("is-on"); }, 3600);
        scheduleHint();
      }, hintTimer === null ? 6000 : 26000);
    }
    scheduleHint();

    function open() {
      panel.hidden = false;
      launcher.setAttribute("aria-expanded", "true");
      launcher.setAttribute("aria-label", "Close portfolio assistant");
      launcher.classList.add("is-open");
      if (!hasOpened) {
        hasOpened = true;
        clearTimeout(hintTimer);
        hint.classList.remove("is-on");
      }
      if (!greeted) {
        greeted = true;
        addBubble("assistant",
          "Hi — ask me anything about this portfolio: the projects, the stack, incidents, or availability.");
      }
      input.focus();
    }
    function close() {
      panel.hidden = true;
      launcher.setAttribute("aria-expanded", "false");
      launcher.setAttribute("aria-label", "Open portfolio assistant");
      launcher.classList.remove("is-open");
    }

    launcher.addEventListener("click", function () {
      if (panel.hidden) open(); else close();
    });
    closeBtn.addEventListener("click", close);
    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape" && !panel.hidden) { close(); launcher.focus(); }
    });
    /* click anywhere outside the panel (and outside the agent, which
       already toggles itself) minimizes the chat */
    document.addEventListener("click", function (e) {
      if (panel.hidden) return;
      if (panel.contains(e.target) || launcher.contains(e.target)) return;
      close();
    });

    form.addEventListener("submit", function (e) {
      e.preventDefault();
      var text = input.value.trim();
      if (!text || pending) return;
      input.value = "";
      addBubble("user", text);
      var typing = addTyping();
      pending = true;
      fetch(CHAT_ENDPOINT, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: text, history: history }),
      })
        .then(function (r) {
          if (!r.ok) throw new Error("bad status");
          return r.json();
        })
        .then(function (data) {
          typing.remove();
          var reply = data && data.reply
            ? data.reply
            : "Sorry, I couldn't get a response — try the Contact page.";
          addBubble("assistant", reply);
          history.push({ role: "user", content: text });
          history.push({ role: "assistant", content: reply });
          if (history.length > 12) history = history.slice(-12);
        })
        .catch(function () {
          typing.remove();
          addBubble("assistant",
            "Something went wrong reaching the assistant — try again in a moment, or use the Contact page.");
        })
        .finally(function () { pending = false; });
    });
  }

  function init() {
    patchDrawer();
    document.querySelectorAll(".pf-toolbox, [data-pf-marquee]").forEach(pfMarquee);
    initChatWidget();
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();

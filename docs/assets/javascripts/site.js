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
     The agent is the real reference artwork (docs/media/profile/
     agent-figure.png — a woman rendered as a glowing neural network),
     processed offline so her black background is fully transparent:
     whatever the page shows behind her silhouette IS her backdrop.
     The canvas brings her to life on top of that:
     - gentle breathing + lean, idle glances to the sides, occasional
       cursor tracking, and a look up toward the panel while it's open
       (a flat artwork can't move its eyes, so the whole figure turns —
       reads as attention, not as a static sticker)
     - procedural hair strands floating behind her mane
     - twinkling particles sampled from her own brightest pixels, so
       the sparkle always sits ON her lines */
  function mountChatAgent(canvas, launcher) {
    var ctx = canvas.getContext("2d");
    if (!ctx) return;
    var DPR = Math.min(window.devicePixelRatio || 1, 2);
    var TAU = Math.PI * 2;
    var CYAN = "34,211,238", VIOLET = "167,139,250", WHITE = "226,242,255";

    /* draw in fixed design units (150x190); resizing just rescales */
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

    /* the artwork: 370x420 source drawn at 148x168 design units,
       bottom-anchored and centered (full shoulder span, so it fits by
       width and leaves hair headroom above) */
    var IMG = { x: 1, y: 22, w: 148, h: 168 };
    var HEADC = { x: 73, y: 76 };  /* her head center, for hair anchors */
    var img = new Image();
    var imgReady = false;
    var particles = [];
    var sj = document.querySelector('script[src*="site.js"]');
    img.src = sj
      ? sj.src.replace(/assets\/javascripts\/site\.js.*$/, "media/profile/agent-figure.png")
      : "media/profile/agent-figure.png";
    img.onload = function () {
      imgReady = true;
      sampleParticles();
      step(performance.now());
    };

    /* twinkle points sampled from her own brightest pixels, so the
       sparkle always lands on her lines instead of floating in space */
    function sampleParticles() {
      try {
        var oc = document.createElement("canvas");
        oc.width = 150; oc.height = 190;
        var octx = oc.getContext("2d");
        octx.drawImage(img, IMG.x, IMG.y, IMG.w, IMG.h);
        var data = octx.getImageData(0, 0, 150, 190).data;
        var tries = 0;
        while (particles.length < 64 && tries < 4000) {
          tries++;
          var x = 4 + (rnd() * 142) | 0, y = 4 + (rnd() * 182) | 0;
          var i = (y * 150 + x) * 4;
          if (data[i + 3] < 150 || data[i] + data[i + 1] + data[i + 2] < 330) continue;
          var ok = true;
          for (var k = 0; k < particles.length; k++) {
            var dx = particles[k].x - x, dy = particles[k].y - y;
            if (dx * dx + dy * dy < 49) { ok = false; break; }
          }
          if (!ok) continue;
          particles.push({
            x: x, y: y,
            phase: rnd() * TAU,
            period: 1800 + rnd() * 2600,
            r: 0.7 + rnd() * 0.9,
            c: rnd() < 0.25 ? WHITE : (rnd() < 0.7 ? CYAN : VIOLET)
          });
        }
      } catch (e) { /* tainted canvas etc. — she still renders fine */ }
    }

    /* ---- hair: strands floating from behind her mane ---- */
    var hairs = [];
    for (var h = 0; h < 18; h++) {
      var a0 = -Math.PI * (0.08 + rnd() * 0.84); /* upper arc angles */
      hairs.push({
        ax: HEADC.x + Math.cos(a0) * (26 + rnd() * 8),
        ay: HEADC.y + Math.sin(a0) * (24 + rnd() * 7),
        dir: a0,
        segs: 5 + (rnd() * 4 | 0),
        len: 5 + rnd() * 3,
        phase: rnd() * TAU,
        omega: 0.0007 + rnd() * 0.0007,
        amp: 0.11 + rnd() * 0.07,
        color: rnd() < 0.6 ? CYAN : VIOLET
      });
    }

    /* ---- gaze state machine: idle glances / cursor follow / panel ---- */
    var yaw = 0.10, pitch = 0, tYaw = 0.10, tPitch = 0;
    var mode = "idle";
    var nextGlance = 1400, followUntil = 0, nextFollowOk = 6000;
    var mouse = { x: 0, y: 0, at: -1e9 };
    if (finePointer && !reduced) {
      window.addEventListener("mousemove", function (e) {
        mouse.x = e.clientX; mouse.y = e.clientY; mouse.at = performance.now();
      }, { passive: true });
    }

    function step(t) {
      var open = launcher.classList.contains("is-open");
      if (open) {
        mode = "panel"; tYaw = -0.05; tPitch = -0.5;
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
          var hx = rr.left + HEADC.x * S, hy = rr.top + HEADC.y * S;
          tYaw = clamp((mouse.x - hx) / 420, -0.5, 0.5);
          tPitch = clamp((mouse.y - hy) / 600, -0.5, 0.5);
        }
      }
      if (mode === "idle" && t >= nextGlance) {
        nextGlance = t + 2800 + Math.random() * 4200;
        tYaw = (Math.random() * 0.9 - 0.45) * (Math.random() < 0.75 ? 1 : 0.35);
        tPitch = Math.random() * 0.5 - 0.2;
      }
      yaw += (tYaw - yaw) * 0.05;
      pitch += (tPitch - pitch) * 0.05;

      var sway = reduced ? 0 : Math.sin(t / 4600 * TAU) * 0.011;
      var breathe = reduced ? 1 : 1 + Math.sin(t / 3400 * TAU) * 0.006;

      ctx.clearRect(-2, -2, 154, DH + 4);

      /* whole-figure attitude: lean + tiny lift toward the gaze target.
         Rotation pivots at her waist (bottom center). */
      ctx.save();
      ctx.translate(75 + yaw * 5, 190);
      ctx.rotate(yaw * 0.05 + sway);
      ctx.scale(breathe, breathe);
      ctx.translate(-75, -190 + pitch * 3);

      /* hair strands behind her, drifting like they are weightless */
      ctx.lineWidth = 1;
      hairs.forEach(function (hs) {
        var ang = hs.dir + yaw * 0.35;
        var drift = Math.sin(t / 5200 * TAU + hs.phase) * 0.15;
        var px = hs.ax + yaw * 6, py = hs.ay;
        for (var i = 0; i < hs.segs; i++) {
          ang += Math.sin(t * hs.omega + hs.phase + i * 0.62) *
                 hs.amp * (1 + i * 0.30) + drift * 0.12;
          var nx = px + Math.cos(ang) * hs.len;
          var ny = py + Math.sin(ang) * hs.len;
          /* soft walls: steer back before any canvas edge, so hair
             never gets shaved into a flat clipped line */
          if (ny < 8) { ang = -ang * 0.5; ny = py + Math.sin(ang) * hs.len; }
          if (nx < 6) { ang = Math.PI - ang; nx = px + Math.cos(ang) * hs.len; }
          else if (nx > 144) { ang = Math.PI - ang; nx = px + Math.cos(ang) * hs.len; }
          var fal = 0.42 * (1 - i / hs.segs);
          ctx.strokeStyle = "rgba(" + hs.color + "," + fal.toFixed(3) + ")";
          ctx.beginPath(); ctx.moveTo(px, py); ctx.lineTo(nx, ny); ctx.stroke();
          ctx.fillStyle = "rgba(" + hs.color + "," + (fal * 0.9).toFixed(3) + ")";
          ctx.beginPath(); ctx.arc(nx, ny, 1, 0, TAU); ctx.fill();
          px = nx; py = ny;
        }
      });

      /* the reference artwork itself */
      if (imgReady) {
        ctx.drawImage(img, IMG.x, IMG.y, IMG.w, IMG.h);
      } else {
        /* pre-load (or load failure) fallback: a quiet pulsing dot trio
           so the button is never invisible */
        var g0 = 0.5 + 0.5 * Math.sin(t / 900);
        for (var d3 = -1; d3 <= 1; d3++) {
          ctx.fillStyle = "rgba(" + CYAN + "," + (0.35 + g0 * 0.4).toFixed(3) + ")";
          ctx.beginPath(); ctx.arc(75 + d3 * 10, 170, 3, 0, TAU); ctx.fill();
        }
      }

      /* twinkle: her own bright nodes breathing, a few white flares */
      particles.forEach(function (p) {
        var g = 0.5 + 0.5 * Math.sin(t / p.period * TAU + p.phase);
        ctx.fillStyle = "rgba(" + p.c + "," + (0.10 + g * 0.5).toFixed(3) + ")";
        ctx.beginPath(); ctx.arc(p.x, p.y, p.r * (0.7 + g * 0.6), 0, TAU); ctx.fill();
      });

      ctx.restore();
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

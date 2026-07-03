/* Home microinteractions — vanilla, no dependencies.
   Everything motion-related is gated on prefers-reduced-motion. */
(function () {
  "use strict";

  var root = document.querySelector(".ml-home");
  if (!root) return;

  var reduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  var finePointer = window.matchMedia("(pointer: fine)").matches;

  /* ---- pause SVG SMIL animations when motion is reduced ---- */
  if (reduced) {
    root.querySelectorAll("svg").forEach(function (svg) {
      if (typeof svg.pauseAnimations === "function") svg.pauseAnimations();
    });
  }

  /* ---- hero load sequence: staggered entrance ---- */
  var staggered = root.querySelectorAll(".mlh-stagger");
  if (reduced) {
    staggered.forEach(function (el) { el.classList.add("is-in"); });
  } else {
    staggered.forEach(function (el, i) {
      setTimeout(function () { el.classList.add("is-in"); }, 120 + i * 110);
    });
  }

  /* ---- scroll reveals ---- */
  var revealables = root.querySelectorAll("[data-reveal]");
  if (reduced || !("IntersectionObserver" in window)) {
    revealables.forEach(function (el) { el.classList.add("is-in"); });
  } else {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          entry.target.classList.add("is-in");
          io.unobserve(entry.target);
        }
      });
    }, { threshold: 0.15, rootMargin: "0px 0px -8% 0px" });
    revealables.forEach(function (el) { io.observe(el); });
  }

  /* ---- counters (up, and the 81 -> 0 countdown) ---- */
  function animateValue(el, from, to, duration, done) {
    if (reduced) { el.textContent = String(to); if (done) done(); return; }
    var start = null;
    function step(ts) {
      if (start === null) start = ts;
      var p = Math.min((ts - start) / duration, 1);
      var eased = 1 - Math.pow(1 - p, 3); /* ease-out cubic */
      el.textContent = String(Math.round(from + (to - from) * eased));
      if (p < 1) { requestAnimationFrame(step); }
      else if (done) { done(); }
    }
    requestAnimationFrame(step);
  }

  var counterIO = ("IntersectionObserver" in window) && !reduced
    ? new IntersectionObserver(function (entries) {
        entries.forEach(function (entry) {
          if (!entry.isIntersecting) return;
          counterIO.unobserve(entry.target);
          var el = entry.target;
          if (el.hasAttribute("data-count")) {
            animateValue(el, 0, parseInt(el.getAttribute("data-count"), 10), 1400);
          } else {
            animateValue(el, parseInt(el.getAttribute("data-countdown"), 10), 0, 1800, function () {
              el.classList.add("mlh-done");
            });
          }
        });
      }, { threshold: 0.6 })
    : null;

  root.querySelectorAll("[data-count], [data-countdown]").forEach(function (el) {
    if (counterIO) { counterIO.observe(el); }
    else {
      var v = el.hasAttribute("data-count") ? el.getAttribute("data-count") : "0";
      el.textContent = v;
      if (el.hasAttribute("data-countdown")) el.classList.add("mlh-done");
    }
  });

  /* ---- pinned horizontal case rail (GSAP ScrollTrigger; static fallback) ---- */
  var projectCases = [
    {
      tag: "incident // serving",
      project: "BankChurn Predictor",
      href: "projects/bankchurn-debugging/",
      title: "81% of requests failing. The model was fine.",
      description: "A load test exposed an 81% error rate on the BankChurn API. Root cause: uvicorn --workers inside Kubernetes — multiple workers competing for one shared CPU budget produce thrashing, not parallelism. Redesigned the inference path with asyncio plus a ThreadPoolExecutor (GIL analysis documented), errors dropped to zero and the CPU request was halved.",
      metrics: [
        ["errors under load", "81% → 0%"],
        ["cpu request", "2000m → 1000m"],
        ["model", "AUC 0.87 · 90% cov"]
      ],
      diagram: '<svg viewBox="0 0 560 96" class="mlh-diagram" role="img" aria-label="Serving architecture: client to FastAPI single worker, inference offloaded to thread pool, model and SHAP"><g class="mlh-d-node"><rect x="2" y="32" width="86" height="32" rx="3"/><text x="45" y="52">client</text></g><path d="M88 48 H128" class="mlh-d-edge"/><g class="mlh-d-node mlh-d-accent"><rect x="128" y="32" width="150" height="32" rx="3"/><text x="203" y="52">fastapi · 1 worker</text></g><path d="M278 48 H318" class="mlh-d-edge"/><g class="mlh-d-node"><rect x="318" y="32" width="120" height="32" rx="3"/><text x="378" y="52">threadpool</text></g><path d="M438 48 H478" class="mlh-d-edge"/><g class="mlh-d-node"><rect x="478" y="32" width="80" height="32" rx="3"/><text x="518" y="52">model</text></g><text x="203" y="86" class="mlh-d-note">event loop stays free — probes alive under load</text></svg>',
      links: [
        ["See the BankChurn Predictor service", "projects/bankchurn/"],
        ["Read the debugging deep dive", "projects/bankchurn-debugging/"]
      ]
    },
    {
      tag: "trade-off // nlp serving",
      project: "NLPInsight Analyzer",
      href: "projects/nlpinsight/",
      title: "The heavier model we chose not to ship",
      description: "Financial sentiment classification where the production question mattered more than the leaderboard: a transformer would score higher and cost more to operate, explain and debug. NLPInsight ships a lightweight, explainable path — and documents the rejected alternative as an engineering decision, not an omission.",
      metrics: [
        ["accuracy", "80.6%"],
        ["coverage", "98%"],
        ["inference", "CPU-only · low cost"]
      ],
      diagram: '<svg viewBox="0 0 560 96" class="mlh-diagram" role="img" aria-label="NLP architecture: text to TF-IDF linear model to API; transformer path documented but not shipped"><g class="mlh-d-node"><rect x="2" y="14" width="86" height="32" rx="3"/><text x="45" y="34">text</text></g><path d="M88 30 H128" class="mlh-d-edge"/><g class="mlh-d-node mlh-d-accent"><rect x="128" y="14" width="160" height="32" rx="3"/><text x="208" y="34">tf-idf + linear</text></g><path d="M288 30 H328" class="mlh-d-edge"/><g class="mlh-d-node"><rect x="328" y="14" width="80" height="32" rx="3"/><text x="368" y="34">api</text></g><g class="mlh-d-node mlh-d-ghost"><rect x="128" y="58" width="160" height="30" rx="3"/><text x="208" y="77">transformer</text></g><text x="438" y="77" class="mlh-d-note">documented, not shipped — operability won</text></svg>',
      links: [
        ["See the NLPInsight Analyzer service", "projects/nlpinsight/"]
      ]
    },
    {
      tag: "leakage // forecasting",
      project: "ChicagoTaxi Pipeline",
      href: "projects/chicagotaxi/",
      title: "A score too good to be true — until it was",
      description: "Demand forecasting over 6.3M Chicago taxi trips. The first model looked perfect because a feature was leaking the future into training. Removed the leak, rebuilt validation as strictly temporal, and the R² of 0.96 that survived honest re-evaluation is the one published.",
      metrics: [
        ["r²", "0.96 — honest"],
        ["volume", "6.3M trips"],
        ["etl", "PySpark · temporal CV"]
      ],
      diagram: '<svg viewBox="0 0 560 96" class="mlh-diagram" role="img" aria-label="Forecasting pipeline: 6.3M trips through PySpark ETL and temporal cross-validation to forecast; leaky feature removed"><g class="mlh-d-node"><rect x="2" y="32" width="100" height="32" rx="3"/><text x="52" y="52">6.3M trips</text></g><path d="M102 48 H142" class="mlh-d-edge"/><g class="mlh-d-node mlh-d-accent"><rect x="142" y="32" width="120" height="32" rx="3"/><text x="202" y="52">pyspark etl</text></g><path d="M262 48 H302" class="mlh-d-edge"/><g class="mlh-d-node"><rect x="302" y="32" width="130" height="32" rx="3"/><text x="367" y="52">temporal cv</text></g><path d="M432 48 H472" class="mlh-d-edge"/><g class="mlh-d-node"><rect x="472" y="32" width="86" height="32" rx="3"/><text x="515" y="52">forecast</text></g><text x="202" y="86" class="mlh-d-note mlh-d-warn">leaky feature → removed before metrics</text></svg>',
      links: [
        ["See the ChicagoTaxi Pipeline service", "projects/chicagotaxi/"]
      ]
    }
  ];

  function renderProjectRail() {
    var rail = root.querySelector("[data-project-rail]");
    if (!rail || rail.dataset.rendered === "true") return;
    if (rail.children.length > 0) {
      rail.dataset.rendered = "true";
      return;
    }
    rail.innerHTML = projectCases.map(function (item) {
      var metrics = item.metrics.map(function (metric) {
        return "<div><dt>" + metric[0] + "</dt><dd>" + metric[1] + "</dd></div>";
      }).join("");
      var links = item.links.map(function (link) {
        return '<a class="mlh-case-link" data-magnetic href="' + link[1] + '">' + link[0] + "</a>";
      }).join("");
      return '<article class="mlh-case" tabindex="-1">' +
        '<div class="mlh-case-meta"><p class="mlh-case-tag mlh-tag-cyan">' + item.tag + '</p><dl class="mlh-case-metrics">' + metrics + '</dl></div>' +
        '<div class="mlh-case-body"><p class="mlh-case-project">' + item.project + '</p><h3><a href="' + item.href + '">' + item.title + '</a></h3><p>' + item.description + '</p>' + item.diagram + '<div class="mlh-case-links">' + links + '</div></div>' +
        '</article>';
    }).join("");
    rail.dataset.rendered = "true";
  }

  renderProjectRail();

  var hs = root.querySelector("[data-hscroll]");
  function hsActivate(hsEl) {
    hsEl.classList.add("is-on");
    var w = hsEl.closest(".mlh-work");
    if (w) w.classList.add("mlh-work--h");
    return function () {
      hsEl.classList.remove("is-on", "mlh-hscroll--vanilla");
      if (w) w.classList.remove("mlh-work--h");
    };
  }

  /* depth + progress readout for the marquee: neighbor cards scale and
     fade by distance from the section center, ghost numerals drift in
     counter-parallax, dots + counter track whichever case is centered,
     and the neural rail canvas gets the loop position as parallax. */
  var hsRailCanvas = hs && hs.querySelector(".mlh-neural--rail");
  var hsProgressDots = hs ? hs.querySelectorAll("[data-hscroll-progress] > span:not(.mlh-hscroll-count)") : [];
  var hsCount = hs && hs.querySelector("[data-hscroll-count]");
  function hsDepth(track, sticky, baseCount, offset, half) {
    var stickyRect = sticky.getBoundingClientRect();
    var centerX = stickyRect.left + stickyRect.width / 2;
    var halfW = stickyRect.width / 2 || 1;
    var best = 0, bestD = Infinity;
    track.querySelectorAll(".mlh-case").forEach(function (panel, i) {
      var r = panel.getBoundingClientRect();
      var dSigned = ((r.left + r.width / 2) - centerX) / halfW;
      var dNorm = Math.min(1, Math.abs(dSigned));
      if (!reduced) {
        panel.style.transform = "scale(" + (1 - dNorm * 0.09).toFixed(3) + ")";
        panel.style.opacity = (1 - dNorm * 0.4).toFixed(3);
        panel.style.setProperty("--hs-num-x", (dSigned * -70).toFixed(1) + "px");
      }
      if (dNorm < bestD) { bestD = dNorm; best = i % baseCount; }
    });
    if (hsProgressDots.length) {
      hsProgressDots.forEach(function (dot, i) {
        dot.classList.toggle("is-active", i === best);
      });
      if (hsCount) hsCount.innerHTML = "<b>0" + (best + 1) + "</b> / 0" + baseCount;
    }
    if (hsRailCanvas && window.mlhNeuralSetParallax && half > 0) {
      window.mlhNeuralSetParallax(hsRailCanvas, ((offset / half) % 1) * 2 - 1);
    }
  }

  /* The rail is a self-drifting infinite marquee — it never pins or
     hijacks the page scroll (user review round 5). The cases drift
     sideways on their own; hovering holds them, dragging scrubs them,
     and everything pauses off-screen or when the tab is hidden. Under
     prefers-reduced-motion there is no autonomous drift — the rail
     stays static and draggable. Mobile (≤900px) keeps its native
     swipe carousel, pure CSS. */
  if (hs) {
    hsActivate(hs);
    var hsTrack = hs.querySelector(".mlh-hscroll-track");
    var hsSticky = hs.querySelector(".mlh-hscroll-sticky");
    var hsBase = hsTrack.querySelectorAll(".mlh-case").length;
    /* duplicate the set once — the second half makes the loop seamless */
    hsTrack.innerHTML += hsTrack.innerHTML;
    hsTrack.querySelectorAll(".mlh-case").forEach(function (p) {
      p.classList.add("is-in");
      p.removeAttribute("data-reveal");
    });
    var hsOffset = 0, hsHalf = 0, hsGoal = null;
    var hsVel = null, hsVisible = true, hsDragX = null, hsDragged = 0;
    var HS_MAX = reduced ? 0 : 0.5; /* px/frame ≈ 30px/s — also the edge-drive cap */
    function hsMeasure() { hsHalf = hsTrack.scrollWidth / 2; }
    window.addEventListener("resize", hsMeasure);
    window.addEventListener("load", hsMeasure);
    hsMeasure();

    if ("IntersectionObserver" in window) {
      new IntersectionObserver(function (entries) {
        hsVisible = entries[0].isIntersecting;
      }, { rootMargin: "10% 0px" }).observe(hs);
    }

    /* cursor-directed drive (fine pointers): the pointer's distance from
       the section center sets direction AND speed — still in the middle
       holds the rail, edges run it at full auto speed either way */
    if (finePointer) {
      hs.addEventListener("pointermove", function (e) {
        if (e.pointerType !== "mouse") return;
        var r = hs.getBoundingClientRect();
        var nx = ((e.clientX - r.left) / (r.width || 1)) * 2 - 1;
        var mag = Math.max(0, Math.abs(nx) - 0.16) / 0.84;
        hsVel = (nx < 0 ? -1 : 1) * mag * mag * HS_MAX;
      });
      hs.addEventListener("mouseleave", function () { hsVel = null; });
    }

    /* drag to scrub — mouse and touch (track is touch-action: pan-y, so
       vertical page scroll still works on phones) */
    hsTrack.addEventListener("pointerdown", function (e) {
      hsDragX = e.clientX;
      hsDragged = 0;
      hsGoal = null;
    });
    window.addEventListener("pointermove", function (e) {
      if (hsDragX === null) return;
      var dx = e.clientX - hsDragX;
      hsOffset -= dx;
      hsDragged += Math.abs(dx);
      hsDragX = e.clientX;
    }, { passive: true });
    window.addEventListener("pointerup", function () { hsDragX = null; });
    /* touch scrolling fires pointercancel, never pointerup — without
       this the drag stayed "stuck" and the marquee froze on mobile */
    window.addEventListener("pointercancel", function () { hsDragX = null; });

    /* wrapped position used for rendering + click math. hsOffset itself
       stays unbounded: wrapping it every frame while easing toward an
       out-of-range goal caused the "spins at full speed forever" bug. */
    function hsWrapped() { return ((hsOffset % hsHalf) + hsHalf) % hsHalf; }

    function hsGlideTo(target) {
      var delta = ((target - hsWrapped()) % hsHalf + hsHalf) % hsHalf;
      if (delta > hsHalf / 2) delta -= hsHalf;
      hsGoal = hsOffset + delta;
    }

    /* a real drag must not fire the click actions underneath */
    hsTrack.addEventListener("click", function (e) {
      if (hsDragged > 8) {
        hsDragged = 0;
        e.preventDefault();
        e.stopPropagation();
        return;
      }
      /* click on a card (not on its links) glides it to center */
      if (e.target.closest("a, button")) return;
      var card = e.target.closest(".mlh-case");
      if (!card || hsHalf <= 0) return;
      hsGlideTo(card.offsetLeft + card.offsetWidth / 2 - hsSticky.clientWidth / 2);
    }, true);

    /* translucent prev/next arrows — center the NEXT card, snapping any
       mid-drift position to the card grid first so one press always
       lands a card centered (not another half-step position) */
    function hsStep(dir) {
      var card = hsTrack.querySelector(".mlh-case");
      if (!card || hsHalf <= 0) return;
      var gap = parseFloat(getComputedStyle(hsTrack).columnGap) || 0;
      var step = card.offsetWidth + gap;
      var base = card.offsetLeft + card.offsetWidth / 2 - hsSticky.clientWidth / 2;
      var from = hsGoal === null ? hsOffset : hsGoal;
      var n = Math.round((from - base) / step);
      hsGoal = base + (n + dir) * step;
    }
    [["prev", -1, "M15 18l-6-6 6-6"], ["next", 1, "M9 6l6 6-6 6"]].forEach(function (btn) {
      var b = document.createElement("button");
      b.type = "button";
      b.className = "pf-marquee-nav pf-marquee-nav--" + btn[0];
      b.setAttribute("aria-label", btn[0] === "prev" ? "Previous case" : "Next case");
      b.innerHTML = '<svg viewBox="0 0 24 24" aria-hidden="true"><path fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" d="' + btn[2] + '"/></svg>';
      b.addEventListener("click", function (e) { e.stopPropagation(); hsStep(btn[1]); });
      hsSticky.appendChild(b);
    });

    (function hsLoop() {
      requestAnimationFrame(hsLoop);
      if (document.hidden || !hsVisible || hsHalf <= 0) return;
      if (hsDragX === null) {
        if (hsGoal !== null) {
          var d = hsGoal - hsOffset;
          if (Math.abs(d) < 0.5) { hsOffset = hsGoal; hsGoal = null; }
          else hsOffset += d * 0.09;
        } else {
          hsOffset += (hsVel === null ? HS_MAX : hsVel);
        }
      }
      hsTrack.style.transform = "translate3d(" + (-hsWrapped()).toFixed(1) + "px,0,0)";
      hsDepth(hsTrack, hsSticky, hsBase, hsWrapped(), hsHalf);
    })();
  }

  /* ---- magnetic buttons (subtle: max 6px) ---- */
  if (finePointer && !reduced) {
    root.querySelectorAll("[data-magnetic]").forEach(function (el) {
      el.addEventListener("mousemove", function (e) {
        var r = el.getBoundingClientRect();
        var dx = (e.clientX - r.left - r.width / 2) / (r.width / 2);
        var dy = (e.clientY - r.top - r.height / 2) / (r.height / 2);
        el.style.transform = "translate(" + (dx * 6).toFixed(1) + "px," + (dy * 6).toFixed(1) + "px)";
      });
      el.addEventListener("mouseleave", function () {
        el.style.transform = "";
      });
    });
  }

  /* ---- hero copy scroll parallax: text drifts up and fades slightly
     as the hero scrolls out, in counter-motion to the brain scene ---- */
  if (!reduced) {
    var heroGrid = root.querySelector(".mlh-hero-grid");
    var heroEl = root.querySelector(".mlh-hero");
    if (heroGrid && heroEl) {
      var heroTick = false;
      function heroParallax() {
        heroTick = false;
        var y = window.scrollY || 0;
        var hh = heroEl.offsetHeight || 1;
        if (y > hh * 1.2) return;
        var p = Math.min(1, y / hh);
        heroGrid.style.transform = "translateY(" + (p * 46).toFixed(1) + "px)";
        heroGrid.style.opacity = (1 - p * 0.55).toFixed(3);
      }
      window.addEventListener("scroll", function () {
        if (!heroTick) { heroTick = true; requestAnimationFrame(heroParallax); }
      }, { passive: true });
    }
  }

  /* ---- cursor glow (lerped follow) ---- */
  if (finePointer && !reduced) {
    var glow = root.querySelector(".mlh-glow");
    if (glow) {
      var tx = 0, ty = 0, cx = 0, cy = 0, raf = null;
      function tick() {
        cx += (tx - cx) * 0.08;
        cy += (ty - cy) * 0.08;
        glow.style.left = cx + "px";
        glow.style.top = cy + "px";
        if (Math.abs(tx - cx) > 0.5 || Math.abs(ty - cy) > 0.5) {
          raf = requestAnimationFrame(tick);
        } else {
          raf = null;
        }
      }
      document.addEventListener("mousemove", function (e) {
        tx = e.clientX; ty = e.clientY;
        root.classList.add("mlh-glow-on");
        if (!raf) raf = requestAnimationFrame(tick);
      }, { passive: true });
    }
  }
})();

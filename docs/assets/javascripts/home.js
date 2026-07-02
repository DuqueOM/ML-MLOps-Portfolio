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
        return '<a class="mlh-case-link" href="' + link[1] + '">' + link[0] + "</a>";
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

  /* progress dots + carousel depth (scale/opacity on neighbor cards) +
     neural-field parallax — shared by both the GSAP path and the
     vanilla fallback so the two stay in visual parity. */
  var hsRailCanvas = hs && hs.querySelector(".mlh-neural--rail");
  var hsProgressDots = hs ? hs.querySelectorAll("[data-hscroll-progress] > span:not(.mlh-hscroll-count)") : [];
  var hsCount = hs && hs.querySelector("[data-hscroll-count]");
  function hsApplyProgress(track, sticky, progress) {
    var activeIdx = 0;
    if (hsProgressDots.length) {
      activeIdx = Math.round(progress * (hsProgressDots.length - 1));
      hsProgressDots.forEach(function (dot, i) {
        dot.classList.toggle("is-active", i === activeIdx);
      });
      if (hsCount) {
        hsCount.innerHTML = "<b>0" + (activeIdx + 1) + "</b> / 0" + hsProgressDots.length;
      }
    }
    if (!reduced) {
      var panels = track.querySelectorAll(".mlh-case");
      if (panels.length > 1) {
        var stickyRect = sticky.getBoundingClientRect();
        var centerX = stickyRect.left + stickyRect.width / 2;
        var half = stickyRect.width / 2 || 1;
        panels.forEach(function (panel) {
          var r = panel.getBoundingClientRect();
          var dSigned = ((r.left + r.width / 2) - centerX) / half;
          var dNorm = Math.min(1, Math.abs(dSigned));
          panel.style.transform = "scale(" + (1 - dNorm * 0.13).toFixed(3) + ")";
          panel.style.opacity = (1 - dNorm * 0.55).toFixed(3);
          /* ghost numeral drifts against the travel direction — inner parallax */
          panel.style.setProperty("--hs-num-x", (dSigned * -90).toFixed(1) + "px");
        });
      }
    }
    if (hsRailCanvas && window.mlhNeuralSetParallax) {
      window.mlhNeuralSetParallax(hsRailCanvas, progress * 2 - 1);
    }
  }

  /* The rail runs even under prefers-reduced-motion: the scrub maps 1:1
     to the user's own scroll gesture (no autonomous motion). Reduced
     motion only drops the smoothing lag and the auto-snap. */
  if (hs && window.gsap && window.ScrollTrigger) {
    window.gsap.registerPlugin(window.ScrollTrigger);
    var mm = window.gsap.matchMedia();
    mm.add("(min-width: 901px)", function () {
      var deactivate = hsActivate(hs);
      var track = hs.querySelector(".mlh-hscroll-track");
      var sticky = hs.querySelector(".mlh-hscroll-sticky");
      var panels = track.querySelectorAll(".mlh-case").length;
      var getMax = function () {
        return Math.max(0, track.scrollWidth - sticky.clientWidth);
      };
      var tween = window.gsap.to(track, {
        x: function () { return -getMax(); },
        ease: "none",
        scrollTrigger: {
          trigger: hs,
          pin: true,
          scrub: reduced ? true : 1,
          anticipatePin: 1,
          start: "top top",
          end: function () { return "+=" + Math.max(window.innerHeight, getMax()); },
          invalidateOnRefresh: true,
          onUpdate: function (self) { hsApplyProgress(track, sticky, self.progress); },
          snap: (!reduced && panels > 1) ? {
            snapTo: 1 / (panels - 1),
            duration: { min: 0.2, max: 0.55 },
            ease: "power1.inOut"
          } : false
        }
      });
      /* fonts settle after load — recompute distances */
      window.addEventListener("load", function () { window.ScrollTrigger.refresh(); });
      requestAnimationFrame(function () { window.ScrollTrigger.refresh(); });
      return function () {
        if (tween.scrollTrigger) tween.scrollTrigger.kill();
        tween.kill();
        deactivate();
        window.gsap.set(track, { clearProps: "all" });
        track.querySelectorAll(".mlh-case").forEach(function (panel) {
          panel.style.transform = "";
          panel.style.opacity = "";
        });
      };
    });
  } else if (hs && window.matchMedia("(min-width: 901px)").matches) {
    /* vanilla fallback (CDN blocked): sticky viewport + manual scrub */
    hs.classList.add("mlh-hscroll--vanilla");
    hsActivate(hs);
    var hsSticky = hs.querySelector(".mlh-hscroll-sticky");
    var hsTrack = hs.querySelector(".mlh-hscroll-track");
    var hsMax = 0;
    function hsUpdate() {
      var top = hs.getBoundingClientRect().top;
      var range = hs.offsetHeight - window.innerHeight;
      var p = range > 0 ? Math.min(1, Math.max(0, -top / range)) : 0;
      hsTrack.style.transform = "translate3d(" + (-p * hsMax).toFixed(1) + "px,0,0)";
      hsApplyProgress(hsTrack, hsSticky, p);
    }
    function hsMeasure() {
      hsMax = Math.max(0, hsTrack.scrollWidth - hsSticky.clientWidth);
      hs.style.height = (window.innerHeight + hsMax) + "px";
      hsUpdate();
    }
    var hsTick = false;
    window.addEventListener("scroll", function () {
      if (!hsTick) { requestAnimationFrame(function () { hsUpdate(); hsTick = false; }); hsTick = true; }
    }, { passive: true });
    window.addEventListener("resize", hsMeasure);
    window.addEventListener("load", hsMeasure);
    hsMeasure();
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

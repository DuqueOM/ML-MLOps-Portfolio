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

  /* ---- pinned horizontal case rail (GSAP ScrollTrigger; vanilla fallback) ----
     Desktop only: the section pins to the viewport and vertical scroll
     scrubs the three feature panels horizontally, snapping per panel.
     Mobile / reduced-motion / no-JS: panels stack vertically untouched. */
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

  if (hs && !reduced && window.gsap && window.ScrollTrigger) {
    window.gsap.registerPlugin(window.ScrollTrigger);
    var mm = window.gsap.matchMedia();
    mm.add("(min-width: 901px)", function () {
      var deactivate = hsActivate(hs);
      var track = hs.querySelector(".mlh-hscroll-track");
      var panels = track.querySelectorAll(".mlh-case").length;
      var getMax = function () {
        return Math.max(0, track.scrollWidth - hs.clientWidth);
      };
      window.gsap.to(track, {
        x: function () { return -getMax(); },
        ease: "none",
        scrollTrigger: {
          trigger: hs,
          pin: true,
          scrub: 1,
          anticipatePin: 1,
          start: "top top",
          end: function () { return "+=" + getMax(); },
          invalidateOnRefresh: true,
          snap: panels > 1 ? {
            snapTo: 1 / (panels - 1),
            duration: { min: 0.2, max: 0.55 },
            ease: "power1.inOut"
          } : false
        }
      });
      /* fonts settle after load — recompute distances */
      window.addEventListener("load", function () { window.ScrollTrigger.refresh(); });
      return function () {
        deactivate();
        window.gsap.set(track, { clearProps: "all" });
      };
    });
  } else if (hs && !reduced && window.matchMedia("(min-width: 901px)").matches) {
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

/* Inner-page microinteractions — vanilla, no dependencies.
   Scroll reveals with per-row stagger, reading progress, magnetic
   buttons and an ambient cursor glow. The home page is skipped
   (it ships its own orchestration in home.js); reduced motion
   disables everything. */
(function () {
  "use strict";

  if (document.querySelector(".ml-home")) return;
  var page = document.querySelector(".portfolio-page");
  if (!page) return;

  var reduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  var finePointer = window.matchMedia("(pointer: fine)").matches;

  /* ---- reading progress ---- */
  var bar = document.createElement("div");
  bar.className = "pf-progress";
  bar.setAttribute("aria-hidden", "true");
  document.body.appendChild(bar);
  var ticking = false;
  function paintProgress() {
    var doc = document.documentElement;
    var max = doc.scrollHeight - doc.clientHeight;
    bar.style.transform = "scaleX(" + (max > 0 ? doc.scrollTop / max : 0) + ")";
    ticking = false;
  }
  window.addEventListener("scroll", function () {
    if (!ticking) { requestAnimationFrame(paintProgress); ticking = true; }
  }, { passive: true });
  paintProgress();

  /* ---- scroll reveals with per-row stagger ---- */
  if (!reduced && "IntersectionObserver" in window) {
    var targets = page.querySelectorAll(
      ".portfolio-card, .portfolio-stat, .portfolio-system-node, " +
      ".portfolio-step, .portfolio-status-card, .portfolio-callout, " +
      ".portfolio-quote-card, .portfolio-faq-item, .portfolio-media"
    );
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          entry.target.classList.add("is-in");
          io.unobserve(entry.target);
        }
      });
    }, { threshold: 0.12, rootMargin: "0px 0px -6% 0px" });
    targets.forEach(function (el) {
      var idx = Array.prototype.indexOf.call(el.parentElement.children, el);
      el.style.transitionDelay = (idx % 6) * 55 + "ms";
      el.classList.add("js-reveal");
      io.observe(el);
    });
  }

  /* ---- magnetic buttons (subtle: max 4px) ---- */
  if (finePointer && !reduced) {
    document.querySelectorAll(".portfolio-button").forEach(function (el) {
      el.addEventListener("mousemove", function (e) {
        var r = el.getBoundingClientRect();
        var dx = (e.clientX - r.left - r.width / 2) / (r.width / 2);
        var dy = (e.clientY - r.top - r.height / 2) / (r.height / 2);
        el.style.transform = "translate(" + (dx * 4).toFixed(1) + "px," + (dy * 4).toFixed(1) + "px)";
      });
      el.addEventListener("mouseleave", function () { el.style.transform = ""; });
    });
  }

  /* ---- ambient cursor glow ---- */
  if (finePointer && !reduced) {
    var glow = document.createElement("div");
    glow.className = "pf-glow";
    glow.setAttribute("aria-hidden", "true");
    document.body.appendChild(glow);
    var tx = 0, ty = 0, cx = 0, cy = 0, raf = null;
    function tick() {
      cx += (tx - cx) * 0.08;
      cy += (ty - cy) * 0.08;
      glow.style.left = cx + "px";
      glow.style.top = cy + "px";
      raf = (Math.abs(tx - cx) > 0.5 || Math.abs(ty - cy) > 0.5)
        ? requestAnimationFrame(tick) : null;
    }
    document.addEventListener("mousemove", function (e) {
      tx = e.clientX; ty = e.clientY;
      glow.classList.add("is-on");
      if (!raf) raf = requestAnimationFrame(tick);
    }, { passive: true });
  }
})();

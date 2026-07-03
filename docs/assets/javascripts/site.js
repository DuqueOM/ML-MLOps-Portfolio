/* Site-wide UI tweaks — vanilla, no dependencies. Unlike home.js and
   portfolio.js this file runs on EVERY page (loaded via mkdocs.yml
   extra_javascript), so keep it small and unconditional.

   1) Mobile drawer: the "Projects" section behaves as a direct link to
      the overview page instead of unfolding a submenu (user request —
      desktop keeps the full sidebar).
   2) pfMarquee: the generic infinite-drift rail extracted from the home
      case carousel — auto-drift, cursor-edge direction/speed, drag to
      scrub, click/tap to center, edge fade handled by CSS. Auto-mounts
      on About's ".pf-toolbox". */
(function () {
  "use strict";

  var reduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  var finePointer = window.matchMedia("(pointer: fine)").matches;

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

  function init() {
    patchDrawer();
    document.querySelectorAll(".pf-toolbox, [data-pf-marquee]").forEach(pfMarquee);
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();

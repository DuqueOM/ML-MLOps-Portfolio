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
   3) Chat widget: floating assistant backed by the Cloudflare Worker in
      cloudflare/portfolio-chat-worker.js. Mounted on every page since a
      recruiter can land on any tab. History lives in memory only —
      resets on reload, nothing persisted, nothing sent anywhere but the
      Worker (which itself only forwards to Workers AI). */
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

  /* ---- 3) chat widget: floating neural-avatar assistant + panel ----
     The launcher shows the neural "wireframe bust" avatar image (same
     visual language as the site's neural scenes), breathing slowly.
     A speech-bubble hint with three dots pulses in every so often
     before the visitor has opened it once — a quiet nudge, not a
     badge/counter. When open, the avatar dims under a ✕ overlay. */
  function initChatWidget() {
    if (document.querySelector(".pf-chat-launcher")) return;

    var history = [];
    var pending = false;
    var greeted = false;
    var hasOpened = false;
    var hintTimer = null;

    /* pages sit at different depths — derive the site base from this
       script's own URL instead of hardcoding a relative path */
    var sj = document.querySelector('script[src*="site.js"]');
    var AVATAR_URL = sj
      ? sj.src.replace(/assets\/javascripts\/site\.js.*$/, "media/profile/assistant-avatar.png")
      : "media/profile/assistant-avatar.png";

    var launcher = document.createElement("button");
    launcher.type = "button";
    launcher.className = "pf-chat-launcher";
    launcher.setAttribute("aria-label", "Open portfolio assistant");
    launcher.setAttribute("aria-expanded", "false");
    launcher.innerHTML =
      '<span class="pf-chat-avatar-clip" aria-hidden="true">' +
        '<img class="pf-chat-avatar" src="' + AVATAR_URL + '" alt="">' +
      "</span>" +
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

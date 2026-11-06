/* PaperGaki deck runtime — fixed 16:9 stage, keyboard/touch navigation. */
(function () {
  "use strict";

  var stage = document.querySelector(".deck-stage");
  var slides = Array.prototype.slice.call(document.querySelectorAll(".slide"));
  if (!stage || !slides.length) return;

  var fill = document.querySelector(".hud__fill");
  var count = document.querySelector(".hud__count");
  var index = 0;

  function fit() {
    var scale = Math.min(window.innerWidth / 1920, window.innerHeight / 1080);
    var x = (window.innerWidth - 1920 * scale) / 2;
    var y = (window.innerHeight - 1080 * scale) / 2;
    stage.style.transform = "translate(" + x + "px," + y + "px) scale(" + scale + ")";
  }

  function render() {
    slides.forEach(function (slide, i) {
      var active = i === index;
      slide.classList.toggle("is-active", active);
      slide.setAttribute("aria-hidden", active ? "false" : "true");
    });
    if (fill) fill.style.width = ((index + 1) / slides.length) * 100 + "%";
    if (count) {
      var w = String(slides.length).length;
      count.textContent =
        String(index + 1).padStart(w, "0") + " / " + String(slides.length).padStart(w, "0");
    }
    try {
      history.replaceState(null, "", "#" + (index + 1));
    } catch (e) {
      /* file:// */
    }
  }

  function go(n) {
    var next = Math.max(0, Math.min(slides.length - 1, n));
    if (next === index) return;
    index = next;
    render();
  }

  function fromHash() {
    var n = parseInt((location.hash || "").replace("#", ""), 10);
    if (!isNaN(n)) index = Math.max(0, Math.min(slides.length - 1, n - 1));
    render();
  }

  window.addEventListener("resize", fit);

  document.addEventListener("keydown", function (event) {
    var key = event.key;
    if (key === "ArrowRight" || key === "PageDown" || key === " " || key === "Enter") {
      event.preventDefault();
      go(index + 1);
    } else if (key === "ArrowLeft" || key === "PageUp") {
      event.preventDefault();
      go(index - 1);
    } else if (key === "Home") {
      event.preventDefault();
      go(0);
    } else if (key === "End") {
      event.preventDefault();
      go(slides.length - 1);
    } else if (key === "f" || key === "F") {
      event.preventDefault();
      if (document.fullscreenElement) document.exitFullscreen();
      else if (document.documentElement.requestFullscreen) document.documentElement.requestFullscreen();
    } else if (key === "p" || key === "P") {
      event.preventDefault();
      window.print();
    }
  });

  document.addEventListener("click", function (event) {
    if (event.target.closest("a")) return;
    var x = event.clientX / window.innerWidth;
    if (x > 0.6) go(index + 1);
    else if (x < 0.4) go(index - 1);
  });

  var touchX = null;
  document.addEventListener("touchstart", function (e) {
    touchX = e.touches[0].clientX;
  }, { passive: true });
  document.addEventListener("touchend", function (e) {
    if (touchX === null) return;
    var dx = e.changedTouches[0].clientX - touchX;
    if (Math.abs(dx) > 46) go(index + (dx < 0 ? 1 : -1));
    touchX = null;
  }, { passive: true });

  window.addEventListener("hashchange", fromHash);

  fit();
  fromHash();
})();

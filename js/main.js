(function () {
  "use strict";

  var nav = document.querySelector("[data-nav]");
  var toggle = document.querySelector("[data-nav-toggle]");
  var yearNodes = document.querySelectorAll("[data-year]");
  var form = document.querySelector("[data-booking-form]");

  yearNodes.forEach(function (node) {
    node.textContent = String(new Date().getFullYear());
  });

  if (toggle && nav) {
    function closeMenu() {
      nav.classList.remove("is-open");
      toggle.setAttribute("aria-expanded", "false");
    }
    toggle.addEventListener("click", function () {
      var open = nav.classList.toggle("is-open");
      toggle.setAttribute("aria-expanded", open ? "true" : "false");
      document.body.classList.toggle("nav-open", open);
    });

    nav.querySelectorAll("a").forEach(function (link) {
      link.addEventListener("click", function () {
        nav.classList.remove("is-open");
        toggle.setAttribute("aria-expanded", "false");
        document.body.classList.remove("nav-open");
      });
    });
    document.addEventListener("keydown", function (event) {
      if (event.key === "Escape" && nav.classList.contains("is-open")) {
        closeMenu();
        toggle.focus();
      }
    });
    document.addEventListener("click", function (event) {
      if (!nav.contains(event.target) && !toggle.contains(event.target)) closeMenu();
    });
  }

  document.querySelectorAll("[data-submenu-toggle]").forEach(function (button) {
    button.addEventListener("click", function () {
      var expanded = button.getAttribute("aria-expanded") === "true";
      button.setAttribute("aria-expanded", expanded ? "false" : "true");
      var menu = button.nextElementSibling;
      if (menu) {
        menu.hidden = expanded;
      }
    });
  });

  function siteBase() {
    var base = document.querySelector("base[href]");
    if (base && base.href) {
      return base.href.endsWith("/") ? base.href : base.href + "/";
    }
    return window.location.origin + "/";
  }

  var params = new URLSearchParams(window.location.search);
  var campaignKeys = ["utm_source", "utm_medium", "utm_campaign", "utm_content", "utm_term"];
  var filePreview = /^(raw|rawcdn)\.githack\.com$/.test(window.location.hostname);
  var reasonSelect = form && form.querySelector("[name='reason']");
  if (reasonSelect && Array.from(reasonSelect.options).some(function (option) { return option.value === params.get("reason"); })) {
    reasonSelect.value = params.get("reason");
  }
  // Keep attribution in same-site links without storing visitor data.
  document.querySelectorAll("a[href]").forEach(function (link) {
    var url = new URL(link.href);
    if (url.origin !== window.location.origin || !url.pathname.startsWith(new URL(siteBase()).pathname)) return;
    campaignKeys.forEach(function (key) {
      if (params.has(key)) url.searchParams.set(key, params.get(key));
    });
    if (url.pathname.endsWith("/contact/") && url.hash === "#book") {
      var reason = form && form.querySelector("[name='reason']");
      if (reason) url.searchParams.set("reason", reason.value);
    }
    // File-based branch previews do not serve directory indexes automatically.
    if (filePreview && url.pathname.endsWith("/")) url.pathname += "index.html";
    link.href = url.href;
  });

  if (form) {
    var nextField = form.querySelector("[name='_next']");
    if (nextField) {
      nextField.value = siteBase() + "thank-you/" + (filePreview ? "index.html" : "");
    }

    var pageField = form.querySelector("[name='page']");
    if (pageField) {
      pageField.value = window.location.href;
    }

    campaignKeys.forEach(function (key) {
      var input = form.querySelector("[name='" + key + "']");
      if (input && params.get(key)) {
        input.value = params.get(key);
      }
    });

  }
})();

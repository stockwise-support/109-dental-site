(function () {
  "use strict";

  var nav = document.querySelector("[data-nav]");
  var toggle = document.querySelector("[data-nav-toggle]");
  var yearNodes = document.querySelectorAll("[data-year]");
  var form = document.querySelector("[data-booking-form]");
  var faqButtons = document.querySelectorAll("[data-faq-button]");

  yearNodes.forEach(function (node) {
    node.textContent = String(new Date().getFullYear());
  });

  if (toggle && nav) {
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

  faqButtons.forEach(function (button) {
    button.addEventListener("click", function () {
      var expanded = button.getAttribute("aria-expanded") === "true";
      var panelId = button.getAttribute("aria-controls");
      var panel = panelId ? document.getElementById(panelId) : null;
      button.setAttribute("aria-expanded", expanded ? "false" : "true");
      if (panel) {
        panel.hidden = expanded;
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

  if (form) {
    var nextField = form.querySelector("[name='_next']");
    if (nextField) {
      nextField.value = siteBase() + "thank-you/";
    }

    var pageField = form.querySelector("[name='page']");
    if (pageField) {
      pageField.value = window.location.href;
    }

    var params = new URLSearchParams(window.location.search);
    ["utm_source", "utm_medium", "utm_campaign", "utm_content", "utm_term"].forEach(function (key) {
      var input = form.querySelector("[name='" + key + "']");
      if (input && params.get(key)) {
        input.value = params.get(key);
      }
    });

    var reasonSelect = form.querySelector("[name='reason']");
    if (reasonSelect && params.get("reason")) {
      reasonSelect.value = params.get("reason");
    }
  }
})();

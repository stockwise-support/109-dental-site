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
      document.body.classList.remove("nav-open");
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

  if (form) {
    var nextField = form.querySelector("[name='_next']");
    if (nextField) {
      nextField.value = siteBase() + "thank-you/";
    }

    var pageField = form.querySelector("[name='page']");
    if (pageField) {
      pageField.value = window.location.origin + window.location.pathname;
    }


  }
})();

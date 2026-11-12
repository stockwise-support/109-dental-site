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

  if (form) {
    var button = form.querySelector("button[type='submit']");
    var status = form.querySelector("[data-form-status]");
    var busy = false;
    var ready = false;
    var finished = false;
    var endpoint = new URL(form.getAttribute("action"), document.baseURI);
    function report(message, error) {
      status.textContent = message;
      status.classList.toggle("form-error", !!error);
    }
    async function request(options) {
      var controller = new AbortController();
      var timeout = setTimeout(function () { controller.abort(); }, 20000);
      try {
        var response = await fetch(endpoint, Object.assign({credentials:"same-origin",cache:"no-store",headers:{"X-Enquiry-Request":"1"},signal:controller.signal}, options));
        var data = await response.json();
        return {response:response,data:data};
      } finally { clearTimeout(timeout); }
    }
    async function prepare() {
      try {
        if (window.location.protocol !== "https:" || endpoint.origin !== window.location.origin) throw new Error();
        var result = await request({method:"GET"});
        if (!result.response.ok || !result.data.csrf || !result.data.request_id) throw new Error();
        form.elements.csrf.value = result.data.csrf;
        form.elements.request_id.value = result.data.request_id;
        ready = true;
        button.disabled = false;
        report("", false);
      } catch (_) {
        report("The secure form is unavailable. Please call or email us using the details below.", true);
      }
    }
    form.addEventListener("submit", async function (event) {
      event.preventDefault();
      if (busy || finished || !ready || !form.reportValidity()) return;
      busy = true;
      button.disabled = true;
      button.textContent = "Sending…";
      form.setAttribute("aria-busy", "true");
      report("Sending your enquiry…", false);
      try {
        var result = await request({method:"POST",body:new URLSearchParams(new FormData(form))});
        if (!result.response.ok) {
          report((result.data.error || "We could not send your enquiry.") + " You can call or email us using the details below.", true);
          // Validation errors can be corrected. Delivery failures and ambiguous outcomes require office contact.
          finished = result.response.status !== 422;
        } else {
          finished = true;
          report(result.data.message, false);
          form.reset();
        }
      } catch (_) {
        finished = true;
        report("We could not confirm whether your enquiry was accepted. Please call or email us rather than submitting again.", true);
      } finally {
        busy = false;
        form.removeAttribute("aria-busy");
        button.disabled = finished;
        button.textContent = finished ? "Enquiry finished" : "Send enquiry";
      }
    });
    prepare();
  }
})();

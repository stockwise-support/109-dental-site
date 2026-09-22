#!/usr/bin/env python3
"""Generate the static 109 Dental HTML pages. Run from repo root: python3 tools/generate.py"""

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CANON = "https://109dental.ca"
# Fallback <base> for GitHub Pages. An inline script then rewrites it:
# GH Pages (/109-dental-site/) keeps this prefix; Vercel/Hostinger/localhost
# use the current origin + "/". Do not use path-absolute /css URLs.
GH_PAGES_BASE = "https://stockwise-support.github.io/109-dental-site/"


def u(path: str) -> str:
    """Site path as a <base>-relative URL."""
    if not path or path == "/":
        return "./"
    if path.startswith(("#", "tel:", "mailto:", "http://", "https://")):
        return path
    return path.lstrip("/")


def rebase_html(html: str) -> str:
    """Convert leftover path-absolute href/src to base-relative URLs."""

    def repl(match: re.Match[str]) -> str:
        attr, quote, url = match.group(1), match.group(2), match.group(3)
        if url.startswith("/") and not url.startswith("//"):
            url = "./" if url == "/" else url.lstrip("/")
        return f"{attr}={quote}{url}{quote}"

    return re.sub(r"\b(href|src)=([\"'])([^\"']+)\2", repl, html)
PHONE_DISPLAY = "(780) 435-5300"
PHONE_TEL = "+17804355300"
EMAIL = "dental_appointment@shaw.ca"
NAP_NAME = "109 Dental"
NAP_STREET = "Suite 204, 7125 109 St NW"
NAP_CITY = "Edmonton, AB T6G 1B9"
ENTITY = (
    "109 Dental is a family dental clinic in Suite 204 at 7125 109 Street NW "
    "in Edmonton's Queen Alexandra / Strathcona area, near the University of Alberta."
)
MAP_EMBED = (
    "https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d2372.7717299152596"
    "!2d-113.51137609999999!3d53.508272999999996!2m3!1f0!2f0!3f0!3m2!1i1024"
    "!2i768!4f13.1!3m3!1m2!1s0x53a021ff735aaf45%3A0x2c79bd58134a09ae"
    "!2s109%20Dental%20%7C%20South%20Edmonton%20Dentist!5e0!3m2!1sen!2sca"
)
MAP_LINK = (
    "https://www.google.com/maps/place/109+Dental/"
    "@53.508273,-113.5113761,15z/data=!4m6!3m5!1s0x53a021ff735aaf45:0x2c79bd58134a09ae"
    "!8m2!3d53.508273!4d-113.5113761"
)
FB = "https://www.facebook.com/109Dental"
IG = "https://www.instagram.com/109Dental"

SERVICES = [
    ("/services/family-dentistry/", "Family Dentistry"),
    ("/services/childrens-dentistry/", "Children's Dentistry"),
    ("/services/emergency-dentist/", "Emergency Dentist"),
    ("/services/wisdom-teeth/", "Wisdom Teeth"),
    ("/services/dental-implants/", "Dental Implants"),
    ("/services/cosmetic-dentistry/", "Cosmetic Dentistry"),
    ("/services/orthodontics-invisalign/", "Orthodontics & Invisalign"),
    ("/services/root-canals/", "Root Canals"),
    ("/services/crowns-bridges/", "Crowns & Bridges"),
]


def esc(text: str) -> str:
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def nav_html(current: str) -> str:
    def item(href, label, key):
        cur = ' aria-current="page"' if current == key else ""
        return f'<li><a href="{u(href)}"{cur}>{label}</a></li>'

    service_links = []
    for href, label in SERVICES:
        current_attr = ' aria-current="page"' if current == href else ""
        service_links.append(f'<a href="{u(href)}"{current_attr}>{label}</a>')
    service_links = "\n".join(service_links)
    services_current = ' aria-current="page"' if current.startswith("/services") else ""
    return f"""
    <nav class="nav" id="site-nav" data-nav aria-label="Primary">
      <ul class="nav-list">
        {item("/", "Home", "/")}
        {item("/about/", "About", "/about/")}
        <li class="has-sub">
          <a href="{u('/services/')}"{services_current}>Services</a>
          <div class="submenu">
            <a href="{u('/services/')}">All services</a>
            {service_links}
          </div>
        </li>
        {item("/new-patients/", "New Patients", "/new-patients/")}
        {item("/reviews/", "Reviews", "/reviews/")}
        {item("/contact/", "Contact", "/contact/")}
      </ul>
    </nav>
    """


def footer_html() -> str:
    service_lis = "\n".join(f'<li><a href="{u(href)}">{label}</a></li>' for href, label in SERVICES)
    return f"""
<footer class="site-footer">
  <div class="container footer-grid">
    <div>
      <div class="footer-title">{NAP_NAME}</div>
      <address class="nap">
        <p>{NAP_NAME}</p>
        <p>{NAP_STREET}<br>{NAP_CITY}</p>
        <p><a href="tel:{PHONE_TEL}">{PHONE_DISPLAY}</a></p>
        <p><a href="mailto:{EMAIL}">{EMAIL}</a></p>
        <p><a href="{CANON}">{CANON.replace("https://", "")}</a></p>
      </address>
      <p><a href="{MAP_LINK}">Open Edmonton map</a></p>
    </div>
    <div>
      <div class="footer-title">Visit</div>
      <ul class="footer-links">
        <li><a href="{u('/')}">Home</a></li>
        <li><a href="{u('/about/')}">About</a></li>
        <li><a href="{u('/new-patients/')}">New patients</a></li>
        <li><a href="{u('/reviews/')}">Reviews</a></li>
        <li><a href="{u('/contact/')}">Contact</a></li>
        <li><a href="{u('/privacy/')}">Privacy</a></li>
        <li><a href="{u('/accessibility/')}">Accessibility</a></li>
      </ul>
    </div>
    <div>
      <div class="footer-title">Services</div>
      <ul class="footer-links">
        {service_lis}
      </ul>
    </div>
  </div>
</footer>
"""


def sticky_bar() -> str:
    return f"""
<div class="sticky-bar" aria-label="Mobile contact actions">
  <a class="btn btn-primary" href="tel:{PHONE_TEL}">Call {PHONE_DISPLAY}</a>
  <a class="btn btn-copper" href="{u('/contact/#book')}">Book</a>
</div>
"""


def booking_form(default_reason: str = "other", heading: str = "Request an appointment") -> str:
    reasons = [
        ("new-patient", "New patient visit"),
        ("wisdom", "Wisdom teeth"),
        ("emergency", "Dental emergency"),
        ("other", "Other / general care"),
    ]
    options = "\n".join(
        f'<option value="{value}"{" selected" if value == default_reason else ""}>{label}</option>'
        for value, label in reasons
    )
    return f"""
<form class="form-card" data-booking-form action="https://formsubmit.co/{EMAIL}" method="POST">
  <h2>{heading}</h2>
  <p class="form-note">Short request only. We reply during business hours. For pain or swelling, call {PHONE_DISPLAY} first.</p>
  <input type="hidden" name="_subject" value="109 Dental appointment request">
  <input type="hidden" name="_template" value="table">
  <input type="hidden" name="_captcha" value="false">
  <input type="hidden" name="_next" value="{CANON}/thank-you/">
  <input type="hidden" name="page" value="">
  <input type="hidden" name="utm_source" value="">
  <input type="hidden" name="utm_medium" value="">
  <input type="hidden" name="utm_campaign" value="">
  <input type="hidden" name="utm_content" value="">
  <input type="hidden" name="utm_term" value="">
  <label class="hp" for="website">Website</label>
  <input class="hp" id="website" type="text" name="_honey" tabindex="-1" autocomplete="off">
  <label for="name">Name</label>
  <input id="name" name="name" type="text" required autocomplete="name">
  <label for="phone">Phone</label>
  <input id="phone" name="phone" type="tel" required autocomplete="tel">
  <label for="email">Email</label>
  <input id="email" name="email" type="email" required autocomplete="email">
  <label for="preferred_time">Preferred time</label>
  <input id="preferred_time" name="preferred_time" type="text" placeholder="Morning, afternoon, or a day that works">
  <label for="reason">Reason for visit</label>
  <select id="reason" name="reason" required>
    {options}
  </select>
  <label for="notes">Notes (optional)</label>
  <textarea id="notes" name="notes"></textarea>
  <button class="btn btn-primary" type="submit">Send request</button>
</form>
"""


def photo(label: str, min_height: str | None = None) -> str:
    style = f' style="min-height:{min_height}"' if min_height else ""
    return f'<div class="photo-ph"{style}><span>Photo placeholder: {esc(label)}</span></div>'


def faq_block(items: list[tuple[str, str]]) -> str:
    parts = ['<div class="faq">']
    for i, (q, a) in enumerate(items, 1):
        parts.append(
            f"""
            <div class="faq-item">
              <button type="button" data-faq-button aria-expanded="false" aria-controls="faq-{i}">{esc(q)}</button>
              <div class="faq-panel" id="faq-{i}" hidden><p>{a}</p></div>
            </div>
            """
        )
    parts.append("</div>")
    return "\n".join(parts)


def crumbs(items: list[tuple[str, str]]) -> str:
    bits = []
    for i, (href, label) in enumerate(items):
        if i == len(items) - 1:
            bits.append(f"<span>{esc(label)}</span>")
        else:
            bits.append(f'<a href="{u(href)}">{esc(label)}</a>')
    return f'<nav class="crumbs" aria-label="Breadcrumb">{" / ".join(bits)}</nav>'


def dentist_schema() -> str:
    return f"""
{{
  "@context": "https://schema.org",
  "@type": ["Dentist", "DentalClinic"],
  "name": "{NAP_NAME}",
  "url": "{CANON}/",
  "telephone": "{PHONE_TEL}",
  "email": "{EMAIL}",
  "image": "{CANON}/assets/logo.svg",
  "address": {{
    "@type": "PostalAddress",
    "streetAddress": "{NAP_STREET}",
    "addressLocality": "Edmonton",
    "addressRegion": "AB",
    "postalCode": "T6G 1B9",
    "addressCountry": "CA"
  }},
  "geo": {{
    "@type": "GeoCoordinates",
    "latitude": 53.508273,
    "longitude": -113.5113761
  }},
  "openingHoursSpecification": [
    {{"@type":"OpeningHoursSpecification","dayOfWeek":["Monday","Tuesday"],"opens":"08:30","closes":"16:30"}},
    {{"@type":"OpeningHoursSpecification","dayOfWeek":["Wednesday","Thursday"],"opens":"07:30","closes":"15:30"}},
    {{"@type":"OpeningHoursSpecification","dayOfWeek":["Friday"],"opens":"09:00","closes":"15:00"}}
  ],
  "sameAs": ["{FB}", "{IG}", "{MAP_LINK}"],
  "areaServed": ["Queen Alexandra", "Strathcona", "University of Alberta", "Whyte Avenue", "Edmonton"],
  "isAcceptingNewPatients": true,
  "priceRange": "$$"
}}
"""


def faq_schema(items: list[tuple[str, str]]) -> str:
    return json.dumps(
        {
            "@context": "https://schema.org",
            "@type": "FAQPage",
            "mainEntity": [
                {
                    "@type": "Question",
                    "name": q,
                    "acceptedAnswer": {"@type": "Answer", "text": a},
                }
                for q, a in items
            ],
        }
    )


def service_schema(name: str, url: str, desc: str) -> str:
    return json.dumps(
        {
            "@context": "https://schema.org",
            "@type": "Service",
            "name": name,
            "serviceType": name,
            "url": CANON + url,
            "description": desc,
            "areaServed": ["Queen Alexandra", "Strathcona", "University of Alberta", "Edmonton"],
            "provider": {
                "@type": "Dentist",
                "name": NAP_NAME,
                "telephone": PHONE_TEL,
                "address": {
                    "@type": "PostalAddress",
                    "streetAddress": NAP_STREET,
                    "addressLocality": "Edmonton",
                    "addressRegion": "AB",
                    "postalCode": "T6G 1B9",
                    "addressCountry": "CA",
                },
            },
        }
    )


def breadcrumb_schema(items: list[tuple[str, str]]) -> str:
    return json.dumps(
        {
            "@context": "https://schema.org",
            "@type": "BreadcrumbList",
            "itemListElement": [
                {
                    "@type": "ListItem",
                    "position": i,
                    "name": label,
                    "item": CANON + href,
                }
                for i, (href, label) in enumerate(items, 1)
            ],
        }
    )


def page(
    path: str,
    title: str,
    description: str,
    current: str,
    body: str,
    schemas: list[str],
    extra_head: str = "",
) -> None:
    canonical = CANON + (path if path.endswith("/") or path.endswith(".html") else path + "/")
    if path == "/":
        canonical = CANON + "/"
    schema_tags = "\n".join(
        f'<script type="application/ld+json">{s.strip()}</script>' for s in schemas
    )
    html = f"""<!DOCTYPE html>
<html lang="en-CA">
<head>
  <meta charset="utf-8">
  <base href="{GH_PAGES_BASE}" data-gh-pages-base>
  <script>
    (function () {{
      var base = document.querySelector("base[data-gh-pages-base]");
      if (!base) return;
      var host = location.hostname;
      var path = location.pathname || "/";
      if (host === "localhost" || host === "127.0.0.1") {{
        base.href = location.origin + "/";
        return;
      }}
      if (host.indexOf("github.io") !== -1 && path.indexOf("/109-dental-site/") === 0) {{
        base.href = location.origin + "/109-dental-site/";
        return;
      }}
      base.href = location.origin + "/";
    }})();
  </script>
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{esc(title)}</title>
  <meta name="description" content="{esc(description)}">
  <link rel="canonical" href="{canonical}">
  <meta property="og:title" content="{esc(title)}">
  <meta property="og:description" content="{esc(description)}">
  <meta property="og:type" content="website">
  <meta property="og:url" content="{canonical}">
  <meta property="og:locale" content="en_CA">
  <meta name="theme-color" content="#1a5c63">
  <link rel="icon" href="{u('/assets/favicon.svg')}" type="image/svg+xml">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,560;9..144,650&family=Source+Sans+3:wght@400;600;700&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="{u('/css/styles.css')}?v=20260922">
  {extra_head}
  {schema_tags}
</head>
<body>
  <a class="skip-link" href="#main">Skip to content</a>
  <div class="preview-banner">Preview for Sandra and StockWise. Feedback welcome before we switch 109dental.ca over.</div>
  <header class="site-header">
    <div class="topbar">
      <div class="container topbar-inner">
        <span>Queen Alexandra / Strathcona · near U of A</span>
        <a href="tel:{PHONE_TEL}">{PHONE_DISPLAY}</a>
      </div>
    </div>
    <div class="container header-inner">
      <a class="logo" href="{u('/')}"><img src="{u('/assets/logo.svg')}" width="190" height="42" alt="109 Dental, Strathcona Edmonton"></a>
      {nav_html(current)}
      <div class="header-cta">
        <a class="btn btn-secondary" href="tel:{PHONE_TEL}">Call {PHONE_DISPLAY}</a>
        <a class="btn btn-primary" href="{u('/contact/#book')}">Book</a>
        <button class="nav-toggle" type="button" data-nav-toggle aria-expanded="false" aria-controls="site-nav">Menu</button>
      </div>
    </div>
  </header>
  <main id="main">
    {body}
  </main>
  {footer_html()}
  {sticky_bar()}
  <script src="{u('/js/main.js')}" defer></script>
</body>
</html>
"""
    html = rebase_html(html)
    if path == "/":
        out = ROOT / "index.html"
    elif path.endswith(".html"):
        out = ROOT / path.lstrip("/")
    else:
        out = ROOT / path.strip("/") / "index.html"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(html, encoding="utf-8")
    print("wrote", out.relative_to(ROOT))


HOME_FAQS = [
    (
        "Do you accept the Canadian Dental Care Plan?",
        "Yes. 109 Dental accepts the Canadian Dental Care Plan. Bring your CDCP details to your visit and we will help you understand what is covered. Confirm any remaining balance with our team before treatment.",
    ),
    (
        "Are you accepting new patients?",
        "Yes. We welcome new patients of all ages, including students near the University of Alberta and families in Queen Alexandra and Strathcona.",
    ),
    (
        "Can I be seen for a dental emergency?",
        "Call (780) 435-5300 during office hours. We do our best to see emergency patients the same day when we can. If bleeding will not stop or you have facial swelling that affects breathing, go to a hospital emergency department.",
    ),
    (
        "Is there parking near the clinic?",
        "Yes. Patients have free parking at the building. The clinic is also reachable by Edmonton transit along 109 Street, close to Whyte Avenue and the University of Alberta.",
    ),
    (
        "What insurance plans do you accept?",
        "We accept most major dental insurance plans and can often direct bill. Call with your plan details if you want us to check coverage before your appointment.",
    ),
]


def home():
    body = f"""
    <section class="hero hero-brand">
      <div class="container hero-grid">
        <div>
          <p class="kicker">Queen Alexandra / Strathcona</p>
          <h1>Family dentistry near the University of Alberta</h1>
          <p class="lede">{ENTITY} We look after new patients, families, and same-day emergencies when we can.</p>
          <p>You may know us as Dr. Guy Girtel Family Dentistry. Drs. Steve Barkwell and Guy Girtel still provide general dental care in the same 109 Street office.</p>
          <div class="hero-actions">
            <a class="btn btn-primary" href="tel:{PHONE_TEL}">Call {PHONE_DISPLAY}</a>
            <a class="btn btn-secondary" href="/contact/#book">Book an appointment</a>
          </div>
          <div class="trust-row">
            <span class="chip">New patients welcome</span>
            <span class="chip">CDCP accepted</span>
            <span class="chip">Free parking</span>
            <span class="chip">Transit on 109 Street</span>
          </div>
        </div>
        {photo("clinic exterior on 109 Street near Whyte Avenue", "320px")}
      </div>
    </section>
    <section class="section section-alt">
      <div class="container">
        <h2>Care for everyday visits and urgent ones</h2>
        <div class="cards">
          <article class="card">
            <h3><a href="/new-patients/">New patients</a></h3>
            <p>Bring ID, insurance or CDCP information, and a medication list. We will walk you through the first visit.</p>
          </article>
          <article class="card">
            <h3><a href="/services/emergency-dentist/">Emergency dentist</a></h3>
            <p>Toothache, a broken tooth, or a knocked-out tooth. Call first and we will try to see you the same day.</p>
          </article>
          <article class="card">
            <h3><a href="/services/family-dentistry/">Family dentistry</a></h3>
            <p>Checkups, cleanings, and restorative care for kids, students, and adults in one neighbourhood clinic.</p>
          </article>
        </div>
      </div>
    </section>
    <section class="section">
      <div class="container two-col">
        <div>
          <h2>Services people book most</h2>
          <ul class="list">
            <li><a href="/services/wisdom-teeth/">Wisdom teeth assessment and removal</a></li>
            <li><a href="/services/dental-implants/">Dental implants</a></li>
            <li><a href="/services/cosmetic-dentistry/">Cosmetic dentistry</a></li>
            <li><a href="/services/orthodontics-invisalign/">Invisalign and orthodontics</a></li>
            <li><a href="/services/childrens-dentistry/">Children's dentistry</a></li>
            <li><a href="/services/">See all services</a></li>
          </ul>
        </div>
        {photo("treatment room at 109 Dental", "280px")}
      </div>
    </section>
    <section class="section section-teal">
      <div class="container two-col">
        <div>
          <h2>Need a dentist near campus or Whyte Ave?</h2>
          <p>We are in Suite 204 at 7125 109 St NW, a short trip from the University of Alberta and Whyte Avenue. Free parking is available at the building.</p>
          <div class="cta-row">
            <a class="btn btn-copper" href="tel:{PHONE_TEL}">Call {PHONE_DISPLAY}</a>
            <a class="btn btn-secondary" href="/contact/">Map, hours, and parking</a>
          </div>
        </div>
        <div>
          <iframe class="map-frame" title="Map of 109 Dental in Edmonton" src="{MAP_EMBED}" loading="lazy" referrerpolicy="no-referrer-when-downgrade"></iframe>
        </div>
      </div>
    </section>
    <section class="section">
      <div class="container two-col">
        <div>
          <h2>Common questions</h2>
          {faq_block(HOME_FAQS)}
        </div>
        {booking_form("new-patient", "Book a visit")}
      </div>
    </section>
    """
    page(
        "/",
        "Family Dentist in Strathcona Near U of A | 109 Dental",
        "Family and emergency dental care in Queen Alexandra / Strathcona, near the University of Alberta. New patients and CDCP welcome.",
        "/",
        body,
        [dentist_schema(), faq_schema(HOME_FAQS)],
    )


def about():
    body = f"""
    <section class="section">
      <div class="container">
        {crumbs([("/", "Home"), ("/about/", "About")])}
        <p class="kicker">Our team</p>
        <h1>Dentists in Queen Alexandra you can stay with</h1>
        <p class="lede">{ENTITY}</p>
        <p>109 Dental was formerly Dr. Guy Girtel Family Dentistry. Dr. Girtel still practises here with Dr. Steve Barkwell. The name changed. The neighbourhood practice did not.</p>
      </div>
    </section>
    <section class="section section-alt">
      <div class="container two-col">
        <article class="card team-card">
          {photo("Dr. Steve Barkwell")}
          <h2>Dr. Steve Barkwell</h2>
          <p>Dr. Barkwell was born in Edmonton and completed biochemistry and dentistry degrees at UBC. He has practised in Alberta for more than 11 years.</p>
          <p>He provides a wide range of general care, including implants, Invisalign, children's dentistry, wisdom teeth, and TMJ-related treatment. Bios should be confirmed with the clinic before launch.</p>
        </article>
        <article class="card team-card">
          {photo("Dr. Guy Girtel")}
          <h2>Dr. Guy Girtel</h2>
          <p>Dr. Girtel has served Edmonton patients for more than 25 years, with a focus on general and family dentistry. Patients often know him from the long-running practice on 109 Street.</p>
          <p>He is known for a calm, careful approach. Details beyond this public bio should be confirmed with Sandra.</p>
        </article>
      </div>
    </section>
    <section class="section">
      <div class="container two-col">
        <div>
          <h2>What to expect</h2>
          <p>We are a general dental clinic for families, students, and long-time patients. We accept new patients and the Canadian Dental Care Plan. Direct billing is available for many insurance plans.</p>
          <p>If you are returning after the name change, you are in the same building: Suite 204, 7125 109 St NW.</p>
          <div class="cta-row">
            <a class="btn btn-primary" href="tel:{PHONE_TEL}">Call {PHONE_DISPLAY}</a>
            <a class="btn btn-secondary" href="/new-patients/">New patient information</a>
          </div>
        </div>
        {photo("front desk and waiting area")}
      </div>
    </section>
    """
    page(
        "/about/",
        "Drs. Barkwell & Girtel | 109 Dental Queen Alexandra",
        "Meet Drs. Steve Barkwell and Guy Girtel at 109 Dental, formerly Dr. Guy Girtel Family Dentistry, in Queen Alexandra near U of A.",
        "/about/",
        body,
        [dentist_schema(), breadcrumb_schema([("/", "Home"), ("/about/", "About")])],
    )


CONTACT_FAQS = [
    (
        "Where is 109 Dental?",
        "Suite 204, 7125 109 St NW, Edmonton, AB T6G 1B9, in Queen Alexandra / Strathcona near the University of Alberta and Whyte Avenue.",
    ),
    (
        "What are your hours?",
        "Monday and Tuesday 8:30 AM to 4:30 PM. Wednesday and Thursday 7:30 AM to 3:30 PM. Friday 9:00 AM to 3:00 PM. Saturday and Sunday closed. Please confirm Friday hours when you book. Public listings have not always matched.",
    ),
    (
        "How do I book?",
        "Call (780) 435-5300 or send the short form on this page. We respond during business hours.",
    ),
]


def contact():
    body = f"""
    <section class="section">
      <div class="container">
        {crumbs([("/", "Home"), ("/contact/", "Contact")])}
        <p class="kicker">Edmonton clinic</p>
        <h1>Contact 109 Dental in Strathcona</h1>
        <p class="lede">{ENTITY} Call, email, or send a short appointment request. This map is Edmonton only.</p>
      </div>
    </section>
    <section class="section section-alt">
      <div class="container two-col">
        <div class="panel">
          <h2>Clinic details</h2>
          <address class="nap">
            <p><strong>{NAP_NAME}</strong></p>
            <p>{NAP_STREET}<br>{NAP_CITY}</p>
            <p>Phone: <a href="tel:{PHONE_TEL}">{PHONE_DISPLAY}</a></p>
            <p>Email: <a href="mailto:{EMAIL}">{EMAIL}</a></p>
          </address>
          <h3>Hours</h3>
          <div class="hours-grid">
            <div>Monday to Tuesday</div><div>8:30 AM to 4:30 PM</div>
            <div>Wednesday to Thursday</div><div>7:30 AM to 3:30 PM</div>
            <div>Friday</div><div>9:00 AM to 3:00 PM</div>
            <div>Saturday and Sunday</div><div>Closed</div>
          </div>
          <p class="form-note">Friday hours have appeared as 8:00 or 9:00 on different listings. Confirm with the office when you book.</p>
          <h3>Parking and transit</h3>
          <p>Free patient parking at the building. Transit runs along 109 Street. We are near Whyte Avenue and a short trip from the University of Alberta.</p>
          <div class="cta-row">
            <a class="btn btn-primary" href="tel:{PHONE_TEL}">Call {PHONE_DISPLAY}</a>
            <a class="btn btn-secondary" href="{MAP_LINK}">Open in Google Maps</a>
          </div>
        </div>
        <div id="book">
          {booking_form("other", "Request an appointment")}
        </div>
      </div>
    </section>
    <section class="section">
      <div class="container">
        <h2>Find us in Edmonton</h2>
        <iframe class="map-frame" title="Google Map of 109 Dental at 7125 109 Street NW, Edmonton" src="{MAP_EMBED}" loading="lazy" referrerpolicy="no-referrer-when-downgrade"></iframe>
      </div>
    </section>
    <section class="section">
      <div class="container narrow">
        <h2>Questions before you visit</h2>
        {faq_block(CONTACT_FAQS)}
      </div>
    </section>
    """
    page(
        "/contact/",
        "Contact 109 Dental | Strathcona / Queen Alexandra",
        "Call (780) 435-5300 or book at Suite 204, 7125 109 St NW, Edmonton. Map, hours, parking, and transit for our Strathcona clinic.",
        "/contact/",
        body,
        [dentist_schema(), faq_schema(CONTACT_FAQS), breadcrumb_schema([("/", "Home"), ("/contact/", "Contact")])],
    )


NP_FAQS = [
    (
        "What should I bring to my first appointment?",
        "Bring government photo ID, dental insurance or CDCP information, a list of medications, and any recent dental records if you have them.",
    ),
    (
        "Do you accept CDCP?",
        "Yes. We accept the Canadian Dental Care Plan. We will help you use your coverage and explain any portion that may not be covered.",
    ),
    (
        "Do you take new patients who live near campus?",
        "Yes. Many patients come from the University of Alberta, Garneau, Queen Alexandra, and Whyte Avenue. Free parking is available.",
    ),
]


def new_patients():
    body = f"""
    <section class="section">
      <div class="container hero-grid">
        <div>
          {crumbs([("/", "Home"), ("/new-patients/", "New patients")])}
          <p class="kicker">First visit</p>
          <h1>New patients in Strathcona and near U of A</h1>
          <p class="lede">{ENTITY} If you need a new family dentist, start with a phone call or the form on this page.</p>
          <div class="hero-actions">
            <a class="btn btn-primary" href="tel:{PHONE_TEL}">Call {PHONE_DISPLAY}</a>
            <a class="btn btn-secondary" href="#book">Request an appointment</a>
          </div>
        </div>
        {photo("new patient welcome at reception")}
      </div>
    </section>
    <section class="section section-alt">
      <div class="container two-col">
        <div>
          <h2>What to expect</h2>
          <p>Your first visit is usually a conversation, a review of your health history, and an exam. X-rays are taken when they are needed, not by default for every person.</p>
          <ul class="list">
            <li>Tell us about pain, sensitivity, or overdue care</li>
            <li>Share insurance or CDCP details so we can estimate coverage</li>
            <li>Ask about cleanings, wisdom teeth, or a second opinion</li>
          </ul>
          <h2>What to bring</h2>
          <ul class="list">
            <li>Photo ID</li>
            <li>Insurance card or CDCP information</li>
            <li>Medication list and medical history</li>
            <li>Previous dental records, if you have them</li>
          </ul>
        </div>
        <div>
          <h2>Insurance, CDCP, parking</h2>
          <p>We accept most major dental plans and the Canadian Dental Care Plan. We can often direct bill. Coverage still depends on your plan and the treatment recommended.</p>
          <p>Free parking is available at 7125 109 St NW. Transit along 109 Street is a straightforward option if you are coming from campus or Whyte Avenue.</p>
          <p><a href="/contact/">See hours and the Edmonton map</a> or <a href="/services/family-dentistry/">read about family dentistry</a>.</p>
        </div>
      </div>
    </section>
    <section class="section" id="book">
      <div class="container two-col">
        {booking_form("new-patient", "Book as a new patient")}
        <div>
          <h2>Questions new patients ask</h2>
          {faq_block(NP_FAQS)}
        </div>
      </div>
    </section>
    """
    page(
        "/new-patients/",
        "New Patients in Strathcona Near U of A | 109 Dental",
        "New patients are welcome at 109 Dental in Queen Alexandra. Learn what to bring, CDCP and insurance notes, parking, and how to book.",
        "/new-patients/",
        body,
        [faq_schema(NP_FAQS), breadcrumb_schema([("/", "Home"), ("/new-patients/", "New patients")])],
    )


def reviews():
    body = f"""
    <section class="section">
      <div class="container narrow">
        {crumbs([("/", "Home"), ("/reviews/", "Reviews")])}
        <p class="kicker">Social proof</p>
        <h1>Reviews for 109 Dental</h1>
        <p class="lede">We do not invent testimonials. When Sandra shares approved comments, they will appear here with a clear source. Until then, the honest path is Google and a conversation with the office.</p>
        <div class="panel">
          <h2>Read or leave a Google review</h2>
          <p>Search Google for 109 Dental at Suite 204, 7125 109 St NW, Edmonton. Use the clinic listing that shows this address, not an out-of-province result.</p>
          <div class="cta-row">
            <a class="btn btn-primary" href="{MAP_LINK}">Open our Edmonton Google listing</a>
            <a class="btn btn-secondary" href="tel:{PHONE_TEL}">Call {PHONE_DISPLAY}</a>
          </div>
        </div>
        <div class="notice" style="margin-top:1.2rem">
          Placeholder for approved patient comments. Do not publish names or quotes until the clinic confirms them.
        </div>
        <h2>What patients often mention</h2>
        <p>People usually want to know that we are the same 109 Street practice, that new patients can join, and that parking is straightforward. If you have a visit coming up, <a href="/new-patients/">see what to bring</a> or <a href="/contact/">book from the contact page</a>.</p>
      </div>
    </section>
    """
    page(
        "/reviews/",
        "Patient Reviews | 109 Dental Strathcona Edmonton",
        "Find 109 Dental reviews for our Queen Alexandra / Strathcona clinic. We link to Google and only publish quotes the office approves.",
        "/reviews/",
        body,
        [breadcrumb_schema([("/", "Home"), ("/reviews/", "Reviews")])],
    )


def services_hub():
    cards = "".join(
        f'<article class="card"><h3><a href="{href}">{label}</a></h3><p>Care at our 109 Street clinic in Queen Alexandra, near U of A and Whyte Avenue.</p></article>'
        for href, label in SERVICES
    )
    body = f"""
    <section class="section">
      <div class="container">
        {crumbs([("/", "Home"), ("/services/", "Services")])}
        <p class="kicker">Care menu</p>
        <h1>Dental services in Strathcona</h1>
        <p class="lede">{ENTITY} Choose the page that matches what you need. Each service has its own URL so you can go straight to the details.</p>
        <div class="cards">{cards}</div>
        <div class="cta-row">
          <a class="btn btn-primary" href="tel:{PHONE_TEL}">Call {PHONE_DISPLAY}</a>
          <a class="btn btn-secondary" href="/contact/#book">Book an appointment</a>
        </div>
      </div>
    </section>
    """
    page(
        "/services/",
        "Dental Services in Strathcona | 109 Dental Edmonton",
        "Family dentistry, emergency care, wisdom teeth, implants, Invisalign, and more at 109 Dental in Queen Alexandra near U of A.",
        "/services/",
        body,
        [breadcrumb_schema([("/", "Home"), ("/services/", "Services")])],
    )


def service_page(
    slug: str,
    title: str,
    description: str,
    h1: str,
    intro: str,
    more: str,
    reason: str,
    faqs: list[tuple[str, str]],
    related: list[tuple[str, str]],
    extra_head: str = "",
    extra_top: str = "",
    include_map: bool = False,
):
    url = f"/services/{slug}/"
    related_html = "".join(f'<li><a href="{href}">{label}</a></li>' for href, label in related)
    body = f"""
    <section class="section">
      <div class="container">
        {crumbs([("/", "Home"), ("/services/", "Services"), (url, h1)])}
        <p class="kicker">109 Street clinic</p>
        <h1>{h1}</h1>
        <p class="lede">{intro}</p>
        {extra_top}
        <div class="hero-actions">
          <a class="btn btn-primary" href="tel:{PHONE_TEL}">Call {PHONE_DISPLAY}</a>
          <a class="btn btn-secondary" href="#book">Book / request an appointment</a>
        </div>
      </div>
    </section>
    <section class="section section-alt">
      <div class="container two-col">
        <div>
          {more}
          <h2>Related care</h2>
          <ul class="list">{related_html}</ul>
        </div>
        {photo(f"{h1} at 109 Dental")}
      </div>
    </section>
    <section class="section" id="book">
      <div class="container two-col">
        {booking_form(reason, "Request this visit")}
        <div>
          <h2>Questions</h2>
          {faq_block(faqs)}
          <p style="margin-top:1rem"><a href="/contact/">Hours, parking, and Edmonton map</a></p>
        </div>
      </div>
    </section>
    {f'''
    <section class="section section-alt">
      <div class="container two-col">
        <div>
          <h2>Find 109 Dental in Edmonton</h2>
          <address class="nap">
            <p><strong>{NAP_NAME}</strong></p>
            <p>{NAP_STREET}<br>{NAP_CITY}</p>
            <p><a href="tel:{PHONE_TEL}">{PHONE_DISPLAY}</a></p>
          </address>
          <p>Free parking at the building. Transit along 109 Street, near Whyte Avenue and the University of Alberta.</p>
        </div>
        <iframe class="map-frame" title="Map of 109 Dental in Edmonton" src="{MAP_EMBED}" loading="lazy" referrerpolicy="no-referrer-when-downgrade"></iframe>
      </div>
    </section>
    ''' if include_map else ''}
    """
    schemas = [
        service_schema(h1, url, description),
        breadcrumb_schema([("/", "Home"), ("/services/", "Services"), (url, h1)]),
        faq_schema(faqs),
    ]
    page(url, title, description, url, body, schemas, extra_head=extra_head)


def wisdom():
    extra = """
    <!-- STOCKWISE: Meta Pixel placeholder. Replace PIXEL_ID before ads. Do not enable until StockWise installs the real pixel.
    <script>
    !function(f,b,e,v,n,t,s){if(f.fbq)return;n=f.fbq=function(){n.callMethod?
    n.callMethod.apply(n,arguments):n.queue.push(arguments)};if(!f._fbq)f._fbq=n;
    n.push=n;n.loaded=!0;n.version='2.0';n.queue=[];t=b.createElement(e);t.async=!0;
    t.src=v;s=b.getElementsByTagName(e)[0];s.parentNode.insertBefore(t,s)}(window, document,'script',
    'https://connect.facebook.net/en_US/fbevents.js');
    fbq('init', 'PIXEL_ID');
    fbq('track', 'PageView');
    </script>
    -->
    """
    faqs = [
        (
            "How do I know if my wisdom teeth need to come out?",
            "Pain, swelling, food traps, or an x-ray that shows crowding or impaction are common reasons to assess third molars. The dentists review your mouth and images with you before recommending removal.",
        ),
        (
            "Can students near U of A book a wisdom teeth visit?",
            "Yes. The clinic is on 109 Street in Queen Alexandra, a short trip from campus. Call (780) 435-5300 or use the form on this page.",
        ),
        (
            "Does CDCP or insurance cover wisdom teeth removal?",
            "Sometimes. Coverage depends on your plan and the procedure required. Bring CDCP or insurance details and we will help you estimate benefits.",
        ),
        (
            "Is wisdom teeth removal always surgical?",
            "No. Erupted teeth may be a simpler extraction. Impacted teeth can need a surgical approach. We explain that after we see you. We do not promise a specific method online.",
        ),
    ]
    more = """
    <h2>Who this page is for</h2>
    <p>Students and adults near the University of Alberta, Whyte Avenue, and Strathcona who have sore or erupting wisdom teeth, or who were told to have them checked.</p>
    <h2>What to expect</h2>
    <p>We look at the teeth, the gums around them, and current x-rays. Removal is recommended only when it is the better option for your mouth. Some wisdom teeth stay and are monitored.</p>
    <p>If removal is planned, the visit can range from a straightforward extraction with local anaesthetic to a more involved appointment for teeth still in the bone. Aftercare instructions cover swelling, eating, and when to call us. Healing varies. We will not promise a pain-free recovery.</p>
    <h2>Why people book here</h2>
    <ul class="list">
      <li>Neighbourhood clinic on 109 Street, not a downtown maze</li>
      <li>Family dentists who already treat many campus-area patients</li>
      <li>New patients welcome, including CDCP</li>
      <li>Free parking and a clear phone number: (780) 435-5300</li>
    </ul>
    """
    extra_top = f"""
    <p>Sore back molars, swelling, or a referral for third molars? Call {PHONE_DISPLAY}. We will tell you if you should come in now or book a planned assessment.</p>
    """
    service_page(
        "wisdom-teeth",
        "Wisdom Teeth Removal Near U of A | 109 Dental",
        "Wisdom teeth assessment and removal in Strathcona / near U of A. Call (780) 435-5300 or request a visit at 109 Dental.",
        "Wisdom Teeth Removal in Strathcona / Near U of A",
        "If a wisdom tooth is sore, swollen, or overdue for a look, 109 Dental can assess it at Suite 204, 7125 109 St NW. We explain options in plain language and book removal only when it makes sense.",
        more,
        "wisdom",
        faqs,
        [("/services/emergency-dentist/", "Emergency dentist"), ("/new-patients/", "New patients"), ("/contact/", "Contact and map")],
        extra_head=extra,
        extra_top=extra_top,
        include_map=True,
    )


def remaining_services():
    service_page(
        "family-dentistry",
        "Family Dentistry in Queen Alexandra | 109 Dental",
        "Family dentistry in Queen Alexandra / Strathcona near U of A. Checkups, cleanings, and restorative care for all ages.",
        "Family dentistry in Queen Alexandra",
        f"{ENTITY} This page is for households who want one clinic for checkups, fillings, and ongoing care.",
        """
        <h2>What family care includes</h2>
        <p>Exams, cleanings, fillings, and the everyday work that keeps kids and adults comfortable. When someone needs a crown, implant, or Invisalign, we discuss that on a dedicated visit.</p>
        <p>We accept new patients and the Canadian Dental Care Plan. Direct billing is available for many insurance plans.</p>
        """,
        "new-patient",
        [
            ("Can the whole family come here?", "Yes. We see children, students, and adults. Book each person a time that fits, or ask about same-day family blocks when the schedule allows."),
            ("Do you offer regular cleanings?", "Yes. Hygiene visits are a core part of family dentistry. Frequency depends on your gums and history."),
        ],
        [("/services/childrens-dentistry/", "Children's dentistry"), ("/new-patients/", "New patients")],
    )
    service_page(
        "emergency-dentist",
        "Emergency Dentist Strathcona / Near U of A | 109 Dental",
        "Emergency dentist in Strathcona near U of A. Call (780) 435-5300 for toothache, broken teeth, or injuries during office hours.",
        "Emergency dentist in Strathcona",
        "If you have sudden tooth pain, a broken tooth, or a dental injury near Whyte Avenue or campus, call 109 Dental first. We help you decide how soon you need to be seen.",
        """
        <h2>Call us during office hours</h2>
        <p>Phone (780) 435-5300. We try to see emergencies the same day when the schedule allows. We are not a 24-hour hospital. If bleeding will not stop, or swelling affects breathing or an eye, go to emergency care.</p>
        <h2>Until you arrive</h2>
        <ul class="list">
          <li>Toothache: rinse with warm water, floss gently, use a cold compress on the cheek. Do not put aspirin on the gum.</li>
          <li>Broken tooth: rinse, keep any fragments, and call us.</li>
          <li>Knocked-out tooth: hold it by the crown, rinse gently, keep it in milk or saliva, and come in as soon as you can.</li>
        </ul>
        <p>New patients with an emergency are welcome to call. <a href="/new-patients/">See first-visit notes</a> if you also need to join the practice.</p>
        """,
        "emergency",
        [
            ("Do you see emergency patients who are new to the clinic?", "Yes. Call and describe the problem. We will do our best to fit you in during open hours."),
            ("What if it is after hours?", "We are closed Saturday and Sunday. For severe bleeding, trouble breathing, or facial trauma, use a hospital emergency department."),
        ],
        [("/services/wisdom-teeth/", "Wisdom teeth"), ("/contact/", "Contact")],
        include_map=True,
    )
    service_page(
        "cosmetic-dentistry",
        "Cosmetic Dentistry in Strathcona | 109 Dental Edmonton",
        "Cosmetic dentistry in Strathcona near Whyte Avenue: whitening, veneers, and bonding discussed after a real exam.",
        "Cosmetic dentistry in Strathcona",
        "If you want a brighter or more even smile, start with an exam at our 109 Street clinic. Whitening, bonding, and veneers are options we discuss after we see your teeth.",
        """
        <h2>What we can talk through</h2>
        <p>Whitening, bonding, and veneers are the usual cosmetic requests. Some smiles need a crown or orthodontics first. We will say so instead of selling a treatment that will not last.</p>
        <p>Results vary. Photos on this site are placeholders until the clinic supplies real cases.</p>
        """,
        "other",
        [
            ("Can I book whitening as a new patient?", "Yes, but we still need a checkup first so we are not bleaching over decay or gum disease."),
            ("Do you offer veneers?", "Veneers can be discussed when they are a fit. They are not the first answer for every chip or colour concern."),
        ],
        [("/services/orthodontics-invisalign/", "Invisalign"), ("/services/crowns-bridges/", "Crowns and bridges")],
    )
    service_page(
        "dental-implants",
        "Dental Implants Near U of A | 109 Dental Strathcona",
        "Dental implants at 109 Dental in Strathcona near U of A. A consult first, then a plan if an implant is the right replacement.",
        "Dental implants near U of A",
        "Missing a tooth and want a fixed replacement? 109 Dental can assess whether an implant is a sound option for your bone and bite.",
        """
        <h2>How implants work in plain terms</h2>
        <p>An implant is a titanium post placed in the jaw, then a connector and a crown. It can replace one tooth or support more than one, if your health and bone allow it.</p>
        <p>Not every patient is a candidate on the first visit. We explain that after x-rays and a health review. Healing takes time. Online claims of instant perfect smiles are not how we work.</p>
        """,
        "other",
        [
            ("Do you place implants at this clinic?", "Dr. Barkwell provides implant care as part of general dentistry. A consult tells us whether you can be treated here or need a specialist."),
            ("Will insurance or CDCP help?", "Sometimes. Implant benefits vary widely. Bring your plan details to the consult."),
        ],
        [("/services/crowns-bridges/", "Crowns and bridges"), ("/services/family-dentistry/", "Family dentistry")],
    )
    service_page(
        "orthodontics-invisalign",
        "Invisalign in Strathcona Near U of A | 109 Dental",
        "Invisalign and orthodontic options in Strathcona near U of A. A consult first to see if clear aligners fit your bite.",
        "Invisalign and orthodontics in Strathcona",
        "Crooked teeth or a bite that bothers you? We can talk through Invisalign and other orthodontic options at our Queen Alexandra clinic.",
        """
        <h2>Clear aligners and when they fit</h2>
        <p>Invisalign-style aligners suit many mild to moderate cases. Some bites need a different plan. We will not start aligners until we have records and a clear goal.</p>
        <p>Adults and older teens near campus often ask about this. Wear time and retainers matter. Results depend on following the plan.</p>
        """,
        "other",
        [
            ("Can I get Invisalign as a student near U of A?", "Yes, if the case is a fit. Book a consult and bring any previous ortho records."),
            ("Do you also treat kids who may need braces?", "We watch growth and crowding in children and discuss timing. See our children's dentistry page for younger visits."),
        ],
        [("/services/childrens-dentistry/", "Children's dentistry"), ("/services/cosmetic-dentistry/", "Cosmetic dentistry")],
    )
    service_page(
        "childrens-dentistry",
        "Children's Dentistry in Strathcona | 109 Dental",
        "Children's dentist in Strathcona / Queen Alexandra near U of A. Calm first visits, checkups, and family follow-up care.",
        "Children's dentistry near Whyte Ave",
        "Looking for a kids' dentist close to Strathcona and the University of Alberta? 109 Dental sees children for checkups and everyday treatment.",
        """
        <h2>First visits</h2>
        <p>We keep first appointments simple: a look, a conversation with the parent or caregiver, and treatment only when it is needed. Tell us if your child is anxious.</p>
        <p>For injuries, call the emergency line on this site. Stay calm with your child and we will help you decide next steps.</p>
        """,
        "new-patient",
        [
            ("What age do you see children?", "We see children for routine care. If you are unsure whether your child is ready, call and ask."),
            ("Do you accept CDCP for kids?", "Yes, when the child is covered. Bring CDCP details to the visit."),
        ],
        [("/services/family-dentistry/", "Family dentistry"), ("/services/emergency-dentist/", "Emergency dentist")],
    )
    service_page(
        "root-canals",
        "Root Canal Treatment in Strathcona | 109 Dental",
        "Root canal treatment in Strathcona near U of A. We assess the tooth and explain whether a root canal or another option is next.",
        "Root canals in Queen Alexandra",
        "A toothache that lingers, or a tooth the dentist flagged, may need a root canal. We assess first and explain the plan before we start.",
        """
        <h2>What a root canal is for</h2>
        <p>The goal is to keep a tooth that would otherwise be lost to infection or deep decay. Some teeth need a crown afterward. Some need extraction instead. That decision is clinical, not a website promise.</p>
        """,
        "other",
        [
            ("Does a root canal always save the tooth?", "Not always. We tell you if the tooth is a poor candidate and talk about extraction or an implant if that is safer."),
            ("Can this wait if I am in pain?", "Call us. Waiting with an infection can make the visit harder. Use the emergency page if you need same-day advice."),
        ],
        [("/services/emergency-dentist/", "Emergency dentist"), ("/services/crowns-bridges/", "Crowns and bridges")],
    )
    service_page(
        "crowns-bridges",
        "Crowns and Bridges in Strathcona | 109 Dental",
        "Crowns and bridges in Strathcona / Queen Alexandra. Restore a broken or missing tooth after a clear exam and estimate.",
        "Crowns and bridges in Strathcona",
        "A cracked, heavily filled, or missing tooth may need a crown or a bridge. We explain the difference after we see the tooth and your bite.",
        """
        <h2>Crowns versus bridges</h2>
        <p>A crown covers one tooth. A bridge replaces a gap by using neighbouring teeth. Implants are another way to fill a space. We compare those options with cost and upkeep in mind.</p>
        """,
        "other",
        [
            ("How long does a crown take?", "Often more than one visit. Timing depends on the tooth and the lab work. We will outline that before you book treatment."),
            ("Is a bridge better than an implant?", "It depends on the bone, the neighbouring teeth, and your budget. That is a consult question, not a slogan."),
        ],
        [("/services/dental-implants/", "Dental implants"), ("/services/family-dentistry/", "Family dentistry")],
    )


def legal():
    page(
        "/privacy/",
        "Privacy Policy | 109 Dental Edmonton",
        "How 109 Dental handles appointment requests and contact details sent through this website.",
        "/privacy/",
        f"""
        <section class="section"><div class="container narrow">
        {crumbs([("/", "Home"), ("/privacy/", "Privacy")])}
        <h1>Privacy</h1>
        <p>Appointment forms go to {EMAIL} through FormSubmit. Use the form for scheduling, not for detailed health records.</p>
        <p>Do not send personal health numbers or full medical histories through the website. Bring those to the clinic or call {PHONE_DISPLAY}.</p>
        <p>This preview site may be hosted on a temporary domain before DNS points to 109dental.ca. Hosting and form processors keep their own logs.</p>
        </div></section>
        """,
        [breadcrumb_schema([("/", "Home"), ("/privacy/", "Privacy")])],
    )
    page(
        "/accessibility/",
        "Accessibility | 109 Dental Edmonton",
        "Accessibility notes for the 109 Dental website and Queen Alexandra clinic.",
        "/accessibility/",
        f"""
        <section class="section"><div class="container narrow">
        {crumbs([("/", "Home"), ("/accessibility/", "Accessibility")])}
        <h1>Accessibility</h1>
        <p>This website is built in plain HTML with keyboard-visible controls and a skip link. If a page is hard to use, email {EMAIL} and tell us the page URL.</p>
        <p>The clinic is at Suite 204, 7125 109 St NW. Ask us about building access and parking when you book so we can prepare for your visit.</p>
        </div></section>
        """,
        [breadcrumb_schema([("/", "Home"), ("/accessibility/", "Accessibility")])],
    )
    page(
        "/thank-you/",
        "Request Received | 109 Dental",
        "Your appointment request was sent to 109 Dental. We reply during business hours.",
        "/thank-you/",
        f"""
        <section class="section"><div class="container narrow">
        <h1>We received your request</h1>
        <p>The office reviews messages during open hours. If you are in pain, call <a href="tel:{PHONE_TEL}">{PHONE_DISPLAY}</a> instead of waiting on email.</p>
        <p><a href="/">Back to the homepage</a></p>
        </div></section>
        """,
        [],
    )
    page(
        "404.html",
        "Page Not Found | 109 Dental",
        "That page is not on the 109 Dental site. Use the menu or call the clinic.",
        "/",
        f"""
        <section class="section"><div class="container narrow">
        <h1>This page is not here</h1>
        <p>Try <a href="/">Home</a>, <a href="/services/">Services</a>, or <a href="/contact/">Contact</a>. Or call {PHONE_DISPLAY}.</p>
        </div></section>
        """,
        [],
    )


def write_support_files():
    urls = [
        "/",
        "/about/",
        "/contact/",
        "/new-patients/",
        "/reviews/",
        "/services/",
        "/privacy/",
        "/accessibility/",
        "/thank-you/",
    ] + [href for href, _ in SERVICES]
    urlset = "\n".join(
        f"  <url><loc>{CANON}{u}</loc><changefreq>monthly</changefreq></url>" for u in urls
    )
    (ROOT / "sitemap.xml").write_text(
        f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{urlset}\n</urlset>\n',
        encoding="utf-8",
    )
    (ROOT / "robots.txt").write_text(
        f"User-agent: *\nAllow: /\nSitemap: {CANON}/sitemap.xml\n",
        encoding="utf-8",
    )
    (ROOT / "llms.txt").write_text(
        f"""# 109 Dental

{ENTITY}

## Contact
- Name: 109 Dental
- Address: {NAP_STREET}, {NAP_CITY}
- Phone: {PHONE_DISPLAY}
- Email: {EMAIL}
- Website: {CANON}
- Area: Queen Alexandra, Strathcona, University of Alberta, Whyte Avenue, Edmonton, Alberta
- New patients: yes
- CDCP: accepted (confirm coverage at the visit)
- Parking: free patient parking at the building
- Hours: Mon-Tue 8:30-16:30; Wed-Thu 7:30-15:30; Fri 9:00-15:00; Sat-Sun closed (confirm Friday with the clinic)

## Services
Family dentistry, children's dentistry, emergency dentist, wisdom teeth removal, dental implants, cosmetic dentistry, orthodontics and Invisalign, root canals, crowns and bridges.

## Team
Dr. Steve Barkwell and Dr. Guy Girtel. Formerly Dr. Guy Girtel Family Dentistry.

## Booking
Call {PHONE_DISPLAY} or use the appointment form on {CANON}/contact/
""",
        encoding="utf-8",
    )
    (ROOT / ".htaccess").write_text(
        """RewriteEngine On
RewriteCond %{HTTPS} !=on
RewriteCond %{HTTP:X-Forwarded-Proto} !https
RewriteRule ^ https://%{HTTP_HOST}%{REQUEST_URI} [L,R=301]

ErrorDocument 404 /404.html

<IfModule mod_expires.c>
  ExpiresActive On
  ExpiresByType text/css "access plus 1 month"
  ExpiresByType application/javascript "access plus 1 month"
  ExpiresByType image/svg+xml "access plus 1 month"
  ExpiresByType image/png "access plus 1 month"
  ExpiresByType image/jpeg "access plus 1 month"
</IfModule>

<IfModule mod_headers.c>
  Header set X-Content-Type-Options "nosniff"
  Header set Referrer-Policy "strict-origin-when-cross-origin"
  Header set X-Frame-Options "SAMEORIGIN"
</IfModule>
""",
        encoding="utf-8",
    )
    print("wrote support files")


if __name__ == "__main__":
    home()
    about()
    contact()
    new_patients()
    reviews()
    services_hub()
    wisdom()
    remaining_services()
    legal()
    write_support_files()

"""Check generated links, booking anchors, schema, and review-build safeguards."""
import json
import argparse
import re
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit, unquote

ROOT = Path(__file__).resolve().parents[1]
SOURCE_ROOT = ROOT
parser = argparse.ArgumentParser()
parser.add_argument('--root', type=Path, default=ROOT)
parser.add_argument('--production', action='store_true')
args = parser.parse_args()
ROOT = args.root.resolve()
PUBLIC_EMAIL = "dental_appointment@shaw.ca"
BOOKING_EMAIL = "109dentaloffice@gmail.com"
FORM_ACTION = f"https://formsubmit.co/{BOOKING_EMAIL}"
OLD_FORM_ACTION = f"https://formsubmit.co/{PUBLIC_EMAIL}"
BOOKING_FIELDS = {
    "_subject": "109 Dental appointment request",
    "_template": "table",
    "_captcha": "false",
    "_next": "https://109dental.ca/thank-you/",
    "page": "",
    "utm_source": "",
    "utm_medium": "",
    "utm_campaign": "",
    "utm_content": "",
    "utm_term": "",
    "_honey": None,
    "name": None,
    "phone": None,
    "email": None,
    "preferred_time": None,
    "reason": None,
    "notes": None,
}


class Page(HTMLParser):
    def __init__(self, path):
        super().__init__(convert_charrefs=True)
        self.path = path
        self.ids = set()
        self.links = []
        self.schemas = []
        self.schema_text = None
        self.questions, self.answers = [], []
        self.question = None
        self.answer = None
        self.in_answer = False
        self.robots = None
        self.h1 = 0
        self.forms = []
        self._form = None
        self.feed(path.read_text(encoding="utf-8"))

    def handle_starttag(self, tag, attributes):
        a = dict(attributes)
        if a.get("id"):
            assert a["id"] not in self.ids, f"Duplicate id: {self.path}: {a['id']}"
            self.ids.add(a["id"])
        if tag == "h1": self.h1 += 1
        if tag == "meta" and a.get("name") == "robots": self.robots = a.get("content")
        if tag in ("a", "link", "img", "script"):
            url = a.get("href") or a.get("src")
            if url: self.links.append(url)
        if tag == "img": assert a.get("alt"), f"Missing image alt: {self.path}"
        if tag == "form":
            assert self._form is None, f"Nested form: {self.path}"
            self._form = {"action": a.get("action"), "method": (a.get("method") or "").upper(), "fields": {}, "submit": False}
        if self._form is not None and tag == "input" and a.get("name"):
            self._form["fields"][a["name"]] = a.get("value")
        if self._form is not None and tag in ("select", "textarea") and a.get("name"):
            self._form["fields"][a["name"]] = tag
        if self._form is not None and tag == "button":
            self._form["submit"] = a.get("type") == "submit"
        if tag == "script" and a.get("type") == "application/ld+json": self.schema_text = ""
        if tag == "summary": self.question = ""
        if tag == "div" and a.get("class") == "faq-panel": self.in_answer = True
        if tag == "p" and self.in_answer: self.answer = ""

    def handle_data(self, data):
        if self.schema_text is not None: self.schema_text += data
        if self.question is not None: self.question += data
        if self.answer is not None: self.answer += data

    def handle_endtag(self, tag):
        if tag == "form" and self._form is not None:
            self.forms.append(self._form)
            self._form = None
        if tag == "script" and self.schema_text is not None:
            self.schemas.append(json.loads(self.schema_text)); self.schema_text = None
        if tag == "summary" and self.question is not None:
            self.questions.append(self.question.strip()); self.question = None
        if tag == "p" and self.answer is not None:
            self.answers.append(self.answer.strip()); self.answer = None; self.in_answer = False


pages = {p.resolve(): Page(p) for p in ROOT.rglob("*.html") if ".git" not in p.parts}
manifest = json.loads((ROOT / 'build-manifest.json').read_text(encoding='utf-8'))
assert manifest['mode'] == ('production' if args.production else 'preview')
assert len(pages) == len(manifest['pages']) == 34, "Unexpected generated page count"
faq_count = 0
form_count = 0
dentist_email_count = 0
scanned_suffixes = {".html", ".py", ".md", ".js", ".mjs", ".txt", ".xml", ".json", ".css"}
for path in ROOT.rglob("*"):
    if not path.is_file() or ".git" in path.parts or path.suffix.lower() not in scanned_suffixes:
        continue
    assert OLD_FORM_ACTION not in path.read_text(encoding="utf-8"), f"Old Shaw form action: {path}"
for path, page in pages.items():
    assert page.h1 == 1, f"Expected one H1: {path}"
    utility = path.relative_to(ROOT).as_posix() in ('404.html', 'thank-you/index.html')
    expected_robots = 'noindex, follow' if utility or not args.production else None
    assert page.robots == expected_robots, f"Wrong indexing mode: {path}"
    html = path.read_text(encoding="utf-8")
    for unwanted in ("Photo placeholder:", "Bios should be confirmed", "Placeholder for approved", "—", "Vista Dental", "Redwater Dental", "Formerly Dr.", "Previously known as"):
        assert unwanted not in html, f"Unwanted public copy: {path}: {unwanted}"
    for url in page.links:
        parsed = urlsplit(url)
        if parsed.scheme or parsed.netloc:
            if parsed.scheme == "tel": assert url == "tel:+17804355300"
            continue
        assert not url.startswith("/"), f"Root-absolute URL breaks Pages: {path}: {url}"
        target = ROOT / unquote(parsed.path)
        if target.is_dir(): target /= "index.html"
        assert target.exists(), f"Missing target: {path}: {url}"
        if parsed.fragment:
            target_page = pages.get(target.resolve())
            assert target_page and parsed.fragment in target_page.ids, f"Broken fragment: {path}: {url}"
            if parsed.fragment in ("book", "main") and parsed.path not in ("contact/",):
                assert target.resolve() == path, f"Anchor leaves its page: {path}: {url}"
    for schema in page.schemas:
        assert schema.get("@type") != "DentalClinic"
        if schema.get("@type") == "FAQPage":
            qa = schema["mainEntity"]
            assert [q["name"] for q in qa] == page.questions, f"FAQ questions differ: {path}"
            assert [q["acceptedAnswer"]["text"] for q in qa] == page.answers, f"FAQ answers differ: {path}"
            faq_count += len(qa)
        if schema.get("@type") == "Dentist" and "email" in schema:
            assert schema["email"] == PUBLIC_EMAIL, f"JSON-LD contact email changed: {path}"
            hours = schema.get("openingHoursSpecification", [])
            days = []
            for spec in hours:
                day = spec["dayOfWeek"]
                days.extend(day if isinstance(day, list) else [day])
            assert "Friday" not in days, f"Friday was added to schema: {path}"
            assert {"Monday", "Tuesday", "Wednesday", "Thursday"} <= set(days), f"Weekday hours missing: {path}"
            dentist_email_count += 1
    assert len(page.forms) <= 1, f"Unexpected extra form: {path}"
    if page.forms:
        form_count += 1
        form = page.forms[0]
        assert form["action"] == FORM_ACTION, f"Booking action: {path}"
        assert form["method"] == "POST", f"Booking method: {path}"
        assert form["submit"], f"Missing submit button: {path}"
        assert form["fields"].keys() == BOOKING_FIELDS.keys(), f"Booking fields changed: {path}"
        for name, value in BOOKING_FIELDS.items():
            if value is not None:
                assert form["fields"][name] == value, f"Booking field {name}: {path}"
        for extra in ("_cc", "_autoresponse", "_webhook", "_replyto"):
            assert extra not in form["fields"], f"Unexpected mail field {extra}: {path}"
    html_lower = html.lower()
    assert f"mailto:{BOOKING_EMAIL}" not in html_lower, f"Public mailto switched to booking inbox: {path}"

contact_html = (ROOT / "contact/index.html").read_text(encoding="utf-8")
assert '<div>Friday</div><div>9:00 AM to 3:00 PM</div>' in contact_html
assert "Friday 9:00 AM to 3:00 PM" in contact_html
assert f"mailto:{PUBLIC_EMAIL}" in contact_html
assert f'<p>Email: <a href="mailto:{PUBLIC_EMAIL}">{PUBLIC_EMAIL}</a></p>' in contact_html
privacy_html = (ROOT / "privacy/index.html").read_text(encoding="utf-8")
assert f"Appointment forms go to {BOOKING_EMAIL} through FormSubmit." in privacy_html
home_html = (ROOT / "index.html").read_text(encoding="utf-8")
assert "Yes. 109 Dental accepts the Canadian Dental Care Plan." in home_html
new_patients_html = (ROOT / "new-patients/index.html").read_text(encoding="utf-8")
assert "Yes. We accept the Canadian Dental Care Plan." in new_patients_html
assert "We accept most major dental plans and the Canadian Dental Care Plan." in new_patients_html
assert "CDCP: accepted (confirm coverage at the visit)" in (ROOT / "llms.txt").read_text(encoding="utf-8")
assert form_count == 12, f"Unexpected booking form count: {form_count}"
assert dentist_email_count == 3, f"Expected JSON-LD email on home, about, and contact: {dentist_email_count}"

assert "/thank-you/" not in (ROOT / "sitemap.xml").read_text()
assert "https://109dental.ca/404.html" in (ROOT / "404.html").read_text()
assert "CDCP does not cover dental implants" in (ROOT / "services/dental-implants/index.html").read_text()
titles = [re.search(r'<title>(.*?)</title>', p.read_text(encoding='utf-8')).group(1) for p in pages]
assert len(titles) == len(set(titles)), 'Duplicate titles'
migration = json.loads((SOURCE_ROOT / 'tools/migration.json').read_text(encoding='utf-8'))
assert len(migration) == 42
config = (ROOT / '.htaccess').read_text(encoding='utf-8')
for row in migration:
    target = ROOT / row['to'].strip('/') / 'index.html'
    assert target.exists(), f"Missing migration destination: {row}"
    if row['from'] != row['to']:
        assert row['to'] not in [r['from'] for r in migration if r['from'] != r['to']], f'Redirect chain: {row}'
        rule = f"RewriteRule ^{re.escape(row['from'].strip('/'))}/?$ {row['to']} [R=301,L,NE]"
        assert rule in config, f'Missing redirect: {row}'
        assert row['from'] not in manifest['pages'], f'Redirect shadows content: {row}'
from xml.etree import ElementTree as ET
sitemap = ET.parse(ROOT / 'sitemap.xml')
urls = [node.text for node in sitemap.findall('.//{*}loc')]
assert len(urls) == len(set(urls)) == 32
assert set(urls) == {'https://109dental.ca' + p for p in manifest['pages'] if p not in ('/404.html', '/thank-you/')}
print('PASS: 42 legacy URLs accounted for; 23 exact redirects; unique titles; sitemap; build-mode checks.')
print(f"PASS: {len(pages)} pages; {form_count} booking forms to {BOOKING_EMAIL}; public email {PUBLIC_EMAIL}; Friday 9:00 AM to 3:00 PM; {faq_count} matching FAQs; no Shaw form action.")

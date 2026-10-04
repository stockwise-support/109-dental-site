"""Check generated links, booking anchors, schema, and review-build safeguards."""
import json
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit, unquote

ROOT = Path(__file__).resolve().parents[1]


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
            assert a.get("action") == "https://formsubmit.co/dental_appointment@shaw.ca"
        if tag == "script" and a.get("type") == "application/ld+json": self.schema_text = ""
        if tag == "summary": self.question = ""
        if tag == "div" and a.get("class") == "faq-panel": self.in_answer = True
        if tag == "p" and self.in_answer: self.answer = ""

    def handle_data(self, data):
        if self.schema_text is not None: self.schema_text += data
        if self.question is not None: self.question += data
        if self.answer is not None: self.answer += data

    def handle_endtag(self, tag):
        if tag == "script" and self.schema_text is not None:
            self.schemas.append(json.loads(self.schema_text)); self.schema_text = None
        if tag == "summary" and self.question is not None:
            self.questions.append(self.question.strip()); self.question = None
        if tag == "p" and self.answer is not None:
            self.answers.append(self.answer.strip()); self.answer = None; self.in_answer = False


pages = {p.resolve(): Page(p) for p in ROOT.rglob("*.html") if ".git" not in p.parts}
assert len(pages) == 19, "Unexpected generated page count"
faq_count = 0
for path, page in pages.items():
    assert page.h1 == 1, f"Expected one H1: {path}"
    assert page.robots == "noindex, follow", f"Review page is indexable: {path}"
    html = path.read_text(encoding="utf-8")
    for unwanted in ("Photo placeholder:", "Bios should be confirmed", "Placeholder for approved", "—", "Vista Dental", "Redwater Dental"):
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

assert "/thank-you/" not in (ROOT / "sitemap.xml").read_text()
assert "https://109dental.ca/404.html" in (ROOT / "404.html").read_text()
assert "CDCP does not cover dental implants" in (ROOT / "services/dental-implants/index.html").read_text()
print(f"PASS: {len(pages)} pages; all internal targets and fragments; {faq_count} matching FAQs; NAP, review noindex, metadata and copy checks.")

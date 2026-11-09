# 109 Dental website

Plain HTML, CSS and JavaScript for 109 Dental in Edmonton. The Python generator is the source of truth for shared templates and page copy. This branch is a review build for Sandra, not an approved production launch.

## Build and check

```sh
python tools/generate.py
python tools/check_site.py
node tools/check_base_paths.mjs
node --check js/main.js
python -m http.server 8099
```

The default build includes a small preview banner and `noindex, follow` on every page. Generated HTML is committed with the generator. Do not edit generated pages alone.

Only after an approved launch:

```sh
python tools/generate.py --production
```

Production mode removes the preview banner and general noindex rule. Thank-you and 404 pages remain noindex. The review validator intentionally expects a review build. A deployment must use the correct build mode and verify effective HTTP headers/robots on the actual hostname.

## Design and interactions

- Warm off-white, deep teal, serif headings, and real clinic photography.
- Responsive navigation, fixed mobile Call / Request a visit buttons, and a scrollable mobile menu with Escape/outside-click dismissal.
- Native details/summary FAQs remain usable without JavaScript.
- Page-qualified booking and skip anchors work with the shared base tag.
- Campaign parameters stay in same-site navigation. No new cookies, storage, analytics or Meta IDs were added.
- Appointment forms POST to FormSubmit at 109dentaloffice@gmail.com. The public contact address remains dental_appointment@shaw.ca. No real test request has been sent.

## Base paths and review links

Assets and navigation are base-relative. Keep GitHub's `/109-dental-site/` prefix and the root-domain behavior intact.

The inline base script supports the original and review GitHub Pages projects, Hostinger, the production domain and localhost.

Local review: http://127.0.0.1:8099/ after starting the server above.

A separate 109-dental-review GitHub Pages project is supported by the base-path code but has not been created or published. Public review publication needs AJ's approval. The source of truth remains stockwise-support/109-dental-site.

Preview locations:

- https://stockwise-support.github.io/109-dental-site/
- https://palevioletred-ant-543523.hostingersite.com/

GitHub Pages builds main and still shows the older build. Hostinger auto-deploys cursor/fix-gh-pages-css-3e09, verified during review updates. Do not force-push or change DNS to publish a review.

## Clinic facts awaiting confirmation

- Friday hours. The existing site's 9 AM to 3 PM hours remain visible with a call-to-confirm note; Friday is omitted from schema until confirmed.
- Direct billing and new-patient availability. Existing pages already say CDCP is accepted; that copy was left unchanged.
- Steve/Steven Barkwell spelling, both dentists' bios, offered services and emergency arrangements.
- Parking/building-access instructions and official social accounts.
- FormSubmit activation for 109dentaloffice@gmail.com. The inbox must open FormSubmit's one-time confirmation before requests are delivered. Do not send a test submission to trigger that email. Staff response ownership is still open.
- Any patient quote needs the appropriate approval and consent. The review page only links to the clinic's Google listing.

The implant FAQ distinguishes CDCP exclusions from private coverage, based on Health Canada's CDCP Dental Benefits Guide: https://www.canada.ca/en/services/benefits/dental/dental-care-plan/guide.html

## Launch hold

The November 8 migration map accounts for all 42 current production sitemap URLs: 19 retained paths and 23 exact permanent redirects. See tools/migration.json and docs/LAUNCH.md. Clinical sign-off, booking inbox delivery, account-level checks, and approved production deployment remain launch gates.

Verify production robots.txt directly. The Hostinger temporary hostname served a Googlebot block that differed from the repository file during the audit. Preview noindex must not accidentally remain on production, and robots must allow crawlers to read noindex on review hosts.

AJ must approve a merge and DNS cutover separately. No email or message to the clinic is sent automatically.

## Identity and assets

109 Dental, Suite 204, 7125 109 St NW, Edmonton, AB T6G 1B9.
Phone: (780) 435-5300. Public email: dental_appointment@shaw.ca. Booking form delivery: 109dentaloffice@gmail.com.

Use the existing clinic images in assets/photos and original logo in assets/brand-logo.png. See assets/photos/SOURCES.txt. Do not mix Vista or Redwater content, tracking or assets into this repository. Do not invent clinic facts, medical claims or awards. Keep copy direct, with no em dashes.

## Launch preparation

See [launch handoff](docs/LAUNCH.md) for production packaging, validation, migration decisions, and remaining checks. `tools/launch_content.py` holds the supplemental patient copy and primary references. `tools/prepare_release.py` builds and validates an isolated production ZIP without changing the review files.

November 8 hosting verification is blocked: the temporary hostname returns connection errors and a parked-domain HTML response at its stylesheet URL. Code is pushed, but the latest preview deployment has not been verified. Check the Hostinger website/domain assignment and Git connection before cutover.

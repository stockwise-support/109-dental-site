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
- Forms continue to POST to FormSubmit at dental_appointment@shaw.ca. No real test request has been sent as part of the refresh.

## Base paths and review links

Assets and navigation are base-relative. Keep GitHub's `/109-dental-site/` prefix and the root-domain behavior intact.

The inline base script supports GitHub Pages, Hostinger, the production domain and localhost. It also supports public, commit-pinned raw.githack.com / rawcdn.githack.com previews. Those previews use explicit index.html links because file servers do not resolve directory indexes. This is implemented in js/main.js and does not affect normal hosts.

A commit preview has this shape:

`https://raw.githack.com/stockwise-support/109-dental-site/COMMIT_SHA/index.html`

These are third-party review links, not production hosting. Verify nested navigation and assets before sharing. Do not share a branch URL expecting cache invalidation; use a commit SHA.

Existing previews (unchanged until a separately approved deployment):

- https://stockwise-support.github.io/109-dental-site/
- https://palevioletred-ant-543523.hostingersite.com/

GitHub Pages is configured to build main. Hostinger historically used cursor/fix-gh-pages-css-3e09. Confirm the actual connection and prefer main. Do not force-push or change DNS to publish a review.

## Clinic facts awaiting confirmation

- Friday hours. The existing site's 9 AM to 3 PM hours remain visible with a call-to-confirm note; Friday is omitted from schema until confirmed.
- Current CDCP participation, direct billing, and new-patient availability.
- Steve/Steven Barkwell spelling, both dentists' bios, offered services and emergency arrangements.
- Parking/building-access instructions and official social accounts.
- Appointment mailbox activation, delivery and staff response ownership.
- Any patient quote needs the appropriate approval and consent. The review page only links to the clinic's Google listing.

The implant FAQ distinguishes CDCP exclusions from private coverage, based on Health Canada's CDCP Dental Benefits Guide: https://www.canada.ca/en/services/benefits/dental/dental-care-plan/guide.html

## Launch hold

The September 30 audit found 37 old-site URLs missing from the rebuild. URL mapping/content preservation is separate launch work. Do not cut over until that migration is resolved. Search Console baseline data and clinic approvals are also outstanding.

Verify production robots.txt directly. The Hostinger temporary hostname served a Googlebot block that differed from the repository file during the audit. Preview noindex must not accidentally remain on production, and robots must allow crawlers to read noindex on review hosts.

AJ must approve a merge and DNS cutover separately. No email or message to the clinic is sent automatically.

## Identity and assets

109 Dental, Suite 204, 7125 109 St NW, Edmonton, AB T6G 1B9.
Phone: (780) 435-5300. Email: dental_appointment@shaw.ca.

Use the existing clinic images in assets/photos and original logo in assets/brand-logo.png. See assets/photos/SOURCES.txt. Do not mix Vista or Redwater content, tracking or assets into this repository. Do not invent clinic facts, medical claims or awards. Keep copy direct, with no em dashes.

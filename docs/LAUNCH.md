# 109 Dental launch handoff

Updated November 10, 2026. Main domain and DNS have not been changed.

## Current preview status

Verified November 12: the working preview is https://blueviolet-rhinoceros-423405.hostingersite.com/. The earlier palevioletred-ant hostname is obsolete for this site. Hostinger is connected to cursor/booking-form-gmail-2808; the previously assumed fix-gh-pages branch was not the connected branch. DNS remains unchanged.

Correct preview: https://blueviolet-rhinoceros-423405.hostingersite.com/. The new PHP form is ready there. One synthetic enquiry was submitted through the contact page and the server returned: “Your enquiry has been accepted for email delivery to our team. Sending this form does not confirm an appointment. Our team will follow up with you.” This verifies native PHP mail acceptance, not Gmail receipt. No second delivery test was sent. Mobile layouts were inspected at 390px and checked at 320px with no horizontal overflow. Form fields use 16px text and at least 48px heights. Server security and validation tests passed without sending mail.

## Ready in this branch

- 44 pages, with the existing clinic photos and logo.
- Dedicated CDCP/insurance page, four updated patient guides at their existing URLs, and nine additional dental-topic pages preserving old search intent.
- More practical content on the priority service pages and links between guides, services, insurance, and booking.
- Dentist identity data connected to the clinic. Unverified Facebook and Instagram URLs removed from schema.
- All 42 URLs from the production page/post sitemaps checked November 8 are accounted for: 29 retained, 13 exact permanent redirects. Mapping: `tools/migration.json`.
- Booking destination incorporates the November 5 branch: 109dentaloffice@gmail.com. Public contact email stays dental_appointment@shaw.ca.
- Separate, tested production packaging; default generated pages remain a noindex review build.

## Build and release

Do not point production at the committed preview build without generating production HTML.

```sh
python tools/generate.py
python tools/check_site.py
node tools/check_base_paths.mjs
node --check js/main.js
python tools/prepare_release.py ../109-Dental-production-ready.zip
```

The packaging command creates a fresh isolated build, validates production indexing and the same page/form/link checks, and creates a ZIP plus SHA-256 file. It does not deploy, merge main, or change DNS. It refuses to overwrite an existing archive. ZIP contents belong directly in the web root, including `.htaccess`.

For an approved Git-based launch, generate with `python tools/generate.py --production`, validate with `python tools/check_site.py --production`, then commit/deploy those generated files through the approved branch. Hostinger currently deploys `cursor/fix-gh-pages-css-3e09`; main still has the older build. Do not switch branches without accounting for this.

## Launch gates

1. AJ approves the production release and domain cutover. Back up the current live website and record the current DNS/hosting settings first; keep the old site available for rollback. Do not overwrite email-related DNS records.
2. Clinic verifies FormSubmit activation for 109dentaloffice@gmail.com and confirms delivery/response ownership. No test message was sent. Use an explicitly approved test with staff watching the inbox; a correct HTML action is not proof of delivery.
3. Clinic confirms current hours (especially Friday), new-patient availability, direct billing, CDCP participation, clinician names/bios, and service arrangements. Existing claims remain where they were already published; unknown treatment availability is not presented as confirmed.
4. Clinical review: approve the informational additions before public launch. No dentist has been falsely credited as author or reviewer. Named techniques on legacy pages are discussed as questions to raise, not promises that those procedures are provided.
5. Deploy production files on the approved domain. Confirm HTTPS for apex and www, robots.txt, response headers, canonical host, redirects, and mobile booking navigation. The temporary Hostinger hostname currently overrides robots.txt with a Googlebot block; recheck the actual production hostname rather than trusting the repo file.

After deployment:

```sh
node tools/check_deployment.mjs https://109dental.ca --production
```

This checks pages, indexing markers, canonical URLs, booking destination, all 13 redirects (including preserved campaign parameters), images/assets, robots, and a true 404. It never submits forms. Also check the site visually on a phone and desktop, verify real inbox delivery with permission, and inspect the main URLs in Search Console and Bing Webmaster Tools. Submit https://109dental.ca/sitemap.xml through the authorized accounts.

## Content and migration notes

The old pages were not copied verbatim. Several carried broad treatment claims, promises, or branded techniques needing confirmation. Relevant URLs now retain concise educational content or redirect to a closely related page that covers the subject. Clinical depth can be expanded with verified practice details. URL coverage is not a guarantee that existing search rankings will be preserved.

Sources are linked on the patient pages: Health Canada for CDCP, ADA/MouthHealthy for common dental topics, NIDCR for gum disease and TMD, NHS for tongue-tie, and NHLBI for sleep apnea. Do not label these pages medically reviewed until an actual clinician reviews them. Keep the former clinic name out of patient-facing copy.

## Off-site and measurement work

`docs/ai-visibility-prompts.csv` is a repeatable question set, not a measured ranking report. For each run, record date, assistant/model, web-search mode, Edmonton location context, prompt, named practices, source URLs, and any wrong facts. Repeat prompts in fresh sessions. Keep recommendation rate and site-citation rate separate. Compare monthly using the same question set; do not interpret a single response as a stable rank.

Track calls and appointment requests alongside visibility. No analytics account IDs, pixels, cookies, or call-tracking numbers were invented. Account access is needed for Search Console, Bing Webmaster Tools, analytics, Google Business Profile, Apple Maps, and listing changes. No listings were edited and no reviews, outreach, or emails were sent.

For a listing audit, use: 109 Dental; Suite 204, 7125 109 St NW, Edmonton AB T6G 1B9; (780) 435-5300; https://109dental.ca/. Verify operating hours and the public email with the clinic before bulk updates. Prioritize actual conflicts and duplicates over buying a large directory package.

## November 10 audit implementation

Ten distinct service URLs now have their own patient guides: checkups, cleaning, fillings/bonding, crowns, bridges, whitening, veneers, braces, gum contouring and infant feeding/tongue-tie assessment. The migration map has six content consolidations and seven URL renames; no page is pruned without a destination. All service guides are linked from Services, with contextual links from related overview pages.

Location wording identifies Queen Alexandra and describes Strathcona as nearby. Appointment requests explicitly require office confirmation. Form attribution fields and URL query forwarding were removed. Escape and outside-click now restore scrolling after closing the mobile menu. Existing photos are unchanged. Patient explanations include preparation, alternatives, estimates, insurance limitations and aftercare without invented prices or guarantees.

Verification: run `python tools/check_site.py`, `node tools/check_base_paths.mjs`, `node tools/check_interactions.mjs` and the isolated production release check. Local browser navigation to port 8110 timed out on November 10, so visual desktop/mobile review remains unverified.

### Clinic and account follow-up

- Confirm Friday hours before updating visible hours, schema or external listings; existing sources disagree.
- Confirm clinician names, roles, current service availability, referral arrangements and clinical copy. Do not claim a clinician has reviewed these additions yet.
- Confirm the booking inbox and FormSubmit activation with an approved delivery test; no form has been submitted as part of this update.
- Resolve Hostinger's parked-domain/connection problem and verify the actual deployed pages, redirects, assets and crawl settings before launch.
- Reconcile Google Business Profile, Bing Places, Apple Business Connect and verified directory entries against clinic-confirmed details. Do not manufacture reviews, memberships or social accounts.
- Once live, submit the production sitemap through the clinic's Search Console and Bing accounts and establish a baseline from real data. No ranking or AI-recommendation improvement is claimed without measurement.

## November 12 enquiry form

All 12 contact/appointment forms use api/enquiry.php instead of FormSubmit. The fixed recipient is 109dentaloffice@gmail.com, the sender is website@109dental.ca, and a validated visitor email is Reply-To. Hostinger native PHP mail is used; no credentials are needed or committed. PHP 8.1+ and mbstring are required. Session cookies require HTTPS. Only the production domain and the currently assigned blueviolet-rhinoceros preview host are allowed.

The server validates all fields, rejects control characters in header inputs, checks a session-bound CSRF token and same-origin header, uses a honeypot, and limits accepted attempts to five per IP/hour, five globally/minute and 80/day. A locked, private file outside public_html stores keyed hashes, timestamps and outcomes, not enquiry content. Failed/uncertain attempts cannot silently resend. Identical content is suppressed for one hour; request IDs for 24 hours. Expired records are removed on the next processed enquiry. Client requests do not contain query parameters or enquiry analytics. No application request-content logging is used.

Operational follow-up: confirm clinic ownership of the website@109dental.ca sender identity and the appropriate SPF/DKIM/DMARC configuration with the existing mail administrator; do not change DNS without approval. Native mail acceptance does not establish Gmail receipt or authentication success. Hostinger hosting/email processing terms, the clinic's Google mailbox arrangements, access controls, retention and applicable privacy agreements still require clinic review. This implementation does not assert HIPAA compliance or suitability for clinical records.

The current assigned preview is https://blueviolet-rhinoceros-423405.hostingersite.com/. The old palevioletred-ant address is obsolete for this deployment. The existing connected branch is cursor/booking-form-gmail-2808; update it by fast-forward, not main. The November 11 FormSubmit test was submitted once and accepted; no confirmation of inbox receipt was obtained. A new single synthetic test is authorized for this replacement PHP form.

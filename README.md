# 109 Dental website

Static HTML/CSS/JS preview site for **109 Dental** (Edmonton), built for StockWise Marketing so Sandra can review before Hostinger DNS cutover to [109dental.ca](https://109dental.ca).

Stack matches the StockWise Hostinger pattern: crawlable pages, FormSubmit booking, `sitemap.xml`, `robots.txt`, `llms.txt`, and `.htaccess`. No Next.js, React, or page builder.

## How to preview locally

From the repo root:

```bash
python3 -m http.server 8080
```

Open [http://localhost:8080](http://localhost:8080). The repo also previews on GitHub Pages: [https://stockwise-support.github.io/109-dental-site/](https://stockwise-support.github.io/109-dental-site/).

Asset and nav URLs are **base-relative** (`css/styles.css`, `contact/`), not path-absolute (`/css/styles.css`). Path-absolute URLs ignore `<base>` and 404 on GitHub Pages because the site lives under `/109-dental-site/`.

Optional: `python3 tools/generate.py` rebuilds every HTML page, sitemap, robots, llms.txt, and `.htaccess` from the shared template. Edit `tools/generate.py` if you need a sitewide NAP or nav change, then regenerate. Small copy tweaks can be made directly in the HTML.

## How Sandra can give feedback

1. Share the Hostinger temp URL (or this repo preview) with Sandra.
2. The tan **Preview for Sandra and StockWise** bar stays up until launch. Ask her to ignore it as design.
3. Collect notes by page: Home, About, New Patients, Contact, Reviews, Wisdom Teeth, Emergency, other services.
4. Highest-value confirms are listed under [Unverified facts](#unverified-facts-flag-for-sandra).
5. Send approved team photos, waiting-room photos, and any patient quotes she wants published. Placeholders are labeled on purpose.
6. Reviews page does **not** invent testimonials. Paste only quotes Sandra approves, or keep the Google listing link.

## Unverified facts (flag for Sandra)

Use these on the site for now, but confirm before launch:

| Item | What we used | Why it needs a check |
| --- | --- | --- |
| Hours | Mon–Tue 8:30–4:30; Wed–Thu 7:30–3:30; Fri 9:00–3:00; Sat–Sun closed | Listings disagree on Friday (8:00 vs 9:00). Contact copy already says confirm Friday. |
| CDCP | Accepted | Stated on the current 109dental.ca site. Confirm still true and how to bill. |
| Bios | Dr. Steve Barkwell and Dr. Guy Girtel, paraphrased from the current About page | Brief says Steven; the live site says Steve. Confirm spelling, years, and services. |
| Direct billing / most major insurance | Stated as available | From current site language. Confirm which plans. |
| Free parking / transit | Stated as true | From current site. Confirm lot instructions if any. |
| Instagram | `instagram.com/109Dental` (linked from current site) | Confirm the profile is still official before leaning on it in ads. |
| Reviews | No quotes published | Need approved comments or a preferred Google review URL. |

ADA directory showed a different phone at one point. Sitewide NAP uses **(780) 435-5300** only.

## Pages

- `/` Home
- `/about/`
- `/new-patients/`
- `/reviews/` (in main nav)
- `/contact/` with Edmonton-only map
- `/services/` plus family, children, emergency, wisdom teeth, implants, cosmetic, Invisalign, root canals, crowns and bridges
- `/privacy/`, `/accessibility/`, `/thank-you/`, `404.html`

Wisdom teeth (`/services/wisdom-teeth/`) is the Meta lander: problem, solution, call/book, who it is for, what to expect, FAQ, NAP, Edmonton map, UTM fields on the form, Meta pixel placeholder comment.

## NAP (keep identical)

109 Dental  
Suite 204, 7125 109 St NW, Edmonton, AB T6G 1B9  
(780) 435-5300  
https://109dental.ca  
Email: dental_appointment@shaw.ca (no trailing space in mailto)

Map embed and schema geo use the Edmonton listing at 53.508273, -113.5113761. Do not replace this with a generic “109 Dental” search that can resolve out of province.

## Hostinger temp subdomain

1. In Hostinger File Manager or FTP, upload the repo contents to `public_html` (or the subdomain folder). Keep folder structure: `index.html`, `css/`, `js/`, `assets/`, `about/`, `services/`, `.htaccess`, `sitemap.xml`, `robots.txt`, `llms.txt`.
2. Point a Hostinger subdomain (example: `preview.109dental.ca` or Hostinger’s default temp URL) at that folder.
3. Confirm HTTPS works (`.htaccess` already redirects HTTP to HTTPS when Apache + cert are in place).
4. Open the temp URL and click Call, Book, Contact map, Wisdom Teeth, and the form.
5. First FormSubmit send from a new domain needs a one-time email confirm to `dental_appointment@shaw.ca`.
6. Optional while previewing: add `<meta name="robots" content="noindex, nofollow">` in the shared head (in `tools/generate.py`) if you do not want the temp host indexed. Production `robots.txt` currently allows crawl for 109dental.ca.

## GitHub Pages base tag (remove or rewrite before Hostinger)

Every page has:

```html
<base href="https://stockwise-support.github.io/109-dental-site/" data-gh-pages-base>
```

That prefix plus base-relative URLs is what makes CSS, JS, the logo, and in-site links work on the project Pages URL.

Before Hostinger / `109dental.ca` cutover:

1. In `tools/generate.py`, change `GH_PAGES_BASE` to `https://109dental.ca/` or `/`.
2. Run `python3 tools/generate.py`.
3. Do **not** delete `<base>` unless you also convert every nested-page link to `../` form. Nested folders (`about/`, `services/wisdom-teeth/`) need either a root `<base>` or `../` paths.

## DNS cutover to 109dental.ca

1. Remove the preview banner in `tools/generate.py` (the `preview-banner` div) and regenerate, or delete that bar from each HTML file.
2. Switch `GH_PAGES_BASE` as above, then regenerate.
3. Keep canonicals, sitemap, schema, and footer links on `https://109dental.ca` (already set).
4. At the domain registrar / current host, point 109dental.ca A/CNAME records to Hostinger as Hostinger documents.
5. Wait for DNS, then test HTTPS, the Edmonton map, mailto, and a form submit.
6. Request indexing in Google Search Console for the homepage and `/services/wisdom-teeth/`.
7. Replace photo placeholders with clinic images. Add the real Meta pixel ID on the wisdom teeth page when ads start.

## Forms

Booking forms POST to [FormSubmit](https://formsubmit.co) at `dental_appointment@shaw.ca`.

Fields: name, phone, email, preferred time, reason (new patient / wisdom / emergency / other), optional notes. JavaScript copies UTM query params into hidden fields and sets `_next` to `/thank-you/` on the current host.

## Launch checklist

- [ ] Sandra confirms hours, CDCP, bios, parking notes
- [ ] Real photos swapped in
- [ ] Preview banner removed
- [ ] FormSubmit confirmed on the production domain
- [ ] Meta pixel installed if ads are live
- [ ] DNS live on 109dental.ca

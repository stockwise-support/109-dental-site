# 109 Dental website

Static HTML/CSS/JS clinic site for **109 Dental** (Edmonton). No Next.js. Built so StockWise can share one HTTPS link with Sandra, then cut over to [109dental.ca](https://109dental.ca) on Hostinger later.

## Photos imported from 109dental.ca

Used on Home, About, New Patients, Contact, and service pages (not invented, not stock tiles):

- `assets/photos/exterior.webp` — clinic building with the 109 Dental sign
- `assets/photos/reception.webp` — front desk and waiting chairs
- `assets/photos/waiting-room.webp` — waiting area
- `assets/photos/operatory.webp` — treatment room / hallway
- `assets/photos/front-desk.webp` — team member at reception
- `assets/photos/treatment-room.webp` — team member in a treatment room
- `assets/photos/dr-steve-barkwell.webp` and `dr-guy-girtel.webp` — About portraits
- `assets/brand-logo.png` and `assets/brand-mark.png` — their wordmark and tooth mark

See `assets/photos/SOURCES.txt`. Generic old-site stock (Shutterstock tiles, posed family/emergency shots) was not reused.

## Share this link (Sandra / StockWise)

**https://stockwise-support.github.io/109-dental-site/**

That is the live GitHub Pages preview. Hard-refresh if a tab still looks unstyled. CSS, JS, and the logo load from `/109-dental-site/…`, not from the github.io domain root.

## How to preview locally

From the repo root:

```bash
python3 -m http.server 8080
```

Open [http://localhost:8080](http://localhost:8080).

Asset and nav URLs are **base-relative** (`css/styles.css`, `contact/`). An inline script sets `<base>` to:

- `https://stockwise-support.github.io/109-dental-site/` on GitHub Pages
- `https://<your-host>/` on Vercel, Hostinger, or `109dental.ca`
- `http://localhost:8080/` on local preview

Do not switch back to path-absolute `/css/styles.css`. Those ignore `<base>` and 404 on project Pages.

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

## Vercel one-click (`vercel.json`)

Root `vercel.json` is a no-framework static config (`trailingSlash: true`, `cleanUrls: false`). Folder URLs (`/about/`, `/contact/`) and root `404.html` work at domain root.

1. Import `stockwise-support/109-dental-site` in Vercel (Framework Preset: Other / no framework).
2. Deploy. The base script switches to `/` on `*.vercel.app` so CSS loads from the Vercel domain, not GitHub Pages.
3. Share the `*.vercel.app` URL if you want a root preview. GitHub Pages stays the default Sandra link.

No Vercel token is stored in this repo. If import is not connected yet, keep using the Pages URL above.

## Hostinger fallback (Git App cannot see this repo)

Hostinger Git import only lists repos the GitHub App is granted. Vista can show while `109-dental-site` does not. Do not wait on that grant to share a preview.

**Share now:** use the GitHub Pages link.

**When you want Hostinger anyway:**

1. GitHub → org Settings → GitHub Apps → Hostinger → Repository access → add `109-dental-site`, or
2. Zip the repo and upload to `public_html` (keep `index.html`, `css/`, `js/`, `assets/`, `about/`, `services/`, `.htaccess`, `sitemap.xml`, `robots.txt`, `llms.txt`, `vercel.json`).

On a Hostinger root or temp subdomain the same base script sets `<base>` to that host. First FormSubmit send from a new domain needs a one-time confirm to `dental_appointment@shaw.ca`.

## GitHub Pages `<base>` tag

Every page still has `data-gh-pages-base`. The default `href` is the Pages URL so CSS works even if the rewrite script is blocked. On Vercel or Hostinger the script changes it to `/`.

Optional before `109dental.ca` cutover: set `GH_PAGES_BASE` in `tools/generate.py` to `https://109dental.ca/` or `/` and run `python3 tools/generate.py`. Do **not** delete `<base>` unless every nested link is rewritten with `../`.

## DNS cutover to 109dental.ca

1. Remove the preview banner in `tools/generate.py` (the `preview-banner` div) and regenerate, or delete that bar from each HTML file.
2. Optional: set `GH_PAGES_BASE` to `https://109dental.ca/` and regenerate. The runtime base script already uses `/` on a root host.
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

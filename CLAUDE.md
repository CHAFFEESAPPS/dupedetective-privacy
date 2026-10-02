# Dupe Detective website

Marketing site and privacy policy for **Dupe Detective: Receipt Scanner**, an iPhone and Mac app (one App Store listing, same bundle ID) that scans paper receipts and highlights items charged more than once.

- App Store: https://apps.apple.com/us/app/dupedetective-receipt-scanner/id6773174333 (app ID 6773174333)
- Support email: support@dupedetective.tech (Zoho Mail)
- The owner is not a developer. Explain steps in plain language and do the git work for them.

## What lives where

| Path | What it is | Hosted on |
|---|---|---|
| `index.html` (repo root) | Privacy policy. The URL in App Store Connect points here. Don't move it. | GitHub Pages: https://chaffeesapps.github.io/dupedetective-privacy/ |
| `website/` | Marketing site: landing page, FAQ, blog | Cloudflare Pages, project `dupedetective`, production branch `main`, no build command, output dir `website`. Custom domain https://dupedetective.tech |
| `content/blog/*.html` | Blog post sources (front-matter comment + body HTML) | — |
| `scripts/build_site.py` | Generates `website/blog/*`, `sitemap.xml`, `robots.txt`, `llms.txt`, the homepage Guides list, and the shared header and footer on every page | — |
| `website/images/` | App Store screenshots (WebP, 600px wide) | — |

Pushing to `main` deploys the site automatically via Cloudflare.

## Working on the site

- **Add a blog post:** create `content/blog/<slug>.html` with `title`, `description`, `date`, `answer` in the top comment. Add the slug to `POSTS` and `RELATED` in `scripts/build_site.py`. Run `python3 scripts/build_site.py`. Commit both `content/` and `website/`.
- **Never hand-edit** `website/blog/*`, `sitemap.xml`, `robots.txt` or `llms.txt`. They're generated. `website/index.html`, `website/faq.html`, `website/about.html`, `website/checkout-overcharge-statistics.html`, `website/styles.css` and `website/404.html` are hand-edited, except for the blocks between `<!-- header:start/end -->`, `<!-- footer:start/end -->` and `<!-- guides:start/end -->` markers, which the build script fills in.
- **Header and footer** are defined once in `scripts/build_site.py` (`header()` and `FOOTER`). The footer carries the priority pages (download links, How it works, FAQ, statistics, About). A new hand-edited page needs the markers and an entry in `STATIC_PAGES`.
- **Statistics page** (`/checkout-overcharge-statistics`): only cite government, university or established consumer-publication sources, link the original, and give sample and dates beside each figure. Review quarterly and update the "Last reviewed" date and `dateModified`.
- Internal links use clean root-relative URLs (`/faq`, `/blog/<slug>`), matching the canonical tags.
- When FAQ answers change, update both the visible text and the FAQPage JSON-LD in `website/faq.html`.

## Messaging rules (from the owner)

- **Main pitch: scan your receipt before you leave the store.** It takes a few seconds, and a double charge caught at the register gets fixed on the spot instead of a bank dispute later.
- Disputes happen in the banking app ("Dispute" / "Report a problem") or by calling the number on the back of the card. Don't tell people to write letters.
- Only claim what the app actually does: on-device scanning, iCloud sync via the user's private database (developers have no access), camera used only when scanning.
- Other confirmed features: grocery list that syncs between Mac and iPhone on the same Apple ID; the list scrolls across the top of the app like a stock ticker while shopping; receipt history; import digital receipts; works with Costco, Kroger, Fry's, Sam's Club, Walmart and most grocery stores; pricing: free download, 3 free scans, then a 7-day free trial, then Dupe Detective Pro at $4.99/year (subscription). Don't call the app "free" without the trial context. (The App Store description still says "No subscription required"; the owner should fix it in App Store Connect.)
- Each blog post targets a real search question and opens with a short, direct answer.

## Open items

1. ~~Apply the SEO spec from https://x.com/borjafat/status/2104896885173436464~~ Done: About page, statistics page, footer with priority links. Original research for the statistics page would also help (for example an opt-in in-app survey); the app is on-device, so there's no receipt data to draw on.
2. ~~Add App Store screenshots to "How it works"~~ Done.
3. Add `www.dupedetective.tech` as a Cloudflare custom domain and redirect it to the apex domain (Cloudflare dashboard → Rules → Redirect Rules).
4. Set up Google Search Console for dupedetective.tech and submit `https://dupedetective.tech/sitemap.xml`.
5. Privacy policy (`index.html` at root) fixes, discussed but not made yet:
   - The "delete data by uninstalling" line ignores the iCloud copy.
   - "Anonymous usage analytics" conflicts with "doesn't transmit data to third parties". Need to know which analytics, if any.
   - Missing sections: data retention, children's privacy, policy changes.
6. Confirm Zoho email still works after the nameserver move to Cloudflare (MX, SPF, DKIM records).

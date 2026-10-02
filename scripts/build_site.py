#!/usr/bin/env python3
"""Build the blog, sitemap, robots.txt and llms.txt for the Dupe Detective site.

Blog posts live in content/blog/<slug>.html. Each file starts with a comment
block of `key: value` lines (title, description, date, answer), followed by
the post body HTML.

To add a post: create the content file, add its slug to POSTS (and RELATED),
then run `python3 scripts/build_site.py` and commit the result. Cloudflare
Pages serves the `website/` folder as-is; there is no build step there.
"""
import html
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SITE = ROOT / "website"
CONTENT = ROOT / "content" / "blog"

BASE = "https://dupedetective.tech"
APP_ID = "6773174333"
APP_URL = "https://apps.apple.com/us/app/dupedetective-receipt-scanner/id6773174333"
POLICY_URL = "https://chaffeesapps.github.io/dupedetective-privacy/"
EMAIL = "support@dupedetective.tech"

# Newest or most important first. This is the order on the blog index.
POSTS = [
    "why-was-i-charged-twice",
    "double-charged-what-to-do",
    "pending-charge-showing-twice",
    "charged-twice-grocery-store",
    "how-to-dispute-a-double-charge",
    "double-charged-debit-card",
    "how-to-check-receipt-for-errors",
    "spot-duplicate-charges-on-receipts",
]

RELATED = {
    "why-was-i-charged-twice": ["pending-charge-showing-twice", "double-charged-what-to-do", "charged-twice-grocery-store"],
    "double-charged-what-to-do": ["how-to-dispute-a-double-charge", "double-charged-debit-card", "why-was-i-charged-twice"],
    "pending-charge-showing-twice": ["why-was-i-charged-twice", "double-charged-debit-card", "how-to-dispute-a-double-charge"],
    "charged-twice-grocery-store": ["how-to-check-receipt-for-errors", "spot-duplicate-charges-on-receipts", "how-to-dispute-a-double-charge"],
    "how-to-dispute-a-double-charge": ["double-charged-what-to-do", "double-charged-debit-card", "pending-charge-showing-twice"],
    "double-charged-debit-card": ["how-to-dispute-a-double-charge", "pending-charge-showing-twice", "why-was-i-charged-twice"],
    "how-to-check-receipt-for-errors": ["charged-twice-grocery-store", "spot-duplicate-charges-on-receipts", "why-was-i-charged-twice"],
    "spot-duplicate-charges-on-receipts": ["how-to-check-receipt-for-errors", "charged-twice-grocery-store", "double-charged-what-to-do"],
}

FONTS = "https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,600;12..96,700&family=IBM+Plex+Mono:wght@400;600&family=Public+Sans:wght@400;600&display=swap"

LOGO = ('<svg width="26" height="26" viewBox="0 0 26 26" aria-hidden="true"><rect x="3" y="2" width="14" height="19" rx="2" fill="none" stroke="currentColor" stroke-width="2"/>'
        '<path d="M6.5 7h7M6.5 11h5" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>'
        '<circle cx="17" cy="16" r="4.5" fill="var(--mark)" stroke="currentColor" stroke-width="2"/>'
        '<path d="M20.3 19.3 24 23" stroke="currentColor" stroke-width="2.4" stroke-linecap="round"/></svg>')


def parse(slug):
    raw = (CONTENT / f"{slug}.html").read_text()
    m = re.match(r"\s*<!--(.*?)-->\s*(.*)", raw, re.S)
    meta = {}
    for line in m.group(1).strip().splitlines():
        key, _, value = line.partition(":")
        meta[key.strip()] = value.strip()
    meta["body"] = m.group(2).rstrip()
    meta["slug"] = slug
    meta["url"] = f"{BASE}/blog/{slug}"
    return meta


def human_date(iso):
    import datetime
    d = datetime.date.fromisoformat(iso)
    return f"{d.strftime('%B')} {d.day}, {d.year}"


def head(title, description, canonical, og_type="website", extra=""):
    e = html.escape
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{e(title)}</title>
  <meta name="description" content="{e(description)}">
  <meta name="apple-itunes-app" content="app-id={APP_ID}">
  <link rel="canonical" href="{canonical}">
  <link rel="icon" href="/favicon.svg" type="image/svg+xml">
  <link rel="apple-touch-icon" href="/apple-touch-icon.png">
  <meta property="og:type" content="{og_type}">
  <meta property="og:site_name" content="Dupe Detective">
  <meta property="og:title" content="{e(title)}">
  <meta property="og:description" content="{e(description)}">
  <meta property="og:url" content="{canonical}">
  <meta property="og:image" content="{BASE}/og-image.png">
  <meta name="twitter:card" content="summary_large_image">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link rel="stylesheet" href="{FONTS}">
  <link rel="stylesheet" href="/styles.css">
{extra}</head>"""


def header(current):
    def link(href, label, key):
        cur = ' aria-current="page"' if key == current else ""
        return f'<a href="{href}"{cur}>{label}</a>'
    return f"""  <header class="site-header">
    <div class="wrap">
      <a class="brand" href="/">
        {LOGO}
        Dupe Detective
      </a>
      <nav class="nav" aria-label="Main">
        {link("/#how", "How it works", "how")}
        {link("/faq", "FAQ", "faq")}
        {link("/blog/", "Blog", "blog")}
        {link("/about", "About", "about")}
      </nav>
    </div>
  </header>"""


FOOTER = f"""  <footer class="site-footer">
    <div class="wrap">
      <div class="footer-cols">
        <nav aria-label="Get the app">
          <h2>Get the app</h2>
          <a href="{APP_URL}">Download for iPhone</a>
          <a href="{APP_URL}">Download for Mac</a>
          <a href="/#how">How Dupe Detective works</a>
          <a href="/faq">Receipt scanner FAQ</a>
        </nav>
        <nav aria-label="Learn">
          <h2>Learn</h2>
          <a href="/checkout-overcharge-statistics">Checkout overcharge statistics 2026</a>
          <a href="/blog/why-was-i-charged-twice">Why was I charged twice?</a>
          <a href="/blog/charged-twice-grocery-store">Charged twice at the grocery store</a>
          <a href="/blog/">All guides</a>
        </nav>
        <nav aria-label="Company">
          <h2>Company</h2>
          <a href="/about">About Dupe Detective</a>
          <a href="{POLICY_URL}">Privacy policy</a>
          <a href="mailto:{EMAIL}">Contact support</a>
        </nav>
      </div>
      <p class="footer-legal">© 2026 Dupe Detective · {EMAIL}</p>
    </div>
  </footer>"""

# Hand-written pages: (file, nav key). Their header and footer are replaced
# between <!-- header:start/end --> and <!-- footer:start/end --> markers.
STATIC_PAGES = [
    ("index.html", "home"),
    ("faq.html", "faq"),
    ("about.html", "about"),
    ("checkout-overcharge-statistics.html", "stats"),
]


def inject(text, name, block):
    return re.sub(rf"(<!-- {name}:start -->\n).*?(<!-- {name}:end -->)",
                  lambda m: m.group(1) + block + "\n" + m.group(2), text, flags=re.S)


def ld(obj):
    return '  <script type="application/ld+json">\n  ' + json.dumps(obj, ensure_ascii=False) + "\n  </script>\n"


def post_page(p, posts):
    schema = ld({
        "@context": "https://schema.org",
        "@type": "BlogPosting",
        "headline": p["title"],
        "description": p["description"],
        "datePublished": p["date"],
        "dateModified": p.get("updated", p["date"]),
        "image": f"{BASE}/og-image.png",
        "author": {"@type": "Organization", "name": "Dupe Detective", "url": BASE + "/"},
        "publisher": {"@type": "Organization", "name": "Dupe Detective", "logo": {"@type": "ImageObject", "url": f"{BASE}/apple-touch-icon.png"}},
        "mainEntityOfPage": p["url"],
    }) + ld({
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Home", "item": BASE + "/"},
            {"@type": "ListItem", "position": 2, "name": "Blog", "item": BASE + "/blog/"},
            {"@type": "ListItem", "position": 3, "name": p["title"], "item": p["url"]},
        ],
    })
    related = "\n".join(
        f'          <li><a href="/blog/{s}">{html.escape(posts[s]["title"])}</a></li>' for s in RELATED[p["slug"]]
    )
    main = f"""  <main class="wrap">
    <article class="article prose">
      <header>
        <nav class="crumbs eyebrow" aria-label="Breadcrumb"><a href="/">Home</a> / <a href="/blog/">Blog</a></nav>
        <h1>{html.escape(p["title"])}</h1>
        <time datetime="{p["date"]}">{human_date(p["date"])}</time>
      </header>
      <div class="answer">
        <p class="eyebrow">Short answer</p>
        <p>{html.escape(p["answer"])}</p>
      </div>
      <p class="tip"><strong>Skip the hassle next time.</strong> Scan your receipt with <a href="/">Dupe Detective</a> before you leave the store. It takes a few seconds, and a double charge caught at the register is fixed on the spot.</p>
      <div class="body">
{p["body"]}
      </div>
      <aside class="app-cta">
        <div>
          <h2>Scan it before you leave the store</h2>
          <p>Dupe Detective checks your receipt in a few seconds and highlights anything you were charged for twice, so you can get it fixed at the register instead of disputing it later.</p>
        </div>
        <a class="btn btn-primary" href="{APP_URL}">Download on the App Store</a>
      </aside>
      <nav class="related" aria-label="Related guides">
        <h2>Related guides</h2>
        <ul>
{related}
        </ul>
      </nav>
    </article>
  </main>"""
    return f"""{head(p["title"] + " · Dupe Detective", p["description"], p["url"], "article", schema)}
<body>
{header("blog")}

{main}

{FOOTER}
</body>
</html>
"""


def blog_index(posts):
    items = "\n".join(f"""      <li>
        <time datetime="{p["date"]}">{human_date(p["date"])}</time>
        <a href="/blog/{p["slug"]}"><h2>{html.escape(p["title"])}</h2></a>
        <p>{html.escape(p["description"])}</p>
      </li>""" for p in posts)
    schema = ld({
        "@context": "https://schema.org",
        "@type": "Blog",
        "name": "Dupe Detective Blog",
        "url": BASE + "/blog/",
        "blogPost": [{"@type": "BlogPosting", "headline": p["title"], "url": p["url"], "datePublished": p["date"]} for p in posts],
    })
    return f"""{head("Blog · Dupe Detective", "Guides to spotting duplicate charges, reading receipts and getting refunds when you're charged twice.", BASE + "/blog/", "website", schema)}
<body>
{header("blog")}

  <main class="wrap">
    <div class="page-head">
      <p class="eyebrow">Blog</p>
      <h1>Guides to catching double charges</h1>
      <p>Practical answers to the questions people ask when they see the same charge twice: why it happened, how to tell a hold from a duplicate, and how to get the money back. The easiest fix is to catch it before you leave the store.</p>
    </div>
    <ul class="post-list">
{items}
    </ul>
  </main>

{FOOTER}
</body>
</html>
"""


def home_guides(posts):
    return "\n".join(
        f'          <li><a href="/blog/{p["slug"]}">{html.escape(p["title"])}</a></li>' for p in posts[:5]
    )


def main():
    posts = {s: parse(s) for s in POSTS}
    ordered = [posts[s] for s in POSTS]
    blog = SITE / "blog"
    blog.mkdir(exist_ok=True)
    for old in blog.glob("*.html"):
        old.unlink()
    for p in ordered:
        (blog / f"{p['slug']}.html").write_text(post_page(p, posts))
    (blog / "index.html").write_text(blog_index(ordered))

    for name, key in STATIC_PAGES:
        page = SITE / name
        text = page.read_text()
        text = inject(text, "header", header(key))
        text = inject(text, "footer", FOOTER)
        text = inject(text, "guides", home_guides(ordered))
        page.write_text(text)

    latest = max(p.get("updated", p["date"]) for p in ordered)
    urls = [("/", latest), ("/faq", latest), ("/about", latest),
            ("/checkout-overcharge-statistics", latest), ("/blog/", latest)] + [
        (f"/blog/{p['slug']}", p.get("updated", p["date"])) for p in ordered
    ]
    (SITE / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + "".join(f"  <url><loc>{BASE}{u}</loc><lastmod>{d}</lastmod></url>\n" for u, d in urls)
        + "</urlset>\n"
    )

    search_bots = ["Googlebot", "Bingbot", "Applebot", "DuckDuckBot"]
    ai_bots = ["OAI-SearchBot", "ChatGPT-User", "GPTBot",
               "Claude-SearchBot", "Claude-User", "ClaudeBot",
               "PerplexityBot", "Perplexity-User",
               "Google-Extended", "Applebot-Extended",
               "Meta-ExternalAgent", "Amazonbot", "DuckAssistBot", "MistralAI-User"]
    (SITE / "robots.txt").write_text(
        "# robots.txt for https://dupedetective.tech\n"
        "# Every page on this site is public and may be crawled, indexed and cited.\n"
        "# Generated by scripts/build_site.py. Don't edit by hand.\n\n"
        "# Cloudflare content signals: allow search results, AI answers that cite\n"
        "# this site, and AI training. See https://contentsignals.org\n"
        "User-agent: *\n"
        "Content-Signal: search=yes, ai-input=yes, ai-train=yes\n"
        "Allow: /\n"
        "Disallow: /404\n\n"
        "# Search engines\n"
        + "".join(f"User-agent: {b}\n" for b in search_bots)
        + "Allow: /\n"
        "Disallow: /404\n\n"
        "# AI search, assistant and model crawlers\n"
        + "".join(f"User-agent: {b}\n" for b in ai_bots)
        + "Allow: /\n"
        "Disallow: /404\n\n"
        f"Sitemap: {BASE}/sitemap.xml\n"
    )

    (SITE / "llms.txt").write_text(
        "# Dupe Detective\n\n"
        "> Dupe Detective is a receipt scanner for iPhone and Mac. You scan a paper receipt and the app "
        "highlights any item that appears more than once, such as an item scanned twice at the register. "
        "Scanning takes a few seconds, so shoppers can catch a double charge before leaving the store "
        "and have it fixed at the register instead of disputing it with their bank later. "
        "Receipts are processed on the device and sync through the user's private iCloud database; the "
        "developers cannot access them.\n\n"
        f"- App Store: {APP_URL}\n"
        f"- Support: {EMAIL}\n"
        f"- Privacy policy: {POLICY_URL}\n\n"
        "## Pages\n\n"
        f"- [Home]({BASE}/): what the app does and how it works\n"
        f"- [FAQ]({BASE}/faq): privacy, iCloud sync, deleting data, refunds\n"
        f"- [About]({BASE}/about): what Dupe Detective does, who it's for and who makes it\n"
        f"- [Checkout overcharge statistics 2026]({BASE}/checkout-overcharge-statistics): "
        "sourced figures on how often stores overcharge at the register\n\n"
        "## Guides\n\n"
        + "".join(f"- [{p['title']}]({p['url']}): {p['answer']}\n" for p in ordered)
    )
    print(f"Built {len(ordered)} posts, blog index, sitemap.xml, robots.txt, llms.txt")


if __name__ == "__main__":
    main()

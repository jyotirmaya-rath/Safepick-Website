#!/usr/bin/env python3
"""Builds the SafePick website (safepick.app) into ../site.

Run from anywhere:   python3 build/build.py
Needs only Python 3 (already on the Mac). Nothing to install.

What to edit
  CONFIG below        company name, e-mail addresses, the "last updated" date of the legal pages
  pages/*.html        the words on each page
  partials/*.html     the shared pieces (header, footer, phone screens)
  static/             styles, script and pictures, copied as they are
Then run this file again. It rewrites every page in ../site and checks every link and picture.
"""
import html
import re
import shutil
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE.parent / "site"

CONFIG = {
    "site_url": "https://www.safepick.app",
    "company": "SafePick Corporation",
    "company_place": "British Columbia, Canada",
    "email_support": "support@safepick.app",
    "email_business": "partners@safepick.app",
    "email_privacy": "privacy@safepick.app",
    "legal_updated": "November 17, 2026",
    "legal_updated_iso": "2026-11-17",
    "year": "2026",
}

# path ('' is the home page), source file, name in the menu, <title>, description
PAGES = [
    ("", "home.html", None,
     "SafePick: scan food and beauty barcodes before you buy",
     "Scan the barcode on packaged food, beauty and personal-care products. SafePick shows a clear score, what's Approved and Disapproved, allergen alerts and better choices. No ads."),
    ("features/", "features.html", "Features",
     "Features: barcode scanner, product scores and better choices | SafePick",
     "Everything SafePick does: a fast barcode scanner, a clear score for food and beauty products, better choices from the same shelf, search, history and offline copies."),
    ("for-you/", "for-you.html", "For you",
     "Allergy, diet and health checks on every scan | SafePick",
     "Save your allergies, intolerances, diet and health goals once. Every SafePick scan then tells you how the product fits you. Optional, free and kept on your phone."),
    ("beauty/", "beauty.html", "Beauty",
     "Beauty and personal-care scanner: ingredients, skin match | SafePick",
     "Scan skincare, makeup and haircare. SafePick reads the ingredient list, shows what is and isn't listed, how the formula suits your skin type, and better-rated options."),
    ("how-scores-work/", "scores.html", "Scores",
     "How SafePick scores work: method, data and limits",
     "How SafePick turns a label into a score out of 100: the nutrients it reads, the score bands, what is never guessed, which products aren't scored and where the data comes from."),
    ("plans/", "plans.html", "Plans",
     "Plans: Free, Premium and the Supporter Pass | SafePick",
     "SafePick is free to scan, with 1,000 different products a month. Premium adds unlimited scans, full product details and personal tools. No ads on any plan."),
    ("business/", "business.html", "Business",
     "For brands, retailers and data partners | SafePick",
     "Work with SafePick Corporation: correct or submit product data, connect your store, or license product data. Scores are independent and cannot be bought."),
    ("about/", "about.html", "About",
     "About SafePick Corporation",
     "SafePick Corporation is a Canadian company building an independent, ad-free product scanner for food, beauty and personal care, launching first in Canada."),
    ("founders/", "founders.html", None,
     "Founders: Jyotirmaya Rath and Phani Komi | SafePick",
     "Meet the co-founders of SafePick Corporation: Jyotirmaya Rath, who leads product and technology, and Phani Komi, who leads partnerships and customer relationships."),
    ("blog/", None, "Blog",
     "Blog: food labels, healthy eating and food safety | SafePick",
     "Plain-language articles from SafePick on reading food labels, eating well, feeding kids and food safety."),
    ("support/", "support.html", "Support",
     "Support and contact | SafePick",
     "Get help with SafePick, report a product problem, ask a privacy question or contact SafePick Corporation. Answers to common questions about scanning, accounts and Premium."),
    ("privacy/", "privacy.html", None,
     "Privacy policy | SafePick",
     "What the SafePick app and safepick.app website do with your information: what stays on your phone, what is kept on your account, who we share it with and how to delete it."),
    ("terms/", "terms.html", None,
     "Terms of use | SafePick",
     "The terms for using the SafePick app and website: not medical advice, accuracy of product data, store and affiliate links, contributions, Premium and the Supporter Pass."),
    ("delete-account/", "delete-account.html", None,
     "Delete your SafePick account and data",
     "How to delete your SafePick account and the data kept with it, in the app or by e-mail, what is deleted, what is kept and how long it takes."),
]

# Blog posts, newest first: address, source file, title, one-line summary, picture, what the picture shows, minutes to read
POSTS = [
    ("what-healthy-food-looks-like", "blog-healthy-food.html",
     "What healthy food actually looks like",
     "Forget superfoods. Healthy eating is a pattern you can see on a plate: half vegetables and fruits, a quarter whole grains, a quarter protein, and water to drink.",
     "healthy-plate.jpg", "A plate divided into half vegetables and fruits, a quarter whole grain foods and a quarter protein foods, with a glass of water", 5),
    ("what-is-bad-food", "blog-bad-food.html",
     "What is \"bad\" food? Three things to check on any label",
     "No single food is the villain. What matters is how much sugar, sodium and saturated fat a packaged food carries, and how often you eat it.",
     "high-in.jpg", "Four packaged foods on a shelf, tagged high in sugars, high in sodium and high in saturated fat", 5),
    ("how-to-read-the-back-of-a-food-package", "blog-back-of-pack.html",
     "What's on the back of the pack: a guided tour",
     "The front of a package is advertising. The back is information. Here is what each part of the back panel tells you, and how to read it in under a minute.",
     "back-of-pack.jpg", "The back of a cereal box with the nutrition table, ingredient list, allergen statement, date and barcode pointed out", 6),
    ("scan-before-you-buy", "blog-scan-before-you-buy.html",
     "Your phone is your best defence in the grocery aisle",
     "You already carry the tool that can read the back of every pack for you. How to make a ten-second scan part of every shop.",
     "phone-shield.jpg", "A phone scanning a barcode in front of a shield, with packaged foods on shelves either side", 4),
    ("how-safepick-is-different", "blog-how-different.html",
     "How SafePick is different",
     "Six questions worth asking of any product-scanner app, and how SafePick answers each of them.",
     "how-different.jpg", "A nutrition-style label titled SafePick Facts listing zero ads, zero scores for sale and zero data sold", 4),
    ("healthiest-foods-for-kids", "blog-kids-top-10.html",
     "The top 10 healthiest foods for kids",
     "Ten everyday foods that children's nutrition guidance keeps coming back to, with tips for serving each one safely.",
     "kids-top-10.jpg", "Ten plates numbered one to ten holding vegetables, fruit, an egg, yogurt, oats, beans, fish, nut butter, bread and milk", 6),
    ("tukaram-mundhe-food-safety", "blog-tukaram-mundhe.html",
     "Tukaram Mundhe: the officer who made food safety go viral",
     "How an IAS officer known for 25 transfers in 21 years turned Maharashtra's Food and Drug Administration into a household name, and why his methods are debated.",
     "food-safety-inspection.jpg", "An inspection clipboard with ticks and crosses beside a magnifying glass held over a plate of food", 6),
]
POST_DATE = "November 17, 2026"
POST_DATE_ISO = "2026-11-17"

NAV = [(p, name) for p, _src, name, _t, _d in PAGES if name]
LEGAL = {"privacy/", "terms/", "delete-account/"}


def read(rel):
    return (HERE / rel).read_text(encoding="utf-8")


def expand(text, root, extra=None):
    """Fill {{> partial}} includes, then {{name}} values."""
    values = dict(CONFIG)
    values["root"] = root
    if extra:
        values.update(extra)

    def include(m):
        return expand(read(f"partials/{m.group(1)}.html"), root, extra)

    for _ in range(4):  # partials may include partials
        text, n = re.subn(r"\{\{>\s*([\w-]+)\s*\}\}", include, text)
        if not n:
            break

    def value(m):
        key = m.group(1)
        if key not in values:
            raise KeyError(f"unknown value {{{{{key}}}}}")
        return str(values[key])

    return re.sub(r"\{\{(\w+)\}\}", value, text)


TABS_RE = re.compile(r"<!--tabs:(.*?)-->(.*?)<!--/tabs-->", re.S)


def tabs(text):
    """<!--tabs: Name=id | Name=id --> ...sections... <!--/tabs-->  becomes a row of tabs over one visible section.
    Without JavaScript every section simply shows, one under the other."""
    def build(m):
        pairs = [x.strip().rsplit("=", 1) for x in m.group(1).split("|")]
        inner = m.group(2)
        links = []
        for name, pid in pairs:
            name, pid = name.strip(), pid.strip()
            links.append(f'<a class="tab" href="#{pid}" data-panel="{pid}">{html.escape(name)}</a>')
            new, n = re.subn(
                r'<section class="[^"]*" id="' + re.escape(pid) + r'"[^>]*>',
                f'<section class="tabpanel" id="{pid}" aria-label="{html.escape(name, quote=True)}">',
                inner, count=1,
            )
            if n != 1:
                raise ValueError(f"tabs: no <section id=\"{pid}\"> found")
            inner = new
        row = "\n        ".join(links)
        return (
            '  <div class="tabs" data-tabs>\n'
            '    <div class="wrap">\n      <nav class="tablist" aria-label="Sections of this page">\n        '
            + row + "\n      </nav>\n    </div>" + inner + "  </div>"
        )
    return TABS_RE.sub(build, text)


def nav_html(root, current):
    items = []
    for path, name in NAV:
        on = path == current or (path == "blog/" and current and current.startswith("blog/"))
        cur = (' aria-current="page"' if path == current else ' aria-current="true"') if on else ""
        items.append(f'      <a href="{root}{path}"{cur}>{html.escape(name)}</a>')
    return "\n".join(items)


def post_card(root, post, heading="h3", lead=False):
    slug, _src, title, dek, cover, alt, minutes = post
    cls = "post-card lead" if lead else "post-card"
    return (
        f'<a class="{cls}" href="{root}blog/{slug}/">'
        f'<img src="{root}assets/img/blog/{cover}" alt="{html.escape(alt, quote=True)}" width="1600" height="900">'
        f'<span class="post-card-text"><span class="post-meta">{minutes} min read</span>'
        f'<{heading}>{html.escape(title)}</{heading}><span class="post-dek">{html.escape(dek)}</span></span></a>'
    )


def blog_carousel(root, posts, heading="h3", label="Articles from the blog"):
    cards = "\n          ".join(post_card(root, p, heading) for p in posts)
    return (
        f'<div class="carousel" data-carousel data-label="{label}">\n'
        '        <div class="post-grid carousel-track" data-track style="--per-lg:3;--per-md:2;--per-sm:1.12;--gap:24px">\n          '
        + cards + "\n        </div>\n      </div>"
    )


def blog_index(root):
    featured = "\n          ".join(post_card(root, p, "h2", lead=True) for p in POSTS[:3])
    cards = "\n        ".join(post_card(root, p, "h2") for p in POSTS[3:])
    return f"""
  <section class="page-head">
    <div class="wrap page-head-solo">
      <div class="page-head-copy">
        <p class="eyebrow">Blog</p>
        <h1>Read the label. Know the food.</h1>
        <p class="lede">Plain-language articles on food labels, eating well, feeding kids and food safety, from the team behind SafePick.</p>
      </div>
    </div>
  </section>

  <section class="section section-tint" id="posts" style="padding-top:clamp(40px,5vw,64px)">
    <div class="wrap">
      <div class="carousel carousel-featured" data-carousel data-autoplay="6000" data-label="Featured articles">
        <div class="post-grid carousel-track" data-track style="--per-lg:1;--per-md:1;--per-sm:1;--gap:24px">
          {featured}
        </div>
      </div>
      <div class="post-grid four" style="margin-top:clamp(28px,4vw,44px)">
        {cards}
      </div>
      <p class="note" style="margin-top:28px">Our articles are general information, not medical advice. For a health condition, an allergy or a child's diet, ask a doctor or a registered dietitian.</p>
    </div>
  </section>
"""


def post_page(root, post):
    slug, src, title, dek, cover, alt, minutes = post
    body = expand(read(f"pages/{src}"), root)
    others = [p for p in POSTS if p[0] != slug]
    i = [p[0] for p in POSTS].index(slug)
    nxt = [POSTS[(i + k) % len(POSTS)] for k in range(1, len(POSTS))]
    more = blog_carousel(root, nxt, label="More articles")
    heads = re.findall(r'<h2 id="([\w-]+)">(.*?)</h2>', body)
    toc = ""
    if len(heads) >= 3:
        chips = "".join(f'<a href="#{i}">{re.sub(r"^\d+\.\s*", "", re.sub(r"<[^>]+>", "", t))}</a>' for i, t in heads)
        toc = f'<nav class="post-toc" aria-label="In this article">{chips}</nav>'

    return f"""
  <article>
    <header class="page-head post-top">
      <div class="wrap">
        <div class="post-head">
          <p class="eyebrow"><a href="{root}blog/">Blog</a></p>
          <h1>{html.escape(title)}</h1>
          <p class="lede">{html.escape(dek)}</p>
          <p class="post-meta">By the SafePick team · {POST_DATE} · {minutes} min read</p>
        </div>
      </div>
    </header>
    <div class="wrap">
      <figure class="post-cover"><img src="{root}assets/img/blog/{cover}" alt="{html.escape(alt, quote=True)}" width="1600" height="900"></figure>
      {toc}
      <div class="doc post">
{body}
        <p class="post-disclaimer">This article is general information, not medical advice. SafePick reads what is printed on a pack; it can't know your health, and it never replaces the label or advice from a doctor or registered dietitian.</p>
      </div>
    </div>
  </article>

  <section class="section section-tint" id="more">
    <div class="wrap">
      <div class="section-head"><h2>Keep reading</h2></div>
      {more}
    </div>
  </section>
"""


def post_schema(post):
    slug, _src, title, dek, cover, _alt, _m = post
    import json
    data = {
        "@context": "https://schema.org", "@type": "BlogPosting",
        "headline": title, "description": dek,
        "image": f"{CONFIG['site_url']}/assets/img/blog/{cover}",
        "datePublished": POST_DATE_ISO, "dateModified": POST_DATE_ISO,
        "author": {"@type": "Organization", "name": CONFIG["company"], "url": CONFIG["site_url"] + "/"},
        "publisher": {"@type": "Organization", "name": CONFIG["company"],
                      "logo": {"@type": "ImageObject", "url": f"{CONFIG['site_url']}/assets/img/icon-512.png"}},
        "mainEntityOfPage": f"{CONFIG['site_url']}/blog/{slug}/",
    }
    return '  <script type="application/ld+json">' + json.dumps(data, ensure_ascii=False) + "</script>\n"


def render(path, src, title, desc, body=None, schema=None, og_image=None):
    depth = path.count("/")
    root = "../" * depth
    if body is None:
        body = blog_index(root) if path == "blog/" else tabs(
            expand(read(f"pages/{src}"), root, {"blog_carousel": blog_carousel(root, POSTS)}))
    canonical = CONFIG["site_url"] + "/" + path
    extra = {
        "title": html.escape(title, quote=True),
        "desc": html.escape(desc, quote=True),
        "canonical": canonical,
        "nav": nav_html(root, path),
        "home": root if root else "./",
        "body": body,
        "body_class": "legal" if path in LEGAL else ("home" if path == "" else "inner"),
        "schema": schema if schema is not None else (expand(read("partials/schema.html"), root) if path == "" else ""),
    }
    page = expand(read("partials/layout.html"), root, extra)
    if og_image:
        page = page.replace(f'{CONFIG["site_url"]}/assets/img/og-image.png', og_image)
        page = page.replace('<meta property="og:type" content="website">', '<meta property="og:type" content="article">')
        page = page.replace('<meta property="og:image:width" content="1200">', '<meta property="og:image:width" content="1600">')
        page = page.replace('<meta property="og:image:height" content="630">', '<meta property="og:image:height" content="900">')
    return page


def render_404():
    # served for any missing address at any depth, so its links start from the top of the site
    root = "/"
    body = expand(read("pages/404.html"), root)
    extra = {
        "title": "Page not found | SafePick",
        "desc": "This page doesn't exist. Go back to the SafePick home page.",
        "canonical": CONFIG["site_url"] + "/",
        "nav": nav_html(root, None),
        "home": root,
        "body": body,
        "body_class": "inner",
        "schema": "",
    }
    page = expand(read("partials/layout.html"), root, extra)
    return page.replace('<meta name="robots" content="index, follow">', '<meta name="robots" content="noindex">')


def check(out):
    """Every local link, picture and #anchor must exist."""
    problems = []
    pages = sorted(out.rglob("*.html"))
    ids = {}
    for f in pages:
        ids[f] = set(re.findall(r'\sid="([^"]+)"', f.read_text(encoding="utf-8")))
    for f in pages:
        text = f.read_text(encoding="utf-8")
        if "{{" in text:
            problems.append(f"{f.relative_to(out)}: unfilled {{{{ }}}}")
        for attr, url in re.findall(r'\s(href|src)="([^"]*)"', text):
            if re.match(r"^(https?:|mailto:|tel:|data:)", url) or url == "":
                continue
            target, _, frag = url.partition("#")
            if target == "":
                dest = f
            else:
                base = out if target.startswith("/") else f.parent
                dest = (base / target.lstrip("/")).resolve()
                if dest.is_dir():
                    dest = dest / "index.html"
                if not dest.exists():
                    problems.append(f"{f.relative_to(out)}: missing {url}")
                    continue
            if frag and dest.suffix == ".html" and frag not in ids.get(dest, set()):
                problems.append(f"{f.relative_to(out)}: no #{frag} in {dest.relative_to(out)}")
        for use in re.findall(r'<use href="#([^"]+)"', text):
            if use not in ids[f]:
                problems.append(f"{f.relative_to(out)}: icon #{use} not defined")
    return problems


def main():
    if OUT.exists():
        shutil.rmtree(OUT)
    shutil.copytree(HERE / "static", OUT)
    for path, src, _name, title, desc in PAGES:
        dest = OUT / path / "index.html"
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(render(path, src, title, desc), encoding="utf-8")
    for post in POSTS:
        slug, _src, title, dek, cover, _alt, _m = post
        path = f"blog/{slug}/"
        dest = OUT / path / "index.html"
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(
            render(path, None, f"{title} | SafePick", dek, body=post_page("../../", post), schema=post_schema(post),
                   og_image=f"{CONFIG['site_url']}/assets/img/blog/{cover}"),
            encoding="utf-8",
        )
    (OUT / "404.html").write_text(render_404(), encoding="utf-8")

    all_paths = [p for p, *_ in PAGES] + [f"blog/{post[0]}/" for post in POSTS]
    urls = "\n".join(
        f"  <url><loc>{CONFIG['site_url']}/{p}</loc></url>" for p in all_paths
    )
    (OUT / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + urls + "\n</urlset>\n",
        encoding="utf-8",
    )
    (OUT / "robots.txt").write_text(
        f"User-agent: *\nAllow: /\n\nSitemap: {CONFIG['site_url']}/sitemap.xml\n", encoding="utf-8"
    )
    (OUT / "CNAME").write_text(CONFIG["site_url"].split("://", 1)[1] + "\n", encoding="utf-8")
    (OUT / ".nojekyll").write_text("", encoding="utf-8")

    problems = check(OUT)
    n = len(list(OUT.rglob("*.html")))
    if problems:
        print(f"Built {n} pages, but found {len(problems)} problem(s):")
        for p in problems:
            print("  -", p)
        sys.exit(1)
    print(f"Built {n} pages into {OUT}. Every link, picture and icon checks out.")


if __name__ == "__main__":
    main()

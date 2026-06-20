#!/usr/bin/env python3
"""
Databery static build step.

Bakes the shared nav + footer into every .html page as REAL markup (so the site
works without JavaScript and is fully crawlable for SEO), injects per-page
Open Graph / Twitter / canonical / JSON-LD tags, and regenerates sitemap.xml
and robots.txt.

Idempotent: safe to run any number of times.  After editing nav/footer here,
just re-run:  python build.py
"""
import os, re, glob, html, json, datetime

HERE = os.path.dirname(os.path.abspath(__file__))
BASE_URL = "https://www.databery.com"   # <-- change to your real domain
YEAR = datetime.datetime.now().year

def _ver(rel):
    p = os.path.join(HERE, rel)
    return int(os.path.getmtime(p)) if os.path.exists(p) else 0
CSS_VER = _ver(os.path.join("css", "styles.css"))
JS_VER = _ver(os.path.join("js", "main.js"))

# ---------------------------------------------------------------- brand mark
LOGO = (
 '<svg class="brand-mark" viewBox="0 0 48 48" fill="none" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">'
 '<defs><linearGradient id="dbg" x1="8" y1="42" x2="40" y2="8" gradientUnits="userSpaceOnUse">'
 '<stop stop-color="#1c1b4e"/><stop offset=".5" stop-color="#6324c4"/><stop offset="1" stop-color="#3f5efb"/></linearGradient></defs>'
 '<path d="M23 13c-1-3 0-6 2-8" stroke="#1c1b4e" stroke-width="2" stroke-linecap="round"/>'
 '<path d="M26 12c1.5-4.5 6-6.5 10-5.5.4 4-2 8.5-6.5 9.6-1.8.4-3-.5-3.5-1.6z" fill="url(#dbg)"/>'
 '<g stroke="url(#dbg)" stroke-width="1.4" opacity=".5"><path d="M16 18 24 16M16 18 12 26M24 16 28 24M12 26 20 30M28 24 20 30M20 30 16 38M16 38 26 36M28 24 26 36"/></g>'
 '<g fill="url(#dbg)"><circle cx="16" cy="18" r="3"/><circle cx="24" cy="16" r="3.4"/><circle cx="12" cy="26" r="3.6"/>'
 '<circle cx="28" cy="24" r="3"/><circle cx="20" cy="30" r="4"/><circle cx="16" cy="38" r="3.4"/><circle cx="26" cy="36" r="3"/></g>'
 '<g fill="#3f5efb"><circle cx="34" cy="20" r="1.7"/><circle cx="37.5" cy="26" r="2"/><circle cx="34.5" cy="32" r="1.6"/>'
 '<circle cx="31" cy="38" r="1.3"/><circle cx="38.5" cy="33" r="1.1"/></g></svg>'
)
BRAND = ('<a href="index.html" class="brand">' + LOGO +
         '<span class="brand-text"><span class="t-ink">Data</span><span class="t-grad">bery</span></span></a>')
ARROW = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M5 12h14M13 6l6 6-6 6"/></svg>'
CARET = '<svg class="caret" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="m6 9 6 6 6-6"/></svg>'

def ic(paths):
    return '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7">%s</svg>' % paths

# ---------------------------------------------------------------- services (mega)
SERVICES = [
 ("account-intelligence", "Account Intelligence", "Intent-scored target accounts, signal-rich and ready for outreach.",
  '<circle cx="12" cy="12" r="8"/><circle cx="12" cy="12" r="3.4"/><path d="M12 2v3M12 19v3M2 12h3M19 12h3"/>'),
 ("pipeline-signal-monitoring", "Pipeline Signal Monitoring", "Ongoing buying-trigger monitoring across your account list.",
  '<path d="M3 12h4l2-6 4 12 2-6h6"/>'),
 ("competitive-intelligence", "Competitive Intelligence", "A living view of your top 3-5 competitors and their gaps.",
  '<path d="M12 2 4 6v6c0 5 3.5 8 8 10 4.5-2 8-5 8-10V6Z"/><path d="m9 12 2 2 4-4"/>'),
 ("stakeholder-executive-intelligence", "Stakeholder &amp; Executive Intel", "Profiles of the people you must influence to win the deal.",
  '<path d="M16 7a4 4 0 1 1-8 0 4 4 0 0 1 8 0Z"/><path d="M4 21v-1a6 6 0 0 1 6-6h4a6 6 0 0 1 6 6v1"/>'),
 ("gtm-research", "Go-To-Market Research", "A research-backed foundation for a new market or vertical.",
  '<circle cx="12" cy="12" r="9"/><path d="M3 12h18M12 3a14 14 0 0 1 0 18M12 3a14 14 0 0 0 0 18"/>'),
 ("win-loss-intelligence", "Win-Loss Intelligence", "Why you really won or lost - and what to change next time.",
  '<path d="M7 4h10v4a5 5 0 0 1-10 0V4Z"/><path d="M7 6H4v1a3 3 0 0 0 3 3M17 6h3v1a3 3 0 0 1-3 3M9 18h6M10 14v4M14 14v4"/>'),
 ("battlecard-research", "Battlecard Research", "Live intelligence that powers your sales battlecards.",
  '<path d="M12 3 3 8l9 5 9-5-9-5Z"/><path d="m3 12 9 5 9-5M3 16l9 5 9-5"/>'),
]

# ---------------------------------------------------------------- dropdowns
RESOURCES = [  # href, label, desc, icon
 ("insights.html",          "Blog",             "Field notes from our analysts",        '<path d="M4 4h16v16H4z"/><path d="M8 8h8M8 12h8M8 16h5"/>'),
 ("resources.html#playbooks","CMO Playbooks",   "Strategic guides for revenue leaders",  '<path d="M4 5a2 2 0 0 1 2-2h12v18H6a2 2 0 0 1-2-2z"/><path d="M8 3v18"/>'),
 ("resources.html#ebooks",  "Ebooks &amp; Guides","Deep dives you can download",         '<path d="M12 3 2 8l10 5 10-5z"/><path d="M2 8v6l10 5 10-5V8"/>'),
 ("resources.html#templates","Templates &amp; Tools","Free frameworks to steal",           '<path d="M3 3h7v7H3zM14 3h7v4h-7zM14 11h7v10h-7zM3 14h7v7H3z"/>'),
 ("faq.html",               "FAQ",              "Answers to common questions",          '<circle cx="12" cy="12" r="9"/><path d="M9.6 9a2.4 2.4 0 1 1 3.4 2.2c-.8.4-1 .9-1 1.6"/><path d="M12 17h.01"/>'),
]
ABOUT = [
 ("about.html",   "Who We Are",   "Our story, mission &amp; team",       '<path d="M16 7a4 4 0 1 1-8 0 4 4 0 0 1 8 0Z"/><path d="M4 21v-1a6 6 0 0 1 6-6h4a6 6 0 0 1 6 6v1"/>'),
 ("why.html",     "Why Databery", "What makes us different",          '<path d="M12 2 4 6v6c0 5 3.5 8 8 10 4.5-2 8-5 8-10V6Z"/><path d="m9 12 2 2 4-4"/>'),
 ("process.html", "Our Process",  "How an engagement runs",           '<path d="M4 6h16M4 12h16M4 18h16"/><circle cx="8" cy="6" r="1.4" fill="currentColor"/><circle cx="14" cy="12" r="1.4" fill="currentColor"/><circle cx="10" cy="18" r="1.4" fill="currentColor"/>'),
 ("careers.html", "Careers",      "Join the analyst team",            '<rect x="3" y="7" width="18" height="13" rx="2"/><path d="M8 7V5a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/>'),
]

# ---------------------------------------------------------------- solutions (buyer-centric nav)
SOLUTIONS = [  # href, label, desc, icon  (live in nav — 3 buyer types)
 ("solution-sales-revenue.html",       "Sales &amp; Revenue Teams",       "Know which accounts are buying, and when to move.", '<path d="M3 3v18h18"/><path d="M7 14l3-4 4 3 5-7"/>'),
 ("solution-founders-startups.html",   "Founders &amp; Startups",         "Get targeting &amp; positioning right before you dial.", '<path d="M4 20h16M6 20V8l6-4 6 4v12"/><path d="M10 20v-5h4v5"/>'),
 ("solution-consulting-research.html", "Consulting &amp; Research Firms",  "Senior research capacity, under your brand.", '<circle cx="11" cy="11" r="7"/><path d="m21 21-4.3-4.3"/>'),
]

# Pages kept on disk but hidden from nav, sitemap, and search (noindex).
# - the 2 buyer types to launch later, and the old per-service pages now folded into the buyer pages.
NOINDEX = {
 "solution-private-equity.html", "solution-enterprise-strategy.html",
 "services.html", "use-cases.html",
 "service-account-intelligence.html", "service-pipeline-signal-monitoring.html",
 "service-competitive-intelligence.html", "service-stakeholder-executive-intelligence.html",
 "service-gtm-research.html", "service-win-loss-intelligence.html", "service-battlecard-research.html",
}

# data-page key -> active nav group
GROUP = {
 "home":"home", "solutions":"solutions", "services":"solutions",
 "insights":"resources", "use-cases":"resources", "resources":"resources", "faq":"resources",
 "about":"about", "why":"about", "process":"about", "careers":"about",
 "contact":"contact",
}

def mega_link(slug, name, blurb, icon):
    return ('<a class="mega-link" href="service-%s.html"><span class="mega-ic">%s</span>'
            '<span><strong>%s</strong><em>%s</em></span></a>') % (slug, ic(icon), name, blurb)

def drop_link(href, label, desc, icon):
    return ('<a class="drop-link" href="%s"><span class="drop-ic">%s</span>'
            '<span><strong>%s</strong><em>%s</em></span></a>') % (href, ic(icon), label, desc)

def build_nav(key):
    grp = GROUP.get(key, "")
    # solutions dropdown (buyer-centric)
    sol = '<div class="dropdown">%s</div>' % "".join(drop_link(*s) for s in SOLUTIONS)
    solutions = ('<div class="nav-item has-dropdown%s"><a href="index.html#solutions" class="dropdown-trigger">Solutions %s</a>%s</div>'
                 ) % (" active" if grp == "solutions" else "", CARET, sol)
    # resources dropdown (left aligned)
    res = '<div class="dropdown">%s</div>' % "".join(drop_link(*r) for r in RESOURCES)
    resources = ('<div class="nav-item has-dropdown%s"><a href="insights.html" class="dropdown-trigger">Resources %s</a>%s</div>'
                 ) % (" active" if grp == "resources" else "", CARET, res)
    # about dropdown (right aligned)
    ab = '<div class="dropdown right">%s</div>' % "".join(drop_link(*a) for a in ABOUT)
    about = ('<div class="nav-item has-dropdown%s"><a href="about.html" class="dropdown-trigger">About us %s</a>%s</div>'
             ) % (" active" if grp == "about" else "", CARET, ab)

    home = '<a href="index.html" class="%s">Home</a>' % ("active" if grp == "home" else "")
    contact = '<a href="contact.html" class="%s">Contact</a>' % ("active" if grp == "contact" else "")
    links = home + solutions + resources + about + contact
    return (
     '<header class="nav"><div class="container nav-inner">' + BRAND +
     '<nav class="nav-links" aria-label="Primary">' + links + '</nav>'
     '<div class="nav-cta"><a href="contact.html" class="btn btn-primary" data-magnetic>Book a call ' + ARROW + '</a></div>'
     '<button class="nav-toggle" aria-label="Toggle menu" aria-expanded="false"><span></span><span></span></button>'
     '</div></header>'
    )

def build_footer():
    foot_solutions = "".join('<li><a href="%s">%s</a></li>' % (s[0], s[1]) for s in SOLUTIONS)
    return (
     '<footer class="footer"><div class="container">'
     '<div class="footer-top">'
     '<div>' + BRAND +
     '<p class="about">Account &amp; sales intelligence that turns target lists into closed revenue - researched account by account.</p>'
     '<div class="tagline-chip" style="margin-top:22px"><b>Insights</b> &middot; <b>Intelligence</b> &middot; <b>Impact</b></div>'
     '<p style="margin-top:20px;font-size:.88rem"><a href="mailto:hello@databery.com" style="color:var(--muted)">hello@databery.com</a></p></div>'
     '<div><h5>Solutions</h5><ul>' + foot_solutions + '</ul></div>'
     '<div><h5>Company</h5><ul>'
     '<li><a href="about.html">Who we are</a></li><li><a href="why.html">Why Databery</a></li>'
     '<li><a href="process.html">Our process</a></li><li><a href="careers.html">Careers</a></li>'
     '<li><a href="contact.html">Contact</a></li></ul></div>'
     '<div><h5>Resources</h5><ul>'
     '<li><a href="insights.html">Blog</a></li>'
     '<li><a href="resources.html#playbooks">CMO playbooks</a></li><li><a href="resources.html#templates">Templates</a></li>'
     '<li><a href="faq.html">FAQ</a></li></ul></div></div>'
     '<div class="footer-bottom"><div class="footer-legal">'
     '<span>&copy; ' + str(YEAR) + ' Databery. All rights reserved.</span>'
     '<a href="privacy.html">Privacy</a><a href="cookies.html">Cookies</a></div>'
     '<div class="socials">'
     '<a href="#" aria-label="LinkedIn"><svg viewBox="0 0 24 24" width="16" fill="currentColor"><path d="M4.98 3.5A2.5 2.5 0 1 1 0 3.5a2.5 2.5 0 0 1 4.98 0ZM.5 8h4V24h-4V8Zm7 0h3.8v2.2h.05c.53-1 1.83-2.2 3.77-2.2 4 0 4.8 2.65 4.8 6.1V24h-4v-6.9c0-1.65-.03-3.77-2.3-3.77-2.3 0-2.65 1.8-2.65 3.65V24h-4V8Z"/></svg></a>'
     '<a href="#" aria-label="X"><svg viewBox="0 0 24 24" width="15" fill="currentColor"><path d="M18.9 2H22l-7.1 8.1L23.2 22h-6.6l-5.2-6.8L5.5 22H2.4l7.6-8.7L1.2 2h6.7l4.7 6.2L18.9 2Zm-1.1 18h1.8L7.3 3.9H5.4L17.8 20Z"/></svg></a>'
     '<a href="#" aria-label="Instagram"><svg viewBox="0 0 24 24" width="16" fill="none" stroke="currentColor" stroke-width="2"><rect x="2" y="2" width="20" height="20" rx="5.5"/><circle cx="12" cy="12" r="4"/><circle cx="17.5" cy="6.5" r="1.1" fill="currentColor" stroke="none"/></svg></a>'
     '<a href="#" aria-label="Email"><svg viewBox="0 0 24 24" width="16" fill="none" stroke="currentColor" stroke-width="2"><rect x="2" y="4" width="20" height="16" rx="2"/><path d="m2 6 10 7 10-7"/></svg></a>'
     '</div></div></div></footer>'
    )

ORG_JSONLD = (
 '<script type="application/ld+json">{"@context":"https://schema.org","@type":"Organization",'
 '"name":"Databery","url":"%s","description":"Account & sales intelligence firm that researches target accounts for B2B revenue teams.",'
 '"email":"hello@databery.com","slogan":"Insights. Intelligence. Impact.",'
 '"sameAs":["https://www.linkedin.com/company/databery"]}</script>' % BASE_URL
)

def faq_schema(text):
    qs = re.findall(r'<button class="faq-q">(.*?)\s*<span class="pm">', text, re.S)
    ans = re.findall(r'<div class="faq-a"><p>(.*?)</p>\s*</div>', text, re.S)
    items = []
    for q, a in zip(qs, ans):
        qt = re.sub(r'<[^>]+>', '', q).strip()
        at = re.sub(r'<[^>]+>', '', a).strip()
        if qt and at:
            items.append('{"@type":"Question","name":%s,"acceptedAnswer":{"@type":"Answer","text":%s}}'
                         % (json.dumps(qt), json.dumps(at)))
    if not items:
        return ""
    return ('<script type="application/ld+json">{"@context":"https://schema.org",'
            '"@type":"FAQPage","mainEntity":[%s]}</script>' % ",".join(items))

def meta_value(text, name):
    m = re.search(r'<meta\s+name="%s"\s+content="(.*?)"' % name, text, re.S)
    return m.group(1).strip() if m else ""

def build_seo(fname, text):
    title = ""
    tm = re.search(r"<title>(.*?)</title>", text, re.S)
    if tm: title = html.unescape(tm.group(1).strip())
    desc = html.unescape(meta_value(text, "description"))
    url = BASE_URL + "/" + fname
    is_article = fname.startswith("insight-")
    og_type = "article" if is_article else "website"
    img = BASE_URL + "/assets/img/og-card.jpg"
    ov = re.search(r'<meta name="x-og-image" content="(.*?)"', text)   # per-page OG image (articles)
    if ov:
        img = ov.group(1)
    parts = [
     '<link rel="canonical" href="%s"/>' % url,
     '<link rel="alternate" type="application/rss+xml" title="Databery Blog" href="%s/rss.xml"/>' % BASE_URL,
     '<link rel="apple-touch-icon" href="assets/img/apple-touch-icon.png"/>',
     '<meta name="theme-color" content="#6324c4"/>',
     '<meta property="og:type" content="%s"/>' % og_type,
     '<meta property="og:site_name" content="Databery"/>',
     '<meta property="og:title" content="%s"/>' % html.escape(title, quote=True),
     '<meta property="og:description" content="%s"/>' % html.escape(desc, quote=True),
     '<meta property="og:url" content="%s"/>' % url,
     '<meta property="og:image" content="%s"/>' % img,
     '<meta property="og:image:width" content="1200"/>',
     '<meta property="og:image:height" content="630"/>',
     '<meta property="og:image:alt" content="Databery — Account &amp; Sales Intelligence"/>',
     '<meta name="twitter:card" content="summary_large_image"/>',
     '<meta name="twitter:title" content="%s"/>' % html.escape(title, quote=True),
     '<meta name="twitter:description" content="%s"/>' % html.escape(desc, quote=True),
     '<meta name="twitter:image" content="%s"/>' % img,
     ORG_JSONLD,
    ]
    # NOTE: article (BlogPosting) JSON-LD is embedded by the Markdown blog generator
    # (render_article) with full author/date/image data, so it is not added here.
    if fname == "faq.html":
        fs = faq_schema(text)
        if fs:
            parts.append(fs)
    if fname in NOINDEX:
        parts.insert(0, '<meta name="robots" content="noindex"/>')
    return "".join(parts)

def replace_region(text, start, end, payload, fallback_pat):
    block = "<!--%s-->%s<!--%s-->" % (start, payload, end)
    pat = re.compile(re.escape("<!--%s-->" % start) + ".*?" + re.escape("<!--%s-->" % end), re.S)
    if pat.search(text):
        return pat.sub(lambda m: block, text)
    if fallback_pat:
        fp = re.compile(fallback_pat, re.S)
        if fp.search(text):
            return fp.sub(lambda m: block, text, count=1)
    return text

def page_key(text):
    m = re.search(r'data-page="([\w-]+)"', text)
    key = m.group(1) if m else ""
    if key.startswith("insight"): return "insights"
    return key

def process(path):
    fname = os.path.basename(path)
    with open(path, "r", encoding="utf-8") as f:
        text = f.read()
    key = page_key(text)
    text = replace_region(text, "NAV", "/NAV", build_nav(key), r'<div id="site-header"></div>')
    text = replace_region(text, "FOOTER", "/FOOTER", build_footer(), r'<div id="site-footer"></div>')
    seo = build_seo(fname, text)
    if re.search(r"<!--SEO-->.*?<!--/SEO-->", text, re.S):
        text = replace_region(text, "SEO", "/SEO", seo, None)
    else:
        text = text.replace("</head>", "<!--SEO-->" + seo + "<!--/SEO-->\n</head>", 1)
    text = re.sub(r'\s*<script src="js/components\.js"></script>', "", text)
    # cache-bust CSS + JS so browsers always pick up changes after a build
    text = re.sub(r'href="css/styles\.css(?:\?v=\d+)?"', 'href="css/styles.css?v=%d"' % CSS_VER, text)
    text = re.sub(r'src="js/main\.js(?:\?v=\d+)?"', 'src="js/main.js?v=%d"' % JS_VER, text)
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)
    return fname, key

# ================================================================ BLOG (Markdown)
POSTS_DIR = os.path.join(HERE, "posts")
PER_PAGE = 10  # client-side pagination size (kicks in above this many posts)
FAVICON = ("assets/img/logo_image.png")
MONTHS = ['January','February','March','April','May','June','July','August',
          'September','October','November','December']

def slugify(s):
    return re.sub(r'[^a-z0-9]+', '-', s.lower()).strip('-')

def initials(name):
    parts = [p for p in re.split(r'\s+', name.strip()) if p]
    if not parts: return "DB"
    if len(parts) == 1: return parts[0][:2].upper()
    return (parts[0][0] + parts[1][0]).upper()

# ---- minimal, dependency-free Markdown -> HTML ----
def _inline(s):
    s = s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
    s = re.sub(r'!\[([^\]]*)\]\(([^)]+)\)', r'<img src="\2" alt="\1" loading="lazy" />', s)
    s = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2">\1</a>', s)
    s = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', s)
    s = re.sub(r'(?<!\*)\*([^*\n]+)\*(?!\*)', r'<em>\1</em>', s)
    s = re.sub(r'`([^`]+)`', r'<code>\1</code>', s)
    return s

def md_to_html(md):
    lines = md.replace('\r\n', '\n').split('\n')
    out, i, n = [], 0, len(lines)
    block_start = re.compile(r'^(#{1,4}\s|>|[-*]\s|\d+\.\s|```|-{3,}$|\*{3,}$)')
    while i < n:
        stripped = lines[i].strip()
        if not stripped:
            i += 1; continue
        if stripped.startswith('```'):
            i += 1; code = []
            while i < n and not lines[i].strip().startswith('```'):
                code.append(lines[i]); i += 1
            i += 1
            esc = '\n'.join(code).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
            out.append('<pre><code>%s</code></pre>' % esc); continue
        if re.match(r'^(-{3,}|\*{3,})$', stripped):
            out.append('<hr />'); i += 1; continue
        m = re.match(r'^(#{1,4})\s+(.*)$', stripped)
        if m:
            lvl = len(m.group(1)); out.append('<h%d>%s</h%d>' % (lvl, _inline(m.group(2).strip()), lvl)); i += 1; continue
        if stripped.startswith('>'):
            buf = []
            while i < n and lines[i].strip().startswith('>'):
                buf.append(re.sub(r'^\s*>\s?', '', lines[i]).strip()); i += 1
            out.append('<blockquote><p>%s</p></blockquote>' % _inline(' '.join(buf))); continue
        if re.match(r'^[-*]\s+', stripped):
            items = []
            while i < n and re.match(r'^[-*]\s+', lines[i].strip()):
                items.append('<li>%s</li>' % _inline(re.sub(r'^[-*]\s+', '', lines[i].strip()))); i += 1
            out.append('<ul>%s</ul>' % ''.join(items)); continue
        if re.match(r'^\d+\.\s+', stripped):
            items = []
            while i < n and re.match(r'^\d+\.\s+', lines[i].strip()):
                items.append('<li>%s</li>' % _inline(re.sub(r'^\d+\.\s+', '', lines[i].strip()))); i += 1
            out.append('<ol>%s</ol>' % ''.join(items)); continue
        if re.match(r'^!\[[^\]]*\]\([^)]+\)$', stripped):
            out.append('<figure class="prose-figure">%s</figure>' % _inline(stripped)); i += 1; continue
        buf = []
        while i < n and lines[i].strip() and not block_start.match(lines[i].strip()):
            buf.append(lines[i].strip()); i += 1
        out.append('<p>%s</p>' % _inline(' '.join(buf)))
    return '\n'.join(out)

def parse_frontmatter(raw):
    lines = raw.replace('\r\n', '\n').split('\n')
    meta, body_start = {}, 0
    if lines and lines[0].strip() == '---':
        end = next((idx for idx in range(1, len(lines)) if lines[idx].strip() == '---'), None)
        if end is not None:
            for ln in lines[1:end]:
                if ':' not in ln: continue
                k, v = ln.split(':', 1); k, v = k.strip(), v.strip()
                if not k: continue
                if k == 'tags':
                    v = v.strip('[]')
                    meta[k] = [t.strip().strip('"\'') for t in v.split(',') if t.strip()]
                else:
                    meta[k] = v.strip('"\'')
            body_start = end + 1
    return meta, '\n'.join(lines[body_start:]).strip('\n')

def load_posts():
    posts = []
    for path in glob.glob(os.path.join(POSTS_DIR, "*.md")):
        meta, body = parse_frontmatter(open(path, encoding="utf-8").read())
        if str(meta.get('draft', '')).lower() == 'true':
            continue
        slug = os.path.splitext(os.path.basename(path))[0]
        try:
            d = datetime.datetime.strptime(meta.get('date', ''), '%Y-%m-%d')
        except ValueError:
            d = datetime.datetime.now()
        author = meta.get('author', 'Databery Team')
        cat = meta.get('category', 'Insights')
        words = len(re.findall(r'\w+', body))
        tags = meta.get('tags', [])
        posts.append({
            'slug': slug, 'file': 'insight-%s.html' % slug,
            'title': meta.get('title', slug),
            'date': d,
            'date_display': '%s %d, %d' % (MONTHS[d.month - 1], d.day, d.year),
            'date_iso': d.strftime('%Y-%m-%d'),
            'date_rfc': d.strftime('%a, %d %b %Y 09:00:00 +0000'),
            'author': author, 'initials': initials(author),
            'category': cat, 'cat_slug': slugify(cat),
            'description': meta.get('description', ''),
            'image': meta.get('featured_image', 'assets/img/hero-abstract.jpg'),
            'tags': tags if isinstance(tags, list) else [],
            'body_html': md_to_html(body),
            'read': max(1, round(words / 200)),
        })
    posts.sort(key=lambda p: p['date'], reverse=True)
    return posts

def page_head(title, desc, extra=""):
    e = lambda s: html.escape(s, quote=True)
    return (
'<!DOCTYPE html>\n<html lang="en">\n<head>\n'
'  <meta charset="UTF-8" />\n'
'  <meta name="viewport" content="width=device-width, initial-scale=1.0" />\n'
f'  <title>{e(title)}</title>\n'
f'  <meta name="description" content="{e(desc)}" />\n'
'  <link rel="preconnect" href="https://fonts.googleapis.com" />\n'
'  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />\n'
'  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=Space+Grotesk:wght@400;500;600;700&display=swap" rel="stylesheet" />\n'
'  <link rel="stylesheet" href="css/styles.css" />\n'
f'  <link rel="icon" href="{FAVICON}" />\n'
f'{extra}</head>\n')

PAGE_TOP = ('<body data-page="insights">\n'
            '  <div class="scroll-bar"></div>\n  <div class="cursor-dot"></div>\n  <div class="cursor-ring"></div>\n\n'
            '  <div id="site-header"></div>\n')
PAGE_END = '\n  <div id="site-footer"></div>\n\n  <script src="js/main.js"></script>\n</body>\n</html>\n'

def post_card(p, delay=""):
    e = lambda s: html.escape(s, quote=True)
    tags = e(' '.join(p['tags']) + ' ' + p['category'])
    dl = f' data-delay="{delay}"' if delay else ''
    return (f'<a class="post-card reveal"{dl} data-cat="{p["cat_slug"]}" data-title="{e(p["title"])}" data-tags="{tags}" href="{p["file"]}">'
            f'<div class="post-thumb"><img src="{p["image"]}" alt="{e(p["title"])}" loading="lazy" width="1400" height="875" /></div>'
            f'<div class="post-body"><div class="post-cat">{e(p["category"])}</div>'
            f'<h3>{e(p["title"])}</h3><p>{e(p["description"])}</p>'
            f'<div class="post-meta">{e(p["author"])} &middot; {p["read"]} min read</div></div></a>')

def pick_related(post, posts):
    same = [p for p in posts if p['slug'] != post['slug'] and p['cat_slug'] == post['cat_slug']]
    other = [p for p in posts if p['slug'] != post['slug'] and p['cat_slug'] != post['cat_slug']]
    return (same + other)[:3]

CTA_BLOCK = (
 '\n  <section class="container section-pad" style="padding-top:0">\n'
 '    <div class="cta-band reveal">\n'
 '      <h2>Want intelligence like this<br />on your real accounts?</h2>\n'
 '      <p>Book a free 30-minute call and we\'ll research one of your target accounts live.</p>\n'
 '      <div class="hero-actions">\n'
 '        <a href="contact.html" class="btn btn-primary" data-magnetic>Book a call '
 '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M5 12h14M13 6l6 6-6 6"/></svg></a>\n'
 '        <a href="insights.html" class="btn btn-ghost" data-magnetic>More insights</a>\n'
 '      </div>\n    </div>\n  </section>\n')

def render_article(post, related):
    e = lambda s: html.escape(s, quote=True)
    abs_img = BASE_URL + "/" + post['image']
    ld = {
        "@context": "https://schema.org", "@type": "BlogPosting",
        "headline": post['title'], "description": post['description'],
        "image": abs_img, "datePublished": post['date_iso'], "dateModified": post['date_iso'],
        "author": {"@type": "Organization", "name": post['author']},
        "publisher": {"@type": "Organization", "name": "Databery",
                      "logo": {"@type": "ImageObject", "url": BASE_URL + "/assets/img/apple-touch-icon.png"}},
        "mainEntityOfPage": BASE_URL + "/" + post['file'],
        "keywords": ", ".join(post['tags']),
    }
    head_extra = f'  <meta name="x-og-image" content="{abs_img}" />\n'
    rel = ""
    if related:
        cards = "".join(post_card(r) for r in related)
        rel = ('\n  <section class="container section-pad" style="padding-top:0">\n'
               '    <div class="sec-head reveal"><span class="eyebrow">Keep reading</span><h2>Related articles</h2></div>\n'
               f'    <div class="post-grid">{cards}</div>\n  </section>\n')
    body = (PAGE_TOP +
 '\n  <section class="page-hero article-hero">\n    <div class="hero-orb"></div>\n    <div class="container article">\n'
 f'      <div class="breadcrumb reveal"><a href="index.html">Home</a> &middot; <a href="insights.html">Blog</a> &middot; {e(post["category"])}</div>\n'
 f'      <span class="eyebrow reveal">{e(post["category"])}</span>\n'
 f'      <h1 class="reveal" data-delay="1">{e(post["title"])}</h1>\n'
 f'      <div class="article-meta reveal" data-delay="2"><span class="tst-avatar">{post["initials"]}</span> {e(post["author"])} &middot; {post["date_display"]} &middot; {post["read"]} min read</div>\n'
 '    </div>\n  </section>\n\n'
 '  <section class="container" style="padding-bottom:clamp(64px,9vw,110px)">\n    <div class="article">\n'
 f'      <div class="article-cover reveal"><img src="{post["image"]}" alt="{e(post["title"])}" loading="lazy" width="1400" height="600" /></div>\n'
 f'      <div class="prose reveal" style="margin-top:36px">\n{post["body_html"]}\n      </div>\n    </div>\n  </section>\n'
 + rel + CTA_BLOCK +
 f'  <script type="application/ld+json">{json.dumps(ld)}</script>\n' +
 PAGE_END)
    return page_head(post['title'] + " — Databery", post['description'], head_extra) + body

NEWSLETTER_BLOCK = (
 '\n  <section class="container section-pad" style="padding-top:0">\n'
 '    <div class="newsletter reveal">\n'
 '      <span class="eyebrow" style="justify-content:center">The signal, monthly</span>\n'
 '      <h3 style="margin-top:14px">One sharp idea on account intelligence, once a month.</h3>\n'
 '      <p>No fluff, no spam — just what\'s working in B2B research and outbound. Unsubscribe anytime.</p>\n'
 '      <form class="news-form" id="news-form" action="https://api.web3forms.com/submit" method="POST">\n'
 '        <input type="hidden" name="access_key" value="47ae131a-cdfa-4fd4-b47d-8493f4a99dc0" />\n'
 '        <input type="hidden" name="subject" value="New newsletter subscriber — Databery" />\n'
 '        <input type="hidden" name="from_name" value="Databery Newsletter" />\n'
 '        <input type="checkbox" name="botcheck" tabindex="-1" autocomplete="off" aria-hidden="true" style="display:none !important" />\n'
 '        <input type="email" name="email" placeholder="you@company.com" aria-label="Email address" autocomplete="email" required />\n'
 '        <button type="submit" class="btn btn-primary" data-magnetic>Subscribe '
 '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M5 12h14M13 6l6 6-6 6"/></svg></button>\n'
 '      </form>\n'
 '      <p class="form-msg" id="news-msg" role="alert" aria-live="assertive" style="max-width:470px;margin:14px auto 0"></p>\n'
 '    </div>\n  </section>\n')

def render_index(posts, cats):
    e = lambda s: html.escape(s, quote=True)
    chips = '<button class="chip active" data-cat="all">All</button>' + "".join(
        f'<button class="chip" data-cat="{cs}">{e(cn)}</button>' for cs, cn in cats)
    cards = "".join(post_card(p, delay=str((idx % 3) + 1)) for idx, p in enumerate(posts))
    desc = "Field notes on account intelligence, buying signals, and modern B2B sales research from the Databery analyst team. Search and filter our latest articles."
    body = (PAGE_TOP +
 '\n  <section class="page-hero">\n    <div class="hero-orb"></div>\n    <div class="container">\n'
 '      <div class="breadcrumb reveal"><a href="index.html">Home</a> &middot; <a href="resources.html">Resources</a> &middot; Blog</div>\n'
 '      <span class="eyebrow reveal">The blog</span>\n'
 '      <h1 class="reveal" data-delay="1">Field notes on <span class="gradient-text">account intelligence &amp; modern selling.</span></h1>\n'
 '      <p class="lead reveal" data-delay="2">Practical thinking from our analysts on buying signals, account research, and how revenue teams win complex deals.</p>\n'
 '    </div>\n  </section>\n\n'
 '  <section class="section-pad" style="padding-top:clamp(36px,5vw,64px)">\n    <div class="container">\n'
 '      <div class="blog-toolbar reveal">\n'
 '        <div class="search-box"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="7"/><path d="m21 21-4.3-4.3"/></svg>'
 '<input id="blog-search" type="search" placeholder="Search articles…" aria-label="Search articles" /></div>\n'
 f'        <div class="cat-chips">{chips}</div>\n      </div>\n'
 f'      <div class="blog-count" id="blog-count">{len(posts)} articles</div>\n'
 f'      <div class="post-grid" id="blog-list">{cards}</div>\n'
 '      <div class="no-results" id="blog-empty"><h3 style="margin-bottom:8px">No articles found</h3><p>Try a different search or category.</p></div>\n'
 '      <div class="pagination" id="blog-pagination"></div>\n'
 '    </div>\n  </section>\n'
 + NEWSLETTER_BLOCK + PAGE_END)
    return page_head("Blog — Databery", desc, "") + body

def render_rss(posts):
    x = lambda s: html.escape(s)
    now = datetime.datetime.now(datetime.timezone.utc).strftime('%a, %d %b %Y %H:%M:%S +0000')
    items = ""
    for p in posts:
        link = BASE_URL + "/" + p['file']
        items += (f'<item><title>{x(p["title"])}</title><link>{link}</link>'
                  f'<guid isPermaLink="true">{link}</guid><pubDate>{p["date_rfc"]}</pubDate>'
                  f'<category>{x(p["category"])}</category>'
                  f'<description>{x(p["description"])}</description></item>')
    return ('<?xml version="1.0" encoding="UTF-8"?>\n'
            '<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom"><channel>'
            '<title>Databery Blog</title>'
            f'<link>{BASE_URL}/insights.html</link>'
            f'<atom:link href="{BASE_URL}/rss.xml" rel="self" type="application/rss+xml"/>'
            '<description>Field notes on account &amp; sales intelligence from Databery.</description>'
            f'<language>en-us</language><lastBuildDate>{now}</lastBuildDate>'
            + items + '</channel></rss>\n')

def generate_blog(posts):
    # remove previously generated article pages so deleted posts don't linger
    for p in glob.glob(os.path.join(HERE, "insight-*.html")):
        os.remove(p)
    for post in posts:
        with open(os.path.join(HERE, post['file']), "w", encoding="utf-8") as f:
            f.write(render_article(post, pick_related(post, posts)))
    cats, seen = [], set()
    for p in posts:
        if p['cat_slug'] not in seen:
            seen.add(p['cat_slug']); cats.append((p['cat_slug'], p['category']))
    with open(os.path.join(HERE, "insights.html"), "w", encoding="utf-8") as f:
        f.write(render_index(posts, cats))
    with open(os.path.join(HERE, "rss.xml"), "w", encoding="utf-8") as f:
        f.write(render_rss(posts))
    return posts

def main():
    posts = generate_blog(load_posts())
    pages = sorted(glob.glob(os.path.join(HERE, "*.html")))
    done = [process(p) for p in pages]
    no_index = {"404.html"} | NOINDEX
    urls = "".join('<url><loc>%s/%s</loc><changefreq>weekly</changefreq></url>' % (BASE_URL, os.path.basename(p))
                   for p in pages if os.path.basename(p) not in no_index)
    with open(os.path.join(HERE, "sitemap.xml"), "w", encoding="utf-8") as f:
        f.write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">' + urls + '</urlset>\n')
    with open(os.path.join(HERE, "robots.txt"), "w", encoding="utf-8") as f:
        f.write("User-agent: *\nAllow: /\nSitemap: %s/sitemap.xml\n" % BASE_URL)
    print("Built %d pages (%d blog posts):" % (len(done), len(posts)))
    for fname, key in done:
        print("  %-46s [%s]" % (fname, key or "-"))
    print("Wrote sitemap.xml + robots.txt + rss.xml")

if __name__ == "__main__":
    main()

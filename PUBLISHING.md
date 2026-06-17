# Publishing a new article

The Databery blog is **Markdown-driven**. To publish, you write one Markdown file and run the build — everything else (the article page, blog index, category filters, related articles, RSS feed, sitemap, and SEO schema) is generated automatically.

There are **no external dependencies** — `build.py` is pure Python 3, so it runs anywhere (including the Cloudflare Pages build environment) with nothing to install.

---

## TL;DR — publish in 3 steps

1. Create a file in **`/posts`**, e.g. `posts/my-new-article.md`, with frontmatter + Markdown body (see below).
2. Run the build:
   ```bash
   python build.py
   ```
3. Commit and push. Cloudflare Pages deploys automatically.

The file name becomes the URL: `posts/my-new-article.md` → **`insight-my-new-article.html`**.

---

## 1. Frontmatter (required at the top of every post)

```markdown
---
title: The 7 buying signals that actually predict a deal
date: 2026-06-02
author: Databery Team
category: Buying signals
description: A one-sentence summary used for SEO, the card, and social sharing.
featured_image: assets/img/pipeline-monitoring.jpg
tags: [intent, triggers, outbound]
---
```

| Field | Required | Notes |
|---|---|---|
| `title` | ✅ | Article headline (also the `<h1>` and `<title>`). |
| `date` | ✅ | `YYYY-MM-DD`. Controls ordering (newest first) and RSS/schema dates. |
| `author` | ✅ | e.g. `Databery Team`. Initials are auto-generated for the avatar. |
| `category` | ✅ | Free text, e.g. `Strategy`. A filter chip is created automatically. |
| `description` | ✅ | 1–2 sentences. Used in the card, meta description, OG tags, and RSS. |
| `featured_image` | ✅ | Site-relative path, e.g. `assets/img/gtm.jpg`. Used for the cover, card thumbnail, and the article's social share image. |
| `tags` | optional | `[tag1, tag2]` — used for search and schema keywords. |
| `draft` | optional | `draft: true` excludes the post from the build (write ahead, publish later). |

> Put your images in `assets/img/`. To add a fresh image, drop the file in that folder and reference it in `featured_image`.

---

## 2. Writing the body (supported Markdown)

Everything below the second `---` is the article body. Supported syntax:

- `## Heading` and `### Subheading`
- Paragraphs (blank line between them)
- **`**bold**`**, *`*italic*`*, `` `inline code` ``
- `[link text](services.html)` or full URLs
- Bullet lists (`- item`) and numbered lists (`1. item`)
- `> Blockquote` (great for pull-quotes)
- `![alt text](assets/img/example.jpg)` for in-body images
- Fenced code blocks with triple backticks
- `---` for a horizontal divider

Links, headings, lists, and quotes are all styled to match the site automatically — don't add inline styles.

---

## 3. What gets generated automatically

Running `python build.py` regenerates:

- **`insight-<slug>.html`** — the full article page (hero, cover, prose, related articles, CTA), with the shared nav/footer and **BlogPosting schema** (author, date, image, keywords) for rich results.
- **`insights.html`** — the blog index: a card per post, **category filter chips** (built from the categories you used), live search, and a result count.
- **Related articles** — up to 3 per article, same category first, then most recent.
- **`rss.xml`** — a valid RSS 2.0 feed of all posts (linked from every page's `<head>`).
- **`sitemap.xml`** — refreshed to include every article + the index.
- **Pagination** — kicks in automatically once there are **more than 10** posts (10 per page, works alongside search/filter).

To **unpublish/delete** a post: delete its `.md` file and run the build — the old HTML is cleaned up automatically.

---

## 4. Cloudflare Pages deployment

Because `build.py` has zero dependencies, you have two equally valid options:

### Option A — Cloudflare builds it (recommended)
In your Cloudflare Pages project settings:

| Setting | Value |
|---|---|
| Framework preset | **None** |
| Build command | `python3 build.py` |
| Build output directory | `/` (root) |

Then publishing is simply: **add a `.md` file → `git push`**. Cloudflare runs the build and deploys. (The `404.html`, `sitemap.xml`, `robots.txt`, and `rss.xml` are all served correctly by Cloudflare Pages as-is.)

### Option B — Build locally, push static files
Set the build command to empty (or `: `) and output directory to `/`. Then your flow is:
```bash
# add posts/my-article.md
python build.py
git add . && git commit -m "New post: my article" && git push
```

**Before your first deploy:** open `build.py` and set `BASE_URL` to your real domain (it's currently `https://www.databery.com`). That value is used for canonical URLs, OG tags, the sitemap, and the RSS feed.

---

## Quick reference

```bash
python build.py        # regenerate the whole site (blog + pages + sitemap + rss)
python make_assets.py  # regenerate the OG share image / icons and recompress photos
```

Folder map:
```
posts/            ← your Markdown articles (the only thing you edit to publish)
build.py          ← generator (blog + nav/footer/SEO injection)
css/ js/ assets/  ← design system, scripts, images
insight-*.html    ← generated article pages (do not edit by hand)
insights.html     ← generated blog index (do not edit by hand)
rss.xml sitemap.xml robots.txt  ← generated
```

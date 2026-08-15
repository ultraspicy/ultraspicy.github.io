# ed25519.io

Personal blog, built with [Astro](https://astro.build) and deployed to GitHub
Pages at [ed25519.io](https://ed25519.io).

## Writing

Articles live in **`src/content/blog/`** — one Markdown file per post. The
filename becomes the URL (`my-post.md` → `/blog/my-post/`).

Each file starts with frontmatter:

```markdown
---
title: My Post Title
description: A one-line summary (optional).
pubDate: 2026-08-15
tags: [notes, rust]
draft: false
---

Your content here…
```

| Field         | Required | Notes                                            |
| ------------- | -------- | ------------------------------------------------ |
| `title`       | yes      | Post title.                                      |
| `pubDate`     | yes      | Publish date, `YYYY-MM-DD`.                      |
| `description` | no       | Shown on the home page and in the RSS feed.      |
| `tags`        | no       | List, e.g. `[a, b]`. Defaults to empty.          |
| `updatedDate` | no       | Optional "last updated" date.                    |
| `draft`       | no       | `true` hides it from listings. Defaults `false`. |

Scaffold a new post quickly:

```bash
npm run new "My Post Title"
```

## Local development

```bash
npm install      # first time only
npm run dev      # http://localhost:4321
npm run build    # production build into dist/
npm run preview  # preview the production build
```

## Customizing

- Site title, description, and nav links: `src/consts.ts`
- About page: `src/pages/about.astro`
- Styles: `src/styles/global.css`
- Favicon: `public/favicon.svg`

## Deployment

Pushing to `main` triggers `.github/workflows/deploy.yml`, which builds the site
and publishes it to GitHub Pages. See `SETUP.md` for the one-time setup to get
the domain and Pages connected.

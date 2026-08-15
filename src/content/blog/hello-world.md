---
title: Hello, world
description: The first post — and a quick tour of how to write here.
pubDate: 2026-08-15
tags: [meta]
draft: true
---

Welcome to the blog. This first post doubles as a cheat sheet for writing new ones.

## Writing a post

Every article is a Markdown file in `src/content/blog/`. The block at the top
(between the `---` lines) is **frontmatter** — metadata about the post:

- `title` — required.
- `description` — optional; shown on the home page and in RSS.
- `pubDate` — required; the publish date, e.g. `2026-08-15`.
- `tags` — optional list, e.g. `[rust, notes]`.
- `draft` — set to `true` to keep a post out of listings while you work on it.

The filename becomes the URL: `hello-world.md` is served at `/blog/hello-world/`.

## Formatting

You get all the usual Markdown: **bold**, *italics*, [links](https://ed25519.io),
lists, blockquotes, and images.

> Blockquotes look like this.

Code blocks are syntax-highlighted:

```js
const keypair = generateKeypair('ed25519');
console.log(keypair.publicKey);
```

## Images and diagrams

Export your diagram from Lucidchart (**File → Download As → SVG**, or PNG),
drop the file in `src/content/blog/images/`, and reference it with a **relative**
path. Astro optimizes anything referenced this way:

![A simple system diagram](./images/system-diagram.svg)

```markdown
![A simple system diagram](./images/system-diagram.svg)
```

That's it. Add a new file, write, commit, push — it's live.

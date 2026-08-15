#!/usr/bin/env node
// Usage: npm run new "My Post Title"
import { writeFile, mkdir } from 'node:fs/promises';
import { existsSync } from 'node:fs';
import { join } from 'node:path';

const title = process.argv.slice(2).join(' ').trim();
if (!title) {
  console.error('Usage: npm run new "My Post Title"');
  process.exit(1);
}

const slug = title
  .toLowerCase()
  .replace(/[^a-z0-9]+/g, '-')
  .replace(/^-+|-+$/g, '');

const dir = join(process.cwd(), 'src', 'content', 'blog');
const file = join(dir, `${slug}.md`);

if (existsSync(file)) {
  console.error(`A post already exists at ${file}`);
  process.exit(1);
}

const today = new Date().toISOString().slice(0, 10);
const frontmatter = `---
title: ${title}
description:
pubDate: ${today}
tags: []
draft: true
---

Write your post here.
`;

await mkdir(dir, { recursive: true });
await writeFile(file, frontmatter);
console.log(`Created src/content/blog/${slug}.md`);

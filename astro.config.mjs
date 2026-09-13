// @ts-check
import { defineConfig } from 'astro/config';
import sitemap from '@astrojs/sitemap';

// https://astro.build/config
export default defineConfig({
  // Your production URL. Update this if you use a different domain.
  site: 'https://ultraspicy.github.io',
  integrations: [sitemap()],
  markdown: {
    shikiConfig: {
      // Code block themes for light and dark mode.
      themes: {
        light: 'github-light',
        dark: 'github-dark',
      },
    },
  },
});

import { defineConfig } from 'vite';
import handlebars from 'vite-plugin-handlebars';
import { resolve } from 'path';

// Static portfolio site. Compiles to dist/ which nginx serves as-is — no backend.
// Partials live in partials/ and are pulled in with {{> name }}; per-page meta
// (title/description/canonical) comes from the context lookup below.
const pageData = {
  '/index.html': {
    title: 'Paul — self-hosted, containerized tools',
    description:
      'Paul (parmati94) builds self-hosted, containerized tools — playlist AI, game-server dashboards, save viewers — all shipped as Docker containers.',
    canonical: 'https://parmati.me/',
    isHome: true,
  },
  '/resume.html': {
    title: 'Resume — Paul',
    description: "Paul's resume — view online or download the PDF.",
    canonical: 'https://parmati.me/resume',
    isHome: false,
  },
};

export default defineConfig({
  root: './',
  publicDir: 'public',
  plugins: [
    handlebars({
      partialDirectory: resolve(__dirname, 'partials'),
      context(pagePath) {
        return pageData[pagePath];
      },
    }),
  ],
  build: {
    outDir: 'dist',
    emptyOutDir: true,
    minify: 'esbuild',
    sourcemap: false,
    rollupOptions: {
      input: {
        main: resolve(__dirname, 'index.html'),
        resume: resolve(__dirname, 'resume.html'),
      },
    },
  },
});

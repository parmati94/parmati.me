import defaultTheme from 'tailwindcss/defaultTheme';

/** @type {import('tailwindcss').Config} */
export default {
  content: ['./*.html', './partials/**/*.html', './js/**/*.js'],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        // Semantic tokens resolve to CSS vars set in css/main.css (R G B triplets),
        // so toggling .dark on <html> reskins the whole UI. Dark is the primary look
        // ("server room at night"); light values are tuned for equivalent contrast.
        bg: 'rgb(var(--bg) / <alpha-value>)',
        surface: 'rgb(var(--surface) / <alpha-value>)',
        raised: 'rgb(var(--raised) / <alpha-value>)',
        line: 'rgb(var(--line) / <alpha-value>)',
        ink: 'rgb(var(--ink) / <alpha-value>)',
        muted: 'rgb(var(--muted) / <alpha-value>)',
        accent: 'rgb(var(--accent) / <alpha-value>)',
        ok: 'rgb(var(--ok) / <alpha-value>)',
      },
      fontFamily: {
        sans: ['"IBM Plex Sans"', ...defaultTheme.fontFamily.sans],
        mono: ['"IBM Plex Mono"', ...defaultTheme.fontFamily.mono],
      },
    },
  },
  plugins: [],
};

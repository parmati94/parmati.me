// Dark/light toggle. The inline guard in partials/head.html sets .dark on <html>
// before first paint (stored choice, else system preference); this module just
// keeps Alpine state in sync and persists toggles.
const KEY = 'pm-theme';

export function theme() {
  return {
    mode: 'dark',

    initTheme() {
      this.mode = document.documentElement.classList.contains('dark') ? 'dark' : 'light';
    },

    toggleTheme() {
      this.mode = this.mode === 'dark' ? 'light' : 'dark';
      document.documentElement.classList.toggle('dark', this.mode === 'dark');
      localStorage.setItem(KEY, this.mode);
    },
  };
}

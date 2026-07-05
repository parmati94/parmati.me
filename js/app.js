import Alpine from 'alpinejs';
import '../css/main.css';
import { github } from './github.js';
import { projects } from './projects.js';
import { theme } from './theme.js';

document.addEventListener('alpine:init', () => {
  Alpine.data('app', () => ({
    // Feature modules spread in so the markup sees one flat component.
    ...theme(),
    ...projects(),
    ...github(),

    photoOk: false, // flips true when /content/img/photo.jpg loads; monogram shows otherwise
    gridOnline: false, // set on first scroll into view → cards stagger in
    year: new Date().getFullYear(),

    async init() {
      this.initTheme();
      // Projects/GitHub only exist on the index page; resume.html shares this bundle.
      if (document.getElementById('projects')) {
        await this.loadProjects();
        this.loadGithubMeta();
        this._watchGrid();
      }
    },

    _watchGrid() {
      const el = document.getElementById('projects');
      if (!el || !('IntersectionObserver' in window)) {
        this.gridOnline = true;
        return;
      }
      const io = new IntersectionObserver(
        (entries) => {
          if (entries.some((e) => e.isIntersecting)) {
            this.gridOnline = true;
            io.disconnect();
          }
        },
        { threshold: 0.1 }
      );
      io.observe(el);
    },
  }));
});

window.Alpine = Alpine;
Alpine.start();

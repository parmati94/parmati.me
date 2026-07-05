// Curated project list. Fetched from /content/projects.json so the live copy on
// the content volume can be edited without a rebuild (baked default ships in
// public/content/).
export function projects() {
  return {
    projects: [],
    projectsError: false,

    async loadProjects() {
      try {
        const res = await fetch('/content/projects.json', { cache: 'no-cache' });
        if (!res.ok) throw new Error(`projects.json ${res.status}`);
        const data = await res.json();
        this.projects = (data.projects || [])
          .slice()
          .sort((a, b) => (a.order ?? 99) - (b.order ?? 99));
      } catch (e) {
        this.projectsError = true;
      }
    },

    repoUrl(p) {
      return `https://github.com/${p.repo}`;
    },
  };
}

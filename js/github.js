// Live GitHub enrichment for the service board: one unauthenticated request for
// all public repos (60/hr/IP limit — one call is nothing), filtered client-side
// to the curated list. Cached in localStorage for 6h; on rate-limit or network
// failure we keep whatever cache exists, of any age, and the cards simply render
// without badges. The page never depends on this data.
const KEY = 'pm-gh-meta';
const TTL_MS = 6 * 60 * 60 * 1000;
const RUNNING_WINDOW_MS = 90 * 24 * 60 * 60 * 1000; // pushed within 90d = "running"

function readCache() {
  try {
    const raw = localStorage.getItem(KEY);
    return raw ? JSON.parse(raw) : null;
  } catch (e) {
    return null;
  }
}

function relTime(iso) {
  const secs = (Date.now() - new Date(iso).getTime()) / 1000;
  const rtf = new Intl.RelativeTimeFormat('en', { numeric: 'always', style: 'narrow' });
  if (secs < 3600) return rtf.format(-Math.max(1, Math.round(secs / 60)), 'minute');
  if (secs < 86400) return rtf.format(-Math.round(secs / 3600), 'hour');
  if (secs < 86400 * 30) return rtf.format(-Math.round(secs / 86400), 'day');
  if (secs < 86400 * 365) return rtf.format(-Math.round(secs / (86400 * 30)), 'month');
  return rtf.format(-Math.round(secs / (86400 * 365)), 'year');
}

export function github() {
  return {
    gh: {},

    async loadGithubMeta() {
      const cached = readCache();
      if (cached) this.gh = cached.byRepo || {};
      if (cached && Date.now() - cached.fetchedAt < TTL_MS) return;

      try {
        const res = await fetch('https://api.github.com/users/parmati94/repos?per_page=100');
        if (!res.ok) throw new Error(`github ${res.status}`);
        const repos = await res.json();
        const byRepo = {};
        for (const r of repos) {
          byRepo[r.full_name.toLowerCase()] = {
            stars: r.stargazers_count,
            pushedAt: r.pushed_at,
            language: r.language,
          };
        }
        this.gh = byRepo;
        localStorage.setItem(KEY, JSON.stringify({ fetchedAt: Date.now(), byRepo }));
      } catch (e) {
        /* stale cache (if any) already applied; badges stay hidden otherwise */
      }
    },

    ghMeta(p) {
      return this.gh[p.repo.toLowerCase()] || null;
    },

    isRunning(p) {
      const m = this.ghMeta(p);
      // No data yet → optimistic green; with data, dim anything idle >90d.
      if (!m) return true;
      return Date.now() - new Date(m.pushedAt).getTime() < RUNNING_WINDOW_MS;
    },

    pushedLabel(p) {
      const m = this.ghMeta(p);
      return m ? `pushed ${relTime(m.pushedAt)}` : '';
    },
  };
}

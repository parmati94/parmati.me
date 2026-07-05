// Native resume view. resume.json is produced by resume-sync/ from the LaTeX
// source; if it's missing or invalid we force the PDF view — the page must keep
// working for a content dir that only has resume.pdf.
export function resume() {
  return {
    resume: null,
    resumeView: 'web', // 'web' | 'pdf'

    async loadResume() {
      try {
        const res = await fetch('/content/resume.json', { cache: 'no-cache' });
        if (!res.ok) throw new Error(`resume.json ${res.status}`);
        this.resume = await res.json();
        const stored = localStorage.getItem('pm-resume-view');
        if (stored === 'pdf' || stored === 'web') this.resumeView = stored;
      } catch (e) {
        this.resume = null;
        this.resumeView = 'pdf';
      }
    },

    setResumeView(v) {
      this.resumeView = v;
      localStorage.setItem('pm-resume-view', v);
    },

    resumeEntryHasHeading(entry) {
      return !!(entry.left || entry.center || entry.right);
    },
  };
}

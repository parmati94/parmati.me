# resume-sync

Companion container for the site's `/resume` page. **Not implemented yet — design lives in
`../PLANNING.md` (gitignored working doc).**

Polls the private [`parmati94/resume`](https://github.com/parmati94/resume) repo; on a new
commit it compiles `resume.tex` → `resume.pdf` (tectonic), parses the McDowell CV structure
→ `resume.json`, and atomically publishes both into the site's content volume
(`~/.config/parmati-me/`). The site renders `resume.json` natively, with the PDF one pill
away. On any compile/parse failure it keeps the last good outputs and logs the error —
the live site never breaks.

Planned layout:

```
resume-sync/
├── Dockerfile        # debian-slim + git + tectonic + python3
├── sync.py           # poll loop: pull → compile → parse → publish
├── parser.py         # mcdowellcv .tex → resume.json
└── tests/            # golden file: sample .tex → expected .json
```

Runtime (own Portainer stack, LAN-only, no public exposure):
- env: repo URL + read-only fine-grained PAT
- mounts: `~/.config/resume-sync` (state + tectonic cache), `~/.config/parmati-me` (output)

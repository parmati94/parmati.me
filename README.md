# parmati.me

Personal site for [parmati.me](https://parmati.me) — about, projects, and resume.
Static Vite + Tailwind + Alpine.js build served by nginx in a single container.

## Updating the resume (no rebuild)

The container mounts `./content` over the site's `/content/` path. To publish a new
resume, drop the file in and refresh — no rebuild, no restart:

```bash
cp ~/my-new-resume.pdf ./content/resume.pdf
```

The same goes for everything under `./content/`:

| File                  | What it controls                              |
| --------------------- | --------------------------------------------- |
| `content/resume.pdf`  | `/resume` viewer + download                    |
| `content/projects.json` | Project cards (name, description, tags, order, `demoUrl`) |
| `content/img/photo.jpg` | Hero photo (a monogram renders until it exists) |
| `content/img/*`       | Optional project screenshots (`image` in projects.json) |

Defaults for all of these are baked into the image from `public/content/`, so the
container also runs fine with no volume mounted. Anything in `./content` overrides
the baked default with the same name.

## Development

```bash
npm install
npm run dev        # dev server; / and /resume.html
npm run build      # → dist/
```

## Deployment

```bash
docker compose up -d --build
```

Serves on port `5580`; point the reverse proxy for `parmati.me` at it.
Health check: `GET /healthz`.

## Project data

`content/projects.json` drives the grid. Cards are enriched client-side with live
stars / last-push / language from the GitHub API (one request, cached in
localStorage for 6h; the page works fine without it). A project with
`"demoUrl": "https://..."` gets a demo link next to its repo link — flip those on
as demos get hosted.

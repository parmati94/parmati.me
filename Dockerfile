# ===== BUILDER STAGE — compile the Vite/Tailwind site to static assets =====
FROM node:20-slim AS builder

WORKDIR /app

# Install deps first (cached unless package files change), then build.
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build   # → /app/dist

# ===== RUNTIME STAGE — plain nginx serving the static build =====
FROM nginx:alpine

COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/nginx.conf

# Mount point for live content (resume.pdf, projects.json, img/) — see compose.
RUN mkdir -p /content

EXPOSE 80

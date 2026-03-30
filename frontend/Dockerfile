# ── Stage 1: builder ─────────────────────────────────────────────────
FROM node:20-alpine AS builder

WORKDIR /app

# Copy package files first for layer caching
COPY package.json package-lock.json* ./

RUN npm install --registry=https://registry.npmmirror.com

# Copy source
COPY . .

# Build production bundle (skip vue-tsc type check for faster Docker builds)
RUN npx vite build


# ── Stage 2: nginx runtime ────────────────────────────────────────────
FROM nginx:1.25-alpine AS runtime

# Copy built assets
COPY --from=builder /app/dist /usr/share/nginx/html

# Nginx config: SPA routing + proxy /api to backend
COPY docker/nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

HEALTHCHECK --interval=15s --timeout=5s --start-period=10s --retries=3 \
    CMD wget -qO- http://localhost/api/v1/health || exit 1

CMD ["nginx", "-g", "daemon off;"]

# ========== Stage 1: Build ==========
FROM node:20-alpine AS builder

WORKDIR /app

COPY package*.json ./
RUN npm ci || npm install

COPY . .
RUN npm run build

# ========== Stage 2: Serve with nginx ==========
FROM nginx:alpine

# Copy nginx config as a TEMPLATE (envsubst will process it at startup)
# nginx:alpine auto-processes /etc/nginx/templates/*.template → /etc/nginx/conf.d/
COPY nginx.conf /etc/nginx/templates/default.conf.template

# Copy built React files
COPY --from=builder /app/dist /usr/share/nginx/html

# Default backend host (overridden in docker-compose & K8s)
ENV BACKEND_HOST=backend:8000

EXPOSE 80

HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
  CMD wget -q --spider http://127.0.0.1/ || exit 1

CMD ["nginx", "-g", "daemon off;"]
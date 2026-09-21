# ============================================================
# BMW ENTERPRISE BATCH ETL - REACT FRONTEND
# ============================================================

# Stage 1 — Build React application
FROM node:22-alpine AS build

WORKDIR /app

# Copy dependency files first
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy frontend source
COPY . .

# Build production application
RUN npm run build


# ============================================================
# Stage 2 — Serve React application
# ============================================================

FROM nginx:alpine

# Remove default nginx website
RUN rm -rf /usr/share/nginx/html/*

# Copy React production build
COPY --from=build /app/dist /usr/share/nginx/html

# Copy custom Nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Expose HTTP port
EXPOSE 80

# Start nginx
CMD ["nginx", "-g", "daemon off;"]
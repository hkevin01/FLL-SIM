##############################
# FLL-Sim Web Frontend Dockerfile
# React/Vue.js frontend application
##############################

FROM node:18-alpine AS base

WORKDIR /app

# Install dependencies
COPY web/package.json web/package-lock.json ./
RUN npm ci --only=production

# Build stage
FROM base AS build
RUN npm ci
COPY web/ ./
RUN npm run build

# Production stage
FROM node:18-alpine AS runtime
WORKDIR /app

# Install serve for production
RUN npm install -g serve

# Copy built application
COPY --from=build /app/dist ./dist

# Create non-root user
RUN addgroup -g 1001 -S webuser && \
    adduser -S webuser -u 1001 -G webuser
USER webuser

# Expose web port
EXPOSE 3000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:3000/health || exit 1

# Serve application
CMD ["serve", "-s", "dist", "-p", "3000"]

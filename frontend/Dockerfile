# Build stage for development and production
FROM node:18-alpine as build

# Set working directory
WORKDIR /app

# Set environment variables for optimized builds
ENV NODE_OPTIONS="--max-old-space-size=8192"
ENV SKIP_PREFLIGHT_CHECK=true

# Copy package files
COPY package.json package-lock.json ./

# Install dependencies with clean npm cache
RUN npm ci && npm cache clean --force

# Copy all files
COPY . .

# For development mode, we'll use the npm start command defined in docker-compose
# For production build, we'll use this:
RUN npm run build:prod

# Production stage
FROM nginx:1.25-alpine as production

# Add labels
LABEL maintainer="Vishal Bharti <https://github.com/visvikbharti>"
LABEL description="StickForStats Frontend - Statistical Analysis Platform"
LABEL version="1.0"

# Set environment variables
ENV NGINX_WORKER_PROCESSES="auto"
ENV NGINX_WORKER_CONNECTIONS="1024"

# Copy nginx configuration
COPY nginx/nginx.conf /etc/nginx/conf.d/default.conf

# Copy built assets from the build stage
COPY --from=build /app/build /usr/share/nginx/html

# Expose port
EXPOSE 80

# Set up health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 \
    CMD wget -q --no-cache --spider http://localhost:80 || exit 1

# Start nginx
CMD ["nginx", "-g", "daemon off;"]
# Multi-stage build for Angular application
FROM node:18-alpine AS builder

# Set working directory
WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci

# Copy source code
COPY . .

# Build application for production
RUN npm run build -- --configuration=production

# Production stage - serve with Node.js
FROM node:18-alpine AS runner

# Set working directory
WORKDIR /app

# Install serve package
RUN npm install -g serve

# Copy built application
COPY --from=builder /app/dist/frontend-angular ./dist

# Create non-root user
RUN addgroup -g 1001 -S nodejs && \
    adduser -S nextjs -u 1001

# Change ownership of the app directory
RUN chown -R nextjs:nodejs /app

# Switch to non-root user
USER nextjs

# Expose port
EXPOSE 3000

# Start the application
CMD ["serve", "-s", "dist", "-l", "3000"] 
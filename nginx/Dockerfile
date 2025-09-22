FROM node:20-alpine as builder

ARG VITE_API_BASE_URL
ARG NODE_ENV=production
ENV NODE_ENV=production
ENV VITE_API_BASE_URL=${VITE_API_BASE_URL:-http://api:8000/api}

WORKDIR /app

COPY frontend/package*.json .

RUN npm install

COPY frontend/ .

RUN npm run build

FROM nginx:alpine

COPY --from=builder /app/dist /usr/share/nginx/html

COPY nginx/nginx.conf /etc/nginx/conf.d/default.conf
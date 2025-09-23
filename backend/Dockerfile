FROM node:18

WORKDIR /app

COPY . .

RUN bun install

EXPOSE 3000

CMD ["node", "server.js"]
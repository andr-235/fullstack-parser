FROM node:20-alpine AS builder

WORKDIR /app

COPY package.json package-lock.json ./
RUN npm ci

COPY . .

# Generate Prisma client before building
RUN npx prisma generate

RUN npm run build


FROM node:20-alpine AS production

WORKDIR /app

# Копируем package.json и tsconfig
COPY package.json package-lock.json tsconfig.json ./

# Устанавливаем только production зависимости
RUN npm ci --omit=dev

# Копируем скомпилированный код
COPY --from=builder /app/dist ./dist
COPY --from=builder /app/prisma ./prisma

# Копируем Prisma client из builder
COPY --from=builder /app/node_modules/.prisma ./node_modules/.prisma
COPY --from=builder /app/node_modules/@prisma ./node_modules/@prisma

EXPOSE 3000

CMD ["npm", "start"]
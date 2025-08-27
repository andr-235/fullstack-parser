FROM nginx:alpine

# Устанавливаем необходимые пакеты для production
RUN apk add --no-cache \
 dumb-init \
 curl \
 && rm -rf /var/cache/apk/*

# Создаем директорию для логов и устанавливаем правильные права
RUN mkdir -p /var/log/nginx \
 && chown -R nginx:nginx /var/log/nginx \
 && touch /var/run/nginx.pid \
 && chown -R nginx:nginx /var/run/nginx.pid \
 && mkdir -p /var/cache/nginx \
 && chown -R nginx:nginx /var/cache/nginx

# Копируем оптимизированную конфигурацию nginx
COPY nginx.prod.ip.conf /etc/nginx/nginx.conf

# Проверяем конфигурацию nginx на этапе сборки (убрано, так как upstream сервисы еще не запущены)
# RUN nginx -t

# Устанавливаем nginx как пользователя по умолчанию
USER nginx

# Используем dumb-init для правильной обработки сигналов
ENTRYPOINT ["dumb-init", "--"]

EXPOSE 80

# Запускаем nginx в foreground режиме
CMD ["nginx", "-g", "daemon off;"] 
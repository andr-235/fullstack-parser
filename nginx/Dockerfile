FROM nginx:alpine

# Копируем конфигурацию nginx
COPY nginx.prod.ip.conf /etc/nginx/nginx.conf

# Копируем SSL сертификаты
COPY ssl/ /etc/nginx/ssl/

# Создаем директорию для логов
RUN mkdir -p /var/log/nginx

EXPOSE 80 443

CMD ["nginx", "-g", "daemon off;"] 
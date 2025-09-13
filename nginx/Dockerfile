FROM nginx:alpine

# Копируем конфигурацию nginx
COPY nginx/nginx.conf /etc/nginx/nginx.conf

# Создаем директории для логов
RUN mkdir -p /var/log/nginx

# Открываем порт 80
EXPOSE 80

# Запускаем nginx
CMD ["nginx", "-g", "daemon off;"]

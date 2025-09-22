FROM nginx:alpine

COPY nginx/nginx.conf /etc/nginx/conf.d/default.conf

# Создаем директорию для статических файлов
RUN mkdir -p /usr/share/nginx/html

# Nginx будет проксировать запросы к фронтенду
EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
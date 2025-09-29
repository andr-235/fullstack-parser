#!/bin/bash

# Простой скрипт для проверки VK токена
echo "=== VK Token Tester ==="
echo ""

# Текущий токен из кода
CURRENT_TOKEN="vk1.a.iK84KPuaW9THi354Pn7xGK5CnEgP8gFHrsACtz_DgJ01cjVc_jN0hVI-GpM8gm5UJLnDupWVjw55_sqF1EV5ZuMlhLqGB1nH4GqiNWHLbnQG03zTnVnMlgCDYbTbjE9d146HPS2RIHAd-SYtme-FnLjraGrKA-Eig3fS028_mU7xDoS5UCaZRPAqtZL9lKL8wKsWWjSTGLEnLGG4kJXVTQ"

echo "Проверяем текущий токен..."
echo "Токен: ${CURRENT_TOKEN:0:20}..."
echo ""

# Проверка токена (следуем редиректам)
echo "=== Тест 1: account.getInfo ==="
RESPONSE1=$(curl -s -L "https://dev.vk.com/method/account.getInfo?access_token=${CURRENT_TOKEN}&v=5.199")
echo "Ответ: $RESPONSE1"
echo ""

# Проверка доступа к группам
echo "=== Тест 2: groups.getById для группы 2249 ==="
RESPONSE2=$(curl -s -L "https://dev.vk.com/method/groups.getById?group_ids=40023088&access_token=${CURRENT_TOKEN}&v=5.199")
echo "Ответ: $RESPONSE2"
echo ""

# Проверка доступа к стене группы
echo "=== Тест 3: wall.get для группы 2249 ==="
RESPONSE3=$(curl -s -L "https://dev.vk.com/method/wall.get?owner_id=40023088&count=1&access_token=${CURRENT_TOKEN}&v=5.199")
echo "Ответ: $RESPONSE3"
echo ""

# Анализ результатов
echo "=== Анализ результатов ==="

if echo "$RESPONSE1" | grep -q "error"; then
    ERROR1=$(echo "$RESPONSE1" | grep -o '"error_msg":"[^"]*"' | cut -d'"' -f4)
    echo "❌ account.getInfo: ОШИБКА - $ERROR1"
else
    echo "✅ account.getInfo: OK"
fi

if echo "$RESPONSE2" | grep -q "error"; then
    ERROR2=$(echo "$RESPONSE2" | grep -o '"error_msg":"[^"]*"' | cut -d'"' -f4)
    echo "❌ groups.getById: ОШИБКА - $ERROR2"
else
    echo "✅ groups.getById: OK"
fi

if echo "$RESPONSE3" | grep -q "error"; then
    ERROR3=$(echo "$RESPONSE3" | grep -o '"error_msg":"[^"]*"' | cut -d'"' -f4)
    echo "❌ wall.get: ОШИБКА - $ERROR3"
else
    echo "✅ wall.get: OK"
fi

echo ""
echo "=== Информация о IP ==="
echo "Ваш внешний IP:"
curl -s ifconfig.me
echo ""
echo ""
echo "IP Docker контейнера (если запущен):"
docker inspect $(docker-compose ps -q api 2>/dev/null) --format='{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' 2>/dev/null || echo "Контейнер не запущен"

echo ""
echo "=== Рекомендации ==="
if echo "$RESPONSE1$RESPONSE2$RESPONSE3" | grep -q "access_token was given to another ip"; then
    echo "🔄 Проблема с IP-адресом. Решения:"
    echo "1. Получите новый токен с текущего IP"
    echo "2. Используйте network_mode: host в Docker"
    echo "3. Или запустите ./get_vk_token.sh для получения нового токена"
elif echo "$RESPONSE1$RESPONSE2$RESPONSE3" | grep -q "error"; then
    echo "❌ Есть ошибки API. Проверьте права доступа токена"
else
    echo "✅ Токен работает корректно!"
fi
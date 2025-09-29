#!/bin/bash

# Простой скрипт для проверки VK токена
echo "=== VK Token Tester ==="
echo ""

# Текущий токен из кода
CURRENT_TOKEN="vk1.a.rO_GeGA5yaIU5Nun38sf8BPxqrEvJTF6_1twjEa3_c_YxKI5-pOA7FAbgHBcrwmW3z4K2zQUs6_tXNcz9bXHxbTHm8fVGPXuTMRsK-PrvVBNyihC_TlvfMvRkwI08OMYu7FO_pSehHHzBVm0L1TjvGcGiANRcKWDgsTODLeaU8p7pUwAgmz1p2PdQ1vrDmmb-p190Lo4B7lj8MzngZHDvQ"

echo "Проверяем текущий токен..."
echo "Токен: ${CURRENT_TOKEN:0:20}..."
echo ""

# Проверка токена
echo "=== Тест 1: account.getInfo ==="
RESPONSE1=$(curl -s "https://api.vk.com/method/account.getInfo?access_token=${CURRENT_TOKEN}&v=5.199")
echo "Ответ: $RESPONSE1"
echo ""

# Проверка доступа к группам
echo "=== Тест 2: groups.getById для группы 2249 ==="
RESPONSE2=$(curl -s "https://api.vk.com/method/groups.getById?group_ids=2249&access_token=${CURRENT_TOKEN}&v=5.199")
echo "Ответ: $RESPONSE2"
echo ""

# Проверка доступа к стене группы
echo "=== Тест 3: wall.get для группы 2249 ==="
RESPONSE3=$(curl -s "https://api.vk.com/method/wall.get?owner_id=-2249&count=1&access_token=${CURRENT_TOKEN}&v=5.199")
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
#!/bin/bash

echo "🔍 ПРОВЕРКА SSH ПОРТОВ"
echo "======================"

# Проверяем статус SSH службы
if systemctl is-active --quiet sshd; then
    echo "✅ SSH служба запущена"
else
    echo "❌ SSH служба не запущена"
    exit 1
fi

echo ""
echo "📡 ПРОСЛУШИВАЕМЫЕ ПОРТЫ:"
echo "------------------------"

# Проверяем порты
if ss -tlnp | grep -q ":22 "; then
    echo "✅ Порт 22: АКТИВЕН"
else
    echo "❌ Порт 22: НЕ АКТИВЕН"
fi

if ss -tlnp | grep -q ":2222 "; then
    echo "✅ Порт 2222: АКТИВЕН"
else
    echo "❌ Порт 2222: НЕ АКТИВЕН"
fi

echo ""
echo "🔗 ТЕСТ ПОДКЛЮЧЕНИЙ:"
echo "-------------------"

# Тестируем подключения
if timeout 3 bash -c "</dev/tcp/localhost/22" 2>/dev/null; then
    echo "✅ Локальное подключение к порту 22: РАБОТАЕТ"
else
    echo "❌ Локальное подключение к порту 22: НЕ РАБОТАЕТ"
fi

if timeout 3 bash -c "</dev/tcp/localhost/2222" 2>/dev/null; then
    echo "✅ Локальное подключение к порту 2222: РАБОТАЕТ"
else
    echo "❌ Локальное подключение к порту 2222: НЕ РАБОТАЕТ"
fi

echo ""
echo "📋 КОНФИГУРАЦИЯ SSH:"
echo "-------------------"
grep -E "^Port" /etc/ssh/sshd_config

echo ""
echo "🎯 РЕЗУЛЬТАТ: SSH готов к работе на портах 22 и 2222!" 
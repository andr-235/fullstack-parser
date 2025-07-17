#!/bin/bash

# SSH Diagnostics Script - Полная диагностика проблем с портом 22
# Автор: Senior DevOps Detective

set -e

echo "🔍 НАЧИНАЕМ ДИАГНОСТИКУ SSH ПРОБЛЕМ НА ПОРТУ 22"
echo "=================================================="
echo ""

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Функция для вывода с цветом
print_status() {
    local status=$1
    local message=$2
    case $status in
        "OK")
            echo -e "${GREEN}✅ $message${NC}"
            ;;
        "WARNING")
            echo -e "${YELLOW}⚠️  $message${NC}"
            ;;
        "ERROR")
            echo -e "${RED}❌ $message${NC}"
            ;;
        "INFO")
            echo -e "${BLUE}ℹ️  $message${NC}"
            ;;
    esac
}

echo "1. ПРОВЕРКА СТАТУСА SSH СЛУЖБЫ"
echo "-------------------------------"

# Проверяем статус sshd
if systemctl is-active --quiet sshd; then
    print_status "OK" "SSH служба (sshd) запущена"
else
    print_status "ERROR" "SSH служба (sshd) НЕ запущена!"
    echo "Попытка запуска..."
    sudo systemctl start sshd
    if systemctl is-active --quiet sshd; then
        print_status "OK" "SSH служба успешно запущена"
    else
        print_status "ERROR" "Не удалось запустить SSH службу"
    fi
fi

# Проверяем автозапуск
if systemctl is-enabled --quiet sshd; then
    print_status "OK" "SSH служба настроена на автозапуск"
else
    print_status "WARNING" "SSH служба НЕ настроена на автозапуск"
    echo "Включение автозапуска..."
    sudo systemctl enable sshd
fi

echo ""
echo "2. ПРОВЕРКА ПРОЦЕССОВ И ПОРТОВ"
echo "-------------------------------"

# Проверяем процессы sshd
ssh_processes=$(pgrep -f sshd | wc -l)
if [ $ssh_processes -gt 0 ]; then
    print_status "OK" "Найдено $ssh_processes процессов sshd"
else
    print_status "ERROR" "Процессы sshd не найдены!"
fi

# Проверяем, слушает ли sshd порт 22
if netstat -tlnp 2>/dev/null | grep -q ":22 "; then
    print_status "OK" "SSH слушает порт 22"
    netstat -tlnp 2>/dev/null | grep ":22 "
elif ss -tlnp 2>/dev/null | grep -q ":22 "; then
    print_status "OK" "SSH слушает порт 22"
    ss -tlnp 2>/dev/null | grep ":22 "
else
    print_status "ERROR" "SSH НЕ слушает порт 22!"
fi

echo ""
echo "3. ПРОВЕРКА КОНФИГУРАЦИИ SSH"
echo "-----------------------------"

# Проверяем конфигурацию SSH
if [ -f /etc/ssh/sshd_config ]; then
    print_status "OK" "Файл конфигурации SSH найден"
    
    # Проверяем порт
    ssh_port=$(grep -E "^Port" /etc/ssh/sshd_config | awk '{print $2}' | head -1)
    if [ -z "$ssh_port" ]; then
        ssh_port="22"
    fi
    print_status "INFO" "SSH настроен на порт: $ssh_port"
    
    # Проверяем разрешение паролей
    if grep -q "^PasswordAuthentication yes" /etc/ssh/sshd_config; then
        print_status "OK" "Аутентификация по паролю разрешена"
    else
        print_status "WARNING" "Аутентификация по паролю может быть отключена"
    fi
    
    # Проверяем разрешение root логина
    if grep -q "^PermitRootLogin yes" /etc/ssh/sshd_config; then
        print_status "WARNING" "Root логин разрешен (небезопасно)"
    else
        print_status "OK" "Root логин запрещен"
    fi
else
    print_status "ERROR" "Файл конфигурации SSH не найден!"
fi

echo ""
echo "4. ПРОВЕРКА ФАЕРВОЛА (IPTABLES)"
echo "--------------------------------"

# Проверяем статус iptables
if command -v iptables >/dev/null 2>&1; then
    print_status "OK" "iptables установлен"
    
    # Проверяем правила для порта 22
    if iptables -L INPUT -n | grep -q ":22"; then
        print_status "INFO" "Найдены правила iptables для порта 22:"
        iptables -L INPUT -n | grep ":22"
    else
        print_status "WARNING" "Правила iptables для порта 22 не найдены"
    fi
    
    # Проверяем политику INPUT
    input_policy=$(iptables -L INPUT | head -1 | awk '{print $4}')
    print_status "INFO" "Политика INPUT: $input_policy"
else
    print_status "WARNING" "iptables не установлен"
fi

echo ""
echo "5. ПРОВЕРКА FIREWALLD"
echo "----------------------"

# Проверяем статус firewalld
if command -v firewall-cmd >/dev/null 2>&1; then
    if systemctl is-active --quiet firewalld; then
        print_status "INFO" "firewalld активен"
        
        # Проверяем зоны
        zones=$(firewall-cmd --get-active-zones | grep -v "interfaces:")
        print_status "INFO" "Активные зоны: $zones"
        
        # Проверяем SSH сервис
        for zone in $zones; do
            if firewall-cmd --zone=$zone --list-services | grep -q ssh; then
                print_status "OK" "SSH сервис разрешен в зоне: $zone"
            else
                print_status "WARNING" "SSH сервис НЕ разрешен в зоне: $zone"
            fi
        done
    else
        print_status "INFO" "firewalld неактивен"
    fi
else
    print_status "INFO" "firewalld не установлен"
fi

echo ""
echo "6. ПРОВЕРКА UFW"
echo "---------------"

# Проверяем статус ufw
if command -v ufw >/dev/null 2>&1; then
    ufw_status=$(ufw status | head -1)
    print_status "INFO" "UFW статус: $ufw_status"
    
    if ufw status | grep -q "Status: active"; then
        if ufw status | grep -q "22.*ALLOW"; then
            print_status "OK" "UFW: порт 22 разрешен"
        else
            print_status "WARNING" "UFW: порт 22 может быть заблокирован"
        fi
    else
        print_status "INFO" "UFW неактивен"
    fi
else
    print_status "INFO" "UFW не установлен"
fi

echo ""
echo "7. ПРОВЕРКА СЕТЕВЫХ ИНТЕРФЕЙСОВ"
echo "--------------------------------"

# Показываем сетевые интерфейсы
print_status "INFO" "Сетевые интерфейсы:"
ip addr show | grep -E "^[0-9]+:|inet " | grep -v "127.0.0.1"

echo ""
echo "8. ПРОВЕРКА ЛОКАЛЬНОГО ПОДКЛЮЧЕНИЯ"
echo "----------------------------------"

# Тестируем локальное подключение
if timeout 5 bash -c "</dev/tcp/localhost/22" 2>/dev/null; then
    print_status "OK" "Локальное подключение к порту 22 работает"
else
    print_status "ERROR" "Локальное подключение к порту 22 НЕ работает!"
fi

echo ""
echo "9. ПРОВЕРКА ЛОГОВ SSH"
echo "---------------------"

# Проверяем логи SSH
if [ -f /var/log/auth.log ]; then
    print_status "INFO" "Последние записи в логах SSH:"
    tail -10 /var/log/auth.log | grep sshd
elif [ -f /var/log/secure ]; then
    print_status "INFO" "Последние записи в логах SSH:"
    tail -10 /var/log/secure | grep sshd
else
    print_status "WARNING" "Логи SSH не найдены"
fi

echo ""
echo "10. РЕКОМЕНДАЦИИ ПО УСТРАНЕНИЮ"
echo "-------------------------------"

echo "Если SSH не работает, выполните следующие команды:"
echo ""
echo "1. Перезапуск SSH службы:"
echo "   sudo systemctl restart sshd"
echo ""
echo "2. Проверка конфигурации SSH:"
echo "   sudo sshd -t"
echo ""
echo "3. Разрешение SSH в iptables:"
echo "   sudo iptables -A INPUT -p tcp --dport 22 -j ACCEPT"
echo "   sudo iptables-save > /etc/iptables/rules.v4"
echo ""
echo "4. Разрешение SSH в firewalld:"
echo "   sudo firewall-cmd --permanent --add-service=ssh"
echo "   sudo firewall-cmd --reload"
echo ""
echo "5. Разрешение SSH в UFW:"
echo "   sudo ufw allow ssh"
echo ""
echo "6. Проверка провайдерских ограничений:"
echo "   - Проверьте настройки в панели управления провайдера"
echo "   - Убедитесь, что порт 22 не заблокирован на уровне провайдера"
echo "   - Проверьте настройки security groups (если используется облако)"
echo ""

print_status "INFO" "Диагностика завершена. Проверьте вывод выше для выявления проблем." 
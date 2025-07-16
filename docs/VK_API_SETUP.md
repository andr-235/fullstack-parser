# Настройка VK API

## Получение Access Token для ВКонтакте

Для работы с VK API необходимо получить access token. Следуйте этим шагам:

### Шаг 1: Создание VK приложения

1. Перейдите на [vk.com/dev](https://vk.com/dev)
2. Войдите в свой аккаунт ВКонтакте
3. Нажмите "Создать приложение"
4. Выберите тип "Standalone приложение"
5. Заполните необходимые поля:
   - Название: "VK Comments Parser"
   - Категория: "Утилиты"
6. Сохраните приложение

### Шаг 2: Получение Access Token

1. В настройках приложения найдите "ID приложения" (APP_ID)
2. Используйте один из методов получения токена:

#### Метод 1: Через Implicit Flow (рекомендуется для разработки)

Перейдите по ссылке (замените YOUR_APP_ID на ID вашего приложения):

```
https://oauth.vk.com/authorize?client_id=YOUR_APP_ID&display=page&redirect_uri=https://oauth.vk.com/blank.html&scope=groups&response_type=token&v=5.131
```

**Необходимые разрешения (scope):**
- `groups` - доступ к информации о группах
- `offline` - работа приложения в любое время (опционально)

#### Метод 2: Через Service Token (для production)

1. В настройках приложения найдите раздел "Сервисный токен"
2. Создайте сервисный токен с необходимыми правами
3. Скопируйте полученный токен

### Шаг 3: Настройка .env файла

1. Откройте файл `.env` в корне проекта
2. Найдите строку с `VK_ACCESS_TOKEN`
3. Замените `your-vk-access-token-here` на полученный токен:

```env
VK_ACCESS_TOKEN=your_actual_access_token_here
VK_API_VERSION=5.131
VK_APP_ID=your_app_id_here
```

### Шаг 4: Перезапуск сервисов

После обновления .env файла перезапустите backend:

```bash
docker-compose restart backend
```

### Проверка настройки

1. Откройте страницу VK Группы в приложении
2. Попробуйте добавить группу, например: `https://vk.com/livebir`
3. При корректной настройке группа должна быть добавлена без ошибок

### Возможные ошибки

#### User authorization failed: invalid access_token (4)
- Проверьте правильность токена в .env файле
- Убедитесь, что токен не истек
- Проверьте, что у токена есть права на доступ к группам

#### Access denied: no access to this group
- Группа может быть закрытой
- Попробуйте добавить открытую группу

### Полезные ссылки

- [VK API Documentation](https://dev.vk.com/api/getting-started)
- [OAuth авторизация](https://dev.vk.com/api/access-token/implicit-flow-user)
- [Список методов Groups API](https://dev.vk.com/method/groups)

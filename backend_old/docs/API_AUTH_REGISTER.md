# API Documentation: User Registration

## POST /api/v1/auth/register

Регистрация нового пользователя в системе.

### Rate Limiting
- **Лимит**: 3 запроса в минуту
- **При превышении**: HTTP 429 Too Many Requests

### Request Body

```json
{
  "email": "user@example.com",
  "password": "password123",
  "full_name": "John Doe"
}
```

#### Поля запроса

| Поле | Тип | Обязательное | Описание | Ограничения |
|------|-----|--------------|----------|-------------|
| `email` | string | Да | Email пользователя | Валидный email формат |
| `password` | string | Да | Пароль пользователя | Минимум 8 символов |
| `full_name` | string | Да | Полное имя пользователя | 2-100 символов |

### Response

#### Успешная регистрация (201 Created)

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 3600,
  "user": {
    "id": 1,
    "email": "user@example.com",
    "full_name": "John Doe",
    "is_superuser": false
  }
}
```

#### Ошибки

##### 400 Bad Request - Пользователь уже существует
```json
{
  "detail": "User with this email already exists"
}
```

##### 422 Unprocessable Entity - Ошибка валидации
```json
{
  "detail": [
    {
      "loc": ["body", "email"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

##### 429 Too Many Requests - Превышен лимит запросов
```json
{
  "detail": "Rate limit exceeded: 3 per 1 minute"
}
```

### Примеры использования

#### cURL
```bash
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "password123",
    "full_name": "John Doe"
  }'
```

#### Python
```python
import requests

url = "http://localhost:8000/api/v1/auth/register"
data = {
    "email": "user@example.com",
    "password": "password123",
    "full_name": "John Doe"
}

response = requests.post(url, json=data)
if response.status_code == 201:
    result = response.json()
    access_token = result["access_token"]
    print(f"Registration successful! Access token: {access_token}")
else:
    print(f"Registration failed: {response.json()}")
```

#### JavaScript
```javascript
const response = await fetch('http://localhost:8000/api/v1/auth/register', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    email: 'user@example.com',
    password: 'password123',
    full_name: 'John Doe'
  })
});

const result = await response.json();
if (response.ok) {
  console.log('Registration successful!', result);
} else {
  console.error('Registration failed:', result);
}
```

### Безопасность

1. **Хеширование паролей**: Пароли хешируются с использованием bcrypt
2. **Rate Limiting**: Защита от брутфорс атак
3. **Валидация данных**: Строгая валидация всех входных данных
4. **Логирование**: Все события регистрации логируются для аудита
5. **JWT токены**: Безопасные токены для аутентификации

### Интеграция с системой

После успешной регистрации:
- Пользователь автоматически аутентифицирован
- Создаются access и refresh токены
- Данные пользователя кэшируются
- Логируется событие безопасности
- Пользователь может сразу использовать API

### Связанные endpoints

- `POST /api/v1/auth/login` - Вход в систему
- `POST /api/v1/auth/refresh` - Обновление токена
- `GET /api/v1/auth/me` - Информация о текущем пользователе

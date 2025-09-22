# Использование рефакторированного модуля Auth

## 🚀 Быстрый старт

### Подключение router в main.py

```python
# В main.py добавьте:
from auth.presentation.api.auth_router import router

app.include_router(router)
```

### Использование в коде

```python
# Импорт компонентов
from auth.domain.entities.user import User
from auth.domain.value_objects.email import Email
from auth.domain.value_objects.password import Password
from auth.application.use_cases.register_user import RegisterUserUseCase
from auth.application.dto.register_user_dto import RegisterUserDTO

# Создание Value Objects
email = Email("user@example.com")
password = Password.create_from_plain("SecurePass123")

# Использование Use Cases
use_case = RegisterUserUseCase(user_repository, password_service)
dto = RegisterUserDTO(email="user@example.com", full_name="John Doe", password="SecurePass123")
user = await use_case.execute(dto)
```

## 🔧 Решение проблемы циклических импортов

### Проблема
Циклические импорты возникают из-за:
1. `auth.models` → `database` → `auth` (через старые импорты)
2. `auth` → `presentation` → `infrastructure` → `auth.models`

### Решение
1. **Временное**: Используйте прямой импорт router
2. **Постоянное**: Создайте отдельную модель UserModel для нового модуля

### Временное решение
```python
# В main.py
from auth.presentation.api.auth_router import router
app.include_router(router)
```

### Постоянное решение
Создайте новый файл `auth/infrastructure/models/user_model.py`:

```python
from sqlalchemy import Column, String, Boolean, DateTime, Integer
from src.models import Base

class UserModel(Base):
    __tablename__ = "users"
    
    email = Column(String(255), unique=True, index=True, nullable=False)
    full_name = Column(String(255), nullable=False)
    hashed_password = Column(String(512), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    is_superuser = Column(Boolean, default=False, nullable=False)
    # ... остальные поля
```

## 📁 Структура модуля

```
auth/
├── domain/           # Доменная логика
├── application/      # Use cases и DTO
├── infrastructure/   # Реализации репозиториев
├── presentation/     # API и схемы
└── shared/          # Общие компоненты
```

## 🧪 Тестирование

```bash
cd /opt/app/backend
poetry run python test_auth_refactor.py
```

## ✅ Статус

- ✅ Domain Layer - готов
- ✅ Application Layer - готов  
- ✅ Infrastructure Layer - готов
- ✅ Presentation Layer - готов
- ⚠️ Router импорт - требует решения циклических зависимостей
- ✅ Тесты - работают
- ✅ Архитектура - Clean Architecture реализована

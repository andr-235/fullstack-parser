# API Versioning Strategy

## Проблемы текущей версии

- Отсутствует версионирование API
- Нет обратной совместимости
- Сложно добавлять новые функции без breaking changes

## Рекомендации

### 1. URL Versioning

```python
# Текущий подход
app.include_router(auth_router, prefix="/api/v1", tags=["Authentication"])

# Улучшенный подход
app.include_router(auth_router, prefix="/api/v1", tags=["Authentication"])
app.include_router(auth_router_v2, prefix="/api/v2", tags=["Authentication v2"])
```

### 2. Header Versioning

```python
from fastapi import Header, Depends

async def get_api_version(x_api_version: str = Header(default="v1")):
    return x_api_version

@app.get("/users/")
async def get_users(version: str = Depends(get_api_version)):
    if version == "v2":
        return {"users": [], "metadata": {"version": "v2"}}
    return {"users": []}
```

### 3. Deprecation Strategy

```python
from fastapi import Depends
from datetime import datetime, timedelta

def check_deprecation(version: str = Depends(get_api_version)):
    if version == "v1":
        deprecation_date = datetime.utcnow() + timedelta(days=90)
        return {
            "deprecated": True,
            "sunset_date": deprecation_date.isoformat(),
            "migration_guide": "/docs/migration/v1-to-v2"
        }
    return {"deprecated": False}
```

### 4. Version Management

```python
# src/api/versions.py
from enum import Enum

class APIVersion(str, Enum):
    V1 = "v1"
    V2 = "v2"
    V3 = "v3"

class VersionConfig:
    SUPPORTED_VERSIONS = [APIVersion.V1, APIVersion.V2]
    CURRENT_VERSION = APIVersion.V2
    DEPRECATED_VERSIONS = [APIVersion.V1]
```

### 5. Backward Compatibility

```python
# src/api/compatibility.py
from typing import Any, Dict

def ensure_backward_compatibility(data: Dict[str, Any], version: str) -> Dict[str, Any]:
    if version == "v1":
        # Убираем новые поля для v1
        return {k: v for k, v in data.items() if k not in ["new_field", "metadata"]}
    return data
```

## Implementation Plan

1. Добавить версионирование в URL
2. Создать middleware для проверки версий
3. Реализовать deprecation warnings
4. Настроить автоматическую документацию по версиям
5. Создать migration guides

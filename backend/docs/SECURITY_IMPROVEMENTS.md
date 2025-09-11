# Security Improvements Guide

## Текущие уязвимости

- Слабая аутентификация
- Отсутствует rate limiting
- Нет валидации входных данных
- Отсутствует audit logging
- Нет защиты от CSRF

## Рекомендации

### 1. Enhanced Authentication

```python
# src/auth/security.py
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Optional
import secrets

class SecurityManager:
    def __init__(self, secret_key: str, algorithm: str = "HS256"):
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        self.secret_key = secret_key
        self.algorithm = algorithm
        self.refresh_tokens = {}  # В production использовать Redis

    def create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None):
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=15)

        to_encode.update({"exp": expire, "type": "access"})
        return jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)

    def create_refresh_token(self, user_id: str):
        token = secrets.token_urlsafe(32)
        self.refresh_tokens[token] = {
            "user_id": user_id,
            "created_at": datetime.utcnow(),
            "expires_at": datetime.utcnow() + timedelta(days=30)
        }
        return token

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return self.pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password: str) -> str:
        return self.pwd_context.hash(password)
```

### 2. Rate Limiting

```python
# src/middleware/rate_limiting.py
from fastapi import Request, HTTPException
from typing import Dict, Tuple
import time
import redis.asyncio as redis

class AdvancedRateLimiter:
    def __init__(self, redis_url: str):
        self.redis = redis.from_url(redis_url)
        self.limits = {
            "login": (5, 300),  # 5 попыток за 5 минут
            "api": (100, 3600),  # 100 запросов за час
            "parser": (10, 3600),  # 10 парсингов за час
        }

    async def check_rate_limit(self, request: Request, limit_type: str) -> bool:
        client_ip = request.client.host
        user_id = getattr(request.state, 'user_id', None)
        key = f"rate_limit:{limit_type}:{user_id or client_ip}"

        limit, window = self.limits.get(limit_type, (100, 3600))

        current_time = int(time.time())
        window_start = current_time - window

        # Используем Redis pipeline для атомарности
        pipe = self.redis.pipeline()
        pipe.zremrangebyscore(key, 0, window_start)
        pipe.zcard(key)
        pipe.zadd(key, {str(current_time): current_time})
        pipe.expire(key, window)

        results = await pipe.execute()
        current_count = results[1]

        if current_count >= limit:
            raise HTTPException(
                status_code=429,
                detail=f"Rate limit exceeded. {limit} requests per {window} seconds allowed."
            )

        return True
```

### 3. Input Validation & Sanitization

```python
# src/validation/input_validator.py
from pydantic import BaseModel, validator, Field
from typing import Any, Dict, List
import re
import html

class InputValidator:
    @staticmethod
    def sanitize_string(value: str) -> str:
        """Очистка строки от потенциально опасных символов"""
        if not isinstance(value, str):
            return str(value)

        # HTML escaping
        value = html.escape(value)

        # Удаление потенциально опасных символов
        value = re.sub(r'[<>"\']', '', value)

        # Ограничение длины
        return value[:1000]

    @staticmethod
    def validate_email(email: str) -> bool:
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))

    @staticmethod
    def validate_vk_id(vk_id: str) -> bool:
        """Валидация VK ID"""
        try:
            id_int = int(vk_id)
            return 1 <= id_int <= 2**31 - 1
        except (ValueError, TypeError):
            return False

class SecureBaseModel(BaseModel):
    """Базовая модель с автоматической валидацией"""

    @validator('*', pre=True)
    def sanitize_fields(cls, v):
        if isinstance(v, str):
            return InputValidator.sanitize_string(v)
        return v
```

### 4. SQL Injection Protection

```python
# src/database/secure_queries.py
from sqlalchemy import text
from sqlalchemy.orm import Session
from typing import Any, Dict, List

class SecureQueryBuilder:
    @staticmethod
    def safe_select(table: str, filters: Dict[str, Any]) -> str:
        """Безопасное построение SELECT запросов"""
        base_query = f"SELECT * FROM {table}"
        conditions = []
        params = {}

        for i, (field, value) in enumerate(filters.items()):
            param_name = f"param_{i}"
            conditions.append(f"{field} = :{param_name}")
            params[param_name] = value

        if conditions:
            base_query += " WHERE " + " AND ".join(conditions)

        return base_query, params

    @staticmethod
    async def execute_safe_query(session: Session, query: str, params: Dict[str, Any]):
        """Безопасное выполнение запроса с параметрами"""
        return await session.execute(text(query), params)
```

### 5. CORS Security

```python
# src/middleware/secure_cors.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

def setup_secure_cors(app: FastAPI, allowed_origins: List[str]):
    """Настройка безопасного CORS"""
    app.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins,  # Только доверенные домены
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE"],  # Только необходимые методы
        allow_headers=[
            "Authorization",
            "Content-Type",
            "X-Requested-With",
            "X-API-Key"
        ],  # Только необходимые заголовки
        expose_headers=["X-Total-Count", "X-Page-Count"],
        max_age=3600,  # Кеширование preflight запросов
    )
```

### 6. Audit Logging

```python
# src/security/audit_logger.py
from datetime import datetime
from typing import Dict, Any, Optional
import json
import logging

class AuditLogger:
    def __init__(self):
        self.logger = logging.getLogger("audit")
        handler = logging.FileHandler("audit.log")
        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)

    def log_auth_event(self, event_type: str, user_id: Optional[str],
                      ip_address: str, success: bool, details: Dict[str, Any] = None):
        """Логирование событий аутентификации"""
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "event_type": event_type,
            "user_id": user_id,
            "ip_address": ip_address,
            "success": success,
            "details": details or {}
        }
        self.logger.info(json.dumps(log_data))

    def log_api_access(self, endpoint: str, method: str, user_id: Optional[str],
                      ip_address: str, status_code: int, response_time: float):
        """Логирование доступа к API"""
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "event_type": "api_access",
            "endpoint": endpoint,
            "method": method,
            "user_id": user_id,
            "ip_address": ip_address,
            "status_code": status_code,
            "response_time": response_time
        }
        self.logger.info(json.dumps(log_data))
```

### 7. Security Headers

```python
# src/middleware/security_headers.py
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)

        # Security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Content-Security-Policy"] = "default-src 'self'"
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"

        return response
```

### 8. Data Encryption

```python
# src/security/encryption.py
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
import os

class DataEncryption:
    def __init__(self, password: str):
        self.password = password.encode()
        self.salt = os.urandom(16)
        self.key = self._derive_key()
        self.cipher = Fernet(self.key)

    def _derive_key(self) -> bytes:
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=self.salt,
            iterations=100000,
        )
        return base64.urlsafe_b64encode(kdf.derive(self.password))

    def encrypt(self, data: str) -> str:
        """Шифрование данных"""
        return self.cipher.encrypt(data.encode()).decode()

    def decrypt(self, encrypted_data: str) -> str:
        """Расшифровка данных"""
        return self.cipher.decrypt(encrypted_data.encode()).decode()
```

### 9. Environment Security

```python
# src/config/secure_config.py
from pydantic import BaseSettings, Field
from typing import List

class SecureSettings(BaseSettings):
    # Обязательные секретные ключи
    secret_key: str = Field(..., min_length=32)
    database_password: str = Field(..., min_length=8)
    redis_password: str = Field(..., min_length=8)

    # JWT настройки
    jwt_secret: str = Field(..., min_length=32)
    jwt_algorithm: str = "HS256"
    jwt_expiration_minutes: int = 15

    # CORS настройки
    allowed_origins: List[str] = Field(default_factory=list)

    # Rate limiting
    rate_limit_enabled: bool = True
    max_requests_per_minute: int = 60

    # Security features
    enable_audit_logging: bool = True
    enable_csrf_protection: bool = True
    enable_sql_injection_protection: bool = True

    class Config:
        env_file = ".env"
        case_sensitive = False
```

## Implementation Checklist

### Immediate (Week 1-2)

- [ ] Внедрить rate limiting
- [ ] Добавить security headers
- [ ] Настроить audit logging
- [ ] Усилить валидацию входных данных

### Short-term (Month 1)

- [ ] Реализовать enhanced authentication
- [ ] Добавить encryption для sensitive data
- [ ] Настроить secure CORS
- [ ] Внедрить SQL injection protection

### Medium-term (Month 2-3)

- [ ] Настроить monitoring и alerting
- [ ] Реализовать session management
- [ ] Добавить API key authentication
- [ ] Внедрить data masking

### Long-term (Month 3+)

- [ ] Penetration testing
- [ ] Security audit
- [ ] Compliance certification
- [ ] Advanced threat detection

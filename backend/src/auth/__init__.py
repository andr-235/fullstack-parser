"""
Модуль аутентификации (Clean Architecture)

Предоставляет функциональность аутентификации и управления пользователями
с использованием принципов Clean Architecture и SOLID
"""

# Временно убираем импорт router из-за циклических импортов
# Проблема: auth.models импортирует database, что создает циклические зависимости

# Для использования router в main.py используйте:
# from auth.presentation.api.auth_router import router

# Экспорт
__all__ = []

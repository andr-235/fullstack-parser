#!/usr/bin/env python3
"""
Скрипт для проверки структуры проекта после миграции

Проверяет наличие всех необходимых файлов и директорий
в соответствии с fastapi-best-practices
"""

import os
import sys
from pathlib import Path


def check_structure():
    """Проверить структуру проекта"""

    base_path = Path("/opt/app/backend")
    src_path = base_path / "src"

    print("🔍 Проверка структуры проекта VK Comments Parser")
    print("=" * 50)

    # Проверка основных директорий
    required_dirs = [
        "src",
        "src/auth",
        "src/comments",
        "src/groups",
        "src/parser",
        "src/monitoring",
        "src/morphological",
        "src/keywords",
        "tests",
        "tests/auth",
        "tests/comments",
        "tests/groups",
        "tests/parser",
        "tests/monitoring",
        "tests/morphological",
        "requirements",
        "alembic",
    ]

    print("📁 Проверка директорий:")
    all_dirs_ok = True

    for dir_path in required_dirs:
        full_path = base_path / dir_path
        if full_path.exists():
            print(f"  ✅ {dir_path}")
        else:
            print(f"  ❌ {dir_path} - НЕ НАЙДЕН")
            all_dirs_ok = False

    # Проверка глобальных файлов
    required_global_files = [
        "src/__init__.py",
        "src/main.py",
        "src/config.py",
        "src/database.py",
        "src/exceptions.py",
        "src/models.py",
        "src/pagination.py",
        "requirements/base.txt",
        "requirements/dev.txt",
        "requirements/prod.txt",
        "pyproject.toml",
        "alembic.ini",
    ]

    print("\n📄 Проверка глобальных файлов:")
    all_global_files_ok = True

    for file_path in required_global_files:
        full_path = base_path / file_path
        if full_path.exists():
            print(f"  ✅ {file_path}")
        else:
            print(f"  ❌ {file_path} - НЕ НАЙДЕН")
            all_global_files_ok = False

    # Проверка файлов модулей
    modules = [
        "auth",
        "comments",
        "groups",
        "parser",
        "monitoring",
        "morphological",
        "keywords",
        "vk_api",
        "settings",
        "health",
        "error_reporting",
    ]
    required_module_files = [
        "router.py",
        "schemas.py",
        "models.py",
        "dependencies.py",
        "config.py",
        "constants.py",
        "exceptions.py",
        "service.py",
        "utils.py",
    ]

    # Специальные файлы для модулей
    special_files = {
        "parser": ["client.py"],
        "vk_api": ["client.py"],
    }

    print("\n🏗️ Проверка файлов модулей:")
    all_module_files_ok = True

    for module in modules:
        module_path = src_path / module
        if not module_path.exists():
            print(f"  ❌ Модуль {module} - ДИРЕКТОРИЯ НЕ НАЙДЕНА")
            all_module_files_ok = False
            continue

        print(f"  📦 Модуль {module}:")

        for file_name in required_module_files:
            file_path = module_path / file_name
            if file_path.exists():
                print(f"    ✅ {file_name}")
            else:
                print(f"    ❌ {file_name} - НЕ НАЙДЕН")
                all_module_files_ok = False

        # Специальная проверка для модулей с дополнительными файлами
        if module in special_files:
            for special_file in special_files[module]:
                file_path = module_path / special_file
                if file_path.exists():
                    print(f"    ✅ {special_file} (специальный)")
                else:
                    print(f"    ❌ {special_file} (специальный) - НЕ НАЙДЕН")
                    all_module_files_ok = False

    # Итоговый результат
    print("\n" + "=" * 50)
    print("📊 РЕЗУЛЬТАТЫ ПРОВЕРКИ:")

    if all_dirs_ok and all_global_files_ok and all_module_files_ok:
        print("✅ ВСЕ ПРОВЕРКИ ПРОШЛИ УСПЕШНО!")
        print("🎉 Структура проекта соответствует fastapi-best-practices")
        return True
    else:
        print("❌ ОБНАРУЖЕНЫ ПРОБЛЕМЫ!")
        if not all_dirs_ok:
            print("  - Проблемы с директориями")
        if not all_global_files_ok:
            print("  - Проблемы с глобальными файлами")
        if not all_module_files_ok:
            print("  - Проблемы с файлами модулей")
        return False


def check_file_sizes():
    """Проверить размеры файлов (базовая проверка)"""

    print("\n📏 ПРОВЕРКА РАЗМЕРОВ ФАЙЛОВ:")

    important_files = [
        "src/main.py",
        "src/config.py",
        "src/database.py",
        "src/exceptions.py",
        "src/models.py",
        "requirements/base.txt",
    ]

    for file_path in important_files:
        full_path = Path("/opt/app/backend") / file_path
        if full_path.exists():
            size = full_path.stat().st_size
            print(f"  📄 {file_path} - {size} байт")
        else:
            print(f"  ❌ {file_path} - ФАЙЛ НЕ НАЙДЕН")


if __name__ == "__main__":
    print("🚀 Запуск проверки структуры проекта...")

    success = check_structure()
    check_file_sizes()

    if success:
        print("\n🎊 ПОЗДРАВЛЯЕМ! Структура проекта успешно создана!")
        print("📋 Следующие шаги:")
        print("  1. Начать миграцию модулей (comments, groups, etc.)")
        print("  2. Создать модуль аутентификации (auth)")
        print("  3. Протестировать новую структуру")
        sys.exit(0)
    else:
        print("\n💥 ОБНАРУЖЕНЫ ПРОБЛЕМЫ СО СТРУКТУРОЙ!")
        print("🔧 Исправьте проблемы перед продолжением миграции")
        sys.exit(1)

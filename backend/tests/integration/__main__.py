"""
Запуск интеграционных тестов VK Comments Parser

Использование:
    python -m tests.integration
    python tests/integration/
"""

import sys
import subprocess
from pathlib import Path


def main():
    """Главная функция для запуска интеграционных тестов"""
    project_root = Path(__file__).parent.parent.parent

    # Команда для запуска pytest
    cmd = [
        sys.executable, "-m", "pytest",
        str(project_root / "tests" / "integration"),
        "-v",
        "--tb=short",
        "--strict-markers",
        "--disable-warnings"
    ]

    # Добавляем дополнительные аргументы из командной строки
    if len(sys.argv) > 1:
        cmd.extend(sys.argv[1:])

    print("🚀 Запуск интеграционных тестов VK Comments Parser")
    print(f"📂 Каталог: {project_root / 'tests' / 'integration'}")
    print(f"⚡ Команда: {' '.join(cmd)}")
    print("-" * 60)

    try:
        result = subprocess.run(cmd, cwd=project_root)
        sys.exit(result.returncode)
    except KeyboardInterrupt:
        print("\n⏹️  Тесты прерваны пользователем")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Ошибка запуска тестов: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

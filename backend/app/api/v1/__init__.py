"""
API v1 модуль

Этот пакет содержит все API эндпоинты версии 1.0
для VK Comments Parser.
"""

from . import (
    api,
    background_tasks,
    comments,
    dependencies,
    errors,
    exceptions,
    groups,
    health,
    keywords,
    monitoring,
    morphological,
    parser,
    settings,
    stats,
    utils,
)

__all__ = [
    "api",
    "background_tasks",
    "comments",
    "dependencies",
    "errors",
    "exceptions",
    "groups",
    "health",
    "keywords",
    "monitoring",
    "morphological",
    "parser",
    "settings",
    "stats",
    "utils",
]

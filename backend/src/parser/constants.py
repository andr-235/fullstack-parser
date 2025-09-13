"""
Константы модуля Parser

Содержит основные константы используемые в модуле парсера
"""

# Статусы задач
TASK_STATUS_PENDING = "pending"
TASK_STATUS_RUNNING = "running"
TASK_STATUS_COMPLETED = "completed"
TASK_STATUS_FAILED = "failed"
TASK_STATUS_STOPPED = "stopped"

# Приоритеты задач
TASK_PRIORITY_LOW = "low"
TASK_PRIORITY_NORMAL = "normal"
TASK_PRIORITY_HIGH = "high"

# VK API константы
VK_API_POSTS_FIELDS = "id,text,date,likes,reposts,comments"
VK_API_COMMENTS_FIELDS = "id,text,date,likes,thread"
VK_API_GROUP_FIELDS = "id,name,screen_name,description,members_count,photo_200,is_closed"
VK_API_USER_FIELDS = "id,first_name,last_name,screen_name,photo_100"

# Размеры батчей
BATCH_SIZE_POSTS = 100
BATCH_SIZE_COMMENTS = 100
BATCH_SIZE_SAVE = 50

# Экспорт
__all__ = [
    "TASK_STATUS_PENDING",
    "TASK_STATUS_RUNNING",
    "TASK_STATUS_COMPLETED",
    "TASK_STATUS_FAILED",
    "TASK_STATUS_STOPPED",
    "TASK_PRIORITY_LOW",
    "TASK_PRIORITY_NORMAL",
    "TASK_PRIORITY_HIGH",
    "VK_API_POSTS_FIELDS",
    "VK_API_COMMENTS_FIELDS",
    "VK_API_GROUP_FIELDS",
    "VK_API_USER_FIELDS",
    "BATCH_SIZE_POSTS",
    "BATCH_SIZE_COMMENTS",
    "BATCH_SIZE_SAVE",
]

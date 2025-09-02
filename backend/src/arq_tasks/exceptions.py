"""
Исключения для ARQ модуля

Содержит пользовательские исключения для работы с асинхронными задачами.
"""


class ArqException(Exception):
    """
    Базовое исключение для ARQ модуля
    """

    pass


class ArqServiceNotInitializedError(ArqException):
    """
    Исключение, когда ARQ сервис не инициализирован
    """

    def __init__(self, message: str = "ARQ сервис не инициализирован"):
        self.message = message
        super().__init__(self.message)


class TaskNotFoundError(ArqException):
    """
    Исключение, когда задача не найдена
    """

    def __init__(self, job_id: str):
        self.job_id = job_id
        self.message = f"Задача с ID '{job_id}' не найдена"
        super().__init__(self.message)


class TaskEnqueueError(ArqException):
    """
    Исключение при ошибке добавления задачи в очередь
    """

    def __init__(self, function_name: str, error: str = None):
        self.function_name = function_name
        self.error = error
        self.message = (
            f"Не удалось добавить задачу '{function_name}' в очередь"
        )
        if error:
            self.message += f": {error}"
        super().__init__(self.message)


class TaskTimeoutError(ArqException):
    """
    Исключение при превышении таймаута выполнения задачи
    """

    def __init__(self, job_id: str, timeout: int):
        self.job_id = job_id
        self.timeout = timeout
        self.message = f"Задача '{job_id}' превысила таймаут {timeout} секунд"
        super().__init__(self.message)


class TaskMaxRetriesError(ArqException):
    """
    Исключение при превышении максимального количества попыток
    """

    def __init__(self, job_id: str, max_tries: int):
        self.job_id = job_id
        self.max_tries = max_tries
        self.message = f"Задача '{job_id}' превысила максимальное количество попыток ({max_tries})"
        super().__init__(self.message)


class ArqConfigurationError(ArqException):
    """
    Исключение при ошибке конфигурации ARQ
    """

    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)


class RedisConnectionError(ArqException):
    """
    Исключение при ошибке подключения к Redis
    """

    def __init__(self, message: str = "Ошибка подключения к Redis"):
        self.message = message
        super().__init__(self.message)


class TaskValidationError(ArqException):
    """
    Исключение при ошибке валидации задачи
    """

    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)


class CronJobError(ArqException):
    """
    Исключение при работе с cron задачами
    """

    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)

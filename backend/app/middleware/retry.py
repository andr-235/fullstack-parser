"""
Retry middleware for handling temporary failures.
Provides automatic retry logic for VK API and other external service calls.
"""

import asyncio
import time
from typing import Callable, Any, Optional
from functools import wraps
from structlog import get_logger

from ..core.exceptions import (
    VKAPIError,
    RateLimitError,
    ServiceUnavailableError,
)

logger = get_logger()


class RetryConfig:
    """Configuration for retry behavior."""

    def __init__(
        self,
        max_retries: int = 3,
        base_delay: float = 1.0,
        max_delay: float = 60.0,
        exponential_backoff: bool = True,
        retry_on_exceptions: tuple = (
            VKAPIError,
            RateLimitError,
            ServiceUnavailableError,
        ),
    ):
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.exponential_backoff = exponential_backoff
        self.retry_on_exceptions = retry_on_exceptions


def retry_async(
    max_retries: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    exponential_backoff: bool = True,
    retry_on_exceptions: tuple = (
        VKAPIError,
        RateLimitError,
        ServiceUnavailableError,
    ),
):
    """
    Decorator for async functions with retry logic.

    Args:
        max_retries: Maximum number of retry attempts
        base_delay: Base delay between retries in seconds
        max_delay: Maximum delay between retries in seconds
        exponential_backoff: Whether to use exponential backoff
        retry_on_exceptions: Tuple of exceptions to retry on
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            last_exception = None

            for attempt in range(max_retries + 1):
                try:
                    return await func(*args, **kwargs)

                except retry_on_exceptions as e:
                    last_exception = e

                    if attempt == max_retries:
                        logger.error(
                            "Max retries exceeded",
                            function=func.__name__,
                            max_retries=max_retries,
                            final_exception=str(e),
                        )
                        raise

                    # Calculate delay
                    if exponential_backoff:
                        delay = min(base_delay * (2**attempt), max_delay)
                    else:
                        delay = base_delay

                    # Handle rate limit errors
                    if isinstance(e, RateLimitError) and e.retry_after:
                        delay = max(delay, e.retry_after)

                    logger.warning(
                        "Retry attempt",
                        function=func.__name__,
                        attempt=attempt + 1,
                        max_retries=max_retries,
                        delay=delay,
                        exception=str(e),
                    )

                    await asyncio.sleep(delay)

                except Exception as e:
                    # Don't retry on non-retryable exceptions
                    logger.error(
                        "Non-retryable exception",
                        function=func.__name__,
                        exception=str(e),
                        exception_type=type(e).__name__,
                    )
                    raise

            # This should never be reached, but just in case
            if last_exception:
                raise last_exception

        return wrapper

    return decorator


class RetryMiddleware:
    """FastAPI middleware for automatic retry on specific endpoints."""

    def __init__(self, app, config: Optional[RetryConfig] = None):
        self.app = app
        self.config = config or RetryConfig()

    async def __call__(self, scope, receive, send):
        """Process request with retry logic for specific endpoints."""

        # Only apply retry to VK API related endpoints
        path = scope.get("path", "")
        if "/api/v1/vk/" in path:
            return await self._retry_request(scope, receive, send)

        # Call the next middleware/app
        await self.app(scope, receive, send)

    async def _retry_request(self, scope, receive, send):
        """Retry request with exponential backoff."""

        last_exception = None
        path = scope.get("path", "")

        for attempt in range(self.config.max_retries + 1):
            try:
                # Call the next middleware/app
                await self.app(scope, receive, send)
                return

            except Exception as e:
                last_exception = e

                if attempt == self.config.max_retries:
                    logger.error(
                        "Max retries exceeded for request",
                        path=path,
                        max_retries=self.config.max_retries,
                        final_exception=str(e),
                    )
                    raise

                # Calculate delay
                if self.config.exponential_backoff:
                    delay = min(
                        self.config.base_delay * (2**attempt),
                        self.config.max_delay,
                    )
                else:
                    delay = self.config.base_delay

                logger.warning(
                    "Retry request",
                    path=path,
                    attempt=attempt + 1,
                    max_retries=self.config.max_retries,
                    delay=delay,
                    exception=str(e),
                )

                await asyncio.sleep(delay)

        if last_exception:
            raise last_exception


def create_retry_config(
    max_retries: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    exponential_backoff: bool = True,
) -> RetryConfig:
    """Create a retry configuration."""
    return RetryConfig(
        max_retries=max_retries,
        base_delay=base_delay,
        max_delay=max_delay,
        exponential_backoff=exponential_backoff,
    )

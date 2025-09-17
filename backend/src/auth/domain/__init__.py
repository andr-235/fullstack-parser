"""
Доменный слой аутентификации
"""

from .entities import User, UserStatus, TokenType, SecurityEventType, TokenData, SecurityEvent, LoginAttempt
from .exceptions import (
    AuthDomainException,
    InvalidCredentialsError,
    InvalidTokenError,
    TokenExpiredError,
    UserAlreadyExistsError,
    UserNotFoundError,
    UserInactiveError,
    UserLockedError,
    TooManyLoginAttemptsError,
    PasswordTooWeakError,
    InvalidPasswordResetTokenError,
)
from .interfaces import (
    IUserRepository,
    ICacheService,
    IEventService,
    IUnitOfWork,
    IAuthenticationService,
    IAuthorizationService,
    ITokenService,
    IPasswordService,
    IUserManagementService,
)

__all__ = [
    # Entities
    "User",
    "UserStatus", 
    "TokenType",
    "SecurityEventType",
    "TokenData",
    "SecurityEvent",
    "LoginAttempt",
    
    # Exceptions
    "AuthDomainException",
    "InvalidCredentialsError",
    "InvalidTokenError", 
    "TokenExpiredError",
    "UserAlreadyExistsError",
    "UserNotFoundError",
    "UserInactiveError",
    "UserLockedError",
    "TooManyLoginAttemptsError",
    "PasswordTooWeakError",
    "InvalidPasswordResetTokenError",
    
    # Interfaces
    "IUserRepository",
    "ICacheService",
    "IEventService", 
    "IUnitOfWork",
    "IAuthenticationService",
    "IAuthorizationService",
    "ITokenService",
    "IPasswordService",
    "IUserManagementService",
]

/**
 * Утилиты для работы с JWT токенами
 */

import type { AuthTokens } from '../types'

/**
 * Интерфейс для декодированного JWT токена
 */
interface DecodedToken {
  exp: number
  iat: number
  sub: string
  email?: string
  roles?: string[]
  [key: string]: any
}

/**
 * Класс для работы с JWT токенами
 */
export class TokenUtils {
  /**
   * Декодирование JWT токена без верификации
   * @param token - JWT токен
   * @returns Декодированный токен или null при ошибке
   */
  static decodeToken(token: string): DecodedToken | null {
    try {
      const payload = token.split('.')[1]
      if (!payload) return null

      const decoded = JSON.parse(atob(payload))
      return decoded
    } catch (error) {
      console.error('Ошибка декодирования токена:', error)
      return null
    }
  }

  /**
   * Проверка срока действия токена
   * @param token - JWT токен
   * @param thresholdMinutes - Порог в минутах до истечения (по умолчанию 5)
   * @returns true если токен действителен и не истекает в ближайшее время
   */
  static isTokenValid(token: string, thresholdMinutes: number = 5): boolean {
    const decoded = this.decodeToken(token)
    if (!decoded || !decoded.exp) return false

    const now = Math.floor(Date.now() / 1000)
    const threshold = thresholdMinutes * 60

    return decoded.exp > (now + threshold)
  }

  /**
   * Получение времени до истечения токена в минутах
   * @param token - JWT токен
   * @returns Время в минутах или -1 если токен недействителен
   */
  static getTokenExpirationTime(token: string): number {
    const decoded = this.decodeToken(token)
    if (!decoded || !decoded.exp) return -1

    const now = Math.floor(Date.now() / 1000)
    const timeLeft = decoded.exp - now

    return Math.floor(timeLeft / 60)
  }

  /**
   * Извлечение email из токена
   * @param token - JWT токен
   * @returns Email пользователя или null
   */
  static getEmailFromToken(token: string): string | null {
    const decoded = this.decodeToken(token)
    return decoded?.email || null
  }

  /**
   * Извлечение ролей из токена
   * @param token - JWT токен
   * @returns Массив ролей или пустой массив
   */
  static getRolesFromToken(token: string): string[] {
    const decoded = this.decodeToken(token)
    return decoded?.roles || []
  }

  /**
   * Извлечение ID пользователя из токена
   * @param token - JWT токен
   * @returns ID пользователя или null
   */
  static getUserIdFromToken(token: string): string | null {
    const decoded = this.decodeToken(token)
    return decoded?.sub || null
  }

  /**
   * Проверка наличия роли в токене
   * @param token - JWT токен
   * @param role - Роль для проверки
   * @returns true если роль присутствует
   */
  static hasRoleInToken(token: string, role: string): boolean {
    const roles = this.getRolesFromToken(token)
    return roles.includes(role)
  }

  /**
   * Проверка наличия любой из ролей в токене
   * @param token - JWT токен
   * @param roles - Массив ролей для проверки
   * @returns true если хотя бы одна роль присутствует
   */
  static hasAnyRoleInToken(token: string, roles: string[]): boolean {
    const userRoles = this.getRolesFromToken(token)
    return roles.some(role => userRoles.includes(role))
  }

  /**
   * Сохранение токенов в localStorage
   * @param tokens - Объект с токенами
   */
  static saveTokens(tokens: AuthTokens): void {
    try {
      localStorage.setItem('access_token', tokens.access_token)
      localStorage.setItem('refresh_token', tokens.refresh_token)
      localStorage.setItem('token_type', tokens.token_type)
      localStorage.setItem('expires_in', tokens.expires_in.toString())
    } catch (error) {
      console.error('Ошибка сохранения токенов:', error)
    }
  }

  /**
   * Загрузка токенов из localStorage
   * @returns Объект с токенами или null
   */
  static loadTokens(): AuthTokens | null {
    try {
      const accessToken = localStorage.getItem('access_token')
      const refreshToken = localStorage.getItem('refresh_token')
      const tokenType = localStorage.getItem('token_type')
      const expiresIn = localStorage.getItem('expires_in')

      if (!accessToken || !refreshToken || !tokenType || !expiresIn) {
        return null
      }

      return {
        access_token: accessToken,
        refresh_token: refreshToken,
        token_type: tokenType,
        expires_in: parseInt(expiresIn, 10)
      }
    } catch (error) {
      console.error('Ошибка загрузки токенов:', error)
      return null
    }
  }

  /**
   * Удаление токенов из localStorage
   */
  static clearTokens(): void {
    try {
      localStorage.removeItem('access_token')
      localStorage.removeItem('refresh_token')
      localStorage.removeItem('token_type')
      localStorage.removeItem('expires_in')
    } catch (error) {
      console.error('Ошибка удаления токенов:', error)
    }
  }

  /**
   * Обновление access токена в localStorage
   * @param accessToken - Новый access токен
   */
  static updateAccessToken(accessToken: string): void {
    try {
      localStorage.setItem('access_token', accessToken)
    } catch (error) {
      console.error('Ошибка обновления access токена:', error)
    }
  }

  /**
   * Генерация заголовка Authorization
   * @param token - JWT токен
   * @param tokenType - Тип токена (по умолчанию Bearer)
   * @returns Строка заголовка Authorization
   */
  static generateAuthHeader(token: string, tokenType: string = 'Bearer'): string {
    return `${tokenType} ${token}`
  }
}

/**
 * Утилиты для работы с авторизацией
 */
export class AuthUtils {
  /**
   * Проверка прав доступа на основе ролей
   * @param userRoles - Роли пользователя
   * @param requiredRoles - Требуемые роли
   * @param requireAll - Требовать все роли (по умолчанию false)
   * @returns true если доступ разрешен
   */
  static hasPermission(
    userRoles: string[],
    requiredRoles: string[],
    requireAll: boolean = false
  ): boolean {
    if (requiredRoles.length === 0) return true
    if (userRoles.length === 0) return false

    if (requireAll) {
      return requiredRoles.every(role => userRoles.includes(role))
    } else {
      return requiredRoles.some(role => userRoles.includes(role))
    }
  }

  /**
   * Проверка прав доступа на основе разрешений
   * @param userPermissions - Разрешения пользователя
   * @param requiredPermissions - Требуемые разрешения
   * @param requireAll - Требовать все разрешения (по умолчанию false)
   * @returns true если доступ разрешен
   */
  static hasPermissions(
    userPermissions: string[],
    requiredPermissions: string[],
    requireAll: boolean = false
  ): boolean {
    if (requiredPermissions.length === 0) return true
    if (userPermissions.length === 0) return false

    if (requireAll) {
      return requiredPermissions.every(permission => userPermissions.includes(permission))
    } else {
      return requiredPermissions.some(permission => userPermissions.includes(permission))
    }
  }

  /**
   * Получение ролей пользователя из токена
   * @param token - JWT токен
   * @returns Массив ролей
   */
  static getUserRoles(token: string): string[] {
    return TokenUtils.getRolesFromToken(token)
  }

  /**
   * Получение разрешений пользователя из токена
   * @param token - JWT токен
   * @returns Массив разрешений
   */
  static getUserPermissions(token: string): string[] {
    const decoded = TokenUtils.decodeToken(token)
    return decoded?.permissions || []
  }

  /**
   * Проверка является ли пользователь администратором
   * @param token - JWT токен
   * @returns true если пользователь администратор
   */
  static isAdmin(token: string): boolean {
    return TokenUtils.hasRoleInToken(token, 'admin')
  }

  /**
   * Проверка является ли пользователь модератором
   * @param token - JWT токен
   * @returns true если пользователь модератор
   */
  static isModerator(token: string): boolean {
    return TokenUtils.hasRoleInToken(token, 'moderator')
  }

  /**
   * Проверка является ли пользователь премиум пользователем
   * @param token - JWT токен
   * @returns true если пользователь премиум
   */
  static isPremium(token: string): boolean {
    return TokenUtils.hasRoleInToken(token, 'premium')
  }

  /**
   * Получение уровня доступа пользователя
   * @param token - JWT токен
   * @returns Числовой уровень доступа
   */
  static getAccessLevel(token: string): number {
    const roles = TokenUtils.getRolesFromToken(token)

    if (roles.includes('admin')) return 100
    if (roles.includes('moderator')) return 50
    if (roles.includes('premium')) return 10

    return 1 // обычный пользователь
  }
}

/**
 * Утилиты для работы с localStorage
 */
export class StorageUtils {
  /**
   * Безопасная установка значения в localStorage
   * @param key - Ключ
   * @param value - Значение
   */
  static setItem(key: string, value: string): void {
    try {
      localStorage.setItem(key, value)
    } catch (error) {
      console.error(`Ошибка сохранения в localStorage (${key}):`, error)
    }
  }

  /**
   * Безопасное получение значения из localStorage
   * @param key - Ключ
   * @returns Значение или null
   */
  static getItem(key: string): string | null {
    try {
      return localStorage.getItem(key)
    } catch (error) {
      console.error(`Ошибка чтения из localStorage (${key}):`, error)
      return null
    }
  }

  /**
   * Безопасное удаление значения из localStorage
   * @param key - Ключ
   */
  static removeItem(key: string): void {
    try {
      localStorage.removeItem(key)
    } catch (error) {
      console.error(`Ошибка удаления из localStorage (${key}):`, error)
    }
  }

  /**
   * Очистка всех данных аутентификации
   */
  static clearAuthData(): void {
    this.removeItem('access_token')
    this.removeItem('refresh_token')
    this.removeItem('token_type')
    this.removeItem('expires_in')
    this.removeItem('user_data')
  }
}
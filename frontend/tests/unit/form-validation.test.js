import { describe, it, expect } from 'vitest'

/**
 * Тесты валидации форм
 * Эти функции валидации используются в модальных окнах создания задач
 */

describe('Comments Task Form Validation', () => {
  // Валидация Owner ID
  const ownerIdRules = [
    (value) => !!value || 'Owner ID обязателен',
    (value) => !isNaN(value) || 'Owner ID должен быть числом',
    (value) => parseInt(value) < 0 || 'Owner ID должен быть отрицательным числом'
  ]

  describe('Owner ID validation', () => {
    it('should reject empty value', () => {
      const result = ownerIdRules[0]('')
      expect(result).toBe('Owner ID обязателен')
    })

    it('should reject null value', () => {
      const result = ownerIdRules[0](null)
      expect(result).toBe('Owner ID обязателен')
    })

    it('should reject non-numeric value', () => {
      const result = ownerIdRules[1]('abc')
      expect(result).toBe('Owner ID должен быть числом')
    })

    it('should reject positive number', () => {
      const result = ownerIdRules[2]('123')
      expect(result).toBe('Owner ID должен быть отрицательным числом')
    })

    it('should reject zero', () => {
      const result = ownerIdRules[2]('0')
      expect(result).toBe('Owner ID должен быть отрицательным числом')
    })

    it('should accept negative number', () => {
      const value = '-123'
      const result1 = ownerIdRules[0](value)
      const result2 = ownerIdRules[1](value)
      const result3 = ownerIdRules[2](value)

      expect(result1).toBe(true)
      expect(result2).toBe(true)
      expect(result3).toBe(true)
    })
  })

  // Валидация Post ID
  const postIdRules = [
    (value) => !!value || 'Post ID обязателен',
    (value) => !isNaN(value) || 'Post ID должен быть числом',
    (value) => parseInt(value) > 0 || 'Post ID должен быть положительным числом'
  ]

  describe('Post ID validation', () => {
    it('should reject empty value', () => {
      const result = postIdRules[0]('')
      expect(result).toBe('Post ID обязателен')
    })

    it('should reject non-numeric value', () => {
      const result = postIdRules[1]('abc')
      expect(result).toBe('Post ID должен быть числом')
    })

    it('should reject negative number', () => {
      const result = postIdRules[2]('-123')
      expect(result).toBe('Post ID должен быть положительным числом')
    })

    it('should reject zero', () => {
      const result = postIdRules[2]('0')
      expect(result).toBe('Post ID должен быть положительным числом')
    })

    it('should accept positive number', () => {
      const value = '123'
      const result1 = postIdRules[0](value)
      const result2 = postIdRules[1](value)
      const result3 = postIdRules[2](value)

      expect(result1).toBe(true)
      expect(result2).toBe(true)
      expect(result3).toBe(true)
    })
  })

  // Валидация токена
  const tokenRules = [
    (value) => !!value || 'VK токен обязателен',
    (value) => value.length >= 10 || 'VK токен слишком короткий'
  ]

  describe('Token validation', () => {
    it('should reject empty value', () => {
      const result = tokenRules[0]('')
      expect(result).toBe('VK токен обязателен')
    })

    it('should reject short token', () => {
      const result = tokenRules[1]('short')
      expect(result).toBe('VK токен слишком короткий')
    })

    it('should accept valid token', () => {
      const value = 'valid_long_token_123'
      const result1 = tokenRules[0](value)
      const result2 = tokenRules[1](value)

      expect(result1).toBe(true)
      expect(result2).toBe(true)
    })
  })
})

describe('VK Collect Task Form Validation', () => {
  // Симуляция парсинга групп
  const parseGroups = (input) => {
    if (!input.trim()) return { groups: [], errors: [] }

    const lines = input
      .split(/[,\n\r]/)
      .map(line => line.trim())
      .filter(line => line.length > 0)

    const groups = []
    const errors = []

    lines.forEach((line, index) => {
      const num = parseInt(line)
      if (isNaN(num)) {
        errors.push(`Строка ${index + 1}: "${line}" не является числом`)
      } else if (num <= 0) {
        errors.push(`Строка ${index + 1}: ${num} должно быть положительным числом`)
      } else if (groups.includes(num)) {
        errors.push(`Строка ${index + 1}: ${num} уже добавлен`)
      } else {
        groups.push(num)
      }
    })

    return { groups, errors }
  }

  describe('Groups parsing', () => {
    it('should handle empty input', () => {
      const result = parseGroups('')
      expect(result.groups).toEqual([])
      expect(result.errors).toEqual([])
    })

    it('should parse valid groups separated by newlines', () => {
      const result = parseGroups('12345\n67890\n11111')
      expect(result.groups).toEqual([12345, 67890, 11111])
      expect(result.errors).toEqual([])
    })

    it('should parse valid groups separated by commas', () => {
      const result = parseGroups('12345,67890,11111')
      expect(result.groups).toEqual([12345, 67890, 11111])
      expect(result.errors).toEqual([])
    })

    it('should handle mixed separators', () => {
      const result = parseGroups('12345,67890\n11111')
      expect(result.groups).toEqual([12345, 67890, 11111])
      expect(result.errors).toEqual([])
    })

    it('should ignore empty lines', () => {
      const result = parseGroups('12345\n\n67890\n')
      expect(result.groups).toEqual([12345, 67890])
      expect(result.errors).toEqual([])
    })

    it('should detect non-numeric values', () => {
      const result = parseGroups('12345\nabc\n67890')
      expect(result.groups).toEqual([12345, 67890])
      expect(result.errors).toHaveLength(1)
      expect(result.errors[0]).toContain('не является числом')
    })

    it('should detect negative numbers', () => {
      const result = parseGroups('12345\n-67890\n11111')
      expect(result.groups).toEqual([12345, 11111])
      expect(result.errors).toHaveLength(1)
      expect(result.errors[0]).toContain('должно быть положительным числом')
    })

    it('should detect zero', () => {
      const result = parseGroups('12345\n0\n11111')
      expect(result.groups).toEqual([12345, 11111])
      expect(result.errors).toHaveLength(1)
      expect(result.errors[0]).toContain('должно быть положительным числом')
    })

    it('should detect duplicates', () => {
      const result = parseGroups('12345\n67890\n12345')
      expect(result.groups).toEqual([12345, 67890])
      expect(result.errors).toHaveLength(1)
      expect(result.errors[0]).toContain('уже добавлен')
    })

    it('should handle multiple errors', () => {
      const result = parseGroups('12345\nabc\n-67890\n12345\n0')
      expect(result.groups).toEqual([12345])
      expect(result.errors).toHaveLength(4)
    })
  })

  // Валидация групп для формы
  const groupsRules = [
    (value) => !!value.trim() || 'Список групп обязателен',
    (value) => {
      const parsed = parseGroups(value)
      return parsed.groups.length > 0 || 'Необходимо указать хотя бы одну корректную группу'
    },
    (value) => {
      const parsed = parseGroups(value)
      return parsed.errors.length === 0 || 'Исправьте ошибки в списке групп'
    }
  ]

  describe('Groups validation rules', () => {
    it('should reject empty input', () => {
      const result = groupsRules[0]('')
      expect(result).toBe('Список групп обязателен')
    })

    it('should reject input with no valid groups', () => {
      const result = groupsRules[1]('abc\ndef')
      expect(result).toBe('Необходимо указать хотя бы одну корректную группу')
    })

    it('should reject input with errors', () => {
      const result = groupsRules[2]('12345\nabc\n67890')
      expect(result).toBe('Исправьте ошибки в списке групп')
    })

    it('should accept valid input', () => {
      const value = '12345\n67890\n11111'
      const result1 = groupsRules[0](value)
      const result2 = groupsRules[1](value)
      const result3 = groupsRules[2](value)

      expect(result1).toBe(true)
      expect(result2).toBe(true)
      expect(result3).toBe(true)
    })
  })
})

describe('File Upload Validation', () => {
  // Симуляция валидации файлов
  const validateFile = (file) => {
    if (!file) {
      return 'Выберите файл для загрузки'
    }

    // Проверка расширения файла
    const allowedExtensions = ['.txt', '.csv']
    const extension = '.' + file.name.split('.').pop().toLowerCase()
    if (!allowedExtensions.includes(extension)) {
      return 'Поддерживаются только файлы TXT и CSV'
    }

    // Проверка размера файла (10MB лимит)
    const maxSize = 10 * 1024 * 1024 // 10MB
    if (file.size > maxSize) {
      return 'Размер файла не должен превышать 10 МБ'
    }

    return true
  }

  describe('File validation', () => {
    it('should reject null file', () => {
      const result = validateFile(null)
      expect(result).toBe('Выберите файл для загрузки')
    })

    it('should reject undefined file', () => {
      const result = validateFile(undefined)
      expect(result).toBe('Выберите файл для загрузки')
    })

    it('should reject file with invalid extension', () => {
      const file = { name: 'test.jpg', size: 1000 }
      const result = validateFile(file)
      expect(result).toBe('Поддерживаются только файлы TXT и CSV')
    })

    it('should reject file that is too large', () => {
      const file = { name: 'test.txt', size: 15 * 1024 * 1024 } // 15MB
      const result = validateFile(file)
      expect(result).toBe('Размер файла не должен превышать 10 МБ')
    })

    it('should accept valid TXT file', () => {
      const file = { name: 'test.txt', size: 1024 }
      const result = validateFile(file)
      expect(result).toBe(true)
    })

    it('should accept valid CSV file', () => {
      const file = { name: 'test.csv', size: 1024 }
      const result = validateFile(file)
      expect(result).toBe(true)
    })

    it('should handle case insensitive extensions', () => {
      const file = { name: 'test.TXT', size: 1024 }
      const result = validateFile(file)
      expect(result).toBe(true)
    })
  })
})
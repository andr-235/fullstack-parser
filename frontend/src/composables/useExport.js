import { ref } from 'vue'

/**
 * Composable для экспорта данных в различные форматы
 *
 * @returns {Object} Объект с методами экспорта
 */
export function useExport() {
  const isExporting = ref(false)
  const exportProgress = ref(0)
  const exportError = ref(null)

  /**
   * Экспортирует данные в CSV формат
   *
   * @param {Array} data - Данные для экспорта
   * @param {Array|Object} columns - Конфигурация колонок
   * @param {string} filename - Имя файла
   * @param {Object} options - Дополнительные настройки
   */
  const exportToCSV = (data, columns, filename = 'export.csv', options = {}) => {
    const {
      delimiter = ',',
      includeHeaders = true,
      encoding = 'utf-8',
      dateFormat = 'dd.MM.yyyy HH:mm'
    } = options

    try {
      isExporting.value = true
      exportError.value = null

      // Нормализация колонок
      const normalizedColumns = Array.isArray(columns)
        ? columns.map(col => typeof col === 'string' ? { key: col, title: col } : col)
        : Object.entries(columns).map(([key, title]) => ({ key, title }))

      const csvRows = []

      // Добавление заголовков
      if (includeHeaders) {
        const headers = normalizedColumns.map(col => `"${col.title}"`)
        csvRows.push(headers.join(delimiter))
      }

      // Обработка данных
      data.forEach((item, index) => {
        exportProgress.value = Math.round(((index + 1) / data.length) * 100)

        const row = normalizedColumns.map(col => {
          let value = getNestedValue(item, col.key)

          // Форматирование значения
          if (col.formatter && typeof col.formatter === 'function') {
            value = col.formatter(value, item)
          } else if (value instanceof Date) {
            value = formatDate(value, dateFormat)
          } else if (value === null || value === undefined) {
            value = ''
          } else if (typeof value === 'object') {
            value = JSON.stringify(value)
          }

          // Экранирование кавычек и обертывание в кавычки
          return `"${String(value).replace(/"/g, '""')}"`
        })

        csvRows.push(row.join(delimiter))
      })

      const csvContent = csvRows.join('\n')
      downloadFile(csvContent, filename, 'text/csv', encoding)

      exportProgress.value = 100
    } catch (error) {
      exportError.value = error.message || 'Ошибка экспорта в CSV'
      throw error
    } finally {
      isExporting.value = false
      setTimeout(() => {
        exportProgress.value = 0
      }, 2000)
    }
  }

  /**
   * Экспортирует данные в JSON формат
   *
   * @param {*} data - Данные для экспорта
   * @param {string} filename - Имя файла
   * @param {Object} options - Дополнительные настройки
   */
  const exportToJSON = (data, filename = 'export.json', options = {}) => {
    const {
      pretty = true,
      includeMetadata = true
    } = options

    try {
      isExporting.value = true
      exportError.value = null

      let exportData = data

      if (includeMetadata) {
        exportData = {
          metadata: {
            exportedAt: new Date().toISOString(),
            totalRecords: Array.isArray(data) ? data.length : 1,
            format: 'JSON'
          },
          data
        }
      }

      const jsonContent = pretty
        ? JSON.stringify(exportData, null, 2)
        : JSON.stringify(exportData)

      downloadFile(jsonContent, filename, 'application/json', 'utf-8')
      exportProgress.value = 100
    } catch (error) {
      exportError.value = error.message || 'Ошибка экспорта в JSON'
      throw error
    } finally {
      isExporting.value = false
      setTimeout(() => {
        exportProgress.value = 0
      }, 2000)
    }
  }

  /**
   * Экспортирует данные в XML формат
   *
   * @param {*} data - Данные для экспорта
   * @param {string} filename - Имя файла
   * @param {Object} options - Дополнительные настройки
   */
  const exportToXML = (data, filename = 'export.xml', options = {}) => {
    const {
      rootElement = 'export',
      itemElement = 'item',
      includeHeader = true
    } = options

    try {
      isExporting.value = true
      exportError.value = null

      let xml = ''

      if (includeHeader) {
        xml += '<?xml version="1.0" encoding="UTF-8"?>\n'
      }

      xml += `<${rootElement}>\n`

      if (Array.isArray(data)) {
        data.forEach((item, index) => {
          exportProgress.value = Math.round(((index + 1) / data.length) * 100)
          xml += `  <${itemElement}>\n`
          xml += objectToXML(item, '    ')
          xml += `  </${itemElement}>\n`
        })
      } else {
        xml += objectToXML(data, '  ')
      }

      xml += `</${rootElement}>`

      downloadFile(xml, filename, 'application/xml', 'utf-8')
      exportProgress.value = 100
    } catch (error) {
      exportError.value = error.message || 'Ошибка экспорта в XML'
      throw error
    } finally {
      isExporting.value = false
      setTimeout(() => {
        exportProgress.value = 0
      }, 2000)
    }
  }

  /**
   * Экспортирует данные в текстовый формат
   *
   * @param {string} content - Содержимое
   * @param {string} filename - Имя файла
   * @param {Object} options - Дополнительные настройки
   */
  const exportToTXT = (content, filename = 'export.txt', options = {}) => {
    const {
      encoding = 'utf-8'
    } = options

    try {
      isExporting.value = true
      exportError.value = null

      downloadFile(content, filename, 'text/plain', encoding)
      exportProgress.value = 100
    } catch (error) {
      exportError.value = error.message || 'Ошибка экспорта в TXT'
      throw error
    } finally {
      isExporting.value = false
      setTimeout(() => {
        exportProgress.value = 0
      }, 2000)
    }
  }

  /**
   * Утилитарная функция для скачивания файла
   *
   * @param {string} content - Содержимое файла
   * @param {string} filename - Имя файла
   * @param {string} mimeType - MIME тип
   * @param {string} encoding - Кодировка
   */
  const downloadFile = (content, filename, mimeType, encoding = 'utf-8') => {
    const blob = new Blob([content], { type: `${mimeType};charset=${encoding}` })
    const url = URL.createObjectURL(blob)

    const link = document.createElement('a')
    link.setAttribute('href', url)
    link.setAttribute('download', filename)
    link.style.visibility = 'hidden'

    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)

    // Освобождение памяти
    setTimeout(() => {
      URL.revokeObjectURL(url)
    }, 1000)
  }

  /**
   * Получает значение по вложенному ключу
   *
   * @param {Object} obj - Объект
   * @param {string} path - Путь к значению (например, 'user.name')
   * @returns {*} Значение
   */
  const getNestedValue = (obj, path) => {
    return path.split('.').reduce((current, key) => {
      return current && current[key] !== undefined ? current[key] : null
    }, obj)
  }

  /**
   * Преобразует объект в XML строку
   *
   * @param {*} obj - Объект для конвертации
   * @param {string} indent - Отступ
   * @returns {string} XML строка
   */
  const objectToXML = (obj, indent = '') => {
    let xml = ''

    for (const [key, value] of Object.entries(obj)) {
      const tagName = key.replace(/[^a-zA-Z0-9_-]/g, '_')

      if (value === null || value === undefined) {
        xml += `${indent}<${tagName}/>\n`
      } else if (typeof value === 'object' && !Array.isArray(value)) {
        xml += `${indent}<${tagName}>\n`
        xml += objectToXML(value, indent + '  ')
        xml += `${indent}</${tagName}>\n`
      } else if (Array.isArray(value)) {
        xml += `${indent}<${tagName}>\n`
        value.forEach(item => {
          xml += `${indent}  <item>\n`
          if (typeof item === 'object') {
            xml += objectToXML(item, indent + '    ')
          } else {
            xml += `${indent}    ${escapeXML(String(item))}\n`
          }
          xml += `${indent}  </item>\n`
        })
        xml += `${indent}</${tagName}>\n`
      } else {
        xml += `${indent}<${tagName}>${escapeXML(String(value))}</${tagName}>\n`
      }
    }

    return xml
  }

  /**
   * Экранирует специальные символы для XML
   *
   * @param {string} str - Строка для экранирования
   * @returns {string} Экранированная строка
   */
  const escapeXML = (str) => {
    return str
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&apos;')
  }

  /**
   * Форматирует дату
   *
   * @param {Date} date - Дата
   * @param {string} format - Формат
   * @returns {string} Отформатированная дата
   */
  const formatDate = (date, format = 'dd.MM.yyyy HH:mm') => {
    if (!(date instanceof Date) || isNaN(date)) {
      return ''
    }

    const pad = (num) => String(num).padStart(2, '0')

    return format
      .replace(/yyyy/g, date.getFullYear())
      .replace(/MM/g, pad(date.getMonth() + 1))
      .replace(/dd/g, pad(date.getDate()))
      .replace(/HH/g, pad(date.getHours()))
      .replace(/mm/g, pad(date.getMinutes()))
      .replace(/ss/g, pad(date.getSeconds()))
  }

  /**
   * Очищает состояние экспорта
   */
  const clearExportState = () => {
    exportError.value = null
    exportProgress.value = 0
    isExporting.value = false
  }

  return {
    // State
    isExporting,
    exportProgress,
    exportError,

    // Methods
    exportToCSV,
    exportToJSON,
    exportToXML,
    exportToTXT,
    downloadFile,
    clearExportState
  }
}

/**
 * Предустановленные форматы экспорта для общих сущностей
 */
export const ExportFormats = {
  tasks: {
    columns: [
      { key: 'id', title: 'ID' },
      { key: 'type', title: 'Тип' },
      { key: 'status', title: 'Статус' },
      { key: 'progress.processed', title: 'Обработано' },
      { key: 'progress.total', title: 'Всего' },
      {
        key: 'createdAt',
        title: 'Создана',
        formatter: (value) => value ? new Date(value).toLocaleString('ru-RU') : ''
      }
    ]
  },

  groups: {
    columns: [
      { key: 'groupId', title: 'ID группы' },
      { key: 'name', title: 'Название' },
      { key: 'status', title: 'Статус' },
      {
        key: 'uploadedAt',
        title: 'Загружена',
        formatter: (value) => value ? new Date(value).toLocaleString('ru-RU') : ''
      },
      { key: 'errorsCount', title: 'Ошибки' }
    ]
  },

  comments: {
    columns: [
      { key: 'id', title: 'ID' },
      { key: 'groupId', title: 'Группа' },
      { key: 'postId', title: 'Пост' },
      { key: 'content', title: 'Содержимое' },
      { key: 'sentiment', title: 'Настроение' },
      { key: 'author.name', title: 'Автор' },
      {
        key: 'date',
        title: 'Дата',
        formatter: (value) => value ? new Date(value).toLocaleString('ru-RU') : ''
      }
    ]
  }
}
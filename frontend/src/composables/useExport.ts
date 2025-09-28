interface ExportOptions {
  delimiter?: string
  includeHeaders?: boolean
  encoding?: string
  dateFormat?: string
}

interface JsonExportOptions {
  pretty?: boolean
  includeMetadata?: boolean
}

interface XmlExportOptions {
  rootElement?: string
  itemElement?: string
  includeHeader?: boolean
}

interface FileExportOptions {
  encoding?: string
}

export function useExport() {
  /**
   * Экспорт данных в CSV формат
   */
  const exportToCSV = (data: any[], columns: any[], options: ExportOptions = {}) => {
    const config: ExportOptions = {
      delimiter: options.delimiter ?? ',',
      includeHeaders: options.includeHeaders ?? true,
      encoding: options.encoding ?? 'utf-8',
      dateFormat: options.dateFormat ?? 'YYYY-MM-DD HH:mm:ss'
    }

    try {
      let csvContent = ''

      // Добавляем заголовки
      if (config.includeHeaders) {
        const headers = columns.map(col => typeof col === 'string' ? col : col.header || col.key)
        csvContent += headers.map(header => `"${header}"`).join(config.delimiter) + '\n'
      }

      // Добавляем данные
      data.forEach((item: any, index: number) => {
        const row = columns.map(col => {
          const key = typeof col === 'string' ? col : col.key
          let value = getNestedValue(item, key)

          // Форматирование значений
          if (value instanceof Date) {
            value = formatDate(value)
          } else if (typeof value === 'object' && value !== null) {
            value = JSON.stringify(value)
          } else if (value === null || value === undefined) {
            value = ''
          }

          // Экранирование кавычек и обертывание в кавычки
          return `"${String(value).replace(/"/g, '""')}"`
        })

        csvContent += row.join(config.delimiter) + '\n'
      })

      downloadFile(csvContent, 'export.csv', 'text/csv')
    } catch (error: any) {
      console.error('Ошибка экспорта в CSV:', error)
      throw new Error('Не удалось экспортировать данные в CSV')
    }
  }

  /**
   * Экспорт данных в JSON формат
   */
  const exportToJSON = (data: any[], options: JsonExportOptions = {}) => {
    const config: JsonExportOptions = {
      pretty: options.pretty ?? true,
      includeMetadata: options.includeMetadata ?? false
    }

    try {
      let exportData: any = data

      if (config.includeMetadata) {
        exportData = {
          metadata: {
            exportDate: new Date().toISOString(),
            totalRecords: data.length,
            version: '1.0'
          },
          data: data
        }
      }

      const jsonContent = config.pretty
        ? JSON.stringify(exportData, null, 2)
        : JSON.stringify(exportData)

      downloadFile(jsonContent, 'export.json', 'application/json')
    } catch (error: any) {
      console.error('Ошибка экспорта в JSON:', error)
      throw new Error('Не удалось экспортировать данные в JSON')
    }
  }

  /**
   * Экспорт данных в XML формат
   */
  const exportToXML = (data: any[], options: XmlExportOptions = {}) => {
    const config: XmlExportOptions = {
      rootElement: options.rootElement ?? 'data',
      itemElement: options.itemElement ?? 'item',
      includeHeader: options.includeHeader ?? true
    }

    try {
      let xmlContent = ''

      if (config.includeHeader) {
        xmlContent += '<?xml version="1.0" encoding="UTF-8"?>\n'
      }

      xmlContent += `<${config.rootElement}>\n`

      data.forEach(item => {
        xmlContent += `  <${config.itemElement}>\n`

        Object.entries(item).forEach(([key, value]) => {
          const escapedValue = String(value || '')
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;')
            .replace(/'/g, '&apos;')

          xmlContent += `    <${key}>${escapedValue}</${key}>\n`
        })

        xmlContent += `  </${config.itemElement}>\n`
      })

      xmlContent += `</${config.rootElement}>`

      downloadFile(xmlContent, 'export.xml', 'application/xml')
    } catch (error: any) {
      console.error('Ошибка экспорта в XML:', error)
      throw new Error('Не удалось экспортировать данные в XML')
    }
  }

  /**
   * Экспорт текстового содержимого в файл
   */
  const exportToFile = (content: any, options: FileExportOptions = {}) => {
    const config: FileExportOptions = {
      encoding: options.encoding ?? 'utf-8'
    }

    try {
      downloadFile(String(content), 'export.txt', 'text/plain')
    } catch (error: any) {
      console.error('Ошибка экспорта в файл:', error)
      throw new Error('Не удалось экспортировать данные в файл')
    }
  }

  /**
   * Универсальная функция для скачивания файла
   */
  const downloadFile = (content: any, filename: any, mimeType: any) => {
    try {
      // Создаем Blob с содержимым
      const blob = new Blob([content], { type: mimeType })

      // Создаем URL для blob
      const url = window.URL.createObjectURL(blob)

      // Создаем временную ссылку для скачивания
      const link = document.createElement('a')
      link.href = url
      link.download = filename

      // Добавляем ссылку в DOM, кликаем и удаляем
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)

      // Освобождаем URL
      window.URL.revokeObjectURL(url)
    } catch (error) {
      console.error('Ошибка скачивания файла:', error)
      throw new Error('Не удалось скачать файл')
    }
  }

  /**
   * Получение вложенного значения по пути
   */
  const getNestedValue = (obj: any, path: any): any => {
    return path.split('.').reduce((current: any, key: any) => current?.[key], obj)
  }

  /**
   * Экранирование CSV значений
   */
  const escapeCSV = (str: any): string => {
    if (typeof str !== 'string') return String(str || '')

    // Если содержит запятую, кавычки или переносы строк - оборачиваем в кавычки
    if (str.includes(',') || str.includes('"') || str.includes('\n') || str.includes('\r')) {
      return `"${str.replace(/"/g, '""')}"`
    }

    return str
  }

  /**
   * Форматирование даты
   */
  const formatDate = (date: any): string => {
    const pad = (num: any) => String(num).padStart(2, '0')

    return `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())} ${pad(date.getHours())}:${pad(date.getMinutes())}:${pad(date.getSeconds())}`
  }

  return {
    exportToCSV,
    exportToJSON,
    exportToXML,
    exportToFile,
    downloadFile
  }
}
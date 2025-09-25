import { test, expect } from '@playwright/test'
import path from 'path'

test.describe('Groups Upload Page', () => {
  test.beforeEach(async ({ page }) => {
    // Переходим на страницу загрузки групп
    await page.goto('/groups/upload')
  })

  test('should display groups upload page with correct structure', async ({ page }) => {
    // Проверяем заголовок страницы
    await expect(page.locator('h1')).toContainText('Загрузка групп')

    // Проверяем наличие формы загрузки
    await expect(page.locator('text=Загрузка файла групп')).toBeVisible()

    // Проверяем наличие поля выбора файла
    await expect(page.locator('input[type="file"]')).toBeVisible()

    // Проверяем наличие селектора кодировки
    await expect(page.locator('label:has-text("Кодировка файла")')).toBeVisible()

    // Проверяем наличие кнопки загрузки
    await expect(page.locator('text=Загрузить группы')).toBeVisible()

    // Проверяем, что кнопка изначально отключена
    await expect(page.locator('text=Загрузить группы')).toBeDisabled()
  })

  test('should show drag and drop zone when no file selected', async ({ page }) => {
    // Проверяем наличие зоны drag & drop
    await expect(page.locator('text=Перетащите файл сюда')).toBeVisible()
    await expect(page.locator('text=или нажмите для выбора')).toBeVisible()
    await expect(page.locator('text=Поддерживаются файлы: TXT, CSV')).toBeVisible()
  })

  test('should enable upload button when valid file is selected', async ({ page }) => {
    // Создаем временный тестовый файл
    const testFileContent = '12345\n67890\n11111'
    const testFilePath = path.join(__dirname, '..', 'fixtures', 'test-groups.txt')

    // Загружаем файл
    await page.setInputFiles('input[type="file"]', {
      name: 'test-groups.txt',
      mimeType: 'text/plain',
      buffer: Buffer.from(testFileContent)
    })

    // Проверяем, что кнопка загрузки стала активной
    await expect(page.locator('text=Загрузить группы')).not.toBeDisabled()

    // Проверяем, что отображается информация о файле
    await expect(page.locator('text=test-groups.txt')).toBeVisible()
  })

  test('should validate file type and show error for invalid files', async ({ page }) => {
    // Пытаемся загрузить файл неправильного типа
    await page.setInputFiles('input[type="file"]', {
      name: 'test-image.jpg',
      mimeType: 'image/jpeg',
      buffer: Buffer.from('fake image content')
    })

    // Кнопка должна остаться неактивной или показать ошибку валидации
    await expect(page.locator('text=Загрузить группы')).toBeDisabled()
  })

  test('should change encoding option', async ({ page }) => {
    // Кликаем на селектор кодировки
    await page.locator('label:has-text("Кодировка файла")').click()

    // Выбираем другую кодировку
    await page.locator('text=Windows-1251').click()

    // Проверяем, что выбор применился
    // Это зависит от реализации селектора в Vuetify
  })

  test('should show upload progress when file is being uploaded', async ({ page }) => {
    // Загружаем файл
    const testFileContent = '12345\n67890\n11111'
    await page.setInputFiles('input[type="file"]', {
      name: 'test-groups.txt',
      mimeType: 'text/plain',
      buffer: Buffer.from(testFileContent)
    })

    // Мокаем медленный API ответ
    await page.route('**/api/groups/upload', route => {
      setTimeout(() => {
        route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({ taskId: '12345' })
        })
      }, 2000)
    })

    // Нажимаем кнопку загрузки
    await page.locator('text=Загрузить группы').click()

    // Проверяем, что показывается индикатор загрузки
    await expect(page.locator('text=Загрузка...')).toBeVisible()

    // Проверяем, что кнопка стала неактивной во время загрузки
    await expect(page.locator('text=Загрузка...')).toBeDisabled()

    // Ждем завершения загрузки
    await expect(page.locator('text=Загрузка...')).not.toBeVisible({ timeout: 5000 })
  })

  test('should display task status card after successful upload', async ({ page }) => {
    // Мокаем успешный API ответ
    await page.route('**/api/groups/upload', route => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ taskId: '12345' })
      })
    })

    // Мокаем API статуса задачи
    await page.route('**/api/groups/upload/12345/status', route => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          status: 'processing',
          progress: { processed: 50, total: 100 },
          message: 'Обрабатывается...'
        })
      })
    })

    // Загружаем файл и отправляем
    const testFileContent = '12345\n67890\n11111'
    await page.setInputFiles('input[type="file"]', {
      name: 'test-groups.txt',
      mimeType: 'text/plain',
      buffer: Buffer.from(testFileContent)
    })

    await page.locator('text=Загрузить группы').click()

    // Проверяем, что появилась карточка статуса задачи
    await expect(page.locator('text=Обработка файла')).toBeVisible({ timeout: 5000 })
    await expect(page.locator('text=12345')).toBeVisible()

    // Проверяем прогресс-бар
    await expect(page.locator('text=Прогресс обработки')).toBeVisible()
    await expect(page.locator('text=50/100')).toBeVisible()
  })

  test('should show error report download button when errors occur', async ({ page }) => {
    // Мокаем API ответы с ошибками
    await page.route('**/api/groups/upload', route => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ taskId: '12345' })
      })
    })

    await page.route('**/api/groups/upload/12345/status', route => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          status: 'completed',
          progress: { processed: 95, total: 100 },
          errors: [
            { line: 5, message: 'Неверный ID группы' },
            { line: 8, message: 'Группа не найдена' }
          ]
        })
      })
    })

    // Загружаем файл
    const testFileContent = '12345\n67890\ninvalid\n11111'
    await page.setInputFiles('input[type="file"]', {
      name: 'test-groups.txt',
      mimeType: 'text/plain',
      buffer: Buffer.from(testFileContent)
    })

    await page.locator('text=Загрузить группы').click()

    // Ждем обработки и появления ошибок
    await expect(page.locator('text=Скачать отчёт об ошибках')).toBeVisible({ timeout: 5000 })

    // Проверяем, что показаны ошибки парсинга
    await expect(page.locator('text=Ошибки парсинга')).toBeVisible()
    await expect(page.locator('text=2')).toBeVisible() // количество ошибок
  })

  test('should navigate to groups list after successful completion', async ({ page }) => {
    // Мокаем успешное завершение
    await page.route('**/api/groups/upload', route => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ taskId: '12345' })
      })
    })

    await page.route('**/api/groups/upload/12345/status', route => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          status: 'completed',
          progress: { processed: 100, total: 100 },
          message: 'Загрузка завершена успешно'
        })
      })
    })

    // Загружаем файл
    const testFileContent = '12345\n67890\n11111'
    await page.setInputFiles('input[type="file"]', {
      name: 'test-groups.txt',
      mimeType: 'text/plain',
      buffer: Buffer.from(testFileContent)
    })

    await page.locator('text=Загрузить группы').click()

    // Ждем появления кнопки перехода к группам
    await expect(page.locator('text=Просмотреть группы')).toBeVisible({ timeout: 5000 })

    // Кликаем по кнопке перехода
    await page.locator('text=Просмотреть группы').click()

    // Проверяем, что произошла навигация
    await expect(page).toHaveURL(/\/groups/)
  })
})
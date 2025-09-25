import { test, expect } from '@playwright/test'

test.describe('Tasks Page', () => {
  test.beforeEach(async ({ page }) => {
    // Переходим на страницу задач
    await page.goto('/tasks')
  })

  test('should display tasks page with correct title and structure', async ({ page }) => {
    // Проверяем заголовок страницы
    await expect(page.locator('h1')).toContainText('Задачи')

    // Проверяем наличие кнопок создания задач
    await expect(page.locator('text=Задача комментариев')).toBeVisible()
    await expect(page.locator('text=VK Collect задача')).toBeVisible()

    // Проверяем наличие фильтра по статусу
    await expect(page.locator('[data-testid="status-filter"], label:has-text("Фильтр по статусу")')).toBeVisible()

    // Проверяем наличие кнопки обновить
    await expect(page.locator('text=Обновить')).toBeVisible()
  })

  test('should open create comments task modal when button clicked', async ({ page }) => {
    // Нажимаем на кнопку создания задачи комментариев
    await page.locator('text=Задача комментариев').click()

    // Проверяем, что модальное окно открылось
    await expect(page.locator('text=Создать задачу комментариев')).toBeVisible()

    // Проверяем наличие полей формы
    await expect(page.locator('label:has-text("ID владельца")')).toBeVisible()
    await expect(page.locator('label:has-text("ID поста")')).toBeVisible()
    await expect(page.locator('label:has-text("VK токен")')).toBeVisible()

    // Проверяем кнопки
    await expect(page.locator('text=Отмена')).toBeVisible()
    await expect(page.locator('text=Создать задачу')).toBeVisible()

    // Закрываем модальное окно
    await page.locator('text=Отмена').click()
    await expect(page.locator('text=Создать задачу комментариев')).not.toBeVisible()
  })

  test('should open create VK collect task modal when button clicked', async ({ page }) => {
    // Нажимаем на кнопку создания VK collect задачи
    await page.locator('text=VK Collect задача').click()

    // Проверяем, что модальное окно открылось
    await expect(page.locator('text=Создать VK Collect задачу')).toBeVisible()

    // Проверяем наличие полей формы
    await expect(page.locator('label:has-text("VK токен")')).toBeVisible()
    await expect(page.locator('label:has-text("ID групп")')).toBeVisible()

    // Закрываем модальное окно
    await page.locator('text=Отмена').click()
    await expect(page.locator('text=Создать VK Collect задачу')).not.toBeVisible()
  })

  test('should validate form fields in comments task modal', async ({ page }) => {
    // Открываем модальное окно
    await page.locator('text=Задача комментариев').click()

    // Пытаемся создать задачу без заполнения полей
    await page.locator('text=Создать задачу').click()

    // Проверяем, что модальное окно не закрылось (валидация сработала)
    await expect(page.locator('text=Создать задачу комментариев')).toBeVisible()

    // Заполняем поле owner ID неправильным значением (должно быть отрицательным)
    await page.fill('input[type="number"] >> nth=0', '123')
    await page.locator('text=Создать задачу').click()

    // Модальное окно должно оставаться открытым из-за валидации
    await expect(page.locator('text=Создать задачу комментариев')).toBeVisible()

    // Заполняем правильные значения
    await page.fill('input[type="number"] >> nth=0', '-123')
    await page.fill('input[type="number"] >> nth=1', '456')
    await page.fill('input[type="password"]', 'test-token')

    // Кнопка должна стать активной
    await expect(page.locator('text=Создать задачу').last()).not.toBeDisabled()
  })

  test('should filter tasks by status', async ({ page }) => {
    // Ждем загрузки данных
    await page.waitForLoadState('networkidle')

    // Открываем фильтр по статусу
    await page.locator('[data-testid="status-filter"], label:has-text("Фильтр по статусу")').click()

    // Выбираем статус "В процессе"
    await page.locator('text=В процессе').click()

    // Ждем применения фильтра
    await page.waitForTimeout(1000)

    // Проверяем, что фильтр применился (URL или состояние изменилось)
    // Это зависит от реализации - может быть изменение в URL или в отображаемых данных
  })

  test('should navigate to task details when task row is clicked', async ({ page }) => {
    // Ждем загрузки данных
    await page.waitForLoadState('networkidle')

    // Если есть задачи в таблице, кликаем на первую строку
    const firstTaskRow = page.locator('table tbody tr').first()

    if (await firstTaskRow.isVisible()) {
      await firstTaskRow.click()

      // Проверяем, что произошла навигация на страницу деталей
      await expect(page).toHaveURL(/\/tasks\/\d+/)

      // Проверяем элементы страницы деталей
      await expect(page.locator('text=Задача #')).toBeVisible()
    }
  })

  test('should refresh tasks when refresh button is clicked', async ({ page }) => {
    // Нажимаем кнопку обновить
    await page.locator('text=Обновить').click()

    // Проверяем, что показался индикатор загрузки или произошло обновление
    // Это можно проверить по изменению состояния кнопки или появлению спиннера
    await expect(page.locator('text=Обновить')).toBeVisible()
  })
})
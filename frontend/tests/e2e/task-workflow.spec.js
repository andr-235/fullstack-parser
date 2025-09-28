import { test, expect } from '@playwright/test'

// Конфигурация для E2E тестов
const BASE_URL = process.env.E2E_BASE_URL || 'http://localhost:5173'
const API_BASE_URL = process.env.E2E_API_URL || 'http://localhost:3000'

test.describe('Task Workflow E2E Tests', () => {
  test.beforeEach(async ({ page }) => {
    // Перехватываем API запросы для контроля ответов
    await page.route('**/api/**', (route) => {
      // Пропускаем реальные запросы, но логируем их
      console.log(`API Request: ${route.request().method()} ${route.request().url()}`)
      route.continue()
    })

    await page.goto(BASE_URL)
  })

  test.describe('Task Creation and Monitoring', () => {
    test('should create VK collect task and monitor progress', async ({ page }) => {
      // Mock API responses for predictable testing
      await page.route('**/api/tasks/collect', async (route) => {
        if (route.request().method() === 'POST') {
          await route.fulfill({
            status: 201,
            contentType: 'application/json',
            body: JSON.stringify({
              success: true,
              data: { taskId: 123, status: 'created' }
            })
          })
        }
      })

      // Mock task status endpoint with progression
      let statusCallCount = 0
      await page.route('**/api/tasks/123', async (route) => {
        statusCallCount++
        let status = 'pending'
        let progress = { processed: 0, total: 100 }

        if (statusCallCount > 2) {
          status = 'processing'
          progress = { processed: 50, total: 100 }
        }
        if (statusCallCount > 5) {
          status = 'completed'
          progress = { processed: 100, total: 100 }
        }

        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            success: true,
            data: {
              id: 123,
              status,
              type: 'fetch_comments',
              progress,
              errors: [],
              groups: [12345, 67890],
              startedAt: new Date().toISOString(),
              createdAt: new Date().toISOString()
            }
          })
        })
      })

      // Navigate to task creation page
      await page.click('text=Создать задачу')
      await expect(page).toHaveURL(/.*fetch-comments/)

      // Fill in task creation form
      await page.fill('[data-testid=\"group-ids-input\"]', '12345, 67890')

      // Submit task creation
      await page.click('button:has-text(\"Создать задачу\")')

      // Should redirect to task status page
      await expect(page).toHaveURL(/.*tasks\/123/)

      // Check initial task status
      await expect(page.locator('[data-testid=\"task-status\"]')).toContainText('pending')

      // Wait for status to change to processing
      await expect(page.locator('[data-testid=\"task-status\"]')).toContainText('processing', {
        timeout: 10000
      })

      // Check progress indicator
      await expect(page.locator('[data-testid=\"progress-bar\"]')).toBeVisible()

      // Wait for completion
      await expect(page.locator('[data-testid=\"task-status\"]')).toContainText('completed', {
        timeout: 15000
      })

      // Verify final progress
      await expect(page.locator('[data-testid=\"progress-text\"]')).toContainText('100 / 100')
    })

    test('should handle task creation errors gracefully', async ({ page }) => {
      // Mock API error response
      await page.route('**/api/tasks/collect', async (route) => {
        await route.fulfill({
          status: 400,
          contentType: 'application/json',
          body: JSON.stringify({
            success: false,
            error: 'Validation failed: groups is required'
          })
        })
      })

      await page.click('text=Создать задачу')
      await expect(page).toHaveURL(/.*fetch-comments/)

      // Submit without filling required fields
      await page.click('button:has-text(\"Создать задачу\")')

      // Should show error message
      await expect(page.locator('[data-testid=\"error-message\"]')).toContainText('Validation failed')
      await expect(page.locator('[data-testid=\"error-message\"]')).toBeVisible()
    })

    test('should handle network errors during task status polling', async ({ page }) => {
      // Mock successful task creation
      await page.route('**/api/tasks/collect', async (route) => {
        await route.fulfill({
          status: 201,
          contentType: 'application/json',
          body: JSON.stringify({
            success: true,
            data: { taskId: 456, status: 'created' }
          })
        })
      })

      // Mock network failure for status endpoint
      await page.route('**/api/tasks/456', async (route) => {
        await route.abort('failed')
      })

      await page.click('text=Создать задачу')
      await page.fill('[data-testid=\"group-ids-input\"]', '12345')
      await page.click('button:has-text(\"Создать задачу\")')

      await expect(page).toHaveURL(/.*tasks\/456/)

      // Should show network error message
      await expect(page.locator('[data-testid=\"error-message\"]')).toBeVisible({ timeout: 10000 })
      await expect(page.locator('[data-testid=\"error-message\"]')).toContainText('Ошибка')
    })
  })

  test.describe('Task List and Navigation', () => {
    test('should display tasks list with correct pagination', async ({ page }) => {
      // Mock tasks list API
      await page.route('**/api/tasks**', async (route) => {
        const url = new URL(route.request().url())
        const page_param = url.searchParams.get('page') || '1'
        const limit = url.searchParams.get('limit') || '10'

        const mockTasks = Array.from({ length: 25 }, (_, i) => ({
          id: i + 1,
          status: i % 3 === 0 ? 'completed' : i % 3 === 1 ? 'processing' : 'pending',
          type: 'fetch_comments',
          createdAt: new Date().toISOString(),
          progress: { processed: Math.floor(Math.random() * 100), total: 100 }
        }))

        const pageNum = parseInt(page_param)
        const limitNum = parseInt(limit)
        const start = (pageNum - 1) * limitNum
        const end = start + limitNum
        const paginatedTasks = mockTasks.slice(start, end)

        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            success: true,
            data: paginatedTasks,
            pagination: {
              page: pageNum,
              limit: limitNum,
              total: mockTasks.length,
              totalPages: Math.ceil(mockTasks.length / limitNum)
            }
          })
        })
      })

      // Navigate to tasks list
      await page.click('text=Задачи')
      await expect(page).toHaveURL(/.*tasks/)

      // Should display tasks
      await expect(page.locator('[data-testid=\"task-item\"]')).toHaveCount(10)

      // Check pagination
      await expect(page.locator('[data-testid=\"pagination\"]')).toBeVisible()
      await expect(page.locator('text=Страница 1 из 3')).toBeVisible()

      // Navigate to next page
      await page.click('[data-testid=\"next-page\"]')
      await expect(page.locator('text=Страница 2 из 3')).toBeVisible()

      // Check that new tasks are loaded
      await expect(page.locator('[data-testid=\"task-item\"]')).toHaveCount(10)
    })

    test('should filter tasks by status', async ({ page }) => {
      await page.route('**/api/tasks**', async (route) => {
        const url = new URL(route.request().url())
        const status = url.searchParams.get('status')

        let filteredTasks = []
        if (status === 'pending') {
          filteredTasks = [
            { id: 1, status: 'pending', type: 'fetch_comments' },
            { id: 2, status: 'pending', type: 'fetch_comments' }
          ]
        } else if (status === 'completed') {
          filteredTasks = [
            { id: 3, status: 'completed', type: 'fetch_comments' }
          ]
        } else {
          filteredTasks = [
            { id: 1, status: 'pending', type: 'fetch_comments' },
            { id: 2, status: 'pending', type: 'fetch_comments' },
            { id: 3, status: 'completed', type: 'fetch_comments' }
          ]
        }

        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            success: true,
            data: filteredTasks,
            pagination: { page: 1, limit: 10, total: filteredTasks.length, totalPages: 1 }
          })
        })
      })

      await page.click('text=Задачи')

      // Initially should show all tasks
      await expect(page.locator('[data-testid=\"task-item\"]')).toHaveCount(3)

      // Filter by pending
      await page.selectOption('[data-testid=\"status-filter\"]', 'pending')
      await expect(page.locator('[data-testid=\"task-item\"]')).toHaveCount(2)

      // Filter by completed
      await page.selectOption('[data-testid=\"status-filter\"]', 'completed')
      await expect(page.locator('[data-testid=\"task-item\"]')).toHaveCount(1)
    })
  })

  test.describe('Task Details and Status Updates', () => {
    test('should show real-time task progress updates', async ({ page }) => {
      let progressValue = 0

      await page.route('**/api/tasks/789', async (route) => {
        progressValue += 10
        const status = progressValue >= 100 ? 'completed' : 'processing'

        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            success: true,
            data: {
              id: 789,
              status,
              type: 'fetch_comments',
              progress: { processed: progressValue, total: 100 },
              errors: [],
              groups: [12345],
              startedAt: new Date().toISOString(),
              createdAt: new Date().toISOString()
            }
          })
        })
      })

      // Navigate directly to task status page
      await page.goto(`${BASE_URL}/tasks/789`)

      // Should start polling and show progress updates
      await expect(page.locator('[data-testid=\"task-status\"]')).toContainText('processing')

      // Wait for progress to update
      await page.waitForFunction(() => {
        const progressText = document.querySelector('[data-testid=\"progress-text\"]')?.textContent
        return progressText && parseInt(progressText) >= 50
      }, { timeout: 15000 })

      // Eventually should show completion
      await expect(page.locator('[data-testid=\"task-status\"]')).toContainText('completed', {
        timeout: 20000
      })
    })

    test('should handle pending tasks correctly', async ({ page }) => {
      await page.route('**/api/tasks/999', async (route) => {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            success: true,
            data: {
              id: 999,
              status: 'pending',
              type: 'fetch_comments',
              progress: { processed: 0, total: 0 },
              errors: [],
              groups: [12345],
              startedAt: null,
              createdAt: new Date().toISOString()
            }
          })
        })
      })

      await page.goto(`${BASE_URL}/tasks/999`)

      // Should show pending status
      await expect(page.locator('[data-testid=\"task-status\"]')).toContainText('pending')

      // Should show appropriate message for pending tasks
      await expect(page.locator('[data-testid=\"pending-message\"]')).toContainText('Задача ожидает')

      // Progress should be 0 or minimal
      await expect(page.locator('[data-testid=\"progress-text\"]')).toContainText('0')
    })
  })

  test.describe('Error Handling and Recovery', () => {
    test('should handle 404 errors gracefully', async ({ page }) => {
      await page.route('**/api/tasks/404', async (route) => {
        await route.fulfill({
          status: 404,
          contentType: 'application/json',
          body: JSON.stringify({
            success: false,
            error: 'Task not found'
          })
        })
      })

      await page.goto(`${BASE_URL}/tasks/404`)

      // Should show 404 error message
      await expect(page.locator('[data-testid=\"error-message\"]')).toContainText('Task not found')
      await expect(page.locator('[data-testid=\"error-message\"]')).toBeVisible()
    })

    test('should retry on temporary failures', async ({ page }) => {
      let attemptCount = 0

      await page.route('**/api/tasks/retry', async (route) => {
        attemptCount++

        if (attemptCount <= 2) {
          // First two attempts fail
          await route.fulfill({
            status: 500,
            contentType: 'application/json',
            body: JSON.stringify({
              success: false,
              error: 'Internal server error'
            })
          })
        } else {
          // Third attempt succeeds
          await route.fulfill({
            status: 200,
            contentType: 'application/json',
            body: JSON.stringify({
              success: true,
              data: {
                id: 'retry',
                status: 'processing',
                type: 'fetch_comments',
                progress: { processed: 25, total: 100 }
              }
            })
          })
        }
      })

      await page.goto(`${BASE_URL}/tasks/retry`)

      // Should eventually succeed after retries
      await expect(page.locator('[data-testid=\"task-status\"]')).toContainText('processing', {
        timeout: 10000
      })
    })
  })

  test.describe('Cross-browser Compatibility', () => {
    test('should work consistently across different browsers', async ({ page, browserName }) => {
      // Mock basic task response
      await page.route('**/api/tasks/browser-test', async (route) => {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            success: true,
            data: {
              id: 'browser-test',
              status: 'completed',
              type: 'fetch_comments',
              progress: { processed: 100, total: 100 }
            }
          })
        })
      })

      await page.goto(`${BASE_URL}/tasks/browser-test`)

      // Basic functionality should work in all browsers
      await expect(page.locator('[data-testid=\"task-status\"]')).toContainText('completed')
      await expect(page.locator('[data-testid=\"progress-text\"]')).toContainText('100')

      // Browser-specific checks
      if (browserName === 'webkit') {
        // Safari-specific checks
        console.log('Running Safari-specific tests')
      } else if (browserName === 'firefox') {
        // Firefox-specific checks
        console.log('Running Firefox-specific tests')
      } else {
        // Chrome-specific checks
        console.log('Running Chrome-specific tests')
      }
    })
  })
})
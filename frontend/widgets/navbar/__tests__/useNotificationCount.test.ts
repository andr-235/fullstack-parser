import { renderHook, waitFor } from '@testing-library/react'

import { useNotificationCount } from '../useNotificationCount'

// Mock httpClient
jest.mock('@/shared/lib', () => ({
  httpClient: {
    get: jest.fn(),
  },
}))

const mockHttpClient = require('@/shared/lib').httpClient

describe('useNotificationCount', () => {
  beforeEach(() => {
    jest.clearAllMocks()
    jest.useFakeTimers()
  })

  afterEach(() => {
    jest.useRealTimers()
  })

  it('возвращает 0 при успешном ответе без уведомлений', async () => {
    mockHttpClient.get.mockResolvedValueOnce({ data: { today_comments: 0 } })

    const { result } = renderHook(() => useNotificationCount())

    await waitFor(() => {
      expect(result.current).toBe(0)
    })
  })

  it('возвращает количество уведомлений при успешном ответе', async () => {
    mockHttpClient.get.mockResolvedValueOnce({ data: { today_comments: 5 } })

    const { result } = renderHook(() => useNotificationCount())

    await waitFor(() => {
      expect(result.current).toBe(5)
    })
  })

  it('возвращает 0 при ошибке API', async () => {
    mockHttpClient.get.mockRejectedValueOnce(new Error('API Error'))

    const { result } = renderHook(() => useNotificationCount())

    await waitFor(() => {
      expect(result.current).toBe(0)
    })
  })

  it('обновляет данные каждые 30 секунд', async () => {
    mockHttpClient.get
      .mockResolvedValueOnce({ data: { today_comments: 5 } })
      .mockResolvedValueOnce({ data: { today_comments: 10 } })

    const { result } = renderHook(() => useNotificationCount())

    await waitFor(() => {
      expect(result.current).toBe(5)
    })

    // Продвигаем время на 30 секунд
    jest.advanceTimersByTime(30000)

    await waitFor(() => {
      expect(result.current).toBe(10)
    })

    expect(mockHttpClient.get).toHaveBeenCalledTimes(2)
  })

  it('обрабатывает частичные ошибки API', async () => {
    mockHttpClient.get
      .mockRejectedValueOnce(new Error('Global stats error'))
      .mockResolvedValueOnce({ data: { today_comments: 3 } })

    const { result } = renderHook(() => useNotificationCount())

    await waitFor(() => {
      expect(result.current).toBe(3)
    })
  })

  it('очищает интервал при размонтировании', () => {
    const clearIntervalSpy = jest.spyOn(global, 'clearInterval')
    
    const { unmount } = renderHook(() => useNotificationCount())
    
    unmount()
    
    expect(clearIntervalSpy).toHaveBeenCalled()
  })
})

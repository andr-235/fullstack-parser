import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { setActivePinia } from 'pinia'
import { createPinia } from 'pinia'
import { useTasksStore } from '../tasks'
import * as api from '@/services/api'

vi.mock('@/services/api', () => ({
  postFetchComments: vi.fn(),
  getTaskStatus: vi.fn()
}))

describe('Tasks Store', () => {
  let pinia
  let store

  beforeEach(() => {
    pinia = createPinia()
    setActivePinia(pinia)
    store = useTasksStore()
    vi.useFakeTimers()
  })

  afterEach(() => {
    vi.useRealTimers()
    vi.clearAllMocks()
  })

  it('initial state', () => {
    expect(store.currentTaskId).toBeNull()
    expect(store.status).toBe('')
    expect(store.progress).toBe(0)
  })

  it('startTask success', async () => {
    const mockResponse = { data: { task_id: '123' } }
    api.postFetchComments.mockResolvedValue(mockResponse)

    const result = await store.startTask({ owner_id: 1, post_id: 2, access_token: 'token' })

    expect(api.postFetchComments).toHaveBeenCalledWith({ owner_id: 1, post_id: 2, access_token: 'token' })
    expect(store.currentTaskId).toBe('123')
    expect(result).toBe('123')
  })

  it('startTask error', async () => {
    api.postFetchComments.mockRejectedValue(new Error('Start error'))

    const result = await store.startTask({})

    expect(result).toBeNull()
  })

  it('startPolling sets interval and calls getTaskStatus', async () => {
    const mockGetStatus = vi.fn().mockResolvedValue({ data: { status: 'pending', progress: 0 } })
    api.getTaskStatus.mockImplementation(mockGetStatus)

    store.startPolling('123', 1000)

    vi.advanceTimersByTime(1000)

    expect(api.getTaskStatus).toHaveBeenCalledWith('123')
    expect(store.status).toBe('pending')
    expect(store.progress).toBe(0)
  })

  it('startPolling handles error', async () => {
    api.getTaskStatus.mockRejectedValue(new Error('Polling error'))

    store.startPolling('123', 1000)

    vi.advanceTimersByTime(1000)

    expect(store.currentTaskId).toBeNull()
    expect(store.status).toBe('')
    expect(store.progress).toBe(0)
  })

  it('stopPolling clears interval and resets state', () => {
    const mockClearInterval = vi.fn()
    global.clearInterval = mockClearInterval
    store.pollingInterval = 123

    store.stopPolling()

    expect(mockClearInterval).toHaveBeenCalledWith(123)
    expect(store.currentTaskId).toBeNull()
    expect(store.status).toBe('')
    expect(store.progress).toBe(0)
    expect(store.pollingInterval).toBeNull()
  })

  it('updateStatus sets status and progress', () => {
    store.updateStatus({ status: 'completed', progress: 100 })

    expect(store.status).toBe('completed')
    expect(store.progress).toBe(100)
  })
})
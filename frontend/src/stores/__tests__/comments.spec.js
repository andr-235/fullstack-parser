import { describe, it, expect, vi, beforeEach } from 'vitest'
import { setActivePinia } from 'pinia'
import { createPinia } from 'pinia'
import { useCommentsStore } from '../comments'
import { getComments } from '@/services/api'

vi.mock('@/services/api', () => ({
  getComments: vi.fn()
}))

describe('Comments Store', () => {
  let pinia
  let store

  beforeEach(() => {
    pinia = createPinia()
    setActivePinia(pinia)
    store = useCommentsStore()
  })

  it('initial state', () => {
    expect(store.comments).toEqual([])
    expect(store.total).toBe(0)
    expect(store.filters).toEqual({ task_id: null, post_id: null, sentiment: null })
    expect(store.pagination).toEqual({ limit: 20, offset: 0 })
  })

  it('fetchComments success', async () => {
    const mockResponse = { data: { comments: [{ id: 1, text: 'Test' }], total: 1 } }
    getComments.mockResolvedValue(mockResponse)

    await store.fetchComments()

    expect(getComments).toHaveBeenCalledWith({ limit: 20, offset: 0 })
    expect(store.comments).toEqual([{ id: 1, text: 'Test' }])
    expect(store.total).toBe(1)
  })

  it('fetchComments error', async () => {
    getComments.mockRejectedValue(new Error('API error'))

    await store.fetchComments()

    expect(store.comments).toEqual([])
    expect(store.total).toBe(0)
  })

  it('updateFilters merges filters, resets offset, fetches', async () => {
    const mockResponse = { data: { comments: [], total: 0 } }
    getComments.mockResolvedValue(mockResponse)

    store.updateFilters({ task_id: 123, sentiment: 'positive' })

    expect(store.filters).toEqual({ task_id: 123, post_id: null, sentiment: 'positive' })
    expect(store.pagination.offset).toBe(0)
    expect(getComments).toHaveBeenCalledWith({ task_id: 123, sentiment: 'positive', limit: 20, offset: 0 })
  })

  it('nextPage increases offset and fetches', async () => {
    const mockResponse = { data: { comments: [], total: 0 } }
    getComments.mockResolvedValue(mockResponse)

    store.nextPage()

    expect(store.pagination.offset).toBe(20)
    expect(getComments).toHaveBeenCalledWith({ limit: 20, offset: 20 })
  })

  it('prevPage decreases offset if >0 and fetches', async () => {
    const mockResponse = { data: { comments: [], total: 0 } }
    getComments.mockResolvedValue(mockResponse)

    store.pagination.offset = 40
    store.prevPage()

    expect(store.pagination.offset).toBe(20)
    expect(getComments).toHaveBeenCalledWith({ limit: 20, offset: 20 })
  })

  it('prevPage does nothing if offset 0', () => {
    store.pagination.offset = 0
    store.prevPage()

    expect(store.pagination.offset).toBe(0)
  })
})
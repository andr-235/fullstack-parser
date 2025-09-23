import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import CommentsList from '../CommentsList.vue'
import LoadingSpinner from '@/components/LoadingSpinner.vue'
import { useCommentsStore } from '@/stores/comments'
import { useSnackbarStore } from '@/stores/snackbar'

// Mocks
vi.mock('@/stores/comments', () => ({
  useCommentsStore: vi.fn(() => ({
    comments: [],
    total: 0,
    filters: {},
    pagination: { limit: 20, offset: 0 },
    updateFilters: vi.fn(),
    fetchComments: vi.fn(),
    nextPage: vi.fn(),
    prevPage: vi.fn()
  }))
}))
vi.mock('@/stores/snackbar', () => ({
  useSnackbarStore: vi.fn(() => ({
    show: vi.fn()
  }))
}))

describe('CommentsList.vue', () => {
  let wrapper
  let pinia
  let mockCommentsStore
  let mockSnackbarStore

  beforeEach(() => {
    pinia = createPinia()
    setActivePinia(pinia)
    mockCommentsStore = {
      comments: [{ id: 1, text: 'Test comment', author: 'User', date: '2023-01-01', sentiment: 'positive', keywords: ['key1', 'key2'] }],
      total: 1,
      filters: { task_id: '', post_id: '', sentiment: null },
      pagination: { limit: 20, offset: 0 },
      updateFilters: vi.fn(),
      fetchComments: vi.fn(),
      nextPage: vi.fn(),
      prevPage: vi.fn()
    }
    vi.mocked(useCommentsStore).mockReturnValue(mockCommentsStore)
    mockSnackbarStore = { show: vi.fn() }
    vi.mocked(useSnackbarStore).mockReturnValue(mockSnackbarStore)

    wrapper = mount(CommentsList, {
      global: {
        plugins: [pinia],
        stubs: {
          VContainer: true,
          VRow: true,
          VCol: true,
          VCard: true,
          VCardTitle: true,
          VCardText: true,
          VTextField: true,
          VSelect: true,
          VBtn: true,
          VDataTable: true,
          VChip: true,
          VResponsive: true
        }
      }
    })
  })

  it('renders title', () => {
    expect(wrapper.find('[data-testid="title"]').text()).toBe('Список комментариев')
  })

  it('shows LoadingSpinner when loading', async () => {
    await wrapper.setData({ loading: true })
    expect(wrapper.findComponent(LoadingSpinner).exists()).toBe(true)
  })

  it('renders filters when not loading', () => {
    const taskField = wrapper.find('input[placeholder*="ID задачи"]')
    const postField = wrapper.find('input[placeholder*="ID поста"]')
    const sentimentSelect = wrapper.find('select')
    expect(taskField.exists()).toBe(true)
    expect(postField.exists()).toBe(true)
    expect(sentimentSelect.exists()).toBe(true)
  })

  it('updates filters on input change', async () => {
    const taskField = wrapper.find('input[placeholder*="ID задачи"]')
    await taskField.setValue('456')
    expect(wrapper.vm.filters.task_id).toBe('456')

    const sentimentSelect = wrapper.find('select')
    await sentimentSelect.setValue('positive')
    expect(wrapper.vm.filters.sentiment).toBe('positive')
  })

  it('calls search and updates filters', async () => {
    await wrapper.find('input[placeholder*="ID задачи"]').setValue('456')
    await wrapper.find('button').trigger('click')

    expect(mockCommentsStore.updateFilters).toHaveBeenCalledWith({
      task_id: '456',
      post_id: '',
      sentiment: null,
      page: 1,
      itemsPerPage: 20
    })
  })

  it('handles search error', async () => {
    mockCommentsStore.updateFilters = vi.fn().mockRejectedValue(new Error('Search error'))
    await wrapper.find('button').trigger('click')

    expect(mockSnackbarStore.show).toHaveBeenCalledWith('Ошибка поиска комментариев', 'error')
  })

  it('renders data table with comments', () => {
    const table = wrapper.findComponent({ name: 'v-data-table' })
    expect(table.exists()).toBe(true)
    expect(table.props('items')).toEqual(mockCommentsStore.comments)
  })

  it('renders sentiment chip with color', () => {
    expect(wrapper.vm.getSentimentColor('positive')).toBe('green')
    expect(wrapper.vm.getSentimentColor('negative')).toBe('red')
    expect(wrapper.vm.getSentimentColor('neutral')).toBe('blue')
    expect(wrapper.vm.getSentimentColor('unknown')).toBe('grey')
  })

  it('renders keywords chips', () => {
    const keywordsSlot = wrapper.findAll('[data-testid="keyword-chip"]')
    expect(keywordsSlot.length).toBe(2) // first 3, but example has 2
    expect(keywordsSlot[0].text()).toBe('key1')
  })

  it('handles pagination update', () => {
    const options = { page: 2, itemsPerPage: 10 }
    wrapper.vm.updatePagination(options)
    expect(mockCommentsStore.updateFilters).toHaveBeenCalledWith(expect.objectContaining({
      page: 2,
      itemsPerPage: 10
    }))
  })

  it('sentiment options are correct', () => {
    expect(wrapper.vm.sentimentOptions).toEqual([
      { text: 'Позитивный', value: 'positive' },
      { text: 'Негативный', value: 'negative' },
      { text: 'Нейтральный', value: 'neutral' }
    ])
  })
})
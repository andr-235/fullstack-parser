import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import { createRouter, createWebHistory } from 'vue-router'
import TaskStatus from '../TaskStatus.vue'
import LoadingSpinner from '@/components/LoadingSpinner.vue'
import ErrorMessage from '@/components/ErrorMessage.vue'
import { useTasksStore } from '@/stores/tasks'

// Mocks
vi.mock('@/stores/tasks', () => ({
  useTasksStore: vi.fn()
}))

const mockRouter = createRouter({
  history: createWebHistory(),
  routes: []
})

describe('TaskStatus.vue', () => {
  let wrapper
  let pinia
  let mockTasksStore

  beforeEach(() => {
    pinia = createPinia()
    setActivePinia(pinia)
    mockTasksStore = {
      tasks: {},
      startPolling: vi.fn(),
      stopPolling: vi.fn()
    }
    vi.mocked(useTasksStore).mockReturnValue(mockTasksStore)
    wrapper = mount(TaskStatus, {
      global: {
        plugins: [pinia, mockRouter],
        stubs: {
          VContainer: true,
          VRow: true,
          VCol: true,
          VCard: true,
          VCardTitle: true,
          VCardText: true,
          VProgressLinear: true
        }
      },
      props: {
        id: '123'
      }
    })
    vi.useFakeTimers()
  })

  afterEach(() => {
    vi.useRealTimers()
    vi.clearAllMocks()
  })

  it('renders title', () => {
    expect(wrapper.find('[data-testid="title"]').text()).toBe('Статус задачи')
  })

  it('shows LoadingSpinner initially', () => {
    expect(wrapper.findComponent(LoadingSpinner).exists()).toBe(true)
  })

  it('shows ErrorMessage when error', async () => {
    await wrapper.setData({ error: 'Test error' })
    expect(wrapper.findComponent(ErrorMessage).exists()).toBe(true)
  })

  it('starts polling on mounted', () => {
    expect(mockTasksStore.startPolling).toHaveBeenCalledWith('123')
  })

  it('updates progress and status from store', async () => {
    mockTasksStore.tasks = { '123': { progress: 50, status: 'processing' } }
    await wrapper.vm.$nextTick()

    expect(wrapper.find('[data-testid="status-text"]').text()).toBe('processing')
    expect(wrapper.findComponent({ name: 'v-progress-linear' }).props('modelValue')).toBe(50)
  })

  it('clears interval when status completed', async () => {
    const mockInterval = vi.fn()
    global.setInterval = mockInterval

    mockTasksStore.tasks = { '123': { status: 'completed' } }
    await wrapper.vm.$nextTick()

    expect(mockInterval).not.toHaveBeenCalled()
  })

  it('stops polling on unmount', async () => {
    await wrapper.unmount()
    expect(mockTasksStore.stopPolling).toHaveBeenCalled()
  })

  it('handles polling error', async () => {
    mockTasksStore.startPolling = vi.fn(() => {
      throw new Error('Polling failed')
    })
    await wrapper.vm.$nextTick()
    expect(mockTasksStore.stopPolling).toHaveBeenCalled()
  })
})
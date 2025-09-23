import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { createRouter, createWebHistory } from 'vue-router'
import { createPinia, setActivePinia } from 'pinia'
import FetchComments from '../FetchComments.vue'
import * as api from '@/services/api'
import LoadingSpinner from '@/components/LoadingSpinner.vue'
import ErrorMessage from '@/components/ErrorMessage.vue'

// Mocks
vi.mock('@/stores/tasks', () => ({
  useTasksStore: vi.fn(() => ({
    startTask: vi.fn()
  }))
}))
vi.mock('@/stores/snackbar', () => ({
  useSnackbarStore: vi.fn(() => ({
    show: vi.fn()
  }))
}))
vi.mock('@/services/api', () => ({
  postFetchComments: vi.fn()
}))

const mockRouter = {
  push: vi.fn()
}
const createTestRouter = () => createRouter({
  history: createWebHistory(),
  routes: [{ path: '/task/:id', name: 'Task' }]
})

describe('FetchComments.vue', () => {
  let wrapper
  let pinia
  let router

  beforeEach(() => {
    pinia = createPinia()
    setActivePinia(pinia)
    router = createTestRouter()
    wrapper = mount(FetchComments, {
      global: {
        plugins: [pinia, router],
        stubs: {
          VContainer: true,
          VRow: true,
          VCol: true,
          VCard: true,
          VCardTitle: true,
          VCardText: true,
          VForm: true,
          VTextField: true,
          VBtn: true
        },
        mocks: {
          $router: mockRouter
        }
      }
    })
    vi.clearAllMocks()
  })

  it('renders form title', () => {
    expect(wrapper.find('[data-testid="title"]').text()).toBe('Сбор комментариев VK')
  })

  it('shows LoadingSpinner when loading', async () => {
    await wrapper.setData({ loading: true })
    expect(wrapper.findComponent(LoadingSpinner).exists()).toBe(true)
  })

  it('shows ErrorMessage when error', async () => {
    await wrapper.setData({ error: 'Test error' })
    expect(wrapper.findComponent(ErrorMessage).exists()).toBe(true)
  })

  it('validates required fields', async () => {
    const ownerField = wrapper.find('input[placeholder*="ID владельца"]')
    await ownerField.setValue('')
    expect(ownerField.element.validationMessage).toContain('Обязательное поле')

    const postField = wrapper.find('input[placeholder*="ID поста"]')
    await postField.setValue('abc')
    expect(postField.element.validationMessage).toContain('Должно быть числом')
  })

  it('validates number fields', async () => {
    const ownerField = wrapper.find('input[placeholder*="ID владельца"]')
    await ownerField.setValue('123')
    expect(ownerField.element.validationMessage).toBe('')
  })

  it('disables submit button when invalid or loading', async () => {
    const submitBtn = wrapper.find('button[type="submit"]')
    expect(submitBtn.attributes('disabled')).toBeDefined()

    await wrapper.find('input[placeholder*="ID владельца"]').setValue('123')
    await wrapper.find('input[placeholder*="ID поста"]').setValue('456')
    expect(submitBtn.attributes('disabled')).toBeUndefined()

    await wrapper.setData({ loading: true })
    expect(submitBtn.attributes('disabled')).toBeDefined()
  })

  it('submits form successfully and redirects', async () => {
    const mockStartTask = vi.fn().mockResolvedValue({ task_id: '123' })
    const { useTasksStore } = await import('@/stores/tasks')
    useTasksStore().startTask = mockStartTask

    await wrapper.find('input[placeholder*="ID владельца"]').setValue('123')
    await wrapper.find('input[placeholder*="ID поста"]').setValue('456')

    await wrapper.find('form').trigger('submit')

    expect(mockStartTask).toHaveBeenCalledWith({
      owner_id: 123,
      post_id: 456
    })
    expect(mockRouter.push).toHaveBeenCalledWith('/task/123')
  })

  it('handles submit error', async () => {
    const mockStartTask = vi.fn().mockRejectedValue(new Error('API error'))
    const { useTasksStore } = await import('@/stores/tasks')
    useTasksStore().startTask = mockStartTask

    const { useSnackbarStore } = await import('@/stores/snackbar')
    useSnackbarStore().show = vi.fn()

    await wrapper.find('input[placeholder*="ID владельца"]').setValue('123')
    await wrapper.find('input[placeholder*="ID поста"]').setValue('456')

    await wrapper.find('form').trigger('submit')

    await vi.waitFor(() => {
      expect(wrapper.vm.error).toBe('Ошибка запуска задачи: API error')
      expect(useSnackbarStore().show).toHaveBeenCalledWith('Ошибка запуска задачи', 'error')
    })
  })

  it('form validation rules work', () => {
    const rules = wrapper.vm.rules
    expect(rules.required('')).toBe('Обязательное поле')
    expect(rules.required('value')).toBe(true)
    expect(rules.number('123')).toBe(true)
    expect(rules.number('abc')).toBe('Должно быть числом')
  })
})
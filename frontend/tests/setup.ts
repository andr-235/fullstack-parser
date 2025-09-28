import { vi } from 'vitest'
import { config } from '@vue/test-utils'

// Mock глобальных объектов
Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: vi.fn().mockImplementation(query => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: vi.fn(), // deprecated
    removeListener: vi.fn(), // deprecated
    addEventListener: vi.fn(),
    removeEventListener: vi.fn(),
    dispatchEvent: vi.fn(),
  })),
})

// Mock для localStorage
Object.defineProperty(window, 'localStorage', {
  value: {
    getItem: vi.fn(),
    setItem: vi.fn(),
    removeItem: vi.fn(),
    clear: vi.fn(),
    length: 0,
    key: vi.fn(),
  },
  writable: true,
})

// Mock для sessionStorage
Object.defineProperty(window, 'sessionStorage', {
  value: {
    getItem: vi.fn(),
    setItem: vi.fn(),
    removeItem: vi.fn(),
    clear: vi.fn(),
    length: 0,
    key: vi.fn(),
  },
  writable: true,
})

// Mock для IntersectionObserver
global.IntersectionObserver = vi.fn().mockImplementation(() => ({
  observe: vi.fn(),
  unobserve: vi.fn(),
  disconnect: vi.fn(),
}))

// Mock для ResizeObserver
global.ResizeObserver = vi.fn().mockImplementation(() => ({
  observe: vi.fn(),
  unobserve: vi.fn(),
  disconnect: vi.fn(),
}))

// Глобальная конфигурация для Vue Test Utils
config.global.stubs = {
  // Заглушки для внешних компонентов, если нужно
}

// Mock для Vue Router
const mockRouter = {
  push: vi.fn(),
  replace: vi.fn(),
  go: vi.fn(),
  back: vi.fn(),
  forward: vi.fn(),
  currentRoute: {
    value: {
      path: '/',
      query: {},
      params: {},
      meta: {},
      name: undefined,
      fullPath: '/',
      hash: '',
      matched: [],
      redirectedFrom: undefined
    }
  }
}

config.global.mocks = {
  $router: mockRouter,
  $route: mockRouter.currentRoute.value
}

// Дополнительные настройки для тестирования
beforeEach(() => {
  // Очистка моков перед каждым тестом
  vi.clearAllMocks()
})

afterEach(() => {
  // Очистка после каждого теста
  vi.restoreAllMocks()
})
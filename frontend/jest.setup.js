import '@testing-library/jest-dom'

// Мокаем IntersectionObserver
global.IntersectionObserver = class IntersectionObserver {
  constructor() {}
  disconnect() {}
  observe() {}
  unobserve() {}
}

// Мокаем ResizeObserver
global.ResizeObserver = class ResizeObserver {
  constructor() {}
  disconnect() {}
  observe() {}
  unobserve() {}
}

// Мокаем window.matchMedia
Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: jest.fn().mockImplementation(query => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: jest.fn(),
    removeListener: jest.fn(),
    addEventListener: jest.fn(),
    removeEventListener: jest.fn(),
    dispatchEvent: jest.fn(),
  })),
})

// Мокаем Radix UI компоненты для тестов
jest.mock('@radix-ui/react-select', () => ({
  Root: ({ children, ...props }) => <div {...props}>{children}</div>,
  Trigger: ({ children, ...props }) => <button {...props}>{children}</button>,
  Content: ({ children, ...props }) => <div {...props}>{children}</div>,
  Item: ({ children, ...props }) => <div {...props}>{children}</div>,
  Value: ({ children, ...props }) => <span {...props}>{children}</span>,
  Label: ({ children, ...props }) => <label {...props}>{children}</label>,
  Group: ({ children, ...props }) => <div {...props}>{children}</div>,
  Separator: ({ children, ...props }) => <div {...props}>{children}</div>,
  Viewport: ({ children, ...props }) => <div {...props}>{children}</div>,
  Portal: ({ children }) => <>{children}</>,
  Icon: ({ children, ...props }) => <span {...props}>{children}</span>,
  ItemIndicator: ({ children, ...props }) => <span {...props}>{children}</span>,
  ItemText: ({ children, ...props }) => <span {...props}>{children}</span>,
}))

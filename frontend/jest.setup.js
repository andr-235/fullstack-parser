// Optional: configure or set up a testing framework before each test.
// If you delete this file, remove `setupFilesAfterEnv` from `jest.config.js`

// Learn more: https://jestjs.io/docs/configuration#setupfilesafterenv-array
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
  value: jest.fn().mockImplementation((query) => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: jest.fn(), // deprecated
    removeListener: jest.fn(), // deprecated
    addEventListener: jest.fn(),
    removeEventListener: jest.fn(),
    dispatchEvent: jest.fn(),
  })),
})

// Мокаем console.warn и console.error для тестов
const originalWarn = console.warn
const originalError = console.error

beforeAll(() => {
  console.warn = jest.fn()
  console.error = jest.fn()
})

afterAll(() => {
  console.warn = originalWarn
  console.error = originalError
})

// Мок Radix UI Select для тестов (обход проблемы с jsdom)
jest.mock('@radix-ui/react-select', () => {
  const React = require('react')

  // Контекст для value/onValueChange
  const SelectContext = React.createContext({
    value: undefined,
    onValueChange: undefined,
  })

  // Root (Select) — кладёт value/onValueChange в контекст
  const Root = React.forwardRef(
    (
      {
        value: controlledValue,
        defaultValue,
        onValueChange,
        children,
        ...props
      },
      ref
    ) => {
      const [uncontrolledValue, setUncontrolledValue] =
        React.useState(defaultValue)
      const isControlled = controlledValue !== undefined
      const value = isControlled ? controlledValue : uncontrolledValue
      const handleValueChange = (val) => {
        if (!isControlled) setUncontrolledValue(val)
        if (onValueChange) onValueChange(val)
      }
      return (
        <SelectContext.Provider
          value={{ value, onValueChange: handleValueChange }}
        >
          <div ref={ref} {...props}>
            {children}
          </div>
        </SelectContext.Provider>
      )
    }
  )

  // Trigger с role="combobox" и aria-activedescendant
  const Trigger = React.forwardRef((props, ref) => {
    const { value } = React.useContext(SelectContext)
    return (
      <button
        ref={ref}
        role="combobox"
        aria-haspopup="listbox"
        aria-expanded="false"
        aria-activedescendant={value}
        {...props}
      >
        {props.children}
      </button>
    )
  })

  // Content с role="listbox"
  const Content = React.forwardRef((props, ref) => (
    <div ref={ref} role="listbox" {...props}>
      {props.children}
    </div>
  ))

  // Item с role="option" — вызывает onValueChange из контекста при клике
  const Item = React.forwardRef(({ value, children, ...props }, ref) => {
    const { onValueChange } = React.useContext(SelectContext)
    return (
      <div
        ref={ref}
        role="option"
        tabIndex={0}
        data-value={value}
        onClick={() => onValueChange && onValueChange(value)}
        {...props}
      >
        {children}
      </div>
    )
  })

  // Остальные компоненты
  const Group = React.forwardRef((props, ref) => (
    <div ref={ref} {...props}>
      {props.children}
    </div>
  ))
  const Value = React.forwardRef((props, ref) => (
    <span ref={ref} {...props}>
      {props.children}
    </span>
  ))
  const Label = React.forwardRef((props, ref) => (
    <label ref={ref} {...props}>
      {props.children}
    </label>
  ))
  const Separator = React.forwardRef((props, ref) => (
    <div ref={ref} role="separator" {...props}>
      {props.children}
    </div>
  ))
  const Viewport = React.forwardRef((props, ref) => (
    <div ref={ref} {...props}>
      {props.children}
    </div>
  ))
  const Portal = ({ children }) => <>{children}</>
  const Icon = (props) => <span {...props}>{props.children}</span>
  const ItemIndicator = React.forwardRef((props, ref) => (
    <span ref={ref} {...props}>
      {props.children}
    </span>
  ))
  const ItemText = React.forwardRef((props, ref) => (
    <span ref={ref} {...props}>
      {props.children}
    </span>
  ))

  // Экспортируем оба варианта имён
  return {
    __esModule: true,
    Root,
    Group,
    Value,
    Trigger,
    Content,
    Label,
    Item,
    Separator,
    Viewport,
    Portal,
    Icon,
    ItemIndicator,
    ItemText,
    SelectRoot: Root,
    SelectGroup: Group,
    SelectValue: Value,
    SelectTrigger: Trigger,
    SelectContent: Content,
    SelectLabel: Label,
    SelectItem: Item,
    SelectSeparator: Separator,
    SelectViewport: Viewport,
    SelectPortal: Portal,
    SelectIcon: Icon,
    SelectItemIndicator: ItemIndicator,
    SelectItemText: ItemText,
    default: {
      Root,
      Group,
      Value,
      Trigger,
      Content,
      Label,
      Item,
      Separator,
      Viewport,
      Portal,
      Icon,
      ItemIndicator,
      ItemText,
    },
  }
})

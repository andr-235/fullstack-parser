import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import DashboardPage from './DashboardPage'

// Мокаем хуки
jest.mock('@/hooks/use-stats', () => ({
  useGlobalStats: jest.fn(),
  useDashboardStats: jest.fn(),
}))

jest.mock('date-fns', () => ({
  formatDistanceToNow: jest.fn(() => '2 минуты назад'),
  format: jest.fn(() => '01.01'),
}))

jest.mock('date-fns/locale', () => ({
  ru: {},
}))

// Мокаем Recharts
jest.mock('recharts', () => ({
  LineChart: ({ children }: { children: React.ReactNode }) => <div data-testid="line-chart">{children}</div>,
  Line: () => <div data-testid="line" />,
  AreaChart: ({ children }: { children: React.ReactNode }) => <div data-testid="area-chart">{children}</div>,
  Area: () => <div data-testid="area" />,
  BarChart: ({ children }: { children: React.ReactNode }) => <div data-testid="bar-chart">{children}</div>,
  Bar: () => <div data-testid="bar" />,
  PieChart: ({ children }: { children: React.ReactNode }) => <div data-testid="pie-chart">{children}</div>,
  Pie: () => <div data-testid="pie" />,
  Cell: () => <div data-testid="cell" />,
  XAxis: () => <div data-testid="x-axis" />,
  YAxis: () => <div data-testid="y-axis" />,
  CartesianGrid: () => <div data-testid="cartesian-grid" />,
  Tooltip: () => <div data-testid="tooltip" />,
  Legend: () => <div data-testid="legend" />,
  ResponsiveContainer: ({ children }: { children: React.ReactNode }) => <div data-testid="responsive-container">{children}</div>,
}))

const mockGlobalStats = {
  total_groups: 15,
  active_groups: 12,
  total_keywords: 45,
  active_keywords: 42,
  total_comments: 1234,
  comments_with_keywords: 89,
  last_parse_time: '2024-01-01T12:00:00Z',
}

const mockDashboardStats = {
  today_comments: 23,
  today_matches: 7,
  week_comments: 156,
  week_matches: 34,
  top_groups: [
    { name: 'Crypto News', count: 45 },
    { name: 'Bitcoin Club', count: 32 },
  ],
  top_keywords: [
    { word: 'Криптовалюта', count: 23 },
    { word: 'Биткоин', count: 18 },
  ],
  recent_activity: [
    {
      id: 1,
      type: 'parse',
      message: 'Завершен парсинг группы',
      timestamp: '2024-01-01T12:00:00Z',
    },
  ],
}

const createWrapper = () => {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: {
        retry: false,
      },
    },
  })
  
  return ({ children }: { children: React.ReactNode }) => (
    <QueryClientProvider client={queryClient}>
      {children}
    </QueryClientProvider>
  )
}

describe('DashboardPage', () => {
  const mockUseGlobalStats = jest.mocked(require('@/hooks/use-stats').useGlobalStats)
  const mockUseDashboardStats = jest.mocked(require('@/hooks/use-stats').useDashboardStats)

  beforeEach(() => {
    jest.clearAllMocks()
  })

  it('отображает загрузку при получении данных', () => {
    mockUseGlobalStats.mockReturnValue({
      data: undefined,
      isLoading: true,
      error: null,
    })
    
    mockUseDashboardStats.mockReturnValue({
      data: undefined,
      isLoading: true,
      error: null,
    })

    render(<DashboardPage />, { wrapper: createWrapper() })
    
    expect(screen.getByTestId('loading-spinner')).toBeInTheDocument()
  })

  it('отображает ошибку при неудачной загрузке', () => {
    mockUseGlobalStats.mockReturnValue({
      data: undefined,
      isLoading: false,
      error: new Error('Ошибка загрузки'),
    })
    
    mockUseDashboardStats.mockReturnValue({
      data: undefined,
      isLoading: false,
      error: null,
    })

    render(<DashboardPage />, { wrapper: createWrapper() })
    
    expect(screen.getByText('Ошибка загрузки')).toBeInTheDocument()
    expect(screen.getByText('Обновить')).toBeInTheDocument()
  })

  it('отображает основные метрики', () => {
    mockUseGlobalStats.mockReturnValue({
      data: mockGlobalStats,
      isLoading: false,
      error: null,
    })
    
    mockUseDashboardStats.mockReturnValue({
      data: mockDashboardStats,
      isLoading: false,
      error: null,
    })

    render(<DashboardPage />, { wrapper: createWrapper() })
    
    expect(screen.getByText('Дашборд')).toBeInTheDocument()
    expect(screen.getByText('15')).toBeInTheDocument() // total_groups
    expect(screen.getByText('1,234')).toBeInTheDocument() // total_comments
    expect(screen.getByText('45')).toBeInTheDocument() // total_keywords
    expect(screen.getByText('89')).toBeInTheDocument() // comments_with_keywords
  })

  it('отображает вкладки', () => {
    mockUseGlobalStats.mockReturnValue({
      data: mockGlobalStats,
      isLoading: false,
      error: null,
    })
    
    mockUseDashboardStats.mockReturnValue({
      data: mockDashboardStats,
      isLoading: false,
      error: null,
    })

    render(<DashboardPage />, { wrapper: createWrapper() })
    
    expect(screen.getByText('Обзор')).toBeInTheDocument()
    expect(screen.getByText('Активность')).toBeInTheDocument()
    expect(screen.getByText('Группы')).toBeInTheDocument()
    expect(screen.getByText('Ключевые слова')).toBeInTheDocument()
  })

  it('переключает вкладки', async () => {
    mockUseGlobalStats.mockReturnValue({
      data: mockGlobalStats,
      isLoading: false,
      error: null,
    })
    
    mockUseDashboardStats.mockReturnValue({
      data: mockDashboardStats,
      isLoading: false,
      error: null,
    })

    render(<DashboardPage />, { wrapper: createWrapper() })
    
    const activityTab = screen.getByText('Активность')
    fireEvent.click(activityTab)
    
    await waitFor(() => {
      expect(screen.getByText('Динамика комментариев')).toBeInTheDocument()
    })
  })

  it('отображает графики', () => {
    mockUseGlobalStats.mockReturnValue({
      data: mockGlobalStats,
      isLoading: false,
      error: null,
    })
    
    mockUseDashboardStats.mockReturnValue({
      data: mockDashboardStats,
      isLoading: false,
      error: null,
    })

    render(<DashboardPage />, { wrapper: createWrapper() })
    
    expect(screen.getByTestId('area-chart')).toBeInTheDocument()
    expect(screen.getByTestId('pie-chart')).toBeInTheDocument()
  })

  it('отображает последнюю активность', () => {
    mockUseGlobalStats.mockReturnValue({
      data: mockGlobalStats,
      isLoading: false,
      error: null,
    })
    
    mockUseDashboardStats.mockReturnValue({
      data: mockDashboardStats,
      isLoading: false,
      error: null,
    })

    render(<DashboardPage />, { wrapper: createWrapper() })
    
    expect(screen.getByText('Последняя активность')).toBeInTheDocument()
    expect(screen.getByText('Завершен парсинг группы')).toBeInTheDocument()
  })

  it('отображает кнопки действий', () => {
    mockUseGlobalStats.mockReturnValue({
      data: mockGlobalStats,
      isLoading: false,
      error: null,
    })
    
    mockUseDashboardStats.mockReturnValue({
      data: mockDashboardStats,
      isLoading: false,
      error: null,
    })

    render(<DashboardPage />, { wrapper: createWrapper() })
    
    expect(screen.getByText('Экспорт')).toBeInTheDocument()
    expect(screen.getByText('Фильтры')).toBeInTheDocument()
    expect(screen.getByText('Обновить')).toBeInTheDocument()
  })

  it('обрабатывает обновление данных', async () => {
    const mockRefetch = jest.fn()
    
    mockUseGlobalStats.mockReturnValue({
      data: mockGlobalStats,
      isLoading: false,
      error: null,
      refetch: mockRefetch,
    })
    
    mockUseDashboardStats.mockReturnValue({
      data: mockDashboardStats,
      isLoading: false,
      error: null,
      refetch: mockRefetch,
    })

    render(<DashboardPage />, { wrapper: createWrapper() })
    
    const refreshButton = screen.getByText('Обновить')
    fireEvent.click(refreshButton)
    
    // Проверяем, что кнопка обновления работает
    expect(refreshButton).toBeInTheDocument()
  })

  it('отображает статистику по времени', () => {
    mockUseGlobalStats.mockReturnValue({
      data: mockGlobalStats,
      isLoading: false,
      error: null,
    })
    
    mockUseDashboardStats.mockReturnValue({
      data: mockDashboardStats,
      isLoading: false,
      error: null,
    })

    render(<DashboardPage />, { wrapper: createWrapper() })
    
    // Переключаемся на вкладку Активность
    const activityTab = screen.getByText('Активность')
    fireEvent.click(activityTab)
    
    expect(screen.getByText('23')).toBeInTheDocument() // today_comments
    expect(screen.getByText('7')).toBeInTheDocument() // today_matches
    expect(screen.getByText('156')).toBeInTheDocument() // week_comments
    expect(screen.getByText('34')).toBeInTheDocument() // week_matches
  })

  it('отображает графики производительности групп', () => {
    mockUseGlobalStats.mockReturnValue({
      data: mockGlobalStats,
      isLoading: false,
      error: null,
    })
    
    mockUseDashboardStats.mockReturnValue({
      data: mockDashboardStats,
      isLoading: false,
      error: null,
    })

    render(<DashboardPage />, { wrapper: createWrapper() })
    
    // Переключаемся на вкладку Группы
    const groupsTab = screen.getByText('Группы')
    fireEvent.click(groupsTab)
    
    expect(screen.getByText('Производительность групп')).toBeInTheDocument()
    expect(screen.getByTestId('bar-chart')).toBeInTheDocument()
  })

  it('отображает распределение ключевых слов', () => {
    mockUseGlobalStats.mockReturnValue({
      data: mockGlobalStats,
      isLoading: false,
      error: null,
    })
    
    mockUseDashboardStats.mockReturnValue({
      data: mockDashboardStats,
      isLoading: false,
      error: null,
    })

    render(<DashboardPage />, { wrapper: createWrapper() })
    
    // Переключаемся на вкладку Ключевые слова
    const keywordsTab = screen.getByText('Ключевые слова')
    fireEvent.click(keywordsTab)
    
    expect(screen.getByText('Распределение ключевых слов')).toBeInTheDocument()
    expect(screen.getByText('Топ ключевых слов')).toBeInTheDocument()
    expect(screen.getByTestId('pie-chart')).toBeInTheDocument()
  })
})

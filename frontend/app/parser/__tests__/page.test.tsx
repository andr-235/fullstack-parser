import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import ParserPage from '../page'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import {
  useParserState,
  useRecentRuns,
  useParserStats,
  useStartParser,
  useStopParser,
} from '@/hooks/use-parser'
import { useGroups } from '@/hooks/use-groups'
import type {
  ParseTaskResponse,
  ParserState,
  ParserStats,
  VKGroupResponse,
} from '@/types/api'

// --- Mocks ---
const mockUseParserState = useParserState as jest.Mock
const mockUseParserStats = useParserStats as jest.Mock
const mockUseRecentRuns = useRecentRuns as jest.Mock
const mockUseStartParser = useStartParser as jest.Mock
const mockUseStopParser = useStopParser as jest.Mock
const mockUseGroups = useGroups as jest.Mock

jest.mock('@/hooks/use-parser', () => ({
  useParserState: jest.fn(),
  useParserStats: jest.fn(),
  useRecentRuns: jest.fn(),
  useStartParser: jest.fn(),
  useStopParser: jest.fn(),
}))

jest.mock('@/hooks/use-groups', () => ({
  useGroups: jest.fn(),
}))

// --- Mock Data ---
const mockGroups: VKGroupResponse[] = [
  {
    id: 1,
    name: 'Test Group 1',
    screen_name: 'test_group_1',
    vk_id: 101,
    is_active: true,
    total_posts_parsed: 100,
    total_comments_found: 1000,
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
    is_closed: false,
    max_posts_to_check: 100,
  },
]

const mockStoppedState: ParserState = { status: 'stopped' }

const mockRunningState: ParserState = {
  status: 'running',
  task: {
    task_id: 'task-123',
    group_id: 1,
    group_name: 'Test Group 1',
    progress: 50,
    posts_processed: 50,
  },
}

const mockStats: ParserStats = {
  total_runs: 10,
  successful_runs: 8,
  failed_runs: 2,
  average_duration: 120,
  total_posts_processed: 1000,
  total_comments_found: 5000,
  total_comments_with_keywords: 500,
}

const mockRecentRuns: { items: ParseTaskResponse[]; total: number } = {
  items: [
    {
      task_id: 'task-abc',
      group_id: 1,
      group_name: 'Test Group 1',
      status: 'completed',
      started_at: new Date().toISOString(),
      completed_at: new Date().toISOString(),
      stats: {
        posts_processed: 10,
        comments_found: 50,
        comments_with_keywords: 5,
        new_comments: 20,
        keyword_matches: 5,
        duration_seconds: 60,
      },
    },
  ],
  total: 1,
}

const queryClient = new QueryClient()

const renderWithProviders = (ui: React.ReactElement) => {
  return render(
    <QueryClientProvider client={queryClient}>{ui}</QueryClientProvider>
  )
}

describe('ParserPage', () => {
  beforeEach(() => {
    // Reset mocks
    mockUseParserState.mockReturnValue({
      data: mockStoppedState,
      isLoading: false,
    })
    mockUseParserStats.mockReturnValue({ data: mockStats, isLoading: false })
    mockUseRecentRuns.mockReturnValue({
      data: mockRecentRuns,
      isLoading: false,
    })
    mockUseStartParser.mockReturnValue({ mutate: jest.fn(), isPending: false })
    mockUseStopParser.mockReturnValue({ mutate: jest.fn(), isPending: false })
    mockUseGroups.mockReturnValue({
      data: { items: mockGroups, total: mockGroups.length },
    })
  })

  it('должна рендериться без ошибок в состоянии "остановлен"', () => {
    renderWithProviders(<ParserPage />)
    expect(
      screen.getByRole('heading', { name: /Управление парсером/i })
    ).toBeInTheDocument()
    expect(screen.getByText('Остановлен')).toBeInTheDocument()
    expect(screen.getByText('Нет активных задач')).toBeInTheDocument()
  })

  it('должна отображать статистику и недавние запуски', () => {
    renderWithProviders(<ParserPage />)
    // Stats
    expect(screen.getByText(mockStats.total_runs)).toBeInTheDocument()
    // Recent Runs
    expect(
      screen.getByText(mockRecentRuns.items[0].group_name!)
    ).toBeInTheDocument()
    expect(screen.getByText('Завершено')).toBeInTheDocument()
  })

  it('должна отображать состояние "выполняется", когда парсер запущен', () => {
    mockUseParserState.mockReturnValue({
      data: mockRunningState,
      isLoading: false,
    })
    renderWithProviders(<ParserPage />)

    expect(screen.getByText('Выполняется')).toBeInTheDocument()
    expect(
      screen.getByRole('button', { name: /Остановить/i })
    ).toBeInTheDocument()
    if (mockRunningState.task?.group_name) {
      expect(
        screen.getByText(mockRunningState.task.group_name)
      ).toBeInTheDocument()
    }
    expect(
      screen.getByText(`${mockRunningState.task!.progress.toFixed(2)}%`)
    ).toBeInTheDocument()
  })

  it('должна позволять запустить парсер', async () => {
    const startMutate = jest.fn()
    mockUseStartParser.mockReturnValue({
      mutate: startMutate,
      isPending: false,
    })
    renderWithProviders(<ParserPage />)

    const startButton = screen.getByRole('button', { name: /Запустить/i })
    expect(startButton).toBeDisabled()

    // Radix select doesn't work well with getByRole, using querySelector
    const selectTrigger = document.querySelector('[aria-haspopup="listbox"]')
    fireEvent.mouseDown(selectTrigger as Element)

    const groupOption = await screen.findByText(mockGroups[0].name)
    fireEvent.click(groupOption)

    await waitFor(() => {
      expect(startButton).toBeEnabled()
    })

    fireEvent.click(startButton)

    expect(startMutate).toHaveBeenCalledWith({ group_id: mockGroups[0].id })
  })

  it('должна позволять остановить парсер', () => {
    mockUseParserState.mockReturnValue({
      data: mockRunningState,
      isLoading: false,
    })
    const stopMutate = jest.fn()
    mockUseStopParser.mockReturnValue({ mutate: stopMutate, isPending: false })

    renderWithProviders(<ParserPage />)

    const stopButton = screen.getByRole('button', { name: /Остановить/i })
    fireEvent.click(stopButton)

    expect(stopMutate).toHaveBeenCalled()
  })
})

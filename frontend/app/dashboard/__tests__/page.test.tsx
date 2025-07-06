import { render, screen } from '@testing-library/react'
import DashboardPage from '../page'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { useGlobalStats } from '@/hooks/use-stats'

jest.mock('@/hooks/use-stats', () => ({
  useDashboardStats: jest.fn(() => ({
    data: {
      today_comments: 0,
      today_matches: 0,
      week_comments: 0,
      week_matches: 0,
      top_groups: [],
      top_keywords: [],
      recent_activity: [],
    },
    isLoading: false,
    error: null,
  })),
  useGlobalStats: jest.fn(() => ({
    data: {
      total_groups: 0,
      active_groups: 0,
      total_keywords: 0,
      active_keywords: 0,
      total_comments: 0,
      comments_with_keywords: 0,
    },
    isLoading: false,
    error: null,
  })),
}))

const queryClient = new QueryClient()

const renderWithProviders = (ui: React.ReactElement) => {
  return render(
    <QueryClientProvider client={queryClient}>{ui}</QueryClientProvider>
  )
}

describe('DashboardPage', () => {
  it('должна рендериться без ошибок', () => {
    renderWithProviders(<DashboardPage />)
    expect(
      screen.getByRole('heading', { name: /Активность комментариев/i })
    ).toBeInTheDocument()
  })

  it('должна правильно отображать статистику', () => {
    const mockStats = {
      total_groups: 10,
      active_groups: 5,
      total_keywords: 100,
      active_keywords: 50,
      total_comments: 1000,
      comments_with_keywords: 200,
    }
    ;(useGlobalStats as jest.Mock).mockReturnValue({
      data: mockStats,
      isLoading: false,
      error: null,
    })

    renderWithProviders(<DashboardPage />)

    expect(screen.getByText('10')).toBeInTheDocument()
    expect(screen.getByText('1000')).toBeInTheDocument()
    expect(screen.getByText('100')).toBeInTheDocument()
  })
})

import { render, screen } from '@testing-library/react'
import ParserPage from '../page'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'

jest.mock('@/hooks/use-parser', () => ({
  useParserState: jest.fn(() => ({ data: { status: 'stopped' } })),
  useParserStats: jest.fn(() => ({ data: {} })),
  useRecentParseTasks: jest.fn(() => ({ data: { items: [], total: 0 } })),
  useRecentRuns: jest.fn(() => ({ data: { items: [], total: 0 } })),
  useStartParser: jest.fn(() => ({ mutate: jest.fn() })),
  useStopParser: jest.fn(() => ({ mutate: jest.fn() })),
}))

jest.mock('@/hooks/use-groups', () => ({
  useGroups: jest.fn(() => ({
    data: { items: [], total: 0 },
  })),
}))

const queryClient = new QueryClient()

const renderWithProviders = (ui: React.ReactElement) => {
  return render(
    <QueryClientProvider client={queryClient}>{ui}</QueryClientProvider>
  )
}

describe('ParserPage', () => {
  it('должна рендериться без ошибок', () => {
    renderWithProviders(<ParserPage />)
    expect(
      screen.getByRole('heading', { name: /Управление парсером/i })
    ).toBeInTheDocument()
  })
})

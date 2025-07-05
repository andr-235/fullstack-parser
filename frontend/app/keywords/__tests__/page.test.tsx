import { render, screen, fireEvent, waitFor, within } from '@testing-library/react'
import KeywordsPage from '../page'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { Toaster } from 'react-hot-toast'
import type { KeywordResponse } from '@/types/api'

// Mocks
const mockUseKeywords = jest.fn()
const mockUseCreateKeyword = jest.fn()

jest.mock('@/components/ui/loading-spinner', () => ({
  LoadingSpinnerWithText: ({ text }: { text: string }) => <div>{text}</div>,
}))

jest.mock('@/hooks/use-keywords', () => ({
  useKeywords: (props: any) => mockUseKeywords(props),
  useKeywordCategories: jest.fn(() => ({ data: [] })),
  useCreateKeyword: () => mockUseCreateKeyword(),
  useUpdateKeyword: jest.fn(() => ({ mutate: jest.fn() })),
  useDeleteKeyword: jest.fn(() => ({ mutate: jest.fn() })),
}))

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: false,
    },
  },
})

const renderWithProviders = (ui: React.ReactElement) => {
  return render(
    <QueryClientProvider client={queryClient}>
      {ui}
      <Toaster />
    </QueryClientProvider>
  )
}

const mockKeywords: KeywordResponse[] = [
  {
    id: 1,
    word: 'Test Keyword 1',
    is_active: true,
    is_case_sensitive: false,
    is_whole_word: false,
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
    category: 'Test',
    total_matches: 10,
  },
  {
    id: 2,
    word: 'Test Keyword 2',
    is_active: false,
    is_case_sensitive: true,
    is_whole_word: true,
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
    category: 'Test',
    total_matches: 5,
  },
]

describe('KeywordsPage', () => {
  beforeEach(() => {
    // Reset mocks before each test
    queryClient.clear()
    mockUseKeywords.mockReturnValue({
      data: { items: [], total: 0 },
      isLoading: false,
    })
    mockUseCreateKeyword.mockReturnValue({
      mutate: jest.fn(),
      isPending: false,
    })
  })

  it('должна рендериться без ошибок', () => {
    renderWithProviders(<KeywordsPage />)
    expect(
      screen.getByRole('heading', { name: /Ключевые слова/i, level: 1 })
    ).toBeInTheDocument()
  })

  it('должна отображать список ключевых слов', () => {
    mockUseKeywords.mockReturnValue({
      data: { items: mockKeywords, total: 2 },
      isLoading: false,
    })
    renderWithProviders(<KeywordsPage />)
    expect(screen.getByText('Test Keyword 1')).toBeInTheDocument()
    expect(screen.getByText('Test Keyword 2')).toBeInTheDocument()
  })

  it('должна успешно добавлять новое ключевое слово', async () => {
    const createMutate = jest.fn()
    mockUseCreateKeyword.mockReturnValue({
      mutate: createMutate,
      isPending: false,
    })

    renderWithProviders(<KeywordsPage />)

    const addKeywordCard = screen
      .getByPlaceholderText(/Новое ключевое слово/i)
      .closest('div.space-x-2') as HTMLElement
    if (!addKeywordCard) throw new Error('Add keyword card not found')

    const input = within(addKeywordCard).getByPlaceholderText(
      /Новое ключевое слово/i
    )
    const addButton = within(addKeywordCard).getByRole('button', {
      name: /Добавить/i,
    })

    fireEvent.change(input, { target: { value: 'New Keyword' } })
    fireEvent.click(addButton)

    await waitFor(() => {
      expect(createMutate).toHaveBeenCalledWith(
        {
          word: 'New Keyword',
          is_active: true,
          is_case_sensitive: false,
          is_whole_word: false,
          category: 'Без категории',
        },
        {
          onSuccess: expect.any(Function),
        }
      )
    })
  })

  it('должна показывать ошибку при попытке добавить пустое ключевое слово', async () => {
    renderWithProviders(<KeywordsPage />)

    const addKeywordCard = screen
      .getByPlaceholderText(/Новое ключевое слово/i)
      .closest('div.space-x-2') as HTMLElement
    if (!addKeywordCard) throw new Error('Add keyword card not found')

    const addButton = within(addKeywordCard).getByRole('button', {
      name: /Добавить/i,
    })
    fireEvent.click(addButton)

    // Check that create was not called
    expect(mockUseCreateKeyword().mutate).not.toHaveBeenCalled()
  })
}) 
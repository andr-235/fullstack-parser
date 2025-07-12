import {
  render,
  screen,
  fireEvent,
  waitFor,
  within,
} from '@testing-library/react'
import KeywordsPage from '../page'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { Toaster } from 'react-hot-toast'
import type { KeywordResponse } from '@/types/api'

// Mocks
const mockUseKeywords = jest.fn()
const mockUseCreateKeyword = jest.fn()
const mockUseUpdateKeyword = jest.fn()
const mockUseDeleteKeyword = jest.fn()

jest.mock('@/components/ui/loading-spinner', () => ({
  LoadingSpinnerWithText: ({ text }: { text: string }) => <div>{text}</div>,
}))

jest.mock('@/hooks/use-keywords', () => ({
  useKeywords: (props: any) => mockUseKeywords(props),
  useKeywordCategories: jest.fn(() => ({ data: ['General', 'Tech'] })),
  useCreateKeyword: () => mockUseCreateKeyword(),
  useUpdateKeyword: () => mockUseUpdateKeyword(),
  useDeleteKeyword: () => mockUseDeleteKeyword(),
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
    word: 'Inactive Keyword',
    is_active: false,
    is_case_sensitive: true,
    is_whole_word: true,
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
    category: 'Tech',
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
      error: null,
    })
    mockUseCreateKeyword.mockReturnValue({
      mutate: jest.fn(),
      isPending: false,
    })
    mockUseUpdateKeyword.mockReturnValue({
      mutate: jest.fn(),
      mutateAsync: jest.fn().mockResolvedValue({}),
      isPending: false,
    })
    mockUseDeleteKeyword.mockReturnValue({
      mutate: jest.fn(),
      isPending: false,
    })
    jest.spyOn(window, 'confirm').mockReturnValue(true)
  })

  it('должна рендериться без ошибок', () => {
    renderWithProviders(<KeywordsPage />)
    expect(
      screen.getByRole('heading', { name: /Ключевые слова/i, level: 1 })
    ).toBeInTheDocument()
  })

  it('должна показывать спиннер загрузки', () => {
    mockUseKeywords.mockReturnValue({
      data: null,
      isLoading: true,
      error: null,
    })
    renderWithProviders(<KeywordsPage />)
    expect(screen.getByText('Загрузка ключевых слов...')).toBeInTheDocument()
  })

  it('должна показывать сообщение об ошибке', () => {
    const error = new Error('Failed to fetch')
    mockUseKeywords.mockReturnValue({
      data: null,
      isLoading: false,
      error,
    })
    renderWithProviders(<KeywordsPage />)
    expect(screen.getByText('Ошибка загрузки')).toBeInTheDocument()
    expect(screen.getByText(error.message)).toBeInTheDocument()
  })

  it('должна отображать список ключевых слов', () => {
    mockUseKeywords.mockReturnValue({
      data: { items: mockKeywords, total: 2 },
      isLoading: false,
    })
    renderWithProviders(<KeywordsPage />)
    expect(screen.getByText('Test Keyword 1')).toBeInTheDocument()
    expect(screen.getByText('Inactive Keyword')).toBeInTheDocument()
  })

  it('должна правильно отображать статистику', () => {
    mockUseKeywords.mockReturnValue({
      data: {
        items: mockKeywords,
        total: mockKeywords.length,
      },
      isLoading: false,
      error: null,
    })
    renderWithProviders(<KeywordsPage />)

    // Total Keywords
    expect(screen.getByText(mockKeywords.length.toString())).toBeInTheDocument()
    // Active Keywords
    const activeKeywords = mockKeywords.filter((k) => k.is_active).length
    expect(screen.getByText(activeKeywords.toString())).toBeInTheDocument()
    // Total Matches
    const totalMatches = mockKeywords.reduce(
      (sum, k) => sum + k.total_matches,
      0
    )
    expect(
      screen.getByText(new Intl.NumberFormat('ru-RU').format(totalMatches))
    ).toBeInTheDocument()
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

    const input =
      within(addKeywordCard).getByPlaceholderText(/Новое ключевое слово/i)
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

  it('должна удалять ключевое слово', async () => {
    mockUseKeywords.mockReturnValue({
      data: { items: mockKeywords, total: 2 },
      isLoading: false,
      error: null,
    })
    const deleteMutate = jest.fn()
    mockUseDeleteKeyword.mockReturnValue({
      mutate: deleteMutate,
      isPending: false,
    })

    renderWithProviders(<KeywordsPage />)

    const keywordRow = screen.getByText('Test Keyword 1').closest('div.grid')
    const deleteButton = within(keywordRow as HTMLElement).getByRole('button', {
      name: /удалить/i,
    })

    fireEvent.click(deleteButton)

    expect(window.confirm).toHaveBeenCalled()
    expect(deleteMutate).toHaveBeenCalledWith(mockKeywords[0].id)
  })

  it('должна переключать статус активности', async () => {
    mockUseKeywords.mockReturnValue({
      data: { items: mockKeywords, total: 2 },
      isLoading: false,
      error: null,
    })
    const updateMutate = jest.fn()
    mockUseUpdateKeyword.mockReturnValue({
      mutate: updateMutate,
      isPending: false,
    })

    renderWithProviders(<KeywordsPage />)

    const keywordRow = screen.getByText('Test Keyword 1').closest('div.grid')
    const switchControl = within(keywordRow as HTMLElement).getByRole('switch')

    fireEvent.click(switchControl)

    expect(updateMutate).toHaveBeenCalledWith(
      {
        keywordId: mockKeywords[0].id,
        data: { is_active: !mockKeywords[0].is_active },
      },
      {
        onSuccess: expect.any(Function),
        onError: expect.any(Function),
      }
    )
  })

  it('должна позволять редактировать и сохранять ключевое слово', async () => {
    mockUseKeywords.mockReturnValue({
      data: { items: mockKeywords, total: 2 },
      isLoading: false,
      error: null,
    })
    const updateMutateAsync = jest.fn().mockResolvedValue({})
    mockUseUpdateKeyword.mockReturnValue({
      mutate: jest.fn(),
      mutateAsync: updateMutateAsync,
      isPending: false,
    })

    renderWithProviders(<KeywordsPage />)

    const keywordRow = screen.getByText('Test Keyword 1').closest('div.grid')
    const editButton = within(keywordRow as HTMLElement).getByRole('button', {
      name: /редактировать/i,
    })

    // Enter edit mode
    fireEvent.click(editButton)

    const input = within(keywordRow as HTMLElement).getByDisplayValue(
      'Test Keyword 1'
    )
    const saveButton = within(keywordRow as HTMLElement).getByRole('button', {
      name: /сохранить/i,
    })

    expect(input).toBeInTheDocument()
    expect(saveButton).toBeInTheDocument()

    // Change value and save
    fireEvent.change(input, { target: { value: 'Updated Keyword' } })
    fireEvent.click(saveButton)

    await waitFor(() => {
      expect(updateMutateAsync).toHaveBeenCalledWith({
        keywordId: mockKeywords[0].id,
        data: { word: 'Updated Keyword' },
      })
    })
  })

  it('должна фильтровать ключевые слова по поисковому запросу', async () => {
    renderWithProviders(<KeywordsPage />)

    const searchInput = screen.getByPlaceholderText(/Поиск по словам.../i)
    fireEvent.change(searchInput, { target: { value: 'search term' } })

    await waitFor(() => {
      expect(mockUseKeywords).toHaveBeenCalledWith(
        expect.objectContaining({
          q: 'search term',
        })
      )
    })
  })

  it('должна фильтровать по статусу активности', async () => {
    renderWithProviders(<KeywordsPage />)

    const activeOnlySwitch = screen.getByLabelText(/Только активные/i)
    // It's on by default, so we turn it off
    fireEvent.click(activeOnlySwitch)

    await waitFor(() => {
      expect(mockUseKeywords).toHaveBeenCalledWith(
        expect.objectContaining({
          active_only: false,
        })
      )
    })
  })

  it('должна фильтровать по категории', async () => {
    renderWithProviders(<KeywordsPage />)

    const categorySelect = screen.getByRole('combobox')
    fireEvent.click(categorySelect)

    // The category list is mocked to return ['General', 'Tech']
    const option = await screen.findByText('Tech')
    fireEvent.click(option)

    await waitFor(() => {
      expect(mockUseKeywords).toHaveBeenCalledWith(
        expect.objectContaining({
          category: 'Tech',
        })
      )
    })
  })
})

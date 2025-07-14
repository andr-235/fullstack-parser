import {
  render,
  screen,
  fireEvent,
  waitFor,
  within,
  act,
} from '@testing-library/react'
import KeywordsPage from './KeywordsPage'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { Toaster } from 'react-hot-toast'
import type { KeywordResponse } from '@/types/api'

// Моки хуков
const mockUseKeywords = jest.fn()
const mockUseCreateKeyword = jest.fn()
const mockUseDeleteKeyword = jest.fn()
// const mockUseUpdateKeyword = jest.fn() // Удаляем, теперь не нужен
const mockUseKeywordCategories = jest.fn()

// Вынесенные моки для update
const updateMutate = jest.fn()
const updateMutateAsync = jest.fn().mockResolvedValue({})
const updateKeywordMutation = {
  mutate: updateMutate,
  mutateAsync: updateMutateAsync,
  isPending: false,
}

jest.mock('@/hooks/use-keywords', () => ({
  useKeywords: (...args: any[]) => mockUseKeywords(...args),
  useCreateKeyword: (...args: any[]) => mockUseCreateKeyword(...args),
  useDeleteKeyword: (...args: any[]) => mockUseDeleteKeyword(...args),
  useUpdateKeyword: (...args: any[]) => updateKeywordMutation,
  useKeywordCategories: (...args: any[]) => ({ data: ['General', 'Tech'] }),
}))

jest.mock('@/components/ui/loading-spinner', () => ({
  LoadingSpinner: () => <div role="status">Загрузка ключевых слов...</div>,
  LoadingSpinnerWithText: ({ text }: { text: string }) => <div>{text}</div>,
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

// Глобальный мок scrollIntoView для jsdom
beforeAll(() => {
  window.HTMLElement.prototype.scrollIntoView = function () {}
})

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
    mockUseDeleteKeyword.mockReturnValue({
      mutate: jest.fn(),
      isPending: false,
    })
    mockUseKeywordCategories.mockReturnValue({ data: ['General', 'Tech'] })
    jest.spyOn(window, 'confirm').mockImplementation(() => true)
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

    const row = screen
      .getAllByRole('row')
      .find((tr) => within(tr).queryByText('Test Keyword 1')) as HTMLElement
    expect(row).toBeInTheDocument()
    const deleteButton = within(row).getByRole('button', { name: /удалить/i })

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

    renderWithProviders(<KeywordsPage />)

    const row = screen
      .getAllByRole('row')
      .find((tr) => within(tr).queryByText('Test Keyword 1')) as HTMLElement
    expect(row).toBeInTheDocument()
    const switchControl = within(row).getByRole('switch')

    await act(async () => {
      fireEvent.click(switchControl)
    })
    screen.debug()

    await waitFor(() => {
      expect(updateMutateAsync).toHaveBeenCalledWith({
        keywordId: mockKeywords[0].id,
        data: { is_active: !mockKeywords[0].is_active },
      })
    })
  })

  it('должна позволять редактировать и сохранять ключевое слово', async () => {
    mockUseKeywords.mockReturnValue({
      data: { items: mockKeywords, total: 2 },
      isLoading: false,
      error: null,
    })

    renderWithProviders(<KeywordsPage />)

    const row = screen
      .getAllByRole('row')
      .find((tr) => within(tr).queryByText('Test Keyword 1')) as HTMLElement
    expect(row).toBeInTheDocument()
    const editButton = within(row).getByRole('button', {
      name: /редактировать/i,
    })

    // Enter edit mode
    await act(async () => {
      fireEvent.click(editButton)
    })

    const input = within(row).getByDisplayValue('Test Keyword 1')
    await act(async () => {
      fireEvent.change(input, { target: { value: 'Updated Keyword' } })
    })
    const saveButton = within(row).getByRole('button', { name: /сохранить/i })
    await act(async () => {
      fireEvent.click(saveButton)
    })
    screen.debug()

    await waitFor(() => {
      expect(updateMutate).toHaveBeenCalledWith(
        { keywordId: mockKeywords[0].id, data: { word: 'Updated Keyword' } },
        expect.any(Object)
      )
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
    screen.debug()

    // Используем кастомный matcher для поиска 'Tech'
    // Добавим дополнительный debug DOM
    // Попробуем найти опцию по data-value или role="option"
    const options = screen.getAllByRole('option')
    const techOption = options.find((opt) => opt.textContent?.includes('Tech'))
    expect(techOption).toBeDefined()
    fireEvent.click(techOption!)

    await waitFor(() => {
      expect(mockUseKeywords).toHaveBeenCalledWith(
        expect.objectContaining({
          category: 'Tech',
        })
      )
    })
  })
})

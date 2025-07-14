import {
  render,
  screen,
  fireEvent,
  waitFor,
  within,
  act,
} from '@testing-library/react'
import CommentsPage from '@/app/comments/page'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { useInfiniteComments } from '@/hooks/use-comments'
import { useGroups } from '@/hooks/use-groups'
import { useKeywords } from '@/hooks/use-keywords'
import type {
  VKCommentResponse,
  VKGroupResponse,
  KeywordResponse,
} from '@/types/api'
import '@testing-library/jest-dom'

jest.mock('@/hooks/use-comments', () => ({
  useInfiniteComments: jest.fn(),
}))

jest.mock('@/hooks/use-groups', () => ({
  useGroups: jest.fn(),
}))

jest.mock('@/hooks/use-keywords', () => ({
  useKeywords: jest.fn(),
}))

const mockUseInfiniteComments = useInfiniteComments as jest.Mock
const mockUseGroups = useGroups as jest.Mock
const mockUseKeywords = useKeywords as jest.Mock

const queryClient = new QueryClient()

const renderWithProviders = (ui: React.ReactElement) => {
  return render(
    <QueryClientProvider client={queryClient}>{ui}</QueryClientProvider>
  )
}

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

const mockKeywords: KeywordResponse[] = [
  {
    id: 1,
    word: 'Test Keyword 1',
    is_active: true,
    is_case_sensitive: false,
    is_whole_word: false,
    total_matches: 10,
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
  },
]

const mockComment = (id: number, text: string): VKCommentResponse => ({
  id,
  text,
  post_id: id,
  vk_id: id * 100,
  post_vk_id: id * 10,
  author_id: id * 1000,
  author_name: `Test User ${id}`,
  published_at: new Date().toISOString(),
  created_at: new Date().toISOString(),
  updated_at: new Date().toISOString(),
  group: mockGroups[0],
  matched_keywords: [mockKeywords[0]],
  likes_count: 0,
  has_attachments: false,
  matched_keywords_count: 1,
  is_processed: true,
})

describe('CommentsPage', () => {
  beforeEach(() => {
    mockUseInfiniteComments.mockReturnValue({
      data: { pages: [], pageParams: [] },
      fetchNextPage: jest.fn(),
      hasNextPage: false,
      isFetchingNextPage: false,
      isLoading: false,
      error: null,
    })
    mockUseGroups.mockReturnValue({ data: { items: mockGroups, total: 1 } })
    mockUseKeywords.mockReturnValue({ data: { items: mockKeywords, total: 1 } })
    jest.useFakeTimers()
  })
  afterEach(() => {
    jest.useRealTimers()
  })

  it('должна рендериться без ошибок', () => {
    renderWithProviders(<CommentsPage />)
    expect(
      screen.getByRole('heading', {
        name: /Фильтры комментариев/i,
        level: 1,
      }) as unknown as HTMLElement
    ).toBeInTheDocument()
  })

  it('должна показывать спиннер загрузки', async () => {
    mockUseInfiniteComments.mockReturnValue({
      data: { pages: [], pageParams: [] },
      isLoading: true,
      isFetching: true,
      isFetchingNextPage: false,
    })
    await act(async () => {
      renderWithProviders(<CommentsPage />)
    })
    expect(
      screen.getByRole('status') as unknown as HTMLElement
    ).toBeInTheDocument()
  })

  it('должна показывать сообщение об ошибке', async () => {
    const error = new Error('Failed to fetch comments')
    mockUseInfiniteComments.mockReturnValue({
      data: { pages: [], pageParams: [] },
      isLoading: false,
      error,
    })
    await act(async () => {
      renderWithProviders(<CommentsPage />)
    })
    expect(
      screen.getByText(`Ошибка: ${error.message}`) as unknown as HTMLElement
    ).toBeInTheDocument()
  })

  it('должна отображать список комментариев', async () => {
    mockUseInfiniteComments.mockReturnValue({
      data: {
        pages: [
          {
            items: [
              mockComment(1, 'This is a test comment'),
              mockComment(2, 'Another test comment'),
            ],
            total: 2,
            limit: 2,
            skip: 0,
          },
        ],
        pageParams: [null],
      },
      isLoading: false,
      error: null,
    })
    await act(async () => {
      renderWithProviders(<CommentsPage />)
    })
    expect(
      screen.getByText('This is a test comment') as unknown as HTMLElement
    ).toBeInTheDocument()
    expect(
      screen.getByText('Another test comment') as unknown as HTMLElement
    ).toBeInTheDocument()
  })

  it('должна показывать сообщение, когда комментарии не найдены', async () => {
    await act(async () => {
      renderWithProviders(<CommentsPage />)
    })
    expect(
      screen.getByText('Комментарии не найдены.') as unknown as HTMLElement
    ).toBeInTheDocument()
  })

  it('должна фильтровать комментарии по поисковому запросу', async () => {
    renderWithProviders(<CommentsPage />)

    const searchInput = screen.getByPlaceholderText('Поиск по тексту...')
    await act(async () => {
      fireEvent.change(searchInput, { target: { value: 'filter' } })
      jest.advanceTimersByTime(300)
    })

    await waitFor(() => {
      expect(mockUseInfiniteComments).toHaveBeenCalledWith(
        expect.objectContaining({
          text: 'filter',
        })
      )
    })
  })

  it('должна загружать больше комментариев при нажатии на кнопку', async () => {
    const fetchNextPage = jest.fn()
    mockUseInfiniteComments.mockReturnValue({
      data: {
        pages: [
          {
            items: [mockComment(1, 'First comment')],
            total: 2,
            limit: 1,
            skip: 0,
          },
        ],
        pageParams: [null],
      },
      fetchNextPage,
      hasNextPage: true,
      isFetchingNextPage: false,
      isLoading: false,
      error: null,
    })

    renderWithProviders(<CommentsPage />)
    const loadMoreButton = screen.getByRole('button', {
      name: /Загрузить еще/i,
    })
    await act(async () => {
      fireEvent.click(loadMoreButton)
    })
    expect(fetchNextPage).toHaveBeenCalled()
  })

  it('должна фильтровать по группе', async () => {
    renderWithProviders(<CommentsPage />)

    // Используем aria-label для SelectTrigger
    const groupSelectTrigger = screen.getByLabelText('Группа')
    await act(async () => {
      fireEvent.mouseDown(groupSelectTrigger)
    })

    const groupOption = await screen.findByText('Test Group 1')
    await act(async () => {
      fireEvent.click(groupOption) // Явно кликаем по Item
    })
    await waitFor(() => {
      const calls = mockUseInfiniteComments.mock.calls.map((c) => c[0])
      expect(calls).toEqual(
        expect.arrayContaining([
          expect.objectContaining({ group_id: mockGroups[0].id }),
        ])
      )
    })
  })

  it('должна фильтровать по ключевому слову', async () => {
    renderWithProviders(<CommentsPage />)

    // Используем aria-label для второго SelectTrigger
    const keywordSelectTrigger = screen.getByLabelText('Ключевое слово')
    await act(async () => {
      fireEvent.mouseDown(keywordSelectTrigger)
    })

    const keywordOption = await screen.findByText('Test Keyword 1')
    await act(async () => {
      fireEvent.click(keywordOption) // Явно кликаем по Item
    })
    await waitFor(() => {
      const calls = mockUseInfiniteComments.mock.calls.map((c) => c[0])
      expect(calls).toEqual(
        expect.arrayContaining([
          expect.objectContaining({ keyword_id: mockKeywords[0].id }),
        ])
      )
    })
  })
})

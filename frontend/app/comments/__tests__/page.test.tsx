import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import CommentsPage from '../page'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { useInfiniteComments } from '@/hooks/use-comments'

jest.mock('@/hooks/use-comments', () => ({
  useInfiniteComments: jest.fn(),
}))

jest.mock('@/hooks/use-groups', () => ({
  useGroups: jest.fn(() => ({
    data: { items: [], total: 0 },
  })),
}))

jest.mock('@/hooks/use-keywords', () => ({
  useKeywords: jest.fn(() => ({
    data: { items: [], total: 0 },
  })),
}))

const mockUseInfiniteComments = useInfiniteComments as jest.Mock

const queryClient = new QueryClient()

const renderWithProviders = (ui: React.ReactElement) => {
  return render(
    <QueryClientProvider client={queryClient}>{ui}</QueryClientProvider>
  )
}

const mockComment = (id: number, text: string) => ({
  id,
  text,
  post_id: id,
  vk_group_id: 1,
  owner_id: 1,
  created_at: new Date().toISOString(),
  vk_group: { name: 'Test Group' },
  author: { first_name: 'Test', last_name: 'User' },
  matches: [],
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
  })

  it('должна рендериться без ошибок', () => {
    renderWithProviders(<CommentsPage />)
    expect(
      screen.getByRole('heading', { name: /Фильтры комментариев/i })
    ).toBeInTheDocument()
  })

  it('должна отображать список комментариев', () => {
    mockUseInfiniteComments.mockReturnValue({
      data: {
        pages: [
          {
            items: [
              mockComment(1, 'This is a test comment'),
              mockComment(2, 'Another test comment'),
            ],
            total: 2,
          },
        ],
        pageParams: [null],
      },
      isLoading: false,
    })

    renderWithProviders(<CommentsPage />)
    expect(screen.getByText('This is a test comment')).toBeInTheDocument()
    expect(screen.getByText('Another test comment')).toBeInTheDocument()
  })

  it('должна показывать сообщение, когда комментарии не найдены', () => {
    renderWithProviders(<CommentsPage />)
    expect(screen.getByText('Комментарии не найдены.')).toBeInTheDocument()
  })

  it('должна фильтровать комментарии по поисковому запросу', async () => {
    renderWithProviders(<CommentsPage />)

    const searchInput = screen.getByPlaceholderText(/Поиск по тексту/i)
    fireEvent.change(searchInput, { target: { value: 'filter' } })

    await waitFor(() => {
      expect(mockUseInfiniteComments).toHaveBeenCalledWith(
        expect.objectContaining({
          text: 'filter',
        })
      )
    })
  })
})

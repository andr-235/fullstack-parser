import React from 'react'
import { render, screen, fireEvent } from '@testing-library/react'
import { CommentsFilters } from '../CommentsFilters'

// Mock hooks
jest.mock('@/shared/hooks', () => ({
  useDebounce: jest.fn((value) => value),
}))

const mockGroups = [
  {
    id: 1,
    name: 'Группа 1',
    vk_id: 1,
    screen_name: 'group1',
    description: '',
    is_active: true,
    max_posts_to_check: 10,
    total_posts_parsed: 0,
    total_comments_found: 0,
    is_closed: false,
    created_at: '',
    updated_at: '',
  },
  {
    id: 2,
    name: 'Группа 2',
    vk_id: 2,
    screen_name: 'group2',
    description: '',
    is_active: true,
    max_posts_to_check: 10,
    total_posts_parsed: 0,
    total_comments_found: 0,
    is_closed: false,
    created_at: '',
    updated_at: '',
  },
]

const mockKeywords = [
  {
    id: 1,
    word: 'ключевое слово 1',
    category: '',
    description: '',
    is_active: true,
    is_case_sensitive: false,
    is_whole_word: false,
    total_matches: 0,
    created_at: '',
    updated_at: '',
  },
  {
    id: 2,
    word: 'ключевое слово 2',
    category: '',
    description: '',
    is_active: true,
    is_case_sensitive: false,
    is_whole_word: false,
    total_matches: 0,
    created_at: '',
    updated_at: '',
  },
]

const mockFilters = {
  text: '',
  groupId: null,
  keywordId: null,
  authorScreenName: [],
  dateFrom: '',
  dateTo: '',
  status: '',
}

describe('CommentsFilters', () => {
  const mockOnFiltersChange = jest.fn()
  const mockOnReset = jest.fn()

  beforeEach(() => {
    jest.clearAllMocks()
  })

  it('renders all filter inputs', () => {
    render(
      <CommentsFilters
        groups={mockGroups}
        keywords={mockKeywords}
        filters={mockFilters}
        onFiltersChange={mockOnFiltersChange}
        onReset={mockOnReset}
      />
    )

    expect(
      screen.getByPlaceholderText('Введите текст для поиска...')
    ).toBeInTheDocument()
    expect(screen.getByText('Все группы')).toBeInTheDocument()
    expect(screen.getByText('Все ключевые слова')).toBeInTheDocument()
    expect(screen.getByText('Все статусы')).toBeInTheDocument()
  })

  it('calls onFiltersChange when text input changes', () => {
    render(
      <CommentsFilters
        groups={mockGroups}
        keywords={mockKeywords}
        filters={mockFilters}
        onFiltersChange={mockOnFiltersChange}
        onReset={mockOnReset}
      />
    )

    const textInput = screen.getByPlaceholderText('Введите текст для поиска...')
    fireEvent.change(textInput, { target: { value: 'test' } })

    expect(mockOnFiltersChange).toHaveBeenCalledWith({
      ...mockFilters,
      text: 'test',
    })
  })

  it('calls onReset when reset button is clicked', () => {
    render(
      <CommentsFilters
        groups={mockGroups}
        keywords={mockKeywords}
        filters={mockFilters}
        onFiltersChange={mockOnFiltersChange}
        onReset={mockOnReset}
      />
    )

    const resetButton = screen.getByText('Сбросить')
    fireEvent.click(resetButton)

    expect(mockOnReset).toHaveBeenCalled()
  })

  it('displays special authors when they exist', () => {
    const filtersWithAuthors = {
      ...mockFilters,
      authorScreenName: ['author1', 'author2'],
    }

    render(
      <CommentsFilters
        groups={mockGroups}
        keywords={mockKeywords}
        filters={filtersWithAuthors}
        onFiltersChange={mockOnFiltersChange}
        onReset={mockOnReset}
      />
    )

    expect(screen.getByText('author1')).toBeInTheDocument()
    expect(screen.getByText('author2')).toBeInTheDocument()
  })
})

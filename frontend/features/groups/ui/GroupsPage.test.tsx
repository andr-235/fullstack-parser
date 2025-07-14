import {
  render,
  screen,
  fireEvent,
  waitFor,
  within,
} from '@testing-library/react'
import GroupsPage from '@/app/groups/page'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { Toaster } from 'react-hot-toast'
import type { VKGroupResponse } from '@/types/api'

// Mocks
const mockUseGroups = jest.fn()
const mockUseCreateGroup = jest.fn()
const mockUseUpdateGroup = jest.fn()
const mockUseDeleteGroup = jest.fn()

jest.mock('@/hooks/use-groups', () => ({
  useGroups: (props?: any) => mockUseGroups(props),
  useCreateGroup: () => mockUseCreateGroup(),
  useUpdateGroup: () => mockUseUpdateGroup(),
  useDeleteGroup: () => mockUseDeleteGroup(),
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

const mockGroups: VKGroupResponse[] = [
  {
    id: 1,
    name: 'Active Group',
    screen_name: 'active_group',
    vk_id: 101,
    is_active: true,
    total_posts_parsed: 100,
    total_comments_found: 1000,
    last_parsed_at: new Date().toISOString(),
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
    is_closed: false,
    max_posts_to_check: 100,
  },
  {
    id: 2,
    name: 'Inactive Group',
    screen_name: 'inactive_group',
    vk_id: 102,
    is_active: false,
    total_posts_parsed: 50,
    total_comments_found: 500,
    last_parsed_at: new Date().toISOString(),
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
    is_closed: false,
    max_posts_to_check: 100,
  },
]

describe('GroupsPage', () => {
  beforeEach(() => {
    mockUseGroups.mockReturnValue({
      data: { items: [], total: 0 },
      isLoading: false,
      error: null,
    })
    mockUseCreateGroup.mockReturnValue({ mutate: jest.fn(), isPending: false })
    mockUseUpdateGroup.mockReturnValue({ mutate: jest.fn() })
    mockUseDeleteGroup.mockReturnValue({ mutate: jest.fn() })
    jest.spyOn(window, 'confirm').mockReturnValue(true)
  })

  it('должна рендериться без ошибок', () => {
    renderWithProviders(<GroupsPage />)
    expect(
      screen.getByRole('heading', { name: /VK Группы/i, level: 1 })
    ).toBeInTheDocument()
  })

  it('должна показывать спиннер загрузки', () => {
    mockUseGroups.mockReturnValue({
      data: null,
      isLoading: true,
      error: null,
    })
    renderWithProviders(<GroupsPage />)
    expect(screen.getByText('Загрузка групп...')).toBeInTheDocument()
  })

  it('должна показывать сообщение об ошибке', () => {
    mockUseGroups.mockReturnValue({
      data: null,
      isLoading: false,
      error: new Error('Failed to fetch'),
    })
    renderWithProviders(<GroupsPage />)
    expect(screen.getByText('Ошибка загрузки групп')).toBeInTheDocument()
  })

  it('должна отображать список групп', () => {
    mockUseGroups.mockReturnValue({
      data: { items: mockGroups, total: mockGroups.length },
      isLoading: false,
      error: null,
    })
    renderWithProviders(<GroupsPage />)
    expect(screen.getByText('Active Group')).toBeInTheDocument()
    expect(screen.getByText('Inactive Group')).toBeInTheDocument()
  })

  it('должна правильно отображать статистику', () => {
    mockUseGroups.mockReturnValue({
      data: { items: mockGroups, total: mockGroups.length },
      isLoading: false,
      error: null,
    })
    renderWithProviders(<GroupsPage />)

    // Всего групп
    expect(screen.getByText(/Всего групп:/i).nextSibling?.textContent).toBe(
      mockGroups.length.toString()
    )
    // Активных
    expect(screen.getByText(/Активных:/i).nextSibling?.textContent).toBe(
      mockGroups.filter((g) => g.is_active).length.toString()
    )
    // Неактивных
    expect(screen.getByText(/Неактивных:/i).nextSibling?.textContent).toBe(
      mockGroups.filter((g) => !g.is_active).length.toString()
    )
    // Всего комментариев
    const totalComments = mockGroups.reduce(
      (sum, g) => sum + g.total_comments_found,
      0
    )
    const formattedTotalComments = new Intl.NumberFormat('ru-RU').format(
      totalComments
    )
    expect(
      screen.getByText(/Всего комментариев:/i).nextSibling?.textContent
    ).toBe(formattedTotalComments)
  })

  it('должна успешно добавлять новую группу', async () => {
    const createMutate = jest.fn()
    mockUseCreateGroup.mockReturnValue({
      mutate: createMutate,
      isPending: false,
    })

    renderWithProviders(<GroupsPage />)
    const urlInput = screen.getByPlaceholderText(
      /https:\/\/vk.com\/example или example/i
    )
    const addButton = screen.getByRole('button', { name: /Добавить/i })

    fireEvent.change(urlInput, { target: { value: 'new_group_url' } })
    fireEvent.click(addButton)

    await waitFor(() => {
      expect(createMutate).toHaveBeenCalledWith(
        expect.objectContaining({
          vk_id_or_screen_name: 'new_group_url',
        }),
        expect.any(Object)
      )
    })
  })

  it('должна удалять группу', async () => {
    mockUseGroups.mockReturnValue({
      data: { items: mockGroups, total: mockGroups.length },
      isLoading: false,
      error: null,
    })
    const deleteMutate = jest.fn()
    mockUseDeleteGroup.mockReturnValue({ mutate: deleteMutate })
    jest.spyOn(window, 'confirm').mockReturnValue(true)

    renderWithProviders(<GroupsPage />)

    const row = screen
      .getAllByRole('row')
      .find((tr) => within(tr).queryByText('Active Group')) as HTMLElement
    expect(row).toBeInTheDocument()
    const deleteButton = within(row).getByRole('button', { name: /удалить/i })

    fireEvent.click(deleteButton)

    expect(window.confirm).toHaveBeenCalled()
    expect(deleteMutate).toHaveBeenCalledWith(mockGroups[0].id)
  })

  it('должна переключать статус активности группы', async () => {
    mockUseGroups.mockReturnValue({
      data: { items: mockGroups, total: mockGroups.length },
      isLoading: false,
      error: null,
    })
    const updateMutate = jest.fn()
    mockUseUpdateGroup.mockReturnValue({ mutate: updateMutate })

    renderWithProviders(<GroupsPage />)

    const row = screen
      .getAllByRole('row')
      .find((tr) => within(tr).queryByText('Active Group')) as HTMLElement
    expect(row).toBeInTheDocument()
    const switchButton = within(row).getByRole('button', {
      name: /Приостановить/i,
    })

    fireEvent.click(switchButton)

    expect(updateMutate).toHaveBeenCalledWith({
      groupId: mockGroups[0].id,
      data: { is_active: !mockGroups[0].is_active },
    })
  })

  it('должна фильтровать группы по поисковому запросу', async () => {
    mockUseGroups.mockReturnValue({
      data: { items: mockGroups, total: mockGroups.length },
      isLoading: false,
      error: null,
    })
    renderWithProviders(<GroupsPage />)
    const searchInput = screen.getByPlaceholderText(
      /Поиск по названию или screen_name/i
    )

    expect(screen.getByText('Active Group')).toBeInTheDocument()
    expect(screen.getByText('Inactive Group')).toBeInTheDocument()

    fireEvent.change(searchInput, { target: { value: 'Active' } })

    await waitFor(() => {
      expect(screen.getByText('Active Group')).toBeInTheDocument()
      expect(screen.queryByText('Inactive Group')).not.toBeInTheDocument()
    })
  })

  it('должна фильтровать группы по статусу "только активные"', async () => {
    mockUseGroups.mockReturnValue({
      data: { items: mockGroups, total: mockGroups.length },
      isLoading: false,
      error: null,
    })
    renderWithProviders(<GroupsPage />)
    const activeOnlyCheckbox = screen.getByLabelText(/Только активные/i)

    expect(screen.getByText('Active Group')).toBeInTheDocument()
    expect(screen.getByText('Inactive Group')).toBeInTheDocument()

    fireEvent.click(activeOnlyCheckbox)

    await waitFor(() => {
      expect(screen.getByText('Active Group')).toBeInTheDocument()
      expect(screen.queryByText('Inactive Group')).not.toBeInTheDocument()
    })
  })
})

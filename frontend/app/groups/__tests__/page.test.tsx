import { render, screen } from '@testing-library/react'
import GroupsPage from '../page'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { Toaster } from 'react-hot-toast'

jest.mock('@/hooks/use-groups', () => ({
  useGroups: jest.fn(() => ({
    data: { items: [], total: 0 },
    isLoading: false,
    error: null,
  })),
  useCreateGroup: jest.fn(() => ({
    mutate: jest.fn(),
    isPending: false,
  })),
  useUpdateGroup: jest.fn(() => ({
    mutate: jest.fn(),
  })),
  useDeleteGroup: jest.fn(() => ({
    mutate: jest.fn(),
  })),
}))

const queryClient = new QueryClient()

const renderWithProviders = (ui: React.ReactElement) => {
  return render(
    <QueryClientProvider client={queryClient}>
      {ui}
      <Toaster />
    </QueryClientProvider>
  )
}

describe('GroupsPage', () => {
  it('должна рендериться без ошибок', () => {
    renderWithProviders(<GroupsPage />)
    expect(
      screen.getByRole('heading', { name: /VK Группы/i, level: 1 })
    ).toBeInTheDocument()
  })
})

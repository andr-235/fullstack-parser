import { render, screen } from '@testing-library/react'
import { usePathname } from 'next/navigation'

import { Navbar } from '../Navbar'

// Mock Next.js hooks
jest.mock('next/navigation', () => ({
  usePathname: jest.fn(),
}))

const mockUsePathname = usePathname as jest.MockedFunction<typeof usePathname>

describe('Navbar', () => {
  beforeEach(() => {
    mockUsePathname.mockReturnValue('/dashboard/comments')
  })

  it('отображает breadcrumbs для текущего пути', () => {
    render(<Navbar />)

    expect(screen.getByText('Панель управления')).toBeInTheDocument()
    expect(screen.getByText('Комментарии')).toBeInTheDocument()
  })

  it('отображает кнопку уведомлений с количеством', () => {
    render(<Navbar notificationCount={5} />)

    const notificationButton = screen.getByLabelText('Notifications')
    expect(notificationButton).toBeInTheDocument()
    expect(screen.getByText('5')).toBeInTheDocument()
  })

  it('отображает 99+ для больших чисел уведомлений', () => {
    render(<Navbar notificationCount={150} />)

    expect(screen.getByText('99+')).toBeInTheDocument()
  })

  it('не отображает badge для нулевого количества уведомлений', () => {
    render(<Navbar notificationCount={0} />)

    const notificationButton = screen.getByLabelText('Notifications')
    expect(notificationButton).toBeInTheDocument()
    expect(screen.queryByText('0')).not.toBeInTheDocument()
  })

  it('отображает поле поиска', () => {
    render(<Navbar />)

    const searchInput = screen.getByPlaceholderText('Поиск...')
    expect(searchInput).toBeInTheDocument()
  })

  it('отображает кнопки управления', () => {
    render(<Navbar />)

    expect(screen.getByLabelText('Toggle sidebar')).toBeInTheDocument()
    expect(screen.getByLabelText('Toggle theme')).toBeInTheDocument()
    expect(screen.getByLabelText('Notifications')).toBeInTheDocument()
  })

  it('переводит известные страницы', () => {
    mockUsePathname.mockReturnValue('/settings/groups')
    render(<Navbar />)

    expect(screen.getByText('Настройки')).toBeInTheDocument()
    expect(screen.getByText('Группы')).toBeInTheDocument()
  })

  it('использует оригинальное название для неизвестных страниц', () => {
    mockUsePathname.mockReturnValue('/unknown-page')
    render(<Navbar />)

    expect(screen.getByText('Unknown-page')).toBeInTheDocument()
  })
})

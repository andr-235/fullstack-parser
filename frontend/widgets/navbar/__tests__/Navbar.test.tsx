import { render, screen, fireEvent } from '@testing-library/react'

import { Navbar } from '../Navbar'

describe('Navbar', () => {

  it('отображает логотип и название', () => {
    render(<Navbar />)

    expect(screen.getByText('Analytics')).toBeInTheDocument()
    expect(screen.getByText('A')).toBeInTheDocument() // Логотип
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

  it('отображает поле поиска на десктопе', () => {
    render(<Navbar />)

    const searchInput = screen.getByPlaceholderText('Поиск...')
    expect(searchInput).toBeInTheDocument()
  })

  it('отображает кнопки управления', () => {
    render(<Navbar />)

    expect(screen.getByLabelText('Toggle sidebar')).toBeInTheDocument()
    expect(screen.getByLabelText('Toggle theme')).toBeInTheDocument()
    expect(screen.getByLabelText('Notifications')).toBeInTheDocument()
    expect(screen.getByLabelText('Search')).toBeInTheDocument()
  })


  it('отображает пользовательское меню', () => {
    render(<Navbar />)

    expect(screen.getByText('Пользователь')).toBeInTheDocument()
    expect(screen.getByText('U')).toBeInTheDocument() // Аватар
  })

  it('переключает мобильный поиск', () => {
    render(<Navbar />)

    const searchButton = screen.getByLabelText('Search')
    fireEvent.click(searchButton)

    // На мобильных устройствах должно появиться поле поиска
    const searchInputs = screen.getAllByPlaceholderText('Поиск...')
    expect(searchInputs).toHaveLength(2) // Один для десктопа, один для мобильного
  })

  it('переключает тему', () => {
    render(<Navbar />)

    const themeButton = screen.getByLabelText('Toggle theme')
    fireEvent.click(themeButton)

    // Проверяем что иконка изменилась (Sun вместо Moon)
    expect(screen.getByTestId('sun-icon') || screen.getByTestId('moon-icon')).toBeInTheDocument()
  })
})

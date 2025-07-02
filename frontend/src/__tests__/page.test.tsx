import { render, screen } from '@testing-library/react'
import Home from '../../app/page'

describe('Home', () => {
  it('renders homepage heading', () => {
    render(<Home />)

    const heading = screen.getByRole('heading', {
      name: /vk comments parser/i,
    })

    expect(heading).toBeInTheDocument()
  })

  it('renders description text', () => {
    render(<Home />)

    const description = screen.getByText(
      /парсинг и анализ комментариев вконтакте/i
    )

    expect(description).toBeInTheDocument()
  })

  it('renders feature cards', () => {
    render(<Home />)

    expect(screen.getByText(/поиск по ключевым словам/i)).toBeInTheDocument()
    expect(screen.getByText(/аналитика/i)).toBeInTheDocument()
    expect(screen.getByText(/высокая производительность/i)).toBeInTheDocument()
  })

  it('renders action buttons', () => {
    render(<Home />)

    expect(screen.getByText(/начать парсинг/i)).toBeInTheDocument()
    expect(screen.getByText(/посмотреть документацию/i)).toBeInTheDocument()
  })
})

import { render, screen } from '@testing-library/react'
import Home from '../app/page'

describe('Home', () => {
  it('renders homepage heading', () => {
    render(<Home />)

    const heading = screen.getByRole('heading', {
      name: /fullstack parser/i,
    })

    expect(heading).toBeInTheDocument()
  })

  it('renders description text', () => {
    render(<Home />)

    const description = screen.getByText(/современное fullstack приложение/i)

    expect(description).toBeInTheDocument()
  })
})

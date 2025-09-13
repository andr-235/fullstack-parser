import { render, screen, fireEvent } from "@testing-library/react";
import { NavUser } from "../ui/NavUser";

const mockUser = {
  id: "1",
  name: "Иван Иванов",
  email: "ivan@example.com",
  avatar: "/avatars/ivan.jpg",
  role: "admin" as const,
  status: "active" as const,
};

// Mock Next.js router
jest.mock("next/navigation", () => ({
  useRouter: () => ({
    push: jest.fn(),
  }),
}));

// Mock react-hot-toast
jest.mock("react-hot-toast", () => ({
  toast: {
    success: jest.fn(),
    error: jest.fn(),
    info: jest.fn(),
  },
}));

describe("NavUser", () => {
  it("рендерится без ошибок", () => {
    render(<NavUser user={mockUser} />);
    expect(screen.getByText("Иван Иванов")).toBeInTheDocument();
  });

  it("отображает email пользователя", () => {
    render(<NavUser user={mockUser} />);
    expect(screen.getByText("ivan@example.com")).toBeInTheDocument();
  });

  it("отображает инициалы в fallback аватара", () => {
    render(<NavUser user={mockUser} />);
    expect(screen.getByText("ИИ")).toBeInTheDocument();
  });

  it("открывает dropdown при клике", () => {
    render(<NavUser user={mockUser} />);
    const trigger = screen.getByRole("button");
    fireEvent.click(trigger);
    expect(screen.getByText("Обновить до Pro")).toBeInTheDocument();
  });

  it("отображает все пункты меню", () => {
    render(<NavUser user={mockUser} />);
    const trigger = screen.getByRole("button");
    fireEvent.click(trigger);
    
    expect(screen.getByText("Обновить до Pro")).toBeInTheDocument();
    expect(screen.getByText("Аккаунт")).toBeInTheDocument();
    expect(screen.getByText("Оплата")).toBeInTheDocument();
    expect(screen.getByText("Уведомления")).toBeInTheDocument();
    expect(screen.getByText("Выйти")).toBeInTheDocument();
  });
});
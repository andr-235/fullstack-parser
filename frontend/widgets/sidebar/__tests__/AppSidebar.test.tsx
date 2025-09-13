import { render, screen } from "@testing-library/react";
import { AppSidebar } from "../ui/AppSidebar";

// Mock the NavigationContext
jest.mock("@/shared/contexts/NavigationContext", () => ({
  useNavigation: () => ({
    stats: {
      comments: { new: 5, total: 100 },
      groups: { active: 3, total: 10 },
      keywords: { active: 15, total: 50 },
    },
    activePath: "/dashboard",
  }),
}));

// Mock Next.js components
jest.mock("next/link", () => {
  return function MockLink({ children, href }: { children: React.ReactNode; href: string }) {
    return <a href={href}>{children}</a>;
  };
});

describe("AppSidebar", () => {
  it("рендерится без ошибок", () => {
    render(<AppSidebar />);
    expect(screen.getByRole("complementary")).toBeInTheDocument();
  });

  it("отображает заголовок с TeamSwitcher", () => {
    render(<AppSidebar />);
    expect(screen.getByText("Парсер комментариев VK")).toBeInTheDocument();
  });

  it("отображает навигационные элементы", () => {
    render(<AppSidebar />);
    expect(screen.getByText("Панель управления")).toBeInTheDocument();
    expect(screen.getByText("Комментарии")).toBeInTheDocument();
    expect(screen.getByText("Группы")).toBeInTheDocument();
    expect(screen.getByText("Ключевые слова")).toBeInTheDocument();
  });

  it("отображает проекты", () => {
    render(<AppSidebar />);
    expect(screen.getByText("Мониторинг")).toBeInTheDocument();
    expect(screen.getByText("Парсер")).toBeInTheDocument();
    expect(screen.getByText("Настройки")).toBeInTheDocument();
  });

  it("отображает пользователя в футере", () => {
    render(<AppSidebar />);
    expect(screen.getByText("Администратор")).toBeInTheDocument();
    expect(screen.getByText("admin@vkparser.com")).toBeInTheDocument();
  });
});
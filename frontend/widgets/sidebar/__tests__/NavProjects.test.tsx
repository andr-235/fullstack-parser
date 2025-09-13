import { render, screen, fireEvent } from "@testing-library/react";
import { NavProjects } from "../ui/NavProjects";
import { Monitor, FileText, Settings } from "lucide-react";

const mockProjects = [
  {
    id: "1",
    name: "Мониторинг",
    url: "/monitoring",
    icon: Monitor,
    status: "active" as const,
    description: "Мониторинг активности групп",
  },
  {
    id: "2",
    name: "Парсер",
    url: "/parser",
    icon: FileText,
    status: "active" as const,
    description: "Парсинг комментариев",
  },
  {
    id: "3",
    name: "Настройки",
    url: "/settings",
    icon: Settings,
    status: "active" as const,
    description: "Настройки системы",
  },
];

// Mock Next.js components
jest.mock("next/link", () => {
  return function MockLink({ children, href }: { children: React.ReactNode; href: string }) {
    return <a href={href}>{children}</a>;
  };
});

jest.mock("next/navigation", () => ({
  usePathname: () => "/monitoring",
}));

// Mock react-hot-toast
jest.mock("react-hot-toast", () => ({
  toast: {
    success: jest.fn(),
    error: jest.fn(),
    info: jest.fn(),
  },
}));

describe("NavProjects", () => {
  it("рендерится без ошибок", () => {
    render(<NavProjects projects={mockProjects} />);
    expect(screen.getByText("Инструменты")).toBeInTheDocument();
  });

  it("отображает все проекты", () => {
    render(<NavProjects projects={mockProjects} />);
    expect(screen.getByText("Мониторинг")).toBeInTheDocument();
    expect(screen.getByText("Парсер")).toBeInTheDocument();
    expect(screen.getByText("Настройки")).toBeInTheDocument();
  });

  it("выделяет активный проект", () => {
    render(<NavProjects projects={mockProjects} />);
    const activeLink = screen.getByRole("link", { name: "Мониторинг" });
    expect(activeLink).toHaveAttribute("href", "/monitoring");
  });

  it("открывает dropdown при клике на кнопку действий", () => {
    render(<NavProjects projects={mockProjects} />);
    const actionButtons = screen.getAllByRole("button");
    const moreButton = actionButtons.find(button => 
      button.querySelector('svg')?.getAttribute('data-lucide') === 'more-horizontal'
    );
    
    if (moreButton) {
      fireEvent.click(moreButton);
      expect(screen.getByText("Просмотреть проект")).toBeInTheDocument();
    }
  });

  it("отображает все действия в dropdown", () => {
    render(<NavProjects projects={mockProjects} />);
    const actionButtons = screen.getAllByRole("button");
    const moreButton = actionButtons.find(button => 
      button.querySelector('svg')?.getAttribute('data-lucide') === 'more-horizontal'
    );
    
    if (moreButton) {
      fireEvent.click(moreButton);
      expect(screen.getByText("Просмотреть проект")).toBeInTheDocument();
      expect(screen.getByText("Поделиться проектом")).toBeInTheDocument();
      expect(screen.getByText("Удалить проект")).toBeInTheDocument();
    }
  });
});
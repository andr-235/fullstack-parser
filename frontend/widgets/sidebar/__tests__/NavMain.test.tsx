import { render, screen } from "@testing-library/react";
import { NavMain } from "../ui/NavMain";
import { LayoutDashboard, MessageSquare, Users, Hash } from "lucide-react";

const mockNavItems = [
  {
    id: "dashboard",
    title: "Панель управления",
    url: "/dashboard",
    icon: LayoutDashboard,
    isActive: true,
  },
  {
    id: "comments",
    title: "Комментарии",
    url: "/comments",
    icon: MessageSquare,
    isActive: false,
    badge: <span data-testid="comments-badge">5</span>,
  },
  {
    id: "groups",
    title: "Группы",
    url: "/groups",
    icon: Users,
    isActive: false,
    badge: <span data-testid="groups-badge">3</span>,
  },
  {
    id: "keywords",
    title: "Ключевые слова",
    url: "/keywords",
    icon: Hash,
    isActive: false,
    badge: <span data-testid="keywords-badge">15</span>,
  },
];

// Mock Next.js components
jest.mock("next/link", () => {
  return function MockLink({ children, href }: { children: React.ReactNode; href: string }) {
    return <a href={href}>{children}</a>;
  };
});

jest.mock("next/navigation", () => ({
  usePathname: () => "/dashboard",
}));

describe("NavMain", () => {
  it("рендерится без ошибок", () => {
    render(<NavMain items={mockNavItems} />);
    expect(screen.getByText("Платформа")).toBeInTheDocument();
  });

  it("отображает все навигационные элементы", () => {
    render(<NavMain items={mockNavItems} />);
    expect(screen.getByText("Панель управления")).toBeInTheDocument();
    expect(screen.getByText("Комментарии")).toBeInTheDocument();
    expect(screen.getByText("Группы")).toBeInTheDocument();
    expect(screen.getByText("Ключевые слова")).toBeInTheDocument();
  });

  it("отображает бейджи для элементов с ними", () => {
    render(<NavMain items={mockNavItems} />);
    expect(screen.getByTestId("comments-badge")).toBeInTheDocument();
    expect(screen.getByTestId("groups-badge")).toBeInTheDocument();
    expect(screen.getByTestId("keywords-badge")).toBeInTheDocument();
  });

  it("создает правильные ссылки", () => {
    render(<NavMain items={mockNavItems} />);
    expect(screen.getByRole("link", { name: "Панель управления" })).toHaveAttribute("href", "/dashboard");
    expect(screen.getByRole("link", { name: "Комментарии" })).toHaveAttribute("href", "/comments");
    expect(screen.getByRole("link", { name: "Группы" })).toHaveAttribute("href", "/groups");
    expect(screen.getByRole("link", { name: "Ключевые слова" })).toHaveAttribute("href", "/keywords");
  });
});
import { render, screen, within } from "@testing-library/react";
import DashboardPage from "@/app/dashboard/page";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { useGlobalStats } from "@/hooks/use-stats";

jest.mock("@/hooks/use-stats", () => ({
  useGlobalStats: jest.fn(),
}));

const queryClient = new QueryClient();

const renderWithProviders = (ui: React.ReactElement) => {
  return render(
    <QueryClientProvider client={queryClient}>{ui}</QueryClientProvider>,
  );
};

// Универсальный мок статистики для всех тестов
const mockStats = {
  groups: 0,
  comments: 0,
  keywords: 0,
  activity: [],
  total_groups: 10,
  total_comments: 1000,
  total_keywords: 100,
};

describe("DashboardPage", () => {
  beforeEach(() => {
    // Сбрасываем моки перед каждым тестом
    (useGlobalStats as jest.Mock).mockClear();
  });

  it("должна отображать спиннер загрузки", () => {
    (useGlobalStats as jest.Mock).mockReturnValue({
      data: undefined,
      isLoading: true,
      error: null,
    });
    renderWithProviders(<DashboardPage />);
    // Ищем по классу, если нет role="status"
    expect(document.querySelector(".animate-spin")).toBeInTheDocument();
  });

  it("должна отображать сообщение об ошибке", () => {
    const errorMessage = "Network Error";
    (useGlobalStats as jest.Mock).mockReturnValue({
      data: undefined,
      isLoading: false,
      error: new Error(errorMessage),
    });
    renderWithProviders(<DashboardPage />);
    expect(screen.getByText("Ошибка")).toBeInTheDocument();
    expect(
      screen.getByText(
        "Не удалось загрузить статистику. Попробуйте обновить страницу.",
      ),
    ).toBeInTheDocument();
    expect(screen.getByText(errorMessage)).toBeInTheDocument();
  });

  it("должна рендериться без ошибок и отображать заголовки", () => {
    (useGlobalStats as jest.Mock).mockReturnValue({
      data: {},
      isLoading: false,
      error: null,
    });
    renderWithProviders(<DashboardPage />);
    expect(
      screen.getByRole("heading", { name: /Группы/i }),
    ).toBeInTheDocument();
    expect(
      screen.getByRole("heading", { name: /Комментарии/i }),
    ).toBeInTheDocument();
    expect(
      screen.getByRole("heading", { name: /Ключевые слова/i }),
    ).toBeInTheDocument();
    expect(
      screen.getByRole("heading", { name: /Активность комментариев/i }),
    ).toBeInTheDocument();
  });

  it("должна правильно отображать статистику", () => {
    (useGlobalStats as jest.Mock).mockReturnValue({
      data: mockStats,
      isLoading: false,
      error: null,
    });

    renderWithProviders(<DashboardPage />);

    const groupsCard = screen.getByRole("heading", { name: /Группы/i })
      .parentElement?.parentElement;
    const commentsCard = screen.getByRole("heading", { name: /Комментарии/i })
      .parentElement?.parentElement;
    const keywordsCard = screen.getByRole("heading", {
      name: /Ключевые слова/i,
    }).parentElement?.parentElement;

    expect(
      within(groupsCard as HTMLElement).getByText("10"),
    ).toBeInTheDocument();
    expect(
      within(commentsCard as HTMLElement).getByText("1000"),
    ).toBeInTheDocument();
    expect(
      within(keywordsCard as HTMLElement).getByText("100"),
    ).toBeInTheDocument();
  });

  it("должна отображать заглушку для графика", () => {
    (useGlobalStats as jest.Mock).mockReturnValue({
      data: mockStats,
      isLoading: false,
      error: null,
    });
    renderWithProviders(<DashboardPage />);
    expect(screen.getByText("График скоро появится здесь")).toBeInTheDocument();
  });
});

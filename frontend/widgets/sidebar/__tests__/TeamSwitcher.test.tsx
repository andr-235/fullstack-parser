import { render, screen, fireEvent } from "@testing-library/react";
import { TeamSwitcher } from "../ui/TeamSwitcher";
import { GalleryVerticalEnd } from "lucide-react";

const mockTeams = [
  {
    id: "1",
    name: "Парсер комментариев VK",
    logo: GalleryVerticalEnd,
    plan: "Корпоративная",
    status: "active" as const,
  },
  {
    id: "2",
    name: "Другая команда",
    logo: GalleryVerticalEnd,
    plan: "Базовый",
    status: "active" as const,
  },
];

describe("TeamSwitcher", () => {
  it("рендерится без ошибок", () => {
    render(<TeamSwitcher teams={mockTeams} />);
    expect(screen.getByText("Парсер комментариев VK")).toBeInTheDocument();
  });

  it("отображает активную команду", () => {
    render(<TeamSwitcher teams={mockTeams} />);
    expect(screen.getByText("Корпоративная")).toBeInTheDocument();
  });

  it("открывает dropdown при клике", () => {
    render(<TeamSwitcher teams={mockTeams} />);
    const trigger = screen.getByRole("button");
    fireEvent.click(trigger);
    expect(screen.getByText("Команды")).toBeInTheDocument();
  });

  it("отображает все команды в dropdown", () => {
    render(<TeamSwitcher teams={mockTeams} />);
    const trigger = screen.getByRole("button");
    fireEvent.click(trigger);
    expect(screen.getByText("Парсер комментариев VK")).toBeInTheDocument();
    expect(screen.getByText("Другая команда")).toBeInTheDocument();
  });

  it("отображает кнопку добавления команды", () => {
    render(<TeamSwitcher teams={mockTeams} />);
    const trigger = screen.getByRole("button");
    fireEvent.click(trigger);
    expect(screen.getByText("Добавить команду")).toBeInTheDocument();
  });
});
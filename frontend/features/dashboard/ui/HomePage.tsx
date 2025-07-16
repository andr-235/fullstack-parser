"use client";

import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { BarChart, Search, Zap, Code } from "lucide-react";
import Link from "next/link";

const features = [
  {
    icon: <Search className="h-8 w-8 text-primary" />,
    title: "Поиск по ключевым словам",
    description:
      "Настраиваемый поиск комментариев по заданным ключевым словам.",
    href: "/keywords",
  },
  {
    icon: <BarChart className="h-8 w-8 text-primary" />,
    title: "Аналитика",
    description: "Подробная статистика и визуализация найденных данных.",
    href: "/dashboard",
  },
  {
    icon: <Zap className="h-8 w-8 text-primary" />,
    title: "Высокая производительность",
    description: "Асинхронная обработка и кэширование для быстрого анализа.",
    href: "/parser",
  },
];

export default function HomePage() {
  return (
    <div className="flex flex-col items-center justify-center min-h-full p-2 text-center">
      <div className="max-w-4xl w-full">
        <header className="mb-6">
          <h1 className="text-4xl font-bold tracking-tight">
            VK Comments Parser
          </h1>
          <p className="mt-2 text-base text-muted-foreground">
            Парсинг и анализ комментариев ВКонтакте на новом уровне.
          </p>
        </header>

        <main className="grid gap-2 md:grid-cols-3">
          {features.map((feature) => (
            <Card key={feature.title} className="text-left">
              <CardHeader>
                {feature.icon}
                <CardTitle className="mt-2 text-base font-bold">
                  {feature.title}
                </CardTitle>
              </CardHeader>
              <CardContent>
                <CardDescription className="text-xs">
                  {feature.description}
                </CardDescription>
              </CardContent>
            </Card>
          ))}
        </main>

        <footer className="mt-6">
          <div className="flex justify-center gap-2">
            <Button asChild>
              <Link href="/parser">
                <Zap className="mr-2 h-4 w-4" /> Начать парсинг
              </Link>
            </Button>
            <Button variant="outline" asChild>
              <Link href="/docs">
                <Code className="mr-2 h-4 w-4" /> Посмотреть документацию
              </Link>
            </Button>
          </div>
        </footer>
      </div>
    </div>
  );
}

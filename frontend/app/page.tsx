'use client'

import Link from 'next/link'
import { Search, BarChart, Zap, FileText } from 'lucide-react'

const features = [
  {
    icon: Search,
    title: 'Поиск по ключевым словам',
    description:
      'Настраиваемый поиск комментариев по заданным ключевым словам.',
  },
  {
    icon: BarChart,
    title: 'Аналитика',
    description: 'Подробная статистика и визуализация найденных данных.',
  },
  {
    icon: Zap,
    title: 'Высокая производительность',
    description: 'Асинхронная обработка и кэширование для быстрого анализа.',
  },
]

export default function HomePage() {
  return (
    <div className="hero min-h-full bg-base-100">
      <div className="hero-content text-center">
        <div className="max-w-2xl">
          <div className="flex justify-center items-center gap-4 mb-4">
            <h1 className="text-5xl font-bold">VK Comments Parser</h1>
          </div>
          <p className="py-6 text-lg">
            Парсинг и анализ комментариев ВКонтакте
          </p>

          <div className="grid sm:grid-cols-1 md:grid-cols-3 gap-6 mb-8">
            {features.map((feature, index) => {
              const Icon = feature.icon
              return (
                <div key={index} className="card bg-base-200 shadow-md">
                  <div className="card-body items-center text-center">
                    <Icon className="w-10 h-10 mb-4 text-primary" />
                    <h2 className="card-title">{feature.title}</h2>
                    <p>{feature.description}</p>
                  </div>
                </div>
              )
            })}
          </div>

          <div className="flex justify-center gap-4">
            <Link href="/parser" className="btn btn-primary">
              Начать парсинг
            </Link>
            <Link href="/docs" className="btn btn-ghost">
              <FileText className="w-4 h-4 mr-2" />
              Посмотреть документацию
            </Link>
          </div>
        </div>
      </div>
    </div>
  )
}

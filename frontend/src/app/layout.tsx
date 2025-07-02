import type { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'Fullstack Parser',
  description: 'Современное fullstack приложение для парсинга данных ВКонтакте',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="ru">
      <body>{children}</body>
    </html>
  )
} 
import type { Metadata } from 'next'
import { Inter, JetBrains_Mono } from 'next/font/google'
import './globals.css'

import { ReactQueryProvider } from '@/providers/react-query-provider'
import { Sidebar } from '@/components/layout/sidebar'
import { Header } from '@/components/layout/header'

const inter = Inter({
  variable: '--font-inter',
  subsets: ['latin'],
})

const jetbrainsMono = JetBrains_Mono({
  variable: '--font-jetbrains-mono',
  subsets: ['latin'],
})

export const metadata: Metadata = {
  title: 'VK Comments Parser',
  description: 'Fullstack приложение для парсинга комментариев ВКонтакте',
}

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode
}>) {
  return (
    <html lang="ru" data-theme="light">
      <body
        className={`${inter.variable} ${jetbrainsMono.variable} antialiased`}
      >
        <ReactQueryProvider>
          <div className="drawer lg:drawer-open">
            <input id="my-drawer-2" type="checkbox" className="drawer-toggle" />
            <div className="drawer-content flex flex-col">
              <Header />
              <main className="flex-1 overflow-auto p-6 bg-base-200">
                {children}
              </main>
            </div>
            <div className="drawer-side">
              <label
                htmlFor="my-drawer-2"
                aria-label="close sidebar"
                className="drawer-overlay"
              ></label>
              <Sidebar />
            </div>
          </div>
        </ReactQueryProvider>
      </body>
    </html>
  )
}

import type { Metadata } from 'next'
import localFont from 'next/font/local'
import './globals.css'

import { ReactQueryProvider } from '@/providers/react-query-provider'
import { Toaster } from 'react-hot-toast'
import { Sidebar } from '@/components/layout/sidebar'
import { Header } from '@/components/layout/header'

const inter = localFont({
  src: './fonts/Inter-VariableFont_opsz,wght.ttf',
  display: 'swap',
  variable: '--font-inter',
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
    <html lang="ru" className="dark">
      <body
        className={`${inter.variable} bg-slate-900 font-sans text-slate-50`}
      >
        <ReactQueryProvider>
          <div className="flex min-h-screen">
            <Sidebar />
            <div className="flex-1 flex flex-col">
              <Header />
              <main className="flex-1 overflow-auto p-6">{children}</main>
              <Toaster
                position="bottom-center"
                toastOptions={{ duration: 4000 }}
              />
            </div>
          </div>
        </ReactQueryProvider>
      </body>
    </html>
  )
}

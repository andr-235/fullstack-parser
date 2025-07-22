import type { Metadata, Viewport } from 'next'
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
  title: 'ВК Парсер',
  description: 'Fullstack приложение для парсинга комментариев ВКонтакте',
  icons: {
    icon: [
      { url: '/favicon.svg', sizes: 'any', type: 'image/svg+xml' },
      { url: '/favicon-16x16.png', sizes: '16x16', type: 'image/png' },
      { url: '/favicon-32x32.png', sizes: '32x32', type: 'image/png' },
    ],
    shortcut: '/favicon.ico',
    apple: '/apple-touch-icon.png',
  },
  manifest: '/site.webmanifest',
  robots: 'index, follow',
}

export const viewport: Viewport = {
  width: 'device-width',
  initialScale: 1,
  themeColor: '#0f172a', // slate-900
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

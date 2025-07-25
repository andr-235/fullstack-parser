import { Inter } from 'next/font/google'

import type { Metadata } from 'next'

import './globals.css'
import { APP_CONFIG } from '@/shared/config'
import { ErrorBoundary } from '@/shared/ui/ErrorBoundary'
import { DebugPanel } from '@/shared/ui/debug/DebugPanel'
import { ThemeProvider } from '@/shared/ui/theme-provider'

import { QueryProvider } from '@/providers/QueryProvider'
import { Sidebar, Header } from '@/widgets/layout'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: APP_CONFIG.name,
  description: APP_CONFIG.description,
  metadataBase: new URL(
    process.env.NEXT_PUBLIC_APP_URL || 'https://parser.mysite.ru'
  ),
  icons: {
    icon: [
      { url: '/favicon-16x16.png', sizes: '16x16', type: 'image/png' },
      { url: '/favicon-32x32.png', sizes: '32x32', type: 'image/png' },
    ],
    apple: [
      { url: '/apple-touch-icon.png', sizes: '180x180', type: 'image/png' },
    ],
    other: [
      { url: '/favicon.svg', type: 'image/svg+xml' },
    ],
  },
  manifest: '/site.webmanifest',
  openGraph: {
    title: APP_CONFIG.name,
    description: APP_CONFIG.description,
    type: 'website',
  },
  twitter: {
    card: 'summary_large_image',
    title: APP_CONFIG.name,
    description: APP_CONFIG.description,
  },
  robots: {
    index: true,
    follow: true,
  },
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="ru" suppressHydrationWarning>
      <body className={inter.className}>
        <div id="__next">
          <ErrorBoundary>
            <ThemeProvider
              attribute="class"
              defaultTheme="dark"
              enableSystem
              disableTransitionOnChange
            >
              <QueryProvider>
                <div className="flex h-screen">
                  <Sidebar />
                  <div className="flex-1 flex flex-col">
                    <Header />
                    <main className="flex-1 overflow-auto">{children}</main>
                  </div>
                </div>
                <DebugPanel />
              </QueryProvider>
            </ThemeProvider>
          </ErrorBoundary>
        </div>
      </body>
    </html>
  )
}

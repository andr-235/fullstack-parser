import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'
import { QueryProvider } from '@/providers/QueryProvider'
import { ErrorBoundary } from '@/shared/ui/ErrorBoundary'
import { APP_CONFIG } from '@/shared/config'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: APP_CONFIG.name,
  description: APP_CONFIG.description,
  metadataBase: new URL(process.env.NEXT_PUBLIC_APP_URL || 'http://localhost:3000'),
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
        <ErrorBoundary>
          <QueryProvider>
            {children}
          </QueryProvider>
        </ErrorBoundary>
      </body>
    </html>
  )
}

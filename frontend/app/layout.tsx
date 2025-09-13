import { Inter } from 'next/font/google';
import type { Metadata } from 'next';



import './globals.css';

import { APP_CONFIG } from '@/shared/config';
import { AppProviders } from '@/shared/providers/AppProviders';

import { AppLayout } from '@/widgets/layout/AppLayout';

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: APP_CONFIG.name,
  description: APP_CONFIG.description,
  viewport: 'width=device-width, initial-scale=1',
  icons: {
    icon: '/favicon.ico',
    apple: '/apple-touch-icon.png',
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
  robots: 'index,follow',
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="ru" suppressHydrationWarning>
      <body className={inter.className}>
        <AppProviders>
          <AppLayout>{children}</AppLayout>
        </AppProviders>
      </body>
    </html>
  )
}

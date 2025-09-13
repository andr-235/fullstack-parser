'use client'

import { Inter } from 'next/font/google'
import Head from 'next/head'

import './globals.css'

import { APP_CONFIG } from '@/shared/config'
import { AppProviders } from '@/shared/providers/AppProviders'
import { AppLayout } from '@/widgets/layout/AppLayout'

const inter = Inter({ subsets: ['latin'] })

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="ru" suppressHydrationWarning>
      <Head>
        <title>{APP_CONFIG.name}</title>
        <meta name="description" content={APP_CONFIG.description} />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <link rel="icon" href="/favicon.ico" />
        <link rel="apple-touch-icon" href="/apple-touch-icon.png" />
        <link rel="manifest" href="/site.webmanifest" />
        <meta property="og:title" content={APP_CONFIG.name} />
        <meta property="og:description" content={APP_CONFIG.description} />
        <meta property="og:type" content="website" />
        <meta name="twitter:card" content="summary_large_image" />
        <meta name="twitter:title" content={APP_CONFIG.name} />
        <meta name="twitter:description" content={APP_CONFIG.description} />
        <meta name="robots" content="index,follow" />
      </Head>
      <body className={inter.className}>
        <AppProviders>
          <AppLayout>{children}</AppLayout>
        </AppProviders>
      </body>
    </html>
  )
}

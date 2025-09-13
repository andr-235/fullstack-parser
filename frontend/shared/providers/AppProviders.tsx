'use client'

import { useState, type ReactNode, type ComponentType } from 'react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { ThemeProvider } from '@/shared/ui/theme-provider'
import { NavigationProvider } from '@/shared/contexts/NavigationContext'
import { AuthProvider } from './AuthProvider'
import { ToastProvider } from './ToastProvider'

// Type-only import for devtools component
type ReactQueryDevtoolsType = ComponentType<{ initialIsOpen?: boolean }>

// Conditionally import devtools only in development
let ReactQueryDevtools: ReactQueryDevtoolsType | null = null
if (process.env.NODE_ENV === 'development') {
  try {
    const devtoolsModule = require('@tanstack/react-query-devtools')
    ReactQueryDevtools = devtoolsModule.ReactQueryDevtools as ReactQueryDevtoolsType
  } catch {
    // Devtools not available, skip silently
  }
}

const CACHE_CONFIG = {
  staleTime: 5 * 60 * 1000, // 5 минут
  gcTime: 10 * 60 * 1000, // 10 минут
}

interface AppProvidersProps {
  children: ReactNode
}

export function AppProviders({ children }: AppProvidersProps) {
  const [queryClient] = useState(
    () =>
      new QueryClient({
        defaultOptions: {
          queries: {
            staleTime: CACHE_CONFIG.staleTime,
            gcTime: CACHE_CONFIG.gcTime,
            retry: 3,
            retryDelay: attemptIndex => Math.min(1000 * 2 ** attemptIndex, 30000),
            refetchOnWindowFocus: false,
            refetchOnReconnect: true,
            refetchOnMount: true,
          },
          mutations: {
            retry: 1,
            retryDelay: 1000,
          },
        },
      })
  )

  return (
    <ThemeProvider attribute="class" defaultTheme="dark" enableSystem disableTransitionOnChange>
      <QueryClientProvider client={queryClient}>
        <AuthProvider>
          <NavigationProvider>{children}</NavigationProvider>
          <ToastProvider />
        </AuthProvider>
        {ReactQueryDevtools && <ReactQueryDevtools initialIsOpen={false} />}
      </QueryClientProvider>
    </ThemeProvider>
  )
}

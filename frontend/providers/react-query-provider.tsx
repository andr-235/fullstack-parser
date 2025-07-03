'use client'

import { useState } from 'react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'

interface ReactQueryProviderProps {
  children: React.ReactNode
}

export function ReactQueryProvider({ children }: ReactQueryProviderProps) {
  const [queryClient] = useState(
    () =>
      new QueryClient({
        defaultOptions: {
          queries: {
            staleTime: 5 * 60 * 1000, // 5 минут
            gcTime: 10 * 60 * 1000,   // 10 минут (было cacheTime)
            refetchOnWindowFocus: false,
            retry: 2,
          },
        },
      })
  )

  return (
    <QueryClientProvider client={queryClient}>
      {children}
      {process.env.NODE_ENV === 'development' && (
        <DevTools />
      )}
    </QueryClientProvider>
  )
}

// Динамическая загрузка DevTools для избежания проблем с chunks
function DevTools() {
  const { ReactQueryDevtools } = require('@tanstack/react-query-devtools')
  return <ReactQueryDevtools initialIsOpen={false} />
} 
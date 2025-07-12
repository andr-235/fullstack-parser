'use client'

import { useState } from 'react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import dynamic from 'next/dynamic'

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
            gcTime: 10 * 60 * 1000, // 10 минут (было cacheTime)
            refetchOnWindowFocus: false,
            retry: 2,
          },
        },
      })
  )

  return (
    <QueryClientProvider client={queryClient}>
      {children}
      {process.env.NODE_ENV === 'development' && <DevtoolsLazy />}
    </QueryClientProvider>
  )
}

// Динамическая загрузка DevTools только на клиенте, чтобы избежать ошибок
const DevtoolsLazy = dynamic(
  () =>
    import('@tanstack/react-query-devtools').then((m) => {
      return {
        default: m.ReactQueryDevtools,
      }
    }),
  {
    ssr: false,
    loading: () => null,
  }
)

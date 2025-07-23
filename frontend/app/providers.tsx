'use client'

import { ReactQueryProvider } from '@/providers/react-query-provider'
import { Toaster } from 'react-hot-toast'

interface ProvidersProps {
 children: React.ReactNode
}

export function Providers({ children }: ProvidersProps) {
 return (
  <ReactQueryProvider>
   {children}
   <Toaster
    position="bottom-center"
    toastOptions={{ duration: 4000 }}
   />
  </ReactQueryProvider>
 )
} 
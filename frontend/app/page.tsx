'use client'

import { useEffect } from 'react'


import { useRouter } from 'next/navigation'



import { useAuth } from '@/features/auth/hooks'

export default function MainRoute() {
  const router = useRouter()
  const { isAuthenticated, isLoading } = useAuth()

  useEffect(() => {
    if (!isLoading) {
      if (isAuthenticated) {
        router.replace('/dashboard')
      } else {
        router.replace('/login')
      }
    }
  }, [isAuthenticated, isLoading, router])

  return null
}

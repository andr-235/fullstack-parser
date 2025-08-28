'use client'

import { useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { Button } from '@/shared/ui'
import { Home, ArrowLeft } from 'lucide-react'

export default function NotFound() {
 const router = useRouter()

 useEffect(() => {
  // Redirect to dashboard after a short delay
  const timer = setTimeout(() => {
   router.push('/dashboard')
  }, 3000)

  return () => clearTimeout(timer)
 }, [router])

 return (
  <div className="flex flex-col items-center justify-center min-h-screen bg-background text-foreground">
   <div className="text-center space-y-6">
    <div className="space-y-2">
     <h1 className="text-6xl font-bold text-muted-foreground">404</h1>
     <h2 className="text-2xl font-semibold">Страница не найдена</h2>
     <p className="text-muted-foreground max-w-md">
      К сожалению, запрашиваемая страница не существует или была перемещена.
     </p>
    </div>

    <div className="flex gap-4 justify-center">
     <Button
      onClick={() => router.back()}
      variant="outline"
      className="flex items-center gap-2"
     >
      <ArrowLeft className="h-4 w-4" />
      Назад
     </Button>
     <Button
      onClick={() => router.push('/dashboard')}
      className="flex items-center gap-2"
     >
      <Home className="h-4 w-4" />
      На главную
     </Button>
    </div>

    <p className="text-sm text-muted-foreground">
     Вы будете автоматически перенаправлены на главную страницу через 3 секунды...
    </p>
   </div>
  </div>
 )
}

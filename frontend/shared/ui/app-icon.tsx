import Image from 'next/image'
import { cn } from '@/lib/utils'
import type { AppIconProps } from '@/shared/types'

const sizeMap = {
 sm: 16,
 md: 32,
 lg: 192,
 xl: 512,
}

const srcMap = {
 16: '/logo-bright.svg', // Используем яркую SVG версию
 32: '/logo-bright.svg',
 192: '/android-chrome-192x192.png',
 512: '/android-chrome-512x512.png',
}

export function AppIcon({ size = 'md', className, priority = false }: AppIconProps) {
 const pixelSize = sizeMap[size]
 const src = srcMap[pixelSize as keyof typeof srcMap]

 return (
  <Image
   src={src}
   alt="ВК Парсер"
   width={pixelSize}
   height={pixelSize}
   className={cn('object-contain', className)}
   priority={priority}
  />
 )
} 
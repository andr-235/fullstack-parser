import { useMemo } from 'react'

interface IconInfo {
  src: string
  sizes: string
  type: string
}

export function useAppIcon() {
  const icons = useMemo<IconInfo[]>(
    () => [
      {
        src: '/favicon-16x16.png',
        sizes: '16x16',
        type: 'image/png',
      },
      {
        src: '/favicon-32x32.png',
        sizes: '32x32',
        type: 'image/png',
      },
      {
        src: '/android-chrome-192x192.png',
        sizes: '192x192',
        type: 'image/png',
      },
      {
        src: '/android-chrome-512x512.png',
        sizes: '512x512',
        type: 'image/png',
      },
      {
        src: '/apple-touch-icon.png',
        sizes: '180x180',
        type: 'image/png',
      },
    ],
    []
  )

  const getIconBySize = (size: number): IconInfo | undefined => {
    return icons.find((icon) => {
      const [width] = icon.sizes.split('x').map(Number)
      return width === size
    })
  }

  const getIconBySizes = (sizes: string): IconInfo | undefined => {
    return icons.find((icon) => icon.sizes === sizes)
  }

  return {
    icons,
    getIconBySize,
    getIconBySizes,
  }
}

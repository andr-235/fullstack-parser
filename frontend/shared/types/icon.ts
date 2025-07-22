export interface AppIconInfo {
  src: string
  sizes: string
  type: string
}

export type AppIconSize = 'sm' | 'md' | 'lg' | 'xl'

export interface AppIconProps {
  size?: AppIconSize
  className?: string
  priority?: boolean
}

export interface AppManifest {
  name: string
  short_name: string
  description: string
  icons: AppIconInfo[]
  theme_color: string
  background_color: string
  display: string
  start_url: string
  scope: string
}

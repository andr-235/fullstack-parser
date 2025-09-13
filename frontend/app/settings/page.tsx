import { SettingsPage } from '@/features/settings'

export default function SettingsRoute() {
  return <SettingsPage />
}

// Force cache invalidation
export const dynamic = 'force-dynamic'
export const revalidate = 0

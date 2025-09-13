import { SettingsPage } from '@/features/settings'
import { useRouteAccess } from "@/shared/hooks/useRouteAccess";

export default function SettingsRoute() {
  return <SettingsPage />
}

// Force cache invalidation
export const dynamic = 'force-dynamic'
export const revalidate = 0

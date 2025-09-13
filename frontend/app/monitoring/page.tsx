import { MonitoringPage } from '@/features/monitoring'
import { useRouteAccess } from "@/shared/hooks/useRouteAccess";

export default function MonitoringPageComponent() {
  return <MonitoringPage />
}

// Force cache invalidation
export const dynamic = 'force-dynamic'
export const revalidate = 0

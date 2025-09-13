import { MonitoringPage } from '@/features/monitoring'

export default function MonitoringPageComponent() {
  return <MonitoringPage />
}

// Force cache invalidation
export const dynamic = 'force-dynamic'
export const revalidate = 0

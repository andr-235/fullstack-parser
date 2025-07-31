import { MonitoringPage } from '@/widgets/monitoring-page'

export default function MonitoringPageComponent() {
  return <MonitoringPage />
}

// Force cache invalidation
export const dynamic = 'force-dynamic'
export const revalidate = 0

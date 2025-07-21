import MonitoringPage from '@/features/monitoring/ui/MonitoringPage'

export default function MonitoringRoute() {
  return <MonitoringPage />
}

// Force cache invalidation
export const dynamic = 'force-dynamic'
export const revalidate = 0

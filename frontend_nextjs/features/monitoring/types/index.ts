export interface MonitoringFilters {
  active_only?: boolean
  monitoring_enabled?: boolean
  search?: string
}

export interface MonitoringTableState {
  filters: MonitoringFilters
  sortBy: string
  sortOrder: 'asc' | 'desc'
  page: number
  pageSize: number
}

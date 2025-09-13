// UI компоненты
export { DashboardWidget, StatCard, QuickActionModal } from "./ui";

// Типы и хуки
export type { DashboardStats, StatCardConfig, QuickAction, DashboardMetrics } from "./model";
export { useDashboard } from "./model";

// API
export { getDashboardMetrics } from "./api";
// UI Components
export { AppSidebar } from "./ui/AppSidebar";
export { NavUser } from "./ui/NavUser";
export { NavMain } from "./ui/NavMain";

// Types
export type {
  User,
  NavSubItem,
  NavItem,
  SidebarStats,
  SidebarData,
} from "./model/types";

// Store
export { useSidebarStore } from "./model/sidebar-store";

// Hooks
export { useSidebarData } from "./model/useSidebarData";
export { useUserActions } from "./model/useUserActions";

// API
export { sidebarApi } from "./api/sidebar-api";
export {
  fetchSidebarStats,
  updateUserProfile,
} from "./api/sidebar-api";

// Utils
export {
  getInitials,
  isActiveRoute,
  getUserRoleColor,
  formatBadgeCount,
  getNavItemIcon,
  shouldShowBadge,
} from "./lib/sidebar-utils";

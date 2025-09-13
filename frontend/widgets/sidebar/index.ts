// UI Components
export { AppSidebar } from "./ui/AppSidebar";
export { TeamSwitcher } from "./ui/TeamSwitcher";
export { NavUser } from "./ui/NavUser";
export { NavProjects } from "./ui/NavProjects";
export { NavMain } from "./ui/NavMain";

// Types
export type {
  User,
  Team,
  Project,
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
export { useProjectActions } from "./model/useProjectActions";

// API
export { sidebarApi } from "./api/sidebar-api";
export {
  fetchSidebarStats,
  updateUserProfile,
  switchTeam,
  createProject,
  deleteProject,
} from "./api/sidebar-api";

// Utils
export {
  getInitials,
  isActiveRoute,
  getProjectStatusColor,
  getTeamStatusColor,
  getUserRoleColor,
  formatBadgeCount,
  getNavItemIcon,
  shouldShowBadge,
} from "./lib/sidebar-utils";

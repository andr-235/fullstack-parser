// import { apiClient } from "@/shared/lib/api";

// Mock API client for now
const apiClient = {
  get: async (url: string) => ({ data: {} }),
  post: async (url: string, data: any) => ({ data: {} }),
  patch: async (url: string, data: any) => ({ data: {} }),
  delete: async (url: string) => ({ data: {} }),
};
import { SidebarData, SidebarStats } from "../model/types";

export const fetchSidebarStats = async (): Promise<SidebarStats> => {
  const response = await apiClient.get("/stats/sidebar");
  return response.data;
};

export const updateUserProfile = async (data: {
  name?: string;
  email?: string;
  avatar?: string;
}): Promise<void> => {
  await apiClient.patch("/user/profile", data);
};

export const switchTeam = async (teamId: string): Promise<void> => {
  await apiClient.post("/user/switch-team", { teamId });
};

export const createProject = async (data: {
  name: string;
  description?: string;
}): Promise<void> => {
  await apiClient.post("/projects", data);
};

export const deleteProject = async (projectId: string): Promise<void> => {
  await apiClient.delete(`/projects/${projectId}`);
};

import type { Group, UpdateGroupRequest } from '../types';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

export const groupsApi = {
  async createGroup(data: Omit<Group, 'id' | 'created_at' | 'updated_at'>): Promise<Group> {
    const response = await fetch(`${API_BASE_URL}/groups/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    });

    if (!response.ok) {
      throw new Error(`Failed to create group: ${response.statusText}`);
    }

    return response.json();
  },

  async updateGroup(id: number, data: UpdateGroupRequest): Promise<Group> {
    const response = await fetch(`${API_BASE_URL}/groups/${id}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    });

    if (!response.ok) {
      throw new Error(`Failed to update group: ${response.statusText}`);
    }

    return response.json();
  },

  async deleteGroup(id: number): Promise<void> {
    const response = await fetch(`${API_BASE_URL}/groups/${id}`, {
      method: 'DELETE',
    });

    if (!response.ok) {
      throw new Error(`Failed to delete group: ${response.statusText}`);
    }
  },

  async toggleGroupStatus(id: number, isActive: boolean): Promise<Group> {
    const endpoint = isActive ? 'deactivate' : 'activate';
    const response = await fetch(`${API_BASE_URL}/groups/${id}/${endpoint}`, {
      method: 'POST',
    });

    if (!response.ok) {
      throw new Error(`Failed to toggle group status: ${response.statusText}`);
    }

    return response.json();
  },
};
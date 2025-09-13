/**
 * API для проверки состояния системы
 */

import { httpClient } from '@/shared/lib/http-client'

export const healthApi = {
  async healthCheck(): Promise<{ success: boolean; message: string }> {
    return httpClient.get('/api/v1/health')
  },

  async detailedHealthCheck(): Promise<Record<string, unknown>> {
    return httpClient.get('/api/v1/health/detailed')
  },

  async readinessCheck(): Promise<Record<string, unknown>> {
    return httpClient.get('/api/v1/health/ready')
  },

  async livenessCheck(): Promise<Record<string, unknown>> {
    return httpClient.get('/api/v1/health/live')
  },

  async systemStatus(): Promise<Record<string, unknown>> {
    return httpClient.get('/api/v1/health/status')
  },
}

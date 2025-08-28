/**
 * Страница настроек приложения
 * Примечание: В соответствии с FSD, основная логика настроек
 * должна быть перенесена в pages/settings слой
 */

import { PageContainer } from '@/shared/ui'

export default function SettingsPage() {
  return (
    <PageContainer maxWidth="full" background="gradient">
      <div className="text-center py-12">
        <h1 className="text-2xl font-bold text-foreground mb-4">
          Настройки приложения
        </h1>
        <p className="text-muted-foreground">
          Компоненты настроек будут реализованы в pages/settings слое
        </p>
      </div>
    </PageContainer>
  )
}

/**
 * Страница настроек приложения
 * Примечание: В соответствии с FSD, основная логика настроек
 * должна быть перенесена в pages/settings слой
 */

export default function SettingsPage() {
  return (
    <div className="space-y-6">
      <div className="text-center py-12">
        <h1 className="text-2xl font-bold text-foreground mb-4">
          Настройки приложения
        </h1>
        <p className="text-muted-foreground">
          Компоненты настроек будут реализованы в pages/settings слое
        </p>
      </div>
    </div>
  )
}

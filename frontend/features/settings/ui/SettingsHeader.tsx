/**
 * Заголовок страницы настроек
 */

import { Settings, Shield, Database, Monitor } from 'lucide-react'

export function SettingsHeader() {
  return (
    <div className="bg-gradient-to-r from-slate-900 to-slate-800 rounded-xl p-6 text-white">
      <div className="flex items-center space-x-3 mb-4">
        <div className="p-2 bg-white/10 rounded-lg">
          <Settings className="h-6 w-6" />
        </div>
        <div>
          <h1 className="text-2xl font-bold">Настройки</h1>
          <p className="text-slate-300">
            Управление конфигурацией приложения и системными параметрами
          </p>
        </div>
      </div>

      <div className="flex flex-wrap gap-4">
        <div className="flex items-center gap-2 text-sm text-slate-300 bg-slate-700/50 px-3 py-1 rounded-lg">
          <Shield className="h-4 w-4 text-blue-400" />
          <span>Безопасность</span>
        </div>
        <div className="flex items-center gap-2 text-sm text-slate-300 bg-slate-700/50 px-3 py-1 rounded-lg">
          <Database className="h-4 w-4 text-green-400" />
          <span>База данных</span>
        </div>
        <div className="flex items-center gap-2 text-sm text-slate-300 bg-slate-700/50 px-3 py-1 rounded-lg">
          <Monitor className="h-4 w-4 text-purple-400" />
          <span>Мониторинг</span>
        </div>
      </div>
    </div>
  )
}

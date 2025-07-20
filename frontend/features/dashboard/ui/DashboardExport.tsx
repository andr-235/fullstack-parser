'use client'

import { useState } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { Switch } from '@/components/ui/switch'
import { Label } from '@/components/ui/label'
import {
  Download,
  FileText,
  FileSpreadsheet,
  Calendar,
  Users,
  Target,
  MessageSquare,
  CheckCircle,
  Loader2,
} from 'lucide-react'

/**
 * Интерфейс для настроек экспорта
 */
export interface ExportSettings {
  format: 'csv' | 'xlsx' | 'json'
  dateRange: string
  includeGroups: boolean
  includeKeywords: boolean
  includeComments: boolean
  includeStats: boolean
  groupBy: string
}

/**
 * Пропсы для компонента экспорта
 */
interface DashboardExportProps {
  onExport: (settings: ExportSettings) => Promise<void>
  isExporting: boolean
}

/**
 * Компонент экспорта данных дашборда
 */
export function DashboardExport({
  onExport,
  isExporting,
}: DashboardExportProps) {
  const [settings, setSettings] = useState<ExportSettings>({
    format: 'csv',
    dateRange: 'all',
    includeGroups: true,
    includeKeywords: true,
    includeComments: true,
    includeStats: true,
    groupBy: 'date',
  })

  const handleSettingChange = (key: keyof ExportSettings, value: any) => {
    setSettings((prev) => ({
      ...prev,
      [key]: value,
    }))
  }

  const getFormatIcon = (format: string) => {
    switch (format) {
      case 'csv':
        return <FileText className="h-4 w-4" />
      case 'xlsx':
        return <FileSpreadsheet className="h-4 w-4" />
      case 'json':
        return <FileText className="h-4 w-4" />
      default:
        return <FileText className="h-4 w-4" />
    }
  }

  const getFormatLabel = (format: string) => {
    switch (format) {
      case 'csv':
        return 'CSV файл'
      case 'xlsx':
        return 'Excel файл'
      case 'json':
        return 'JSON файл'
      default:
        return 'Файл'
    }
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Download className="h-5 w-5" />
          Экспорт данных
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-6">
        {/* Формат файла */}
        <div className="space-y-2">
          <Label className="text-sm font-medium">Формат файла</Label>
          <Select
            value={settings.format}
            onValueChange={(value) =>
              handleSettingChange('format', value as 'csv' | 'xlsx' | 'json')
            }
          >
            <SelectTrigger>
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="csv">
                <div className="flex items-center gap-2">
                  {getFormatIcon('csv')}
                  CSV файл
                </div>
              </SelectItem>
              <SelectItem value="xlsx">
                <div className="flex items-center gap-2">
                  {getFormatIcon('xlsx')}
                  Excel файл
                </div>
              </SelectItem>
              <SelectItem value="json">
                <div className="flex items-center gap-2">
                  {getFormatIcon('json')}
                  JSON файл
                </div>
              </SelectItem>
            </SelectContent>
          </Select>
        </div>

        {/* Период */}
        <div className="space-y-2">
          <Label className="text-sm font-medium flex items-center gap-2">
            <Calendar className="h-4 w-4" />
            Период данных
          </Label>
          <Select
            value={settings.dateRange}
            onValueChange={(value) => handleSettingChange('dateRange', value)}
          >
            <SelectTrigger>
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">Все время</SelectItem>
              <SelectItem value="today">Сегодня</SelectItem>
              <SelectItem value="yesterday">Вчера</SelectItem>
              <SelectItem value="week">За неделю</SelectItem>
              <SelectItem value="month">За месяц</SelectItem>
              <SelectItem value="quarter">За квартал</SelectItem>
              <SelectItem value="year">За год</SelectItem>
            </SelectContent>
          </Select>
        </div>

        {/* Включаемые данные */}
        <div className="space-y-4">
          <Label className="text-sm font-medium">Включаемые данные</Label>

          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Users className="h-4 w-4 text-blue-500" />
                <Label htmlFor="include-groups" className="text-sm">
                  Группы
                </Label>
              </div>
              <Switch
                id="include-groups"
                checked={settings.includeGroups}
                onCheckedChange={(checked) =>
                  handleSettingChange('includeGroups', checked)
                }
              />
            </div>

            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Target className="h-4 w-4 text-green-500" />
                <Label htmlFor="include-keywords" className="text-sm">
                  Ключевые слова
                </Label>
              </div>
              <Switch
                id="include-keywords"
                checked={settings.includeKeywords}
                onCheckedChange={(checked) =>
                  handleSettingChange('includeKeywords', checked)
                }
              />
            </div>

            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <MessageSquare className="h-4 w-4 text-purple-500" />
                <Label htmlFor="include-comments" className="text-sm">
                  Комментарии
                </Label>
              </div>
              <Switch
                id="include-comments"
                checked={settings.includeComments}
                onCheckedChange={(checked) =>
                  handleSettingChange('includeComments', checked)
                }
              />
            </div>

            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <CheckCircle className="h-4 w-4 text-orange-500" />
                <Label htmlFor="include-stats" className="text-sm">
                  Статистика
                </Label>
              </div>
              <Switch
                id="include-stats"
                checked={settings.includeStats}
                onCheckedChange={(checked) =>
                  handleSettingChange('includeStats', checked)
                }
              />
            </div>
          </div>
        </div>

        {/* Группировка */}
        <div className="space-y-2">
          <Label className="text-sm font-medium">Группировка данных</Label>
          <Select
            value={settings.groupBy}
            onValueChange={(value) => handleSettingChange('groupBy', value)}
          >
            <SelectTrigger>
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="date">По дате</SelectItem>
              <SelectItem value="group">По группе</SelectItem>
              <SelectItem value="keyword">По ключевому слову</SelectItem>
              <SelectItem value="none">Без группировки</SelectItem>
            </SelectContent>
          </Select>
        </div>

        {/* Кнопка экспорта */}
        <Button
          onClick={() => onExport(settings)}
          disabled={isExporting}
          className="w-full"
        >
          {isExporting ? (
            <>
              <Loader2 className="h-4 w-4 mr-2 animate-spin" />
              Экспорт...
            </>
          ) : (
            <>
              <Download className="h-4 w-4 mr-2" />
              Экспортировать {getFormatLabel(settings.format)}
            </>
          )}
        </Button>

        {/* Информация о форматах */}
        <div className="text-xs text-slate-500 space-y-1">
          <p>
            <strong>CSV:</strong> Простой текстовый формат, подходит для Excel
          </p>
          <p>
            <strong>Excel:</strong> Нативный формат Microsoft Excel с
            форматированием
          </p>
          <p>
            <strong>JSON:</strong> Структурированный формат для программной
            обработки
          </p>
        </div>
      </CardContent>
    </Card>
  )
}

/**
 * Хук для управления экспортом
 */
export function useDashboardExport() {
  const [isExporting, setIsExporting] = useState(false)

  const handleExport = async (settings: ExportSettings) => {
    setIsExporting(true)
    try {
      // Здесь будет логика экспорта
      console.log('Exporting with settings:', settings)

      // Имитация задержки
      await new Promise((resolve) => setTimeout(resolve, 2000))

      // Создание и скачивание файла
      const fileName = `dashboard-export-${new Date().toISOString().split('T')[0]}.${settings.format}`
      const content = `Экспорт данных дашборда\nФормат: ${settings.format}\nПериод: ${settings.dateRange}\nДата экспорта: ${new Date().toLocaleString('ru-RU')}`

      const blob = new Blob([content], { type: 'text/plain' })
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = fileName
      document.body.appendChild(a)
      a.click()
      document.body.removeChild(a)
      URL.revokeObjectURL(url)
    } catch (error) {
      console.error('Export failed:', error)
    } finally {
      setIsExporting(false)
    }
  }

  return {
    isExporting,
    handleExport,
  }
}

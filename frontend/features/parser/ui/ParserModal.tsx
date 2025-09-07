'use client'

import { useState } from 'react'

import { Play, Settings } from 'lucide-react'

import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '@/shared/ui'
import { Button } from '@/shared/ui'
import { Input } from '@/shared/ui'
import { Label } from '@/shared/ui'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/shared/ui'
import { Switch } from '@/shared/ui'

import type { VKGroup } from '@/entities/groups'
import type { ParserStats } from '@/entities/parser'

interface ParserModalProps {
 groups?: VKGroup[]
 stats?: ParserStats | null
 onStartParsing: (config: {
  groupId?: number | undefined
  parseAllGroups: boolean
  maxPosts: number
  forceReparse: boolean
 }) => void
 isOpen?: boolean
 onOpenChange?: (open: boolean) => void
 trigger?: React.ReactNode
}

export function ParserModal({
 groups = [],
 stats,
 onStartParsing,
 isOpen,
 onOpenChange,
 trigger
}: ParserModalProps) {
 const [selectedGroupId, setSelectedGroupId] = useState<string>('')
 const [maxPosts, setMaxPosts] = useState<number>(100)
 const [forceReparse, setForceReparse] = useState<boolean>(false)
 const [parseAllGroups, setParseAllGroups] = useState<boolean>(false)

 const handleStartParsing = () => {
  if (!parseAllGroups && !selectedGroupId) {
   alert('Выберите группу для парсинга или включите режим парсинга всех групп')
   return
  }

  // Лимиты групп убраны - можно парсить любое количество групп

  onStartParsing({
   groupId: parseAllGroups ? undefined : Number(selectedGroupId),
   parseAllGroups,
   maxPosts,
   forceReparse,
  })

  // Сбросить форму и закрыть модальное окно
  setSelectedGroupId('')
  setParseAllGroups(false)
  onOpenChange?.(false)
 }

 const activeGroups = groups.filter(group => group.is_active)

 return (
  <Dialog open={isOpen ?? false} onOpenChange={onOpenChange ?? (() => { })}>
   {trigger && <DialogTrigger asChild>{trigger}</DialogTrigger>}
   <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
    <DialogHeader>
     <DialogTitle className="flex items-center gap-2">
      <Settings className="h-5 w-5" />
      Настройка парсера
     </DialogTitle>
    </DialogHeader>

    <div className="space-y-6 py-4">
     {/* Режим парсинга */}
     <div className="space-y-4">
      <div className="flex items-center justify-between">
       <div className="space-y-1">
        <Label className="text-base font-medium">Режим парсинга</Label>
        <p className="text-sm text-muted-foreground">
         Выберите одну группу или парсите все активные группы
        </p>
       </div>
       <div className="flex items-center space-x-2">
        <Label htmlFor="parse-all-modal" className="text-sm">Все группы</Label>
        <Switch
         id="parse-all-modal"
         checked={parseAllGroups}
         onCheckedChange={(checked) => {
          setParseAllGroups(checked)
          if (checked) {
           setSelectedGroupId('') // Очищаем выбор группы
          }
         }}
        />
       </div>
      </div>

      {/* Выбор группы */}
      <div className="space-y-2">
       <Label htmlFor="group-select-modal" className="text-base font-medium">Группа для парсинга</Label>
       <Select
        value={selectedGroupId}
        onValueChange={setSelectedGroupId}
        disabled={parseAllGroups}
       >
        <SelectTrigger>
         <SelectValue placeholder={parseAllGroups ? "Все активные группы" : "Выберите группу"} />
        </SelectTrigger>
        <SelectContent>
         {activeGroups.map((group) => (
          <SelectItem key={group.id} value={group.id.toString()}>
           {group.name} ({group.screen_name})
          </SelectItem>
         ))}
        </SelectContent>
       </Select>
       {activeGroups.length === 0 && (
        <p className="text-sm text-muted-foreground">
         Нет активных групп. Сначала настройте группы в разделе &quot;Группы&quot;.
        </p>
       )}
       {parseAllGroups && (
        <div className="p-3 bg-blue-50 border border-blue-200 rounded-lg dark:bg-blue-950/50 dark:border-blue-800">
         <p className="text-sm text-blue-800 dark:text-blue-200">
          📊 Будет запущен парсинг <strong>{activeGroups.length} активных групп</strong>
         </p>
         {/* Лимиты групп убраны - можно парсить любое количество групп */}
         {/* Лимиты групп убраны - можно парсить любое количество групп */}
        </div>
       )}
      </div>
     </div>

     {/* Настройки парсинга */}
     <div className="grid gap-4 md:grid-cols-2">
      <div className="space-y-2">
       <Label htmlFor="max-posts-modal" className="text-base font-medium">Максимум постов на группу</Label>
       <Input
        id="max-posts-modal"
        type="number"
        min="1"
        max="1000"
        value={maxPosts}
        onChange={(e) => setMaxPosts(Number(e.target.value))}
       />
       <p className="text-xs text-muted-foreground">
        Рекомендуется: 50-200 постов
       </p>
      </div>

      <div className="space-y-2">
       <Label htmlFor="force-reparse-modal" className="text-base font-medium">Принудительный повтор</Label>
       <div className="flex items-center space-x-2 pt-2">
        <Switch
         id="force-reparse-modal"
         checked={forceReparse}
         onCheckedChange={setForceReparse}
        />
        <span className="text-sm text-muted-foreground">
         Перепарсить уже обработанные посты
        </span>
       </div>
      </div>
     </div>

     {/* Информация о настройках */}
     <div className="grid gap-4 md:grid-cols-2">
      <div className="space-y-2">
       <Label className="text-base font-medium">Комментариев за запрос</Label>
       <p className="text-sm text-muted-foreground">Автоматически: 50-100</p>
      </div>
      <div className="space-y-2">
       <Label className="text-base font-medium">Задержка между запросами</Label>
       <p className="text-sm text-muted-foreground">Автоматически: 1-3 сек</p>
      </div>
      <div className="space-y-2">
       <Label className="text-base font-medium">Попытки повтора при ошибке</Label>
       <p className="text-sm text-muted-foreground">Максимум: 3</p>
      </div>
      <div className="space-y-2">
       <Label className="text-base font-medium">Таймаут запроса</Label>
       <p className="text-sm text-muted-foreground">Максимум: 30 сек</p>
      </div>
     </div>

     {/* Кнопка запуска */}
     <div className="pt-4 border-t">
      <Button
       onClick={handleStartParsing}
       disabled={(!parseAllGroups && !selectedGroupId) || activeGroups.length === 0}
       className="w-full gap-2"
       size="lg"
      >
       <Play className="h-4 w-4" />
       {parseAllGroups
        ? `Запустить парсинг всех групп (${activeGroups.length})`
        : 'Запустить парсинг выбранной группы'
       }
      </Button>
     </div>

     {/* Информация о группах */}
     {activeGroups.length > 0 && (
      <div className="text-sm text-muted-foreground">
       <p>Доступно групп для парсинга: {activeGroups.length}</p>
       <p>Выберите группу из списка выше для начала парсинга комментариев.</p>
      </div>
     )}
    </div>
   </DialogContent>
  </Dialog>
 )
}

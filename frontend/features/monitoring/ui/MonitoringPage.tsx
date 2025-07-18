"use client";

import { 
  Card, 
  CardContent, 
  CardHeader, 
  CardTitle,
  Button,
  LoadingSpinner
} from "@/shared/ui";
import { useMonitoringStats, useMonitoringGroups, useRunMonitoringCycle } from "@/hooks/use-monitoring";
import { Activity, Play, Users, Clock, AlertTriangle, CheckCircle } from "lucide-react";
import { formatDistanceToNow } from "date-fns";
import { ru } from "date-fns/locale";
import GroupsMonitoringTable from "./GroupsMonitoringTable";

export default function MonitoringPage() {
 const { data: stats, isLoading: statsLoading, error: statsError } = useMonitoringStats();
 const { data: groups, isLoading: groupsLoading, error: groupsError } = useMonitoringGroups();
 const runCycleMutation = useRunMonitoringCycle();

 if (statsLoading || groupsLoading) {
  return (
   <div className="flex justify-center items-center h-full">
    <LoadingSpinner />
   </div>
  );
 }

 if (statsError || groupsError) {
  return (
   <div className="flex justify-center items-center h-full">
    <Card className="w-96">
     <CardHeader>
      <CardTitle className="text-red-500">Ошибка</CardTitle>
     </CardHeader>
     <CardContent>
      <p>
       Не удалось загрузить данные мониторинга. Попробуйте обновить страницу.
      </p>
      <p className="text-sm text-slate-400 mt-2">
       {statsError?.message || groupsError?.message}
      </p>
     </CardContent>
    </Card>
   </div>
  );
 }

 const nextMonitoringTime = stats?.next_monitoring_at
  ? formatDistanceToNow(new Date(stats.next_monitoring_at), {
   addSuffix: true,
   locale: ru
  })
  : "Не запланировано";

 return (
  <div className="space-y-6">
   {/* Заголовок с кнопкой запуска цикла */}
   <div className="flex justify-between items-center">
    <div>
     <h1 className="text-2xl font-bold text-slate-50">Мониторинг групп ВК</h1>
     <p className="text-slate-400 mt-1">
      Автоматический мониторинг и парсинг групп ВКонтакте
     </p>
    </div>
    <Button
     onClick={() => runCycleMutation.mutate()}
     disabled={runCycleMutation.isPending}
     className="flex items-center gap-2"
    >
     <Play className="h-4 w-4" />
     {runCycleMutation.isPending ? "Запуск..." : "Запустить цикл"}
    </Button>
   </div>

   {/* Карточки статистики */}
   <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
    <Card>
     <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
      <CardTitle className="text-sm font-medium">Всего групп</CardTitle>
      <Users className="h-4 w-4 text-slate-400" />
     </CardHeader>
     <CardContent>
      <div className="text-2xl font-bold">{stats?.total_groups || 0}</div>
      <p className="text-xs text-slate-400 mt-1">
       {stats?.active_groups || 0} активных
      </p>
     </CardContent>
    </Card>

    <Card>
     <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
      <CardTitle className="text-sm font-medium">Мониторинг</CardTitle>
      <Activity className="h-4 w-4 text-slate-400" />
     </CardHeader>
     <CardContent>
      <div className="text-2xl font-bold">{stats?.monitored_groups || 0}</div>
      <p className="text-xs text-slate-400 mt-1">
       {stats?.ready_for_monitoring || 0} готовы к проверке
      </p>
     </CardContent>
    </Card>

    <Card>
     <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
      <CardTitle className="text-sm font-medium">Следующий запуск</CardTitle>
      <Clock className="h-4 w-4 text-slate-400" />
     </CardHeader>
     <CardContent>
      <div className="text-sm font-medium text-slate-50">
       {nextMonitoringTime}
      </div>
      <p className="text-xs text-slate-400 mt-1">
       Автоматический цикл
      </p>
     </CardContent>
    </Card>

    <Card>
     <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
      <CardTitle className="text-sm font-medium">Статус</CardTitle>
      {stats?.ready_for_monitoring && stats.ready_for_monitoring > 0 ? (
       <AlertTriangle className="h-4 w-4 text-yellow-400" />
      ) : (
       <CheckCircle className="h-4 w-4 text-green-400" />
      )}
     </CardHeader>
     <CardContent>
      <div className="text-sm font-medium text-slate-50">
       {stats?.ready_for_monitoring && stats.ready_for_monitoring > 0
        ? `${stats.ready_for_monitoring} групп ждут`
        : "Все группы обработаны"
       }
      </div>
      <p className="text-xs text-slate-400 mt-1">
       Система работает
      </p>
     </CardContent>
    </Card>
   </div>

   {/* Таблица групп */}
   <Card>
    <CardHeader>
     <CardTitle className="flex items-center gap-2">
      <Activity className="h-5 w-5" />
      Группы с мониторингом
     </CardTitle>
    </CardHeader>
    <CardContent>
     <GroupsMonitoringTable groups={groups?.items || []} />
    </CardContent>
   </Card>
  </div>
 );
} 
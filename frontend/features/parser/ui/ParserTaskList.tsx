'use client';

import React from 'react';
import { format } from 'date-fns';
import { ru } from 'date-fns/locale';
import type { ParsingTask } from '@/entities/parser/types';
import { Button } from '@/shared/ui/button';
import { Card } from '@/shared/ui/card';
import { Badge } from '@/shared/ui/badge';
// import { LoadingSpinner } from '@/shared/ui/loading-spinner';

interface ParserTaskListProps {
  tasks: ParsingTask[];
  loading?: boolean;
  error?: string | null;
  onStopTask: (taskId: string) => Promise<void>;
  onRefresh: () => void;
}

const getStatusColor = (status: string) => {
  switch (status) {
    case 'pending':
      return 'bg-yellow-100 text-yellow-800';
    case 'running':
      return 'bg-blue-100 text-blue-800';
    case 'completed':
      return 'bg-green-100 text-green-800';
    case 'failed':
      return 'bg-red-100 text-red-800';
    case 'stopped':
      return 'bg-gray-100 text-gray-800';
    default:
      return 'bg-gray-100 text-gray-800';
  }
};

const getStatusText = (status: string) => {
  switch (status) {
    case 'pending':
      return 'Ожидает';
    case 'running':
      return 'Выполняется';
    case 'completed':
      return 'Завершена';
    case 'failed':
      return 'Ошибка';
    case 'stopped':
      return 'Остановлена';
    default:
      return status;
  }
};

const getPriorityColor = (priority: string) => {
  switch (priority) {
    case 'high':
      return 'bg-red-100 text-red-800';
    case 'normal':
      return 'bg-blue-100 text-blue-800';
    case 'low':
      return 'bg-gray-100 text-gray-800';
    default:
      return 'bg-gray-100 text-gray-800';
  }
};

const getPriorityText = (priority: string) => {
  switch (priority) {
    case 'high':
      return 'Высокий';
    case 'normal':
      return 'Нормальный';
    case 'low':
      return 'Низкий';
    default:
      return priority;
  }
};

export const ParserTaskList: React.FC<ParserTaskListProps> = ({
  tasks,
  loading = false,
  error,
  onStopTask,
  onRefresh,
}) => {
  if (loading && tasks.length === 0) {
    return (
      <Card className="p-6">
        <div className="flex items-center justify-center py-8">
          <div className="text-center py-4">Загрузка...</div>
          <span className="ml-2 text-gray-600">Загрузка задач...</span>
        </div>
      </Card>
    );
  }

  if (error) {
    return (
      <Card className="p-6">
        <div className="text-center py-8">
          <div className="text-red-600 mb-4">
            Ошибка загрузки задач: {error}
          </div>
          <Button onClick={onRefresh} variant="outline">
            Попробовать снова
          </Button>
        </div>
      </Card>
    );
  }

  if (tasks.length === 0) {
    return (
      <Card className="p-6">
        <div className="text-center py-8">
          <div className="text-gray-500 mb-4">
            Нет активных задач парсинга
          </div>
          <Button onClick={onRefresh} variant="outline">
            Обновить
          </Button>
        </div>
      </Card>
    );
  }

  return (
    <Card className="p-6">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-xl font-semibold text-gray-900">
          Задачи парсинга ({tasks.length})
        </h2>
        <Button onClick={onRefresh} variant="outline" size="sm">
          Обновить
        </Button>
      </div>

      <div className="space-y-4">
        {tasks.map((task) => (
          <div
            key={task.task_id}
            className="border border-gray-200 rounded-lg p-4 hover:bg-gray-50 transition-colors"
          >
            <div className="flex items-start justify-between mb-3">
              <div className="flex-1">
                <div className="flex items-center gap-2 mb-2">
                  <span className="font-medium text-gray-900">
                    Задача {task.task_id.slice(0, 8)}...
                  </span>
                  <Badge className={getStatusColor(task.status)}>
                    {getStatusText(task.status)}
                  </Badge>
                  <Badge className={getPriorityColor(task.priority)}>
                    {getPriorityText(task.priority)}
                  </Badge>
                </div>

                <div className="text-sm text-gray-600 space-y-1">
                  <div>
                    Группы: {task.group_ids.join(', ')}
                  </div>
                  <div>
                    Создано: {format(new Date(task.created_at), 'dd.MM.yyyy HH:mm', { locale: ru })}
                  </div>
                  {task.started_at && (
                    <div>
                      Начато: {format(new Date(task.started_at), 'dd.MM.yyyy HH:mm', { locale: ru })}
                    </div>
                  )}
                  {task.completed_at && (
                    <div>
                      Завершено: {format(new Date(task.completed_at), 'dd.MM.yyyy HH:mm', { locale: ru })}
                    </div>
                  )}
                </div>
              </div>

              <div className="ml-4">
                {task.status === 'running' && (
                  <Button
                    onClick={() => onStopTask(task.task_id)}
                    variant="outline"
                    size="sm"
                    className="text-red-600 border-red-300 hover:bg-red-50"
                  >
                    Остановить
                  </Button>
                )}
              </div>
            </div>

            {/* Прогресс бар */}
            <div className="w-full bg-gray-200 rounded-full h-2 mb-2">
              <div
                className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                style={{ width: `${task.progress}%` }}
              />
            </div>
            <div className="text-xs text-gray-500 text-right">
              {task.progress}% завершено
            </div>
          </div>
        ))}
      </div>
    </Card>
  );
};
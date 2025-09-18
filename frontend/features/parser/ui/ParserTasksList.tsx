'use client';

import React from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/shared/ui/card';
import { Button } from '@/shared/ui/button';
import { Badge } from '@/shared/ui/badge';
import { Progress } from '@/shared/ui/progress';
import { Alert, AlertDescription } from '@/shared/ui/alert';
import { RefreshCw, Play, Square, AlertCircle } from 'lucide-react';
import { ParsingTask, TaskStatus } from '@/entities/parser';

interface ParserTasksListProps {
  tasks: ParsingTask[] | null;
  loading: boolean;
  error: string | null;
  onRefetch: () => void;
}

const getStatusBadgeVariant = (status: TaskStatus) => {
  switch (status) {
    case 'completed':
      return 'default';
    case 'running':
      return 'secondary';
    case 'failed':
      return 'destructive';
    case 'stopped':
      return 'outline';
    default:
      return 'outline';
  }
};

const getStatusText = (status: TaskStatus) => {
  switch (status) {
    case 'pending':
      return 'Ожидает';
    case 'running':
      return 'Выполняется';
    case 'completed':
      return 'Завершено';
    case 'failed':
      return 'Ошибка';
    case 'stopped':
      return 'Остановлено';
    default:
      return status;
  }
};

export const ParserTasksList: React.FC<ParserTasksListProps> = ({
  tasks,
  loading,
  error,
  onRefetch,
}) => {
  if (error) {
    return (
      <Alert variant="destructive">
        <AlertCircle className="h-4 w-4" />
        <AlertDescription>
          {error}
          <Button
            variant="outline"
            size="sm"
            onClick={onRefetch}
            className="ml-2"
          >
            <RefreshCw className="h-4 w-4 mr-1" />
            Повторить
          </Button>
        </AlertDescription>
      </Alert>
    );
  }

  if (loading && !tasks) {
    return (
      <div className="space-y-4">
        {[...Array(3)].map((_, i) => (
          <Card key={i} className="animate-pulse">
            <CardHeader>
              <div className="h-4 bg-muted rounded w-1/4"></div>
              <div className="h-3 bg-muted rounded w-1/2"></div>
            </CardHeader>
            <CardContent>
              <div className="h-2 bg-muted rounded w-full"></div>
            </CardContent>
          </Card>
        ))}
      </div>
    );
  }

  if (!tasks || tasks.length === 0) {
    return (
      <div className="text-center py-8">
        <p className="text-muted-foreground">Нет активных задач</p>
        <Button
          variant="outline"
          onClick={onRefetch}
          className="mt-4"
        >
          <RefreshCw className="h-4 w-4 mr-2" />
          Обновить
        </Button>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center">
        <h3 className="text-lg font-semibold">Задачи парсинга ({tasks.length})</h3>
        <Button
          variant="outline"
          size="sm"
          onClick={onRefetch}
          disabled={loading}
        >
          <RefreshCw className={`h-4 w-4 mr-2 ${loading ? 'animate-spin' : ''}`} />
          Обновить
        </Button>
      </div>

      {tasks.map((task) => (
        <Card key={task.task_id}>
          <CardHeader className="pb-3">
            <div className="flex justify-between items-start">
              <div>
                <CardTitle className="text-base">
                  Задача {task.task_id.slice(0, 8)}...
                </CardTitle>
                <CardDescription>
                  Группы: {task.group_ids.join(', ')}
                </CardDescription>
              </div>
              <Badge variant={getStatusBadgeVariant(task.status)}>
                {getStatusText(task.status)}
              </Badge>
            </div>
          </CardHeader>
          <CardContent className="space-y-3">
            <div className="flex justify-between text-sm">
              <span>Прогресс:</span>
              <span>{task.progress}%</span>
            </div>
            <Progress value={task.progress} className="h-2" />

            <div className="grid grid-cols-2 gap-4 text-sm">
              <div>
                <span className="text-muted-foreground">Постов найдено:</span>
                <span className="ml-2 font-medium">{task.posts_found}</span>
              </div>
              <div>
                <span className="text-muted-foreground">Комментариев найдено:</span>
                <span className="ml-2 font-medium">{task.comments_found}</span>
              </div>
            </div>

            {task.current_group && (
              <div className="text-sm">
                <span className="text-muted-foreground">Текущая группа:</span>
                <span className="ml-2 font-medium">{task.current_group}</span>
              </div>
            )}

            {task.errors && task.errors.length > 0 && (
              <Alert variant="destructive" className="mt-3">
                <AlertCircle className="h-4 w-4" />
                <AlertDescription>
                  {task.errors.join('; ')}
                </AlertDescription>
              </Alert>
            )}

            <div className="flex justify-between items-center text-xs text-muted-foreground">
              <span>
                Создано: {new Date(task.created_at).toLocaleString('ru-RU')}
              </span>
              {task.completed_at && (
                <span>
                  Завершено: {new Date(task.completed_at).toLocaleString('ru-RU')}
                </span>
              )}
            </div>
          </CardContent>
        </Card>
      ))}
    </div>
  );
};
'use client';

import React from 'react';
import { Button } from '@/shared/ui/button';

interface ParserControlsProps {
  onRefresh: () => void;
  loading?: boolean;
}

export const ParserControls: React.FC<ParserControlsProps> = ({
  onRefresh,
  loading = false,
}) => {
  return (
    <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
      <div className="text-sm text-gray-600">
        Управление парсингом и обновление данных
      </div>

      <div className="flex items-center gap-3">
        <Button
          onClick={onRefresh}
          disabled={loading}
          variant="outline"
          size="sm"
        >
          {loading ? 'Обновление...' : 'Обновить данные'}
        </Button>
      </div>
    </div>
  );
};
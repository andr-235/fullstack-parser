'use client';

import React from 'react';
import { ParserFormData } from '@/entities/parser';

interface ParserFormProps {
  formData: ParserFormData;
  isSubmitting: boolean;
  error: string | null;
  onSubmit: (data: ParserFormData) => Promise<void>;
  onChange: (field: keyof ParserFormData, value: any) => void;
}

export const ParserForm: React.FC<ParserFormProps> = ({
  formData,
  isSubmitting,
  error,
  onSubmit,
  onChange,
}) => {
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    await onSubmit(formData);
  };

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h2 className="text-lg font-semibold text-gray-900 mb-4">
        Создать задачу парсинга
      </h2>

      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label htmlFor="groupIds" className="block text-sm font-medium text-gray-700 mb-1">
            ID групп VK (через запятую)
          </label>
          <input
            type="text"
            id="groupIds"
            value={formData.group_ids}
            onChange={(e) => onChange('group_ids', e.target.value)}
            placeholder="12345678, 87654321, 11223344"
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            required
          />
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div>
            <label htmlFor="maxPosts" className="block text-sm font-medium text-gray-700 mb-1">
              Максимум постов
            </label>
            <input
              type="number"
              id="maxPosts"
              value={formData.max_posts}
              onChange={(e) => onChange('max_posts', Number(e.target.value))}
              min="1"
              max="1000"
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          <div>
            <label htmlFor="maxComments" className="block text-sm font-medium text-gray-700 mb-1">
              Максимум комментариев на пост
            </label>
            <input
              type="number"
              id="maxComments"
              value={formData.max_comments_per_post}
              onChange={(e) => onChange('max_comments_per_post', Number(e.target.value))}
              min="0"
              max="1000"
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
        </div>

        <div className="flex items-center space-x-4">
          <div className="flex items-center">
            <input
              type="checkbox"
              id="forceReparse"
              checked={formData.force_reparse}
              onChange={(e) => onChange('force_reparse', e.target.checked)}
              className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
            />
            <label htmlFor="forceReparse" className="ml-2 text-sm text-gray-700">
              Принудительный перепарсинг
            </label>
          </div>

          <div>
            <label htmlFor="priority" className="block text-sm font-medium text-gray-700 mb-1">
              Приоритет
            </label>
            <select
              id="priority"
              value={formData.priority}
              onChange={(e) => onChange('priority', e.target.value as 'low' | 'normal' | 'high')}
              className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="low">Низкий</option>
              <option value="normal">Нормальный</option>
              <option value="high">Высокий</option>
            </select>
          </div>
        </div>

        {error && (
          <div className="bg-red-50 border border-red-200 rounded-md p-3">
            <p className="text-sm text-red-600">{error}</p>
          </div>
        )}

        <button
          type="submit"
          disabled={isSubmitting}
          className="w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {isSubmitting ? 'Создание задачи...' : 'Запустить парсинг'}
        </button>
      </form>
    </div>
  );
};
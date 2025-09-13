'use client';

import { useState, useEffect } from 'react';
import { Plus, RefreshCw } from 'lucide-react';

import { KeywordsFilters as KeywordsFiltersType, CreateKeywordRequest, UpdateKeywordRequest, useKeywords } from '@/entities/keywords';
import { KeywordForm, KeywordsFilters, KeywordsList } from '@/features/keywords';

const FILTERS_STORAGE_KEY = 'keywords-filters';

export function KeywordsPage() {
  const [filters, setFilters] = useState<KeywordsFiltersType>({ active_only: true });
  const [showCreateForm, setShowCreateForm] = useState(false);

  const { keywords, loading, error, createKeyword, updateKeyword, deleteKeyword, toggleKeywordStatus, refetch } = useKeywords(filters);

  useEffect(() => {
    const saved = localStorage.getItem(FILTERS_STORAGE_KEY);
    if (saved) {
      try {
        setFilters(JSON.parse(saved));
      } catch {
        // Ignore parse errors
      }
    }
  }, []);

  useEffect(() => {
    localStorage.setItem(FILTERS_STORAGE_KEY, JSON.stringify(filters));
  }, [filters]);

  const handleCreate = async (data: any) => {
    const createData: CreateKeywordRequest = {
      word: data.word,
      ...(data.category && { category_name: data.category }),
      ...(data.description && { description: data.description }),
      priority: 0,
    };
    await createKeyword(createData);
    setShowCreateForm(false);
    refetch();
  };

  const handleUpdate = async (id: number, updates: UpdateKeywordRequest) => {
    await updateKeyword(id, updates);
    refetch();
  };

  const handleDelete = async (id: number) => {
    await deleteKeyword(id);
    refetch();
  };

  const handleToggle = async (id: number, isActive: boolean) => {
    await toggleKeywordStatus(id, isActive);
    refetch();
  };

  return (
    <div className="container mx-auto py-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Ключевые слова</h1>
          <p className="text-gray-600">Управление ключевыми словами для мониторинга и фильтрации комментариев</p>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={refetch}
            className="px-4 py-2 border border-gray-300 rounded-md hover:bg-gray-50 flex items-center gap-2"
          >
            <RefreshCw className="h-4 w-4" />
            Обновить
          </button>

          <button
            onClick={() => setShowCreateForm(true)}
            className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 flex items-center gap-2"
          >
            <Plus className="h-4 w-4" />
            Добавить ключевое слово
          </button>
        </div>
      </div>

      <div className="bg-white border border-gray-200 rounded-lg">
        <div className="px-6 py-4 border-b border-gray-200">
          <h2 className="text-lg font-medium">Фильтры</h2>
        </div>
        <div className="p-6">
          <KeywordsFilters filters={filters} onFiltersChange={setFilters} />
        </div>
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 rounded-md p-4">
          <div className="flex items-center justify-between">
            <span className="text-red-800">Ошибка загрузки ключевых слов: {error}</span>
            <button
              onClick={refetch}
              className="ml-4 px-3 py-1 text-sm border border-red-300 rounded hover:bg-red-100"
            >
              Попробовать снова
            </button>
          </div>
        </div>
      )}

      <KeywordsList
        keywords={keywords}
        loading={loading}
        onUpdate={handleUpdate}
        onDelete={handleDelete}
        onToggleStatus={handleToggle}
      />

      {showCreateForm && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg max-w-md w-full mx-4">
            <div className="px-6 py-4 border-b border-gray-200">
              <h2 className="text-lg font-medium">Добавить новое ключевое слово</h2>
            </div>
            <div className="p-6">
              <KeywordForm onSubmit={handleCreate} onCancel={() => setShowCreateForm(false)} />
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

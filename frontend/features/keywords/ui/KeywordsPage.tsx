'use client';

import { useState, useEffect } from 'react';
import { Plus, RefreshCw } from 'lucide-react';

import { Button, Card, CardContent, CardHeader, CardTitle, Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger, FileUploadModal, Alert, AlertDescription } from '@/shared/ui';
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
          <p className="text-muted-foreground">Управление ключевыми словами для мониторинга и фильтрации комментариев</p>
        </div>

        <div className="flex items-center gap-2">
          <Button variant="outline" onClick={refetch}>
            <RefreshCw className="mr-2 h-4 w-4" />
            Обновить
          </Button>

          <FileUploadModal
            type="keywords"
            triggerText="Загрузить из файла"
            onSuccess={refetch}
            apiParams={{ is_active: true, is_case_sensitive: false, is_whole_word: false }}
          />

          <Dialog open={showCreateForm} onOpenChange={setShowCreateForm}>
            <DialogTrigger asChild>
              <Button>
                <Plus className="mr-2 h-4 w-4" />
                Добавить ключевое слово
              </Button>
            </DialogTrigger>
            <DialogContent className="max-w-md">
              <DialogHeader>
                <DialogTitle>Добавить новое ключевое слово</DialogTitle>
              </DialogHeader>
              <KeywordForm onSubmit={handleCreate} onCancel={() => setShowCreateForm(false)} />
            </DialogContent>
          </Dialog>
        </div>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="text-lg">Фильтры</CardTitle>
        </CardHeader>
        <CardContent>
          <KeywordsFilters filters={filters} onFiltersChange={setFilters} />
        </CardContent>
      </Card>

      {error && (
        <Alert className="border-destructive">
          <AlertDescription>
            Ошибка загрузки ключевых слов: {error}
            <Button variant="outline" size="sm" onClick={refetch} className="ml-4">
              Попробовать снова
            </Button>
          </AlertDescription>
        </Alert>
      )}

      <KeywordsList
        keywords={keywords}
        loading={loading}
        onUpdate={handleUpdate}
        onDelete={handleDelete}
        onToggleStatus={handleToggle}
      />
    </div>
  );
}

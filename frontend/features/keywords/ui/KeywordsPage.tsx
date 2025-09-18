'use client';

import { useState, useEffect, useRef } from 'react';
import { Plus, RefreshCw, AlertCircle, Loader2, Upload, Hash } from 'lucide-react';

import { KeywordsFilters as KeywordsFiltersType, CreateKeywordRequest, UpdateKeywordRequest, useKeywords } from '@/entities/keywords';
import { KeywordForm, KeywordsFilters, KeywordsList } from '@/features/keywords';
import { GlassCard, GlassCardHeader, GlassCardTitle, GlassCardContent } from '@/shared/ui/glass-card';
import { GlassButton } from '@/shared/ui/glass-button';

const FILTERS_STORAGE_KEY = 'keywords-filters';

/**
 * Страница управления ключевыми словами
 * Предоставляет интерфейс для просмотра, создания, редактирования и удаления ключевых слов
 */
export function KeywordsPage() {
  const [filters, setFilters] = useState<KeywordsFiltersType>({ active_only: true });
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const { keywords, loading, error, createKeyword, updateKeyword, deleteKeyword, toggleKeywordStatus, refetch } = useKeywords(filters);

  useEffect(() => {
    const saved = localStorage.getItem(FILTERS_STORAGE_KEY);
    if (saved) {
      try {
        setFilters(JSON.parse(saved));
      } catch {
        // Игнорируем ошибки парсинга
      }
    }
  }, []);

  useEffect(() => {
    localStorage.setItem(FILTERS_STORAGE_KEY, JSON.stringify(filters));
  }, [filters]);

  const handleCreate = async (data: any) => {
    try {
      const createData: CreateKeywordRequest = {
        word: data.word,
        ...(data.category && { category_name: data.category }),
        ...(data.description && { description: data.description }),
        priority: 0,
      };
      await createKeyword(createData);
      setShowCreateForm(false);
      refetch();
    } catch (err) {
      console.error('Ошибка создания ключевого слова:', err);
    }
  };

  const handleUpdate = async (id: number, updates: UpdateKeywordRequest) => {
    try {
      await updateKeyword(id, updates);
      refetch();
    } catch (err) {
      console.error('Ошибка обновления ключевого слова:', err);
    }
  };

  const handleDelete = async (id: number) => {
    try {
      await deleteKeyword(id);
      refetch();
    } catch (err) {
      console.error('Ошибка удаления ключевого слова:', err);
    }
  };

  const handleToggle = async (id: number, isActive: boolean) => {
    try {
      await toggleKeywordStatus(id, isActive);
      refetch();
    } catch (err) {
      console.error('Ошибка изменения статуса ключевого слова:', err);
    }
  };

  const handleRefresh = async () => {
    setIsRefreshing(true);
    try {
      await refetch();
    } finally {
      setIsRefreshing(false);
    }
  };

  const parseCsv = (content: string): Array<{ word: string; category?: string; description?: string }> => {
    const lines = content.trim().split('\n');
    if (lines.length < 2 || !lines[0]) return [];

    const headers = lines[0].split(',').map(h => h.trim().toLowerCase());
    const wordIndex = headers.indexOf('слово');
    const categoryIndex = headers.indexOf('категория');
    const descriptionIndex = headers.indexOf('описание');

    if (wordIndex === -1) return [];

    return lines.slice(1)
      .map(line => {
        const values = line.split(',').map(v => v.trim());
        return {
          word: values[wordIndex] || '',
          ...(categoryIndex !== -1 && values[categoryIndex] && { category: values[categoryIndex] }),
          ...(descriptionIndex !== -1 && values[descriptionIndex] && { description: values[descriptionIndex] }),
        };
      })
      .filter(item => item.word);
  };

  const parseTxt = (content: string): Array<{ word: string }> => {
    return content
      .split('\n')
      .map(line => line.trim())
      .filter(line => line && !line.startsWith('#'))
      .map(word => ({ word }));
  };

  const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    // Валидация файла
    if (file.size > 5 * 1024 * 1024) { // 5MB
      alert('Файл слишком большой. Максимальный размер: 5MB');
      return;
    }

    const allowedTypes = ['text/csv', 'text/plain', 'application/vnd.ms-excel'];
    if (!allowedTypes.includes(file.type) && !file.name.endsWith('.csv') && !file.name.endsWith('.txt')) {
      alert('Неподдерживаемый формат файла. Используйте CSV или TXT файлы.');
      return;
    }

    setIsUploading(true);
    try {
      const content = await new Promise<string>((resolve, reject) => {
        const reader = new FileReader();
        reader.onload = (e) => resolve(e.target?.result as string);
        reader.onerror = () => reject(new Error('Ошибка чтения файла'));
        reader.readAsText(file);
      });

      let keywords: Array<{ word: string; category?: string; description?: string }>;

      if (file.name.endsWith('.csv') || file.type === 'text/csv' || file.type === 'application/vnd.ms-excel') {
        keywords = parseCsv(content);
      } else if (file.name.endsWith('.txt') || file.type === 'text/plain') {
        keywords = parseTxt(content);
      } else {
        throw new Error('Неподдерживаемый формат файла');
      }

      if (keywords.length === 0) {
        alert('В файле не найдено ключевых слов');
        return;
      }

      // Создание ключевых слов через API
      for (const keyword of keywords) {
        try {
          const createData: CreateKeywordRequest = {
            word: keyword.word,
            ...(keyword.category && { category_name: keyword.category }),
            ...(keyword.description && { description: keyword.description }),
            priority: 0,
          };
          await createKeyword(createData);
        } catch (err) {
          console.error('Ошибка создания ключевого слова:', keyword.word, err);
          // Продолжаем с остальными словами
        }
      }

      // Обновляем список
      await refetch();
      alert(`Успешно загружено ${keywords.length} ключевых слов`);

    } catch (error) {
      console.error('Ошибка загрузки файла:', error);
      alert('Ошибка загрузки файла: ' + (error instanceof Error ? error.message : 'Неизвестная ошибка'));
    } finally {
      setIsUploading(false);
      // Сбрасываем input
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
    }
  };

  return (
    <main className="container mx-auto py-6 space-y-6" role="main" aria-labelledby="keywords-heading">
      {/* Заголовок страницы */}
      <header className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div className="space-y-1">
          <h1
            id="keywords-heading"
            className="text-3xl font-bold tracking-tight bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent"
          >
            Управление ключевыми словами
          </h1>
          <p className="text-gray-600 dark:text-gray-300">
            Эффективное управление ключевыми словами для SEO-мониторинга и аналитики контента
          </p>
        </div>

        <nav className="flex items-center gap-2" role="navigation" aria-label="Действия со страницей">
          <GlassButton
            onClick={handleRefresh}
            disabled={isRefreshing || loading}
            variant="outline"
            size="md"
            aria-label="Обновить список ключевых слов"
            className="transition-all duration-200 hover:scale-105"
          >
            {isRefreshing ? (
              <Loader2 className="h-4 w-4 animate-spin" />
            ) : (
              <RefreshCw className="h-4 w-4" />
            )}
            <span className="hidden sm:inline">Обновить</span>
          </GlassButton>

          <GlassButton
            onClick={() => fileInputRef.current?.click()}
            disabled={isUploading || loading}
            variant="outline"
            size="md"
            aria-label="Загрузить ключевые слова из файла"
            className="transition-all duration-200 hover:scale-105"
          >
            {isUploading ? (
              <Loader2 className="h-4 w-4 animate-spin" />
            ) : (
              <Upload className="h-4 w-4" />
            )}
            <span className="hidden sm:inline">Загрузить из файла</span>
            <span className="sm:hidden">Загрузить</span>
          </GlassButton>

          <GlassButton
            onClick={() => setShowCreateForm(true)}
            variant="default"
            size="md"
            aria-label="Добавить новое ключевое слово"
            className="transition-all duration-200 hover:scale-105 hover:shadow-lg"
          >
            <Plus className="h-4 w-4" />
            <span className="hidden sm:inline">Добавить ключевое слово</span>
            <span className="sm:hidden">Добавить</span>
          </GlassButton>

          {/* Скрытый input для выбора файла */}
          <input
            ref={fileInputRef}
            type="file"
            accept=".csv,.txt"
            onChange={handleFileUpload}
            className="hidden"
            aria-label="Выбрать файл с ключевыми словами"
          />
        </nav>
      </header>

      {/* Фильтры */}
      <GlassCard className="transition-all duration-300 hover:shadow-xl">
        <GlassCardHeader>
          <GlassCardTitle className="flex items-center gap-2">
            <span>Фильтры</span>
            {loading && <Loader2 className="h-4 w-4 animate-spin" />}
          </GlassCardTitle>
        </GlassCardHeader>
        <GlassCardContent>
          <KeywordsFilters
            filters={filters}
            onFiltersChange={setFilters}
            disabled={loading}
          />
        </GlassCardContent>
      </GlassCard>

      {/* Сообщение об ошибке */}
      {error && (
        <GlassCard className="border-red-500/20 bg-red-500/10 animate-in slide-in-from-top-2 duration-300">
          <GlassCardContent className="pt-6">
            <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
              <div className="flex items-center gap-3">
                <AlertCircle className="h-5 w-5 text-red-500 flex-shrink-0" />
                <span className="text-red-200 font-medium">
                  Ошибка загрузки ключевых слов: {error}
                </span>
              </div>
              <GlassButton
                onClick={handleRefresh}
                variant="outline"
                size="sm"
                className="border-red-500/30 text-red-200 hover:bg-red-500/20 transition-colors"
                aria-label="Попробовать загрузить снова"
              >
                Попробовать снова
              </GlassButton>
            </div>
          </GlassCardContent>
        </GlassCard>
      )}

      {/* Список ключевых слов */}
      <section aria-labelledby="keywords-list-heading">
        <h2 id="keywords-list-heading" className="sr-only">
          Список ключевых слов
        </h2>
        <KeywordsList
          keywords={keywords}
          loading={loading}
          onUpdate={handleUpdate}
          onDelete={handleDelete}
          onToggleStatus={handleToggle}
        />
      </section>

      {/* Модальное окно создания */}
      {showCreateForm && (
        <div
          className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center z-50 animate-in fade-in duration-200"
          role="dialog"
          aria-modal="true"
          aria-labelledby="create-keyword-title"
        >
          <GlassCard className="max-w-md w-full mx-4 animate-in zoom-in-95 duration-200">
            <GlassCardHeader>
              <GlassCardTitle id="create-keyword-title">
                Добавить новое ключевое слово
              </GlassCardTitle>
            </GlassCardHeader>
            <GlassCardContent>
              <KeywordForm
                onSubmit={handleCreate}
                onCancel={() => setShowCreateForm(false)}
              />
            </GlassCardContent>
          </GlassCard>
        </div>
      )}
    </main>
  );
}

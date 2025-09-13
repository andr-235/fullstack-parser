/**
 * Утилиты для работы с комментариями
 */

import type { Comment, CommentResponse, Author } from "../model/types";

/**
 * Форматирует дату комментария
 */
export const formatCommentDate = (dateString: string): string => {
  const date = new Date(dateString);
  return date.toLocaleDateString("ru-RU", {
    year: "numeric",
    month: "short",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
};

/**
 * Получает полное имя автора
 */
export const getAuthorFullName = (author: Author): string => {
  return `${author.first_name} ${author.last_name}`.trim();
};

/**
 * Получает инициалы автора
 */
export const getAuthorInitials = (author: Author): string => {
  const firstInitial = author.first_name.charAt(0).toUpperCase();
  const lastInitial = author.last_name.charAt(0).toUpperCase();
  return `${firstInitial}${lastInitial}`;
};

/**
 * Обрезает текст комментария для предварительного просмотра
 */
export const truncateCommentText = (text: string, maxLength: number = 100): string => {
  if (text.length <= maxLength) return text;
  return text.substring(0, maxLength).trim() + "...";
};

/**
 * Подсчитывает количество слов в тексте
 */
export const countWords = (text: string): number => {
  return text.trim().split(/\s+/).filter(word => word.length > 0).length;
};

/**
 * Извлекает упоминания (@username) из текста
 */
export const extractMentions = (text: string): string[] => {
  const mentionRegex = /@(\w+)/g;
  const mentions: string[] = [];
  let match;
  
  while ((match = mentionRegex.exec(text)) !== null) {
    if (match[1]) {
      mentions.push(match[1]);
    }
  }
  
  return [...new Set(mentions)]; // Убираем дубликаты
};

/**
 * Извлекает хештеги (#hashtag) из текста
 */
export const extractHashtags = (text: string): string[] => {
  const hashtagRegex = /#(\w+)/g;
  const hashtags: string[] = [];
  let match;
  
  while ((match = hashtagRegex.exec(text)) !== null) {
    if (match[1]) {
      hashtags.push(match[1]);
    }
  }
  
  return [...new Set(hashtags)]; // Убираем дубликаты
};

/**
 * Проверяет, является ли комментарий длинным
 */
export const isLongComment = (text: string, threshold: number = 200): boolean => {
  return text.length > threshold;
};

/**
 * Группирует комментарии по дате
 */
export const groupCommentsByDate = (comments: CommentResponse[]): Record<string, CommentResponse[]> => {
  return comments.reduce((groups, comment) => {
    const date = new Date(comment.created_at).toDateString();
    if (!groups[date]) {
      groups[date] = [];
    }
    groups[date].push(comment);
    return groups;
  }, {} as Record<string, CommentResponse[]>);
};

/**
 * Сортирует комментарии по дате (новые сначала)
 */
export const sortCommentsByDate = (comments: CommentResponse[]): CommentResponse[] => {
  return [...comments].sort((a, b) => 
    new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
  );
};

/**
 * Фильтрует комментарии по тексту
 */
export const filterCommentsByText = (
  comments: CommentResponse[],
  searchText: string
): CommentResponse[] => {
  if (!searchText.trim()) return comments;
  
  const lowerSearchText = searchText.toLowerCase();
  return comments.filter(comment => 
    comment.text.toLowerCase().includes(lowerSearchText)
  );
};

/**
 * Вычисляет статистику комментариев
 */
export const calculateCommentStats = (comments: CommentResponse[]) => {
  const totalComments = comments.length;
  const totalWords = comments.reduce((sum, comment) => sum + countWords(comment.text), 0);
  const averageWordsPerComment = totalComments > 0 ? totalWords / totalComments : 0;
  
  const authors = new Set(comments.map(comment => comment.author_id));
  const uniqueAuthors = authors.size;
  
  return {
    totalComments,
    totalWords,
    averageWordsPerComment: Math.round(averageWordsPerComment * 100) / 100,
    uniqueAuthors,
  };
};

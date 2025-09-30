import { VK, CallbackService } from 'vk-io';
import { DirectAuthorization, officialAppCredentials } from '@vk-io/authorization';
import logger from '@/utils/logger';
import {
  VkPost,
  VkComment,
  VkGroup,
  VkProfile,
  VkWallGetResponse,
  VkCommentsGetResponse,
  VkGroupsGetByIdResponse
} from '@/types/vk';

// Интерфейсы для результатов, совместимые с существующим кодом
export interface ProcessedPost {
  vk_post_id: number;
  owner_id: number;
  group_id: number;
  text: string;
  date: Date;
  likes: number;
}

export interface ProcessedComment {
  vk_comment_id: number;
  post_vk_id: number;
  owner_id: number;
  author_id: number;
  author_name: string;
  text: string;
  date: Date;
  likes: number;
}

export interface ProcessedGroup {
  id: number;
  name: string;
  screen_name: string;
  description: string;
  photo_50: string;
  members_count: number;
  is_closed: 0 | 1 | 2;
}

export interface GetPostsResult {
  posts: ProcessedPost[];
}

export interface GetCommentsResult {
  comments: ProcessedComment[];
  hasMore: boolean;
}

/**
 * VkIoService - современный VK API сервис с использованием библиотеки vk-io
 *
 * Основные преимущества:
 * - Автоматический rate limiting
 * - Встроенная обработка ошибок и retry логика
 * - Решение проблемы IP-блокировки через правильную авторизацию
 * - TypeScript поддержка из коробки
 * - 1:1 mapping с VK API методами
 * - Совместимость с существующими интерфейсами
 */
export class VkIoService {
  private vk: VK;
  private isInitialized = false;
  private initializationPromise: Promise<void> | null = null;

  constructor() {
    // Инициализация произойдет при первом вызове API
    this.vk = new VK({
      token: '',
      apiVersion: '5.199'
    });
  }

  /**
   * Инициализация VK API с правильной авторизацией
   * Поддерживает два варианта: существующий токен или DirectAuthorization
   */
  private async initialize(): Promise<void> {
    if (this.isInitialized) {
      return;
    }

    if (this.initializationPromise) {
      return this.initializationPromise;
    }

    this.initializationPromise = this.performInitialization();
    await this.initializationPromise;
  }

  private async performInitialization(): Promise<void> {
    try {
      // Отладочная информация о переменных окружения
      logger.info('VK API initialization debug info', {
        hasVkAccessToken: !!process.env.VK_ACCESS_TOKEN,
        hasVkToken: !!process.env.VK_TOKEN,
        hasVkLogin: !!process.env.VK_LOGIN,
        hasVkPassword: !!process.env.VK_PASSWORD,
        nodeEnv: process.env.NODE_ENV,
        vkAccessTokenLength: process.env.VK_ACCESS_TOKEN?.length,
        vkTokenLength: process.env.VK_TOKEN?.length
      });

      // Вариант 1: Использование существующего токена (если есть)
      const existingToken = process.env.VK_ACCESS_TOKEN;

      if (existingToken) {
        logger.info('Инициализация VK-IO с существующим токеном');
        this.vk = new VK({
          token: existingToken,
          apiVersion: '5.199'
        });

        // Проверяем валидность токена
        try {
          await this.vk.api.account.getInfo({});
          this.isInitialized = true;
          logger.info('VK-IO успешно инициализирован с существующим токеном');
          return;
        } catch (error) {
          logger.warn('Существующий токен недействителен, переходим к DirectAuthorization', {
            error: error instanceof Error ? error.message : String(error)
          });
        }
      }

      // Вариант 2: DirectAuthorization (если есть логин/пароль)
      const vkLogin = process.env.VK_LOGIN;
      const vkPassword = process.env.VK_PASSWORD;

      if (vkLogin && vkPassword) {
        logger.info('Инициализация VK-IO через DirectAuthorization');

        const callbackService = new CallbackService();

        const direct = new DirectAuthorization({
          callbackService,
          scope: 'all',
          ...officialAppCredentials.windows,
          login: vkLogin,
          password: vkPassword,
          apiVersion: '5.199'
        });

        const response = await direct.run();

        this.vk = new VK({
          token: response.token,
          apiVersion: '5.199'
        });

        this.isInitialized = true;
        logger.info('VK-IO успешно инициализирован через DirectAuthorization', {
          userId: response.user,
          expires: response.expires
        });
        return;
      }

      // Если ни один из вариантов не сработал
      throw new Error('Не найдены учетные данные для VK API. Установите VK_ACCESS_TOKEN или VK_LOGIN/VK_PASSWORD');

    } catch (error) {
      const errorMsg = error instanceof Error ? error.message : String(error);
      logger.error('Ошибка инициализации VK-IO', { error: errorMsg });
      throw new Error(`Не удалось инициализировать VK API: ${errorMsg}`);
    }
  }

  /**
   * Получает посты группы с автоматической обработкой ошибок
   * Совместим с существующим интерфейсом
   */
  async getPosts(groupId: number): Promise<GetPostsResult> {
    await this.initialize();

    const ownerId = -Math.abs(groupId); // Группы имеют отрицательный ID

    try {
      logger.info('Получение постов через VK-IO', { groupId, ownerId });

      const response = await this.vk.api.wall.get({
        owner_id: ownerId,
        count: 10,
        extended: 0 // Не включаем профили для экономии запросов
      });

      if (!response.items || response.items.length === 0) {
        logger.warn('Посты не найдены', { groupId, ownerId });
        return { posts: [] };
      }

      logger.info('Посты успешно получены через VK-IO', {
        groupId,
        count: response.items.length
      });

      // Преобразуем в формат, совместимый с существующим кодом
      const posts: ProcessedPost[] = response.items.map(post => ({
        vk_post_id: post.id,
        owner_id: ownerId,
        group_id: Math.abs(groupId),
        text: post.text || '',
        date: new Date(post.date * 1000),
        likes: post.likes?.count || 0
      }));

      return { posts };

    } catch (error) {
      const errorMsg = error instanceof Error ? error.message : String(error);
      logger.error('Ошибка получения постов через VK-IO', {
        groupId,
        ownerId,
        error: errorMsg
      });
      throw new Error(`Ошибка получения постов для группы ${groupId}: ${errorMsg}`);
    }
  }

  /**
   * Получает комментарии к посту с автоматической пагинацией
   * Совместим с существующим интерфейсом
   */
  async getComments(groupId: number, postVkId: number, offset: number = 0): Promise<GetCommentsResult> {
    await this.initialize();

    const ownerId = -Math.abs(groupId);
    let allComments: ProcessedComment[] = [];
    let currentOffset = offset;
    let hasMore = true;
    let maxIterations = 100; // Защита от бесконечного цикла

    try {
      logger.info('Получение комментариев через VK-IO', {
        groupId,
        postVkId,
        offset
      });

      while (hasMore && maxIterations > 0) {
        maxIterations--;

        const response = await this.vk.api.wall.getComments({
          owner_id: ownerId,
          post_id: postVkId,
          offset: currentOffset,
          count: 100,
          extended: 1, // Включаем профили для получения имен
          fields: ['first_name', 'last_name'],
          sort: 'asc' // Сортировка по времени создания
        });

        const items = response.items || [];
        const profiles = response.profiles || [];

        // Создаем маппинг профилей для получения имен авторов
        const profileMap = profiles.reduce((map, profile) => {
          map[profile.id] = `${profile.first_name} ${profile.last_name}`;
          return map;
        }, {} as Record<number, string>);

        // Преобразуем комментарии в нужный формат
        const processedComments: ProcessedComment[] = items.map(comment => ({
          vk_comment_id: comment.id,
          post_vk_id: postVkId,
          owner_id: ownerId,
          author_id: comment.from_id,
          author_name: profileMap[comment.from_id] || `User ${comment.from_id}`,
          text: comment.text || '',
          date: new Date(comment.date * 1000),
          likes: comment.likes?.count || 0
        }));

        allComments = allComments.concat(processedComments);

        // Проверяем, есть ли еще комментарии
        if (items.length < 100) {
          hasMore = false;
        } else {
          currentOffset += 100;
        }
      }

      if (maxIterations <= 0) {
        logger.warn('Достигнут лимит итераций при получении комментариев', {
          groupId,
          postVkId,
          currentOffset,
          commentsCount: allComments.length
        });
      }

      logger.info('Комментарии успешно получены через VK-IO', {
        groupId,
        postVkId,
        commentsCount: allComments.length
      });

      return {
        comments: allComments,
        hasMore: false // Возвращаем все комментарии за один вызов
      };

    } catch (error) {
      const errorMsg = error instanceof Error ? error.message : String(error);
      logger.error('Ошибка получения комментариев через VK-IO', {
        groupId,
        postVkId,
        error: errorMsg
      });
      throw new Error(`Ошибка получения комментариев для поста ${postVkId}: ${errorMsg}`);
    }
  }

  /**
   * Получает информацию о группах
   * Совместим с существующим интерфейсом
   */
  async getGroupsInfo(groupIds: number[]): Promise<ProcessedGroup[]> {
    await this.initialize();

    if (!groupIds || groupIds.length === 0) {
      return [];
    }

    // Конвертируем в положительные ID для VK API
    const positiveIds = groupIds.map(id => Math.abs(id));

    try {
      logger.info('Получение информации о группах через VK-IO', {
        groupIds: positiveIds
      });

      const response = await this.vk.api.groups.getById({
        group_ids: positiveIds,
        fields: ['name', 'screen_name', 'description', 'photo_50', 'members_count', 'is_closed']
      });

      // VK-IO возвращает массив групп напрямую или обернутый в объект
      logger.info('DEBUG: response от groups.getById', {
        responseType: typeof response,
        isArray: Array.isArray(response),
        responseKeys: response ? Object.keys(response).slice(0, 5) : []
      });

      // Определяем формат ответа и извлекаем массив групп
      let groupsArray: VkGroup[];
      if (Array.isArray(response)) {
        groupsArray = response;
      } else if (response && typeof response === 'object') {
        // Проверяем возможные поля с массивами групп
        const responseObj = response as Record<string, unknown>;
        if (Array.isArray(responseObj.groups)) {
          groupsArray = responseObj.groups as VkGroup[];
        } else if (Array.isArray(responseObj.items)) {
          groupsArray = responseObj.items as VkGroup[];
        } else {
          logger.warn('Некорректный ответ от groups.getById', {
            groupIds,
            responseType: typeof response,
            isArray: Array.isArray(response),
            responseKeys: Object.keys(responseObj)
          });
          return [];
        }
      } else {
        logger.warn('Некорректный ответ от groups.getById', {
          groupIds,
          responseType: typeof response,
          isArray: Array.isArray(response)
        });
        return [];
      }

      logger.info('Найден массив групп', {
        count: groupsArray.length,
        sampleGroup: groupsArray[0]
      });

      const processedGroups: ProcessedGroup[] = groupsArray.map(group => ({
        id: Math.abs(group.id), // Возвращаем положительный ID
        name: group.name,
        screen_name: group.screen_name,
        description: group.description || '',
        photo_50: group.photo_50 || '',
        members_count: group.members_count || 0,
        is_closed: group.is_closed ?? 0
      }));

      logger.info('Информация о группах успешно получена через VK-IO', {
        groupIds: positiveIds,
        count: processedGroups.length
      });

      return processedGroups;

    } catch (error) {
      const errorMsg = error instanceof Error ? error.message : String(error);
      logger.error('Ошибка получения информации о группах через VK-IO', {
        groupIds,
        error: errorMsg
      });
      throw new Error(`Ошибка получения информации о группах: ${errorMsg}`);
    }
  }

  /**
   * Проверяет валидность токена
   */
  async validateToken(): Promise<boolean> {
    try {
      await this.initialize();
      await this.vk.api.account.getInfo({});
      return true;
    } catch (error) {
      logger.error('Валидация токена не прошла', {
        error: error instanceof Error ? error.message : String(error)
      });
      return false;
    }
  }

  /**
   * Получает информацию о пользователе по ID
   */
  async getUserInfo(userId: number): Promise<any> {
    await this.initialize();

    try {
      const response = await this.vk.api.users.get({
        user_ids: [Math.abs(userId).toString()],
        fields: ['first_name_nom', 'last_name_nom', 'photo_50']
      });

      return response;
    } catch (error) {
      const errorMsg = error instanceof Error ? error.message : String(error);
      logger.error('Ошибка получения информации о пользователе через VK-IO', {
        userId,
        error: errorMsg
      });
      throw new Error(`Ошибка получения информации о пользователе ${userId}: ${errorMsg}`);
    }
  }

  /**
   * Возвращает статистику и информацию о состоянии сервиса
   */
  getServiceStats(): {
    isInitialized: boolean;
    apiVersion: string;
    serviceName: string;
    features: string[];
  } {
    return {
      isInitialized: this.isInitialized,
      apiVersion: '5.199',
      serviceName: 'VK-IO Service',
      features: [
        'Автоматический rate limiting',
        'Встроенная обработка ошибок',
        'TypeScript поддержка',
        'DirectAuthorization',
        'Решение IP проблемы'
      ]
    };
  }

  /**
   * Принудительная переинициализация сервиса
   * Полезно при смене токенов или отладке
   */
  async reinitialize(): Promise<void> {
    this.isInitialized = false;
    this.initializationPromise = null;

    logger.info('Принудительная переинициализация VK-IO сервиса');
    await this.initialize();
  }

  /**
   * Резолвит screen_name в ID группы
   * Использует метод utils.resolveScreenName VK API
   */
  async resolveScreenName(screenName: string): Promise<number | null> {
    await this.initialize();

    try {
      logger.info('Резолвинг screen_name в ID', { screenName });

      const response = await this.vk.api.utils.resolveScreenName({
        screen_name: screenName
      });

      // Проверяем, что это группа (type: 'group')
      if (response && response.type === 'group' && response.object_id) {
        logger.info('Screen_name успешно резолвлен', {
          screenName,
          groupId: response.object_id
        });
        return response.object_id;
      }

      logger.warn('Screen_name не является группой или не найден', {
        screenName,
        type: response?.type
      });
      return null;

    } catch (error) {
      const errorMsg = error instanceof Error ? error.message : String(error);
      logger.error('Ошибка резолвинга screen_name через VK-IO', {
        screenName,
        error: errorMsg
      });
      return null;
    }
  }

  /**
   * Резолвит массив screen_names в ID групп
   * Обрабатывает батчами для соблюдения rate limits
   */
  async resolveScreenNames(
    screenNames: string[],
    onProgress?: (current: number, total: number) => void
  ): Promise<Map<string, number>> {
    await this.initialize();

    const results = new Map<string, number>();

    logger.info('Начало резолвинга screen_names', {
      totalScreenNames: screenNames.length
    });

    // Обрабатываем по одному из-за ограничений VK API
    for (let i = 0; i < screenNames.length; i++) {
      const screenName = screenNames[i];
      const groupId = await this.resolveScreenName(screenName);
      if (groupId) {
        results.set(screenName, groupId);
      }

      // Вызываем callback прогресса если он предоставлен
      if (onProgress) {
        onProgress(i + 1, screenNames.length);
      }

      // Небольшая задержка для соблюдения rate limits
      await new Promise(resolve => setTimeout(resolve, 350)); // ~3 запроса в секунду
    }

    logger.info('Резолвинг screen_names завершен', {
      totalScreenNames: screenNames.length,
      resolvedCount: results.size,
      unresolvedCount: screenNames.length - results.size
    });

    return results;
  }

  /**
   * Получает экземпляр VK для прямого доступа к API (для расширенного использования)
   */
  getVkInstance(): VK {
    if (!this.isInitialized) {
      throw new Error('VK-IO сервис не инициализирован. Сначала вызовите любой API метод.');
    }
    return this.vk;
  }
}

// Создаем и экспортируем singleton экземпляр
const vkIoService = new VkIoService();
export default vkIoService;
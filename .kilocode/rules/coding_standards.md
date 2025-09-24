# Общие стандарты кодирования

## Обзор

Эти стандарты определяют лучшие практики кодирования для обеспечения качества, поддерживаемости и эффективности кода в JavaScript/TypeScript проектах. Они основаны на общепринятых принципах разработки (включая Airbnb style guide) и должны применяться во всех частях проекта: backend на Node.js/Express, frontend на Vue.js.

## Читаемость кода

- **Ясные имена**: Использовать описательные имена для переменных, функций, классов и методов в camelCase (для переменных и функций) или PascalCase (для классов), отражающие их назначение.
- **Комментарии**: Добавлять JSDoc-комментарии для функций и методов с описанием параметров, возвращаемых значений и примеров. Inline-комментарии для сложной логики.
- **Форматирование**: Соблюдать единообразное форматирование с помощью ESLint и Prettier: 2 пробела для отступов, пробелы вокруг операторов, максимум 100 символов в строке.
- **Структурирование**: Разделять код на логические блоки с использованием пустых строк. В Vue-компонентах — четкое разделение template, script, style.
- **Избегать магических чисел**: Заменять константы на именованные переменные или const в UPPER_SNAKE_CASE.

Пример для Node.js (Express controller):
```javascript
/**
 * Получает комментарии из VK API.
 * @param {Object} req - HTTP-запрос
 * @param {Object} res - HTTP-ответ
 * @returns {Promise<void>}
 */
async function getComments(req, res) {
  try {
    const { ownerId, postId } = req.body;
    const comments = await vkService.fetchComments(ownerId, postId);
    res.json({ comments });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
}
```

Пример для Vue компонента:
```vue
<script setup>
import { ref } from 'vue';
import { useCommentsStore } from '@/stores/comments.js';

/**
 * Компонент списка комментариев.
 */
const commentsStore = useCommentsStore();
const comments = ref([]);
</script>
```

## Написание тестов

- **Unit-тесты**: Писать тесты для каждой функции и метода с использованием Jest (backend) или Vitest (frontend), проверяя их корректность с mocks.
- **Интеграционные тесты**: Тестировать взаимодействие между компонентами, например, API-эндпоинты с supertest.
- **Фреймворки**: Jest для Node.js/Express, Vitest для Vue.js/Pinia.
- **Независимость**: Тесты должны быть независимыми, использовать mocks для внешних зависимостей (jest.mock).
- **Покрытие**: Стремиться к высокому покрытию кода тестами (минимум 80%), измерять с помощью nyc или встроенных инструментов.
- **TDD**: Применять Test-Driven Development для новых функций.

Пример Jest теста для сервиса:
```javascript
import { fetchComments } from '../services/vkService.js';

jest.mock('../repositories/vkApi.js');

test('fetchComments возвращает комментарии', async () => {
  const mockComments = [{ text: 'Test' }];
  vkApi.getComments.mockResolvedValue(mockComments);
  const result = await fetchComments(1, 1);
  expect(result).toEqual(mockComments);
});
```

## Объяснение рассуждений

- **JSDoc**: Добавлять JSDoc к функциям, классам и модулям с описанием параметров (@param), возвращаемых значений (@returns) и примеров (@example).
- **Комментарии в коде**: Объяснять сложные алгоритмы и решения с помощью // или /* */ inline-комментариев.
- **Документация**: Вести актуальную документацию проекта, включая README.md и API-документацию (Swagger для Express).
- **Обоснование решений**: В коммит-сообщениях и pull request'ах объяснять причины изменений на английском.

## Использование популярных библиотек

- **Стандартные модули Node.js**: Предпочитать встроенные модули (fs, path) перед сторонними.
- **Популярные пакеты**: Использовать проверенные библиотеки, такие как axios (HTTP), bullmq (очереди), express (routing), vue/pinia (frontend), pg/sequelize (PostgreSQL).
- **Управление зависимостями**: Использовать npm или yarn (bun для быстрого управления) для установки и package.json/lock-файлов.
- **Обновления**: Регулярно обновлять библиотеки с помощью npm update для исправления уязвимостей и улучшения производительности (использовать npm audit).
- **Лицензии**: Проверять совместимость лицензий используемых библиотек (MIT, Apache и т.д.).

Пример в package.json:
```json
{
  "dependencies": {
    "express": "^4.18.0",
    "axios": "^1.0.0",
    "bullmq": "^4.0.0"
  }
}
```

## Другие лучшие практики

- **DRY (Don't Repeat Yourself)**: Избегать дублирования кода путем создания переиспользуемых функций, сервисов и компонентов (например, общие утилиты в utils/).
- **SOLID принципы**: Соблюдать принципы объектно-ориентированного дизайна: Single Responsibility (отдельные controllers/services), Open-Closed и т.д.
- **Обработка ошибок**: Использовать try-catch для асинхронных операций (async/await), throw new Error() для кастомных ошибок.
- **Безопасность**: Валидировать входные данные с joi или express-validator, избегать SQL-инъекций (использовать parameterized queries в pg), хранить секреты в .env (VK_TOKEN, DB_URL), настраивать CORS в Express.
- **Производительность**: Оптимизировать код для эффективности, использовать async/await вместо callbacks, профилировать с clinic.js.
- **Версионирование**: Использовать семантическое версионирование для релизов (semver в package.json).
- **Code Review**: Проводить ревью кода перед слиянием изменений с помощью pull requests.
- **CI/CD**: Настраивать непрерывную интеграцию и доставку с GitHub Actions для автоматизации тестов, build и deploy (docker-compose).
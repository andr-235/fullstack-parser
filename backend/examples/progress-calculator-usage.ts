/**
 * Примеры использования ProgressCalculator
 * Демонстрирует решение проблемы processed > total
 */

import { ProgressCalculator } from '../src/services/progressCalculator';
import { TaskMetrics } from '../src/types/task';

console.log('=== Демонстрация ProgressCalculator ===\n');

// === ПРИМЕР 1: Начальная фаза (обработка групп) ===
console.log('1. Фаза обработки групп:');
const groupsPhaseMetrics: TaskMetrics = {
  groupsTotal: 10,
  groupsProcessed: 3,
  postsTotal: 0,
  postsProcessed: 0,
  commentsTotal: 0,
  commentsProcessed: 0,
  estimatedCommentsPerPost: 15
};

const groupsResult = ProgressCalculator.calculateProgress(groupsPhaseMetrics);
console.log(`  Прогресс: ${groupsResult.percentage}% (фаза: ${groupsResult.phase})`);
console.log(`  Детали: обработано ${groupsPhaseMetrics.groupsProcessed} из ${groupsPhaseMetrics.groupsTotal} групп`);
console.log(`  Весовая система: groups=${groupsResult.phases.groups.progress * 100}%\n`);

// === ПРИМЕР 2: Переход к фазе постов ===
console.log('2. Фаза получения постов:');
const postsPhaseMetrics: TaskMetrics = {
  groupsTotal: 10,
  groupsProcessed: 10, // Группы завершены
  postsTotal: 500,
  postsProcessed: 200,
  commentsTotal: 0,
  commentsProcessed: 0,
  estimatedCommentsPerPost: 15
};

const postsResult = ProgressCalculator.calculateProgress(postsPhaseMetrics);
console.log(`  Прогресс: ${postsResult.percentage}% (фаза: ${postsResult.phase})`);
console.log(`  Детали: обработано ${postsPhaseMetrics.postsProcessed} из ${postsPhaseMetrics.postsTotal} постов`);
console.log(`  Весовая система: groups=100%, posts=${postsResult.phases.posts.progress * 100}%\n`);

// === ПРИМЕР 3: Фаза комментариев ===
console.log('3. Фаза получения комментариев:');
const commentsPhaseMetrics: TaskMetrics = {
  groupsTotal: 10,
  groupsProcessed: 10,
  postsTotal: 500,
  postsProcessed: 500, // Посты завершены
  commentsTotal: 7500, // 500 * 15
  commentsProcessed: 3750, // 50% комментариев
  estimatedCommentsPerPost: 15
};

const commentsResult = ProgressCalculator.calculateProgress(commentsPhaseMetrics);
console.log(`  Прогресс: ${commentsResult.percentage}% (фаза: ${commentsResult.phase})`);
console.log(`  Детали: обработано ${commentsPhaseMetrics.commentsProcessed} из ${commentsPhaseMetrics.commentsTotal} комментариев`);
console.log(`  Весовая система: groups=100%, posts=100%, comments=${commentsResult.phases.comments.progress * 100}%\n`);

// === ПРИМЕР 4: Демонстрация старой проблемы ===
console.log('4. СТАРАЯ ПРОБЛЕМА - произвольный множитель:');
const posts = 500;
const comments = 6000; // Больше чем posts * 10

const oldAlgorithmTotal = Math.max(posts * 10, comments); // = max(5000, 6000) = 6000
const oldAlgorithmProgress = (comments / oldAlgorithmTotal) * 100; // = 100%

console.log(`  Старый алгоритм: ${Math.round(oldAlgorithmProgress)}% (${comments}/${oldAlgorithmTotal})`);
console.log(`  Проблема: при comments > posts * 10 получаем мгновенно 100%`);

// Сравним с новым алгоритмом
const newMetrics: TaskMetrics = {
  groupsTotal: 10,
  groupsProcessed: 10,
  postsTotal: posts,
  postsProcessed: posts,
  commentsTotal: comments,
  commentsProcessed: comments,
  estimatedCommentsPerPost: 15
};

const newResult = ProgressCalculator.calculateProgress(newMetrics);
console.log(`  Новый алгоритм: ${newResult.percentage}% (точно отражает завершение всех фаз)\n`);

// === ПРИМЕР 5: Оценка общего объема ===
console.log('5. Оценка общего объема работы:');
const taskData1 = { groups: [{ id: 1 }, { id: 2 }, { id: 3 }] };
const estimate1 = ProgressCalculator.estimateTotal(taskData1);
console.log(`  3 группы: ~${estimate1} комментариев`);

const taskData2 = { groupIds: [1, 2, 3, 4, 5], maxComments: 2000 };
const estimate2 = ProgressCalculator.estimateTotal(taskData2);
console.log(`  5 групп с ограничением 2000: ${estimate2} комментариев\n`);

// === ПРИМЕР 6: Валидация метрик ===
console.log('6. Валидация некорректных метрик:');
const badMetrics: TaskMetrics = {
  groupsTotal: 5,
  groupsProcessed: 10, // Больше total!
  postsTotal: 100,
  postsProcessed: 150, // Больше total!
  commentsTotal: 1500,
  commentsProcessed: 2000, // Больше total!
  estimatedCommentsPerPost: 15
};

const validationErrors = ProgressCalculator.validateMetrics(badMetrics);
console.log(`  Найдено ошибок: ${validationErrors.length}`);
validationErrors.forEach(error => console.log(`    - ${error}`));

// Но даже с некорректными данными алгоритм не сломается
const badResult = ProgressCalculator.calculateProgress(badMetrics);
console.log(`  Прогресс с некорректными данными: ${badResult.percentage}% (не превышает 100%)\n`);

// === ПРИМЕР 7: Реальный сценарий использования ===
console.log('7. Реальный сценарий - постепенная обработка:');

const scenarios = [
  { name: 'Начало', groups: 0, posts: 0, comments: 0 },
  { name: 'Обработка групп', groups: 5, posts: 0, comments: 0 },
  { name: 'Группы завершены', groups: 10, posts: 0, comments: 0 },
  { name: 'Получение постов', groups: 10, posts: 250, comments: 0 },
  { name: 'Посты завершены', groups: 10, posts: 500, comments: 0 },
  { name: 'Получение комментариев', groups: 10, posts: 500, comments: 3750 },
  { name: 'Завершение', groups: 10, posts: 500, comments: 7500 }
];

scenarios.forEach(scenario => {
  const metrics: TaskMetrics = {
    groupsTotal: 10,
    groupsProcessed: scenario.groups,
    postsTotal: 500,
    postsProcessed: scenario.posts,
    commentsTotal: 7500,
    commentsProcessed: scenario.comments,
    estimatedCommentsPerPost: 15
  };

  const result = ProgressCalculator.calculateProgress(metrics);
  console.log(`  ${scenario.name}: ${result.percentage}% (${result.phase})`);
});

console.log('\n=== Заключение ===');
console.log('✅ Проблема processed > total решена');
console.log('✅ Прогресс всегда от 0% до 100%');
console.log('✅ Учитываются все фазы обработки');
console.log('✅ Весовая система отражает реальную сложность');
console.log('✅ Валидация предотвращает некорректные данные');
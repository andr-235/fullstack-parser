// Тестовый файл для проверки API подключения
// Запустите: node test-api.js

const API_BASE = 'http://localhost:8000/api/v1'

async function testAPI() {
  console.log('🧪 Тестирование API подключения...\n')

  try {
    // Тест 1: Basic Health check
    console.log('1. Проверка basic health check...')
    const healthResponse = await fetch(`${API_BASE}/health`)
    if (healthResponse.ok) {
      const healthData = await healthResponse.json()
      console.log('✅ Basic health check:', healthData)
    } else {
      console.log('❌ Basic health check: FAILED')
    }

    // Тест 2: Detailed Health check
    console.log('\n2. Проверка detailed health check...')
    const detailedHealthResponse = await fetch(`${API_BASE}/health/detailed`)
    if (detailedHealthResponse.ok) {
      console.log('✅ Detailed health check: OK')
    } else {
      console.log('❌ Detailed health check: FAILED')
    }

    // Тест 3: Получение групп
    console.log('\n3. Получение групп...')
    const groupsResponse = await fetch(`${API_BASE}/groups`)
    if (groupsResponse.ok) {
      const groups = await groupsResponse.json()
      console.log(`✅ Группы получены: ${groups.items?.length || 0} элементов`)
    } else {
      console.log('❌ Получение групп: FAILED')
    }

    // Тест 4: Получение ключевых слов
    console.log('\n4. Получение ключевых слов...')
    const keywordsResponse = await fetch(`${API_BASE}/keywords`)
    if (keywordsResponse.ok) {
      const keywords = await keywordsResponse.json()
      console.log(`✅ Ключевые слова получены: ${keywords.items?.length || 0} элементов`)
    } else {
      console.log('❌ Получение ключевых слов: FAILED')
    }

    // Тест 5: Получение комментариев через parser
    console.log('\n5. Получение комментариев через parser...')
    const commentsResponse = await fetch(`${API_BASE}/parser/comments?size=1`)
    if (commentsResponse.ok) {
      const comments = await commentsResponse.json()
      console.log(`✅ Комментарии получены: ${comments.items?.length || 0} элементов`)
    } else {
      console.log('❌ Получение комментариев: FAILED')
    }

    // Тест 6: Состояние парсера
    console.log('\n6. Получение состояния парсера...')
    const parserStateResponse = await fetch(`${API_BASE}/parser/state`)
    if (parserStateResponse.ok) {
      const parserState = await parserStateResponse.json()
      console.log('✅ Состояние парсера:', parserState)
    } else {
      console.log('❌ Получение состояния парсера: FAILED')
    }

    // Тест 7: Статистика парсера
    console.log('\n7. Получение статистики парсера...')
    const parserStatsResponse = await fetch(`${API_BASE}/parser/stats`)
    if (parserStatsResponse.ok) {
      const parserStats = await parserStatsResponse.json()
      console.log('✅ Статистика парсера:', parserStats)
    } else {
      console.log('❌ Получение статистики парсера: FAILED')
    }

    // Тест 8: Системный статус
    console.log('\n8. Получение системного статуса...')
    const systemStatusResponse = await fetch(`${API_BASE}/health/status`)
    if (systemStatusResponse.ok) {
      const systemStatus = await systemStatusResponse.json()
      console.log('✅ Системный статус:', systemStatus)
    } else {
      console.log('❌ Получение системного статуса: FAILED')
    }
  } catch (error) {
    console.error('❌ Ошибка подключения:', error.message)
    console.log('\n💡 Возможные причины:')
    console.log('1. Backend сервер не запущен на порту 8000')
    console.log('2. Неправильная конфигурация Docker')
    console.log('3. Блокировка firewall')
    console.log('4. CORS политика блокирует запросы')
  }

  console.log('\n🏁 Тестирование завершено')
}

// Запуск теста
testAPI()

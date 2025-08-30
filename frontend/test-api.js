// Тестовый файл для проверки API подключения
// Запустите: node test-api.js

const API_BASE = 'http://localhost/api/v1'

async function testAPI() {
  console.log('🧪 Тестирование API подключения...\n')

  try {
    // Тест 1: Health check
    console.log('1. Проверка health check...')
    const healthResponse = await fetch(`${API_BASE}/health/`)
    if (healthResponse.ok) {
      console.log('✅ Health check: OK')
    } else {
      console.log('❌ Health check: FAILED')
    }

    // Тест 2: Получение групп
    console.log('\n2. Получение групп...')
    const groupsResponse = await fetch(`${API_BASE}/groups`)
    if (groupsResponse.ok) {
      const groups = await groupsResponse.json()
      console.log(`✅ Группы получены: ${groups.items?.length || 0} элементов`)
    } else {
      console.log('❌ Получение групп: FAILED')
    }

    // Тест 3: Получение ключевых слов
    console.log('\n3. Получение ключевых слов...')
    const keywordsResponse = await fetch(`${API_BASE}/keywords`)
    if (keywordsResponse.ok) {
      const keywords = await keywordsResponse.json()
      console.log(
        `✅ Ключевые слова получены: ${keywords.items?.length || 0} элементов`
      )
    } else {
      console.log('❌ Получение ключевых слов: FAILED')
    }

    // Тест 4: Получение комментариев
    console.log('\n4. Получение комментариев...')
    const commentsResponse = await fetch(`${API_BASE}/comments?size=1`)
    if (commentsResponse.ok) {
      const comments = await commentsResponse.json()
      console.log(
        `✅ Комментарии получены: ${comments.items?.length || 0} элементов`
      )
    } else {
      console.log('❌ Получение комментариев: FAILED')
    }

    // Тест 5: Глобальная статистика
    console.log('\n5. Глобальная статистика...')
    const statsResponse = await fetch(`${API_BASE}/stats/global`)
    if (statsResponse.ok) {
      console.log('✅ Глобальная статистика: OK')
    } else {
      console.log('❌ Глобальная статистика: FAILED')
    }

    // Тест 6: Статистика дашборда
    console.log('\n6. Статистика дашборда...')
    const dashboardResponse = await fetch(`${API_BASE}/stats/dashboard`)
    if (dashboardResponse.ok) {
      console.log('✅ Статистика дашборда: OK')
    } else {
      console.log('❌ Статистика дашборда: FAILED')
    }
  } catch (error) {
    console.error('❌ Ошибка подключения:', error.message)
    console.log('\n💡 Возможные причины:')
    console.log('1. Nginx не запущен')
    console.log('2. Backend сервер не запущен')
    console.log('3. Неправильная конфигурация Docker')
    console.log('4. Блокировка firewall')
  }

  console.log('\n🏁 Тестирование завершено')
}

// Запуск теста
testAPI()

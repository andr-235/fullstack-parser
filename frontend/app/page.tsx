export default function Home() {
  return (
    <div className="grid grid-rows-[20px_1fr_20px] items-center justify-items-center min-h-screen p-8 pb-20 gap-16 sm:p-20 font-[family-name:var(--font-inter)]">
      <main className="flex flex-col gap-[32px] row-start-2 items-center sm:items-start">
        <div className="flex items-center gap-4">
          <div className="text-6xl">📊</div>
          <div>
            <h1 className="text-4xl font-bold text-blue-600 dark:text-blue-400">
              VK Comments Parser
            </h1>
            <p className="text-lg text-gray-600 dark:text-gray-300 mt-2">
              Парсинг и анализ комментариев ВКонтакте
            </p>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 w-full max-w-4xl">
          <div className="p-6 bg-white dark:bg-gray-800 rounded-lg shadow-md border border-gray-200 dark:border-gray-700">
            <div className="text-3xl mb-3">🔍</div>
            <h3 className="text-xl font-semibold mb-2">
              Поиск по ключевым словам
            </h3>
            <p className="text-gray-600 dark:text-gray-300">
              Настраиваемый поиск комментариев по заданным ключевым словам
            </p>
          </div>

          <div className="p-6 bg-white dark:bg-gray-800 rounded-lg shadow-md border border-gray-200 dark:border-gray-700">
            <div className="text-3xl mb-3">📈</div>
            <h3 className="text-xl font-semibold mb-2">Аналитика</h3>
            <p className="text-gray-600 dark:text-gray-300">
              Подробная статистика и визуализация найденных данных
            </p>
          </div>

          <div className="p-6 bg-white dark:bg-gray-800 rounded-lg shadow-md border border-gray-200 dark:border-gray-700">
            <div className="text-3xl mb-3">⚡</div>
            <h3 className="text-xl font-semibold mb-2">
              Высокая производительность
            </h3>
            <p className="text-gray-600 dark:text-gray-300">
              Асинхронная обработка и кэширование для быстрого анализа
            </p>
          </div>
        </div>

        <div className="flex gap-4 items-center flex-col sm:flex-row">
          <button className="rounded-lg border border-solid border-transparent transition-colors flex items-center justify-center bg-blue-600 text-white gap-2 hover:bg-blue-700 font-medium text-sm sm:text-base h-10 sm:h-12 px-6 sm:px-8">
            Начать парсинг
          </button>
          <button className="rounded-lg border border-solid border-gray-300 dark:border-gray-600 transition-colors flex items-center justify-center hover:bg-gray-50 dark:hover:bg-gray-800 font-medium text-sm sm:text-base h-10 sm:h-12 px-6 sm:px-8">
            Посмотреть документацию
          </button>
        </div>
      </main>

      <footer className="row-start-3 flex gap-[24px] flex-wrap items-center justify-center text-sm text-gray-500 dark:text-gray-400">
        <span>Built with FastAPI + Next.js</span>
        <span>•</span>
        <span>Docker Ready</span>
        <span>•</span>
        <span>Open Source</span>
      </footer>
    </div>
  )
}

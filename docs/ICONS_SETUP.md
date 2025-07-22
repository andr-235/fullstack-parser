# Настройка иконок приложения

## Обзор

Иконки приложения настроены согласно FSD (Feature-Sliced Design) архитектуре и размещены в соответствующих слоях проекта.

## Структура файлов

### Статические файлы

```
frontend/public/
├── logo.svg                 # Основная SVG иконка (рекомендуется)
├── favicon.svg              # SVG favicon для браузеров
├── favicon.ico              # Основная иконка для браузеров (fallback)
├── favicon-16x16.png        # Маленькая иконка (16x16, fallback)
├── favicon-32x32.png        # Средняя иконка (32x32, fallback)
├── android-chrome-192x192.png # Иконка для Android (192x192)
├── android-chrome-512x512.png # Иконка для Android (512x512)
├── apple-touch-icon.png     # Иконка для iOS (180x180)
└── site.webmanifest        # Манифест PWA
```

### Компоненты и хуки

```
frontend/shared/
├── ui/
│   └── app-icon.tsx        # Компонент AppIcon
├── hooks/
│   └── use-app-icon.ts     # Хук для работы с иконками
└── types/
    └── icon.ts             # Типы для иконок
```

## Использование

### Компонент AppIcon

```tsx
import { AppIcon } from '@/shared/ui'

// Базовое использование
<AppIcon />

// С разными размерами
<AppIcon size="sm" />   // 16x16
<AppIcon size="md" />   // 32x32
<AppIcon size="lg" />   // 192x192
<AppIcon size="xl" />   // 512x512

// С кастомными стилями
<AppIcon size="md" className="w-8 h-8 rounded-lg" />

// С приоритетной загрузкой
<AppIcon size="lg" priority />
```

### Хук useAppIcon

```tsx
import { useAppIcon } from "@/shared/hooks";

function MyComponent() {
  const { icons, getIconBySize, getIconBySizes } = useAppIcon();

  // Получить все иконки
  console.log(icons);

  // Получить иконку по размеру
  const icon32 = getIconBySize(32);

  // Получить иконку по размерам
  const icon192 = getIconBySizes("192x192");

  return (
    <div>
      {icons.map((icon) => (
        <img key={icon.src} src={icon.src} alt="App icon" />
      ))}
    </div>
  );
}
```

## SVG Иконки

### Преимущества SVG

- **Масштабируемость**: Иконки остаются четкими в любом размере
- **Малый размер**: SVG файлы обычно меньше PNG
- **Качество**: Отсутствие пикселизации при увеличении
- **Гибкость**: Легко изменять цвета и стили через CSS

### Структура SVG

Основная иконка `logo.svg` содержит:

- Синий градиентный фон (`#3B82F6` → `#1D4ED8`)
- Белые буквы "Bk" в центре
- Скругленные углы (6px)
- Размер viewBox: 32x32

### Использование SVG

Компонент `AppIcon` автоматически использует SVG для размеров `sm` и `md`:

```tsx
// Использует /logo.svg
<AppIcon size="sm" />
<AppIcon size="md" />

// Использует PNG для больших размеров
<AppIcon size="lg" />
<AppIcon size="xl" />
```

## Метаданные

### Next.js Layout

В `frontend/app/layout.tsx` настроены метаданные для иконок:

```tsx
export const metadata: Metadata = {
  title: "VK Comments Parser",
  description: "Fullstack приложение для парсинга комментариев ВКонтакте",
  icons: {
    icon: [
      { url: "/favicon.svg", sizes: "any", type: "image/svg+xml" },
      { url: "/favicon-16x16.png", sizes: "16x16", type: "image/png" },
      { url: "/favicon-32x32.png", sizes: "32x32", type: "image/png" },
    ],
    shortcut: "/favicon.ico",
    apple: "/apple-touch-icon.png",
  },
  manifest: "/site.webmanifest",
  themeColor: "#0f172a", // slate-900
  viewport: "width=device-width, initial-scale=1",
  robots: "index, follow",
};
```

### PWA Манифест

Файл `frontend/public/site.webmanifest` содержит настройки для PWA:

```json
{
  "name": "ВК Парсер",
  "short_name": "ВК Парсер",
  "description": "Fullstack приложение для парсинга комментариев ВКонтакте",
  "icons": [
    {
      "src": "/android-chrome-192x192.png",
      "sizes": "192x192",
      "type": "image/png"
    },
    {
      "src": "/android-chrome-512x512.png",
      "sizes": "512x512",
      "type": "image/png"
    }
  ],
  "theme_color": "#0f172a",
  "background_color": "#0f172a",
  "display": "standalone",
  "start_url": "/",
  "scope": "/"
}
```

## Типы

```tsx
interface AppIconInfo {
  src: string;
  sizes: string;
  type: string;
}

type AppIconSize = "sm" | "md" | "lg" | "xl";

interface AppIconProps {
  size?: AppIconSize;
  className?: string;
  priority?: boolean;
}

interface AppManifest {
  name: string;
  short_name: string;
  description: string;
  icons: AppIconInfo[];
  theme_color: string;
  background_color: string;
  display: string;
  start_url: string;
  scope: string;
}
```

## Примеры использования

### В Header компоненте

```tsx
import { AppIcon } from "@/shared/ui";

export function Header() {
  return (
    <header>
      <div className="flex items-center gap-2">
        <AppIcon size="sm" className="w-6 h-6" />
        <span className="text-sm font-medium text-slate-200">ВК Парсер</span>
      </div>
    </header>
  );
}
```

### В Loading компоненте

```tsx
import { AppIcon } from "@/shared/ui";

export function LoadingScreen() {
  return (
    <div className="flex items-center justify-center h-screen">
      <div className="flex flex-col items-center gap-4">
        <AppIcon size="lg" className="animate-pulse" />
        <span className="text-lg font-medium">Загрузка...</span>
      </div>
    </div>
  );
}
```

## Поддерживаемые браузеры

- **Chrome/Edge**: favicon.ico, favicon-16x16.png, favicon-32x32.png
- **Firefox**: favicon.ico, favicon-32x32.png
- **Safari**: apple-touch-icon.png
- **Android**: android-chrome-192x192.png, android-chrome-512x512.png
- **iOS**: apple-touch-icon.png

## Обновление иконок

1. Замените файлы в `frontend/public/`
2. Обновите `site.webmanifest` если изменились размеры
3. Пересоберите frontend: `docker-compose build frontend`
4. Перезапустите: `docker-compose up -d frontend`

## Важные замечания

### Dockerfile

В `frontend/Dockerfile` добавлена строка для копирования папки `public`:

```dockerfile
# Копируем папку public с иконками
COPY --from=builder /app/public ./public
```

Это необходимо для того, чтобы статические файлы (иконки, favicon) были доступны в production контейнере.

## FSD Архитектура

Иконки организованы согласно FSD принципам:

- **shared/ui**: Переиспользуемый компонент AppIcon
- **shared/hooks**: Хук useAppIcon для работы с иконками
- **shared/types**: Типы для иконок
- **public**: Статические файлы иконок

Это обеспечивает:

- Переиспользуемость компонентов
- Типобезопасность
- Централизованное управление
- Легкость тестирования

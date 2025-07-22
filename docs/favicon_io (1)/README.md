# Исходные иконки приложения

Эта папка содержит исходные файлы иконок для приложения VK Parser.

## Содержимое

- `favicon.ico` - Основная иконка для браузеров (15KB)
- `favicon-16x16.png` - Маленькая иконка (519B)
- `favicon-32x32.png` - Средняя иконка (992B)
- `android-chrome-192x192.png` - Иконка для Android (7.1KB)
- `android-chrome-512x512.png` - Иконка для Android (21KB)
- `apple-touch-icon.png` - Иконка для iOS (6.4KB)
- `site.webmanifest` - Манифест PWA (263B)
- `about.txt` - Информация о шрифте

## Использование

Эти файлы автоматически копируются в `frontend/public/` при настройке проекта.

## Шрифт

Иконки созданы с использованием шрифта **League Spartan**:

- Источник: https://fonts.gstatic.com/s/leaguespartan/v14/kJEnBuEW6A0lliaV_m88ja5Twtx8BWhtkDVmjZvM_oTpBMdcFguczA.ttf

## Обновление

При изменении иконок:

1. Замените файлы в этой папке
2. Скопируйте в `frontend/public/`: `cp docs/favicon_io\ \(1\)/* frontend/public/`
3. Обновите `site.webmanifest` если изменились размеры
4. Пересоберите frontend: `docker-compose build frontend`
5. Перезапустите: `docker-compose up -d frontend`

## Размеры

- **16x16**: favicon-16x16.png
- **32x32**: favicon-32x32.png
- **180x180**: apple-touch-icon.png
- **192x192**: android-chrome-192x192.png
- **512x512**: android-chrome-512x512.png

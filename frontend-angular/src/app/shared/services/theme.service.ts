import { Injectable, signal, computed, effect } from '@angular/core';

export type Theme = 'light' | 'dark' | 'auto';

@Injectable({
  providedIn: 'root',
})
export class ThemeService {
  private readonly _theme = signal<Theme>('light');
  private readonly _systemTheme = signal<'light' | 'dark'>('light');
  private readonly _isInitialized = signal(false);

  readonly theme = this._theme.asReadonly();
  readonly systemTheme = this._systemTheme.asReadonly();
  readonly isInitialized = this._isInitialized.asReadonly();

  readonly currentTheme = computed(() => {
    const theme = this._theme();
    if (theme === 'auto') {
      return this._systemTheme();
    }
    return theme;
  });

  constructor() {
    // Применяем тему сразу при инициализации для предотвращения мерцания
    this.applyThemeImmediately();

    // Инициализация системной темы
    this.initializeSystemTheme();

    // Эффект для применения темы к документу
    effect(() => {
      const theme = this.currentTheme();
      if (this._isInitialized()) {
        this.applyTheme(theme);
      }
    });
  }

  setTheme(theme: Theme): void {
    this._theme.set(theme);
    try {
      localStorage.setItem('theme', theme);
    } catch (error) {
      console.warn('Failed to save theme to localStorage:', error);
    }
  }

  toggleTheme(): void {
    const currentTheme = this._theme();
    const newTheme: Theme = currentTheme === 'light' ? 'dark' : 'light';
    this.setTheme(newTheme);
  }

  private applyThemeImmediately(): void {
    // Применяем тему до инициализации для предотвращения мерцания
    const savedTheme = localStorage.getItem('theme') as Theme;
    const initialTheme = savedTheme || 'light';

    if (initialTheme === 'auto') {
      const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
      const systemTheme = mediaQuery.matches ? 'dark' : 'light';
      this.applyTheme(systemTheme);
    } else {
      this.applyTheme(initialTheme as 'light' | 'dark');
    }
  }

  private initializeSystemTheme(): void {
    try {
      // Получаем сохраненную тему из localStorage
      const savedTheme = localStorage.getItem('theme') as Theme;
      if (savedTheme) {
        this._theme.set(savedTheme);
      }

      // Определяем системную тему
      const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
      this._systemTheme.set(mediaQuery.matches ? 'dark' : 'light');

      // Слушаем изменения системной темы
      mediaQuery.addEventListener('change', (e) => {
        this._systemTheme.set(e.matches ? 'dark' : 'light');
      });

      // Отмечаем как инициализированную
      this._isInitialized.set(true);
    } catch (error) {
      console.error('Failed to initialize theme service:', error);
      // Устанавливаем дефолтную тему в случае ошибки
      this._theme.set('light');
      this._isInitialized.set(true);
    }
  }

  private applyTheme(theme: 'light' | 'dark'): void {
    const html = document.documentElement;

    if (theme === 'dark') {
      html.classList.add('dark-theme');
      html.classList.remove('light-theme');
      html.setAttribute('data-theme', 'dark');
    } else {
      html.classList.add('light-theme');
      html.classList.remove('dark-theme');
      html.setAttribute('data-theme', 'light');
    }
  }
}

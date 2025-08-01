import { Component, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatMenuModule } from '@angular/material/menu';
import { MatTooltipModule } from '@angular/material/tooltip';
import { MatRippleModule } from '@angular/material/core';
import { ThemeService, type Theme } from '../../services/theme.service';

@Component({
  selector: 'app-theme-toggle',
  standalone: true,
  imports: [
    CommonModule,
    MatButtonModule,
    MatIconModule,
    MatMenuModule,
    MatTooltipModule,
    MatRippleModule,
  ],
  template: `
    <button
      mat-icon-button
      [matMenuTriggerFor]="themeMenu"
      [matTooltip]="'Toggle theme'"
      aria-label="Toggle theme"
      class="theme-toggle-btn"
    >
      <mat-icon class="theme-icon">{{ getThemeIcon() }}</mat-icon>
    </button>

    <mat-menu #themeMenu="matMenu" class="theme-menu">
      <button
        mat-menu-item
        (click)="setTheme('light')"
        [class.active]="theme() === 'light'"
      >
        <mat-icon>light_mode</mat-icon>
        <span>Light</span>
      </button>
      <button
        mat-menu-item
        (click)="setTheme('dark')"
        [class.active]="theme() === 'dark'"
      >
        <mat-icon>dark_mode</mat-icon>
        <span>Dark</span>
      </button>
      <button
        mat-menu-item
        (click)="setTheme('auto')"
        [class.active]="theme() === 'auto'"
      >
        <mat-icon>brightness_auto</mat-icon>
        <span>Auto</span>
        <span class="system-theme">({{ systemTheme() }})</span>
      </button>
    </mat-menu>
  `,
  styles: [
    `
      .theme-toggle-btn {
        transition: transform 0.2s ease;
      }

      .theme-toggle-btn:hover {
        transform: scale(1.1);
      }

      .theme-icon {
        transition: transform 0.3s ease;
      }

      .theme-toggle-btn:hover .theme-icon {
        transform: rotate(180deg);
      }

      .theme-menu {
        min-width: 150px;
      }

      .theme-menu button {
        display: flex;
        align-items: center;
        gap: 12px;
      }

      .theme-menu button.active {
        background-color: var(--app-selected);
        color: var(--app-primary);
      }

      .system-theme {
        margin-left: auto;
        font-size: 0.8em;
        opacity: 0.7;
      }

      /* Анимация для иконок */
      mat-icon {
        transition: all 0.2s ease;
      }

      .theme-menu button:hover mat-icon {
        transform: scale(1.1);
      }
    `,
  ],
})
export class ThemeToggleComponent {
  private themeService = inject(ThemeService);

  readonly theme = this.themeService.theme;
  readonly systemTheme = this.themeService.systemTheme;

  getThemeIcon(): string {
    const currentTheme = this.themeService.currentTheme();
    switch (currentTheme) {
      case 'dark':
        return 'dark_mode';
      case 'light':
        return 'light_mode';
      default:
        return 'brightness_auto';
    }
  }

  setTheme(theme: Theme): void {
    this.themeService.setTheme(theme);
  }
}

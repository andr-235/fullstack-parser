import {
  Component,
  OnInit,
  ChangeDetectionStrategy,
  inject,
  signal,
} from '@angular/core';
import { CommonModule } from '@angular/common';
import {
  ReactiveFormsModule,
  FormControl,
  FormGroup,
  Validators,
} from '@angular/forms';
import { MatCardModule } from '@angular/material/card';
import { MatButtonModule } from '@angular/material/button';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatIconModule } from '@angular/material/icon';
import { MatSnackBar } from '@angular/material/snack-bar';
import { MatSelectModule } from '@angular/material/select';
import { MatExpansionModule } from '@angular/material/expansion';
import { MatSlideToggleModule } from '@angular/material/slide-toggle';
import { MatSliderModule } from '@angular/material/slider';
import { MatDividerModule } from '@angular/material/divider';
import { MatChipsModule } from '@angular/material/chips';
import { SettingsService } from '../../core/services/settings.service';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';

@Component({
  selector: 'app-settings',
  standalone: true,
  changeDetection: ChangeDetectionStrategy.OnPush,
  imports: [
    CommonModule,
    ReactiveFormsModule,
    MatCardModule,
    MatButtonModule,
    MatFormFieldModule,
    MatInputModule,
    MatIconModule,
    MatSelectModule,
    MatExpansionModule,
    MatSlideToggleModule,
    MatSliderModule,
    MatDividerModule,
    MatChipsModule,
    MatProgressSpinnerModule,
  ],
  templateUrl: './settings.component.html',
  styleUrls: ['./settings.component.scss'],
})
export class SettingsComponent implements OnInit {
  generalForm!: FormGroup;
  parserForm!: FormGroup;
  notificationForm!: FormGroup;
  securityForm!: FormGroup;
  appearanceForm!: FormGroup;

  // Используем signals для лучшей производительности
  isLoading = signal(false);
  isSaving = signal(false);

  // Геттеры для template
  get isLoadingData(): boolean {
    return this.isLoading();
  }

  get isSavingData(): boolean {
    return this.isSaving();
  }

  // Используем inject() вместо constructor injection
  private settingsService = inject(SettingsService);
  private snackBar = inject(MatSnackBar);

  constructor() {
    this.initializeForms();
  }

  ngOnInit(): void {
    this.loadSettings();
  }

  private initializeForms(): void {
    // General Settings
    this.generalForm = new FormGroup({
      application_name: new FormControl('', [Validators.required]),
      default_language: new FormControl('ru', [Validators.required]),
      timezone: new FormControl('Europe/Moscow', [Validators.required]),
      date_format: new FormControl('DD.MM.YYYY', [Validators.required]),
      time_format: new FormControl('24', [Validators.required]),
      auto_save_interval: new FormControl(5, [
        Validators.min(1),
        Validators.max(60),
      ]),
    });

    // Parser Settings
    this.parserForm = new FormGroup({
      max_concurrent_groups: new FormControl(3, [
        Validators.min(1),
        Validators.max(10),
      ]),
      parse_interval_minutes: new FormControl(15, [
        Validators.min(5),
        Validators.max(1440),
      ]),
      max_comments_per_group: new FormControl(1000, [
        Validators.min(100),
        Validators.max(10000),
      ]),
      max_retry_attempts: new FormControl(3, [
        Validators.min(1),
        Validators.max(10),
      ]),
      enable_auto_parsing: new FormControl(true),
      enable_keyword_filtering: new FormControl(true),
      enable_sentiment_analysis: new FormControl(false),
      save_raw_data: new FormControl(true),
      retry_failed_requests: new FormControl(true),
    });

    // Notification Settings
    this.notificationForm = new FormGroup({
      email_notifications: new FormControl(false),
      browser_notifications: new FormControl(false),
      notify_on_parse_completion: new FormControl(true),
      notify_on_errors: new FormControl(true),
      notify_on_new_keywords: new FormControl(false),
      notification_sound: new FormControl(true),
      email_address: new FormControl('', [Validators.email]),
      notification_frequency: new FormControl('immediate', [
        Validators.required,
      ]),
      quiet_hours_enabled: new FormControl(false),
      quiet_hours_start: new FormControl('22:00'),
      quiet_hours_end: new FormControl('08:00'),
    });

    // Security Settings
    this.securityForm = new FormGroup({
      session_timeout_minutes: new FormControl(30, [
        Validators.min(5),
        Validators.max(480),
      ]),
      require_password_change: new FormControl(false),
      password_change_interval_days: new FormControl(90, [
        Validators.min(30),
        Validators.max(365),
      ]),
      enable_two_factor: new FormControl(false),
      max_login_attempts: new FormControl(5, [
        Validators.min(3),
        Validators.max(10),
      ]),
      lockout_duration_minutes: new FormControl(15, [
        Validators.min(5),
        Validators.max(60),
      ]),
      enable_audit_log: new FormControl(true),
      log_retention_days: new FormControl(90, [
        Validators.min(7),
        Validators.max(365),
      ]),
    });

    // Appearance Settings
    this.appearanceForm = new FormGroup({
      theme: new FormControl('light', [Validators.required]),
      primary_color: new FormControl('#1976d2', [Validators.required]),
      accent_color: new FormControl('#ff4081', [Validators.required]),
      font_size: new FormControl('medium', [Validators.required]),
      compact_mode: new FormControl(false),
      show_animations: new FormControl(true),
      sidebar_collapsed: new FormControl(false),
      dashboard_layout: new FormControl('grid', [Validators.required]),
    });
  }

  private loadSettings(): void {
    this.isLoading.set(true);
    this.settingsService.getSettings().subscribe({
      next: (settings) => {
        // Patch forms with loaded settings
        if (settings.general) {
          this.generalForm.patchValue(settings.general);
        }
        if (settings.parser) {
          this.parserForm.patchValue(settings.parser);
        }
        if (settings.notifications) {
          this.notificationForm.patchValue(settings.notifications);
        }
        if (settings.security) {
          this.securityForm.patchValue(settings.security);
        }
        if (settings.appearance) {
          this.appearanceForm.patchValue(settings.appearance);
        }
        this.isLoading.set(false);
      },
      error: (error) => {
        console.error('Error loading settings:', error);
        this.snackBar.open('Error loading settings', 'Close', {
          duration: 3000,
        });
        this.isLoading.set(false);
      },
    });
  }

  saveSettings(): void {
    if (
      this.generalForm.invalid ||
      this.parserForm.invalid ||
      this.notificationForm.invalid ||
      this.securityForm.invalid ||
      this.appearanceForm.invalid
    ) {
      this.snackBar.open('Please fix validation errors', 'Close', {
        duration: 3000,
      });
      return;
    }

    this.isSaving.set(true);

    const settings = {
      general: this.generalForm.value,
      parser: this.parserForm.value,
      notifications: this.notificationForm.value,
      security: this.securityForm.value,
      appearance: this.appearanceForm.value,
    };

    this.settingsService.updateSettings(settings).subscribe({
      next: () => {
        this.snackBar.open('Settings saved successfully', 'Close', {
          duration: 2000,
        });
        this.isSaving.set(false);
      },
      error: (error: any) => {
        console.error('Error saving settings:', error);
        this.snackBar.open('Error saving settings', 'Close', {
          duration: 3000,
        });
        this.isSaving.set(false);
      },
    });
  }

  resetToDefaults(): void {
    if (confirm('Are you sure you want to reset all settings to defaults?')) {
      this.initializeForms();
      this.snackBar.open('Settings reset to defaults', 'Close', {
        duration: 2000,
      });
    }
  }

  exportSettings(): void {
    const settings = {
      general: this.generalForm.value,
      parser: this.parserForm.value,
      notifications: this.notificationForm.value,
      security: this.securityForm.value,
      appearance: this.appearanceForm.value,
    };

    const blob = new Blob([JSON.stringify(settings, null, 2)], {
      type: 'application/json',
    });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `settings_${new Date().toISOString().split('T')[0]}.json`;
    document.body.appendChild(a);
    a.click();
    window.URL.revokeObjectURL(url);
    document.body.removeChild(a);

    this.snackBar.open('Settings exported successfully', 'Close', {
      duration: 2000,
    });
  }

  importSettings(event: any): void {
    const file = event.target.files[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = (e: any) => {
      try {
        const settings = JSON.parse(e.target.result);

        if (settings.general) {
          this.generalForm.patchValue(settings.general);
        }
        if (settings.parser) {
          this.parserForm.patchValue(settings.parser);
        }
        if (settings.notifications) {
          this.notificationForm.patchValue(settings.notifications);
        }
        if (settings.security) {
          this.securityForm.patchValue(settings.security);
        }
        if (settings.appearance) {
          this.appearanceForm.patchValue(settings.appearance);
        }

        this.snackBar.open('Settings imported successfully', 'Close', {
          duration: 2000,
        });
      } catch (error) {
        console.error('Error parsing settings file:', error);
        this.snackBar.open('Error importing settings', 'Close', {
          duration: 3000,
        });
      }
    };
    reader.readAsText(file);
  }
}

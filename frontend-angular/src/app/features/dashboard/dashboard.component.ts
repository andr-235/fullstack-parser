import { Component, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatCardModule } from '@angular/material/card';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatChipsModule } from '@angular/material/chips';
import { MatDividerModule } from '@angular/material/divider';
import { MatProgressBarModule } from '@angular/material/progress-bar';
import { MatBadgeModule } from '@angular/material/badge';
import { ThemeService } from '../../shared/services/theme.service';

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [
    CommonModule,
    MatCardModule,
    MatButtonModule,
    MatIconModule,
    MatChipsModule,
    MatDividerModule,
    MatProgressBarModule,
    MatBadgeModule,
  ],
  template: `
    <div class="dashboard">
      <div class="dashboard-header">
        <h1>Dashboard</h1>
        <p class="subtitle">Current theme: {{ currentTheme() }}</p>
      </div>

      <div class="stats-grid">
        <mat-card class="stat-card">
          <mat-card-header>
            <mat-card-title>
              <mat-icon>group</mat-icon>
              Total Groups
            </mat-card-title>
          </mat-card-header>
          <mat-card-content>
            <div class="stat-value">1,234</div>
            <div class="stat-change positive">+12% from last month</div>
          </mat-card-content>
        </mat-card>

        <mat-card class="stat-card">
          <mat-card-header>
            <mat-card-title>
              <mat-icon>key</mat-icon>
              Keywords
            </mat-card-title>
          </mat-card-header>
          <mat-card-content>
            <div class="stat-value">5,678</div>
            <div class="stat-change positive">+8% from last month</div>
          </mat-card-content>
        </mat-card>

        <mat-card class="stat-card">
          <mat-card-header>
            <mat-card-title>
              <mat-icon>comment</mat-icon>
              Comments
            </mat-card-title>
          </mat-card-header>
          <mat-card-content>
            <div class="stat-value">9,876</div>
            <div class="stat-change negative">-3% from last month</div>
          </mat-card-content>
        </mat-card>

        <mat-card class="stat-card">
          <mat-card-header>
            <mat-card-title>
              <mat-icon>trending_up</mat-icon>
              Active Parsers
            </mat-card-title>
          </mat-card-header>
          <mat-card-content>
            <div class="stat-value">12</div>
            <div class="stat-change neutral">No change</div>
          </mat-card-content>
        </mat-card>
      </div>

      <div class="content-grid">
        <mat-card class="content-card">
          <mat-card-header>
            <mat-card-title>Recent Activity</mat-card-title>
          </mat-card-header>
          <mat-card-content>
            <div class="activity-item">
              <mat-icon class="activity-icon">add_circle</mat-icon>
              <div class="activity-content">
                <div class="activity-title">New group added</div>
                <div class="activity-subtitle">
                  VK Group "Tech News" was added
                </div>
                <div class="activity-time">2 minutes ago</div>
              </div>
            </div>
            <mat-divider></mat-divider>
            <div class="activity-item">
              <mat-icon class="activity-icon">key</mat-icon>
              <div class="activity-content">
                <div class="activity-title">Keywords updated</div>
                <div class="activity-subtitle">15 new keywords were added</div>
                <div class="activity-time">15 minutes ago</div>
              </div>
            </div>
            <mat-divider></mat-divider>
            <div class="activity-item">
              <mat-icon class="activity-icon">comment</mat-icon>
              <div class="activity-content">
                <div class="activity-title">Comments processed</div>
                <div class="activity-subtitle">
                  1,234 comments were analyzed
                </div>
                <div class="activity-time">1 hour ago</div>
              </div>
            </div>
          </mat-card-content>
        </mat-card>

        <mat-card class="content-card">
          <mat-card-header>
            <mat-card-title>System Status</mat-card-title>
          </mat-card-header>
          <mat-card-content>
            <div class="status-item">
              <span class="status-label">Database</span>
              <mat-chip color="accent" selected>Online</mat-chip>
            </div>
            <div class="status-item">
              <span class="status-label">Parser Service</span>
              <mat-chip color="accent" selected>Running</mat-chip>
            </div>
            <div class="status-item">
              <span class="status-label">API</span>
              <mat-chip color="accent" selected>Active</mat-chip>
            </div>
            <div class="status-item">
              <span class="status-label">Storage</span>
              <mat-chip color="warn">75% Full</mat-chip>
            </div>

            <mat-divider></mat-divider>

            <div class="progress-section">
              <div class="progress-item">
                <span>CPU Usage</span>
                <mat-progress-bar
                  mode="determinate"
                  value="45"
                ></mat-progress-bar>
                <span>45%</span>
              </div>
              <div class="progress-item">
                <span>Memory Usage</span>
                <mat-progress-bar
                  mode="determinate"
                  value="78"
                ></mat-progress-bar>
                <span>78%</span>
              </div>
              <div class="progress-item">
                <span>Disk Usage</span>
                <mat-progress-bar
                  mode="determinate"
                  value="62"
                ></mat-progress-bar>
                <span>62%</span>
              </div>
            </div>
          </mat-card-content>
        </mat-card>
      </div>

      <div class="theme-demo">
        <mat-card>
          <mat-card-header>
            <mat-card-title>Theme Demo</mat-card-title>
            <mat-card-subtitle
              >This section demonstrates theme-aware
              components</mat-card-subtitle
            >
          </mat-card-header>
          <mat-card-content>
            <div class="demo-buttons">
              <button mat-raised-button color="primary">
                <mat-icon>favorite</mat-icon>
                Primary Button
              </button>
              <button mat-raised-button color="accent">
                <mat-icon>star</mat-icon>
                Accent Button
              </button>
              <button mat-raised-button color="warn">
                <mat-icon>delete</mat-icon>
                Warn Button
              </button>
            </div>

            <div class="demo-chips">
              <mat-chip color="primary" selected>Primary Chip</mat-chip>
              <mat-chip color="accent" selected>Accent Chip</mat-chip>
              <mat-chip color="warn" selected>Warn Chip</mat-chip>
            </div>

            <div class="demo-text">
              <p class="text-primary">This is primary colored text</p>
              <p class="text-secondary">This is secondary colored text</p>
              <p class="text-error">This is error colored text</p>
              <p class="text-success">This is success colored text</p>
              <p class="text-warning">This is warning colored text</p>
              <p class="text-info">This is info colored text</p>
            </div>
          </mat-card-content>
        </mat-card>
      </div>
    </div>
  `,
  styles: [
    `
      .dashboard {
        padding: 20px;
        max-width: 1200px;
        margin: 0 auto;
      }

      .dashboard-header {
        margin-bottom: 24px;
      }

      .dashboard-header h1 {
        margin: 0 0 8px 0;
        color: var(--app-text-primary);
        font-size: 2rem;
        font-weight: 500;
      }

      .subtitle {
        margin: 0;
        color: var(--app-text-secondary);
        font-size: 1rem;
      }

      .stats-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
        gap: 20px;
        margin-bottom: 24px;
      }

      .stat-card {
        transition: transform 0.2s ease, box-shadow 0.2s ease;
      }

      .stat-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px var(--app-shadow);
      }

      .stat-card mat-card-header {
        padding-bottom: 8px;
      }

      .stat-card mat-card-title {
        display: flex;
        align-items: center;
        gap: 8px;
        font-size: 1.1rem;
        color: var(--app-text-primary);
      }

      .stat-value {
        font-size: 2rem;
        font-weight: 500;
        color: var(--app-text-primary);
        margin-bottom: 4px;
      }

      .stat-change {
        font-size: 0.9rem;
        font-weight: 400;
      }

      .stat-change.positive {
        color: var(--app-success);
      }

      .stat-change.negative {
        color: var(--app-error);
      }

      .stat-change.neutral {
        color: var(--app-text-secondary);
      }

      .content-grid {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 20px;
        margin-bottom: 24px;
      }

      @media (max-width: 768px) {
        .content-grid {
          grid-template-columns: 1fr;
        }
      }

      .content-card {
        height: fit-content;
      }

      .activity-item {
        display: flex;
        align-items: flex-start;
        gap: 12px;
        padding: 12px 0;
      }

      .activity-icon {
        color: var(--app-primary);
        margin-top: 2px;
      }

      .activity-content {
        flex: 1;
      }

      .activity-title {
        font-weight: 500;
        color: var(--app-text-primary);
        margin-bottom: 4px;
      }

      .activity-subtitle {
        color: var(--app-text-secondary);
        font-size: 0.9rem;
        margin-bottom: 4px;
      }

      .activity-time {
        color: var(--app-text-secondary);
        font-size: 0.8rem;
      }

      .status-item {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 8px 0;
      }

      .status-label {
        color: var(--app-text-primary);
        font-weight: 500;
      }

      .progress-section {
        margin-top: 16px;
      }

      .progress-item {
        display: flex;
        align-items: center;
        gap: 12px;
        margin-bottom: 12px;
      }

      .progress-item span:first-child {
        min-width: 100px;
        color: var(--app-text-primary);
        font-size: 0.9rem;
      }

      .progress-item mat-progress-bar {
        flex: 1;
      }

      .progress-item span:last-child {
        min-width: 40px;
        text-align: right;
        color: var(--app-text-secondary);
        font-size: 0.9rem;
      }

      .theme-demo {
        margin-top: 24px;
      }

      .demo-buttons {
        display: flex;
        gap: 12px;
        margin-bottom: 16px;
        flex-wrap: wrap;
      }

      .demo-chips {
        display: flex;
        gap: 8px;
        margin-bottom: 16px;
        flex-wrap: wrap;
      }

      .demo-text p {
        margin: 8px 0;
        font-size: 0.9rem;
      }

      // Анимации
      .stat-card,
      .content-card {
        animation: fadeInUp 0.3s ease-out;
      }

      @keyframes fadeInUp {
        from {
          opacity: 0;
          transform: translateY(20px);
        }
        to {
          opacity: 1;
          transform: translateY(0);
        }
      }

      // Адаптивность
      @media (max-width: 600px) {
        .stats-grid {
          grid-template-columns: 1fr;
        }

        .demo-buttons {
          flex-direction: column;
        }

        .demo-chips {
          justify-content: center;
        }
      }
    `,
  ],
})
export class DashboardComponent {
  private themeService = inject(ThemeService);

  readonly currentTheme = this.themeService.currentTheme;
}

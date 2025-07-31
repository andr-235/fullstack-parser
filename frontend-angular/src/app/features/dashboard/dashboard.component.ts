import { Component, ChangeDetectionStrategy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatCardModule } from '@angular/material/card';
import { MatButtonModule } from '@angular/material/button';

@Component({
  selector: 'app-dashboard',
  template: `
    <div class="dashboard-container">
      <mat-card>
        <mat-card-header>
          <mat-card-title>Dashboard</mat-card-title>
          <mat-card-subtitle>VK Parser Dashboard</mat-card-subtitle>
        </mat-card-header>
        <mat-card-content>
          <p>Welcome to the VK Parser Dashboard!</p>
          <p>This is the main dashboard component.</p>
        </mat-card-content>
        <mat-card-actions>
          <button mat-button>View Groups</button>
          <button mat-button>View Keywords</button>
        </mat-card-actions>
      </mat-card>
    </div>
  `,
  styles: [
    `
      .dashboard-container {
        padding: 20px;
        max-width: 1200px;
        margin: 0 auto;
      }

      mat-card {
        margin-bottom: 20px;
      }
    `,
  ],
  standalone: true,
  imports: [CommonModule, MatCardModule, MatButtonModule],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class DashboardComponent {
  // Component logic will be added here
}

import { Routes } from '@angular/router';

export const routes: Routes = [
  {
    path: '',
    redirectTo: '/dashboard',
    pathMatch: 'full',
  },
  {
    path: 'login',
    loadComponent: () =>
      import('./features/auth/login/login.component').then(
        (m) => m.LoginComponent
      ),
  },
  {
    path: 'register',
    loadComponent: () =>
      import('./features/auth/register/register.component').then(
        (m) => m.RegisterComponent
      ),
  },
  {
    path: 'dashboard',
    loadComponent: () =>
      import('./features/dashboard/dashboard.component').then(
        (m) => m.DashboardComponent
      ),
  },
  {
    path: 'groups',
    loadComponent: () =>
      import('./features/groups/groups.component').then(
        (m) => m.GroupsComponent
      ),
  },
  {
    path: 'keywords',
    loadComponent: () =>
      import('./features/keywords/keywords.component').then(
        (m) => m.KeywordsComponent
      ),
  },
  {
    path: 'comments',
    loadComponent: () =>
      import('./features/comments/comments.component').then(
        (m) => m.CommentsComponent
      ),
  },
  {
    path: 'parser',
    loadComponent: () =>
      import('./features/parser/parser.component').then(
        (m) => m.ParserComponent
      ),
  },
  {
    path: 'monitoring',
    loadComponent: () =>
      import('./features/monitoring/monitoring.component').then(
        (m) => m.MonitoringComponent
      ),
  },
  {
    path: 'settings',
    loadComponent: () =>
      import('./features/settings/settings.component').then(
        (m) => m.SettingsComponent
      ),
  },
  {
    path: '**',
    redirectTo: '/dashboard',
  },
];

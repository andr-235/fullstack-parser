# Angular Migration Architecture Design

## 🎨🎨🎨 ENTERING CREATIVE PHASE: ARCHITECTURE DESIGN 🎨🎨🎨

### ПРОБЛЕМА: Миграция фронтенда с Next.js на Angular

**Текущее состояние:**

- Next.js 15 с React 19
- Tailwind CSS + Radix UI компоненты
- Zustand + React Query для состояния
- TypeScript с строгой типизацией

**Требования:**

- Сохранение всей функциональности
- Улучшение производительности и масштабируемости
- Современная Angular архитектура
- Безопасная миграция без потери данных

## АНАЛИЗ АРХИТЕКТУРНЫХ ВАРИАНТОВ

### Option 1: Полная миграция Angular 20

**Описание**: Полная замена Next.js на Angular с современной архитектурой

**Pros:**

- Современная Angular 20 с standalone компонентами
- Отличная производительность с Ivy renderer
- Сильная типизация и валидация
- Встроенная поддержка PWA
- Лучшая экосистема для enterprise
- Angular Material для UI компонентов

**Cons:**

- Высокий риск при миграции
- Долгое время разработки (5-7 месяцев)
- Сложность отладки
- Необходимость переобучения команды

### Option 2: Гибридная миграция

**Описание**: Постепенная миграция с параллельной работой

**Pros:**

- Низкий риск
- Постепенное тестирование
- Возможность отката
- Сохранение функциональности

**Cons:**

- Сложность поддержки двух систем
- Дублирование кода
- Долгий процесс
- Высокие затраты на поддержку

### Option 3: Миграция только UI компонентов

**Описание**: Замена только UI слоя с сохранением Next.js

**Pros:**

- Минимальный риск
- Быстрая миграция
- Улучшение UI компонентов

**Cons:**

- Ограниченные улучшения
- Не решает проблемы архитектуры
- Смешанная технология

## РЕКОМЕНДУЕМЫЙ ПОДХОД: Option 1 - Полная миграция Angular 20

### Обоснование:

1. **Долгосрочная выгода** превышает риски
2. **Angular экосистема** лучше для enterprise
3. **Standalone компоненты** обеспечивают лучшую производительность
4. **Angular Material** предоставляет готовые UI компоненты
5. **TypeScript интеграция** более глубокая

## ИМПЛЕМЕНТАЦИОННЫЕ РУКОВОДСТВА

### Phase 1: Базовая структура Angular (1-2 недели)

```bash
# Создание новой ветки
git checkout -b feature/angular-migration
git push -u origin feature/angular-migration

# Инициализация Angular проекта
ng new frontend-angular --routing --style=scss --skip-git --standalone
cd frontend-angular
ng add @angular/material --standalone
ng add @angular/pwa
```

### Phase 2: Структура проекта (2-3 недели)

```
frontend-angular/
├── src/
│   ├── app/
│   │   ├── core/           # Singleton services, guards, interceptors
│   │   │   ├── services/
│   │   │   │   ├── api.service.ts
│   │   │   │   ├── auth.service.ts
│   │   │   │   └── index.ts
│   │   │   ├── guards/
│   │   │   │   ├── auth.guard.ts
│   │   │   │   └── index.ts
│   │   │   ├── interceptors/
│   │   │   │   ├── auth.interceptor.ts
│   │   │   │   └── index.ts
│   │   │   └── models/
│   │   │       ├── user.model.ts
│   │   │       └── index.ts
│   │   ├── shared/         # Shared components, pipes, directives
│   │   │   ├── components/
│   │   │   │   ├── data-table/
│   │   │   │   │   ├── data-table.component.ts
│   │   │   │   │   ├── data-table.component.html
│   │   │   │   │   └── data-table.component.scss
│   │   │   │   ├── loading-spinner/
│   │   │   │   │   └── loading-spinner.component.ts
│   │   │   │   └── index.ts
│   │   │   ├── pipes/
│   │   │   │   └── index.ts
│   │   │   ├── directives/
│   │   │   │   └── index.ts
│   │   │   └── models/
│   │   │       └── index.ts
│   │   ├── features/       # Feature components (standalone)
│   │   │   ├── dashboard/
│   │   │   │   ├── dashboard.component.ts
│   │   │   │   ├── dashboard.component.html
│   │   │   │   ├── dashboard.component.scss
│   │   │   │   ├── components/
│   │   │   │   │   ├── dashboard-stats.component.ts
│   │   │   │   │   └── dashboard-charts.component.ts
│   │   │   │   └── routes.ts
│   │   │   ├── groups/
│   │   │   │   ├── groups.component.ts
│   │   │   │   ├── groups.component.html
│   │   │   │   ├── groups.component.scss
│   │   │   │   ├── components/
│   │   │   │   │   ├── groups-list.component.ts
│   │   │   │   │   ├── groups-form.component.ts
│   │   │   │   │   └── groups-stats.component.ts
│   │   │   │   └── routes.ts
│   │   │   ├── keywords/
│   │   │   │   └── routes.ts
│   │   │   ├── comments/
│   │   │   │   └── routes.ts
│   │   │   ├── parser/
│   │   │   │   └── routes.ts
│   │   │   ├── monitoring/
│   │   │   │   └── routes.ts
│   │   │   └── settings/
│   │   │       └── routes.ts
│   │   └── layout/         # Layout components
│   │       ├── header/
│   │       │   └── header.component.ts
│   │       ├── sidebar/
│   │       │   └── sidebar.component.ts
│   │       └── footer/
│   │           └── footer.component.ts
│   ├── assets/
│   └── environments/
```

### Phase 3: Core Services (1-2 недели)

```typescript
// src/app/core/services/api.service.ts
@Injectable({
  providedIn: "root",
})
export class ApiService {
  private baseUrl = environment.apiUrl;

  constructor(private http: HttpClient) {}

  get<T>(endpoint: string): Observable<T> {
    return this.http.get<T>(`${this.baseUrl}${endpoint}`);
  }

  post<T>(endpoint: string, data: any): Observable<T> {
    return this.http.post<T>(`${this.baseUrl}${endpoint}`, data);
  }
}

// src/app/core/services/auth.service.ts
@Injectable({
  providedIn: "root",
})
export class AuthService {
  private currentUserSubject = new BehaviorSubject<User | null>(null);
  public currentUser$ = this.currentUserSubject.asObservable();

  constructor(private apiService: ApiService) {}

  login(credentials: LoginCredentials): Observable<User> {
    return this.apiService.post<User>("/auth/login", credentials);
  }
}
```

### Phase 4: Standalone Components (4-6 недель)

```typescript
// src/app/features/dashboard/dashboard.component.ts
@Component({
  selector: "app-dashboard",
  templateUrl: "./dashboard.component.html",
  styleUrls: ["./dashboard.component.scss"],
  standalone: true,
  imports: [
    CommonModule,
    MatCardModule,
    MatButtonModule,
    DashboardStatsComponent,
    DashboardChartsComponent,
  ],
})
export class DashboardComponent {
  // Component logic
}

// src/app/features/groups/groups.component.ts
@Component({
  selector: "app-groups",
  templateUrl: "./groups.component.html",
  styleUrls: ["./groups.component.scss"],
  standalone: true,
  imports: [
    CommonModule,
    ReactiveFormsModule,
    MatTableModule,
    MatButtonModule,
    MatFormFieldModule,
    MatInputModule,
    GroupsListComponent,
    GroupsFormComponent,
    GroupsStatsComponent,
  ],
})
export class GroupsComponent {
  // Component logic
}
```

### Phase 5: Shared Components (2-3 недели)

```typescript
// src/app/shared/components/data-table/data-table.component.ts
@Component({
  selector: "app-data-table",
  templateUrl: "./data-table.component.html",
  styleUrls: ["./data-table.component.scss"],
  standalone: true,
  imports: [CommonModule, MatTableModule, MatPaginatorModule],
})
export class DataTableComponent<T> {
  @Input() data: T[] = [];
  @Input() columns: TableColumn[] = [];
  @Output() rowClick = new EventEmitter<T>();

  onRowClick(item: T): void {
    this.rowClick.emit(item);
  }
}

// src/app/shared/components/loading-spinner/loading-spinner.component.ts
@Component({
  selector: "app-loading-spinner",
  template: ` <mat-spinner [diameter]="diameter"></mat-spinner> `,
  standalone: true,
  imports: [MatProgressSpinnerModule],
})
export class LoadingSpinnerComponent {
  @Input() diameter = 50;
}
```

### Phase 6: State Management (1-2 недели)

```typescript
// src/app/core/store/app.state.ts
export interface AppState {
  auth: AuthState;
  groups: GroupsState;
  keywords: KeywordsState;
  comments: CommentsState;
}

// src/app/core/store/groups/groups.actions.ts
export const loadGroups = createAction("[Groups] Load Groups");
export const loadGroupsSuccess = createAction(
  "[Groups] Load Groups Success",
  props<{ groups: Group[] }>()
);
export const loadGroupsFailure = createAction(
  "[Groups] Load Groups Failure",
  props<{ error: string }>()
);

// src/app/core/store/groups/groups.effects.ts
@Injectable()
export class GroupsEffects {
  loadGroups$ = createEffect(() =>
    this.actions$.pipe(
      ofType(GroupsActions.loadGroups),
      mergeMap(() =>
        this.groupsService.getGroups().pipe(
          map((groups) => GroupsActions.loadGroupsSuccess({ groups })),
          catchError((error) => of(GroupsActions.loadGroupsFailure({ error })))
        )
      )
    )
  );

  constructor(
    private actions$: Actions,
    private groupsService: GroupsService
  ) {}
}
```

### Phase 7: Routing (1 неделя)

```typescript
// src/app/app.routes.ts
export const routes: Routes = [
  {
    path: "",
    component: LayoutComponent,
    children: [
      {
        path: "dashboard",
        loadComponent: () =>
          import("./features/dashboard/dashboard.component").then(
            (m) => m.DashboardComponent
          ),
      },
      {
        path: "groups",
        loadComponent: () =>
          import("./features/groups/groups.component").then(
            (m) => m.GroupsComponent
          ),
      },
      {
        path: "keywords",
        loadComponent: () =>
          import("./features/keywords/keywords.component").then(
            (m) => m.KeywordsComponent
          ),
      },
      {
        path: "comments",
        loadComponent: () =>
          import("./features/comments/comments.component").then(
            (m) => m.CommentsComponent
          ),
      },
      {
        path: "parser",
        loadComponent: () =>
          import("./features/parser/parser.component").then(
            (m) => m.ParserComponent
          ),
      },
      {
        path: "monitoring",
        loadComponent: () =>
          import("./features/monitoring/monitoring.component").then(
            (m) => m.MonitoringComponent
          ),
      },
      {
        path: "settings",
        loadComponent: () =>
          import("./features/settings/settings.component").then(
            (m) => m.SettingsComponent
          ),
      },
    ],
  },
];
```

### Phase 8: Styling и UI (2-3 недели)

```scss
// src/styles/variables.scss
$primary-color: #1976d2;
$secondary-color: #dc004e;
$background-color: #fafafa;
$text-color: #333;

// src/app/shared/components/button/button.component.scss
.app-button {
  padding: 8px 16px;
  border-radius: 4px;
  border: none;
  cursor: pointer;
  font-weight: 500;

  &.primary {
    background-color: $primary-color;
    color: white;
  }

  &.secondary {
    background-color: $secondary-color;
    color: white;
  }
}
```

## ПРОВЕРКА СООТВЕТСТВИЯ ТРЕБОВАНИЯМ

✅ **Сохранение функционала**: Все компоненты и страницы перенесены
✅ **Улучшение производительности**: Angular Ivy + standalone компоненты
✅ **Современная архитектура**: Standalone компоненты + NgRx state management
✅ **Безопасная миграция**: Поэтапный подход с тестированием
✅ **TypeScript интеграция**: Глубокая типизация на всех уровнях

## 🎨🎨🎨 EXITING CREATIVE PHASE 🎨🎨🎨

**Ключевые решения:**

- Angular 20 с standalone компонентами (без NgModules)
- NgRx для state management
- Angular Material для UI компонентов
- Lazy loading для всех feature компонентов
- Progressive Web App (PWA) поддержка

**Следующие шаги:**

1. Создание базовой структуры Angular проекта
2. Настройка core services и interceptors
3. Миграция shared компонентов
4. Поэтапная миграция feature компонентов

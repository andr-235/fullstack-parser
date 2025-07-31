# VK Parser Frontend - Angular Application

## 📋 Overview

This is a modern Angular 20 application for managing VK groups, keywords, comments, and parsing operations. Built with standalone components, Material Design, and comprehensive state management.

## 🚀 Quick Start

### Prerequisites

- Node.js 18+
- npm 9+
- Angular CLI 20+

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd frontend-angular

# Install dependencies
npm install

# Start development server
npm start

# Build for production
npm run build
```

## 🏗️ Architecture

### Project Structure

```
frontend-angular/
├── src/
│   ├── app/
│   │   ├── core/                 # Core services, guards, interceptors
│   │   │   ├── services/         # API, Auth, Cache, Performance services
│   │   │   ├── guards/           # Route guards
│   │   │   ├── interceptors/     # HTTP interceptors
│   │   │   └── models/           # TypeScript interfaces
│   │   ├── shared/               # Shared components, pipes, directives
│   │   │   ├── components/       # Reusable UI components
│   │   │   ├── pipes/            # Custom pipes
│   │   │   └── directives/       # Custom directives
│   │   ├── features/             # Feature modules (standalone)
│   │   │   ├── auth/             # Authentication
│   │   │   ├── dashboard/        # Dashboard
│   │   │   ├── groups/           # VK Groups management
│   │   │   ├── keywords/         # Keywords management
│   │   │   ├── comments/         # Comments management
│   │   │   ├── parser/           # Parser controls
│   │   │   ├── monitoring/       # System monitoring
│   │   │   └── settings/         # Application settings
│   │   └── layout/               # Layout components
│   ├── assets/                   # Static assets
│   └── environments/             # Environment configurations
├── docs/                         # Documentation
└── tests/                        # Test files
```

### Key Technologies

- **Angular 20**: Latest version with standalone components
- **Material Design**: Angular Material components
- **RxJS**: Reactive programming for state management
- **TypeScript**: Strict typing throughout
- **NgRx**: State management (optional)
- **Jasmine/Karma**: Testing framework

## 🔧 Core Services

### API Service

Handles all HTTP communications with the backend API.

```typescript
// Example usage
this.apiService.get<Group[]>("/groups").subscribe((groups) => {
  // Handle response
});
```

### Cache Service

Intelligent caching with TTL support for improved performance.

```typescript
// Example usage
this.cacheService.getOrSet(
  "groups",
  () => this.apiService.get("/groups"),
  2 * 60 * 1000 // 2 minutes TTL
);
```

### Performance Service

Real-time performance monitoring and alerts.

```typescript
// Example usage
this.performanceService.getMetrics().subscribe((metrics) => {
  console.log("Performance metrics:", metrics);
});
```

## 🎨 Components

### Feature Components

#### Groups Component

- **Purpose**: Manage VK groups
- **Features**: CRUD operations, search, filtering, pagination
- **Key Features**:
  - Material table with sorting
  - Advanced search with debouncing
  - Bulk operations
  - Real-time updates

#### Keywords Component

- **Purpose**: Manage keywords for monitoring
- **Features**: Category-based organization, bulk operations
- **Key Features**:
  - Category filtering
  - Bulk import/export
  - Keyword statistics

#### Comments Component

- **Purpose**: Monitor and manage comments
- **Features**: Advanced search, bulk operations
- **Key Features**:
  - Multi-criteria search
  - Bulk moderation
  - Comment analytics

#### Parser Component

- **Purpose**: Control parsing operations
- **Features**: Real-time status, configuration
- **Key Features**:
  - Start/stop parsing
  - Configuration management
  - Real-time status updates

#### Monitoring Component

- **Purpose**: System monitoring dashboard
- **Features**: Real-time metrics, alerts
- **Key Features**:
  - System health monitoring
  - Performance metrics
  - Alert management

#### Settings Component

- **Purpose**: Application configuration
- **Features**: Comprehensive settings management
- **Key Features**:
  - General settings
  - Parser configuration
  - Security settings
  - Import/export functionality

## 🔐 Authentication

### Auth Service

Handles user authentication and session management.

```typescript
// Login
this.authService.login(credentials).subscribe((user) => {
  // Handle successful login
});

// Check authentication status
this.authService.isAuthenticated$.subscribe((isAuth) => {
  // Handle auth state changes
});
```

### Guards

Route protection based on authentication and roles.

```typescript
// Auth guard
@Injectable()
export class AuthGuard {
  canActivate(): boolean {
    return this.authService.isAuthenticated;
  }
}
```

## 📊 State Management

### NgRx Store

Centralized state management for complex data flows.

```typescript
// Store structure
interface AppState {
  auth: AuthState;
  groups: GroupsState;
  keywords: KeywordsState;
  comments: CommentsState;
  parser: ParserState;
  monitoring: MonitoringState;
  settings: SettingsState;
}
```

### Effects

Side effects for API calls and external interactions.

```typescript
// Example effect
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
}
```

## 🧪 Testing

### Unit Tests

Comprehensive unit tests for all components and services.

```bash
# Run unit tests
npm test

# Run tests with coverage
npm run test:coverage
```

### E2E Tests

End-to-end testing for critical user flows.

```bash
# Run E2E tests
npm run e2e
```

## 🚀 Performance Optimizations

### Lazy Loading

All feature routes use lazy loading for optimal bundle size.

```typescript
// Route configuration
{
  path: 'groups',
  loadComponent: () => import('./features/groups/groups.component')
    .then(m => m.GroupsComponent)
}
```

### Change Detection

OnPush strategy for optimized rendering.

```typescript
@Component({
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class GroupsComponent {
  // Component implementation
}
```

### Caching

Intelligent caching with TTL for improved performance.

```typescript
// Cache configuration
this.cacheService.getOrSet(
  "groups",
  () => this.apiService.get("/groups"),
  2 * 60 * 1000 // 2 minutes TTL
);
```

## 📦 Build & Deployment

### Development

```bash
# Start development server
npm start

# Build for development
npm run build:dev
```

### Production

```bash
# Build for production
npm run build

# Build with optimization
npm run build:prod
```

### Docker Deployment

```dockerfile
# Dockerfile
FROM node:18-alpine as builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=builder /app/dist/frontend-angular /usr/share/nginx/html
COPY nginx.conf /etc/nginx/nginx.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

## 🔧 Configuration

### Environment Variables

```typescript
// environment.ts
export const environment = {
  production: false,
  apiUrl: "http://localhost:8000/api",
  version: "1.0.0",
};
```

### Angular Configuration

```json
// angular.json
{
  "projects": {
    "frontend-angular": {
      "architect": {
        "build": {
          "configurations": {
            "production": {
              "optimization": true,
              "outputHashing": "all",
              "sourceMap": false,
              "extractLicenses": true
            }
          }
        }
      }
    }
  }
}
```

## 📚 API Documentation

### Endpoints

#### Groups

- `GET /api/groups` - Get all groups
- `POST /api/groups` - Create new group
- `PUT /api/groups/{id}` - Update group
- `DELETE /api/groups/{id}` - Delete group

#### Keywords

- `GET /api/keywords` - Get all keywords
- `POST /api/keywords` - Create new keyword
- `PUT /api/keywords/{id}` - Update keyword
- `DELETE /api/keywords/{id}` - Delete keyword

#### Comments

- `GET /api/comments` - Get all comments
- `POST /api/comments` - Create new comment
- `PUT /api/comments/{id}` - Update comment
- `DELETE /api/comments/{id}` - Delete comment

#### Parser

- `GET /api/parser/status` - Get parser status
- `POST /api/parser/start` - Start parsing
- `POST /api/parser/stop` - Stop parsing
- `PUT /api/parser/config` - Update parser configuration

#### Monitoring

- `GET /api/monitoring/metrics` - Get system metrics
- `GET /api/monitoring/alerts` - Get system alerts

#### Settings

- `GET /api/settings` - Get application settings
- `PUT /api/settings` - Update application settings

## 🐛 Troubleshooting

### Common Issues

#### Build Errors

```bash
# Clear cache and reinstall
rm -rf node_modules package-lock.json
npm install
```

#### Performance Issues

```bash
# Analyze bundle size
npm run build -- --stats-json
npx webpack-bundle-analyzer dist/frontend-angular/stats.json
```

#### Testing Issues

```bash
# Clear test cache
npm run test -- --watch=false --browsers=ChromeHeadless
```

## 🤝 Contributing

### Development Workflow

1. Create feature branch
2. Implement changes
3. Write tests
4. Update documentation
5. Submit pull request

### Code Style

- Use TypeScript strict mode
- Follow Angular style guide
- Use ESLint and Prettier
- Write comprehensive tests

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:

- Create an issue in the repository
- Check the documentation
- Review the troubleshooting section

---

**Version**: 1.0.0  
**Last Updated**: 2024  
**Angular Version**: 20.0.0

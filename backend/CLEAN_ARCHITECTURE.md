# Clean Architecture - Документация

Этот документ описывает архитектуру backend приложения, следующую принципам Clean Architecture.

## Оглавление

1. [Обзор архитектуры](#обзор-архитектуры)
2. [Слои архитектуры](#слои-архитектуры)
3. [Структура проекта](#структура-проекта)
4. [Dependency Injection](#dependency-injection)
5. [Основные компоненты](#основные-компоненты)
6. [Примеры использования](#примеры-использования)
7. [Тестирование](#тестирование)

## Обзор архитектуры

Проект следует принципам Clean Architecture Роберта Мартина с четырьмя основными слоями:

```
┌─────────────────────────────────────────────┐
│         Presentation Layer                   │
│   (Controllers, HTTP handlers)              │
└─────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────┐
│         Application Layer                    │
│      (Use Cases, DTOs)                      │
└─────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────┐
│           Domain Layer                       │
│  (Entities, Value Objects, Interfaces)     │
└─────────────────────────────────────────────┘
                    ↑
┌─────────────────────────────────────────────┐
│       Infrastructure Layer                   │
│  (DB, External APIs, File System)           │
└─────────────────────────────────────────────┘
```

### Ключевые принципы

1. **Dependency Inversion**: Внутренние слои не зависят от внешних
2. **Separation of Concerns**: Каждый слой имеет четкую ответственность
3. **Testability**: Легко тестировать бизнес-логику без внешних зависимостей
4. **Flexibility**: Легко заменить infrastructure компоненты

## Слои архитектуры

### 1. Domain Layer (`src/domain/`)

**Назначение**: Содержит бизнес-логику и правила домена.

**Компоненты**:
- **Entities** - Объекты с идентичностью и бизнес-логикой
- **Value Objects** - Immutable объекты без идентичности
- **Repository Interfaces** - Контракты для доступа к данным
- **Domain Errors** - Специфичные ошибки домена

**Правила**:
- ❌ НЕ зависит от других слоев
- ❌ НЕ содержит infrastructure деталей
- ✅ Содержит только бизнес-логику
- ✅ Определяет интерфейсы для внешних зависимостей

**Пример**:
```typescript
// src/domain/entities/Group.ts
export class Group {
  private constructor(
    private readonly _id: GroupId,
    private readonly _vkId: VkId,
    private _name: string,
    private _status: GroupStatus
  ) {
    this.validate();
  }

  // Бизнес-логика
  markAsInvalid(reason: string): void {
    this._status = GroupStatus.invalid(reason);
  }

  canBeProcessed(): boolean {
    return this._status.isValid();
  }
}
```

### 2. Application Layer (`src/application/`)

**Назначение**: Оркестрация бизнес-логики через Use Cases.

**Компоненты**:
- **Use Cases** - Сценарии использования приложения
- **DTOs** - Объекты для передачи данных между слоями

**Правила**:
- ✅ Зависит только от Domain Layer
- ✅ Оркеструет Domain Entities
- ✅ Использует Repository интерфейсы из Domain
- ❌ НЕ знает о деталях Infrastructure

**Пример**:
```typescript
// src/application/use-cases/groups/UploadGroupsUseCase.ts
export class UploadGroupsUseCase {
  constructor(
    private readonly groupsRepository: IGroupsRepository,
    private readonly vkApiRepository: IVkApiRepository,
    private readonly taskStorageRepository: ITaskStorageRepository,
    private readonly fileParser: IFileParser
  ) {}

  async execute(input: UploadGroupsInput): Promise<UploadGroupsOutput> {
    // 1. Валидация файла
    const validation = await this.fileParser.validateFile(input.file);

    // 2. Парсинг
    const parseResult = await this.fileParser.parseGroupsFile(
      input.file,
      input.encoding
    );

    // 3. Создание задачи (Domain Entity)
    const task = GroupUploadTask.createNew({
      total: parseResult.groups.length,
      fileName: input.fileName,
      fileSize: input.file.length
    });

    // 4. Сохранение через Repository
    await this.taskStorageRepository.saveTask(task.id.value, task.toPersistence());

    return {
      taskId: task.id.value,
      totalGroups: parseResult.groups.length,
      message: `Загрузка ${parseResult.groups.length} групп запущена`
    };
  }
}
```

### 3. Infrastructure Layer (`src/infrastructure/`)

**Назначение**: Реализация технических деталей и внешних интеграций.

**Компоненты**:
- **Adapters** - Реализации Repository интерфейсов
- **External Services** - Интеграции с внешними API
- **Database** - Работа с БД через ORM
- **DI Container** - Управление зависимостями

**Правила**:
- ✅ Реализует интерфейсы из Domain Layer
- ✅ Содержит технические детали (DB, API, файлы)
- ✅ Адаптирует внешние библиотеки к Domain интерфейсам
- ❌ НЕ содержит бизнес-логику

**Пример**:
```typescript
// src/infrastructure/database/repositories/PrismaGroupsRepository.ts
export class PrismaGroupsRepository implements IGroupsRepository {
  async save(group: Group): Promise<void> {
    const data = group.toPersistence();
    await prisma.groups.upsert({
      where: { vk_id: data.vk_id },
      create: data,
      update: data
    });
  }

  async findAll(options: FindGroupsOptions): Promise<FindGroupsResult> {
    const prismaGroups = await prisma.groups.findMany({
      where: this.buildWhereClause(options),
      take: options.limit,
      skip: options.offset,
      orderBy: this.buildOrderBy(options)
    });

    return {
      groups: prismaGroups.map(pg => this.toDomain(pg)),
      total: await prisma.groups.count()
    };
  }

  private toDomain(prismaGroup: any): Group {
    return Group.restore({
      id: GroupId.create(prismaGroup.id),
      vkId: VkId.create(prismaGroup.vk_id),
      name: prismaGroup.name,
      // ... маппинг остальных полей
    });
  }
}
```

### 4. Presentation Layer (`src/presentation/`)

**Назначение**: HTTP API и обработка запросов.

**Компоненты**:
- **Controllers** - Express route handlers
- **Factories** - Создание Use Cases через DI

**Правила**:
- ✅ Обрабатывает HTTP запросы/ответы
- ✅ Валидирует входные данные
- ✅ Вызывает Use Cases через фабрики
- ❌ НЕ содержит бизнес-логику

**Пример**:
```typescript
// src/presentation/controllers/GroupsController.ts
const uploadGroups = async (req: Request, res: Response): Promise<void> => {
  // 1. Валидация входных данных
  if (!req.file) {
    throw new ValidationError('Файл не был загружен');
  }

  // 2. Получение Use Case из фабрики
  const uploadUseCase = GroupsUseCasesFactory.getUploadGroupsUseCase();

  // 3. Подготовка input
  const input = {
    file: req.file.buffer,
    encoding: req.query.encoding as BufferEncoding || 'utf-8',
    fileName: req.file.originalname
  };

  // 4. Выполнение Use Case
  const result = await uploadUseCase.execute(input);

  // 5. Форматирование ответа
  res.success(result, 'Файл успешно загружен');
};
```

## Структура проекта

```
backend/
├── src/
│   ├── domain/                     # Domain Layer
│   │   ├── entities/              # Бизнес-сущности
│   │   │   ├── Group.ts
│   │   │   ├── Task.ts
│   │   │   └── ...
│   │   ├── value-objects/         # Value Objects
│   │   │   ├── VkId.ts
│   │   │   ├── GroupId.ts
│   │   │   └── ...
│   │   ├── repositories/          # Repository интерфейсы
│   │   │   ├── IGroupsRepository.ts
│   │   │   ├── IVkApiRepository.ts
│   │   │   └── ...
│   │   ├── errors/                # Domain ошибки
│   │   └── index.ts
│   │
│   ├── application/               # Application Layer
│   │   ├── use-cases/            # Use Cases
│   │   │   └── groups/
│   │   │       ├── UploadGroupsUseCase.ts
│   │   │       ├── GetGroupsUseCase.ts
│   │   │       └── ...
│   │   ├── dto/                  # DTOs
│   │   │   ├── UploadGroupsDto.ts
│   │   │   ├── GetGroupsDto.ts
│   │   │   └── ...
│   │   └── index.ts
│   │
│   ├── infrastructure/           # Infrastructure Layer
│   │   ├── database/            # БД адаптеры
│   │   │   └── repositories/
│   │   │       └── PrismaGroupsRepository.ts
│   │   ├── external-services/   # Внешние сервисы
│   │   │   ├── vk-api/
│   │   │   │   └── VkApiAdapter.ts
│   │   │   └── file-parser/
│   │   │       └── FileParserAdapter.ts
│   │   ├── storage/             # Хранилища
│   │   │   └── RedisTaskStorageAdapter.ts
│   │   └── di/                  # Dependency Injection
│   │       ├── Container.ts
│   │       └── index.ts
│   │
│   ├── presentation/            # Presentation Layer
│   │   ├── controllers/        # HTTP контроллеры
│   │   │   └── GroupsController.ts
│   │   └── factories/          # Use Case фабрики
│   │       └── GroupsUseCasesFactory.ts
│   │
│   └── server.ts               # Express app setup
│
└── tests/
    ├── unit/
    │   ├── domain/             # Тесты Domain Layer
    │   └── use-cases/          # Тесты Use Cases
    └── integration/            # Интеграционные тесты
        └── clean-architecture/
```

## Dependency Injection

### DI Container

```typescript
// src/infrastructure/di/Container.ts
export class Container {
  // Singleton паттерн для репозиториев
  getGroupsRepository(): IGroupsRepository {
    if (!this._groupsRepository) {
      this._groupsRepository = new PrismaGroupsRepository();
    }
    return this._groupsRepository;
  }

  // Singleton для Use Cases
  getUploadGroupsUseCase(): UploadGroupsUseCase {
    if (!this._uploadGroupsUseCase) {
      this._uploadGroupsUseCase = new UploadGroupsUseCase(
        this.getGroupsRepository(),
        this.getVkApiRepository(),
        this.getTaskStorageRepository(),
        this.getFileParser()
      );
    }
    return this._uploadGroupsUseCase;
  }
}
```

### Инициализация

```typescript
// src/infrastructure/di/index.ts
let container: Container | null = null;

export function initializeContainer(vkAccessToken: string): Container {
  if (!container) {
    container = new Container(vkAccessToken);
  }
  return container;
}

export function getContainer(): Container {
  if (!container) {
    throw new Error('Container not initialized');
  }
  return container;
}
```

### Использование в контроллерах

```typescript
// src/presentation/factories/GroupsUseCasesFactory.ts
export class GroupsUseCasesFactory {
  static getUploadGroupsUseCase(): UploadGroupsUseCase {
    const container = getContainer();
    return container.getUploadGroupsUseCase();
  }
}

// В контроллере
const useCase = GroupsUseCasesFactory.getUploadGroupsUseCase();
const result = await useCase.execute(input);
```

## Основные компоненты

### Value Objects

**Характеристики**:
- Immutable
- Equality по значению, а не по ссылке
- Валидация в конструкторе

```typescript
export class VkId {
  private readonly _value: number;

  private constructor(value: number) {
    this._value = value;
  }

  static create(value: number): VkId {
    if (!VkId.isValid(value)) {
      throw new DomainError(`Invalid VK ID: ${value}`);
    }
    return new VkId(value);
  }

  equals(other: VkId): boolean {
    return Math.abs(this._value) === Math.abs(other._value);
  }
}
```

### Entities

**Характеристики**:
- Имеют идентичность
- Содержат бизнес-логику
- Защищают инварианты

```typescript
export class Group {
  private constructor(
    private readonly _id: GroupId,
    private readonly _vkId: VkId,
    private _name: string,
    private _status: GroupStatus
  ) {
    this.validate();
  }

  static create(props: CreateGroupProps): Group {
    return new Group(
      GroupId.generate(),
      props.vkId,
      props.name,
      props.status
    );
  }

  static restore(props: RestoreGroupProps): Group {
    return new Group(
      props.id,
      props.vkId,
      props.name,
      props.status
    );
  }

  // Бизнес-логика
  markAsInvalid(reason: string): void {
    this._status = GroupStatus.invalid(reason);
  }

  private validate(): void {
    if (!this._name || this._name.trim().length === 0) {
      throw new InvariantViolationError('Group name cannot be empty');
    }
  }
}
```

## Примеры использования

### Создание нового Use Case

1. **Определите интерфейсы в Domain Layer**:
```typescript
// src/domain/repositories/INewRepository.ts
export interface INewRepository {
  doSomething(): Promise<void>;
}
```

2. **Создайте Use Case в Application Layer**:
```typescript
// src/application/use-cases/NewUseCase.ts
export class NewUseCase {
  constructor(private readonly repository: INewRepository) {}

  async execute(input: Input): Promise<Output> {
    // Бизнес-логика
  }
}
```

3. **Реализуйте адаптер в Infrastructure Layer**:
```typescript
// src/infrastructure/repositories/NewRepositoryAdapter.ts
export class NewRepositoryAdapter implements INewRepository {
  async doSomething(): Promise<void> {
    // Технические детали
  }
}
```

4. **Зарегистрируйте в DI Container**:
```typescript
// src/infrastructure/di/Container.ts
getNewRepository(): INewRepository {
  if (!this._newRepository) {
    this._newRepository = new NewRepositoryAdapter();
  }
  return this._newRepository;
}

getNewUseCase(): NewUseCase {
  if (!this._newUseCase) {
    this._newUseCase = new NewUseCase(this.getNewRepository());
  }
  return this._newUseCase;
}
```

5. **Используйте в контроллере**:
```typescript
const useCase = container.getNewUseCase();
const result = await useCase.execute(input);
```

## Тестирование

### Unit тесты для Use Cases

```typescript
describe('UploadGroupsUseCase', () => {
  let useCase: UploadGroupsUseCase;
  let mockGroupsRepo: jest.Mocked<IGroupsRepository>;
  let mockVkApiRepo: jest.Mocked<IVkApiRepository>;

  beforeEach(() => {
    mockGroupsRepo = {
      save: jest.fn(),
      findAll: jest.fn()
    } as any;

    mockVkApiRepo = {
      getGroupsInfo: jest.fn()
    } as any;

    useCase = new UploadGroupsUseCase(
      mockGroupsRepo,
      mockVkApiRepo,
      // ... другие моки
    );
  });

  it('должен создать задачу загрузки', async () => {
    const result = await useCase.execute(input);
    expect(result).toHaveProperty('taskId');
  });
});
```

### Unit тесты для Domain Entities

```typescript
describe('Group Entity', () => {
  it('должен создать валидную группу', () => {
    const group = Group.create({
      vkId: VkId.create(123),
      name: 'Test',
      status: GroupStatus.valid()
    });

    expect(group.name).toBe('Test');
  });

  it('должен выбросить ошибку при пустом имени', () => {
    expect(() => {
      Group.create({
        vkId: VkId.create(123),
        name: '',
        status: GroupStatus.valid()
      });
    }).toThrow(InvariantViolationError);
  });
});
```

### Integration тесты

```typescript
describe('Groups API', () => {
  beforeAll(() => {
    initializeContainer(vkToken);
  });

  it('должен загрузить файл групп', async () => {
    const response = await request(app)
      .post('/api/groups/upload')
      .attach('file', testFile);

    expect(response.status).toBe(200);
    expect(response.body.data).toHaveProperty('taskId');
  });
});
```

## Миграция legacy кода

### Постепенный переход

1. **Создайте новые компоненты** рядом со старыми
2. **Перенаправьте трафик** на новые endpoints
3. **Удалите старый код** после успешной миграции

### Адаптеры для legacy

Если нужно использовать старый код:

```typescript
// Адаптер для legacy service
export class LegacyServiceAdapter implements INewInterface {
  constructor(private readonly legacyService: OldService) {}

  async newMethod(): Promise<Result> {
    const oldResult = await this.legacyService.oldMethod();
    return this.mapToNewFormat(oldResult);
  }
}
```

## Best Practices

1. **Domain Layer** должен быть независимым
2. **Use Cases** должны быть маленькими и сфокусированными
3. **DTOs** должны быть readonly
4. **Entities** должны защищать свои инварианты
5. **Repository** не должны содержать бизнес-логику
6. **Controllers** должны быть тонкими обертками над Use Cases
7. **Тесты** должны покрывать все Use Cases и Domain Logic

## Дополнительные ресурсы

- [Clean Architecture (Robert C. Martin)](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html)
- [Domain-Driven Design](https://martinfowler.com/bliki/DomainDrivenDesign.html)
- [Dependency Inversion Principle](https://en.wikipedia.org/wiki/Dependency_inversion_principle)

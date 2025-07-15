# Code Examples

Документ содержит краткие примеры кода для типовых сущностей и операций проекта (backend и frontend).

---

## Backend (FastAPI, SQLAlchemy, Pydantic)

### 1. SQLAlchemy-модель
```python
class User(BaseModel):
    __tablename__ = "users"
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
```

### 2. Pydantic-схема
```python
class UserCreate(UserBase):
    password: str
```

### 3. CRUD-сервис (BaseService)
```python
class BaseService(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    async def get(self, db: AsyncSession, id: Any) -> Optional[ModelType]:
        result = await db.execute(select(self.model).filter(self.model.id == id))
        return result.scalar_one_or_none()
    async def create(self, db: AsyncSession, *, obj_in: CreateSchemaType) -> ModelType:
        db_obj = self.model(**jsonable_encoder(obj_in))
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj
```

### 4. API endpoint (FastAPI)
```python
@router.post("/", response_model=VKGroupRead)
async def create_group(group_data: VKGroupCreate, db: AsyncSession = Depends(get_db)):
    new_group = VKGroup(**group_data.dict())
    db.add(new_group)
    await db.commit()
    await db.refresh(new_group)
    return VKGroupRead.model_validate(new_group)
```

---

## Frontend (Next.js, TypeScript, Zustand, React Query)

### 1. UI-компонент (Button)
```tsx
export const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant, size, asChild = false, ...props }, ref) => {
    const Comp = asChild ? Slot : 'button'
    return (
      <Comp className={cn(buttonVariants({ variant, size, className }))} ref={ref} {...props} />
    )
  }
)
```

### 2. React-хук для работы с API (React Query)
```ts
export function useGroups(params?: PaginationParams) {
  return useQuery({
    queryKey: createQueryKey.groups(params),
    queryFn: () => api.getGroups(params),
    staleTime: 5 * 60 * 1000,
  })
}
```

### 3. Zustand store (глобальное состояние)
```ts
export const useAppStore = create<AppStore>()(
  devtools(
    persist((set, get) => ({
      settings: defaultSettings,
      updateSettings: (newSettings) => set((state) => ({ settings: { ...state.settings, ...newSettings } })),
      // ... другие методы
    }))
  )
)
```

---

## Прочее

- Для всех сущностей используются строгие типы и схемы (Pydantic, TypeScript).
- Все операции с БД — асинхронные (async/await).
- Для работы с API на фронте используются хуки и React Query.
- Глобальное состояние — через Zustand store.

Документ приведён к минимально необходимому объёму для понимания основных паттернов кода. 
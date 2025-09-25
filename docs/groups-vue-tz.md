# Техническое задание: Страница управления группами VK (Vue.js)

## 1. Обзор фичи

### Цель
Создать интерфейс для загрузки и управления списком VK групп с возможностью массовой загрузки из TXT файла и мониторинга процесса обработки.

### Контекст
Frontend на Vue 3 + Vuetify 3 + Pinia. Интеграция с существующим backend API для загрузки групп. Соответствие дизайн-системе приложения.

## 2. Функциональные требования

### 2.1 Основные страницы
- **Страница загрузки групп** (`/groups/upload`) - загрузка TXT файла
- **Страница списка групп** (`/groups`) - просмотр загруженных групп
- **Страница статуса задачи** (`/groups/task/:taskId`) - мониторинг обработки

### 2.2 Загрузка файла
- Drag & Drop интерфейс для TXT файлов
- Валидация файла (размер до 10MB, только .txt)
- Выбор кодировки (UTF-8 по умолчанию)
- Предварительный просмотр содержимого
- Прогресс-бар загрузки

### 2.3 Управление группами
- Таблица с пагинацией (20 групп на страницу)
- Фильтрация по статусу (valid, invalid, duplicate)
- Поиск по ID группы или названию
- Сортировка по дате загрузки, статусу
- Массовые операции (удаление, экспорт)

### 2.4 Мониторинг задач
- Real-time обновление статуса (WebSocket или polling)
- Прогресс-бар обработки
- Список ошибок валидации
- Детальная статистика

## 3. Структура компонентов

### 3.1 Страницы
```
src/views/groups/
├── GroupsUpload.vue      # Загрузка файла
├── GroupsList.vue        # Список групп
└── GroupsTaskStatus.vue  # Статус задачи
```

### 3.2 Компоненты
```
src/components/groups/
├── FileUploader.vue      # Drag & Drop загрузчик
├── GroupsTable.vue       # Таблица групп
├── GroupsFilters.vue     # Фильтры и поиск
├── TaskProgress.vue      # Прогресс задачи
└── GroupsStats.vue       # Статистика
```

### 3.3 Store
```
src/stores/groups.js      # Управление состоянием групп
```

## 4. API интеграция

### 4.1 Endpoints
```javascript
// services/api.js
export const groupsApi = {
  // Загрузка файла
  uploadGroups: (file, encoding = 'utf-8') => 
    post('/api/groups/upload', formData, { headers: { 'Content-Type': 'multipart/form-data' }}),
  
  // Статус задачи
  getTaskStatus: (taskId) => 
    get(`/api/groups/upload/${taskId}/status`),
  
  // Список групп
  getGroups: (params) => 
    get('/api/groups', { params }),
  
  // Удаление группы
  deleteGroup: (groupId) => 
    delete(`/api/groups/${groupId}`),
  
  // Массовое удаление
  deleteGroups: (groupIds) => 
    delete('/api/groups/batch', { data: { groupIds }})
}
```

### 4.2 Типы данных
```typescript
interface Group {
  id: number
  name?: string
  status: 'valid' | 'invalid' | 'duplicate'
  taskId: string
  uploadedAt: string
}

interface UploadTask {
  taskId: string
  totalGroups: number
  validGroups: number
  invalidGroups: number
  duplicates: number
}

interface TaskStatus {
  status: 'created' | 'processing' | 'completed' | 'failed'
  progress: {
    processed: number
    total: number
    percentage: number
  }
  errors: Array<{
    groupId: string
    error: string
  }>
}
```

## 5. Store (Pinia)

### 5.1 groups.js
```javascript
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { groupsApi } from '@/services/api'

export const useGroupsStore = defineStore('groups', () => {
  // State
  const groups = ref([])
  const currentTask = ref(null)
  const loading = ref(false)
  const error = ref(null)
  const filters = ref({
    status: 'all',
    search: '',
    sortBy: 'uploadedAt',
    sortOrder: 'desc'
  })
  const pagination = ref({
    page: 1,
    limit: 20,
    total: 0
  })

  // Getters
  const filteredGroups = computed(() => {
    let filtered = groups.value

    // Фильтр по статусу
    if (filters.value.status !== 'all') {
      filtered = filtered.filter(group => group.status === filters.value.status)
    }

    // Поиск
    if (filters.value.search) {
      const search = filters.value.search.toLowerCase()
      filtered = filtered.filter(group => 
        group.id.toString().includes(search) ||
        (group.name && group.name.toLowerCase().includes(search))
      )
    }

    // Сортировка
    filtered.sort((a, b) => {
      const aVal = a[filters.value.sortBy]
      const bVal = b[filters.value.sortBy]
      return filters.value.sortOrder === 'asc' ? aVal - bVal : bVal - aVal
    })

    return filtered
  })

  // Actions
  const uploadGroups = async (file, encoding) => {
    loading.value = true
    error.value = null
    try {
      const formData = new FormData()
      formData.append('file', file)
      formData.append('encoding', encoding)
      
      const response = await groupsApi.uploadGroups(formData, encoding)
      currentTask.value = response.data
      return response.data
    } catch (err) {
      error.value = err.message
      throw err
    } finally {
      loading.value = false
    }
  }

  const fetchGroups = async (params = {}) => {
    loading.value = true
    try {
      const response = await groupsApi.getGroups({
        ...pagination.value,
        ...filters.value,
        ...params
      })
      groups.value = response.data.groups
      pagination.value.total = response.data.total
    } catch (err) {
      error.value = err.message
    } finally {
      loading.value = false
    }
  }

  const pollTaskStatus = async (taskId) => {
    try {
      const response = await groupsApi.getTaskStatus(taskId)
      currentTask.value = response.data
      
      if (response.data.status === 'completed') {
        await fetchGroups()
      }
      
      return response.data
    } catch (err) {
      error.value = err.message
      throw err
    }
  }

  const deleteGroup = async (groupId) => {
    try {
      await groupsApi.deleteGroup(groupId)
      groups.value = groups.value.filter(g => g.id !== groupId)
    } catch (err) {
      error.value = err.message
      throw err
    }
  }

  const updateFilters = (newFilters) => {
    filters.value = { ...filters.value, ...newFilters }
    pagination.value.page = 1
    fetchGroups()
  }

  return {
    // State
    groups,
    currentTask,
    loading,
    error,
    filters,
    pagination,
    
    // Getters
    filteredGroups,
    
    // Actions
    uploadGroups,
    fetchGroups,
    pollTaskStatus,
    deleteGroup,
    updateFilters
  }
})
```

## 6. Компоненты

### 6.1 FileUploader.vue
```vue
<template>
  <v-card class="file-uploader" elevation="2">
    <v-card-title class="d-flex align-center">
      <v-icon class="mr-2">mdi-upload</v-icon>
      Загрузка файла групп
    </v-card-title>
    
    <v-card-text>
      <v-file-input
        v-model="file"
        accept=".txt"
        label="Выберите TXT файл"
        prepend-icon="mdi-file-document"
        :rules="fileRules"
        @change="onFileChange"
      />
      
      <v-select
        v-model="encoding"
        :items="encodingOptions"
        label="Кодировка файла"
        class="mt-4"
      />
      
      <v-btn
        :disabled="!file || uploading"
        :loading="uploading"
        color="primary"
        class="mt-4"
        @click="handleUpload"
      >
        Загрузить группы
      </v-btn>
    </v-card-text>
    
    <!-- Drag & Drop зона -->
    <div
      v-show="!file"
      class="drop-zone"
      :class="{ 'drag-over': isDragOver }"
      @drop="onDrop"
      @dragover="onDragOver"
      @dragleave="onDragLeave"
    >
      <v-icon size="48" color="grey">mdi-cloud-upload</v-icon>
      <p class="text-h6 mt-2">Перетащите TXT файл сюда</p>
      <p class="text-caption">или нажмите для выбора</p>
    </div>
  </v-card>
</template>

<script setup>
import { ref } from 'vue'
import { useGroupsStore } from '@/stores/groups'
import { useRouter } from 'vue-router'

const groupsStore = useGroupsStore()
const router = useRouter()

const file = ref(null)
const encoding = ref('utf-8')
const uploading = ref(false)
const isDragOver = ref(false)

const encodingOptions = [
  { title: 'UTF-8', value: 'utf-8' },
  { title: 'Windows-1251', value: 'windows-1251' },
  { title: 'KOI8-R', value: 'koi8-r' }
]

const fileRules = [
  v => !!v || 'Выберите файл',
  v => !v || v.size <= 10 * 1024 * 1024 || 'Файл должен быть меньше 10MB',
  v => !v || v.type === 'text/plain' || 'Выберите TXT файл'
]

const onFileChange = (file) => {
  if (file) {
    console.log('Файл выбран:', file.name)
  }
}

const onDrop = (e) => {
  e.preventDefault()
  isDragOver.value = false
  
  const files = e.dataTransfer.files
  if (files.length > 0) {
    file.value = files[0]
  }
}

const onDragOver = (e) => {
  e.preventDefault()
  isDragOver.value = true
}

const onDragLeave = () => {
  isDragOver.value = false
}

const handleUpload = async () => {
  if (!file.value) return
  
  uploading.value = true
  try {
    const task = await groupsStore.uploadGroups(file.value, encoding.value)
    router.push(`/groups/task/${task.taskId}`)
  } catch (error) {
    console.error('Ошибка загрузки:', error)
  } finally {
    uploading.value = false
  }
}
</script>

<style scoped>
.file-uploader {
  max-width: 600px;
  margin: 0 auto;
}

.drop-zone {
  border: 2px dashed #ccc;
  border-radius: 8px;
  padding: 40px;
  text-align: center;
  transition: all 0.3s ease;
  cursor: pointer;
}

.drop-zone.drag-over {
  border-color: #1976d2;
  background-color: rgba(25, 118, 210, 0.05);
}
</style>
```

### 6.2 GroupsTable.vue
```vue
<template>
  <v-card>
    <v-card-title class="d-flex justify-space-between align-center">
      <span>Список групп ({{ pagination.total }})</span>
      <v-btn
        color="primary"
        prepend-icon="mdi-plus"
        @click="$emit('upload')"
      >
        Загрузить группы
      </v-btn>
    </v-card-title>
    
    <v-data-table
      :headers="headers"
      :items="groups"
      :loading="loading"
      :items-per-page="pagination.limit"
      :page="pagination.page"
      @update:page="onPageChange"
      @update:items-per-page="onItemsPerPageChange"
    >
      <template v-slot:item.status="{ item }">
        <v-chip
          :color="getStatusColor(item.status)"
          size="small"
        >
          {{ getStatusText(item.status) }}
        </v-chip>
      </template>
      
      <template v-slot:item.actions="{ item }">
        <v-btn
          icon="mdi-delete"
          size="small"
          color="error"
          @click="deleteGroup(item.id)"
        />
      </template>
    </v-data-table>
  </v-card>
</template>

<script setup>
import { computed } from 'vue'
import { useGroupsStore } from '@/stores/groups'

const emit = defineEmits(['upload'])

const groupsStore = useGroupsStore()
const { groups, loading, pagination } = storeToRefs(groupsStore)

const headers = [
  { title: 'ID группы', key: 'id', sortable: true },
  { title: 'Название', key: 'name', sortable: true },
  { title: 'Статус', key: 'status', sortable: true },
  { title: 'Дата загрузки', key: 'uploadedAt', sortable: true },
  { title: 'Действия', key: 'actions', sortable: false }
]

const getStatusColor = (status) => {
  const colors = {
    valid: 'success',
    invalid: 'error',
    duplicate: 'warning'
  }
  return colors[status] || 'default'
}

const getStatusText = (status) => {
  const texts = {
    valid: 'Валидная',
    invalid: 'Невалидная',
    duplicate: 'Дубликат'
  }
  return texts[status] || status
}

const deleteGroup = async (groupId) => {
  if (confirm('Удалить группу?')) {
    await groupsStore.deleteGroup(groupId)
  }
}

const onPageChange = (page) => {
  groupsStore.updateFilters({ page })
}

const onItemsPerPageChange = (limit) => {
  groupsStore.updateFilters({ limit, page: 1 })
}
</script>
```

## 7. Роутинг

### 7.1 Обновление router/index.js
```javascript
const routes = [
  // ... существующие маршруты
  {
    path: '/groups',
    component: () => import('@/views/groups/GroupsList.vue')
  },
  {
    path: '/groups/upload',
    component: () => import('@/views/groups/GroupsUpload.vue')
  },
  {
    path: '/groups/task/:taskId',
    component: () => import('@/views/groups/GroupsTaskStatus.vue')
  }
]
```

## 8. Обновление навигации

### 8.1 Sidebar.vue
```javascript
const menuItems = computed(() => [
  // ... существующие пункты
  {
    title: 'Группы VK',
    subtitle: 'Управление группами',
    to: '/groups',
    icon: 'mdi-account-group'
  }
])
```

## 9. Стили и UX

### 9.1 Дизайн-система
- Использование Vuetify 3 компонентов
- Цветовая схема: primary (#1976d2), success, warning, error
- Анимации: плавные переходы, hover эффекты
- Адаптивность: мобильная версия

### 9.2 UX принципы
- Интуитивная навигация
- Понятные сообщения об ошибках
- Прогресс-индикаторы для длительных операций
- Подтверждения для деструктивных действий

## 10. Тестирование

### 10.1 Unit тесты
- Компоненты: FileUploader, GroupsTable
- Store: actions, getters
- Утилиты: валидация файлов

### 10.2 E2E тесты
- Полный цикл загрузки файла
- Навигация между страницами
- Фильтрация и поиск

## 11. Критерии готовности

- [ ] Страница загрузки файла с валидацией
- [ ] Таблица групп с пагинацией и фильтрами
- [ ] Мониторинг статуса задачи в реальном времени
- [ ] Интеграция с backend API
- [ ] Адаптивный дизайн
- [ ] Обработка ошибок
- [ ] Unit и E2E тесты
- [ ] Обновление навигации

## 12. Дополнительные возможности

### 12.1 Экспорт данных
- CSV экспорт списка групп
- Фильтрация экспорта по статусу

### 12.2 Массовые операции
- Выбор нескольких групп
- Массовое удаление
- Изменение статуса

### 12.3 Статистика
- График загруженных групп по времени
- Распределение по статусам
- Топ групп по активности

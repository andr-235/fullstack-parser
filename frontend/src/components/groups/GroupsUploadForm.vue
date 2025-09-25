<template>
  <v-card elevation="2">
    <v-card-title class="d-flex align-center">
      <v-icon class="me-2" color="primary">mdi-upload</v-icon>
      Загрузка файла групп
    </v-card-title>

    <v-card-text>
      <v-form ref="formRef" v-model="isFormValid">
        <!-- File Input -->
        <v-file-input
          v-model="file"
          :accept="acceptedFileTypes"
          label="Выберите файл с группами"
          prepend-icon="mdi-file-document"
          variant="outlined"
          :rules="fileRules"
          @change="onFileChange"
        >
          <template #selection="{ fileNames }">
            <template v-for="fileName in fileNames" :key="fileName">
              <v-chip
                size="small"
                color="primary"
                variant="tonal"
                class="me-2"
                closable
                @click:close="clearFile"
              >
                <v-icon start size="small">
                  {{ getFileIcon(fileName) }}
                </v-icon>
                {{ fileName }}
              </v-chip>
            </template>
          </template>
        </v-file-input>

        <!-- Encoding Select -->
        <v-select
          v-model="encoding"
          :items="encodingOptions"
          item-title="title"
          item-value="value"
          label="Кодировка файла"
          variant="outlined"
          class="mt-4"
        />

        <!-- File Info -->
        <div v-if="fileInfo" class="mt-4">
          <v-card variant="tonal" color="info" class="pa-3">
            <div class="text-body-2">
              <div><strong>Размер:</strong> {{ formatFileSize(fileInfo.size) }}</div>
              <div><strong>Тип:</strong> {{ fileInfo.type || 'Неизвестно' }}</div>
              <div><strong>Последнее изменение:</strong> {{ formatDate(fileInfo.lastModified) }}</div>
            </div>
          </v-card>
        </div>

        <!-- Upload Button -->
        <v-btn
          :disabled="!isFormValid || uploading"
          :loading="uploading"
          color="primary"
          variant="flat"
          size="large"
          class="mt-6 w-100"
          @click="handleUpload"
          prepend-icon="mdi-cloud-upload"
        >
          {{ uploading ? 'Загрузка...' : 'Загрузить группы' }}
        </v-btn>

        <!-- Error Alert -->
        <v-alert
          v-if="error"
          type="error"
          class="mt-4"
          variant="tonal"
          :text="error"
        />
      </v-form>
    </v-card-text>

    <!-- Drag & Drop Zone -->
    <div
      v-if="!file"
      class="drop-zone ma-4"
      :class="{ 'drag-over': isDragOver }"
      @drop="onDrop"
      @dragover="onDragOver"
      @dragleave="onDragLeave"
      @click="$refs.formRef?.$el.querySelector('input[type=file]')?.click()"
    >
      <v-icon size="64" color="primary" class="mb-3">
        mdi-cloud-upload-outline
      </v-icon>
      <h4 class="text-h6 mb-2">Перетащите файл сюда</h4>
      <p class="text-body-2 text-medium-emphasis mb-2">
        или нажмите для выбора
      </p>
      <p class="text-caption text-medium-emphasis">
        Поддерживаются файлы: TXT, CSV (до 10 МБ)
      </p>
    </div>

    <!-- Upload Progress -->
    <div v-if="uploading" class="ma-4">
      <v-progress-linear
        indeterminate
        color="primary"
        height="6"
        rounded
      />
      <p class="text-center text-caption mt-2">
        Загрузка файла на сервер...
      </p>
    </div>
  </v-card>
</template>

<script setup>
import { ref, computed } from 'vue'
import { groupsApi } from '@/services/api'

const emit = defineEmits(['upload-started'])

// Reactive data
const formRef = ref(null)
const file = ref(null)
const encoding = ref('utf-8')
const uploading = ref(false)
const isDragOver = ref(false)
const error = ref('')
const isFormValid = ref(false)

// Computed
const acceptedFileTypes = '.txt,.csv'

const fileInfo = computed(() => {
  if (!file.value || Array.isArray(file.value) && file.value.length === 0) {
    return null
  }
  const f = Array.isArray(file.value) ? file.value[0] : file.value
  return {
    name: f.name,
    size: f.size,
    type: f.type,
    lastModified: f.lastModified
  }
})

// Data
const encodingOptions = [
  { title: 'UTF-8', value: 'utf-8' },
  { title: 'Windows-1251 (Кириллица)', value: 'windows-1251' },
  { title: 'KOI8-R (Кириллица)', value: 'koi8-r' },
  { title: 'ISO-8859-1 (Latin-1)', value: 'iso-8859-1' }
]

// Validation rules
const fileRules = [
  (value) => {
    if (!value || (Array.isArray(value) && value.length === 0)) {
      return 'Выберите файл для загрузки'
    }

    const f = Array.isArray(value) ? value[0] : value

    // Check file extension
    const allowedExtensions = ['.txt', '.csv']
    const extension = '.' + f.name.split('.').pop().toLowerCase()
    if (!allowedExtensions.includes(extension)) {
      return 'Поддерживаются только файлы TXT и CSV'
    }

    // Check file size (10MB limit)
    const maxSize = 10 * 1024 * 1024 // 10MB
    if (f.size > maxSize) {
      return 'Размер файла не должен превышать 10 МБ'
    }

    return true
  }
]

// Methods
const clearFile = () => {
  file.value = null
  error.value = ''
}

const onFileChange = (event) => {
  error.value = ''
}

const onDrop = (e) => {
  e.preventDefault()
  isDragOver.value = false

  const files = Array.from(e.dataTransfer.files)
  if (files.length > 0) {
    file.value = files[0]
    error.value = ''
  }
}

const onDragOver = (e) => {
  e.preventDefault()
  isDragOver.value = true
}

const onDragLeave = (e) => {
  e.preventDefault()
  isDragOver.value = false
}

const handleUpload = async () => {
  if (!isFormValid.value || !file.value) return

  uploading.value = true
  error.value = ''

  try {
    const f = Array.isArray(file.value) ? file.value[0] : file.value

    // Create FormData
    const formData = new FormData()
    formData.append('file', f)

    // Upload file
    const response = await groupsApi.uploadGroups(formData, encoding.value)

    // Emit success event
    emit('upload-started', response.data)

    // Clear form
    clearFile()
  } catch (err) {
    error.value = err.response?.data?.message || err.message || 'Ошибка загрузки файла'
    console.error('Error uploading file:', err)
  } finally {
    uploading.value = false
  }
}

// Helper functions
const getFileIcon = (fileName) => {
  const extension = fileName.split('.').pop().toLowerCase()
  const icons = {
    'txt': 'mdi-file-document-outline',
    'csv': 'mdi-file-table-outline'
  }
  return icons[extension] || 'mdi-file-outline'
}

const formatFileSize = (bytes) => {
  if (bytes === 0) return '0 Б'

  const k = 1024
  const sizes = ['Б', 'КБ', 'МБ', 'ГБ']
  const i = Math.floor(Math.log(bytes) / Math.log(k))

  return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i]
}

const formatDate = (timestamp) => {
  if (!timestamp) return 'Неизвестно'

  const date = new Date(timestamp)
  return new Intl.DateTimeFormat('ru-RU', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  }).format(date)
}
</script>

<style scoped>
.drop-zone {
  border: 2px dashed rgba(var(--v-theme-primary), 0.3);
  border-radius: 12px;
  padding: 48px 24px;
  text-align: center;
  transition: all 0.3s ease;
  cursor: pointer;
  background: rgba(var(--v-theme-surface), 0.5);
}

.drop-zone:hover {
  border-color: rgba(var(--v-theme-primary), 0.6);
  background: rgba(var(--v-theme-primary), 0.04);
}

.drop-zone.drag-over {
  border-color: var(--v-theme-primary);
  background: rgba(var(--v-theme-primary), 0.08);
  transform: scale(1.02);
}
</style>
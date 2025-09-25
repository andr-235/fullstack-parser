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

const emit = defineEmits(['upload-success'])

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
  v => {
    if (!v) return 'Выберите файл'
    if (Array.isArray(v)) {
      return v.length > 0 ? true : 'Выберите файл'
    }
    return v.type === 'text/plain' || 'Выберите TXT файл'
  }
]


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
    const response = await groupsStore.uploadGroups(file.value, encoding.value)
    emit('upload-success', response)
    
    // taskId находится в response.data.taskId
    const taskId = response.data?.taskId
    if (taskId) {
      router.push(`/groups/task/${taskId}`)
    }
  } catch (error) {
    console.error('Ошибка загрузки:', error)
  } finally {
    uploading.value = false
  }
}
</script>

<style scoped>
.file-uploader {
  width: 600px;
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

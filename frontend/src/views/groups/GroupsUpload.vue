<template>
  <div class="pa-6">
    <div class="d-flex justify-center">
      <FileUploader @upload-success="onUploadSuccess" />
    </div>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'
import FileUploader from '@/components/groups/FileUploader.vue'

const router = useRouter()

const onUploadSuccess = (task) => {
  console.log('Загрузка успешна:', task)
  // Перенаправление происходит в компоненте FileUploader
}
</script>

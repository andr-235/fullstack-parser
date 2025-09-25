<template>
  <v-dialog
    :model-value="modelValue"
    @update:model-value="$emit('update:modelValue', $event)"
    max-width="500px"
    persistent
  >
    <v-card>
      <v-card-title class="d-flex align-center">
        <v-icon class="me-2" color="blue">mdi-comment-multiple</v-icon>
        Создать задачу комментариев
      </v-card-title>

      <v-card-text>
        <v-form ref="formRef" v-model="isFormValid" @submit.prevent="handleSubmit">
          <v-row>
            <!-- Owner ID -->
            <v-col cols="12">
              <v-text-field
                v-model="form.ownerId"
                label="ID владельца (ownerId) *"
                type="number"
                variant="outlined"
                :rules="ownerIdRules"
                required
                persistent-hint
                hint="Отрицательное число для группы (например: -123456)"
              />
            </v-col>

            <!-- Post ID -->
            <v-col cols="12">
              <v-text-field
                v-model="form.postId"
                label="ID поста (postId) *"
                type="number"
                variant="outlined"
                :rules="postIdRules"
                required
                persistent-hint
                hint="Положительное число ID поста"
              />
            </v-col>

            <!-- VK Token -->
            <v-col cols="12">
              <v-text-field
                v-model="form.token"
                label="VK токен доступа *"
                type="password"
                variant="outlined"
                :rules="tokenRules"
                required
                persistent-hint
                hint="Токен доступа VK API для получения комментариев"
                :append-inner-icon="showToken ? 'mdi-eye' : 'mdi-eye-off'"
                @click:append-inner="showToken = !showToken"
                :type="showToken ? 'text' : 'password'"
              />
            </v-col>
          </v-row>

          <v-alert
            v-if="error"
            type="error"
            class="mt-4"
            :text="error"
            variant="tonal"
          />
        </v-form>
      </v-card-text>

      <v-card-actions>
        <v-spacer />
        <v-btn
          variant="text"
          @click="handleCancel"
          :disabled="loading"
        >
          Отмена
        </v-btn>
        <v-btn
          color="primary"
          variant="flat"
          @click="handleSubmit"
          :loading="loading"
          :disabled="!isFormValid"
        >
          Создать задачу
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script setup>
import { ref, watch } from 'vue'
import { useTasksStore } from '@/stores/tasks'

// Props & Emits
const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['update:modelValue', 'created'])

// Store
const tasksStore = useTasksStore()

// Reactive data
const formRef = ref(null)
const isFormValid = ref(false)
const loading = ref(false)
const error = ref('')
const showToken = ref(false)

// Form data
const form = ref({
  ownerId: '',
  postId: '',
  token: ''
})

// Validation rules
const ownerIdRules = [
  (value) => !!value || 'Owner ID обязателен',
  (value) => !isNaN(value) || 'Owner ID должен быть числом',
  (value) => parseInt(value) < 0 || 'Owner ID должен быть отрицательным числом'
]

const postIdRules = [
  (value) => !!value || 'Post ID обязателен',
  (value) => !isNaN(value) || 'Post ID должен быть числом',
  (value) => parseInt(value) > 0 || 'Post ID должен быть положительным числом'
]

const tokenRules = [
  (value) => !!value || 'VK токен обязателен',
  (value) => value.length >= 10 || 'VK токен слишком короткий'
]

// Methods
const resetForm = () => {
  form.value = {
    ownerId: '',
    postId: '',
    token: ''
  }
  error.value = ''
  if (formRef.value) {
    formRef.value.resetValidation()
  }
}

const handleCancel = () => {
  if (!loading.value) {
    resetForm()
    emit('update:modelValue', false)
  }
}

const handleSubmit = async () => {
  if (!isFormValid.value) return

  loading.value = true
  error.value = ''

  try {
    const taskData = {
      ownerId: parseInt(form.value.ownerId),
      postId: parseInt(form.value.postId),
      token: form.value.token
    }

    const response = await tasksStore.createTask(taskData)

    emit('created', { taskId: response.taskId || tasksStore.taskId })
    resetForm()
  } catch (err) {
    error.value = err.response?.data?.message || err.message || 'Ошибка создания задачи'
    console.error('Error creating comments task:', err)
  } finally {
    loading.value = false
  }
}

// Watch for dialog changes
watch(() => props.modelValue, (newValue) => {
  if (!newValue) {
    resetForm()
  }
})
</script>
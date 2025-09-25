<template>
  <v-dialog
    :model-value="modelValue"
    @update:model-value="$emit('update:modelValue', $event)"
    max-width="600px"
    persistent
  >
    <v-card>
      <v-card-title class="d-flex align-center">
        <v-icon class="me-2" color="green">mdi-download</v-icon>
        Создать VK Collect задачу
      </v-card-title>

      <v-card-text>
        <v-form ref="formRef" v-model="isFormValid" @submit.prevent="handleSubmit">
          <v-row>
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
                hint="Токен доступа VK API для получения данных"
                :append-inner-icon="showToken ? 'mdi-eye' : 'mdi-eye-off'"
                @click:append-inner="showToken = !showToken"
                :type="showToken ? 'text' : 'password'"
              />
            </v-col>

            <!-- Groups Input -->
            <v-col cols="12">
              <v-textarea
                v-model="groupsInput"
                label="ID групп *"
                variant="outlined"
                :rules="groupsRules"
                required
                persistent-hint
                hint="Список положительных ID групп, разделенных запятыми или новыми строками"
                rows="4"
                auto-grow
              />
            </v-col>

            <!-- Parsed Groups Preview -->
            <v-col v-if="parsedGroups.length > 0" cols="12">
              <v-expansion-panels variant="accordion">
                <v-expansion-panel>
                  <v-expansion-panel-title>
                    <div class="d-flex align-center">
                      <v-icon class="me-2" color="success">mdi-check-circle</v-icon>
                      Найдено {{ parsedGroups.length }} {{ getGroupsText(parsedGroups.length) }}
                    </div>
                  </v-expansion-panel-title>
                  <v-expansion-panel-text>
                    <div class="d-flex flex-wrap gap-2">
                      <v-chip
                        v-for="groupId in parsedGroups"
                        :key="groupId"
                        size="small"
                        color="primary"
                        variant="tonal"
                      >
                        {{ groupId }}
                      </v-chip>
                    </div>
                  </v-expansion-panel-text>
                </v-expansion-panel>
              </v-expansion-panels>
            </v-col>

            <!-- Validation Errors -->
            <v-col v-if="validationErrors.length > 0" cols="12">
              <v-alert type="warning" variant="tonal">
                <div class="font-weight-medium mb-2">
                  Обнаружены ошибки в ID групп:
                </div>
                <ul class="text-caption">
                  <li
                    v-for="(error, index) in validationErrors.slice(0, 5)"
                    :key="index"
                  >
                    {{ error }}
                  </li>
                  <li v-if="validationErrors.length > 5">
                    ... и еще {{ validationErrors.length - 5 }} ошибок
                  </li>
                </ul>
              </v-alert>
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
          :disabled="!isFormValid || parsedGroups.length === 0"
        >
          Создать задачу
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
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
  token: ''
})

const groupsInput = ref('')
const validationErrors = ref([])

// Computed
const parsedGroups = computed(() => {
  if (!groupsInput.value.trim()) return []

  const lines = groupsInput.value
    .split(/[,\n\r]/)
    .map(line => line.trim())
    .filter(line => line.length > 0)

  const groups = []
  validationErrors.value = []

  lines.forEach((line, index) => {
    const num = parseInt(line)
    if (isNaN(num)) {
      validationErrors.value.push(`Строка ${index + 1}: "${line}" не является числом`)
    } else if (num <= 0) {
      validationErrors.value.push(`Строка ${index + 1}: ${num} должно быть положительным числом`)
    } else if (groups.includes(num)) {
      validationErrors.value.push(`Строка ${index + 1}: ${num} уже добавлен`)
    } else {
      groups.push(num)
    }
  })

  return groups
})

// Validation rules
const tokenRules = [
  (value) => !!value || 'VK токен обязателен',
  (value) => value.length >= 10 || 'VK токен слишком короткий'
]

const groupsRules = [
  (value) => !!value.trim() || 'Список групп обязателен',
  () => parsedGroups.value.length > 0 || 'Необходимо указать хотя бы одну корректную группу',
  () => validationErrors.value.length === 0 || 'Исправьте ошибки в списке групп'
]

// Methods
const resetForm = () => {
  form.value = {
    token: ''
  }
  groupsInput.value = ''
  validationErrors.value = []
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
  if (!isFormValid.value || parsedGroups.value.length === 0) return

  loading.value = true
  error.value = ''

  try {
    const taskData = {
      groups: parsedGroups.value,
      token: form.value.token
    }

    const response = await tasksStore.createVkCollectTask(taskData)

    emit('created', { taskId: response.taskId })
    resetForm()
  } catch (err) {
    error.value = err.response?.data?.message || err.message || 'Ошибка создания задачи'
    console.error('Error creating VK collect task:', err)
  } finally {
    loading.value = false
  }
}

const getGroupsText = (count) => {
  const lastDigit = count % 10
  const lastTwoDigits = count % 100

  if (lastTwoDigits >= 11 && lastTwoDigits <= 14) {
    return 'групп'
  }

  if (lastDigit === 1) return 'группа'
  if (lastDigit >= 2 && lastDigit <= 4) return 'группы'
  return 'групп'
}

// Watch for dialog changes
watch(() => props.modelValue, (newValue) => {
  if (!newValue) {
    resetForm()
  }
})
</script>
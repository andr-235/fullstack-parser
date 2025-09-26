<template>
  <v-dialog
    :model-value="modelValue"
    @update:model-value="$emit('update:modelValue', $event)"
    max-width="700px"
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
            <!-- Groups Selection -->
            <v-col cols="12">
              <v-select
                v-model="selectedGroups"
                :items="availableGroups"
                item-title="displayName"
                item-value="id"
                label="Выберите группы *"
                variant="outlined"
                multiple
                chips
                closable-chips
                :rules="groupsSelectionRules"
                :loading="groupsLoading"
                :disabled="groupsLoading"
                required
                persistent-hint
                hint="Выберите группы из загруженных в базу данных"
                :menu-props="{ maxHeight: 300 }"
              >
                <template v-slot:prepend-item>
                  <v-list-item>
                    <v-list-item-action>
                      <v-checkbox
                        :model-value="selectedGroups.length === availableGroups.length"
                        :indeterminate="selectedGroups.length > 0 && selectedGroups.length < availableGroups.length"
                        @click="toggleAllGroups"
                      ></v-checkbox>
                    </v-list-item-action>
                    <v-list-item-title>Выбрать все</v-list-item-title>
                  </v-list-item>
                  <v-divider></v-divider>
                </template>
                <template v-slot:selection="{ item, index }">
                  <v-chip v-if="index < 3" size="small" color="primary" variant="tonal">
                    {{ item.title }}
                  </v-chip>
                  <span v-if="index === 3" class="text-caption text-grey ml-2">
                    +{{ selectedGroups.length - 3 }} еще
                  </span>
                </template>
              </v-select>
            </v-col>

            <!-- Selected Groups Preview -->
            <v-col v-if="selectedGroups.length > 0" cols="12">
              <v-expansion-panels variant="accordion">
                <v-expansion-panel>
                  <v-expansion-panel-title>
                    <div class="d-flex align-center">
                      <v-icon class="me-2" color="success">mdi-check-circle</v-icon>
                      Выбрано {{ selectedGroups.length }} {{ getGroupsText(selectedGroups.length) }}
                    </div>
                  </v-expansion-panel-title>
                  <v-expansion-panel-text>
                    <div class="d-flex flex-wrap gap-2">
                      <v-chip
                        v-for="groupId in selectedGroups"
                        :key="groupId"
                        size="small"
                        color="primary"
                        variant="tonal"
                        closable
                        @click:close="removeGroup(groupId)"
                      >
                        {{ getGroupDisplayName(groupId) }}
                      </v-chip>
                    </div>
                  </v-expansion-panel-text>
                </v-expansion-panel>
              </v-expansion-panels>
            </v-col>

            <!-- No Groups Available Message -->
            <v-col v-if="!groupsLoading && availableGroups.length === 0" cols="12">
              <v-alert type="info" variant="tonal">
                <div class="font-weight-medium mb-2">
                  Нет доступных групп
                </div>
                <p class="text-body-2 mb-0">
                  Сначала загрузите группы через раздел "Управление группами".
                </p>
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
          :disabled="!isFormValid || selectedGroups.length === 0 || groupsLoading"
        >
          Создать задачу
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { useTasksStore } from '@/stores/tasks'
import { useGroupsStore } from '@/stores/groups'

// Props & Emits
const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['update:modelValue', 'created'])

// Stores
const tasksStore = useTasksStore()
const groupsStore = useGroupsStore()

// Reactive data
const formRef = ref(null)
const isFormValid = ref(false)
const loading = ref(false)
const error = ref('')
const groupsLoading = ref(false)

// Form data
const selectedGroups = ref([])
const availableGroups = ref([])

// Computed
const groupsMap = computed(() => {
  const map = new Map()
  availableGroups.value.forEach(group => {
    map.set(group.id, group)
  })
  return map
})

// Validation rules
const groupsSelectionRules = [
  (value) => (value && value.length > 0) || 'Необходимо выбрать хотя бы одну группу'
]

// Methods
const loadGroups = async () => {
  groupsLoading.value = true
  try {
    const groups = await groupsStore.getAllGroups()
    availableGroups.value = groups.map(group => ({
      id: group.id,
      name: group.name || `Группа ${group.id}`,
      displayName: group.name ? `${group.name} (ID: ${group.id})` : `Группа ${group.id}`
    }))
  } catch (err) {
    error.value = 'Ошибка загрузки групп: ' + (err.message || 'Неизвестная ошибка')
    console.error('Error loading groups:', err)
  } finally {
    groupsLoading.value = false
  }
}

const resetForm = () => {
  selectedGroups.value = []
  error.value = ''
  if (formRef.value) {
    formRef.value.resetValidation()
  }
}

const toggleAllGroups = () => {
  if (selectedGroups.value.length === availableGroups.value.length) {
    selectedGroups.value = []
  } else {
    selectedGroups.value = availableGroups.value.map(group => group.id)
  }
}

const removeGroup = (groupId) => {
  const index = selectedGroups.value.indexOf(groupId)
  if (index > -1) {
    selectedGroups.value.splice(index, 1)
  }
}

const getGroupDisplayName = (groupId) => {
  const group = groupsMap.value.get(groupId)
  return group ? group.name : `Группа ${groupId}`
}

const handleCancel = () => {
  if (!loading.value) {
    resetForm()
    emit('update:modelValue', false)
  }
}

const handleSubmit = async () => {
  if (!isFormValid.value || selectedGroups.value.length === 0) return

  loading.value = true
  error.value = ''

  try {
    const taskData = {
      groups: selectedGroups.value
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

// Lifecycle
onMounted(() => {
  loadGroups()
})

// Watch for dialog changes
watch(() => props.modelValue, async (newValue) => {
  if (newValue) {
    await loadGroups()
  } else {
    resetForm()
  }
})
</script>
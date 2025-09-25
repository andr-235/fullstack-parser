<template>
  <div class="pa-6">
    <h1 class="text-h4 mb-6">Управление группами VK</h1>
    
    <GroupsFilters />
    <GroupsTable @upload="goToUpload" />
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useGroupsStore } from '@/stores/groups'
import GroupsFilters from '@/components/groups/GroupsFilters.vue'
import GroupsTable from '@/components/groups/GroupsTable.vue'

const router = useRouter()
const groupsStore = useGroupsStore()

const goToUpload = () => {
  router.push('/groups/upload')
}

onMounted(() => {
  groupsStore.fetchGroups()
})
</script>

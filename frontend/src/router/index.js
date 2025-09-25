import { createRouter, createWebHistory } from "vue-router"

/**
 * Создает и конфигурирует роутер Vue.
 * @returns {Object} Экземпляр роутера.
 */
const routes = [
  { path: "/", redirect: "/tasks" },
  // Tasks routes
  {
    path: "/tasks",
    component: () => import("@/views/TasksView.vue")
  },
  {
    path: "/tasks/:taskId",
    component: () => import("@/views/TaskDetailsView.vue")
  },
  // Legacy routes (for backward compatibility)
  {
    path: "/fetch",
    component: () => import("@/views/FetchComments.vue")
  },
  {
    path: "/task/:taskId",
    component: () => import("@/views/TaskStatus.vue")
  },
  {
    path: "/comments",
    component: () => import("@/views/CommentsList.vue")
  },
  // Groups routes
  {
    path: "/groups",
    component: () => import("@/views/groups/GroupsList.vue")
  },
  {
    path: "/groups/upload",
    component: () => import("@/views/groups/GroupsUpload.vue")
  },
  {
    path: "/groups/task/:taskId",
    component: () => import("@/views/groups/GroupsTaskStatus.vue")
  },
  {
    path: "/groups/stats/:taskId",
    component: () => import("@/views/groups/GroupsStatsView.vue")
  }
]

export default createRouter({
  history: createWebHistory(),
  routes
})
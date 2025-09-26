import { createApp } from "vue"
import App from "./App.vue"

import { createVuetify } from "vuetify"
import "vuetify/styles"
import * as components from "vuetify/components"
import * as directives from "vuetify/directives"
import { aliases, mdi } from 'vuetify/iconsets/mdi'
import '@mdi/font/css/materialdesignicons.css'

import router from "./router"
import { createPinia } from "./stores"
const pinia = createPinia()

const vuetify = createVuetify({
  components,
  directives,
  icons: {
    defaultSet: 'mdi',
    aliases,
    sets: {
      mdi,
    },
  },
})

createApp(App)
  .use(router)
  .use(pinia)
  .use(vuetify)
  .mount("#app")
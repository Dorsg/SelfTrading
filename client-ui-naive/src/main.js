import { createApp } from 'vue'
import App from './App.vue'
import { createNaiveUI } from './naive'

const app = createApp(App)
app.use(createNaiveUI())
app.mount('#app')
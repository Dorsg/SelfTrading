// main.js
import { createApp } from 'vue'
import App from './App.vue'

// --- AG Grid themes FIRST ---
import 'ag-grid-community/dist/styles/ag-grid.css'
import 'ag-grid-community/dist/styles/ag-theme-alpine-dark.css'

// Quasar core & icons
import { Quasar } from 'quasar'
import 'quasar/dist/quasar.css'
import '@quasar/extras/material-icons/material-icons.css'

// --- Your global overrides LAST ---
import '@/css/general.css'


// ✅ Manually import Quasar components you use
import {
  QDialog,
  QCard,
  QCardSection,
  QSeparator,
  QForm,
  QInput,
  QCheckbox,
  QBtn,
  QTabs,  
  QTab,
  QTable
} from 'quasar'

// Register everything manually
const app = createApp(App)

app.use(Quasar, {
  components: {
    QDialog,
    QCard,
    QCardSection,
    QSeparator,
    QForm,
    QInput,
    QCheckbox,
    QBtn,
    QTabs,
    QTab,
    QTable
  },
  plugins: {} // optionally: Dialog, Notify, etc.
})

app.mount('#app')

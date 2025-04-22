<template>
  <div class="runners-tab page-wrapper">
    <div class="header-bar">
      <h2>Self Runners</h2>
      <div v-if="runnersLastUpdate" class="last-updated">
        Last update on: {{ formatTimestamp(runnersLastUpdate) }}
      </div>
    </div>
    
    <!-- Action Bar -->
    <div class="action-bar">
      <n-button @click="showCreateForm = true">Create Runner</n-button>
      <n-button @click="removeRunner">Remove Runner</n-button>
      <n-button @click="removeAllRunners">Remove All</n-button>
      <n-button @click="activateRunner">Activate Runner</n-button>
    </div>

    <!-- Create Runner Form (floating dialog) -->
    <n-modal v-model:show="showCreateForm" preset="card" title="Create Runner" style="width: 600px">
      <CreateRunnerForm @create="createRunner" @cancel="cancelCreateForm" />
    </n-modal>
    <!-- Runners Grid -->
    <n-card class="card" :style="{ height: '500px', width: '100%' }">
      <ag-grid-vue
        class="ag-theme-alpine-dark"
        :style="{ width: '100%', height: '100%' }"
        :columnDefs="columnDefs"
        :defaultColDef="defaultColDef"
        :rowData="runners"
        :statusBar="statusBar"
        pagination
        :paginationPageSize="25"
        rowSelection="single"
        :animateRows="true"
        @grid-ready="onGridReady"
      />
    </n-card>
  </div>
</template>

<script setup>
import { ref, nextTick, onMounted, onUnmounted } from 'vue'
import { AgGridVue } from 'ag-grid-vue3'
// You can replace this with an actual fetch function later
// import { fetchRunners } from '@/services/dataFetcher'
import 'ag-grid-community/dist/styles/ag-grid.css'
import 'ag-grid-community/dist/styles/ag-theme-alpine-dark.css'

import CreateRunnerForm from '@/components/runners_actions/CreateRunnerForm.vue'

const showCreateForm = ref(false)


// Define mock runners data for now
const runners = ref([
  { id: 1, name: 'Runner 1', strategy: 'Strategy A', budget: 5000, stock: 'AAPL', time_frame: 30, stop_loss: 5, take_profit: 10, time_range: '2023-01-01 to 2023-03-01', commission_ratio: 0.02, exit_strategy: '2023-03-01 15:00:00', created_at: '2023-01-01 10:00:00' },
  { id: 2, name: 'Runner 2', strategy: 'Strategy B', budget: 10000, stock: 'GOOGL', time_frame: 60, stop_loss: 7, take_profit: 12, time_range: '2023-02-01 to 2023-04-01', commission_ratio: 0.015, exit_strategy: '2023-04-01 16:00:00', created_at: '2023-02-01 12:00:00' }
])

const runnersLastUpdate = ref(null)
let gridApi, resizeHandler

// Default column definition for sorting and filtering
const defaultColDef = {
  flex: 1,
  minWidth: 100,
  resizable: true,
  sortable: true,  // Enable sorting for all columns
  filter: true,    // Enable filtering for all columns
}

// Column definitions for the runners grid
const columnDefs = [
  { headerName: 'ID', field: 'id', sortable: true, filter: true },
  { headerName: 'Name', field: 'name', sortable: true, filter: true },
  { headerName: 'Strategy', field: 'strategy', sortable: true, filter: true },
  { headerName: 'Budget', field: 'budget', sortable: true, filter: true },
  { headerName: 'Stock', field: 'stock', sortable: true, filter: true },
  { headerName: 'Time Frame', field: 'time_frame', sortable: true, filter: true },
  { headerName: 'Risk% (Stop Loss)', field: 'stop_loss', sortable: true, filter: true },
  { headerName: 'Take Profit at %', field: 'take_profit', sortable: true, filter: true },
  { headerName: 'Time Range', field: 'time_range', sortable: true, filter: true },
  { headerName: 'Commission:Price Ratio', field: 'commission_ratio', sortable: true, filter: true },
  { headerName: 'Exit Strategy', field: 'exit_strategy', sortable: true, filter: true },
  { headerName: 'Created Date and Time', field: 'created_at', sortable: true, filter: 'agDateColumnFilter' }
]

// Status bar configuration for row count and pagination
const statusBar = {
  statusPanels: [
    { statusPanel: 'agTotalRowCountComponent', align: 'left' },
    { statusPanel: 'agFilteredRowCountComponent', align: 'left' },
    { statusPanel: 'agPaginationComponent', align: 'right' }
  ]
}

// Helper function to format the timestamp
function formatTimestamp(ts) {
  return new Date(ts).toLocaleString()
}

// Function to load runners data (replace with API call in the future)
async function loadRunners() {
  // Replace with the actual API call
  // runners.value = await fetchRunners()
  // Mock last update time
  if (runners.value.length) runnersLastUpdate.value = runners.value[0].created_at
  nextTick(() => gridApi?.sizeColumnsToFit())
}

// Handle grid initialization and resizing
function onGridReady(p) {
  gridApi = p.api
  gridApi.sizeColumnsToFit()
  resizeHandler = () => gridApi?.sizeColumnsToFit()
  window.addEventListener('resize', resizeHandler)
}

// Cleanup when component is unmounted
onUnmounted(() => {
  window.removeEventListener('resize', resizeHandler)
  gridApi = null
})

// Load data when the component is mounted
onMounted(loadRunners)

// Action bar methods
function createRunner(newRunnerData) {
  console.log("Received runner data:", newRunnerData)

  // Add the new runner to the list (mock implementation for now)
  const newRunner = {
    id: runners.value.length + 1,
    ...newRunnerData,
    created_at: new Date().toISOString()
  }

  runners.value.push(newRunner)
  showCreateForm.value = false
  runnersLastUpdate.value = newRunner.created_at
}

function cancelCreateForm() {
  showCreateForm.value = false
}

function removeRunner() {
  console.log("Remove Runner clicked")
  // Implement the logic for removing a runner
}

function removeAllRunners() {
  console.log("Remove All clicked")
  // Implement the logic for removing all runners
}

function activateRunner() {
  console.log("Activate Runner clicked")
  // Implement the logic for activating a runner
}
</script>

<style scoped>
.runners-tab .header-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card {
  margin-top: 20px;
}

.grid-wrapper {
  flex: 1;
  width: 100%;
  height: 100%;
}

.ag-theme-alpine-dark {
  width: 100%;
  height: 100%;
}

.action-bar {
  margin-bottom: 20px;
  display: flex;
  gap: 10px;
}
</style>

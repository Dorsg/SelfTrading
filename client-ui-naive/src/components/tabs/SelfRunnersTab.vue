<template>
  <div class="runners-tab page-wrapper">
    <div class="header-bar">
      <h2>Self Runners</h2>
    </div>

    <!-- Action Bar with Last Update -->
    <div class="action-bar">
      <div class="buttons">
        <n-button @click="showCreateForm = true">Create Runner</n-button>
        <n-button @click="removeRunner">Remove Runner</n-button>
        <n-button @click="InactiveRunner">Inactive Runner</n-button>
        <n-button @click="activateRunner">Activate Runner</n-button>
      </div>
      <div v-if="runnersLastUpdate" class="last-updated">
        Last update on: {{ formatTimestamp(runnersLastUpdate) }}
      </div>
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
        rowSelection="multiple"
        :animateRows="true"
        @grid-ready="onGridReady"
      />
    </n-card>
  </div>
</template>

<script setup>
import { ref, nextTick, onMounted, onUnmounted } from 'vue'
import { AgGridVue } from 'ag-grid-vue3'
import 'ag-grid-community/dist/styles/ag-grid.css'
import 'ag-grid-community/dist/styles/ag-theme-alpine-dark.css'

import CreateRunnerForm from '@/components/runners_actions/CreateRunnerForm.vue'

const showCreateForm = ref(false)
const runners = ref(JSON.parse(localStorage.getItem('runners') || '[]'))
const runnersLastUpdate = ref(null)

let gridApi, resizeHandler

const defaultColDef = {
  flex: 1,
  minWidth: 100,
  resizable: true,
  sortable: true,
  filter: true,
}

const columnDefs = [
  {
    headerName: '',
    checkboxSelection: true,
    headerCheckboxSelection: true,
    width: 10,
  },
  {
    headerName: 'Activation',
    field: 'activation',
    cellRenderer: (params) => {
      return params.value === 'active'
        ? '🟢 Active'
        : '🔴 Inactive'
    },
    width: 120
  },
  { headerName: 'ID', field: 'id' },
  { headerName: 'Name', field: 'name' },
  { headerName: 'Strategy', field: 'strategy' },
  { headerName: 'Budget', field: 'budget' },
  { headerName: 'Stock', field: 'stock' },
  { headerName: 'Time Frame (min)', field: 'time_frame' },
  { headerName: 'Risk % (Stop Loss)', field: 'stop_loss' },
  { headerName: 'Take Profit %', field: 'take_profit' },
  { headerName: 'Start Date', field: 'time_range_from' },
  { headerName: 'End Date', field: 'time_range_to' },
  { headerName: 'Commission Ratio', field: 'commission_ratio' },
  { headerName: 'Exit Strategy', field: 'exit_strategy' },
  { headerName: 'Created At', field: 'created_at' }
]

const statusBar = {
  statusPanels: [
    { statusPanel: 'agTotalRowCountComponent', align: 'left' },
    { statusPanel: 'agFilteredRowCountComponent', align: 'left' },
    { statusPanel: 'agPaginationComponent', align: 'right' }
  ]
}

function formatTimestamp(ts) {
  return new Date(ts).toLocaleString()
}

function createRunner(newRunnerData) {
  const [from, to] = newRunnerData.timeRange || [null, null]

  const newRunner = {
    id: runners.value.length + 1,
    name: newRunnerData.name,
    strategy: newRunnerData.strategy,
    budget: newRunnerData.budget,
    stock: newRunnerData.stock,
    time_frame: newRunnerData.timeFrame,
    stop_loss: newRunnerData.stopLoss,
    take_profit: newRunnerData.takeProfit,
    time_range_from: new Date(from).toLocaleString(),
    time_range_to: new Date(to).toLocaleString(),
    commission_ratio: newRunnerData.commissionRatio,
    exit_strategy: newRunnerData.exitStrategy.join(', '),
    created_at: new Date().toLocaleString(),
    activation: 'active'
  }

  runners.value.push(newRunner)
  saveRunners()

  // 🔥 Force AG Grid to refresh the view
  if (gridApi) {
    gridApi.setRowData(runners.value)
  }

  showCreateForm.value = false
  runnersLastUpdate.value = newRunner.created_at
}

function cancelCreateForm() {
  showCreateForm.value = false
}


function activateRunner() {
  const selectedNodes = gridApi.getSelectedNodes()
  if (selectedNodes.length === 0) return

  selectedNodes.forEach(node => {
    const runner = runners.value.find(r => r.id === node.data.id)
    if (runner) runner.activation = 'active'
  })

  gridApi.setRowData([...runners.value])
  saveRunners()
}

function InactiveRunner() {
  const selectedNodes = gridApi.getSelectedNodes()
  if (selectedNodes.length === 0) return

  selectedNodes.forEach(node => {
    const runner = runners.value.find(r => r.id === node.data.id)
    if (runner) runner.activation = 'inactive'
  })

  gridApi.setRowData([...runners.value])
  saveRunners()
}

function onGridReady(p) {
  gridApi = p.api
  gridApi.sizeColumnsToFit()
  resizeHandler = () => gridApi?.sizeColumnsToFit()
  window.addEventListener('resize', resizeHandler)
}

function saveRunners() {
  localStorage.setItem('runners', JSON.stringify(runners.value))
}

function removeRunner() {
  if (!gridApi) return

  const selectedNodes = gridApi.getSelectedNodes()
  const selectedIds = selectedNodes.map(node => node.data.id)

  if (selectedIds.length === 0) {
    console.warn("No rows selected for deletion")
    return
  }

  // Remove selected rows from the runners array
  runners.value = runners.value.filter(runner => !selectedIds.includes(runner.id))

  // Optionally update last update timestamp
  runnersLastUpdate.value = runners.value.length ? runners.value[0].created_at : null

  // Refresh the grid (optional, but good for syncing selection UI)
  gridApi.setRowData(runners.value)
  saveRunners()
}

onUnmounted(() => {
  window.removeEventListener('resize', resizeHandler)
  gridApi = null
})

onMounted(() => {
  nextTick(() => gridApi?.sizeColumnsToFit())
})
</script>

<style scoped>
.runners-tab .header-bar {
  display: flex;
  align-items: center;
  margin-bottom: 10px;
}

.action-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  margin-bottom: 20px;
}

.action-bar .buttons {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

.last-updated {
  font-size: 14px;
  color: #aaa;
  white-space: nowrap;
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
</style>

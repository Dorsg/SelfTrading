<template>
  <div class="runners-tab page-wrapper">
    <div class="header-bar">
      <h2>Self Runners</h2>
    </div>

    <!-- Action Bar with Last Update -->
    <div class="action-bar">
      <n-button-group class="button-group">
        <n-button @click="showCreateForm = true">
          <template #icon>
            <n-icon><AddOutline /></n-icon>
          </template>
          Create
        </n-button>
        <n-button @click="removeRunner">
          <template #icon>
            <n-icon><TrashOutline /></n-icon>
          </template>
          Remove
        </n-button>
        <n-button @click="InactiveRunner">
          <template #icon>
            <n-icon><PauseOutline /></n-icon>
          </template>
          Inactivate
        </n-button>
        <n-button @click="activateRunner">
          <template #icon>
            <n-icon><PlayOutline /></n-icon>
          </template>
          Reactivate
        </n-button>
      </n-button-group>
      <div v-if="runnersLastUpdate" class="last-updated">
        Last update on: {{ formatTimestamp(runnersLastUpdate) }}
      </div>
    </div>

    <!-- Create Runner Form (floating dialog) -->
    <n-modal
      v-model:show="showCreateForm"
      preset="card"
      title="Create Runner"
      style="width: 600px"
    >
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
import {
  AddOutline,
  TrashOutline,
  PauseOutline,
  PlayOutline,
} from "@vicons/ionicons5";
import { useMessage } from 'naive-ui';
import { ref, nextTick, onMounted, onUnmounted } from "vue";
import { AgGridVue } from "ag-grid-vue3";
import "ag-grid-community/dist/styles/ag-grid.css";
import "ag-grid-community/dist/styles/ag-theme-alpine-dark.css";

import CreateRunnerForm from "@/components/runners_actions/CreateRunnerForm.vue";

// 👇 Import API methods
import {
  createRunnerAPI,
  deleteRunnersAPI,
  activateRunnersAPI,
  deactivateRunnersAPI,
} from "@/services/dataManager";

const showCreateForm = ref(false);
const runners = ref(JSON.parse(localStorage.getItem("runners") || "[]"));
const runnersLastUpdate = ref(null);
const message = useMessage();

let gridApi, resizeHandler;

const defaultColDef = {
  flex: 1,
  minWidth: 100,
  resizable: true,
  sortable: true,
  filter: true,
};

const columnDefs = [
  {
    headerName: "",
    checkboxSelection: true,
    headerCheckboxSelection: true,
    width: 10,
  },
  { headerName: "ID", field: "id" },
  { headerName: "Name", field: "name" },
  { headerName: "Strategy", field: "strategy" },
  {
    headerName: "Activation",
    field: "activation",
    cellRenderer: (params) => {
      return params.value === "active" ? "🟢 Active" : "🔴 Inactive";
    },
    width: 120,
  },
  { headerName: "Budget", field: "budget" },
  { headerName: "Stock", field: "stock" },
  { headerName: "Time Frame (min)", field: "time_frame" },
  { headerName: "Risk % (Stop Loss)", field: "stop_loss" },
  { headerName: "Take Profit %", field: "take_profit" },
  { headerName: "Start Date", field: "time_range_from" },
  { headerName: "End Date", field: "time_range_to" },
  { headerName: "Commission Ratio", field: "commission_ratio" },
  { headerName: "Exit Strategy", field: "exit_strategy" },
  { headerName: "Created At", field: "created_at" },
];

const statusBar = {
  statusPanels: [
    { statusPanel: "agTotalRowCountComponent", align: "left" },
    { statusPanel: "agFilteredRowCountComponent", align: "left" },
    { statusPanel: "agPaginationComponent", align: "right" },
  ],
};

function formatTimestamp(ts) {
  return new Date(ts).toLocaleString();
}

async function createRunner(newRunnerData) {
  const [from, to] = newRunnerData.timeRange || [null, null];

  const newRunner = {
    id: runners.value.length + 1,
    name: newRunnerData.name,
    strategy: newRunnerData.strategy,
    budget: newRunnerData.budget,
    stock: newRunnerData.stock.toUpperCase(),
    time_frame: newRunnerData.timeFrame,
    stop_loss: newRunnerData.stopLoss,
    take_profit: newRunnerData.takeProfit,
    time_range_from: new Date(newRunnerData.startTime).toLocaleString(),
    time_range_to:
      newRunnerData.exitStrategy.includes("expired date") &&
      newRunnerData.endTime
        ? new Date(newRunnerData.endTime).toLocaleString()
        : "Until strategy triggers",
    commission_ratio: newRunnerData.commissionRatio,
    exit_strategy: newRunnerData.exitStrategy.join(", "),
    created_at: new Date().toLocaleString(),
    activation: "active",
  };

  const savedRunner = await createRunnerAPI(newRunner);
  if (savedRunner) {
    runners.value.push(savedRunner);
    saveRunners();
    if (gridApi) gridApi.setRowData(runners.value);
    showCreateForm.value = false;
    runnersLastUpdate.value = savedRunner.created_at;
  }
}

function cancelCreateForm() {
  showCreateForm.value = false;
}

async function activateRunner() {
  const selectedNodes = gridApi.getSelectedNodes();
  if (!selectedNodes.length) {
    message.warning("No runner selected for activation.");
    return;
  }

  const ids = selectedNodes.map((node) => node.data.id);
  const result = await activateRunnersAPI(ids);

  if (result) {
    selectedNodes.forEach((node) => {
      const runner = runners.value.find((r) => r.id === node.data.id);
      if (runner) runner.activation = "active";
    });

    gridApi.setRowData([...runners.value]);
    saveRunners();
  }
}

async function InactiveRunner() {
  const selectedNodes = gridApi.getSelectedNodes();
  if (!selectedNodes.length) {
    message.warning("No runner selected for inactivation.");
    return;
  }

  const ids = selectedNodes.map((node) => node.data.id);
  const result = await deactivateRunnersAPI(ids);

  if (result) {
    selectedNodes.forEach((node) => {
      const runner = runners.value.find((r) => r.id === node.data.id);
      if (runner) runner.activation = "inactive";
    });

    gridApi.setRowData([...runners.value]);
    saveRunners();
  }
}

async function removeRunner() {
  if (!gridApi) return;

  const selectedNodes = gridApi.getSelectedNodes();
  const selectedIds = selectedNodes.map((node) => node.data.id);

  if (!selectedIds.length) {
    message.warning("No runner selected for deletion.");
    return;
  }

  const result = await deleteRunnersAPI(selectedIds);

  if (result) {
    runners.value = runners.value.filter((r) => !selectedIds.includes(r.id));
    runnersLastUpdate.value = runners.value.length
      ? runners.value[0].created_at
      : null;
    gridApi.setRowData(runners.value);
    saveRunners();
  }
}

function onGridReady(params) {
  gridApi = params.api;
  const columnApi = params.columnApi;

  resizeHandler = () => gridApi?.sizeColumnsToFit();
  window.addEventListener("resize", resizeHandler);

  nextTick(() => {
    autoSizeAllColumns(columnApi);
  });
}

function autoSizeAllColumns(columnApi) {
  if (!columnApi) return;

  const allColumnIds = columnApi.getColumns().map((col) => col.getColId());
  columnApi.autoSizeColumns(allColumnIds, false);
}

function saveRunners() {
  localStorage.setItem("runners", JSON.stringify(runners.value));
}

onUnmounted(() => {
  window.removeEventListener("resize", resizeHandler);
  gridApi = null;
});

onMounted(() => {
  nextTick(() => {
    if (gridApi) gridApi.setRowData(runners.value);
    if (runners.value.length) {
      runnersLastUpdate.value = runners.value[0].created_at;
    }
  });
});
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

.ag-header-cell-label {
  white-space: normal !important;
  line-height: 1.2 !important;
}
</style>

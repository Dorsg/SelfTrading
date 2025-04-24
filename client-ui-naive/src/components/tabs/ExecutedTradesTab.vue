<template>
  <div class="executed-trades-tab page-wrapper">
    <div class="header-bar">
      <h2>Executed Trades</h2>
      <div v-if="executedTradesLastUpdate" class="last-updated">
        Last update on: {{ formatTimestamp(executedTradesLastUpdate) }}
      </div>
    </div>

    <n-card class="card" :style="{ height: '500px', width: '100%' }">
      <ag-grid-vue
        class="ag-theme-alpine-dark"
        :style="{ width: '100%', height: '100%' }"
        :columnDefs="columnDefs"
        :defaultColDef="defaultColDef"
        :rowData="executedTrades"
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
import { ref, nextTick, onMounted, onUnmounted } from "vue";
import { AgGridVue } from "ag-grid-vue3";
import { fetchExecutedTrades } from "@/services/dataManager";
import "ag-grid-community/dist/styles/ag-grid.css";
import "ag-grid-community/dist/styles/ag-theme-alpine-dark.css";

const executedTrades = ref([]); // Data for executed trades
const executedTradesLastUpdate = ref(null); // Last update timestamp
let gridApi, resizeHandler;

// Default column definition for sorting and filtering
const defaultColDef = {
  flex: 1,
  minWidth: 100,
  resizable: true,
  sortable: true, // Enable sorting for all columns
  filter: true, // Enable filtering for all columns
};

// Column definitions for the executed trades grid
const columnDefs = [
  { headerName: "ID", field: "id", sortable: true, filter: true },
  { headerName: "Symbol", field: "symbol", sortable: true, filter: true },
  { headerName: "Action", field: "action", sortable: true, filter: true },
  {
    headerName: "Order Type",
    field: "order_type",
    sortable: true,
    filter: true,
  },
  { headerName: "Quantity", field: "quantity", sortable: true, filter: true },
  { headerName: "Price", field: "price", sortable: true, filter: true },
  {
    headerName: "Fill Time",
    field: "fill_time",
    sortable: true,
    filter: "agDateColumnFilter",
  },
  { headerName: "Account", field: "account", sortable: true, filter: true },
];

// Status bar configuration for row count and pagination
const statusBar = {
  statusPanels: [
    { statusPanel: "agTotalRowCountComponent", align: "left" },
    { statusPanel: "agFilteredRowCountComponent", align: "left" },
    { statusPanel: "agPaginationComponent", align: "right" },
  ],
};

// Helper function to format the timestamp
function formatTimestamp(ts) {
  return new Date(ts).toLocaleString();
}

// Function to load executed trades from API
async function loadExecutedTrades() {
  executedTrades.value = await fetchExecutedTrades();
  if (executedTrades.value.length)
    executedTradesLastUpdate.value = executedTrades.value[0].fill_time;
  nextTick(() => gridApi?.sizeColumnsToFit());
}

// Handle grid initialization and resizing
function onGridReady(p) {
  gridApi = p.api;
  gridApi.sizeColumnsToFit();
  resizeHandler = () => gridApi?.sizeColumnsToFit();
  window.addEventListener("resize", resizeHandler);
}

// Cleanup when component is unmounted
onUnmounted(() => {
  window.removeEventListener("resize", resizeHandler);
  gridApi = null;
});

// Load data when the component is mounted
onMounted(loadExecutedTrades);
</script>

<style scoped>
.executed-trades-tab .header-bar {
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
</style>

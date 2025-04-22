<template>
    <div class="orders-tab page-wrapper">
      <div class="header-bar">
        <h2>Open Orders</h2>
        <div v-if="ordersLastUpdate" class="last-updated">
          Last update on: {{ formatTimestamp(ordersLastUpdate) }}
        </div>
      </div>
  
      <n-card class="card" :style="{ height: '500px', width: '100%' }">
        <ag-grid-vue
          class="ag-theme-alpine-dark"
          :style="{ width: '100%', height: '100%' }"
          :columnDefs="columnDefs"
          :defaultColDef="defaultColDef"
          :rowData="orders"
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
  import { fetchOrders } from '@/services/dataFetcher'
  import 'ag-grid-community/dist/styles/ag-grid.css'
  import 'ag-grid-community/dist/styles/ag-theme-alpine-dark.css'
  
  const orders = ref([])
  const ordersLastUpdate = ref(null)
  let gridApi, resizeHandler
  
  const defaultColDef = {
    flex: 1,
    minWidth: 100,
    resizable: true,
    sortable: true, // Enable sorting for all columns
    filter: true, // Enable filtering for all columns
  }
  
  const columnDefs = [
    { headerName: 'ID', field: 'id', sortable: true, filter: true },
    { headerName: 'Symbol', field: 'symbol', sortable: true, filter: true },
    { headerName: 'Qty', field: 'quantity', sortable: true, filter: true },
    { headerName: 'Action', field: 'action', sortable: true, filter: true },
    { headerName: 'Type', field: 'order_type', sortable: true, filter: true },
    { headerName: 'Limit', field: 'limit_price', sortable: true, filter: true },
    { headerName: 'Stop', field: 'stop_price', sortable: true, filter: true },
    { headerName: 'Status', field: 'status', sortable: true, filter: true },
    { headerName: 'Created', field: 'created_at', sortable: true, filter: 'agDateColumnFilter' },
    { headerName: 'Updated', field: 'last_updated', sortable: true, filter: 'agDateColumnFilter' }
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
  
  async function loadOrders() {
    orders.value = await fetchOrders()
    console.log(orders.value)  // Check the loaded data
    if (orders.value.length) ordersLastUpdate.value = orders.value[0].last_updated
    nextTick(() => gridApi?.sizeColumnsToFit())
  }
  
  function onGridReady(p) {
    gridApi = p.api
    gridApi.sizeColumnsToFit()
    resizeHandler = () => gridApi?.sizeColumnsToFit()
    window.addEventListener('resize', resizeHandler)
  }
  
  onUnmounted(() => {
    window.removeEventListener('resize', resizeHandler)
    gridApi = null
  })
  
  onMounted(loadOrders)
  </script>
  
  <style scoped>
  .orders-tab .header-bar {
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
  
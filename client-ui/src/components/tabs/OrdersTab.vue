<template>
  <div class="orders-tab page-wrapper">
    <div class="header-bar">
      <h2>Orders</h2>
      <div v-if="ordersLastUpdate" class="last-updated">
        Last update on: {{ formatTimestamp(ordersLastUpdate) }}
      </div>
    </div>

    <ag-grid-vue
      class="ag-theme-alpine-dark"
      style="width:100%; height:500px"
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
  </div>
</template>

<script setup>
import { ref, nextTick, onMounted, onUnmounted } from 'vue'
import { AgGridVue } from 'ag-grid-vue3'
import { fetchOrders } from '@/services/dataFetcher'
import 'ag-grid-community/dist/styles/ag-grid.css'
import 'ag-grid-community/dist/styles/ag-theme-alpine-dark.css'

const orders           = ref([])
const ordersLastUpdate = ref(null)
let gridApi, resizeHandler

const defaultColDef = { flex:1, minWidth:100, resizable:true }
const columnDefs = [
  { headerName:'ID',field:'id' },
  { headerName:'Symbol',field:'symbol' },
  { headerName:'Action',field:'action' },
  { headerName:'Type',field:'order_type' },
  { headerName:'Qty',field:'quantity',type:'rightAligned' },
  { headerName:'Limit',field:'limit_price',type:'rightAligned' },
  { headerName:'Stop',field:'stop_price',type:'rightAligned' },
  { headerName:'Status',field:'status' },
  { headerName:'Filled',field:'filled_quantity',type:'rightAligned' },
  { headerName:'Avg Fill',field:'avg_fill_price',type:'rightAligned' },
  { headerName:'Account',field:'account' },
  { headerName:'Created',field:'created_at' },
  { headerName:'Updated',field:'last_updated' }
]

/* Row‑count + pagination summary */
const statusBar = {
  statusPanels:[
    { statusPanel:'agTotalRowCountComponent',    align:'left' },
    { statusPanel:'agFilteredRowCountComponent', align:'left' },
    { statusPanel:'agPaginationComponent',       align:'right' }
  ]
}

function formatTimestamp(ts){ return new Date(ts).toLocaleString() }

async function loadOrders(){
  orders.value = await fetchOrders()
  if (orders.value.length) ordersLastUpdate.value = orders.value[0].last_updated
  nextTick(()=>gridApi?.sizeColumnsToFit())
}

function onGridReady(p){
  gridApi = p.api
  gridApi.sizeColumnsToFit()
  resizeHandler = ()=>gridApi?.sizeColumnsToFit()
  window.addEventListener('resize', resizeHandler)
}

onUnmounted(()=>{
  window.removeEventListener('resize', resizeHandler)
  gridApi = null
})

onMounted(loadOrders)
</script>

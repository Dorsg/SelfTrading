<template>
  <div class="trades-tab page-wrapper">
    <div class="header-bar">
      <h2>Executed Trades</h2>
      <div v-if="tradesLastUpdate" class="last-updated">
        Last update on: {{ formatTimestamp(tradesLastUpdate) }}
      </div>
    </div>

    <ag-grid-vue
      class="ag-theme-alpine-dark"
      style="width:100%; height:500px"
      :columnDefs="columnDefs"
      :rowData="trades"
      :statusBar="statusBar"
      pagination
      paginationAutoPageSize
      rowSelection="single"
      :animateRows="true"
      @grid-ready="onGridReady"
    />
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { AgGridVue }          from 'ag-grid-vue3'
import { fetchExecutedTrades } from '@/services/dataFetcher'
import 'ag-grid-community/dist/styles/ag-grid.css'
import 'ag-grid-community/dist/styles/ag-theme-alpine-dark.css'

const trades           = ref([])
const tradesLastUpdate = ref(null)
let gridApi, resizeHandler

const statusBar = {
  statusPanels:[
    { statusPanel:'agTotalRowCountComponent',    align:'left' },
    { statusPanel:'agFilteredRowCountComponent', align:'left' },
    { statusPanel:'agPaginationComponent',       align:'right' }
  ]
}

const columnDefs = [
  { headerName:'ID', field:'id' },
  { headerName:'Perm ID', field:'perm_id' },
  { headerName:'Symbol', field:'symbol' },
  { headerName:'Action', field:'action' },
  { headerName:'Type', field:'order_type' },
  { headerName:'Qty', field:'quantity', type:'rightAligned' },
  { headerName:'Price', field:'price', type:'rightAligned' },
  { headerName:'Filled At', field:'fill_time' },
  { headerName:'Account', field:'account' }
]

function formatTimestamp(ts){ return new Date(ts).toLocaleString() }

async function loadTrades(){
  trades.value = await fetchExecutedTrades()
  if (trades.value.length) tradesLastUpdate.value = trades.value[0].fill_time
}

function onGridReady(p){
  gridApi = p.api
  gridApi.sizeColumnsToFit()
  resizeHandler = ()=>gridApi?.sizeColumnsToFit()
  window.addEventListener('resize', resizeHandler)
}
onUnmounted(()=>{ window.removeEventListener('resize', resizeHandler); gridApi=null })
onMounted(loadTrades)
</script>

<template>
  <div class="account-info page-wrapper">
    <!-- snapshot card grid -->
    <div class="header-bar">
      <h2>Account Overview</h2>
      <div v-if="snapshot?.timestamp" class="last-updated">
        Last update on: {{ formatTimestamp(snapshot.timestamp) }}
      </div>
    </div>

    <div class="card-grid">
      <div class="card" v-for="(item, i) in formattedData" :key="i">
        <label>{{ item.label }}</label>
        <span :class="item.class">{{ item.value }}</span>
      </div>
    </div>

    <!-- positions table -->
    <q-card flat bordered class="dark-card q-mt-md">
      <q-card-section class="row items-center justify-between">
        <div class="text-h6">Open Positions ({{ openPositions.length }})</div>
        <div v-if="positionsLastUpdate" class="last-updated q-mt-none">
          Last update on: {{ formatTimestamp(positionsLastUpdate) }}
        </div>
      </q-card-section>

      <q-card-section>
        <q-table
          :rows="openPositions"
          :columns="positionsColumns"
          :pagination="{ rowsPerPage: 10 }"
          :rows-per-page-options="[10,25,50]"
          row-key="symbol"
          class="my-quasar-table"
        />
      </q-card-section>
    </q-card>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { fetchAccountSnapshot, fetchOpenPositions } from '@/services/dataFetcher'

const snapshot          = ref(null)
const openPositions     = ref([])
const positionsLastUpdate = ref(null)

const positionsColumns = [
  { name:'symbol',  label:'Symbol',      field:'symbol',  align:'center' },
  { name:'quantity', label:'Quantity',   field:'quantity',align:'center' },
  { name:'avg_price',label:'Avg Price',  field:'avg_price',align:'center'},
  { name:'account',  label:'Account',    field:'account', align:'center'},
  { name:'last_update',label:'Last Update',field:'last_update',align:'center'}
]

const formattedData = computed(() => {
  if (!snapshot.value) return []
  return [
    { label:'Account ID',   value:snapshot.value.account },
    { label:'Balance',      value:fmt$(snapshot.value.total_cash_value),'class':'highlight' },
    { label:'Buying Power', value:fmt$(snapshot.value.buying_power),      class:'highlight' },
    { label:'Unrealized PnL', value:fmt$(snapshot.value.unrealized_pnl),
      class: snapshot.value.unrealized_pnl >= 0 ? 'pnl-positive':'pnl-negative' },
    { label:'Realized PnL', value:fmt$(snapshot.value.realized_pnl),
      class: snapshot.value.realized_pnl >= 0 ? 'pnl-positive':'pnl-negative' }
  ]
})

function fmt$ (v) {
  return v != null ? `$${parseFloat(v).toLocaleString(undefined,{minimumFractionDigits:2})}` : '-'
}
function formatTimestamp(ts){ return new Date(ts).toLocaleString() }

async function loadData(){
  snapshot.value = await fetchAccountSnapshot()
  openPositions.value = await fetchOpenPositions()
  if (openPositions.value.length) positionsLastUpdate.value = openPositions.value[0].last_update
}

onMounted(loadData)
</script>

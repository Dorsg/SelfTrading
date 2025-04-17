<template>
  <div class="trades-tab">
    <!-- Styled header to match OrdersTab -->
    <div class="header-bar">
      <h2>Executed Trades</h2>
      <div v-if="tradesLastUpdate" class="last-updated">
        Last update on: {{ formatTimestamp(tradesLastUpdate) }}
      </div>
    </div>

    <!-- AG Grid styled exactly like OrdersTab -->
    <ag-grid-vue
      class="ag-theme-alpine-dark"
      style="width: 100%; height: 500px"
      :columnDefs="columnDefs"
      :rowData="trades"
      rowSelection="single"
      :animateRows="true"
      @grid-ready="onGridReady"
    />
  </div>
</template>

<script>
import { AgGridVue } from 'ag-grid-vue3';
import 'ag-grid-community/dist/styles/ag-grid.css';
import 'ag-grid-community/dist/styles/ag-theme-alpine-dark.css';
import { fetchExecutedTrades } from '@/services/dataFetcher';

export default {
  name: 'TradesTab',
  components: {
    AgGridVue
  },
  data() {
    return {
      trades: [],
      tradesLastUpdate: null,
      columnDefs: [
        { headerName: 'ID', field: 'id' },
        { headerName: 'Perm ID', field: 'perm_id' },
        { headerName: 'Symbol', field: 'symbol' },
        { headerName: 'Action', field: 'action' },
        { headerName: 'Type', field: 'order_type' },
        { headerName: 'Qty', field: 'quantity', type: 'rightAligned' },
        { headerName: 'Price', field: 'price', type: 'rightAligned' },
        { headerName: 'Filled At', field: 'fill_time' },
        { headerName: 'Account', field: 'account' }
      ]
    };
  },
  methods: {
    async loadTrades() {
      try {
        const data = await fetchExecutedTrades();
        this.trades = data;
        if (data.length) {
          this.tradesLastUpdate = data[0].fill_time;
        }
      } catch (err) {
        console.error('Failed to fetch executed trades:', err);
      }
    },
    formatTimestamp(ts) {
      return new Date(ts).toLocaleString();
    },
    onGridReady(params) {
      params.api.sizeColumnsToFit();
    }
  },
  mounted() {
    this.loadTrades();
  }
};
</script>

<style scoped>
h2 {
  margin: 0;
  font-size: 1.5rem;
  color: #00d1b2;
}

.trades-tab {
  padding: 10px;
  background-color: #2d2d2d;
  color: #fff;
}

.header-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.last-updated {
  font-size: 0.85rem;
  color: #bbb;
}

.ag-theme-alpine-dark {
  background-color: #2d2d2d;
  color: #e0e0e0;
}

.ag-header-cell {
  background-color: #444;
}

.ag-row {
  background-color: #333;
}

.ag-row:hover {
  background-color: #555;
}

.ag-cell {
  color: #ccc;
}
</style>

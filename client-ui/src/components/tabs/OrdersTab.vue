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
      style="width: 100%; height: 500px"
      :columnDefs="columnDefs"
      :rowData="orders"
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
import { fetchOrders } from '@/services/dataFetcher';

export default {
  name: 'OrdersTab',
  components: { AgGridVue },
  data() {
    return {
      orders: [],
      ordersLastUpdate: null,
      columnDefs: [
        { headerName: 'ID', field: 'id' },
        { headerName: 'Symbol', field: 'symbol' },
        { headerName: 'Action', field: 'action' },
        { headerName: 'Type', field: 'order_type' },
        { headerName: 'Qty', field: 'quantity', type: 'rightAligned' },
        { headerName: 'Limit', field: 'limit_price', type: 'rightAligned' },
        { headerName: 'Stop', field: 'stop_price', type: 'rightAligned' },
        { headerName: 'Status', field: 'status' },
        { headerName: 'Filled', field: 'filled_quantity', type: 'rightAligned' },
        { headerName: 'Avg Fill', field: 'avg_fill_price', type: 'rightAligned' },
        { headerName: 'Account', field: 'account' },
        { headerName: 'Created', field: 'created_at' },
        { headerName: 'Updated', field: 'last_updated' }
      ]
    };
  },
  methods: {
    async loadOrders() {
      try {
        const data = await fetchOrders();
        this.orders = data;
        if (data.length) this.ordersLastUpdate = data[0].last_updated;
      } catch (err) {
        console.error('Failed to fetch orders:', err);
      }
    },
    formatTimestamp(ts) { return new Date(ts).toLocaleString(); },
    onGridReady(params) { params.api.sizeColumnsToFit(); }
  },
  mounted() { this.loadOrders(); }
};
</script>

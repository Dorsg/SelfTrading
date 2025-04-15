<template>
  <div class="account-info">
    <div class="header-bar">
      <h2>Account Overview</h2>
      <div v-if="snapshot && snapshot.timestamp" class="last-updated">
        Last update on: {{ formatTimestamp(snapshot.timestamp) }}
      </div>
    </div>
    <div class="card-grid">
      <div class="card" v-for="(item, index) in formattedData" :key="index">
        <label>{{ item.label }}</label>
        <span :class="item.class">{{ item.value }}</span>
      </div>
    </div>
  </div>

  <div class="q-mt-md">
    <q-card flat bordered class="dark-card">
      <q-card-section>
        <div class="text-h6">Open Positions</div>
        <div v-if="positionsLastUpdate" class="last-updated">
          Last update on: {{ formatTimestamp(positionsLastUpdate) }}
        </div>
      </q-card-section>

      <q-card-section>
        <ag-grid-vue
          class="ag-theme-alpine-dark"
          style="width: 100%; height: 300px;"
          :columnDefs="positionsColumnDefs"
          :rowData="openPositions"
          :domLayout="'autoHeight'"
          :suppressMovableColumns="true"
          :pagination="false"
        />
      </q-card-section>
    </q-card>
  </div>
</template>

<script>
import { fetchAccountSnapshot, fetchOpenPositions } from '@/services/dataFetcher';
import { AgGridVue } from 'ag-grid-vue3';

export default {
  name: 'AccountInfoTab',
  components: { AgGridVue },
  data() {
    return {
      snapshot: null,
      openPositions: [],
      positionsLastUpdate: null,
      positionsColumnDefs: [
        { field: 'symbol', headerName: 'Symbol' },
        { field: 'quantity', headerName: 'Quantity' },
        { field: 'avg_price', headerName: 'Avg Price' },
        { field: 'account', headerName: 'Account' },
        { field: 'last_update', headerName: 'Last Update' },
      ],
    };
  },
  computed: {
    formattedData() {
      if (!this.snapshot) return [];
      return [
        { label: 'Account ID', value: this.snapshot.account },
        { label: 'Balance', value: this.formatDollar(this.snapshot.total_cash_value), class: 'highlight' },
        { label: 'Buying Power', value: this.formatDollar(this.snapshot.buying_power), class: 'highlight' },
        { label: 'Unrealized PnL', value: this.formatDollar(this.snapshot.unrealized_pnl), class: this.snapshot.unrealized_pnl >= 0 ? 'pnl-positive' : 'pnl-negative' },
        { label: 'Realized PnL', value: this.formatDollar(this.snapshot.realized_pnl), class: this.snapshot.realized_pnl >= 0 ? 'pnl-positive' : 'pnl-negative' },
        { label: 'Margin Ratio', value: this.getMarginRatio() },
      ];
    },
  },
  methods: {
    async loadSnapshot() {
      try {
        this.snapshot = await fetchAccountSnapshot();
      } catch (err) {
        console.error('Failed to fetch snapshot:', err);
      }
    },
    async loadOpenPositions() {
      try {
        const positions = await fetchOpenPositions();
        this.openPositions = positions;
        if (positions.length > 0) {
          this.positionsLastUpdate = positions[0].last_update;
        }
      } catch (err) {
        console.error('Failed to fetch open positions:', err);
      }
    },
    formatDollar(val) {
      return val != null ? `$${parseFloat(val).toLocaleString(undefined, { minimumFractionDigits: 2 })}` : '-';
    },
    getMarginRatio() {
      if (!this.snapshot || !this.snapshot.buying_power || !this.snapshot.total_cash_value) return '-';
      const ratio = 100 * (1 - (this.snapshot.buying_power / this.snapshot.total_cash_value));
      return `${ratio.toFixed(1)}%`;
    },
    formatTimestamp(timestamp) {
      const date = new Date(timestamp);
      return date.toLocaleString();
    },
  },
  mounted() {
    this.loadSnapshot();
    this.loadOpenPositions();
  },
};
</script>

<style scoped>
.account-info {
  padding: 0 10px 10px 10px;
}

.header-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

h2 {
  margin: 0;
  font-size: 1.5rem;
  color: #00d1b2;
}

.last-updated {
  font-size: 0.9rem;
  color: #aaa;
  margin-top: 5px;
}

.card-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 16px;
}

.card, .dark-card {
  background-color: #333;
  padding: 16px;
  border-radius: 8px;
  display: flex;
  flex-direction: column;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.3);
  color: #e0e0e0;
}

label {
  font-size: 0.9rem;
  color: #bbb;
  margin-bottom: 6px;
}

span {
  font-size: 1.2rem;
  font-weight: 600;
  color: #e0e0e0;
}

.highlight {
  color: #00d1b2;
}

.pnl-positive {
  color: #4caf50;
}

.pnl-negative {
  color: #e53935;
}

.ag-theme-alpine-dark {
  --ag-background-color: #2c2c2c;
  --ag-foreground-color: #e0e0e0;
  --ag-header-background-color: #1f1f1f;
  --ag-header-foreground-color: #ccc;
}
</style>

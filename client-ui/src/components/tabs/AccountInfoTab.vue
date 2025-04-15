<template>
  <div class="account-info">
    <h2>Account Overview</h2>
    <div class="card-grid">
      <div class="card" v-for="(item, index) in formattedData" :key="index">
        <label>{{ item.label }}</label>
        <span :class="item.class">{{ item.value }}</span>
      </div>
    </div>
  </div>
</template>

<script>
import { fetchAccountSnapshot } from '@/services/dataFetcher';

export default {
  name: 'AccountInfoTab',
  data() {
    return {
      snapshot: null,
    };
  },
  computed: {
    formattedData() {
      if (!this.snapshot) return [];
      return [
        { label: 'Account ID', value: 'DU1234567' },
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
    formatDollar(val) {
      return val != null ? `$${parseFloat(val).toLocaleString(undefined, { minimumFractionDigits: 2 })}` : '-';
    },
    getMarginRatio() {
      if (!this.snapshot || !this.snapshot.buying_power || !this.snapshot.total_cash_value) return '-';
      const ratio = 100 * (1 - (this.snapshot.buying_power / this.snapshot.total_cash_value));
      return `${ratio.toFixed(1)}%`;
    },
  },
  mounted() {
    this.loadSnapshot();
  },
};
</script>

<style scoped>
.account-info {
  padding: 0 10px 10px 10px;
}

h2 {
  margin: 0 0 20px 0;
  font-size: 1.5rem;
  color: #00d1b2; /* Primary color for the title */
}

.card-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 16px;
}

.card {
  background-color: #333; /* Darker grey background for the cards */
  padding: 16px;
  border-radius: 8px;
  display: flex;
  flex-direction: column;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.3); /* Slightly stronger shadow */
}

label {
  font-size: 0.9rem;
  color: #bbb; /* Slightly lighter grey for the labels */
  margin-bottom: 6px;
}

span {
  font-size: 1.2rem;
  font-weight: 600;
  color: #e0e0e0; /* Lighter grey for text */
}

.highlight {
  color: #00d1b2; /* Highlight color for important values */
}

.pnl-positive {
  color: #4caf50; /* Green for positive values */
}

.pnl-negative {
  color: #e53935; /* Red for negative values */
}
</style>

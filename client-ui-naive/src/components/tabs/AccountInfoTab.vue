<template>
  <div>
    <!-- ▸ UPPER CARD - Snapshot Info -->
    <n-card title="Account Overview" class="q-mb-md">
      <n-row :gutter="[16, 16]">
        <n-col :span="6" v-for="(stat, i) in statistics" :key="i">
          <n-statistic :label="stat.label" :value="stat.value">
            <template #prefix v-if="stat.icon">
              <n-icon>
                <component :is="stat.icon" />
              </n-icon>
            </template>
          </n-statistic>
        </n-col>
      </n-row>
    </n-card>

    <!-- ▸ LOWER CARD - Positions Summary -->
    <n-card title="Positions Summary">
      <n-space vertical :size="12">
        <n-data-table
          :bordered="true"
          :columns="positionsColumns"
          :data="positions"
          :pagination="pagination"
        />
      </n-space>
    </n-card>
  </div>
</template>

<script setup>
import { ref, onMounted, markRaw } from "vue";
import {
  fetchAccountSnapshot,
  fetchOpenPositions,
} from "@/services/dataManager";
import { MdTrendingUp, MdTrendingDown } from "@vicons/ionicons4";

// Example icons
const MdTrendingUpRaw = markRaw(MdTrendingUp);
const MdTrendingDownRaw = markRaw(MdTrendingDown);

const snapshot = ref(null);
const statistics = ref([]);
const positions = ref([]);
const pagination = ref({
  pageSize: 5,
});

// Helper function to format number with a $ suffix and thousand separators
const formatCurrency = (value) => {
  return ` $ ${value.toLocaleString(undefined, {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  })}`; // Adding $ and commas
};

// Helper function to determine the icon and style for P&L
const getPnlIcon = (value) => {
  if (value > 0) {
    return { icon: MdTrendingUpRaw };
  } else if (value < 0) {
    return { icon: MdTrendingDownRaw };
  } else {
    return { icon: null };
  }
};

// Columns for the positions table
const positionsColumns = [
  { title: "Symbol", key: "symbol" },
  { title: "Quantity", key: "quantity" },
  {
    title: "Average Price",
    key: "avg_price",
    render: (row) => formatCurrency(row.avg_price),
  },
  { title: "Last Update", key: "last_update" },
];

onMounted(async () => {
  // Fetch account snapshot data
  const data = await fetchAccountSnapshot();
  if (data) {
    snapshot.value = data;

    statistics.value = [
      { label: "Total Cash", value: formatCurrency(data.total_cash_value) },
      { label: "Net Liquidation", value: formatCurrency(data.net_liquidation) },
      { label: "Available Funds", value: formatCurrency(data.available_funds) },
      { label: "Buying Power", value: formatCurrency(data.buying_power) },
      {
        label: "Unrealized P&L",
        value: formatCurrency(data.unrealized_pnl),
        icon: getPnlIcon(data.unrealized_pnl).icon,
        style: getPnlIcon(data.unrealized_pnl).style,
      },
      {
        label: "Realized P&L",
        value: formatCurrency(data.realized_pnl),
        icon: getPnlIcon(data.realized_pnl).icon,
        style: getPnlIcon(data.realized_pnl).style,
      },
      {
        label: "Excess Liquidity",
        value: formatCurrency(data.excess_liquidity),
      },
      {
        label: "Gross Position Value",
        value: formatCurrency(data.gross_position_value),
      },
    ];
  }

  // Fetch open positions data
  const openPositions = await fetchOpenPositions();
  if (openPositions) {
    positions.value = openPositions;
  }
});
</script>

<style scoped>
.q-mb-md {
  margin-bottom: 24px;
}
</style>

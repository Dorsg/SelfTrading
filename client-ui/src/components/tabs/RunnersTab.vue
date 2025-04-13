// -----------------------------
// RunnersTab.vue
// -----------------------------
<template>
  <div class="runners-tab">
    <div class="header-row">
      <button class="create-btn" @click="showCreateForm = true">
        ➕ Create Runner
      </button>
    </div>

    <CreateRunnerDialog
      v-if="showCreateForm"
      :defaultData="defaultForm"
      @close="showCreateForm = false"
      @created="addRunner"
    />

    <ag-grid-vue
      class="ag-theme-alpine-dark"
      style="width: 100%; height: 500px"
      :columnDefs="columnDefs"
      :rowData="rowData"
      rowSelection="single"
      :animateRows="true"
    />
  </div>
</template>

<script>
import { AgGridVue } from "ag-grid-vue3";
import "ag-grid-community/dist/styles/ag-grid.css";
import "ag-grid-community/dist/styles/ag-theme-alpine-dark.css";
import CreateRunnerDialog from "@/components/runners/CreateRunnerDialog.vue";

export default {
  name: "RunnersTab",
  components: {
    AgGridVue,
    CreateRunnerDialog,
  },
  data() {
    return {
      showCreateForm: false,
      defaultForm: {
        symbol: "",
        is_active: true,
        atrategy: "",
        stock_symbol: "",
        strategy_name: "",
        time_frame: 5,
        max_loss_perc: 1,
        take_profit_perc: 3,
        date_range: "7d",
        stock_number_limit: 1,
      },
      columnDefs: [
        { headerName: "ID", field: "id", width: 60 },
        { headerName: "Symbol", field: "symbol", width: 90 },
        { headerName: "Active", field: "is_active", width: 90 },
        { headerName: "Created At", field: "created_at", width: 120 },
        { headerName: "Strategy", field: "atrategy", width: 100 },
        { headerName: "Stock", field: "stock_symbol", width: 90 },
        { headerName: "Strategy Name", field: "strategy_name", width: 140 },
        { headerName: "Time Frame", field: "time_frame", width: 100 },
        { headerName: "Max Loss %", field: "max_loss_perc", width: 110 },
        { headerName: "Take Profit %", field: "take_profit_perc", width: 120 },
        { headerName: "Date Range", field: "date_range", width: 100 },
        { headerName: "Stock Limit", field: "stock_number_limit", width: 100 }
      ],
      rowData: [
        {
          id: 1,
          symbol: "AAPL",
          is_active: true,
          created_at: "2025-04-13",
          atrategy: "breakout",
          stock_symbol: "AAPL",
          strategy_name: "Breakout Swing",
          time_frame: 15,
          max_loss_perc: 2,
          take_profit_perc: 5,
          date_range: "30d",
          stock_number_limit: 3,
        },
        {
          id: 2,
          symbol: "TSLA",
          is_active: false,
          created_at: "2025-04-12",
          atrategy: "momentum",
          stock_symbol: "TSLA",
          strategy_name: "Momentum Hunt",
          time_frame: 5,
          max_loss_perc: 1,
          take_profit_perc: 3,
          date_range: "7d",
          stock_number_limit: 5,
        }
      ],
    };
  },
  methods: {
    addRunner(runner) {
      this.rowData.push(runner);
    },
  },
};
</script>

<style scoped>
.runners-tab {
  padding: 10px;
}

.header-row {
  display: flex;
  justify-content: flex-start;
  margin-bottom: 15px;
}

.create-btn {
  background-color: #00d1b2;
  color: #1e1e2f;
  border: none;
  padding: 8px 16px;
  border-radius: 6px;
  font-weight: bold;
  cursor: pointer;
}
</style>
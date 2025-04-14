<template>
    <div class="runners-tab">
      <div class="header-row">
        <q-btn
          class="create-btn"
          label="Create Runner"
          @click="showCreateForm = true"
          color="primary"
          icon="add"
          rounded
          dense
          size="md"
        />
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
        @grid-ready="onGridReady"
      />
    </div>
  </template>
  
  <script>
  import { AgGridVue } from "ag-grid-vue3";
  import "ag-grid-community/dist/styles/ag-grid.css";
  import "ag-grid-community/dist/styles/ag-theme-alpine-dark.css";
  import CreateRunnerDialog from "@/components/runners/CreateRunnerDialog.vue";
  import { QBtn } from 'quasar';
  
  export default {
    name: "RunnersTab",
    components: {
      AgGridVue,
      CreateRunnerDialog,
      QBtn,
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
          { headerName: "ID", field: "id" },
          { headerName: "Symbol", field: "symbol" },
          { headerName: "Active", field: "is_active" },
          { headerName: "Created At", field: "created_at" },
          { headerName: "Strategy", field: "atrategy" },
          { headerName: "Stock", field: "stock_symbol" },
          { headerName: "Strategy Name", field: "strategy_name" },
          { headerName: "Time Frame", field: "time_frame" },
          { headerName: "Max Loss %", field: "max_loss_perc" },
          { headerName: "Take Profit %", field: "take_profit_perc" },
          { headerName: "Date Range", field: "date_range" },
          { headerName: "Stock Limit", field: "stock_number_limit" }
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
      onGridReady(params) {
        params.api.sizeColumnsToFit();
      },
    },
  };
  </script>
  
  <style scoped>
  .runners-tab {
    padding: 10px;
    background-color: #2d2d2d; /* Match background with the dark theme */
  }
  
  .header-row {
    display: flex;
    justify-content: flex-start;
    margin-bottom: 15px;
  }
  
  .create-btn {
    background-color: #00d1b2; /* Primary color for the button */
    color: #fff;
    font-weight: bold;
    border-radius: 8px;
    padding: 10px 20px;
    cursor: pointer;
    text-transform: none;
  }
  
  .create-btn:hover {
    background-color: #009688; /* Slightly darker on hover */
  }
  
  .create-btn:active {
    background-color: #00796b; /* Darker on active */
  }
  
  /* Customize grid theme to match dark background */
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
  
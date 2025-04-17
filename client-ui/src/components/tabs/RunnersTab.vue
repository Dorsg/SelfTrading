<template>
  <div class="runners-tab page-wrapper">
    <div class="header-row">
      <q-btn
        class="primary-btn"
        label="Create Runner"
        icon="add"
        rounded
        dense
        size="md"
        @click="showCreateForm = true"
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
import { AgGridVue } from 'ag-grid-vue3';
import 'ag-grid-community/dist/styles/ag-grid.css';
import 'ag-grid-community/dist/styles/ag-theme-alpine-dark.css';
import CreateRunnerDialog from '@/components/runners/CreateRunnerDialog.vue';
import { QBtn } from 'quasar';

export default {
  name: 'RunnersTab',
  components: { AgGridVue, CreateRunnerDialog, QBtn },
  data() {
    return {
      showCreateForm: false,
      defaultForm: {
        symbol: '',
        is_active: true,
        atrategy: '',
        stock_symbol: '',
        strategy_name: '',
        time_frame: 5,
        max_loss_perc: 1,
        take_profit_perc: 3,
        date_range: '7d',
        stock_number_limit: 1
      },
      columnDefs: [
        { headerName: 'ID', field: 'id' },
        { headerName: 'Symbol', field: 'symbol' },
        { headerName: 'Active', field: 'is_active' },
        { headerName: 'Created At', field: 'created_at' },
        { headerName: 'Strategy', field: 'atrategy' },
        { headerName: 'Stock', field: 'stock_symbol' },
        { headerName: 'Strategy Name', field: 'strategy_name' },
        { headerName: 'Time Frame', field: 'time_frame' },
        { headerName: 'Max Loss %', field: 'max_loss_perc' },
        { headerName: 'Take Profit %', field: 'take_profit_perc' },
        { headerName: 'Date Range', field: 'date_range' },
        { headerName: 'Stock Limit', field: 'stock_number_limit' }
      ],
      rowData: [ /* sample records */ ]
    };
  },
  methods: {
    addRunner(runner) { this.rowData.push(runner); },
    onGridReady(params) { params.api.sizeColumnsToFit(); }
  }
};
</script>

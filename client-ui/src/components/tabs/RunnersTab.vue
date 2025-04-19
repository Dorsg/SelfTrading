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
      showCreateForm: false ,
      defaultForm: {
        name: '',
        strategy: '',
        budget: 0,
        stock: '',
        time_frame: '',
        stop_loss: 0,
        take_profit: 0,
        time_range: '',
        commission_ratio: '',
        exit_strategy: '',
        created_at: ''
      },
      columnDefs: [
        { headerName: 'ID', field: 'id' },
        { headerName: 'Name', field: 'name' },
        { headerName: 'Strategy', field: 'strategy' },
        { headerName: 'Budget', field: 'budget' },
        { headerName: 'Stock', field: 'stock' },
        { headerName: 'Time frame', field: 'time_frame' },
        { headerName: 'Risk% (stop loss)', field: 'stop_loss' },
        { headerName: 'Take profit at %', field: 'take_profit' },
        { headerName: 'Time range', field: 'time_range' },
        { headerName: 'Commission:price ratio', field: 'commission_ratio' },
        { headerName: 'Exit strategy (expired date / trail)', field: 'exit_strategy' },
        { headerName: 'Create date and time', field: 'created_at' }
      ],
      rowData: []
    };
  },
  methods: {
    addRunner(runner) {
      this.rowData.push(runner);
    },
    onGridReady(params) {
      params.api.sizeColumnsToFit();
    }
  }
};
</script>

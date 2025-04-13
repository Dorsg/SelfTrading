<template>
    <QDialog v-model="isOpen" persistent transition-show="scale" transition-hide="scale">
      <QCard class="dialog-card">
        <QCardSection class="q-pa-sm">
          <div class="text-h6 text-primary">Create New Runner</div>
        </QCardSection>
  
        <QSeparator dark />
  
        <QCardSection class="form-section">
          <QForm @submit.prevent="submitForm" class="q-gutter-md">
            <div v-for="(field, key) in formFields" :key="key">
              <QInput
                v-if="field.type !== 'checkbox'"
                v-model="localForm[key]"
                :label="field.label"
                :type="field.type"
                dense
                outlined
                color="primary"
                dark
                :rules="[val => !!val || 'Required']"
              />
  
              <QCheckbox
                v-else
                v-model="localForm[key]"
                :label="field.label"
                color="primary"
                dark
              />
            </div>
  
            <div class="row justify-end q-gutter-sm q-mt-md">
              <QBtn flat label="Cancel" color="negative" @click="$emit('close')" />
              <QBtn type="submit" label="Create" color="primary" />
            </div>
          </QForm>
        </QCardSection>
      </QCard>
    </QDialog>
  </template>
  
  <script>
  export default {
    name: "CreateRunnerDialog",
    props: ["defaultData"],
    emits: ["close", "created"],
    data() {
      return {
        isOpen: true,
        localForm: { ...this.defaultData },
        formFields: {
          symbol: { label: "Symbol", type: "text" },
          is_active: { label: "Is Active", type: "checkbox" },
          atrategy: { label: "Strategy", type: "text" },
          stock_symbol: { label: "Stock Symbol", type: "text" },
          strategy_name: { label: "Strategy Name", type: "text" },
          time_frame: { label: "Time Frame", type: "number" },
          max_loss_perc: { label: "Max Loss %", type: "number" },
          take_profit_perc: { label: "Take Profit %", type: "number" },
          date_range: { label: "Date Range", type: "text" },
          stock_number_limit: { label: "Stock Limit", type: "number" },
        },
      };
    },
    methods: {
      submitForm() {
        const newRunner = {
          id: Date.now(),
          created_at: new Date().toISOString().slice(0, 10),
          ...this.localForm,
        };
        this.$emit("created", newRunner);
        this.$emit("close");
      },
    },
  };
  </script>
  
  <style scoped>
  .dialog-card {
    width: 100%;
    max-width: 480px;
    max-height: 90vh;
    overflow: hidden;
    background-color: #2b2b3d;
    border: 1px solid #444;
    border-radius: 12px;
    box-shadow: 0 0 15px rgba(0,0,0,0.4);
    color: #fff;
  }
  
  .form-section {
    max-height: 65vh;
    overflow-y: auto;
    background-color: #1f1f2d;
    padding-right: 8px;
  }
  
  .form-section::-webkit-scrollbar {
    width: 6px;
  }
  
  .form-section::-webkit-scrollbar-thumb {
    background-color: #555;
    border-radius: 6px;
  }
  </style>
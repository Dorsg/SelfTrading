<template>
  <q-dialog v-model="isOpen" persistent transition-show="scale" transition-hide="scale">
    <q-card class="runner-dialog">

      <!-- ▸ TITLE -->
      <q-card-section class="dialog-header">
        <div class="dialog-title">Create New Runner</div>
      </q-card-section>

      <q-separator dark />

      <!-- ▸ BODY -->
      <div class="dialog-body row no-wrap">

        <!-- FORM -->
        <q-card-section class="runner-form col">
          <q-form @submit.prevent="submitForm" class="q-gutter-md">

            <q-input
              v-model="localForm.name"
              label="Name"
              outlined dense dark color="accent"
              @focus="setActive('name')"
            />

            <q-select
              v-model="localForm.strategy"
              label="Strategy"
              :options="strategies"
              outlined dense dark color="accent"
              emit-value map-options
              menu-content-class="my-select-dropdown"
              @focus="setActive('strategy')"
            />

            <q-input
              v-model.number="localForm.budget"
              label="Budget"
              type="number"
              suffix="$"
              outlined dense dark color="accent"
              @focus="setActive('budget')"
            />

            <q-input
              v-model="localForm.stock"
              label="Stock"
              outlined dense dark color="accent"
              @focus="setActive('stock')"
            />

            <q-select
              v-model="localForm.time_frame"
              label="Time Frame"
              :options="timeFrames"
              outlined dense dark color="accent"
              emit-value map-options
              menu-content-class="my-select-dropdown"
              @focus="setActive('time_frame')"
            />

            <q-input
              v-model.number="localForm.stop_loss"
              label="Risk % (stop loss)"
              type="number"
              suffix="%"
              outlined dense dark color="accent"
              @focus="setActive('stop_loss')"
            />

            <q-input
              v-model.number="localForm.take_profit"
              label="Take profit at %"
              type="number"
              suffix="%"
              outlined dense dark color="accent"
              @focus="setActive('take_profit')"
            />

            <!-- DATE‑RANGE FIELD -->
            <q-input
              v-model="timeRangeDisplay"
              label="Time Range"
              outlined dense dark color="accent"
              @focus="setActive('time_range'); $refs.trPopup.show()"
            >
              <template #append>
                <q-icon name="event" class="cursor-pointer" @click.stop="$refs.trPopup.show()" />
              </template>

              <q-popup-proxy
                ref="trPopup"
                transition-show="scale"
                transition-hide="scale"
              >
                <q-date
                  v-model="localForm.time_range"
                  range
                  dark
                  minimal
                  @update:model-value="updateTimeRangeDisplay"
                />
              </q-popup-proxy>
            </q-input>

            <q-select
              v-model="localForm.commission_ratio"
              label="Commission : price ratio"
              :options="commissionRatios"
              outlined dense dark color="accent"
              emit-value map-options
              menu-content-class="my-select-dropdown"
              @focus="setActive('commission_ratio')"
            />

            <q-select
              v-model="localForm.exit_strategy"
              label="Exit Strategy"
              :options="exitStrategies"
              outlined dense dark color="accent"
              emit-value map-options
              menu-content-class="my-select-dropdown"
              @focus="setActive('exit_strategy')"
            />

          </q-form>
        </q-card-section>

        <!-- DESCRIPTION PANEL -->
        <q-separator vertical dark />
        <div class="description-panel col-4">
          <div class="description-text">
            {{ fieldDescriptions[activeField] }}
          </div>
        </div>
      </div>

      <!-- ▸ ACTIONS -->
      <q-card-section class="dialog-actions">
        <q-btn flat label="Cancel" color="negative" class="action-btn" @click="$emit('close')" />
        <q-btn label="Create" color="primary" class="action-btn" @click="submitForm" />
      </q-card-section>

    </q-card>
  </q-dialog>
</template>


<script>
export default {
  name: 'CreateRunnerDialog',
  props: ['defaultData'],
  emits: ['close', 'created'],
  data () {
    return {
      isOpen: true,
      activeField: 'name',

      /* select options ------------------------------------------------ */
      strategies:      ['Fibonacci', 'Tunnel', 'AI'],
      timeFrames:      ['5 minutes', '15 minutes', '30 minutes', '1 hour', '4 hours', '1 day'],
      commissionRatios:['< 1', '< 2', '< 3'],
      exitStrategies:  ['Expired date', 'Trail'],

      /* human‑readable helper for date range --------------------------- */
      timeRangeDisplay: '',

      fieldDescriptions: {
        name:             'Choose a clear, unique identifier for this runner.',
        strategy:         'Select the trading strategy the runner will execute.',
        budget:           'Total capital allocated. Whole dollar amounts only.',
        stock:            'Ticker symbol or asset name you want to trade.',
        time_frame:       'Chart interval the strategy analyses for signals.',
        stop_loss:        'Max acceptable loss per trade, in percent of budget.',
        take_profit:      'Target profit percentage at which to close a trade.',
        time_range:       'Overall period during which the runner is active.',
        commission_ratio: 'Transaction cost relative to position size.',
        exit_strategy:    'Rule that closes positions other than stop / target.'
      },

      /* form model ---------------------------------------------------- */
      localForm: {
        name: '',
        strategy: null,
        budget: null,
        stock: '',
        time_frame: null,
        stop_loss: null,
        take_profit: 3,
        time_range:  null,            // { from:'YYYY/MM/DD', to:'YYYY/MM/DD' }
        commission_ratio: '1:100',
        exit_strategy: null,
        created_at: new Date().toISOString(),
        ...this.defaultData
      }
    }
  },

  mounted () { this.updateTimeRangeDisplay() },

  methods: {
    setActive (f) { this.activeField = f },

    updateTimeRangeDisplay () {
      const r = this.localForm.time_range
      this.timeRangeDisplay = r && r.from && r.to
        ? `${r.from} → ${r.to}`
        : ''
    },

    submitForm () {
      const newRunner = {
        id: Date.now(),
        ...this.localForm,
        created_at: new Date().toISOString()
      }
      this.$emit('created', newRunner)
      this.$emit('close')
    }
  }
}
</script>

<style scoped>
/* ─── Dialog colours & layout ──────────────────────────────────── */
.runner-dialog {
  width: 100%;
  max-width: 900px;
  background: #3b3b3b;
  color: var(--text-light);
  border-radius: var(--card-radius);
  border: 1px solid #606060;
  box-shadow: 0 0 18px rgba(0,0,0,.5);
}

.dialog-header { padding: 12px 18px; background: #454545; }
.dialog-title  { font-size: 1.35rem; font-weight: 600; color: #f1f1f1; }

.dialog-body {
  display: flex;
  flex-wrap: nowrap;
  overflow-y: hidden;
  max-height: 70vh;
}

.runner-form {
  padding: 16px;
  max-height: 70vh;
  overflow-y: auto;
  flex: 1;
  display: flex;
  flex-direction: column;
}
.runner-form .q-field {
  margin-bottom: 10px;
}

.description-panel {
  min-width: 300px;
  padding: 16px;
  background: #2e2e2e;
  display: flex; align-items: center;
}
.description-text { font-size: .85rem; line-height: 1.4; color: #d0d0d0; }

/* ▸ smaller/denser fields */
.runner-form .q-field { font-size: .75rem; }
.runner-form .q-field__control { min-height: 36px; }

/* Buttons */
.dialog-actions { display: flex; justify-content: flex-end; gap: 10px;
  padding: 12px 18px 16px; background: #3b3b3b; }
.action-btn     { font-size: .68rem; padding: 5px 14px; text-transform: none; }

/* Cancel */
.q-btn[color="negative"] {
  background: #4c3030; color: #ff7878; border: 1px solid #ff7878;
}
.q-btn[color="negative"]:hover { background: #663b3b; color:#fff; }

/* Create */
.q-btn[color="primary"] {
  background:#dedede; color:#1c1c1c; border:1px solid #b5b5b5;
}
.q-btn[color="primary"]:hover { background:#ffffff; }

.q-separator {
  margin: 0 !important;
}


</style>

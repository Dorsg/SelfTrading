<template>
    <n-form
      ref="formRef"
      :model="form"
      :rules="rules"
      label-placement="top"
      label-width="auto"
      require-mark-placement="right-hanging"
      :size="formSize"
    >
      <n-grid :x-gap="24" :y-gap="16" :cols="2">
        <n-form-item-gi label="Name" path="name">
          <n-input v-model:value="form.name" placeholder="Runner Name" />
        </n-form-item-gi>
  
        <n-form-item-gi label="Strategy" path="strategy">
          <n-select
            v-model:value="form.strategy"
            placeholder="Select Strategy"
            :options="strategyOptions"
          />
        </n-form-item-gi>
  
        <n-form-item-gi label="Budget $" path="budget">
            <n-input-number
                v-model:value="form.budget"
                placeholder="10000"
            />
        </n-form-item-gi>
  
        <n-form-item-gi label="Stock Symbol" path="stock">
          <n-input v-model:value="form.stock" placeholder="e.g. AAPL" />
        </n-form-item-gi>
  
        <n-form-item-gi label="Time Frame" path="timeFrame">
        <n-select
            v-model:value="form.timeFrame"
            placeholder="Select Time Frame"
            :options="timeFrameOptions"
        />
        </n-form-item-gi>
  
        <n-form-item-gi label="Stop Loss (%)" path="stopLoss">
            <n-input-number
                v-model:value="form.stopLoss"
                placeholder="-5"
                :step="0.5"
            />
            <template #suffix>%</template>
        </n-form-item-gi>
  
        <n-form-item-gi label="Take Profit (%)" path="takeProfit">
          <n-input-number 
                v-model:value="form.takeProfit" 
                placeholder="3"
                :step="0.5"
                />
        </n-form-item-gi>
  
        <n-form-item-gi label="Commission Ratio (% of order)" path="commissionRatio">
          <n-input-number v-model:value="form.commissionRatio" :step="0.01" placeholder="0.1" />
        </n-form-item-gi>
  
        <n-form-item-gi label="Start/End Date Range" path="timeRange">
          <n-date-picker
            v-model:value="form.timeRange"
            type="datetimerange"
            clearable
          />
        </n-form-item-gi>
  
        <n-form-item-gi label="Exit Strategy" path="exitStrategy">
        <n-checkbox-group v-model:value="form.exitStrategy">
            <n-space>
            <n-checkbox value="expired date">Expired Date</n-checkbox>
            <n-checkbox value="strategy">Strategy</n-checkbox>
            </n-space>
        </n-checkbox-group>
        </n-form-item-gi>
      </n-grid>
  
      <div class="form-footer">
        <n-space justify="end">
          <n-button @click="$emit('cancel')">Cancel</n-button>
          <n-button type="primary" @click="validateAndSubmit">Create</n-button>
        </n-space>
      </div>
    </n-form>
  </template>
  
  <script setup>
  import { ref } from 'vue'
  import { useMessage } from 'naive-ui'
  
  const emit = defineEmits(['create', 'cancel'])
  
  const formRef = ref(null)
  const formSize = ref('medium')
  const message = useMessage()
  
  const form = ref({
    name: '',
    strategy: null,
    budget: null,
    stock: '',
    timeFrame: null,
    stopLoss: null,
    takeProfit: null,
    timeRange: null,
    commissionRatio: null,
    exitStrategy: []
  })
  
  const strategyOptions = [
    { label: 'Fibonacci', value: 'Fibonacci' },
    { label: 'AI', value: 'AI' },
  ]

  const timeFrameOptions = [
    { label: '5 minutes', value: 5 },
    { label: '15 minutes', value: 15 },
    { label: '30 minutes', value: 30 },
    { label: '1 hour', value: 60 },
    { label: '4 hours', value: 240 },
    { label: 'Day', value: 1440 }
    ]
    
  const rules = {
    name: { required: true, message: 'Enter name', trigger: ['input', 'blur'] },
    strategy: { required: true, message: 'Select a strategy', trigger: 'change' },
    budget: {
        type: 'number',
        required: true,
        validator: (rule, value) => typeof value === 'number' && value >= 1000,
        message: 'Budget must be greater than $1000',
        trigger: ['blur', 'change']
    },
    stock: {
        required: true,
        validator: validateStockSymbol,
        trigger: ['blur', 'change']
    },
    timeFrame: {
        type: 'number',
        required: true,
        message: 'Select time frame',
        trigger: 'change'
    },
    stopLoss: {
        type: 'number',
        required: true,
        validator: (rule, value) => {
            return typeof value === 'number' && (-10 < value && value < 0)
        },
        message: 'Stop Loss must be between -10 and 0',
        trigger: ['blur', 'change']
    },
    takeProfit: {
        type: 'number',
        required: true,
        validator: (rule, value) => {
            return typeof value === 'number' && value > 0 && value < 30
        },
        message: 'Take Profit must be a number between 0 and 30',
        trigger: ['blur', 'change']
    },
    commissionRatio: {
        type: 'number',
        required: true,
        validator: (rule, value) => typeof value === 'number' && value >= 0.01,
        message: 'Commission ratio must be at least 0.01',
        trigger: ['blur', 'change']
    },
    timeRange: {
        type: 'array',
        required: true,
        validator: (rule, value) => {
            if (!Array.isArray(value) || value.length !== 2) return false
            const [start, end] = value
            const now = Date.now()
            return start >= now && end >= now
        },
        message: 'Dates must not be in the past',
        trigger: 'change'
    },
    exitStrategy: {
        type: 'array',
        required: true,
        message: 'Select at least one exit strategy',
        trigger: 'change'
    }

  }

    async function validateStockSymbol(rule, value) {
        if (!value) {
            return Promise.reject('Stock symbol is required')
        }

        try {
            const res = await fetch(
            `https://finnhub.io/api/v1/search?q=${value}&token=cvvt3q1r01qud9qkg67gcvvt3q1r01qud9qkg680`
            )
            const data = await res.json()

            const exactUSMatch = data.result.some(item => {
            const symbol = item.displaySymbol?.toUpperCase()
            const isExact = symbol === value.toUpperCase()
            const isCommonStock = item.type === 'Common Stock'
            const isUSMarket = !symbol.includes('.') // e.g., not AAPL.TO
            return isExact && isCommonStock && isUSMarket
            })

            return exactUSMatch
            ? Promise.resolve()
            : Promise.reject('Symbol not found in US stock market')
        } catch (e) {
            return Promise.reject('Error checking symbol. Try again later.')
        }
    }


  function validateAndSubmit() {
    formRef.value?.validate((errors) => {
      if (!errors) {
        emit('create', form.value)
        message.success('Runner created')
      } else {
        message.error('Please fix the errors')
      }
    })
  }
  </script>
  
  <style scoped>
  .form-footer {
    margin-top: 24px;
  }
  </style>
  
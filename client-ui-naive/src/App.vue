<template>
  <n-config-provider :theme="darkTheme">
    <n-layout>
      <n-page-header title="SelfTrading" class="header" />

      <n-layout-content class="content">
        <n-tabs v-model:value="activeTab" justify-content="space-evenly" type="line">
          <n-tab name="account" tab="Account Information" />
          <n-tab name="orders" tab="Open Orders" />
          <n-tab name="trades" tab="Executed Trades" />
          <n-tab name="runners" tab="Self Runners" />
        </n-tabs>

        <n-card class="card">
          <component :is="tabComponentMap[activeTab]" />
        </n-card>
      </n-layout-content>
    </n-layout>
  </n-config-provider>
</template>

<script setup>
import { ref } from 'vue'
import { darkTheme } from 'naive-ui'

import AccountInfoTab from './components/tabs/AccountInfoTab.vue'
import OpenOrdersTab from './components/tabs/OpenOrdersTab.vue'
import ExecutedTradesTab from './components/tabs/ExecutedTradesTab.vue'
import SelfRunnersTab from './components/tabs/SelfRunnersTab.vue'

const activeTab = ref('account')

const tabComponentMap = {
  account: AccountInfoTab,
  orders: OpenOrdersTab,
  trades: ExecutedTradesTab,
  runners: SelfRunnersTab
}
</script>

<style>
body {
  background-color: #121212;
  margin: 0;
}

.header {
  padding: 16px;
  border-bottom: 1px solid #444;
  background-color: #1a1a1a;
  color: white;
}

.content {
  padding: 24px;
}

.card {
  margin-top: 20px;
}
</style>

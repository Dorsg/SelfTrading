<template>
    <n-config-provider :theme="darkTheme">
      <n-message-provider>
        <n-layout>  
          <!-- Main -->
          <n-layout-content class="content">
            <n-tabs
              v-model:value="activeTab"
              justify-content="space-evenly"
              type="line"
            >
              <n-tab-pane name="account">
                <template #tab>
                  <n-icon :component="WalletOutline" size="18"
                          style="margin-right: 9px; vertical-align: -3px" />
                  Account Information
                </template>
              </n-tab-pane>
  
              <n-tab-pane name="orders">
                <template #tab>
                  <n-icon :component="DocumentTextOutline" size="18"
                          style="margin-right: 9px; vertical-align: -3px" />
                  Open Orders
                </template>
              </n-tab-pane>
  
              <n-tab-pane name="trades">
                <template #tab>
                  <n-icon :component="StatsChartOutline" size="18"
                          style="margin-right: 9px; vertical-align: -3px" />
                  Executed Trades
                </template>
              </n-tab-pane>
  
              <n-tab-pane name="runners">
                <template #tab>
                  <n-icon :component="RocketOutline" size="18"
                          style="margin-right: 9px; vertical-align: -3px" />
                  Self Runners
                </template>
              </n-tab-pane>
            </n-tabs>
  
            <n-card class="card">
              <component :is="tabComponentMap[activeTab]" />
            </n-card>
          </n-layout-content>
        </n-layout>
      </n-message-provider>
    </n-config-provider>
  </template>
  
  <script setup>
  import { ref, watch } from "vue";
  import { darkTheme } from "naive-ui";
  import {
    WalletOutline,
    DocumentTextOutline,
    StatsChartOutline,
    RocketOutline,
  } from "@vicons/ionicons5";
  
  import AccountInfoTab     from "@/components/tabs/AccountInfoTab.vue";
  import OpenOrdersTab      from "@/components/tabs/OpenOrdersTab.vue";
  import ExecutedTradesTab  from "@/components/tabs/ExecutedTradesTab.vue";
  import SelfRunnersTab     from "@/components/tabs/SelfRunnersTab.vue";
  
  const savedTab  = localStorage.getItem("activeTab") || "account";
  const activeTab = ref(savedTab);
  watch(activeTab, v => localStorage.setItem("activeTab", v));
  
  const tabComponentMap = {
    account: AccountInfoTab,
    orders:  OpenOrdersTab,
    trades:  ExecutedTradesTab,
    runners: SelfRunnersTab,
  };
  </script>
  
  <style scoped>
  .content { padding:24px }
  .card    { margin-top:20px }
  </style>
  
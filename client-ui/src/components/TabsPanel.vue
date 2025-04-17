<template>
  <div>
    <q-tabs
      v-model="selectedTab"
      class="custom-tabs bg-dark text-white q-mb-md"
      dense
      align="left"
    >
      <q-tab
        v-for="(tab, index) in tabs"
        :key="index"
        :label="tab.label"
        :name="index"
        class="custom-tab"
      />
    </q-tabs>

    <div class="tab-content">
      <component :is="tabs[selectedTab].component" />
    </div>
  </div>
</template>

<script>
import AccountInfoTab from './tabs/AccountInfoTab.vue';
import OrdersTab from './tabs/OrdersTab.vue';
import RunnersTab from './tabs/RunnersTab.vue';
import TradesTab from './tabs/TradesTab.vue';
import EmptyTab from './tabs/EmptyTab.vue';

export default {
  components: {
    AccountInfoTab,
    OrdersTab,
    TradesTab,
    RunnersTab,
    EmptyTab
  },
  data() {
    return {
      selectedTab: 0,
      tabs: [
        { label: 'Account Information', component: 'AccountInfoTab' },
        { label: 'Orders', component: 'OrdersTab' },
        { label: 'Trades', component: 'TradesTab' },
        { label: 'Runners', component: 'RunnersTab' },
        { label: 'Tab 3', component: 'EmptyTab' },
      ]
    };
  }
};
</script>

<style scoped>
.custom-tabs {
  --q-tabs-color: #00d1b2; /* active underline & text color */
  --q-tabs-tab-font-size: 16px;
  --q-tabs-padding: 0;
  border-bottom: 1px solid #444;
}

.custom-tab {
  text-transform: none; /* disable ALL CAPS */
  font-weight: 500;
  font-size: 16px;
  padding: 12px 16px;
  min-height: 36px;
  transition: all 0.2s ease-in-out;
}

.custom-tab.q-tab--active {
  color: #00d1b2;
}

.custom-tab.q-tab--active::after {
  height: 2px; /* thinner underline */
  background-color: #00d1b2;
  border-radius: 1px;
}

.q-tab__label {
  letter-spacing: 0.5px;
}
</style>

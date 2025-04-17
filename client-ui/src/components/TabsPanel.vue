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
import OrdersTab      from './tabs/OrdersTab.vue';
import TradesTab      from './tabs/TradesTab.vue';
import RunnersTab     from './tabs/RunnersTab.vue';
import EmptyTab       from './tabs/EmptyTab.vue';

export default {
  components: { AccountInfoTab, OrdersTab, TradesTab, RunnersTab, EmptyTab },
  data() {
    return {
      selectedTab: 0,
      tabs: [
        { label: 'Account Information', component: 'AccountInfoTab' },
        { label: 'Orders',              component: 'OrdersTab'      },
        { label: 'Trades',              component: 'TradesTab'      },
        { label: 'Runners',             component: 'RunnersTab'     },
        { label: 'Tab 3',               component: 'EmptyTab'       }
      ]
    };
  }
};
</script>

<template>
  <div>
    <q-tabs
      v-model="selectedTab"
      class="bg-dark text-white q-mb-md"
      indicator-color="primary"
      dense
      align="left" 
    >
      <q-tab
        v-for="(tab, index) in tabs"
        :key="index"
        :label="tab.label"
        :name="index"
      />
    </q-tabs>

    <div class="tab-content">
      <component :is="tabs[selectedTab].component" />
    </div>
  </div>
</template>

<script>
import AccountInfoTab from './tabs/AccountInfoTab.vue';
import RunnersTab from './tabs/RunnersTab.vue';
import EmptyTab from './tabs/EmptyTab.vue';

export default {
  components: {
    AccountInfoTab,
    RunnersTab,
    EmptyTab
  },
  data() {
    return {
      selectedTab: 0,
      tabs: [
        { label: 'Account Information', component: 'AccountInfoTab' },
        { label: 'Runners', component: 'RunnersTab' },
        { label: 'Tab 3', component: 'EmptyTab' },
        { label: 'Tab 4', component: 'EmptyTab' },
        { label: 'Tab 5', component: 'EmptyTab' }
      ]
    };
  }
};
</script>

<style scoped>
.tab-content {
  background-color: #222;
  padding: 20px;
  border-radius: 0 6px 6px 6px;
  box-shadow: 0 0 6px rgba(0, 0, 0, 0.3);
  color: #ccc;
}
</style>

<template>
    <div>
      <div class="tabs">
        <div
          v-for="(tab, index) in tabs"
          :key="index"
          :class="['tab', { active: selectedTab === index }]"
          @click="selectedTab = index"
        >
          {{ tab.label }}
        </div>
      </div>
  
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
  .tabs {
    display: flex;
    margin-bottom: 10px;
  }
  .tab {
    padding: 10px 20px;
    background-color: #2a2a40;
    color: #aaa;
    cursor: pointer;
    margin-right: 6px;
    border-radius: 6px 6px 0 0;
    transition: background-color 0.2s ease;
  }
  .tab:hover {
    background-color: #3a3a55;
  }
  .tab.active {
    background-color: #00d1b2;
    color: #1e1e2f;
    font-weight: bold;
  }
  .tab-content {
    background-color: #2a2a40;
    padding: 20px;
    border-radius: 0 6px 6px 6px;
    box-shadow: 0 0 6px rgba(0,0,0,0.3);
  }
  </style>
  
<template>
  <div id="app" class="dark-theme">
    <HeaderBar />
    <TabsPanel />
  </div>
</template>

<script>
import HeaderBar from './components/HeaderBar.vue';
import TabsPanel from './components/TabsPanel.vue';

export default {
  name: 'App',
  components: {
    HeaderBar,
    TabsPanel
  },
};
</script>

<style scoped>
.dark-theme {
  background-color: #1e1e2f;
  color: #e0e0e0;
  min-height: 100vh;
  padding: 20px;
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}
</style>

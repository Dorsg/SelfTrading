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
  background-color: #2d2d2d; /* Dark grey-black background */
  color: #ccc; /* Light grey text for readability */
  min-height: 100vh;
  padding: 20px;
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}

header {
  background-color: #222; /* Darker header background */
}

button {
  background-color: #444; /* Dark grey buttons */
  color: #fff;
  border-radius: 6px;
}
</style>

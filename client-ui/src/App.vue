<template>
  <div id="app" class="dark-theme">
    <HeaderBar />
    <TabsPanel />
  </div>
</template>

<script>
import HeaderBar from './components/HeaderBar.vue'
import TabsPanel  from './components/TabsPanel.vue'

export default {
  name: 'App',
  components: { HeaderBar, TabsPanel }
}
</script>
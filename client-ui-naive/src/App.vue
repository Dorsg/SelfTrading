<template>
  <n-config-provider :theme="darkTheme">
    <n-message-provider>
      <n-page-header title="SelfTrading" class="header" />

      <RouterView />
    </n-message-provider>
  </n-config-provider>
</template>

<script setup>
import { darkTheme } from "naive-ui";
</script>

<style>
html, body, #app {
  height: 100%;
  margin: 0;
  background: #121212;
}

.header {
  padding: 16px;
  border-bottom: 1px solid #444;
  background-color: #1a1a1a;
  color: white;
}
</style>
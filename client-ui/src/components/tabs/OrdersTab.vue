<template>
  <div class="orders">
    <div class="header-bar">
      <h2>Account Overview</h2>
      <div v-if="snapshot && snapshot.timestamp" class="last-updated">
        Last update on: {{ formatTimestamp(snapshot.timestamp) }}
      </div>
    </div>
    <div class="card-grid">
      <div class="card" v-for="(item, index) in formattedData" :key="index">
        <label>{{ item.label }}</label>
        <span :class="item.class">{{ item.value }}</span>
      </div>
    </div>
  </div>


</template>

<script>

export default {
  name: 'OrdersTab',
};
</script>

<style scoped>
.orders {
  padding: 0 10px 10px 10px;
}

.header-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}


</style>

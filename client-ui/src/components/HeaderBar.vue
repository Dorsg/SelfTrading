<template>
  <header class="header-bar">
    <div class="logo-container">
      <svg class="logo-icon" viewBox="0 0 24 24" fill="none">
        <rect x="4" y="6" width="2" height="12" fill="#00d1b2"/>
        <rect x="11" y="3" width="2" height="18" fill="#00d1b2"/>
        <rect x="18" y="8" width="2" height="8" fill="#00d1b2"/>
      </svg>
      <span class="app-name">SelfTrading</span>
    </div>
  </header>
</template>

<style scoped>
.header-bar {
  background-color: #151522;
  padding: 8px 16px;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.6);
  margin-bottom: 16px;
}

.logo-container {
  display: flex;
  align-items: center;
  gap: 10px;
}

.logo-icon {
  width: 24px;
  height: 24px;
}

.app-name {
  color: #00d1b2;
  font-size: 1.4rem;
  font-weight: 600;
}
</style>

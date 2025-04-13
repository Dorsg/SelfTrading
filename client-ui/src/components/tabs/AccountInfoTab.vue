<template>
    <div class="account-info">
      <h2>Account Overview</h2>
      <div class="card-grid">
        <div class="card">
          <label>Account ID</label>
          <span>DU1234567</span>
        </div>
        <div class="card">
          <label>Balance</label>
          <span class="highlight">$1,000,000.00</span>
        </div>
        <div class="card">
          <label>Buying Power</label>
          <span class="highlight">$6,666,666.67</span>
        </div>
        <div class="card">
          <label>Unrealized PnL</label>
          <span class="pnl-positive">+ $2,430.00</span>
        </div>
        <div class="card">
          <label>Realized PnL</label>
          <span class="pnl-negative">− $1,150.00</span>
        </div>
        <div class="card">
          <label>Margin Ratio</label>
          <span>35%</span>
        </div>
      </div>
    </div>
  </template>
  
  <style scoped>
.account-info {
  padding: 0 10px 10px 10px;
}

h2 {
  margin: 0 0 20px 0;
  font-size: 1.5rem;
  color: #00d1b2;
}
  
  .card-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
    gap: 16px;
  }
  
  .card {
    background-color: #2a2a40;
    padding: 16px;
    border-radius: 8px;
    display: flex;
    flex-direction: column;
    box-shadow: 0 2px 4px rgba(0,0,0,0.2);
  }
  
  label {
    font-size: 0.85rem;
    color: #bbb;
    margin-bottom: 6px;
  }
  
  span {
    font-size: 1.2rem;
    font-weight: 600;
    color: #e0e0e0;
  }
  
  .highlight {
    color: #00d1b2;
  }
  
  .pnl-positive {
    color: #4caf50;
  }
  
  .pnl-negative {
    color: #e53935;
  }
  </style>
  